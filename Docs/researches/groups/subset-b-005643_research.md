# subset-b-005643 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/miscdev.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/miscdev.c

## Purpose
`miscdev.c` implements the `/dev/ecryptfs` miscdevice used by eCryptfs kernel code to exchange key-management messages with the per-user userspace daemon. It serializes outgoing kernel requests into the eCryptfs packet format, exposes daemon polling and blocking reads, accepts daemon responses, and owns miscdevice open/release lifetime accounting.

## Important APIs, types, and functions
The file operates on `struct ecryptfs_daemon`, `struct ecryptfs_msg_ctx`, and `struct ecryptfs_message` from `ecryptfs_kernel.h`. Important functions are `ecryptfs_miscdev_open`, `ecryptfs_miscdev_release`, `ecryptfs_miscdev_poll`, `ecryptfs_miscdev_read`, `ecryptfs_miscdev_write`, `ecryptfs_miscdev_response`, exported `ecryptfs_send_miscdev`, and init/exit helpers `ecryptfs_init_ecryptfs_miscdev` and `ecryptfs_destroy_ecryptfs_miscdev`. Packet constants define type, counter, length, and maximum encrypted-key response sizes.

## Control flow
Open finds or spawns a daemon for the caller's effective uid under `ecryptfs_daemon_hash_mux`, marks the daemon miscdevice-open, and stores it in `file->private_data`. Kernel callers enqueue messages with `ecryptfs_send_miscdev`, which allocates a message, attaches it to a message context, appends it to the daemon outbound queue, increments the queued count, and wakes the daemon waitqueue. Poll reports readability when the outbound queue is non-empty. Read waits for a queued context, formats type/counter/length/message into userspace, removes the context from the outbound list, and frees non-request contexts. Write validates packet framing, copies the userspace buffer, dispatches response packets to `ecryptfs_process_response`, and ignores HELO/QUIT.

## State and persistence
State is runtime-only: daemon flags such as zombie/open/read/poll, waitqueues, outbound message lists, per-message counters, and `ecryptfs_num_miscdev_opens`. Release clears the open flag, decrements the counter, and exorcises the daemon. No filesystem state is persisted here; the persistent effects come from key availability and later encrypted-file operations.

## Dependencies and integration points
This layer depends on Linux miscdevice, poll, waitqueue, uaccess, endian conversion, slab allocation, and the eCryptfs messaging/daemon helpers in other eCryptfs files. It is the kernel/userspace bridge for authentication token and key-request workflows.

## Risks and test signals
Risks include packet length parsing mistakes, daemon zombie races, read/poll flag serialization, response delivery to stale message contexts, and BUG-triggering release paths if daemon teardown invariants break. Test signals include concurrent opens for the same euid, blocking read wakeups, small-buffer reads, malformed packet writes, HELO/QUIT writes, response matching, daemon exit during pending requests, and module unload with open handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/miscdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/mmap.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/mmap.c

## Purpose
`mmap.c` supplies eCryptfs address-space operations for cached file I/O. It decrypts data read from the lower encrypted file, encrypts dirty upper folios during writeback, maintains eCryptfs metadata file sizes in headers or xattrs, and handles the special "view as encrypted" mode where userspace sees encrypted bytes plus synthetic metadata.

## Important APIs, types, and functions
The exported object is `ecryptfs_aops`. Key helpers include `ecryptfs_writepages`, `ecryptfs_read_folio`, `ecryptfs_write_begin`, `ecryptfs_write_end`, `ecryptfs_copy_up_encrypted_with_header`, `ecryptfs_write_inode_size_to_metadata`, and lower metadata writers for header and xattr storage. It uses `struct ecryptfs_crypt_stat`, `ecryptfs_xattr_cache`, and lower file helpers from `read_write.c`.

## Control flow
Read-folio chooses among direct lower reads for plaintext files, lower encrypted reads for encrypted-view files, xattr-header synthesis for encrypted-view files whose metadata is stored in xattrs, or full page decryption. Write-begin grabs a folio, fills it from lower storage or decrypts it when a partial page write needs existing contents, and extends holes with truncate/zeroing as needed. Write-end writes plaintext lower data for unencrypted files; encrypted files zero the tail beyond EOF, encrypt the folio to lower storage, update upper inode size, and rewrite the size in metadata. Writeback iterates dirty folios and calls `ecryptfs_encrypt_page`.

## State and persistence
Persistent state is the lower file contents plus eCryptfs metadata containing the logical upper size. Depending on `ECRYPTFS_METADATA_IN_XATTR`, the size is stored either in the first eight bytes of the lower file header or inside the lower xattr. Runtime folio state tracks uptodate/error/dirty status and interacts with writeback mapping errors.

## Dependencies and integration points
This file integrates the Linux folio/page-cache write path, xattr APIs, lower VFS reads/writes, eCryptfs crypto routines, and the stacked filesystem inode relationship. It relies on `ecryptfs_encrypt_page`, `ecryptfs_decrypt_page`, metadata packet helpers, and `fsstack_copy_inode_size`.

## Risks and test signals
Risks include stale or corrupt metadata sizes, partial-write data loss when folios are not uptodate, xattr write failures, encrypted-view header synthesis errors, and behavior under blockless builds noted by the `CONFIG_BLOCK` workaround. Test signals include sparse writes, writes crossing EOF, encrypted-view reads with xattr metadata, lower filesystems without xattr support, writeback error propagation, mmap read/write paths, and `bmap` on lower mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/read_write.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/read_write.c

## Purpose
`read_write.c` provides direct lower-file read/write primitives and an eCryptfs page-by-page write helper used outside the normal buffered write path. It translates upper inode offsets to lower file operations and applies encryption and metadata-size maintenance when needed.

## Important APIs, types, and functions
Important exported functions are `ecryptfs_write_lower`, `ecryptfs_write_lower_page_segment`, `ecryptfs_write`, `ecryptfs_read_lower`, and `ecryptfs_read_lower_page_segment`. The file uses `struct ecryptfs_inode_info` for the lower file pointer and `struct ecryptfs_crypt_stat` to decide whether to encrypt pages and update metadata.

## Control flow
`ecryptfs_write_lower` uses `kernel_write` against the lower file and marks the upper inode dirty. Page-segment helpers map a folio with `kmap_local_folio`, compute a byte offset from page index plus in-page offset, and call the lower read/write primitive. `ecryptfs_write` walks the requested range one page at a time, begins at old EOF when filling holes, reads the upper mapping folio, zero-fills hole portions or fresh-page tails, copies caller data, marks the folio uptodate, then either encrypts it or writes plaintext to the lower file. If the write extends size, it updates `i_size` and encrypted metadata size.

## State and persistence
The persistent output is lower file data and, for encrypted inodes, updated header/xattr size metadata. Runtime state includes mapped folio contents, inode size, lower-file availability, and signal interruption via `fatal_signal_pending`.

## Dependencies and integration points
It depends on the VFS kernel read/write helpers, folio mapping APIs, eCryptfs crypto routines, and metadata writer from `mmap.c`. Callers include metadata setup, truncate/extend flows, and any path that needs to write arbitrary upper bytes through the eCryptfs transform.

## Risks and test signals
Risks include using `data_offset` rather than the current segment length for plaintext page-segment writes, interruption leaving partially written data, lower file pointer loss returning `-EIO`, and metadata update failure after data has been written. Test signals include unencrypted writes across multiple pages, encrypted writes with holes, signal-interrupted writes, lower write short/error returns, reads past EOF, and lower-file missing scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/read_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/super.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/super.c

## Purpose
`super.c` defines eCryptfs superblock operations and inode-cache lifetime. It allocates and initializes eCryptfs private inode state, forwards filesystem statistics to the lower filesystem, reports mount options, and tears down lower inode references on eviction.

