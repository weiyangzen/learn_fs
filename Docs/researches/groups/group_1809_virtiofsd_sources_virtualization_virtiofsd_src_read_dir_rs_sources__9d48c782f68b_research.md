# Group Research: group_1809_virtiofsd_sources_virtualization_virtiofsd_src_read_dir_rs_sources__9d48c782f68b

Scope verified against `Docs/research_subset_a.md`: `sources/virtualization/virtiofsd` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/read_dir.rs -->
# File Research: sources/virtualization/virtiofsd/src/read_dir.rs

## Purpose

This file implements a Linux `getdents64(2)` based directory reader for virtiofsd. It adapts raw kernel `linux_dirent64` records into the crate’s `filesystem::DirectoryIterator` interface, yielding `filesystem::DirEntry` values with inode, offset, file type, and C-string name.

## Main Types And Functions

- `LinuxDirent64`: packed representation of the fixed-size prefix of Linux `struct linux_dirent64`.
- `ReadDir<P>`: buffered directory iterator over a caller-provided mutable byte buffer.
- `ReadDir::new(dir, offset, buf)`: seeks the directory file descriptor to a requested offset with `lseek64`, then fills the buffer through `new_no_seek`.
- `ReadDir::new_no_seek(dir, buf)`: unsafe constructor that calls `SYS_getdents64` at the descriptor’s current position without seeking.
- `ReadDir::remaining()`: returns unread bytes in the current buffer.
- `DirectoryIterator for ReadDir<P>`: parses one dirent at a time from the internal byte buffer.
- `strip_padding(b)`: converts padded kernel name bytes to a `CStr` by truncating after the first NUL.

## Control Flow

Construction either seeks first (`new`) or trusts the current descriptor position (`new_no_seek`). Both paths call Linux `getdents64` into the supplied buffer and set `current = 0`, `end = returned_byte_count`.

Iteration slices `buf[current..end]`, reads a `LinuxDirent64` from the front using `vm_memory::ByteValued::from_slice`, computes the name payload length from `d_reclen`, strips alignment padding, builds a `DirEntry`, then advances `current` by `d_reclen`.

## Integration Points

This module depends on:

- `crate::filesystem::{DirEntry, DirectoryIterator}` for the abstract directory iteration contract used by `server.rs` for FUSE `READDIR` and `READDIRPLUS`.
- `libc::SYS_getdents64`, `lseek64`, and Unix raw file descriptors.
- `vm_memory::ByteValued` to decode the packed dirent prefix from bytes.

The `seccomp.rs` allowlist includes `getdents64`, which is required by this reader.

## Important Invariants

- `new_no_seek` is unsafe because callers must ensure the directory FD position is valid and not concurrently manipulated.
- The parser trusts kernel-provided `d_reclen` and buffer layout, using debug assertions rather than runtime validation.
- `strip_padding` requires at least one NUL byte; missing NUL panics.
- Names returned as `&CStr` borrow from the internal buffer and are only valid until the iterator advances or is dropped.

## Tests

Unit tests cover `strip_padding` behavior for padded names, normal C strings, empty names, interior NUL truncation, and missing-NUL panic.

## Risks And Edge Cases

- Malformed buffers would panic or mis-parse, but the code explicitly trusts kernel output.
- Concurrent use of `new_no_seek` on the same descriptor can corrupt logical iteration because directory offsets are descriptor-global.
- `d_reclen` arithmetic assumes the record length is at least the fixed header size; this is only debug-checked.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/read_dir.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/sandbox.rs -->
# File Research: sources/virtualization/virtiofsd/src/sandbox.rs

## Purpose

This file implements virtiofsd sandbox setup. It supports namespace-based isolation, chroot-based isolation, and no isolation. The sandbox code isolates the daemon around the shared directory, captures sandbox-visible `/proc/self/fd` and `/proc/self/mountinfo` descriptors, optionally configures UID/GID maps for unprivileged user namespaces, and coordinates helper child processes.

## Main Types And Functions

- `Error`: detailed sandbox setup failures for mount, chroot, namespace, UID/GID map, group dropping, and process-control operations.
- `SandboxMode`: `Namespace`, `Chroot`, or `None`; parsed from strings.
- `Sandbox`: stores the shared directory, captured proc/mountinfo descriptors, sandbox mode, and requested UID/GID maps.
- `Sandbox::new(...)`: constructs a sandbox configuration.
- `setup_mounts()`: builds namespace mount isolation around the shared directory.
- `setup_id_mappings(uid_map, gid_map, pid)`: configures user namespace UID/GID maps for a target process.
- `enter_namespace(listener)`: creates PID/mount/network/user namespaces, configures ID mappings, forks the daemon child, and arranges parent waiting.
- `enter_chroot()`: opens proc descriptors, chroots into the shared directory, and changes to `/`.
- `must_drop_supplemental_groups()`: decides whether root must drop supplementary groups.
- `drop_supplemental_groups()`: calls `setgroups(0, NULL)` when needed.
- `enter(listener)`: validates mode and maps, drops groups if required, then enters the selected sandbox.
- Accessors: `get_proc_self_fd`, `get_mountinfo_fd`, `get_root_dir`, `get_mountinfo_prefix`.

## Namespace Mount Setup

`setup_mounts()` is the central isolation routine. It:

