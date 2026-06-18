# Group Research: group_880_linux_sources_os_linux_linux_include_linux_fs_h_sources_os_linux_lin_f00e873b644b

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/include/linux/fs.h -->
# File Research: sources/os/linux/linux/include/linux/fs.h

## Purpose
Central Linux VFS header defining core filesystem, inode, file, address-space, I/O, permission, timestamp, mount, and generic helper interfaces used across the kernel.

## Main Contents
- Access and open-mode flags: `MAY_*`, `FMODE_*`, `ATTR_*`, inode `S_*` flags, filesystem `FS_*` flags, `IOCB_*` flags, remap/copy flags.
- Core structures:
  - `struct iattr`: VFS attribute changes, including idmapped-mount-aware uid/gid aliases.
  - `struct kiocb`: kernel I/O control block for sync/async reads and writes.
  - `struct address_space_operations` and `struct address_space`: page-cache and mapping operations/state.
  - `struct inode`: core inode object with operation pointers, timestamps, writeback state, locks, reference counts, file ops, fsnotify state, and private data.
  - `struct file`: open-file object with mode/ops/mapping/path/position/readahead/reference state.
  - `struct file_operations` and `struct inode_operations`: primary VFS operation tables.
  - `struct file_system_type`: filesystem driver registration contract.
  - `struct filename`, `struct delayed_filename`, `struct offset_ctx`, `struct renamedata`, `struct dir_context`.
- Inline helpers for inode locking, mapping locks, `i_size` access, uid/gid idmap translation, timestamp get/set, dirty marking, link count updates, file reference access, DAX checks, write-freeze accounting, write-access denial, directory emit helpers, and `kiocb` flag setup.
- VFS API declarations for create/link/unlink/rename/mkdir/mknod/symlink, open/close, stat/statfs, truncate/fallocate, read/write/copy/remap, fsync, direct I/O, inode lookup/allocation/eviction, generic file helpers, simple filesystem helpers, casefolding, xattr/security-related setattr preparation, fadvise, and char-device registration.

## Important Design Points
- This header is a major kernel-wide contract. Changes to structures or operation tables affect filesystems, drivers, memory management, io_uring, security, fsnotify, block code, and proc/debug paths.
- `struct inode` and `struct file` are arranged for hot-path access and use `__randomize_layout`; comments document locking and lifetime expectations.
- `i_size_read()` / `i_size_write()` have architecture-specific ordering and seqcount behavior for 32-bit SMP/preemptible kernels.
- Idmapped mount helpers (`i_uid_into_vfsuid()`, `i_uid_update()`, `inode_fsuid_set()`, etc.) are embedded in the generic VFS contract.
- `file_operations` includes modern hooks for io_uring commands, iopoll, async buffered I/O capability flags, copy/remap, and the newer `mmap_prepare` compatibility path.
- `kiocb_set_rw_flags()` validates `RWF_*` against file capabilities such as `FMODE_NOWAIT`, `FMODE_CAN_ATOMIC_WRITE`, `FOP_DONTCACHE`, append restrictions, and DAX exclusions.

## Cross-File Relationships
- `include/linux/namei.h` builds on types and helpers from this file for path lookup and directory operation lifetimes.
- io_uring files in this group use `struct file`, `struct inode`, `struct file_operations`, `vfs_fadvise()`, delayed filenames, eventfd/proc callbacks, and `io_uring_cmd` hooks rooted here.
- Almost every Linux filesystem implementation depends on the operation tables, inode/file layout, and generic helpers declared here.

## Risks / Review Notes
- Structure layout changes are high risk because many subsystems depend on exact fields, locking, and lifetime rules.
- Helper semantics often encode subtle locking requirements, especially inode state, `i_rwsem` subclasses, mapping invalidation locks, direct I/O counters, and superblock freeze write accounting.
- `file_dentry()` intentionally warns if `f_path.dentry` and `f_inode` disagree, reflecting overlayfs/backing-file historical pitfalls.
- `mmap` and `mmap_prepare` hooks are mutually exclusive; `can_mmap_file()` warns and rejects invalid dual-hook configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux/include/linux/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/include/linux/namei.h -->
# File Research: sources/os/linux/linux/include/linux/namei.h

## Purpose
Declares Linux pathname lookup/pathwalk interfaces, lookup flags, and helper wrappers for create/remove/rename operations.