## Important APIs, types, and functions
The exported table is `ecryptfs_sops`. Important functions are `ecryptfs_alloc_inode`, `ecryptfs_destroy_inode`, `ecryptfs_free_inode`, `ecryptfs_statfs`, `ecryptfs_evict_inode`, and `ecryptfs_show_options`. The file owns the global `ecryptfs_inode_info_cache`.

## Control flow
Allocation pulls `struct ecryptfs_inode_info` from the slab cache, initializes `crypt_stat`, lower-file mutex/count, and lower-file pointer, and returns the embedded VFS inode. Destroy asserts the lower file has already been dropped and releases crypto state. Eviction truncates page cache, clears the inode, and iputs the lower inode. `statfs` calls the lower superblock operation, rewrites the magic to `ECRYPTFS_SUPER_MAGIC`, and clamps filename length through mount crypto settings. `show_options` walks global auth tokens and prints cipher, key-size, passthrough, xattr metadata, encrypted view, unlink-sigs, and mount-auth-token-only flags.

## State and persistence
The file maintains only runtime slab/inode state. Persistent user-visible state is represented indirectly by mount options and lower filesystem stats. Inode crypto state is initialized here and destroyed when the inode dies.

## Dependencies and integration points
It depends on lower dentry/superblock operations, eCryptfs mount crypt-stat structures, key/auth token lists, and Linux superblock/inode lifecycle callbacks. Other eCryptfs files rely on the initialized private inode layout and crypt stat.

## Risks and test signals
Risks include lower inode reference leaks, BUGs if lower files survive destroy, incorrect `statfs` passthrough, mount option disclosure mismatches, and slab lifetime issues at module unload. Test signals include mount/unmount loops, inode eviction after open lower files, `statfs`, `/proc/mounts` option output, lower filesystems with no `statfs`, and encrypted filename length limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/efivarfs/Kconfig

## Purpose
`Kconfig` exposes the `EFIVAR_FS` build option for the EFI variable filesystem. It lets the kernel or module build include the replacement filesystem for older EFI variable sysfs support.

## Important APIs, types, and functions
The single symbol is `CONFIG_EFIVAR_FS`, a tristate that depends on `EFI` and defaults to module. The help text documents that the module name is `efivarfs` and that efivarfs avoids the old sysfs 1024-byte variable size limit.

## Control flow
There is no runtime control flow. Build selection controls whether `inode.o`, `file.o`, `super.o`, and `vars.o` are linked into `efivarfs.o`.

## State and persistence
The file has no state. Its persistence effect is build configuration only; EFI variables themselves live in firmware NVRAM.

## Dependencies and integration points
It integrates with the kernel Kconfig system and requires EFI runtime variable support. The default modular setting makes efivarfs commonly available without forcing it built in.

## Risks and test signals
Risks are configuration mismatches on non-EFI systems and tests assuming efivarfs exists when `EFI` or `EFIVAR_FS` is disabled. Test signals are build coverage for `n`, `m`, and `y` configurations and boot-time module registration on EFI-capable machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/efivarfs/Makefile

## Purpose
The Makefile builds the efivarfs filesystem module or built-in object set.

## Important APIs, types, and functions
It maps `obj-$(CONFIG_EFIVAR_FS)` to `efivarfs.o` and composes that object from `inode.o`, `file.o`, `super.o`, and `vars.o`.

## Control flow
There is no runtime flow. Kbuild includes these source objects only when the Kconfig symbol is enabled.

## State and persistence
No state is stored here. It determines which implementation units participate in the final kernel image or module.

## Dependencies and integration points
It integrates efivarfs with Kbuild and mirrors the file-level split between VFS operations, firmware variable helpers, and superblock setup.