1. Opens `/proc/self` so `/proc/self/mountinfo` can later be opened after mount changes.
2. Marks `/` recursively slave to prevent propagation to the parent mount namespace.
3. Mounts a fresh procfs at `/proc`.
4. Bind-mounts `/proc/self/fd` over `/proc`, narrowing proc access to file descriptors.
5. Opens the bind-mounted `/proc` as the sandbox’s `proc_self_fd`.
6. Clones the shared directory tree with `open_tree(... OPEN_TREE_CLONE ...)`.
7. Moves the cloned tree to the shared directory path with `move_mount`.
8. Opens old `/`, `fchdir`s into the new root, and compares old/new root statx data.
9. If not already the current root, performs `pivot_root(".", ".")`, switches to old root, makes it slave, lazily unmounts it, and returns to the new root.
10. Opens sandbox-visible `mountinfo` via the saved `/proc/self` descriptor.

The code avoids exposing ancestor directories through `/proc/self/fd` and detaches old root state after pivoting.

## UID/GID Mapping Flow

For unprivileged namespace mode, `enter_namespace()` forks a first child whose only job is to set UID/GID mappings from outside the namespace. Synchronization uses two pipes and `IdMapSetUpPipeMessage::{Request, Done}`:

- Parent calls `unshare(flags)`.
- Parent signals the first child to write maps for the parent process.
- First child invokes `setup_id_mappings`.
- Parent waits for the done byte, then waits for the helper child.

`setup_id_mappings()` defaults to a single identity mapping for the current effective UID/GID if no maps are supplied. If requested maps require privileges or cover more than one ID, it shells out to `newuidmap` or `newgidmap`; otherwise it writes `/proc/<pid>/uid_map`, `/proc/<pid>/setgroups`, and `/proc/<pid>/gid_map` directly.

## Process Model

`enter_namespace()` uses `util::sfork()` rather than plain `fork()`, so children receive a parent-death signal and detect parent death races. After namespace setup and ID mapping, the process sets uid/gid to root inside the namespace and forks a second child. The second child runs `setup_mounts()` and continues with the vhost-user listener. The parent closes the listener FD without unlinking the socket and then calls `util::wait_for_child(child)`, which never returns.

This listener handling prevents the parent from keeping a listening socket open after the child accepts, avoiding hangs from a misconfigured VMM connecting twice.

## Chroot Mode

`enter_chroot()` is simpler:

1. Opens `/proc/self/fd` as `proc_self_fd`.
2. Opens `/proc/self/mountinfo` as `mountinfo_fd`.
3. Calls `chroot(shared_dir)`.
4. Calls `chdir("/")`.

Chroot mode is restricted to root by `enter()`.

## Validation And Security Rules

`enter()` enforces:

- Non-root cannot use `SandboxMode::Chroot`; it should use namespace mode.
- Explicit UID/GID maps are only accepted for non-root namespace mode.
- Supplementary groups are dropped when root can switch arbitrary groups, unless the process is already in a restricted user namespace with single UID/GID mappings and `setgroups` is denied.

## Integration Points

This module integrates with:

- `crate::idmap::{UidMap, GidMap, IdMapSetUpPipeMessage}` for namespace maps.
- `crate::oslib` for mount wrappers, `open_tree`, `move_mount`, `fchdir`, `umount2`, and pipes.
- `crate::passthrough::statx` to compare mount/root identity.
- `crate::util::{sfork, wait_for_child}` for safer fork/wait behavior.
- `vhost::vhost_user::Listener`, which is passed through sandbox entry.
- The broader passthrough filesystem code through `proc_self_fd`, `mountinfo_fd`, root directory, and mountinfo prefix accessors.

## Risks And Edge Cases

- Namespace setup depends on modern Linux mount APIs such as `open_tree` and `move_mount`.
- Missing `newuidmap`/`newgidmap` or invalid subordinate ID configuration causes explicit map setup failure.
- The parent exits via `wait_for_child`, so callers must expect `enter_namespace()` not to return in the parent.
- `CString::new(self.shared_dir.clone()).unwrap()` assumes the shared directory contains no interior NUL.
- `setup_mounts()` has many privileged syscalls and must stay aligned with the seccomp allowlist.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/sandbox.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/seccomp.rs -->
# File Research: sources/virtualization/virtiofsd/src/seccomp.rs

## Purpose

This file builds and loads virtiofsd’s seccomp filter. It initializes a libseccomp context with a default action and explicitly allowlists syscalls needed by daemon startup, sandboxing, vhost-user transport, FUSE request handling, filesystem operations, threading, memory management, and optional remote logging.

## Main Types And Functions

- `Error`: failures for initializing seccomp, adding an allow rule, or loading the filter.
- `SeccompAction`: default action options: `Allow`, `Kill`, `Log`, `Trap`.
- `impl From<SeccompAction> for u32`: maps to libseccomp actions.
- `allow_syscall!`: helper macro converting a syscall constant to `i32`, adding an allow rule, and returning `AllowSeccompSyscall` on failure.
- `enable_seccomp(action, allow_remote_logging)`: constructs, populates, loads, and releases the seccomp context.

## Behavior

`enable_seccomp()` calls `seccomp_init(action.into())`, where `action` is the default action for non-allowlisted syscalls. It then invokes `allow_syscall!` for each permitted syscall. After all rules are added, it calls `seccomp_load(ctx)` and then `seccomp_release(ctx)`.