## Main Contents
- Symlink recursion limits: `MAX_NESTED_LINKS`, `MAXSYMLINKS`.
- Pathwalk flags:
  - Basic lookup behavior: `LOOKUP_FOLLOW`, `LOOKUP_DIRECTORY`, `LOOKUP_AUTOMOUNT`, `LOOKUP_EMPTY`, `LOOKUP_MOUNTPOINT`, `LOOKUP_RCU`, `LOOKUP_CACHED`, `LOOKUP_PARENT`.
  - Final-component intent flags: `LOOKUP_OPEN`, `LOOKUP_CREATE`, `LOOKUP_EXCL`, `LOOKUP_RENAME_TARGET`.
  - Scoped lookup restrictions: `LOOKUP_NO_SYMLINKS`, `LOOKUP_NO_MAGICLINKS`, `LOOKUP_NO_XDEV`, `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, `LOOKUP_IS_SCOPED`.
- Path lookup APIs: `user_path_at()`, `kern_path()`, `kern_path_parent()`, `vfs_path_lookup()`, `vfs_path_parent_lookup()`.
- Single-component lookup helpers: `lookup_one()`, unlocked/positive variants, and permission-skipping variants.
- Directory operation lifetime helpers: `start_creating*()`, `start_removing*()`, `end_creating()`, `end_creating_keep()`, `end_removing()`, path variants, and rename start/end helpers.
- Mount traversal helpers: `follow_down_one()`, `follow_down()`, `follow_up()`.
- Utility helpers: `mode_strip_umask()`, `nd_jump_link()`, `nd_terminate_link()`, `retry_estale()`.

## Important Design Points
- Lookup flags are split into pathwalk mode, final-component intent, and scoping groups.
- Create/remove helpers centralize locking, lookup, and dentry lifetime handling for VFS operations.
- `mode_strip_umask()` defers umask stripping for POSIX ACL filesystems and honors `SB_I_NOUMASK`.
- `retry_estale()` implements the common “retry once with `LOOKUP_REVAL`” pattern for stale dentries.

## Cross-File Relationships
- Depends on `fs.h` for `struct renamedata`, inode/superblock helpers, `end_dirop()`, and VFS mode/ACL checks.
- Used by io_uring filesystem opcodes in `io_uring/fs.c` through delayed filename and filename-based VFS helpers.
- Lookup flags are consumed by VFS pathwalk/namei implementation outside this header.

## Risks / Review Notes
- Scoped lookup flags are security-sensitive; incorrect combinations can allow path escape, symlink/magic-link traversal, or mount crossing.
- `end_creating_keep()` takes an extra dentry reference before ending the directory operation; callers must manage the returned reference.
- `retry_estale()` only retries if `LOOKUP_REVAL` was not already set.
<!-- END FILE RESEARCH: sources/os/linux/linux/include/linux/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/Kconfig -->
# File Research: sources/os/linux/linux/io_uring/Kconfig

## Purpose
Defines optional io_uring feature configuration symbols.

## Main Contents
- `IO_URING_ZCRX`: enabled by default when io_uring, page pool, INET, and NET_RX_BUSY_POLL are available.
- `IO_URING_BPF`: enabled by default when BPF and networking are available.
- `IO_URING_BPF_OPS`: enabled by default when io_uring, BPF syscall support, BPF JIT, and BTF debug info are available.

## Cross-File Relationships
- Controls compilation of `zcrx.o`, `bpf_filter.o`, and `bpf-ops.o` through the local Makefile.
- Feature guards match conditional code in `bpf_filter.h`, `bpf-ops.h`, and network/NAPI paths.

## Risks / Review Notes
- These are `def_bool y` feature gates driven entirely by dependencies; there are no user-visible prompts or sub-options in this file.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/Makefile -->
# File Research: sources/os/linux/linux/io_uring/Makefile

## Purpose
Builds the io_uring subsystem objects according to kernel configuration.

## Main Contents
- Enables GCOV profiling for io_uring when `CONFIG_GCOV_PROFILE_URING` is set.
- Core `CONFIG_IO_URING` object list includes submission/completion core, opcode definitions, buffers/resources, files, rw, poll, task work, wait, eventfd, uring commands, open/close, sqpoll, xattr, nop, fs ops, splice, sync, msg_ring, advise, statx, timeout, cancel, waitid, register, truncate, memmap, allocation cache, query, and loop.
- Conditional objects: `zcrx.o`, `io-wq.o`, `futex.o`, `epoll.o`, `napi.o`, `net.o`, `cmd_net.o`, `fdinfo.o`, `mock_file.o`, `bpf_filter.o`, `bpf-ops.o`.

## Cross-File Relationships
- Shows which files in this research group are core io_uring objects versus config-dependent support modules.
- `openclose.o` appears twice in the core list, which Kbuild de-duplicates operationally but is worth noticing during maintenance.

## Risks / Review Notes
- Feature boundaries are compile-time; headers in this group provide stub behavior for disabled configs where needed.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/advise.c -->
# File Research: sources/os/linux/linux/io_uring/advise.c

## Purpose
Implements io_uring `madvise` and `fadvise` opcodes.

## Main Functions
- `io_madvise_prep()`: validates unused SQE fields, extracts address/length/advice, and forces async execution when advice syscalls and MMU are available.
- `io_madvise()`: calls `do_madvise()` and completes the request.
- `io_fadvise_force_async()`: identifies fadvise modes that must run asynchronously.
- `io_fadvise_prep()`: validates SQE fields and extracts offset/length/advice.
- `io_fadvise()`: calls `vfs_fadvise()` on `req->file`, marks failed requests, and completes.

## Important Design Points
- `madvise` support is gated by `CONFIG_ADVISE_SYSCALLS` and `CONFIG_MMU`; otherwise prep/issue returns `-EOPNOTSUPP`.
- `madvise` is always forced async because it works on `current->mm`.
- `fadvise` only forces async for advice values outside normal/random/sequential.
- Both operations reject `buf_index` and `splice_fd_in`.

## Cross-File Relationships
- Uses `vfs_fadvise()` declared in `fs.h`.
- Operation prototypes are declared in `advise.h` and wired through io_uring opcode definitions elsewhere.

## Risks / Review Notes
- `sqe->off`, `sqe->addr`, and `sqe->len` carry different meanings between `madvise` and `fadvise`; opcode prep must remain aligned with the userspace ABI.
- `io_fadvise()` warns if forced-async advice reaches nonblocking issue context.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/advise.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/advise.h -->
# File Research: sources/os/linux/linux/io_uring/advise.h

## Purpose
Declares io_uring advise opcode prep and issue functions.

## Main Contents
- Prototypes for `io_madvise_prep()`, `io_madvise()`, `io_fadvise_prep()`, and `io_fadvise()`.

## Cross-File Relationships
- Implemented by `advise.c`.
- Consumed by io_uring opcode dispatch definitions.

## Risks / Review Notes
- No include guard is present; this matches small local io_uring headers but should be preserved only if include patterns remain simple.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/advise.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/alloc_cache.c -->
# File Research: sources/os/linux/linux/io_uring/alloc_cache.c

## Purpose
Implements a small reusable object allocation cache for io_uring internals.

## Main Functions
- `io_alloc_cache_init()`: allocates the pointer array and initializes cache limits, element size, and initial clear size.
- `io_alloc_cache_free()`: drains cached objects with a caller-supplied free function, then frees the pointer array.
- `io_cache_alloc_new()`: allocates a new object and zeroes the configured prefix.

## Important Design Points
- `io_alloc_cache_init()` returns `true` on failure and `false` on success.
- The cache stores object pointers in a `kvmalloc_array()` allocation.
- Only the initial `init_clear` bytes are zeroed for newly allocated objects.

## Cross-File Relationships
- Inline cache get/put helpers are in `alloc_cache.h`.
- Used by futex wait support in `futex.c` and other io_uring request/cache paths.

## Risks / Review Notes
- The inverted boolean return convention is easy to misuse.
- Freeing requires callers to supply a function compatible with cached object allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/alloc_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/alloc_cache.h -->
# File Research: sources/os/linux/linux/io_uring/alloc_cache.h

## Purpose
Defines the io_uring allocation cache API and inline fast paths.

## Main Contents
- `IO_ALLOC_CACHE_MAX` cap of 128 cached entries.
- Prototypes for cache init/free/new allocation.
- Inline helpers:
  - `io_alloc_cache_put()`: poisons and stores an object if capacity remains.
  - `io_alloc_cache_get()`: pops cached object and, under KASAN, unpoisons and clears the configured prefix.
  - `io_cache_alloc()`: get cached object or allocate new.
  - `io_cache_free()`: cache object or free it.

## Important Design Points
- KASAN mempool poisoning is integrated into cache put/get.
- Cached objects are not generally reinitialized unless KASAN is enabled; callers must ensure reused fields are reset or covered by `init_clear`.
- Overflow objects are freed via `kvfree()` in `io_cache_free()`.

## Cross-File Relationships
- Backed by `alloc_cache.c`.
- Used by `futex.c` for `struct io_futex_data` cache management.

## Risks / Review Notes
- Reuse safety depends on each user choosing a correct `init_clear` and clearing any state that must not persist.
- Mixing `kmalloc()` allocation with `kvfree()` is supported but should remain intentional.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/alloc_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/bpf-ops.c -->
# File Research: sources/os/linux/linux/io_uring/bpf-ops.c

## Purpose
Implements BPF struct-ops integration for io_uring loop control and exposes selected io_uring kfuncs to BPF.

## Main Functions
- BPF kfuncs:
  - `bpf_io_uring_submit_sqes()`: submits SQEs for a ring.
  - `bpf_io_uring_get_region()`: returns pointers to mapped io_uring memory/CQ/SQ regions after size validation and with `uring_lock` held.
- BPF verifier support:
  - `bpf_io_is_valid_access()`
  - `bpf_io_btf_struct_access()`
  - `bpf_io_init()`
- Struct-ops lifecycle:
  - `io_install_bpf()`: validates ring mode and installs ops into a context.
  - `bpf_io_reg()`: resolves ring fd, locks, and installs BPF ops.
  - `bpf_io_unreg()` / `io_unregister_bpf_ops()`: eject installed ops safely.
- Module init:
  - `io_uring_bpf_init()`: registers `io_uring_bpf_ops` BPF struct ops.

## Important Design Points
- BPF ops require rings without SQPOLL or IOPOLL and require `IORING_SETUP_DEFER_TASKRUN`.
- Installed ops set `ctx->loop_step`, allowing BPF to participate in ring loop progression.
- `io_bpf_ctrl_mutex` serializes global install/uninstall with per-ring `uring_lock`.
- BTF type lookup requires `struct iou_loop_params`.
- Kfunc region access is restricted to known region IDs and size-checked.

## Cross-File Relationships
- Declares the ops structure in `bpf-ops.h`.
- Uses io_uring core submission, loop, register, and memmap helpers.
- `io_unregister_bpf_ops()` is called during ring teardown to detach BPF state.

## Risks / Review Notes
- Lock ordering between `io_bpf_ctrl_mutex` and `ctx->uring_lock` is intentional; changes can introduce deadlocks.
- `bpf_io_btf_struct_access()` allows only a prefix of `iou_loop_params`; expanding BPF-visible fields requires verifier updates.
- Install rejects several ring modes, so callers must expect `-EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/bpf-ops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/bpf-ops.h -->
# File Research: sources/os/linux/linux/io_uring/bpf-ops.h