## Risks and test signals
Risks are missing object entries when source files gain exported symbols or stale entries after renames. Test signals are modular and built-in builds with `CONFIG_EFIVAR_FS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/file.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/file.c

## Purpose
`file.c` implements efivarfs regular-file operations. Each file represents one EFI variable, where the first four bytes exposed to userspace are EFI attributes and the remaining bytes are variable data.

## Important APIs, types, and functions
The exported table is `efivarfs_file_operations`. Important functions are `efivarfs_file_open`, `efivarfs_file_read`, `efivarfs_file_write`, and `efivarfs_file_release`. They operate on `struct efivar_entry` stored in `inode->i_private` and `file->private_data`.

## Control flow
Open stores the entry in private data and increments `open_count` under the inode lock. Reads rate-limit by user, fetch variable size, return EOF for uncommitted `-ENOENT` variables, allocate an attributes-plus-data buffer, call `efivar_entry_get`, and copy through `simple_read_from_buffer`. Writes require at least an attributes word, reject unknown attribute bits, copy payload data, lock the inode, reject removed variables, call `efivar_entry_set_get_size`, and then update inode size and timestamps. Release decrements `open_count`, marks zero-size last-close variables as removed, and recursively removes the dentry.

## State and persistence
Persistent state is firmware NVRAM variable content changed by SetVariable. Runtime inode size mirrors firmware state and uses zero size to signal a deleted or uncommitted variable. `removed` and `open_count` guard races between failed creates, deletes, and open files.

## Dependencies and integration points
It depends on `vars.c` firmware wrappers, inode locking, uaccess, per-user rate limiting, VFS removal helpers, and EFI attribute constants. It is called by VFS operations assigned in `inode.c`.

## Risks and test signals
Risks include firmware write failures after userspace sees a file, races between delete/create/write/release, attribute validation gaps, rate-limit latency, and size mismatch after append/delete semantics. Test signals include reading existing variables, creating then closing without data, deleting by zero-size SetVariable result, writes with invalid attributes, concurrent opens during unlink, and firmware returning `ENOENT`, `ENOSPC`, or write-protected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/inode.c

## Purpose
`inode.c` provides efivarfs inode creation, directory operations, unlink, immutable flag support, and setattr behavior. It maps valid efivarfs filenames into EFI variable vendor/name pairs.

## Important APIs, types, and functions
Important functions are `efivarfs_get_inode`, `efivarfs_create`, `efivarfs_unlink`, `efivarfs_valid_name`, `efivarfs_fileattr_get`, `efivarfs_fileattr_set`, and `efivarfs_setattr`. It exports `efivarfs_dir_inode_operations` and assigns private file inode operations internally.

## Control flow
`efivarfs_get_inode` creates a new inode with mount uid/gid, timestamps, and immutable state based on whether the variable is removable; regular files get efivarfs file ops and directories get simple directory ops. Create validates `VariableName-GUID` naming, rejects Linux random seed variables, parses the GUID, checks the removable whitelist, fills `struct efivar_entry`, stores it in `i_private`, and makes a persistent dentry without immediately committing firmware data. Unlink calls `efivar_entry_delete` and then `simple_unlink`. File attributes expose only immutable toggling; setattr copies metadata changes without allowing i_size updates.

## State and persistence
Inode state stores `struct efivar_entry`, mode, uid/gid, immutable flag, and open/delete bookkeeping. Firmware persistence occurs through delete/write helpers, not inode allocation alone. Immutable defaults protect non-whitelisted firmware variables from accidental deletion or modification.

## Dependencies and integration points
It depends on EFI GUID parsing, variable validation/whitelist logic in `vars.c`, VFS simple directory helpers, file attributes, and mount options from superblock fs info.

## Risks and test signals
Risks include accepting malformed UTF-8-to-UCS2 names as variable names, immutable flag bypasses, create/unlink races with firmware state, and size updates through setattr. Test signals include filename validation, GUID case handling, `chattr +/-i`, unlink of protected and removable variables, create followed by write/release, and rejection of random-seed GUID variables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/internal.h -->
# sources/distributed-fs/ceph-client/fs/efivarfs/internal.h

## Purpose
`internal.h` declares efivarfs-private data structures and cross-file helper prototypes shared by file, inode, superblock, and firmware variable code.

## Important APIs, types, and functions
Key types are `struct efivarfs_mount_opts`, `struct efivarfs_fs_info`, and `struct efivar_entry`. Important declarations include file and directory operation tables, `efivarfs_get_inode`, UTF-8 filename conversion, validation/removable checks, variable enumeration, and entry get/set/delete/size helpers. `efivar_entry()` converts from VFS inode to the containing entry.

## Control flow
The header has no runtime control flow, but it defines how the implementation units call each other: VFS operations manipulate `efivar_entry`; superblock population calls `efivar_init`; file operations call entry helpers; inode creation asks validation helpers whether variables should be removable.

## State and persistence
It defines runtime state: mount uid/gid options, superblock notifier ownership, per-variable open count, removed flag, and embedded `struct efi_variable`. Persistence remains in EFI firmware variables, accessed through declared helpers.

## Dependencies and integration points
It depends on Linux EFI, fs, notifier, and mutex-visible types. It is the integration contract between efivarfs VFS logic and the kernel EFIVAR namespace imported by `vars.c`.

## Risks and test signals
Risks include struct layout assumptions around `container_of`, missing prototypes after feature changes, and inconsistent use of `removed`/`open_count` across files. Test signals are all efivarfs build configurations and sparse/compiler checks for prototype drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/super.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/super.c

## Purpose
`super.c` registers and mounts efivarfs, populates the root directory from firmware EFI variables, maintains superblock flags as EFI write support changes, supports uid/gid mount options, reports firmware storage capacity, and resynchronizes after freeze/thaw.

## Important APIs, types, and functions
Important functions include `efivarfs_fill_super`, `efivarfs_get_tree`, `efivarfs_init_fs_context`, `efivarfs_reconfigure`, `efivarfs_kill_sb`, `efivarfs_create_dentry`, `efivarfs_callback`, `efivarfs_check_missing`, `efivarfs_freeze_fs`, `efivarfs_unfreeze_fs`, dentry hash/compare helpers, and `efivarfs_statfs`. The file defines `efivarfs_type` and `efivarfs_ops`.

## Control flow
Mount context allocation checks `efivar_is_available`, initializes root uid/gid defaults, and installs fs-context operations. Fill-super sets block sizes, magic, dentry operations, read-only status when firmware lacks writes, creates the root inode, registers an EFI ops notifier, and enumerates firmware variables through `efivar_init`, creating persistent dentries for each non-random-seed variable. Dentry comparison treats variable names case-sensitive and GUID suffixes case-insensitive. Freeze is a no-op; unfreeze scans existing dentries to refresh sizes/remove vanished variables, then enumerates firmware to create missing dentries.

## State and persistence
Runtime superblock state includes mount options, notifier block, root dentry tree, dentry hash rules, and read-only flag. Persistent state is firmware NVRAM; dentries are cached projections and may be resynced after thaw or EFI ops mode changes.

## Dependencies and integration points
It depends on EFI runtime variable APIs, fs_context, simple/persistent dentry helpers, blocking notifier chain `efivar_ops_nh`, statfs, suspend freeze integration, and GUID/UTF-8 conversion helpers.

## Risks and test signals
Risks include duplicate firmware variable loops, stale dentries after external firmware changes, read-only flag races, notifier lifetime on mount failure, mount option parsing errors, and case-sensitive/case-insensitive dentry hash mismatches. Test signals include mount/unmount on EFI systems, uid/gid options, remount rw when SetVariable is unavailable, statfs with and without QueryVariableInfo, freeze/thaw resync, duplicate variable firmware behavior, and GUID-case lookup aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/vars.c -->
# sources/distributed-fs/ceph-client/fs/efivarfs/vars.c

## Purpose
`vars.c` wraps EFI runtime variable enumeration and access for efivarfs and validates writes to sensitive UEFI variables. It converts EFI names to efivarfs filenames, identifies variables safe to remove, and serializes firmware access through the EFIVAR lock.

## Important APIs, types, and functions
Important helpers include validators for device paths, boot order, load options, uint16 values, and ASCII strings; `variable_matches`; `efivar_get_utf8name`; `efivar_validate`; `efivar_variable_is_removable`; `efivar_init`; `efivar_entry_delete`; `efivar_entry_size`; `__efivar_entry_get`; `efivar_entry_get`; and `efivar_entry_set_get_size`. The static `variable_validate` table is both a validation table and removable whitelist.

## Control flow
Variable names are converted from UCS-2 to UTF-8, suffixed with `-GUID`, and slash characters are replaced with `!`. Validation converts the UCS-2 name to UTF-8, finds vendor/name patterns including wildcards, and invokes type-specific validators for boot/device variables. Enumeration allocates a 512-byte name buffer, locks EFI variable iteration, repeatedly calls `efivar_get_next_variable`, checks duplicate presence when requested, and invokes a caller callback. Set/get-size first validates data, locks firmware access, calls SetVariable, then calls GetVariable with size zero to determine the new size or deletion result.

## State and persistence
Persistent state is firmware variable storage changed by SetVariable/DeleteVariable. Runtime state is limited to temporary name buffers and the global EFIVAR lock. The validation whitelist affects whether efivarfs inodes default to immutable.

## Dependencies and integration points
It imports the `EFIVAR` namespace and depends on EFI runtime services, UCS-2 helpers, GUID utilities, hex parsing, and efivarfs superblock duplicate detection callback. File and inode operations call these helpers for all firmware access.

## Risks and test signals
Risks include firmware implementations that loop or return duplicate names, validation accepting malformed boot entries, incorrect wildcard matching, SetVariable/GetVariable races, NVRAM exhaustion, and destructive writes to sensitive variables if whitelist rules are wrong. Test signals include Boot/Driver variable validation, invalid device paths, oversized variable names, duplicate enumeration, delete of missing variables, ENOSPC handling, random seed exclusion, and concurrent readers/writers under efivar locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efivarfs/vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/efs/Kconfig

## Purpose
`Kconfig` defines the `EFS_FS` option for read-only SGI IRIX EFS filesystem support.

## Important APIs, types, and functions
The symbol is a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`. Its help describes EFS as an older SGI filesystem and notes the module name `efs`.

## Control flow
There is no runtime flow. The option controls whether EFS source files are compiled and linked.

## State and persistence
No state is stored. The resulting filesystem driver only reads on-disk EFS images.

## Dependencies and integration points
It integrates with Kconfig, block-device support, and buffer-head infrastructure required by the EFS implementation.

## Risks and test signals
Risks are build regressions when buffer-head assumptions change or tests running on kernels without `EFS_FS`. Test signals include `n`, `m`, and `y` builds and mount tests against EFS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Makefile -->
# sources/distributed-fs/ceph-client/fs/efs/Makefile

## Purpose
The Makefile defines how the EFS filesystem object is assembled.

## Important APIs, types, and functions
`obj-$(CONFIG_EFS_FS)` builds `efs.o`, composed from `super.o`, `inode.o`, `namei.o`, `dir.o`, `file.o`, and `symlink.o`.

## Control flow
No runtime control flow exists. Kbuild uses the object list when `CONFIG_EFS_FS` is enabled.

## State and persistence
No state is stored. It controls compile-time composition.

## Dependencies and integration points
It integrates EFS VFS, inode, lookup, directory, regular-file, and symlink pieces into one module.

## Risks and test signals
Risks are stale object lists after source movement and missing build coverage for module/built-in forms. Test signals are EFS builds in all supported configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/dir.c -->
# sources/distributed-fs/ceph-client/fs/efs/dir.c

## Purpose
`dir.c` implements EFS directory iteration and directory inode/file operation tables.

## Important APIs, types, and functions
The exported tables are `efs_dir_operations` and `efs_dir_inode_operations`. The main function is `efs_readdir`, which emits entries from EFS directory blocks using `struct efs_dir` and `struct efs_dentry`.