The allowlist is architecture-aware using `cfg` gates for syscalls that only exist or are only needed on selected targets, such as `epoll_create`, `epoll_wait`, `fstat`, `getdents`, `newfstatat`, `_llseek`, `open`, `renameat`, `sigreturn`, `time`, and `unlink`.

## Syscall Coverage

The allowlist covers:

- vhost-user socket and messaging: `accept4`, `recvmsg`, `sendmsg`, optional `sendto`.
- Event loops and notification: `epoll_*`, `eventfd2`, `futex`.
- Filesystem operations: `openat`, `openat2`, `open_by_handle_at`, `read`, `write`, `pread*`, `pwrite*`, `readv`, `writev`, `copy_file_range`, `fallocate`, `ftruncate`, `fsync`, `fdatasync`, `syncfs`, `getdents64`, xattrs, links, mkdir/mknod, rename, unlink, symlink, stat/statx/statfs, flock, lseek.
- Sandbox and privilege transitions: `capget`, `capset`, `setgroups`, `setresuid`, `setresgid`, `unshare`, `prctl`.
- Memory and process runtime: `brk`, `clone`, `clone3`, `mmap`, `mprotect`, `mremap`, `munmap`, `madvise`, `exit`, `exit_group`, signal syscalls, `getpid`, `gettid`, `getrandom`, scheduler calls.
- Compatibility/runtime support: `rseq` on GNU, `tkill` for older systems, `membarrier`, `umask`.

## Integration Points

This file must stay synchronized with syscall usage in:

- `read_dir.rs`: `getdents64`, `lseek`.
- `sandbox.rs`: `unshare`, `setresuid`, `setresgid`, `setgroups`, `prctl`, mount-related wrappers, process control.
- `server.rs`: file, xattr, directory, copy, sync, and read/write syscalls through filesystem backends.
- `vhost_user.rs`: epoll/eventfd/socket/vhost-user runtime.
- `util.rs`: `flock`, `pidfd_open`, `fork`, `poll`, `waitpid`, capability operations.

## Risks And Edge Cases

- New filesystem or sandbox functionality can fail under seccomp unless the syscall is added here.
- The default action can be `Kill`, `Trap`, or `Log`, so missing allowlist entries may become fatal depending on configuration.
- The allowlist is syscall-level only; it does not constrain syscall arguments.
- If `seccomp_rule_add` fails partway through, the context is not explicitly released before returning.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/seccomp.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/server.rs -->
# File Research: sources/virtualization/virtiofsd/src/server.rs

## Purpose

This file implements virtiofsd’s FUSE protocol server. It decodes incoming FUSE request messages from guest memory, dispatches them to a generic `FileSystem` implementation, and encodes FUSE replies. It also adapts descriptor-backed I/O to zero-copy filesystem traits and forwards serialization hooks for migration.

## Main Types And Constants

- `FUSE_BUFFER_HEADER_SIZE`: additional inbound size allowance for the FUSE header area.
- `MAX_BUFFER_SIZE`: maximum local request/reply data buffer, 1 MiB.
- `DIRENT_PADDING`: zero padding for 8-byte aligned directory entries.
- `CURRENT_DIR_CSTR`, `PARENT_DIR_CSTR`: special directory entry names used by `READDIRPLUS`.
- `ZcReader<'a>`: wraps descriptor `Reader` as `ZeroCopyReader`.
- `ZcWriter<'a>`: wraps descriptor `Writer` as `ZeroCopyWriter`.
- `Server<F>`: generic FUSE server over a `FileSystem`; stores the filesystem and negotiated FUSE options in an `AtomicU64`.

## Top-Level Dispatch

`Server::handle_message()` reads an `InHeader`, rejects oversized inbound messages, converts the opcode with `Opcode::try_from`, logs request metadata, and dispatches to one method per FUSE opcode.

Implemented dispatch includes lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rmdir, rename, link, open, read, write, statfs, release, fsync, xattrs, flush, init, opendir, readdir, releasedir, fsyncdir, locking stubs, access, create, interrupt, bmap, destroy, ioctl, poll, notify reply, batch forget, fallocate, readdirplus, rename2, lseek, copy file range, setup/remove mapping stubs, syncfs, and tmpfile stub.

Unknown opcodes return `ENOSYS`.

## Request Handling Pattern

Most handlers follow the same pattern:

1. Read the typed FUSE input structure with `Reader::read_obj()`.
2. Compute remaining variable-length bytes using checked subtraction from `in_header.len`.
3. Read names or payloads into a vector.
4. Convert NUL-terminated names with `bytes_to_cstr()`.
5. Convert `InHeader` into filesystem `Context`.
6. Call the corresponding `FileSystem` method.
7. Return either `reply_ok(...)` or `reply_error(...)`.

This pattern is used for metadata operations, namespace operations, file handles, xattrs, and directory handles.

## Zero-Copy I/O

`ZcReader` implements `ZeroCopyReader::write_to_file_at()` by repeatedly writing from guest descriptors into a host file at the requested offset until count is exhausted, a zero write occurs, or checked arithmetic fails.

`ZcWriter` implements `ZeroCopyWriter::read_from_file_at()` by repeatedly reading from a host file into guest descriptors at the requested offset. Both wrappers protect against offset wrap-around and impossible count underflow.