## Purpose
Defines io_uring BPF struct-ops types and unregister hook.

## Main Contents
- Region IDs: `IOU_REGION_MEM`, `IOU_REGION_CQ`, `IOU_REGION_SQ`.
- `struct io_uring_bpf_ops` with:
  - `loop_step` callback.
  - `ring_fd` userspace-selected ring fd.
  - `priv` installed ring context pointer.
- Conditional `io_unregister_bpf_ops()` declaration or no-op stub.

## Cross-File Relationships
- Implemented by `bpf-ops.c`.
- Used by io_uring context teardown and BPF struct-ops registration.

## Risks / Review Notes
- `priv` is owned by install/uninstall paths and protected by locking rules in `bpf-ops.c`; direct consumers must not treat it as generally stable.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/bpf-ops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/bpf_filter.c -->
# File Research: sources/os/linux/linux/io_uring/bpf_filter.c

## Purpose
Implements classic BPF filters for io_uring restrictions, allowing registered filters to allow or deny SQE opcodes based on an io_uring BPF context.

## Main Functions
- `io_uring_populate_bpf_ctx()`: fills `struct io_uring_bpf_ctx` from a request and optional opcode-specific PDU data.
- `__io_uring_run_bpf_filters()`: runs all registered filters for a request opcode; any zero return denies the request.
- `io_uring_check_cbpf_filter()`: validates and rewrites classic BPF instructions to a safe subset over the io_uring context.
- `io_new_bpf_filters()`, `io_free_bpf_filters()`, `io_put_bpf_filters()`: allocate/free reference-counted filter sets.
- `io_bpf_filter_clone()` and `io_bpf_filter_cow()`: clone filters for restrictions with copy-on-write.
- `io_bpf_filter_import()`: imports and validates userspace registration data, opcode, flags, reserved fields, filter length, and PDU size.
- `io_register_bpf_filter()`: creates a BPF program from userspace instructions and installs it into the per-opcode filter list.