## Control flow
`iterate_shared` computes the directory block and slot from `ctx->pos`, reads each mapped directory block through `sb_bread(inode->i_sb, efs_bmap(inode, block))`, validates the directory block magic, scans slot offsets, checks entry name bounds inside the block, and calls `dir_emit`. It advances `ctx->pos` by encoding block and slot. The inode ops only supply lookup through `efs_lookup`.

## State and persistence
EFS is read-only; no on-disk state is changed. Runtime state is the directory iteration position and buffer-head lifetime for each directory block.

## Dependencies and integration points
It depends on `efs_bmap` block mapping from `inode.c`, buffer-head reads, VFS directory iteration, file leasing helpers, and EFS on-disk directory layout macros from `efs.h`.

## Risks and test signals
Risks include malformed slot offsets, non-multiple directory sizes, invalid directory magic, truncated names, and block mapping failures. Test signals include readdir over multi-block directories, empty slots, corrupted directory images, long names near block boundaries, and interrupted or resumed `getdents` positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/efs.h -->
# sources/distributed-fs/ceph-client/fs/efs/efs.h

## Purpose
`efs.h` centralizes EFS in-memory and on-disk format definitions, constants, macros, and cross-file prototypes.

## Important APIs, types, and functions
It defines block size constants, `efs_block_t`, `efs_ino_t`, `efs_extent`, `struct efs_dinode`, `struct efs_inode_info`, directory entry/block structures, and helper macros such as `INODE_INFO`, `SUPER_INFO`, `EFS_SLOTAT`, and magic checks. It declares inode, lookup, block mapping, export, and symlink operation objects used across EFS files.

## Control flow
The header has no runtime flow, but its extent and directory layout definitions drive all block mapping, inode loading, directory iteration, and lookup behavior.

## State and persistence
It describes persistent on-disk state: 512-byte blocks, 128-byte dinodes, direct/indirect extents, EFS directory blocks, superblock information, and SGI device encodings. Runtime state extends VFS inodes with cached extents and last-extent index.

## Dependencies and integration points
It depends on Linux VFS/uaccess types and `linux/efs_fs_sb.h`. It is included by every EFS implementation file and forms the local ABI of the driver.

## Risks and test signals
Risks include bitfield/endian assumptions in `efs_extent`, structure layout drift, incorrect slot arithmetic, and stale prototypes. Test signals include big-endian/little-endian image parsing, direct and indirect extents, special device inodes, and compile-time warnings under different architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/efs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/file.c -->
# sources/distributed-fs/ceph-client/fs/efs/file.c

## Purpose
`file.c` defines regular-file operations for the read-only EFS filesystem.

## Important APIs, types, and functions
The file provides `generic_ro_fops` use through inode setup rather than a custom table here, and historically isolates regular file behavior. In this tree it is small because the actual address-space operations live in `inode.c`.

## Control flow
Regular-file reads flow through VFS generic read operations and the EFS address-space operations assigned by `efs_iget`, specifically `block_read_full_folio` with `efs_get_block`. There is no write path because EFS is forced read-only.

## State and persistence
No state is changed. Runtime file state is ordinary VFS read position/cache state; persistent disk contents are never modified.

## Dependencies and integration points
It integrates with `inode.c`, where regular inodes get `generic_ro_fops` and EFS mapping operations.

## Risks and test signals
Risks are mostly integration drift: if VFS regular-file behavior changes, the minimal EFS file layer relies on generic read-only semantics. Test signals include normal reads, mmap/readpage behavior, attempts to open for write, and splice/read paths through generic helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/inode.c -->
# sources/distributed-fs/ceph-client/fs/efs/inode.c

## Purpose
`inode.c` loads EFS inodes from disk, assigns VFS operations, implements extent-based block mapping, and provides address-space operations for file and symlink data.

## Important APIs, types, and functions
Important functions include `efs_iget`, `extent_copy`, `efs_map_block`, `efs_extent_check`, `efs_read_folio`, and `_efs_bmap`. The file defines `efs_aops`, uses `struct efs_inode_info`, and exports module metadata.

## Control flow
`efs_iget` computes the disk block and offset of a 128-byte dinode from the inode number, cylinder group layout, and filesystem start offset. It reads the dinode, decodes mode, links, uid/gid, size, timestamps, device numbers, extent count, and direct extents, then assigns directory, regular file, symlink, or special inode operations. `efs_map_block` first checks the cached last extent and direct extents; for files with more than `EFS_DIRECTEXTENTS`, it walks indirect extent blocks referenced by the direct extents and maps logical blocks to physical blocks.

## State and persistence
Persistent state is the read-only EFS dinode and extent tree. Runtime state caches direct extents and the last successful extent index in `struct efs_inode_info` to speed repeated mappings.

## Dependencies and integration points
It depends on buffer-head block reads, VFS inode cache, generic block mapping/read helpers, EFS superblock layout from `efs_sb_info`, and symlink operations from `symlink.c`.

## Risks and test signals
Risks include inode-number arithmetic errors, indirect extent traversal bugs, extent magic validation, corrupted device encodings, unsupported modes, and stale `lastextent` assumptions. Test signals include regular reads over fragmented direct and indirect extents, symlink reads, special device nodes, zero-size files, bad extent magic images, and NFS/export inode retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/namei.c -->
# sources/distributed-fs/ceph-client/fs/efs/namei.c

## Purpose
`namei.c` implements EFS pathname lookup and exportfs helpers for NFS-style file handles and parent discovery.

## Important APIs, types, and functions
Important functions are `efs_find_entry`, `efs_lookup`, `efs_nfs_get_inode`, `efs_fh_to_dentry`, `efs_fh_to_parent`, and `efs_get_parent`.

## Control flow
Lookup scans each directory block using `efs_bmap` and `sb_bread`, validates directory block magic, iterates slots, compares name length and bytes, and returns the found inode number. `efs_lookup` converts that inode number into a VFS inode with `efs_iget` and splices aliases. Export helpers use `generic_fh_to_dentry`/`generic_fh_to_parent` with `efs_nfs_get_inode`, and `get_parent` looks up the `..` entry.

## State and persistence
No on-disk state changes occur. Runtime state includes transient buffer heads and dentry/inode cache results.

## Dependencies and integration points
It depends on EFS directory layout, buffer-head reads, `efs_iget`, exportfs, and VFS dentry aliasing. It is wired into directory inode operations and superblock export operations.

## Risks and test signals
Risks include missing boundary checks compared with readdir, corrupted directory slot offsets, bad magic, ESTALE generation checks, and parent lookup on damaged directories. Test signals include positive and negative lookups, NFS export handle decode, hard-linked aliases, `..` parent lookup, and corrupted directory images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/super.c -->
# sources/distributed-fs/ceph-client/fs/efs/super.c

## Purpose
`super.c` registers EFS, parses SGI volume headers and EFS superblocks, forces read-only mounts, owns the EFS inode slab, and reports filesystem statistics.

## Important APIs, types, and functions
Important functions include `init_efs_fs`, `exit_efs_fs`, `efs_init_fs_context`, `efs_get_tree`, `efs_fill_super`, `efs_validate_vh`, `efs_validate_super`, `efs_statfs`, `efs_kill_sb`, and inode-cache helpers. It defines `efs_fs_type`, `efs_superblock_operations`, and `efs_export_ops`.

## Control flow
Module init creates the inode cache and registers the filesystem. Mount allocates `efs_sb_info`, sets 512-byte block size, reads block 0 as an SGI volume header, validates checksum and chooses an EFS partition start if present, reads the EFS superblock, decodes geometry and counters, forces `SB_RDONLY`, installs super/export operations, loads the root inode, and creates the root dentry. Reconfigure syncs and preserves read-only state. Kill-super frees block-super resources and `s_fs_info`.

## State and persistence
Runtime superblock state includes filesystem start, total blocks/groups, inode blocks, and free counters decoded from disk. EFS is read-only, so persistent disk state is not modified.