`read()` splits the reply writer after the `OutHeader` and passes a `ZcWriter` to `fs.read()`. It then writes a custom `OutHeader` whose length includes the actual byte count. `write()` passes a `ZcReader` to `fs.write()` and replies with `WriteOut`.

## Initialization And Negotiation

`init()` reads `InitInCompat`, optionally reads `InitInExt` when `INIT_EXT` is offered, validates protocol major/minor versions, and declares supported FUSE options. Supported defaults include async read, parallel directory ops, big writes, auto invalidation, async DIO, ioctl directory support, atomic truncate, max pages, submounts, init extensions, create supplementary groups, and idmap support.

The effective enabled options are `capable & (want | supported)`, where `want` comes from `fs.init(capable)`. The selected option bits are stored in `self.options`.

The reply sets max background, congestion threshold, max write, nanosecond time granularity, page count, and split 64-bit flags.

## Directory Handling

`readdir()` asks `fs.readdir()` for a `DirectoryIterator`, writes dirents with `add_dirent()`, stops cleanly when the buffer is full, and replies with the actual byte count.

`readdirplus()` additionally resolves each non-`.`/`..` dirent through `fs.lookup()` using `handle_dirent()`, then writes `EntryOut` plus `Dirent`. If the buffer fills or an error occurs after a lookup, it calls `fs.forget(..., nlookup = 1)` to avoid lookup count leaks. If no entries have been written, the first error is returned.

`handle_dirent()` creates synthetic negative entries for `.` and `..` rather than looking them up.

`add_dirent()` strips the trailing NUL from the name, computes aligned dirent length, checks for overflow, writes optional `EntryOut`, writes `Dirent`, writes the name, and pads to 8-byte alignment. It returns `Ok(0)` when the caller’s remaining buffer cannot fit the complete entry.

## Extended Request Extensions

`get_extensions()` parses create-like request extensions after the filename when negotiated options require them. It supports:

- `SECURITY_CTX`: parsed by `parse_security_context()`, currently allowing at most one security context.
- `CREATE_SUPP_GROUP`: parsed by `parse_sup_groups()` into guest GIDs.

It validates extension header sizes, rejects truncated payloads, rejects duplicate or unsupported extensions, and requires a security context when the feature was negotiated. Supplementary groups are optional because the kernel only sends them when needed.

`parse_sup_groups()` enforces `LINUX_NRGROUPS_MAX`, verifies exact padded size, and decodes `u32` GIDs into `GuestGid`.

A unit test verifies that a truncated supplementary-groups extension is rejected with `EINVAL`.

## Reply Helpers

- `reply_readdir(len, unique, w)`: writes a successful `OutHeader` for directory replies and flushes.
- `reply_ok(out, data, unique, w)`: writes a successful header, optional fixed object, and optional byte payload.
- `reply_error(e, unique, w)`: writes an error header using negative errno, defaulting to `EIO`.
- `strerror(error)`: formats errno names for debug logging.
- `bytes_to_cstr(buf)`: validates NUL termination and absence of interior NULs.
- `take_object<T>()`: unaligned decode of a `ByteValued` object from a byte slice.

## Unsupported Or Stubbed Operations

`setupmapping()` and `removemapping()` return `ENOSYS`.

`getlk`, `setlk`, `setlkw`, `bmap`, `ioctl`, `poll`, and `notify_reply` defer to filesystem methods that may themselves return unsupported errors.

`tmpfile()` expects `fs.tmpfile()` to return an error and panics if it unexpectedly succeeds, then returns that error.

`interrupt()` and `destroy()` produce no FUSE reply; `destroy()` calls `fs.destroy()` and clears negotiated options.

## Serialization Integration

`impl SerializableFileSystem for Server<F>` forwards `prepare_serialization`, `serialize`, and `deserialize_and_apply` to the wrapped filesystem. This is used by `vhost_user.rs` migration handling.

## Integration Points

This file is the bridge between:

- `descriptor_utils::{Reader, Writer}` for guest descriptor access.
- `fuse::*` for protocol structures, flags, opcodes, and reply layouts.
- `filesystem::*` for the backend filesystem abstraction.
- `soft_idmap::GuestGid` for supplementary group extension decoding.
- `passthrough::util::einval` for EINVAL construction.
- `vhost_user.rs`, which calls `Server::handle_message()` for each vring descriptor chain and calls serialization methods during migration.

## Important Invariants

- Variable-length request sizes are computed with checked arithmetic to avoid underflow.
- Xattr, directory, and batch-forget sizes are bounded by `MAX_BUFFER_SIZE`.
- Names must be valid C strings with a single trailing NUL.
- Directory entries must be 8-byte aligned.
- `READDIR` and `READDIRPLUS` may return less than requested rather than failing large output sizes.
- `READDIRPLUS` must balance lookup counts when it cannot return an entry it already looked up.
- Negotiated options are stored atomically and affect later parsing of create/xattr extension layouts.

## Risks And Edge Cases

- Many handlers allocate vectors sized by guest-controlled message lengths after validation; missed checks would be high risk.
- Some unsupported operations return success with zero bytes if the filesystem stub returns `Ok(())`; behavior depends on the `FileSystem` trait implementation.
- `tmpfile()` panics if a filesystem reports success even though the server treats the operation as unsupported.
- `take_object()` uses unaligned reads from arbitrary bytes but only for `ByteValued` types.
- Protocol changes in Linux FUSE extension layout must be mirrored in `get_extensions()`.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/server.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/soft_idmap/cmdline.rs -->
# File Research: sources/virtualization/virtiofsd/src/soft_idmap/cmdline.rs