## Important Design Points
- Filters are per opcode and stacked in a linked list; all filters must allow the request.
- `dummy_filter` represents an unconditional deny entry and is used by `IO_URING_BPF_FILTER_DENY_REST`.
- Filter sets are RCU-protected and reference counted.
- Copy-on-write avoids mutating cloned restriction filter sets directly.
- Accepted classic BPF is intentionally constrained: context loads, length loads, ALU, memory, and basic jumps; packet data access is not allowed.
- PDU size negotiation supports strict and non-strict behavior and copies the kernel PDU size back to userspace.

## Cross-File Relationships
- Public/stub declarations are in `bpf_filter.h`.
- Uses opcode metadata from `io_issue_defs`, including optional filter PDU populate callbacks from specific opcode implementations.
- `openclose` and `net` headers are included for opcode-specific filter context population support.

## Risks / Review Notes
- RCU/refcount ownership is subtle: freeing stops walking a filter chain when a node still has references.
- `DENY_REST` fills only currently empty opcode slots; existing filters are preserved.
- Filter instruction validation mutates some BPF load instructions before program creation.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/bpf_filter.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/bpf_filter.h -->
# File Research: sources/os/linux/linux/io_uring/bpf_filter.h

## Purpose
Provides the io_uring BPF filter API with config-dependent stubs.

## Main Contents
- Under `CONFIG_IO_URING_BPF`:
  - `__io_uring_run_bpf_filters()`
  - `io_register_bpf_filter()`
  - `io_put_bpf_filters()`
  - `io_bpf_filter_clone()`
  - Inline `io_uring_run_bpf_filters()`.
- Without BPF support:
  - Registration returns `-EINVAL`.
  - Running filters is a no-op success.
  - Put/clone are no-ops.

## Cross-File Relationships
- Implemented by `bpf_filter.c`.
- Used by io_uring restriction setup and request validation paths.

## Risks / Review Notes
- Stub behavior means code can call filter APIs unconditionally, but registration failure semantics differ when config is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/bpf_filter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/cancel.c -->
# File Research: sources/os/linux/linux/io_uring/cancel.c

## Purpose
Implements io_uring async and sync cancellation across io-wq work, poll, waitid, futex, timeout, uring command, deferred, iopoll, and task-exit paths.

## Main Functions
- Matching and basic cancellation:
  - `io_cancel_req_match()`: matches requests by context, fd, opcode, user data, any/all flags, and cancel sequence.
  - `io_async_cancel_prep()`: validates cancel SQE and imports match criteria.
  - `io_try_cancel()`: tries io-wq, poll, waitid, futex, and timeout cancellation.
  - `io_async_cancel()`: executes an async cancel request and completes it.
- Sync cancellation:
  - `io_sync_cancel()`: handles registered sync cancel with optional timeout, fd lookup, wait/retry loop, and task work execution.
- Shared list helpers:
  - `io_cancel_remove_all()`
  - `io_cancel_remove()`
  - `io_match_task_safe()`
- Task/ring teardown:
  - `io_uring_try_cancel_requests()`: cancels outstanding requests for a context/task.
  - `io_uring_cancel_generic()`: exit/exec cancellation loop for a task’s io_uring contexts.
  - `__io_uring_cancel()`: unregisters ring fd and invokes generic cancel.
- Specialized helpers:
  - `io_cancel_defer_files()`
  - `io_uring_try_cancel_iowq()`
  - `io_cancel_ctx_cb()`

## Important Design Points
- `CANCEL_FLAGS` whitelists supported userspace cancel flags.
- Cancel matching defaults to user data when neither fd nor opcode matching is requested.
- `cancel_seq` prevents an `ASYNC_CANCEL_ALL` style operation from matching the same request repeatedly.
- `io_try_cancel()` continues past `-EALREADY` from io-wq to unarm poll/timeouts where possible.
- Sync cancel with `-EALREADY` waits on `ctx->cq_wait`, runs task work, and retries until completion, timeout, signal, or no matching request.
- Exit cancellation drains multiple sources: io-wq, iopoll, local task work, deferred files, poll, waitid, futex, uring_cmd, and timeouts.

## Cross-File Relationships
- Declared in `cancel.h`.
- Calls into `io-wq`, `poll`, `timeout`, `waitid`, `futex`, `uring_cmd`, `sqpoll`, `tw`, and resource/file helpers.
- Used by fdinfo to display poll/cancel table state.