## Dependencies and integration points
It depends on block devices, buffer heads, fs_context, SGI volume header definitions, EFS superblock definitions, VFS exportfs, and the EFS inode loader.

## Risks and test signals
Risks include memory leaks on early mount errors, SGI partition-table checksum handling, accepting invalid geometry, root inode failures, and read-only enforcement. Test signals include mounting whole disks with SGI labels, mounting partitions without labels, invalid magic/checksum images, remount rw attempts, statfs values, and module load/unload loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/symlink.c -->
# sources/distributed-fs/ceph-client/fs/efs/symlink.c

## Purpose
`symlink.c` supplies EFS symlink address-space behavior so symbolic link targets can be read from read-only EFS extents.

## Important APIs, types, and functions
The exported object is `efs_symlink_aops`. The main callback reads symlink data through the same block-mapping mechanism used for regular file data.

## Control flow
When a symlink inode is loaded, `efs_iget` assigns `page_symlink_inode_operations`, disables highmem for the inode, and attaches `efs_symlink_aops`. Link resolution then reads folios through block mapping, ultimately using `efs_get_block`/`efs_map_block`.

## State and persistence
No state changes occur. Persistent symlink contents live in the EFS extent-backed file data.

## Dependencies and integration points
It integrates with VFS page symlink operations, EFS inode setup, and the extent mapping code in `inode.c`.

## Risks and test signals
Risks include truncated symlink targets, block mapping failures, and highmem assumptions. Test signals include short and multi-block symlinks, broken/corrupt extent maps, and path resolution through nested symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/efs/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/erofs/Kconfig

## Purpose
`Kconfig` defines build-time features for EROFS, a modern read-only filesystem for immutable images, containers, application sandboxes, datasets, and remote/on-demand blobs.

## Important APIs, types, and functions
Important symbols include `EROFS_FS`, `EROFS_FS_DEBUG`, `EROFS_FS_XATTR`, `EROFS_FS_POSIX_ACL`, `EROFS_FS_SECURITY`, `EROFS_FS_BACKED_BY_FILE`, `EROFS_FS_ZIP`, algorithm options for LZMA/DEFLATE/ZSTD, `EROFS_FS_ZIP_ACCEL`, deprecated `EROFS_FS_ONDEMAND`, per-CPU kthread options, and experimental `EROFS_FS_PAGE_CACHE_SHARE`.

## Control flow
There is no runtime control flow. Symbol selections pull in dependencies such as CRC32, FS_IOMAP, decompression libraries, crypto acceleration, fscache/cachefiles, and netfs support.

## State and persistence
The file has no runtime state. It shapes supported on-disk feature compatibility at build time, especially compressed, xattr, file-backed, fscache, and page-cache-sharing behavior.

## Dependencies and integration points
It integrates EROFS with block devices, iomap, optional xattr/ACL/security stacks, compression libraries, crypto acomp, fscache, cachefiles, and netfs.

## Risks and test signals
Risks include unsupported filesystem images when compression algorithms are disabled, deprecated fscache behavior, feature combinations such as page-cache-share excluding ondemand, and debug-only consistency checks. Test signals include build matrices across compression and I/O modes plus mount attempts for images with each advertised on-disk feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Makefile -->
# sources/distributed-fs/ceph-client/fs/erofs/Makefile

## Purpose
The EROFS Makefile assembles the core filesystem and optional feature objects based on Kconfig selections.

## Important APIs, types, and functions
The base `erofs.o` includes `super.o`, `inode.o`, `data.o`, `namei.o`, `dir.o`, and `sysfs.o`. Optional additions cover xattrs, compressed mapping/decompression, LZMA/DEFLATE/ZSTD algorithms, crypto acceleration, file-backed I/O, fscache, and inode sharing.

## Control flow
No runtime flow exists. Kbuild composes the module or built-in object with only the selected feature units.

## State and persistence
No state is stored here. It controls which runtime feature implementations are present.

## Dependencies and integration points
It mirrors the Kconfig feature split and determines which symbols must be stubbed by headers versus provided by compiled objects.

## Risks and test signals
Risks are unresolved symbols in uncommon feature combinations and missing objects for new features. Test signals are allmodconfig-style builds and targeted matrices for ZIP, FILEIO, ONDEMAND, and PAGE_CACHE_SHARE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/compress.h -->
# sources/distributed-fs/ceph-client/fs/erofs/compress.h

## Purpose
`compress.h` defines the internal decompression request and decompressor operation interface used by EROFS compressed data paths.

## Important APIs, types, and functions
Key types are `struct z_erofs_decompress_req` and `struct z_erofs_decompressor`. A request carries input/output page arrays, page offsets, input/output sizes, algorithm id, in-place/partial/fill-gap flags, superblock, and GFP flags. A decompressor supplies optional `config`, `decompress`, `init`, `exit`, and a name.

## Control flow
The header has no runtime flow. Compressed read paths construct requests, select a decompressor from the algorithm table in `decompressor.c`, and call the common function pointers declared by this interface.

## State and persistence
No state lives in the header. It describes transient decompression work and algorithm-global lifecycle hooks.

## Dependencies and integration points
It includes `internal.h` for EROFS types and is used by LZ4, LZMA, DEFLATE, ZSTD, and crypto decompressor implementations.

## Risks and test signals
Risks include request fields not being initialized consistently, algorithm implementations disagreeing about NULL output pages or partial decoding, and lifecycle hooks not matching Makefile/Kconfig combinations. Test signals include compressed reads for every algorithm, in-place I/O, partial decode, sparse output gaps, and low-memory allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/compress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/data.c -->
# sources/distributed-fs/ceph-client/fs/erofs/data.c

## Purpose
`data.c` implements EROFS metadata buffering, logical-to-physical block mapping for uncompressed and chunked files, device mapping for multi-device images, online folio completion tracking, iomap integration, direct/DAX/buffered reads, fiemap, and regular file operations.

## Important APIs, types, and functions
Important functions include `erofs_bread`, `erofs_init_metabuf`, `erofs_read_metabuf`, `erofs_put_metabuf`, `erofs_map_blocks`, `erofs_map_dev`, online folio helpers, `erofs_fiemap`, `erofs_read_folio`, `erofs_readahead`, `erofs_file_read_iter`, `erofs_file_llseek`, and the exported `erofs_aops` and `erofs_file_fops`. It uses `struct erofs_buf`, `struct erofs_map_blocks`, and `struct erofs_map_dev`.

## Control flow
Metadata reads select the correct mapping from block device, file-backed image, fscache blob, or metabox inode, then cache and kmap the needed page. `erofs_map_blocks` handles flat plain, inline tail-packing, and chunk-based files, returning mapped, hole, meta, device id, logical length, and physical address data. `erofs_map_dev` resolves primary, flat, or external devices. The iomap callbacks translate maps into `IOMAP_MAPPED`, `IOMAP_HOLE`, or `IOMAP_INLINE`. Regular reads choose DAX, direct iomap DIO, or page-cache reads.

## State and persistence
Persistent state is on-disk EROFS metadata and data extents. Runtime state includes temporary metadata buffers, device idr mappings, folio private counters for multi-part read completion, and page cache contents. No writes to the filesystem image occur.

## Dependencies and integration points
It depends on iomap, DAX, buffer/page cache APIs, file-backed VFS reads, fscache mode selection, multi-device metadata, tracepoints, and optional inode sharing through `erofs_real_inode`.

## Risks and test signals
Risks include inline data crossing block boundaries, chunk index corruption, multi-device id resolution errors, stale metadata mappings, folio completion counter bugs, direct I/O alignment reporting mismatches, and DAX mapping mistakes. Test signals include flat, inline, sparse, chunked, 48-bit, multi-device, file-backed, fscache, DAX, direct I/O, fiemap, SEEK_DATA/SEEK_HOLE, and metabox metadata images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor.c