## Purpose

This file defines the command-line representation of soft UID/GID mapping rules. It parses user-provided mapping strings into structured `IdMap` enum variants and formats them back to canonical strings. Runtime conversion into range maps is implemented in `soft_idmap/mod.rs`.

## Main Types

- `IdMap`: command-line mapping rule enum.
- `IdMapError`: parse errors for invalid prefixes, invalid field counts, and invalid numeric values.

`IdMap` variants:

- `Guest { from_guest, to_host, count }`: 1:1 guest-to-host range mapping.
- `Host { from_host, to_guest, count }`: 1:1 host-to-guest range mapping.
- `SquashGuest { from_guest, to_host, count }`: many guest IDs to one host ID.
- `SquashHost { from_host, to_guest, count }`: many host IDs to one guest ID.
- `Bidirectional { guest, host, count }`: symmetric 1:1 range mapping in both directions.
- `ForbidGuest { from_guest, count }`: guest range that should fail when mapped.

## Parsing

`impl FromStr for IdMap` calls `pre_parse()` to split the input into a lowercase prefix and parsed `u32` fields. It then matches the prefix:

- `guest`: expects 3 fields.
- `host`: expects 3 fields.
- `squash-guest`: expects 3 fields.
- `squash-host`: expects 3 fields.
- `forbid-guest`: expects 2 fields.
- `map`: expects 3 fields and creates `Bidirectional`.
- Any other prefix returns `InvalidPrefix`.

`pre_parse()` accepts alphanumeric, `-`, and `_` characters in the prefix. The first other character becomes the separator. All remaining fields are split using that exact separator and parsed as `u32`.

This allows forms like `guest:1:2:3` and also other non-alphanumeric separators, except `-` and `_` cannot be separators because they are allowed in prefixes.

## Formatting

`impl Display for IdMap` emits canonical colon-separated strings:

- `guest:<from_guest>:<to_host>:<count>`
- `host:<from_host>:<to_guest>:<count>`
- `squash-guest:<from_guest>:<to_host>:<count>`
- `squash-host:<from_host>:<to_guest>:<count>`
- `forbid-guest:<from_guest>:<count>`
- `map:<guest>:<host>:<count>`

`IdMapError` also has a human-readable `Display` implementation.

## Integration Points

This module is exported by `soft_idmap/mod.rs`. Parsed `Vec<cmdline::IdMap>` values are consumed by `TryFrom<Vec<cmdline::IdMap>> for soft_idmap::IdMap<Guest, Host>`, which performs range validation, overlap detection, and runtime map construction.

## Important Invariants

- All numeric values are `u32`.
- Prefixes are normalized to lowercase.
- Field count validation happens after numeric parsing.
- Empty input returns an `InvalidLength` error with approximate expected/seen values.
- The parser does not validate range overflow or overlap; that is handled by runtime conversion in `mod.rs`.

## Risks And Edge Cases

- Because field count is checked after parsing, extra empty fields produce `InvalidValue` rather than `InvalidLength`.
- The first non-prefix character chooses the separator, so mixed separators are not accepted as intended.
- `forbid-guest` only expresses guest-to-host failure; there is no command-line host-forbid variant in this file.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/soft_idmap/cmdline.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/soft_idmap/id_types.rs -->
# File Research: sources/virtualization/virtiofsd/src/soft_idmap/id_types.rs

## Purpose

This file defines strongly typed UID/GID wrappers for host and guest ID domains. The goal is to prevent accidental mixing of host IDs, guest IDs, UIDs, and GIDs while still allowing range arithmetic needed by soft ID mapping.

## Main Traits

- `Id`: common trait for all ID wrappers. Requires copyability, formatting, ordering, thread-safety, conversion from the raw inner value, and subtraction. It exposes:
  - `type Inner`
  - `is_root()`
  - `into_inner()`

- `GuestId`: marks a guest-side UID/GID. It has:
  - associated `HostType`
  - `id_mapped()` for numeric identity conversion to the host domain
  - an addition bound allowing guest IDs to add offsets derived from host ID ranges

- `HostId`: marks a host-side UID/GID. It has:
  - associated `GuestType`
  - `id_mapped()` for numeric identity conversion to the guest domain
  - an addition bound allowing host IDs to add offsets derived from guest ID ranges

## Main Types

- `UidOffset(u32)`: offset between two UIDs.
- `GidOffset(u32)`: offset between two GIDs.
- `GuestUid(u32)`: guest UID.
- `GuestGid(u32)`: guest GID.
- `HostUid(libc::uid_t)`: host UID.
- `HostGid(libc::gid_t)`: host GID.

The concrete ID wrapper types are generated by `impl_ids!`.

## Macro Behavior

`impl_ids!` generates for each ID type:

- Transparent single-field struct.
- `Clone`, `Copy`, `Debug`, `Default`, `Eq`, `Ord`, `PartialEq`, `PartialOrd`.
- `From<inner>` constructor.
- `Id` implementation with root check and raw extraction.
- `GuestId` or `HostId` implementation with identity mapping.
- `Add<OffsetType>` to advance an ID by an offset.
- `Sub<Self>` to produce an offset between two IDs of the same type.
- `Display` by printing the raw value.