## Risks / Review Notes
- Cancellation correctness depends on each subsystem exposing pending and running requests consistently.
- `io_match_task_safe()` must take `timeout_lock` for linked timeout races.
- Sync cancel temporarily drops `uring_lock` while waiting and must reacquire it before returning.
- Fixed-file cancellation must repeatedly look up fixed slots because `uring_lock` can be dropped.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/cancel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/cancel.h -->
# File Research: sources/os/linux/linux/io_uring/cancel.h

## Purpose
Defines shared cancellation data and declarations for io_uring cancellation paths.

## Main Contents
- `struct io_cancel_data`: context, user data, file, opcode, flags, and cancel sequence.
- Prototypes for async cancel prep/issue, generic try-cancel, sync cancel, request matching, task-safe matching, list removal helpers, context cancellation, and generic task cancellation.
- `io_cancel_match_sequence()`: inline helper that records and detects per-request cancel sequence reuse.

## Cross-File Relationships
- Implemented mainly by `cancel.c`.
- Included by `futex.h`, `fdinfo.c`, and other cancel-aware io_uring modules.

## Risks / Review Notes
- `io_cancel_match_sequence()` mutates request cancel sequence state; it must only be used as part of the intended cancel matching flow.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/cancel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/cmd_net.c -->
# File Research: sources/os/linux/linux/io_uring/cmd_net.c

## Purpose
Implements socket-specific `io_uring_cmd` operations for socket ioctls, sockopts, TX timestamps, and getsockname/getpeername-style queries.

## Main Functions
- `io_uring_cmd_get_sock_ioctl()`: calls protocol `ioctl` for `SIOCINQ`/`SIOCOUTQ`.
- `io_uring_cmd_getsockopt()`: supports `SOL_SOCKET` getsockopt and returns resulting optlen.
- `io_uring_cmd_setsockopt()`: calls socket setsockopt with userspace optval.
- `io_uring_cmd_timestamp()`: multishot timestamp command using the socket error queue and 32-byte CQEs.
- `io_process_timestamp_skb()`: extracts TX timestamp data and posts CQE32 multishot completions.
- `io_uring_cmd_getsockname()`: validates SQE fields and calls `do_getsockname()` with peer selector.
- `io_uring_cmd_sock()`: dispatches socket uring command opcodes and exports the symbol.

## Important Design Points
- TX timestamp command requires CQE32 support and uses `IORING_CQE_F_MORE`, timestamp type flags, and hardware timestamp flag.
- Timestamp processing removes eligible SKBs from the socket error queue, posts completions, and splices unprocessed SKBs back.
- `getsockopt` only supports `SOL_SOCKET` here.
- Compat handling is taken from `issue_flags & IO_URING_F_COMPAT`.

## Cross-File Relationships
- Uses `uring_cmd.h` and io_uring command completion helpers.
- Exported as `io_uring_cmd_sock()` for socket file operations to call.
- Depends on networking socket helpers and timestamp/error-queue APIs.

## Risks / Review Notes
- TX timestamp path is multishot and returns `-EAGAIN` to stay armed.
- Unsupported socket command operations return `-EOPNOTSUPP`, not generic ioctl fallback.
- `io_uring_cmd_getsockname()` rejects several SQE fields and allows `peer` only as 0 or 1.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/cmd_net.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/epoll.c -->
# File Research: sources/os/linux/linux/io_uring/epoll.c

## Purpose
Implements io_uring epoll control and epoll wait opcodes.

## Main Functions
- `io_epoll_ctl_prep()`: validates SQE fields, extracts epfd/op/fd, and copies `epoll_event` from userspace when required.
- `io_epoll_ctl()`: calls `do_epoll_ctl()` and supports nonblocking `-EAGAIN` retry behavior.
- `io_epoll_wait_prep()`: validates SQE fields and stores maxevents/events pointer.
- `io_epoll_wait()`: calls `epoll_sendevents()` and returns `-EAGAIN` if no events are ready.

## Important Design Points
- `io_epoll_ctl()` respects `IO_URING_F_NONBLOCK` via `force_nonblock`.
- `io_epoll_wait()` is naturally retryable when no events are available.
- Prep rejects unused SQE fields to preserve ABI strictness.

## Cross-File Relationships
- Declarations are in `epoll.h`.
- Compiled only with `CONFIG_EPOLL`.
- Uses core eventpoll helpers from the kernel epoll subsystem.

## Risks / Review Notes
- `copy_from_user()` is done during prep for event-bearing epoll ctl operations.
- `epoll_wait` stores userspace event pointer and relies on issue-time helper behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/epoll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/epoll.h -->
# File Research: sources/os/linux/linux/io_uring/epoll.h

## Purpose
Declares io_uring epoll opcode handlers when epoll support is enabled.

## Main Contents
- Under `CONFIG_EPOLL`, prototypes for epoll ctl prep/issue and epoll wait prep/issue.

## Cross-File Relationships
- Implemented by `epoll.c`.
- Included by opcode dispatch definitions.

## Risks / Review Notes
- No disabled-config stubs are provided here; callers must be config-aware.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/epoll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/eventfd.c -->
# File Research: sources/os/linux/linux/io_uring/eventfd.c

## Purpose
Implements eventfd registration, unregistration, and CQ event signaling for io_uring.

## Main Structures
- `struct io_ev_fd`: holds the registered eventfd context, async-only flag, last CQ tail seen, refs, pending operation bits, and RCU callback.

## Main Functions
- `io_eventfd_register()`: installs an eventfd for a ring, initializes last CQ tail, flags, refs, and RCU pointer.
- `io_eventfd_unregister()`: clears ring eventfd state and drops the reference.
- `io_eventfd_signal()`: signals the registered eventfd when completions are posted, respecting disabled CQ flags and async-only mode.
- Internal helpers manage RCU freeing and deferred signaling when direct eventfd signaling is not allowed.