## Purpose
`decompressor.c` provides the common EROFS compressed-data decompressor registry, LZ4 implementation, plain shifted/interlaced transforms, compressed-size fixup, stream buffer switching support, compression config parsing, and decompressor subsystem init/exit.

## Important APIs, types, and functions
Important functions include `z_erofs_load_lz4_config`, `z_erofs_lz4_decompress`, `z_erofs_fixup_insize`, `z_erofs_transform_plain`, `z_erofs_stream_switch_bufs`, `z_erofs_parse_cfgs`, `z_erofs_init_decompressor`, and `z_erofs_exit_decompressor`. It defines the `z_erofs_decomp[]` algorithm table.

## Control flow
Mount-time config parsing either loads legacy LZ4 settings from the superblock or walks compression configuration records after the superblock, enabling only algorithms compiled into the kernel. LZ4 decompression prepares destination pages, decides whether contiguous direct mapping is possible, handles in-place overlap by direct reuse, vmapped input, or per-CPU bounce buffers, fixes leading zero padding to obtain exact compressed size, and invokes safe or partial LZ4 decode. Plain transform copies or moves shifted/interlaced data without decompression. Stream switching supplies input/output page transitions and overlap bounce logic for LZMA/DEFLATE/ZSTD.

## State and persistence
Runtime state includes superblock LZ4 limits, global decompressor registrations, temporary pagepool pages, and per-CPU/global buffers. Persistent state is only read from on-disk compression config records.

## Dependencies and integration points
It depends on LZ4, vm_map_ram, pagepool helpers, EROFS compressed map metadata, optional algorithm modules, and zdata/zmap callers that create requests.

## Risks and test signals
Risks include overlap corruption during in-place decompression, invalid zero-padding fixups, unsupported algorithm bits, huge pcluster limits, partial decode edge cases, and buffer lifecycle leaks. Test signals include LZ4 legacy and config-table images, shifted/interlaced pclusters, in-place and non-in-place I/O, sparse output gaps, partial reads, unsupported algorithms, and low-memory pagepool paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_crypto.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_crypto.c

## Purpose
`decompressor_crypto.c` adds optional hardware/crypto API decompression engines for EROFS compressed data, currently wiring named crypto acomp engines such as `qat_deflate`.

## Important APIs, types, and functions
Important functions are `z_erofs_crypto_decompress`, `z_erofs_crypto_enable_engine`, `z_erofs_crypto_disable_all_engines`, and `z_erofs_crypto_show_engines`. Internal state is `struct z_erofs_crypto_engine` arrays indexed by EROFS compression algorithm and guarded by `z_erofs_crypto_rwsem`.

## Control flow
Decompression takes a read lock, locates an enabled engine for the request algorithm, fills any missing output pages from the pagepool, builds source and destination scatterlists from page arrays and offsets, allocates an acomp request, submits `crypto_acomp_decompress`, waits synchronously, converts failures to `-EIO`, and frees tables/requests. Engine enable scans the configured names, allocates the crypto transform, and stores it; disable frees all enabled transforms.

## State and persistence
State is runtime-only: enabled crypto transform pointers and their names. No on-disk state changes; the same compressed bytes remain readable through software fallback if acceleration is unavailable.

## Dependencies and integration points
It depends on Linux crypto acomp, scatterlist helpers, EROFS pagepool, and the algorithm wrappers that attempt crypto acceleration before software decode.

## Risks and test signals
Risks include scatterlist construction over invalid page arrays, output gap allocation failures, transform lifetime races, name-prefix matching surprises, and synchronous wait latency. Test signals include enabling/disabling engines via sysfs or module controls, deflate reads with QAT available/unavailable, concurrent compressed reads during disable, partial decoding fallback, and crypto error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_deflate.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_deflate.c

## Purpose
`decompressor_deflate.c` implements EROFS DEFLATE compressed-data support using in-kernel zlib, with optional crypto acceleration for full decodes.

## Important APIs, types, and functions
The exported decompressor is `z_erofs_deflate_decomp`. Important functions are `z_erofs_deflate_init`, `z_erofs_deflate_exit`, `z_erofs_load_deflate_config`, `z_erofs_deflate_decompress`, and internal `__z_erofs_deflate_decompress`. Runtime stream state is `struct z_erofs_deflate`, with a zlib stream, workspace, bounce page, global stream list, spinlock, waitqueue, and `deflate_streams` module parameter.

## Control flow
Init chooses a stream count defaulting to possible CPUs. Config validates the on-disk deflate config and lazily allocates zlib workspaces once. Decompression fixes compressed input size, optionally tries crypto acceleration when not partial, waits for an available stream, initializes raw deflate inflate, uses `z_erofs_stream_switch_bufs` to feed multi-page input/output with overlap protection, inflates until output is satisfied or stream ends, ends zlib state, returns the stream to the global list, and wakes waiters.

## State and persistence
Runtime state is the global stream pool and allocated zlib workspaces. Persistent state is the on-disk DEFLATE config and compressed data read only.

## Dependencies and integration points
It depends on zlib inflate, EROFS stream switching, crypto acceleration when enabled, waitqueues, spinlocks, and decompressor config parsing.

## Risks and test signals
Risks include stream-pool deadlocks, ignoring unsupported windowbits because kernel zlib cannot customize it, partial decode termination mistakes, workspace allocation failure, and missed wakeups. Test signals include DEFLATE images, concurrent reads exceeding stream count, partial and full reads, crypto fallback, corrupt compressed streams, and low-memory config initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_lzma.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_lzma.c

## Purpose
`decompressor_lzma.c` implements microLZMA decompression for EROFS compressed files.

## Important APIs, types, and functions
The exported decompressor is `z_erofs_lzma_decomp`. Important functions are `z_erofs_lzma_init`, `z_erofs_lzma_exit`, `z_erofs_load_lzma_config`, and `z_erofs_lzma_decompress`. Runtime state is `struct z_erofs_lzma`, global stream list, max dictionary size, spinlock, waitqueue, and `lzma_streams` module parameter.

## Control flow
Init allocates a stream pool defaulting to possible CPUs. Config validates format and dictionary size, isolates available streams under a resize mutex, reallocates each xz microLZMA decoder for the larger dictionary if needed, returns streams to the pool, updates max dictionary size, and wakes waiters. Decompression fixes input size, waits for a stream, resets the microLZMA decoder for the request, then repeatedly uses common stream buffer switching and `xz_dec_microlzma_run` until output is complete or an error/end condition occurs.

## State and persistence
Runtime state is the decoder pool and maximum dictionary size observed from mounted filesystems. Persistent state is the read-only on-disk LZMA config and compressed clusters.

## Dependencies and integration points
It depends on XZ microLZMA, EROFS stream switching, pagepool, waitqueues, spinlocks, and decompressor config parsing.

## Risks and test signals
Risks include stream isolation races during dictionary resize, waiting while all streams are active, invalid dictionary bounds, partial decoding semantics, and decoder allocation failures. Test signals include LZMA images with minimum/maximum dictionaries, concurrent reads, config resize across mounts, corrupt streams, partial reads, and module unload after all mounts are gone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_lzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_zstd.c -->
# sources/distributed-fs/ceph-client/fs/erofs/decompressor_zstd.c

## Purpose
`decompressor_zstd.c` implements Zstandard decompression for EROFS compressed data.

## Important APIs, types, and functions
The exported decompressor is `z_erofs_zstd_decomp`. Important functions are `z_erofs_zstd_init`, `z_erofs_zstd_exit`, `z_erofs_load_zstd_config`, `z_erofs_zstd_decompress`, and stream isolation helper `z_erofs_isolate_strms`. Runtime state is `struct z_erofs_zstd`, workspace size, max dictionary size, stream list, waitqueue, spinlock, and `zstd_streams` module parameter.