## Integration Points

`soft_idmap/mod.rs` re-exports these types and uses their trait bounds to build generic `IdMap<Guest, Host>` mappings for UID and GID domains. `server.rs` uses `GuestGid` when parsing FUSE supplementary group extensions.

The traits depend on `btree_range_map::{Measure, PartialEnum, RangePartialOrd}` so raw inner types can be keys in `RangeMap`.

## Important Invariants

- Host and guest IDs are distinct types even if they hold numerically equal values.
- UID and GID offsets are separate types, preventing cross-family arithmetic.
- Identity mapping is explicit via `id_mapped()`.
- `is_root()` is a numeric zero check for all ID types.
- Offset subtraction uses raw integer subtraction and assumes operands are ordered appropriately by callers.

## Risks And Edge Cases

- Subtracting a larger ID from a smaller ID can underflow for unsigned inner types.
- Adding offsets can overflow raw integer types; callers must construct ranges carefully.
- The comment for `HostGid` says “Host UID type” but describes a GID; this is a documentation typo, not a type issue.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/soft_idmap/id_types.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/soft_idmap/mod.rs -->
# File Research: sources/virtualization/virtiofsd/src/soft_idmap/mod.rs

## Purpose

This file implements runtime soft UID/GID mapping between guest and host ID domains. It converts parsed command-line mapping rules into efficient non-overlapping range maps and provides lookup functions in both directions.

## Module Structure

- `pub mod cmdline`: command-line syntax and parsing.
- `pub mod id_types`: strong host/guest UID/GID types.
- Re-exports: `GuestGid`, `GuestId`, `GuestUid`, `HostGid`, `HostId`, `HostUid`, `Id`.

## Main Types

- `IdMap<Guest, Host>`: bidirectional mapping container for one ID family, either UID or GID.
  - `guest_to_host: RangeMap<Guest::Inner, MapEntry<Guest, Host>>`
  - `host_to_guest: RangeMap<Host::Inner, MapEntry<Host, Guest>>`

- `MapEntry<Source, Target>`:
  - `Squash { from, to }`: maps a source range to one target ID.
  - `Range { from, to_base }`: maps a source range 1:1 to a target range.
  - `Fail { from }`: explicitly rejects source IDs.

- `MapError<Source>`:
  - `ExplicitFailMapping { id }`

## Mapping Behavior

`IdMap::empty()` creates maps with no explicit entries. Unmapped IDs are identity-mapped numerically through `id_mapped()`.

`map_guest(guest_id)` looks up the guest raw value in `guest_to_host`; if found, the matching `MapEntry` maps or fails the ID. If not found, it returns identity-mapped host ID.

`map_host(host_id)` does the same in the host-to-guest direction.

`MapEntry::map()`:

- `Squash`: returns the single configured target ID.
- `Range`: returns `to_base + (id - from.start)`.
- `Fail`: returns `MapError::ExplicitFailMapping`.

Each branch asserts that the ID is inside the source range.

## Construction And Validation

`do_push()` inserts a `MapEntry` into a `RangeMap`. It converts the typed source range to the raw inner range and rejects any entry that intersects an existing entry. On overlap, it returns an `io::Error` describing the map direction and conflicting entry.

`id_range_from_u32(base, count, param)` constructs a typed half-open range from `base..base+count`, returning `InvalidInput` if `base + count` overflows `u32`.

`TryFrom<Vec<cmdline::IdMap>> for IdMap<Guest, Host>` converts each command-line rule:

- `Guest`: adds guest-to-host `Range`.
- `Host`: adds host-to-guest `Range`.
- `SquashGuest`: adds guest-to-host `Squash`.
- `SquashHost`: adds host-to-guest `Squash`.
- `Bidirectional`: adds both directions as `Range`.
- `ForbidGuest`: adds guest-to-host `Fail`.

Errors are decorated with the original command-line entry using `ResultErrorContext`.

## Integration Points

This module consumes `cmdline::IdMap` and typed IDs from `id_types.rs`. It uses `btree_range_map::RangeMap` for intersection detection and lookup. Mapping errors convert to `io::ErrorKind::PermissionDenied`, allowing filesystem operations to fail naturally when a forbidden guest ID is used.

The module is used by virtiofsd soft ID mapping paths elsewhere in the crate, and `GuestGid` is used directly by FUSE extension parsing in `server.rs`.

## Important Invariants

- Explicit mappings in the same direction must not overlap.
- Guest-to-host and host-to-guest maps are independent; they do not need to be inverses.
- Empty maps are identity maps, not deny-all maps.
- Range ends are half-open.
- Runtime range construction checks overflow for most variants through `id_range_from_u32`.

## Risks And Edge Cases

- `ForbidGuest` constructs `(from_guest.into())..((from_guest + count).into())` directly and does not use `checked_add`; this can overflow in debug builds or wrap in release depending on compilation settings.
- `MapEntry::map()` uses assertions for containment, relying on `RangeMap` correctness.
- Arithmetic in ID wrappers can overflow or underflow if bad ranges slip through.
- Bidirectional mapping can fail halfway if the reverse direction overlaps after the forward entry was inserted, leaving the local construction object partially modified before returning an error. Since construction returns `Err`, callers should discard it.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/soft_idmap/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/util.rs -->
# File Research: sources/virtualization/virtiofsd/src/util.rs