## Important Design Points
- Eventfd state is RCU-protected through `ctx->io_ev_fd`.
- `eventfd_async` restricts signaling to io-wq workers.
- `cqe_event` mode avoids signaling if `cached_cq_tail` did not advance since the last eventfd signal.
- If `eventfd_signal_allowed()` is false, signaling is deferred via RCU callback and `call_rcu_hurry()`.

## Cross-File Relationships
- Declared in `eventfd.h`.
- Uses `io_wq_current_is_worker()` from `io-wq.h`.
- Integrated with io_uring register/unregister operations and completion posting.

## Risks / Review Notes
- Reference handling is split between RCU readers and deferred callbacks; missing `io_eventfd_put()` would leak.
- Signal suppression based on CQ tail is important because applications may rely on eventfd count changing only when new CQEs appear.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/eventfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/eventfd.h -->
# File Research: sources/os/linux/linux/io_uring/eventfd.h

## Purpose
Declares io_uring eventfd registration and signaling functions.

## Main Contents
- Forward declaration for `struct io_ring_ctx`.
- Prototypes for `io_eventfd_register()`, `io_eventfd_unregister()`, and `io_eventfd_signal()`.

## Cross-File Relationships
- Implemented by `eventfd.c`.
- Used by io_uring registration and completion paths.

## Risks / Review Notes
- `io_eventfd_signal()` takes a `cqe_event` boolean that changes suppression semantics; callers must choose it consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/eventfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/fdinfo.c -->
# File Research: sources/os/linux/linux/io_uring/fdinfo.c

## Purpose
Implements `/proc/<pid>/fdinfo` reporting for io_uring file descriptors.

## Main Functions
- `io_uring_show_fdinfo()`: public entry point; tries to lock the ring and emits diagnostic state.
- `__io_uring_show_fdinfo()`: prints SQ/CQ state, visible SQEs/CQEs, SQPOLL thread stats, registered files/buffers, poll list, CQ overflow list, and optional NAPI state.
- NAPI helpers under `CONFIG_NET_RX_BUSY_POLL`: show disabled/dynamic/static tracking and busy-poll settings.

## Important Design Points
- Uses `mutex_trylock(&ctx->uring_lock)` to avoid ABBA deadlock with seq-file locking.
- SQ/CQ observations are intentionally imprecise under concurrent activity.
- Handles SQE128 and mixed SQE layouts, including invalid/corrupt SQE diagnostics.
- CQE32 entries are displayed with extra fields.
- Registered files are displayed through `seq_file_path()`.

## Cross-File Relationships
- Declared in `fdinfo.h`.
- Uses file table helpers, sqpoll state, cancellation table, resource table, opcode names, and NAPI settings.
- Compiled when `CONFIG_PROC_FS` is enabled.

## Risks / Review Notes
- Because it uses trylock, fdinfo may emit nothing if the ring lock is contended.
- It reads user-mutated ring head/tail values and internal cached values without full synchronization for diagnostic purposes.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/fdinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/fdinfo.h -->
# File Research: sources/os/linux/linux/io_uring/fdinfo.h

## Purpose
Declares the io_uring fdinfo display hook.

## Main Contents
- Prototype for `io_uring_show_fdinfo()`.

## Cross-File Relationships
- Implemented by `fdinfo.c`.
- Hooked through io_uring file operations when proc fdinfo is available.

## Risks / Review Notes
- Minimal header with no guard; include usage is local and simple.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/fdinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/filetable.c -->
# File Research: sources/os/linux/linux/io_uring/filetable.c

## Purpose
Implements io_uring fixed-file table allocation, installation, removal, and allocation-range registration.

## Main Functions
- `io_alloc_file_tables()`: allocates resource data and bitmap for registered file slots.
- `io_free_file_tables()`: frees resource data and bitmap.
- `io_file_bitmap_get()`: finds an available slot within the configured allocation range.
- `io_install_fixed_file()`: installs a file into a fixed slot after validation and resource-node allocation.
- `__io_fixed_fd_install()` / `io_fixed_fd_install()`: install a file into a caller-specified or auto-allocated fixed slot.
- `io_fixed_fd_remove()`: removes a fixed file slot and clears its bitmap.
- `io_register_file_alloc_range()`: imports and validates the auto-allocation slot range.

## Important Design Points
- io_uring files themselves cannot be installed as fixed files.
- Userspace fixed slot indices are one-based except `IORING_FILE_INDEX_ALLOC`, which requests automatic allocation.
- Bitmap allocation tracks occupied slots and the next allocation hint.
- File pointer flags are stored in the resource node by `io_fixed_file_set()` from `filetable.h`.

## Cross-File Relationships
- Header helpers are in `filetable.h`.
- Uses resource helpers from `rsrc`.
- Used by open/install fixed-fd operations and cancel paths that resolve fixed files.

## Risks / Review Notes
- `io_fixed_fd_install()` consumes the passed file on error via `fput()`.
- Allocation range validation checks overflow and reserved fields.
- Slot bitmap and resource table must stay synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/filetable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/filetable.h -->
# File Research: sources/os/linux/linux/io_uring/filetable.h

## Purpose
Defines io_uring fixed-file table APIs and inline slot/flag helpers.

## Main Contents
- Prototypes for file table allocation/free, fixed fd install/remove, allocation-range registration, and `io_file_get_flags()`.
- Bitmap helpers:
  - `io_file_bitmap_clear()`
  - `io_file_bitmap_set()`
- Encoded slot flags:
  - `FFS_NOWAIT`
  - `FFS_ISREG`
  - `FFS_MASK`