## Control flow
Init allocates stream records. Config validates ZSTD format/window log, computes dictionary size, isolates all streams under a resize mutex, allocates larger workspaces with `kvmalloc` as needed, restores the stream list, updates max dictionary size, and wakes waiters. Decompression fixes compressed input size, takes one stream, initializes a zstd dstream with the max dictionary/workspace, uses common stream buffer switching for page transitions and overlap handling, calls `zstd_decompress_stream` until all output is produced, then returns the stream.

## State and persistence
Runtime state is the reusable workspace pool and maximum dictionary size. Persistent on-disk state is the ZSTD compression config and compressed clusters.

## Dependencies and integration points
It depends on the in-kernel ZSTD library, EROFS stream switching, pagepool, waitqueues, and the common decompressor registry.

## Risks and test signals
Risks include workspace resize races, incomplete stream-end detection, ZSTD error-name propagation, excessive memory footprint with high stream counts, and blocked readers when streams are exhausted. Test signals include ZSTD images at varied window logs, concurrent reads, corrupt streams, partial reads, low-memory resize failure, and mount/unmount after ZSTD config parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/decompressor_zstd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/dir.c -->
# sources/distributed-fs/ceph-client/fs/erofs/dir.c

## Purpose
`dir.c` implements EROFS directory iteration and directory file operations.

## Important APIs, types, and functions
Important functions are `erofs_readdir` and `erofs_fill_dentries`. The exported table is `erofs_dir_fops`. It reads `struct erofs_dirent` records and emits VFS entries with inode numbers converted through `erofs_nid_to_ino64`.

## Control flow
`erofs_readdir` walks directory blocks from `ctx->pos`, performs readahead for large directories, reads each block with `erofs_bread`, validates the first `nameoff`, adjusts arbitrary starting positions, and delegates record emission. `erofs_fill_dentries` computes each name length from the next record's offset or trailing string length, validates length/range, emits the entry, and advances position. If the on-disk directory omits `.`, a synthetic dot entry is emitted after normal entries.

## State and persistence
No persistent state changes. Runtime state includes directory page cache, readahead state, and `ctx->pos`.

## Dependencies and integration points
It depends on EROFS metadata/page-cache reads, directory block format, VFS dir_context, ioctl forwarding, compat ioctl, and generic leases.

## Risks and test signals
Risks include corrupted `nameoff` values, invalid name lengths, position rounding bugs, dot-omitted synthetic entry handling, and large-directory readahead behavior. Test signals include sorted directory images, malformed directory blocks, resume offsets, directories omitting `.`, long names, fatal-signal interruption, and ioctl passthrough on directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/erofs_fs.h -->
# sources/distributed-fs/ceph-client/fs/erofs/erofs_fs.h

## Purpose
`erofs_fs.h` defines the EROFS on-disk format: superblock, device table, inode layouts, xattrs, chunk indexes, directory entries, compression config, compressed map headers, and compile-time layout checks.

## Important APIs, types, and functions
Key definitions include feature flags, `struct erofs_super_block`, inode datalayout enum, compact and extended inode structs, xattr headers/entries, `struct erofs_inode_chunk_index`, `struct erofs_dirent`, compression algorithm ids, algorithm config structs, `struct z_erofs_map_header`, `struct z_erofs_lcluster_index`, `struct z_erofs_extent`, and `erofs_check_ondisk_layout_definitions`.

## Control flow
The header has no runtime control flow, but mount and inode readers interpret every EROFS image through these structures and feature masks. Compile-time `BUILD_BUG_ON` checks ensure struct sizes and special bit placement remain stable.

## State and persistence
It describes persistent disk state: feature compatibility, block size, root nid, metadata starts, xattr starts, external devices, packed/metabox inode ids, inode contents, xattr filters, chunk maps, directories, and compressed cluster metadata.

## Dependencies and integration points
It is the local on-disk ABI consumed by `super.c`, `inode.c`, `data.c`, xattr code, zmap/zdata, and decompressor config parsing. It must stay compatible with userspace mkfs tooling and kernel documentation.

## Risks and test signals
Risks include ABI-breaking struct layout changes, feature flag aliasing, 48-bit address parsing mistakes, compression metadata version mismatches, and endian handling errors. Test signals include compile-time layout checks, mounts of images using each feature bit, big-endian/little-endian parsing tests, and fsck/mkfs interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/erofs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fileio.c -->
# sources/distributed-fs/ceph-client/fs/erofs/fileio.c

## Purpose
`fileio.c` implements EROFS reads from filesystem image files, avoiding loop devices for file-backed images. It reads data through backing file `kiocb` operations while preserving EROFS folio completion semantics.

## Important APIs, types, and functions
Important types are `struct erofs_fileio_rq` and `struct erofs_fileio`. Important functions include `erofs_fileio_bio_alloc`, `erofs_fileio_submit_bio`, `erofs_fileio_scan_folio`, `erofs_fileio_read_folio`, `erofs_fileio_readahead`, and request allocation/completion helpers. It exports `erofs_fileio_aops`.

## Control flow
Scan initializes online folio tracking, maps file logical ranges with `erofs_map_blocks`, copies inline metadata directly, zero-fills holes, or batches mapped data into a backing-file read request. Requests use embedded bio vectors for page/offset/length accounting, then submit `vfs_iocb_iter_read` under the backing file credentials, optionally with `IOCB_DIRECT` when mount/direct and backing file support allow it. Completion checks short reads, ends online folio pieces or bio endio, uninitializes the bio, and drops request refs.

## State and persistence
Runtime state is request/bio/iocb refs, folio private counters, and backing file page cache or direct I/O state. The EROFS image and backing file are read-only from this path.

## Dependencies and integration points
It depends on EROFS block/device mapping, file-backed device info, VFS backing-file reads, credentials scoping, bio_vec helpers, and online folio completion in `data.c`.

## Risks and test signals
Risks include short-read handling, request refcount leaks, incorrect merging across device/physical discontinuities, `O_DIRECT` compatibility, and credential/path lifetime bugs. Test signals include file-backed mounts over regular files and block files, inline tails, holes, fragmented extents, readahead batching, direct I/O option, short read/error injection, and inode-sharing reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fileio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fscache.c -->
# sources/distributed-fs/ceph-client/fs/erofs/fscache.c

## Purpose
`fscache.c` implements deprecated fscache/cachefiles-backed on-demand EROFS access. It registers volumes/cookies, creates anonymous inodes for blobs, reads metadata and data through netfs cache operations, and supports shared domains for deduplicated blob access.

## Important APIs, types, and functions
Important types are `struct erofs_fscache_io`, `struct erofs_fscache_rq`, and `struct erofs_fscache_bio`. Important functions include `erofs_fscache_read_io_async`, metadata/data folio read and readahead helpers, `erofs_fscache_bio_alloc`, `erofs_fscache_submit_bio`, cookie/domain register/unregister helpers, `erofs_fscache_register_fs`, and `erofs_fscache_unregister_fs`. It exports `erofs_fscache_access_aops`.

## Control flow
Reads allocate request objects covering folio or readahead ranges, map logical data with `erofs_map_blocks`, copy inline metadata, zero holes, or resolve device cookies and issue on-demand fscache reads into xarray iterators. Completion marks folios uptodate or records errors and unlocks them. Registration creates or reuses fscache volumes, optionally creates shared domains backed by a pseudo mount, enforces primary blob uniqueness in shared domains, acquires cookies, calls `fscache_use_cookie`, and creates anonymous metadata inodes using fscache meta aops.

## State and persistence
Runtime state includes global domain/cookie lists, pseudo mount, fscache volumes/cookies, anonymous inodes, request refs, and cache resources. Persistent data is external cache content and the immutable EROFS blobs; this code does not modify filesystem images.

## Dependencies and integration points
It depends on fscache, cachefiles ondemand, netfs APIs, EROFS map/dev resolution, anonymous filesystem mounts, xarray iterators, and multi-device blob naming.