## Purpose

This file provides utility functions for pid files, safer fork behavior, child waiting, capability manipulation, and lightweight error-context helpers used across virtiofsd.

## Main Functions And Traits

- `try_lock_file(file)`: acquires a non-blocking exclusive `flock`.
- `write_pid_file(pid_file_name)`: creates, locks, verifies, and writes the current process ID to a pid file.
- `pidfd_open(pid, flags)`: raw syscall wrapper for `pidfd_open`.
- `sfork()`: forks while arranging parent-death detection for the child.
- `wait_for_child(pid) -> !`: drops parent capabilities, waits for a child, and exits with the child’s status.
- `add_cap_to_eff(cap_name)`: adds a named Linux capability to the effective set using `capng`.
- `other_io_error(err)`: compatibility helper for `io::ErrorKind::Other`.
- `ErrorContext`: trait to prepend context to an `io::Error`.
- `ResultErrorContext`: trait to lazily add context to `Result` errors.

## PID File Handling

`write_pid_file()` loops until it can safely lock the actual current pid file path:

1. Opens/creates the file with mode `0600` and `O_CLOEXEC`.
2. Acquires `LOCK_EX | LOCK_NB`.
3. Compares the inode of the locked file descriptor with the inode currently reachable at the path.
4. Retries if the path was removed or replaced during the race.
5. Writes the current PID and returns the open file, keeping the lock alive.

This avoids stale locks on files that have been unlinked and replaced.

## Safe Fork Flow

`sfork()` uses `pidfd_open(getpid(), 0)` before `fork()` to hold a stable reference to the original parent. In the child:

1. It calls `prctl(PR_SET_PDEATHSIG, SIGTERM)` so the child receives SIGTERM if the parent dies.
2. It polls the parent pidfd with timeout 0 to detect whether the parent died before `prctl()` was set.
3. If the pidfd is readable, it returns an error indicating unexpected parent death.

The parent and child both return the `fork()` result like normal `fork`: child sees `0`, parent sees child PID.

## Child Waiting

`wait_for_child(pid)` clears all capabilities in the waiting parent, applies the change, waits for the child with `waitpid`, and exits with:

- the child exit code if it exited normally,
- negative signal number if it was signaled,
- failure for unexpected wait status or waitpid failure.

This function never returns.

## Capability Helper

`add_cap_to_eff(cap_name)` resolves a capability name without `CAP_`, refreshes process capabilities, adds it to the effective set, and applies the capability set.

## Error Helpers

`other_io_error()` exists because `io::Error::other()` was too new for this project’s target Rust version.

`ErrorContext` and `ResultErrorContext` allow code to add displayable context while preserving an `io::Error` kind. `soft_idmap/mod.rs` uses `err_context()` to attach the originating map entry to construction errors.

## Integration Points

This module is used by:

- `sandbox.rs` for `sfork()`, `wait_for_child()`, and contextual IO errors.
- `vhost_user.rs` and other modules through `other_io_error`.
- `soft_idmap/mod.rs` through `ResultErrorContext`.
- daemon startup code for pid files and capabilities.

## Risks And Edge Cases

- `sfork()` depends on `pidfd_open`, so it requires a kernel with that syscall.
- `wait_for_child()` exits the process and should only be called in a parent supervisory path.
- `write_pid_file()` returns an error if another process already holds the lock; it does not wait.
- `ErrorContext` recreates an `io::Error` with the same kind but a formatted string, so original OS error metadata beyond kind is not preserved.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/util.rs -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/virtiofsd/src/vhost_user.rs -->
# File Research: sources/virtualization/virtiofsd/src/vhost_user.rs

## Purpose

This file implements the vhost-user backend for virtio-fs. It connects guest virtqueues to the FUSE `Server`, negotiates virtio/vhost-user features, supports optional threaded request handling, exposes virtio-fs config, and coordinates device state save/load for migration.

## Main Constants And Types

- `QUEUE_SIZE`: 32768 descriptors.
- `REQUEST_QUEUES`: one request queue is supported.
- `NUM_QUEUES`: high-priority queue plus request queue.
- `HIPRIO_QUEUE_EVENT`, `REQ_QUEUE_EVENT`: device event indices.
- `MAX_TAG_LEN`: 36-byte virtio-fs tag limit.
- `LoggedMemory`: guest memory with dirty bitmap regions.
- `LoggedMemoryAtomic`: atomic guest memory wrapper.
- `Error`: backend setup and queue-processing failures.
- `VhostUserFsThread<F>`: internal per-backend state: guest memory, `Server<F>`, backend request FD, event-idx flag, and optional thread pool.
- `VirtioFsConfig`: packed virtio-fs config containing tag and request queue count.
- `PremigrationThread`: background serialization-preparation handle and cancellation flag.
- `VhostUserFsBackendBuilder`: builder for thread pool size and tag.
- `VhostUserFsBackend<F>`: public vhost-user backend implementing `VhostUserBackend`.

## Backend Construction

`VhostUserFsBackendBuilder` defaults to no thread pool and no tag. It can set:

- `thread_pool_size`: `0` means serial processing.
- `tag`: optional virtio-fs tag; when present the backend advertises `CONFIG`.