- Slot helpers:
  - `io_slot_flags()`
  - `io_slot_file()`
  - `io_fixed_file_set()`
  - `io_file_table_set_alloc_range()`

## Important Design Points
- Low bits of `node->file_ptr` encode fixed-file capability flags; the masked value is the actual `struct file *`.
- `io_slot_flags()` maps stored file flags into request flag positions starting at `REQ_F_SUPPORT_NOWAIT_BIT`.
- Bitmap helpers update `alloc_hint` to speed subsequent allocation.

## Cross-File Relationships
- Implemented by `filetable.c`.
- `io_file_get_flags()` is provided by io_uring core and feeds fixed-file capability encoding.
- Used by cancellation, fdinfo, openclose, and resource paths.

## Risks / Review Notes
- Pointer tagging assumes file pointer alignment leaves low bits free.
- `FFS_MASK` is an inverse mask; helper usage must preserve the intended pointer/flag split.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/filetable.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/fs.c -->
# File Research: sources/os/linux/linux/io_uring/fs.c

## Purpose
Implements io_uring filesystem namespace mutation opcodes: rename, unlink/rmdir, mkdir, symlink, and hardlink.

## Main Functions
- Rename:
  - `io_renameat_prep()`
  - `io_renameat()`
  - `io_renameat_cleanup()`
- Unlink/rmdir:
  - `io_unlinkat_prep()`
  - `io_unlinkat()`
  - `io_unlinkat_cleanup()`
- Mkdir:
  - `io_mkdirat_prep()`
  - `io_mkdirat()`
  - `io_mkdirat_cleanup()`
- Symlink:
  - `io_symlinkat_prep()`
  - `io_symlinkat()`
- Hardlink:
  - `io_linkat_prep()`
  - `io_linkat()`
  - `io_link_cleanup()`

## Important Design Points
- Operations reject fixed-file requests because they operate on directory fds and pathnames rather than a request file.
- Pathnames are captured with `delayed_getname()` / `delayed_getname_uflags()` and completed at issue time with `CLASS(filename_complete_delayed, ...)`.
- All namespace operations force async execution and set `REQ_F_NEED_CLEANUP` after pathname capture.
- Cleanup functions dismiss delayed filenames if the request does not reach normal issue completion.

## Cross-File Relationships
- Declared in `fs.h`.
- Uses filename-based VFS helpers from `../fs/internal.h`.
- Depends on delayed filename machinery declared in `include/linux/fs.h`.

## Risks / Review Notes
- Error paths must dismiss any delayed filename already acquired.
- Normal issue paths clear `REQ_F_NEED_CLEANUP`; cleanup paths must remain paired with prep state.
- `io_unlinkat_prep()` only allows `AT_REMOVEDIR` in flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/fs.h -->
# File Research: sources/os/linux/linux/io_uring/fs.h

## Purpose
Declares io_uring filesystem namespace opcode handlers and cleanup functions.

## Main Contents
- Prototypes for rename, unlink, mkdir, symlink, and link prep/issue functions.
- Cleanup prototypes for rename, unlink, mkdir, and link path resources.

## Cross-File Relationships
- Implemented by `fs.c`.
- Used by io_uring opcode dispatch and cleanup paths.

## Risks / Review Notes
- Cleanup declarations mirror operations that allocate delayed filenames; any new pathname opcode should follow the same pattern.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/futex.c -->
# File Research: sources/os/linux/linux/io_uring/futex.c

## Purpose
Implements io_uring futex wait, futex waitv, futex wake, cancellation, and futex wait allocation caching.

## Main Structures
- `struct io_futex`: per-request parsed futex parameters.
- `struct io_futex_data`: single futex wait queue plus request pointer.
- `struct io_futexv_data`: ownership bit and flexible array of futex vectors.

## Main Functions
- Cache:
  - `io_futex_cache_init()`
  - `io_futex_cache_free()`
- Cancellation:
  - `io_futex_cancel()`
  - `io_futex_remove_all()`
  - `__io_futex_cancel()`
- Prep:
  - `io_futex_prep()`
  - `io_futexv_prep()`
- Wait/wake:
  - `io_futex_wait()`
  - `io_futexv_wait()`
  - `io_futex_wake()`
- Completion/wake callbacks:
  - `io_futex_complete()`
  - `io_futexv_complete()`
  - `io_futex_wake_fn()`
  - `io_futex_wakev_fn()`

## Important Design Points
- Wait requests are tracked inflight so file-exit cancellation can find them.
- Single futex waits allocate `io_futex_data` from `ctx->futex_cache`.
- Waitv requests allocate flexible vector storage and use an ownership bit to arbitrate wake-vs-cancel completion.
- Pending futex waits are linked on `ctx->futex_list` through `req->hash_node`.
- Completion is delivered via io_uring task_work.
- `io_futex_wake()` uses `FLAGS_STRICT` so waking zero futexes yields zero.

## Cross-File Relationships
- Declarations and config stubs are in `futex.h`.
- Uses generic cancel helpers from `cancel.c`.
- Uses allocation cache helpers from `alloc_cache`.
- Depends on kernel futex internals from `../kernel/futex/futex.h`.

## Risks / Review Notes
- Wake/cancel races are delicate, especially for waitv ownership.
- `io_futex_wait()` rejects a zero mask.
- `io_futexv_wait()` must restore task state to `TASK_RUNNING` after setup because async io_uring must not leave the task blocked like the synchronous futex syscall.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/futex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/futex.h -->
# File Research: sources/os/linux/linux/io_uring/futex.h

## Purpose
Declares io_uring futex opcode handlers, cancellation hooks, and config-dependent stubs.