## Risks and test signals
Risks include domain/cookie refcount leaks, shared-domain name collisions, incomplete async read completion, folio unlock without uptodate on errors, pseudo mount lifetime, and deprecated API behavior. Test signals include fscache mounts with and without domains, duplicate fsid in a domain, metadata reads, data readahead, holes and inline data, external devices, cache read failures, and concurrent unregister during I/O teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/fscache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/inode.c -->
# sources/distributed-fs/ceph-client/fs/erofs/inode.c

## Purpose
`inode.c` reads EROFS on-disk inodes, initializes VFS inode state and operations, supports fast symlinks, exposes stat/fiemap/ioctl behavior, and maps NIDs to stable inode-cache keys.

## Important APIs, types, and functions
Important functions include `erofs_read_inode`, `erofs_fill_symlink`, `erofs_fill_inode`, `erofs_iget`, `erofs_getattr`, `erofs_ioctl`, `erofs_compat_ioctl`, and `erofs_ioctl_get_volume_label`. It exports inode operation tables `erofs_generic_iops`, `erofs_symlink_iops`, and `erofs_fast_symlink_iops`.

## Control flow
`erofs_read_inode` locates inode metadata by NID, handles metabox inodes, reads compact or extended inode layouts across block boundaries, decodes mode, uid/gid, nlink, size, times, xattr size, datalayout, start block, device id, chunk info, compressed block counts, and DAX eligibility. Symlinks with inline data are copied into a cached NUL-terminated link. `erofs_fill_inode` assigns file, directory, symlink, or special operations, enables large folios, chooses address-space operations based on datalayout and I/O mode, and optionally enables inode sharing. `erofs_iget` uses `iget5_locked` keyed by NID.

## State and persistence
Persistent state is on-disk inode metadata. Runtime state includes `struct erofs_inode` fields, page-cache aops, cached symlink strings, inode sharing links, ACL/xattr initialization flags, and VFS inode cache membership.

## Dependencies and integration points
It depends on EROFS metadata reads, xattr/ACL helpers, data and compressed aops selection, inode-sharing support, VFS stat/ioctl/fiemap, and metabox-aware NID conversion.

## Risks and test signals
Risks include malformed inode formats, negative or overflowed sizes, xattr body size mistakes, 48-bit address decoding, compressed inodes when ZIP support is disabled, chunk format validation, fast symlink NUL validation, and DAX on unsupported layouts. Test signals include compact/extended inodes, all file types, inline symlinks, compressed and chunked files, metabox images, ACL/noacl xattrs, STATX attributes, volume-label ioctl, and 32-bit inode-number squashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/internal.h -->
# sources/distributed-fs/ceph-client/fs/erofs/internal.h

## Purpose
`internal.h` defines EROFS in-kernel private structures, mount options, feature helpers, mapping types, operation declarations, and compile-time stubs for optional subsystems.

## Important APIs, types, and functions
Key types include `struct erofs_device_info`, `struct erofs_mount_opts`, `struct erofs_dev_context`, `struct erofs_sb_info`, `struct erofs_buf`, `struct erofs_inode`, `struct erofs_map_blocks`, and `struct erofs_map_dev`. It declares core operations, aops/fops/iops, mapping/read helpers, decompression lifecycle, fscache/fileio hooks, inode-share hooks, ioctl helpers, and feature-test inline functions.

## Control flow
The header has no direct runtime flow. It routes call sites through inline feature checks such as fileio/fscache mode and `erofs_get_aops`, which selects compressed, fscache, file-backed, or normal address-space operations. Optional features compile to real declarations or no-op/error stubs.

## State and persistence
It defines runtime superblock and inode state for devices, compression, xattrs, metabox, packed inode, sysfs, fscache domains, page-cache sharing, and mount flags. Persistent disk state is referenced through fields decoded from `erofs_fs.h`.

## Dependencies and integration points
It depends on VFS, DAX, bio, pagemap, iomap, xarray, module, and EROFS on-disk definitions. Every EROFS implementation file includes it, making it the central internal ABI.

## Risks and test signals
Risks include feature-stub mismatches, stale declarations, incorrect aops selection when modes combine, and struct field assumptions across optional configs. Test signals include compile matrices for every optional feature, normal/compressed/fileio/fscache address-space selection, multi-device map resolution, and mount option bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/ishare.c -->
# sources/distributed-fs/ceph-client/fs/erofs/ishare.c

## Purpose
`ishare.c` implements experimental EROFS page-cache sharing for files with identical content fingerprints. It maps multiple real EROFS inodes to anonymous shared inodes so their cached pages can be reused.

## Important APIs, types, and functions
Important functions include `erofs_ishare_fill_inode`, `erofs_ishare_free_inode`, `erofs_real_inode`, `erofs_init_ishare`, `erofs_exit_ishare`, and file-operation wrappers for open/read/mmap/release/fadvise. It exports `erofs_ishare_fops`.

## Control flow
When a regular inode is filled, the code obtains a fingerprint from xattrs plus domain id, hashes it with xxhash, and looks up or creates an anonymous shared inode in a private EROFS anon mount. New shared inodes receive the real file's aops and size; existing ones must match aops and size. Real inodes are linked under the shared inode. Opening an ishare file creates a backing file pointing at the shared inode and original user path; reads and mmap use that realfile. `erofs_real_inode` resolves anonymous shared inodes back to any live real inode for mapping.

## State and persistence
Runtime state includes the anonymous mount, shared inode fingerprints, shared-to-real inode lists, spinlocks, backing file objects, and references. No on-disk state changes; fingerprints come from persistent xattrs.

## Dependencies and integration points
It depends on xattr fingerprint helpers, xxhash, anonymous filesystem mounts, VFS backing files, security mmap checks, page cache, and `erofs_get_aops`.

## Risks and test signals
Risks include fingerprint collision or stale xattr assumptions, size/aops mismatch, list lifetime races, O_DIRECT rejection behavior, mmap security checks, and anonymous mount teardown. Test signals include two images/files with identical fingerprints, mismatched sizes with same fingerprint, read/mmap/fadvise through ishare fops, inode eviction, concurrent opens while freeing real inodes, and feature exclusion with fscache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/ishare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/namei.c -->
# sources/distributed-fs/ceph-client/fs/erofs/namei.c

## Purpose
`namei.c` implements EROFS directory lookup. It exploits alphabetically sorted directory entries to binary-search both directory blocks and entries within a block.

## Important APIs, types, and functions
Important functions include `erofs_dirnamecmp`, `find_target_dirent`, `erofs_find_target_block`, `erofs_namei`, and VFS lookup wrapper `erofs_lookup`. It exports `erofs_dir_iops`.

## Control flow
Lookup rejects names longer than `EROFS_NAME_LEN`, then `erofs_namei` builds a query string and searches directory blocks. `erofs_find_target_block` binary-searches blocks by comparing the first name in each block, preserving matched prefix lengths to reduce comparisons and retaining the last candidate block. If needed, `find_target_dirent` binary-searches entries inside the candidate block. On success the nid and file type are returned and `erofs_lookup` instantiates the inode through `erofs_iget`; `-ENOENT` creates a negative dentry.

## State and persistence
No persistent state changes. Runtime state is metadata buffer ownership during search and dentry/inode cache results.

## Dependencies and integration points
It depends on sorted EROFS directory format, `erofs_bread`, NID-based inode loading, tracepoints, xattr/ACL-capable directory inode operations, and VFS dentry splicing.

## Risks and test signals
Risks include corrupted `nameoff` values, binary-search assumptions violated by unsorted directories, prefix-cache comparison bugs, candidate buffer lifetime mistakes, and metabox NID handling. Test signals include positive/negative lookup, first/last/middle entries, single-entry blocks, unsorted or corrupt directory blocks, long-name rejection, and lookup in metabox-backed directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/namei.c -->