`build(fs)` creates a `VhostUserFsThread` wrapped in `RwLock`, plus migration state locks.

`VhostUserFsThread::new()` creates the `Server`. If a thread pool is requested, it first tests `unshare(CLONE_FS)` in the single-threaded setup phase. Worker threads call `unshare(CLONE_FS)` after start so xattr operations can change FS context without sharing it across threads.

## Queue Processing

Two processing modes exist.

Serial mode:

- `handle_event_serial()` picks the high-priority or request vring.
- `process_queue_serial()` collects available descriptor chains, creates `Reader` and `Writer`, calls `server.handle_message()`, and returns descriptors to the used ring.

Thread-pool mode:

- `handle_event_pool()` picks the vring by event.
- `process_queue_pool()` iterates available chains and spawns one async task per chain.
- Each task clones guest memory, server, backend request handle, vring, and descriptor chain; then it creates `Reader`/`Writer`, calls `server.handle_message()`, and returns the descriptor.

Both modes use `return_descriptor()` to add a used element and signal the used queue. With `EVENT_IDX`, it checks `needs_notification()` before signaling. Event handlers loop disable/process/enable while event-idx indicates more work may have arrived.

## VhostUserBackend Implementation

The backend reports:

- `num_queues()`: 2.
- `max_queue_size()`: 32768.
- `features()`: virtio version 1, indirect descriptors, event idx, protocol features, and log-all.
- `protocol_features()`: multiqueue, backend requests, backend send FD, reply ack, configurable memory slots, log shared memory FD, device state, reset device, and optional config.

Important methods:

- `get_config(offset, size)`: returns a sliced/padded `VirtioFsConfig` with the UTF-8 tag and one request queue.
- `acked_features(features)`: starts or cancels premigration preparation depending on `LOG_ALL`.
- `reset_device()`: calls `Server::destroy()`.
- `set_event_idx(enabled)`: stores negotiated event-idx mode.
- `update_memory(mem)`: stores guest memory.
- `handle_event(...)`: validates `EventSet::IN` and dispatches serial or pool handling.
- `exit_event(...)`: creates an eventfd consumer/notifier pair.
- `set_backend_req_fd(vu_req)`: stores backend request channel.
- `set_device_state_fd(...)`: starts save/load state transfer.
- `check_device_state()`: joins the migration thread and reports its result.

## Migration Flow

Premigration:

- When `LOG_ALL` is acknowledged, `acked_features()` starts a background thread calling `server.prepare_serialization(cancel)`, unless one is already running.
- When `LOG_ALL` is cleared, any premigration thread is canceled and joined.

State save:

- `do_set_device_state_fd(SAVE, STOPPED, file)` takes the premigration thread, joins it if present, or warns and runs `prepare_serialization()` synchronously if no premigration happened.
- It then calls `server.serialize(file)` in a migration thread.

State load:

- `do_set_device_state_fd(LOAD, STOPPED, file)` cancels any premigration thread and starts a migration thread calling `server.deserialize_and_apply(file)`.

Completion:

- `do_check_device_state()` requires a prior migration thread and joins it. Missing migration state is treated as a protocol violation.

Only `VhostTransferStatePhase::STOPPED` is supported.

## Tag Config Behavior

If a tag is configured, the backend advertises the `CONFIG` protocol feature. `get_config()` asserts the tag is non-empty and at most 36 UTF-8 bytes, pads it with NUL bytes to `MAX_TAG_LEN`, and returns the requested config slice padded to the requested size.

`Error::InvalidTag` documents the tag constraints, though validation is expected before `get_config()`.

## Integration Points

This module integrates with:

- `crate::server::Server`, which handles FUSE protocol messages.
- `crate::filesystem::{FileSystem, SerializableFileSystem}` as the backend abstraction.
- `crate::descriptor_utils::{Reader, Writer}` for guest descriptor chains.
- `vhost_user_backend::{VhostUserBackend, Vring*}` for event and vring mechanics.
- `vhost::vhost_user::Backend` for backend requests.
- `vm_memory` and `BitmapMmapRegion` for guest memory and migration logging.
- `futures::executor::ThreadPool` for optional parallel request processing.

## Important Invariants

- Guest memory must be configured before queue processing.
- Only high-priority queue index 0 and request queue index 1 are valid events.
- Queue processing unwraps descriptor reader/writer and server errors inside worker paths, so these are treated as unrecoverable for that task.
- With thread-pool mode, descriptor completion happens asynchronously after `handle_event_pool()` returns.
- `event_idx` mode requires repeated processing until enabling notification reports no more pending events.
- Migration state uses locks so only one premigration thread and one migration thread are tracked.

## Risks And Edge Cases

- Worker tasks use `unwrap()` after mapping errors; malformed descriptors or server errors can panic worker execution.
- Thread-pool mode clones and processes vring state asynchronously; correctness depends on `VringMutex` and descriptor ownership semantics.
- `acked_features()` cancellation behavior for `LOG_ALL` clearing is acknowledged as an interpretation rather than a guaranteed spec signal.
- If the frontend calls `check_device_state()` without a prior successful `set_device_state_fd()`, the backend returns `InvalidInput`.
- `get_config()` panics if called when no tag is configured, relying on feature negotiation to prevent that call.
<!-- END FILE RESEARCH: sources/virtualization/virtiofsd/src/vhost_user.rs -->