## Main Contents
- Prototypes for futex prep, wait, waitv, and wake.
- Under `CONFIG_FUTEX`, prototypes for cancel/remove-all and cache init/free.
- Without futex support, cancel returns neutral values, remove-all returns false, cache init returns false, and cache free is a no-op.

## Cross-File Relationships
- Implemented by `futex.c`.
- Included by cancellation and opcode dispatch paths.

## Risks / Review Notes
- Disabled-config stubs intentionally make futex cancellation/cache hooks safe to call unconditionally.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/futex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/io-wq.c -->
# File Research: sources/os/linux/linux/io_uring/io-wq.c

## Purpose
Implements io_uring’s internal worker-thread pool for asynchronous work that cannot complete inline.

## Main Structures
- `struct io_worker`: one worker thread, including refcount, flags, task, workqueue/account pointers, current work, creation state, and RCU/delayed-work storage.
- `struct io_wq_acct`: bounded or unbounded worker accounting, worker lists, pending work list, and running count.
- `struct io_wq`: per-task workqueue with shared hash serialization state, worker refs/completions, CPU hotplug node, owner task, bounded/unbounded accounts, wait entry, hash tails, and CPU mask.
- `struct io_cb_cancel_data`: cancellation match callback state.

## Main Functional Areas
- Worker lifecycle:
  - `create_io_worker()`, `create_worker_cb()`, `create_worker_cont()`
  - `io_wq_worker()`
  - `io_worker_exit()`
  - `io_wq_exit_start()`, `io_wq_exit_workers()`, `io_wq_put_and_exit()`
- Scheduling and execution:
  - `io_wq_enqueue()`
  - `io_worker_handle_work()`
  - `io_get_next_work()`
  - `io_wq_hash_work()`
  - `io_wq_inc_running()` / `io_wq_dec_running()`
- Cancellation:
  - `io_wq_cancel_cb()`
  - `io_wq_cancel_pending_work()`
  - `io_wq_cancel_running_work()`
  - `io_run_cancel()`
- Worker creation/retry:
  - task_work-based creation on the owner task.
  - delayed retry for transient `create_io_thread()` failures.
- CPU/limit management:
  - CPU hotplug callbacks update worker affinity masks.
  - `io_wq_cpu_affinity()` changes allowed CPUs.
  - `io_wq_max_workers()` gets/sets bounded and unbounded worker limits.
- Idle behavior:
  - idle workers enter free list and exit after timeout or when `EXIT_ON_IDLE` is set.

## Important Design Points
- Work is split into bounded and unbounded accounts. Unbounded max workers are capped by `RLIMIT_NPROC`.
- Hashed work items sharing a hash key do not run concurrently; hash tails let the queue skip runs of identical hashes.
- Current work is set before execution so cancellation can find work removed from pending queues.
- Worker creation is often queued as task_work on the original task to keep worker creation associated with the owning task.
- `IO_WQ_BIT_EXIT` causes new work to be canceled and workers to drain/exit.
- Worker sleep/running hooks are called from scheduler integration to maintain running counts and spawn replacement workers when needed.
- Exit waits are tuned to avoid hung-task false positives under heavy long-running io-wq load.

## Cross-File Relationships
- Public API and flags are in `io-wq.h`.
- Core io_uring submits async work to io-wq and receives completed work through `io_wq_submit_work()` / `io_wq_free_work()` implemented elsewhere.
- Cancellation in `cancel.c` calls `io_wq_cancel_cb()` and `io_wq_exit_start()`.
- Eventfd code uses `io_wq_current_is_worker()` for async eventfd behavior.

## Risks / Review Notes
- Worker, account, and hash locking is complex: raw spinlocks, RCU worker lists, waitqueue hash serialization, task_work, and completions all interact.
- Hashed work correctness depends on maintaining `hash_tail[]` when inserting/removing pending work.
- Cancellation can return “pending canceled” or “running cancellation attempted”; callers must interpret `IO_WQ_CANCEL_*` correctly.
- Worker creation failure paths cancel pending work if no workers remain.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/io-wq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/io_uring/io-wq.h -->
# File Research: sources/os/linux/linux/io_uring/io-wq.h

## Purpose
Declares the io_uring worker-queue API, work flags, cancellation results, and worker detection helpers.

## Main Contents
- Work flags:
  - `IO_WQ_WORK_CANCEL`
  - `IO_WQ_WORK_HASHED`
  - `IO_WQ_WORK_UNBOUND`
  - `IO_WQ_WORK_CONCURRENT`
  - `IO_WQ_HASH_SHIFT`
- `enum io_wq_cancel`: pending-canceled, running-cancel-attempted, or not-found.
- `struct io_wq_hash`: shared hash serialization map and waitqueue.
- `struct io_wq_data`: creation inputs containing hash and owner task.
- API declarations:
  - create/exit/put, exit-on-idle, enqueue, hash work, CPU affinity, max workers, worker stopped, cancel callback.
- Scheduler hook declarations under `CONFIG_IO_WQ`.
- `io_wq_current_is_worker()`: detects current io-wq worker tasks via `PF_IO_WORKER` and `worker_private`.

## Cross-File Relationships
- Implemented by `io-wq.c`.
- Used by core io_uring, cancellation, eventfd, and async submission paths.

## Risks / Review Notes
- Hash bits are stored in the upper bits of work flags; new flags must not collide with `IO_WQ_HASH_SHIFT` encoding.
- `io_wq_current_is_worker()` depends on scheduler task flags and `current->worker_private` being set by io-wq worker setup.
<!-- END FILE RESEARCH: sources/os/linux/linux/io_uring/io-wq.h -->