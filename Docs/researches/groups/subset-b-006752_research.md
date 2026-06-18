# subset-b-006752 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/i915_drm.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/i915_drm.h

## Purpose

`i915_drm.h` is a mirrored Linux UAPI header for the Intel i915 DRM driver. In this `tools/perf/trace/beauty/include/uapi` tree it gives perf trace's "beauty" decoders the same ioctl command numbers, structures, flags, and enum values used by userspace talking to `/dev/dri/*` i915 devices. The file is not an implementation of GPU work; it is the ABI contract that allows tools to format i915-specific ioctls, perf-event identifiers, GEM object operations, context setup, performance streams, query blobs, memory-region descriptions, and protected-content creation consistently with the kernel.

Because it is a large compatibility header, much of its value is in stable numeric assignments and struct layout. Many comments explicitly warn that structs are subject to backwards-compatibility constraints, unused bits must be zero, and several removed APIs must keep their identifiers reserved.

## Important APIs, Types, and Constants

Important top-level identifiers include:

- Uevent strings: `I915_L3_PARITY_UEVENT`, `I915_ERROR_UEVENT`, and `I915_RESET_UEVENT`.
- Extension chaining: `struct i915_user_extension`, used by context creation, execbuffer extensions, VM creation, and GEM create extensions.
- Engine identity: `enum drm_i915_gem_engine_class` and `struct i915_engine_class_instance`, including render, copy, video, video-enhance, compute, and invalid engine markers.
- i915 PMU encodings: `I915_PMU_ENGINE_BUSY`, `I915_PMU_ENGINE_WAIT`, `I915_PMU_ENGINE_SEMA`, `I915_PMU_ACTUAL_FREQUENCY`, `I915_PMU_RC6_RESIDENCY`, and GT-indexed variants.
- DRM ioctl offsets from `DRM_COMMAND_BASE`: legacy DRI ioctls, GEM creation and mapping, execbuffer submission, context create/destroy/getparam/setparam, i915 perf open/config, `DRM_I915_QUERY`, VM create/destroy, and `DRM_I915_GEM_CREATE_EXT`.
- GEM object structures: `drm_i915_gem_create`, `pread`, `pwrite`, `mmap`, `mmap_gtt`, `mmap_offset`, `set_domain`, `sw_finish`, `relocation_entry`, `exec_object`, `exec_object2`, `execbuffer`, `execbuffer2`, `pin`, `busy`, `caching`, `set_tiling`, `get_tiling`, `madvise`, `wait`, and `userptr`.
- Execution flags: `EXEC_OBJECT_*`, `I915_EXEC_*`, sync-file and syncobj fence flags, batch-first and extension flags, BSD ring selection, no-reloc, handle-LUT, secure batch, and timeline fences.
- Context APIs: `drm_i915_gem_context_create_ext`, `drm_i915_gem_context_param`, `drm_i915_gem_context_param_sseu`, engine-map structures, load-balancing, bond, and parallel-submit extension layouts.
- Perf stream APIs: `enum drm_i915_oa_format`, `enum drm_i915_perf_property_id`, `drm_i915_perf_open_param`, i915 perf stream ioctls, perf record headers, record types, and dynamic OA config upload.
- Query APIs: `drm_i915_query`, `drm_i915_query_item`, topology, engine info, perf config, memory regions, GuC submission version, and GuC HWCONFIG blob query IDs.
- Memory-region and create-extension APIs: `I915_MEMORY_CLASS_SYSTEM`, `I915_MEMORY_CLASS_DEVICE`, `drm_i915_memory_region_info`, `drm_i915_gem_create_ext`, memory-region placement, protected-content, PAT, and `I915_PROTECTED_CONTENT_DEFAULT_SESSION`.

## Control Flow and Integration

The header has no runtime control flow, but it describes several user/kernel protocol flows:

1. A userspace process issues a DRM ioctl such as `DRM_IOCTL_I915_GEM_CREATE`, `DRM_IOCTL_I915_GEM_EXECBUFFER2`, `DRM_IOCTL_I915_QUERY`, or `DRM_IOCTL_I915_PERF_OPEN`.
2. The ioctl macro encodes command number, direction, and struct type through DRM's ioctl helpers from `drm.h`.
3. Userspace passes the matching struct. Many structs carry `__u64` pointer fields to maintain 32/64-bit ABI compatibility; older typedefs still expose raw `__user *` pointers and require compat handling.
4. The i915 kernel driver validates flags, reserved fields, object handles, context IDs, engine class/instance pairs, memory-region placements, and extension chains.
5. The kernel updates output fields such as GEM handles, fake mmap offsets, query lengths, query blobs, busy status, perf stream file descriptors, returned fences, or memory-region information.

For perf trace, the integration is narrower: the header feeds generated or hand-written decoder tables so i915-specific ioctl numbers and bit fields can be printed symbolically instead of as opaque integers.

## State and Persistence Behavior

The file itself persists no state. It defines ABI objects that create, mutate, or query persistent kernel-driver state tied to a DRM file descriptor or GPU device:

- GEM handles represent buffer objects scoped to a DRM file.
- Context IDs carry engine maps, scheduler parameters, persistence, protected-content state, VM binding, SSEU settings, and recovery behavior.
- VM IDs identify per-process GPU address spaces.
- i915 perf streams are file descriptors whose enable/disable/config state affects data capture.
- Query and memory-region structures expose hardware and driver state but do not create long-lived state.
- Protected-content objects and contexts depend on PXP session state and become invalid after session teardown.

Many fields are intentionally immutable at creation time, especially newer GEM create extensions for memory placement and caching/PAT policy.

## Dependencies and Integration Points

The header depends on `drm.h` for DRM ioctl encodings and DRM base types. It depends on Linux UAPI types such as `__u32`, `__u64`, `__s64`, `__user`, and ioctl direction macros through the included DRM and kernel headers. It is coupled to the i915 kernel driver, Mesa/Intel userspace drivers, intel-gpu-tools, perf's i915 PMU support, DRM syncobj/sync_file APIs, and virtual-memory/memory-region concepts introduced for newer discrete Intel GPUs.

Within perf, the key integration points are `DRM_IOCTL_I915_*` command decoding, i915 PMU event ID formatting, and symbolic printing of flag fields such as `I915_EXEC_*`, `EXEC_OBJECT_*`, context flags, query IDs, and memory classes.

## Risks

- Numeric ioctl offsets are ABI; adding holes or renumbering breaks user/kernel and trace decoding compatibility.
- Unknown flag masks and reserved MBZ fields must remain strict. Decoders should not treat undefined bits as known semantics.
- Several APIs are removed but their numbers are reserved, such as old execbuffer, context clone, and removed context parameters. Reusing them would misdecode old traces and break userspace assumptions.
- `__u64` user pointers require care when decoding traces from 32-bit tasks; older raw pointer fields also imply compat paths.
- Extension chains cross the user/kernel boundary and can point to variable-size packed structures; trace tooling should avoid dereferencing captured pointers blindly.
- Some comments document hardware-generation restrictions, for example DG1+ caching behavior, small-BAR memory placement, protected-content dependencies, and unsupported userptr flags. A symbolic decoder cannot infer success from the input struct alone.
- `DRM_IOCTL_I915_GEM_MMAP_OFFSET` aliases the same command slot as `DRM_IOCTL_I915_GEM_MMAP_GTT` but uses a different struct interpretation depending on intended API.

## Test Signals

Useful validation signals include:

- Compile a minimal TU including this mirrored header with the perf trace beauty include path.
- Compare `DRM_IOCTL_I915_*` values against the kernel UAPI header used by the target perf version.
- Decode traces containing `DRM_IOCTL_I915_GEM_CREATE`, `GEM_EXECBUFFER2`, `GEM_CONTEXT_CREATE_EXT`, `QUERY`, `PERF_OPEN`, and `GEM_CREATE_EXT`.
- Unit-check symbolic expansion for `I915_EXEC_FENCE_IN`, `I915_EXEC_FENCE_OUT`, `I915_EXEC_USE_EXTENSIONS`, `EXEC_OBJECT_ASYNC`, `EXEC_OBJECT_CAPTURE`, context params, query IDs, memory classes, and perf record types.
- Exercise 32-bit compat traces for structures containing pointer-valued fields.
- Validate that reserved/unknown bits remain visible as hex rather than being silently dropped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/i915_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fadvise.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fadvise.h

## Purpose

`fadvise.h` defines the Linux UAPI advice constants used by `posix_fadvise(2)` and related tracing paths. In the perf trace beauty mirror, it lets syscall decoders render file access pattern hints such as normal, random, sequential, will-need, do-not-need, and no-reuse.

## Important APIs, Types, and Constants

The header defines only preprocessor constants:

- `POSIX_FADV_NORMAL` = 0.
- `POSIX_FADV_RANDOM` = 1.
- `POSIX_FADV_SEQUENTIAL` = 2.
- `POSIX_FADV_WILLNEED` = 3.
- `POSIX_FADV_DONTNEED` and `POSIX_FADV_NOREUSE`, whose numeric values are architecture-dependent.

On `__s390x__`, `DONTNEED` is 6 and `NOREUSE` is 7. On other architectures, they are 4 and 5.

## Control Flow and Integration

There is no executable control flow. The only conditional behavior is compile-time architecture selection for s390x. Runtime flow is external: userspace passes one of these values to fadvise syscalls; the kernel interprets the value as a page-cache/readahead hint; perf trace can print the symbolic name from the numeric argument.

## State and Persistence Behavior

The header stores no state. The syscall using these constants may influence page-cache behavior, readahead heuristics, or discard of cached pages, but those effects live in the kernel's memory-management and filesystem code. The advice is a hint rather than a persistent file attribute.

## Dependencies and Integration Points

This header has no includes. It is coupled to architecture-specific Linux syscall ABI because s390x uses different `DONTNEED` and `NOREUSE` values. Perf decoders that build on a non-s390x host but decode s390x traces need to account for the traced architecture, not just the build host.

## Risks

- The s390x split is the main hazard. A single build-host-generated constant table can mislabel cross-architecture traces.
- These values are user ABI and should not be renumbered.
- Because fadvise calls are hints, tests should not assume an immediately observable filesystem state change after a successful call.

## Test Signals

Useful validation signals include:

- Verify non-s390x decoding of values 0 through 5 to the six expected names.
- Verify s390x decoding maps 6 and 7 to `POSIX_FADV_DONTNEED` and `POSIX_FADV_NOREUSE`.
- Compile-check inclusion under the perf trace beauty include tree.
- Trace `posix_fadvise` calls with `WILLNEED` and `DONTNEED` and confirm symbolic output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fadvise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fcntl.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fcntl.h

## Purpose

`fcntl.h` mirrors Linux-specific file-control and `*at(2)` constants used by `fcntl`, open-like syscalls, stat-like syscalls, pidfd/nsfs helpers, and directory notification APIs. In perf trace beauty it provides symbolic names for command values, seal flags, write-life hints, directory notify masks, special fd constants, and `AT_*` path-resolution flags.

## Important APIs, Types, and Constants

The header includes `<asm/fcntl.h>`, `<linux/openat2.h>`, and `<linux/types.h>`, so architecture-provided base constants and the openat2 ABI remain available.

Important definitions include:

- Linux-specific `fcntl` commands based on `F_LINUX_SPECIFIC_BASE`: `F_SETLEASE`, `F_GETLEASE`, `F_NOTIFY`, `F_DUPFD_QUERY`, `F_CREATED_QUERY`, `F_CANCELLK`, `F_DUPFD_CLOEXEC`, pipe-size controls, memfd seals, write-life hints, and delegation get/set.
- Seal flags: `F_SEAL_SEAL`, `F_SEAL_SHRINK`, `F_SEAL_GROW`, `F_SEAL_WRITE`, `F_SEAL_FUTURE_WRITE`, and `F_SEAL_EXEC`.
- Write-life hints: `RWH_WRITE_LIFE_NOT_SET`, `NONE`, `SHORT`, `MEDIUM`, `LONG`, and `EXTREME`, with compatibility spelling `RWF_WRITE_LIFE_NOT_SET`.
- `struct delegation` for `F_GETDELEG` and `F_SETDELEG`, carrying flags, lock type, and padding.
- Directory notification flags: `DN_ACCESS`, `DN_MODIFY`, `DN_CREATE`, `DN_DELETE`, `DN_RENAME`, `DN_ATTRIB`, and `DN_MULTISHOT`.
- Special fd values: `AT_FDCWD`, `PIDFD_SELF_THREAD`, `PIDFD_SELF_THREAD_GROUP`, `FD_PIDFS_ROOT`, `FD_NSFS_ROOT`, and `FD_INVALID`.
- Generic `AT_*` flags: `AT_SYMLINK_NOFOLLOW`, `AT_SYMLINK_FOLLOW`, `AT_NO_AUTOMOUNT`, `AT_EMPTY_PATH`, `AT_STATX_*`, and `AT_RECURSIVE`.
- Per-syscall overlapping flags: `AT_RENAME_*`, `AT_EACCESS`, `AT_REMOVEDIR`, `AT_HANDLE_*`, and `AT_EXECVE_CHECK`.

## Control Flow and Integration

The header has no runtime control flow. Its semantics are selected by syscall context:

1. `fcntl(fd, cmd, arg)` uses the `F_*` command space and then interprets `arg` as an integer, file descriptor, pointer, seal mask, pipe size, hint, or `struct delegation` depending on `cmd`.
2. `fcntl(fd, F_NOTIFY, mask)` uses the `DN_*` bits for dnotify-style directory event delivery.
3. `openat`, `statx`, `unlinkat`, `renameat2`, `name_to_handle_at`, `faccessat`, and newer `execveat2`-style calls use `AT_*` flags.
4. Perf trace beauty must decode `AT_*` flags with the syscall-specific context because some constants intentionally share numeric values.

## State and Persistence Behavior

The constants can affect kernel state indirectly:

- Leases, pipe sizes, seals, write-life hints, and delegations can persist on an open file description, inode, memfd, pipe, or filesystem object depending on the command.
- Directory notifications attach watch state to the file descriptor and may persist until descriptor close or replacement.
- `AT_*` flags are per-call selectors and do not persist.
- Special fd constants select implicit kernel objects rather than storing state.

The header itself is static ABI metadata.

## Dependencies and Integration Points

The main dependency is `F_LINUX_SPECIFIC_BASE` from `asm/fcntl.h`; changing or mismatching the architecture base would shift command numbers. It also integrates with `linux/openat2.h` path resolution flags, `linux/types.h` fixed-width types, VFS lock/delegation code, memfd sealing, pipe internals, dnotify, pidfs, nsfs, statx, and file-handle syscalls.

Perf integration is strongest for symbolic decoding of `fcntl` command numbers and `AT_*` flag masks in syscall traces.

## Risks

- Per-syscall `AT_*` flags intentionally overlap numerically. Generic flag decoders can print misleading names unless keyed by syscall.
- `FD_INVALID` is derived from a reserved fd range and `EBADF`; treating all negative fds as `AT_FDCWD`-style selectors would be wrong.
- Seal and write-life constants are ABI-visible. Adding names must preserve old spellings and values.
- `struct delegation` has MBZ fields; tests should catch non-zero reserved field handling in the kernel, while trace decoders should still display raw values.

## Test Signals

Useful validation signals include:

- Compile-check the header under a beauty-table generator.
- Decode `fcntl` commands for leases, pipe sizing, seals, and write-life hints.
- Decode `F_NOTIFY` masks including `DN_MULTISHOT`.
- Per-syscall tests showing `0x200` as `AT_EACCESS` for `faccessat`, `AT_REMOVEDIR` for `unlinkat`, and `AT_HANDLE_FID` for `name_to_handle_at`.
- Decode `AT_FDCWD`, pidfd self constants, pidfs/nsfs roots, and invalid fd values distinctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fs.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fs.h

## Purpose

`fs.h` is a broad Linux filesystem and block-device UAPI header. In this perf trace beauty mirror it supplies constants and structures needed to decode generic filesystem ioctls, block ioctls, clone/dedupe/trim requests, inode flags, extended file attributes, per-I/O flags, pagemap scanning, and `/proc/<pid>/maps` query ioctls.

The header is ABI-sensitive and explicitly instructs contributors to coordinate changes through linux-fsdevel and linux-api.

## Important APIs, Types, and Constants

Important groups include:

- File and block defaults: `INR_OPEN_CUR`, `INR_OPEN_MAX`, `BLOCK_SIZE_BITS`, `BLOCK_SIZE`, seek constants including `SEEK_DATA` and `SEEK_HOLE`, and `RENAME_*` flags.
- Integrity metadata flags: `IO_INTEGRITY_CHK_GUARD`, `REFTAG`, `APPTAG`, and `IO_INTEGRITY_VALID_FLAGS`.
- Clone, trim, UUID, sysfs path, and logical-block metadata structs: `file_clone_range`, `fstrim_range`, `fsuuid2`, `fs_sysfs_path`, and `logical_block_metadata_cap`.
- Deduplication ABI: `file_dedupe_range_info`, `file_dedupe_range`, `FILE_DEDUPE_RANGE_SAME`, and `FILE_DEDUPE_RANGE_DIFFERS`.
- File/inode statistics structs: `files_stat_struct` and `inodes_stat_t`.
- Extended attribute structs: `fsxattr`, versioned `file_attr`, and `FS_XFLAG_*` values.
- Block ioctls: `BLKROSET`, `BLKROGET`, `BLKRRPART`, `BLKGETSIZE`, readahead controls, sector size, block size, trace setup, discard, secure discard, zeroout, diskseq, and `BLKTRACESETUP2`.
- Filesystem ioctls: `FIBMAP`, `FIGETBSZ`, `FIFREEZE`, `FITHAW`, `FITRIM`, `FICLONE`, `FICLONERANGE`, `FIDEDUPERANGE`, `FS_IOC_GETFLAGS`, `SETFLAGS`, `GETVERSION`, `FIEMAP`, `FSGETXATTR`, `FSSETXATTR`, `GETFSLABEL`, `SETFSLABEL`, `GETFSUUID`, `GETFSSYSFSPATH`, and `GETLBMD_CAP`.
- Inode flags: `FS_IMMUTABLE_FL`, `FS_APPEND_FL`, `FS_NOATIME_FL`, `FS_ENCRYPT_FL`, `FS_VERITY_FL`, `FS_DAX_FL`, `FS_CASEFOLD_FL`, user-visible and user-modifiable masks.
- Per-I/O flags: bitwise `__kernel_rwf_t`, `RWF_HIPRI`, `RWF_DSYNC`, `RWF_SYNC`, `RWF_NOWAIT`, `RWF_APPEND`, `RWF_NOAPPEND`, `RWF_ATOMIC`, `RWF_DONTCACHE`, `RWF_NOSIGNAL`, and `RWF_SUPPORTED`.
- Procfs ioctl ABIs: `PAGEMAP_SCAN`, `page_region`, `pm_scan_arg`, `PAGE_IS_*`, `PM_SCAN_*`, `PROCMAP_QUERY`, `procmap_query_flags`, and `struct procmap_query`.

## Control Flow and Integration

This file contains declarative ABI definitions. External control flow includes:

1. Filesystem and block-device ioctls use `_IO`, `_IOR`, `_IOW`, and `_IOWR` command encodings. The command determines whether the pointed argument is input, output, or both.
2. Clone/dedupe/trim ioctls transfer fixed structs, some with flexible arrays, between userspace and filesystem implementations.
3. `FS_IOC_GETFLAGS` and `FS_IOC_SETFLAGS` read or write inode flag masks; `FS_IOC_FSGETXATTR` and `FS_IOC_FSSETXATTR` use richer XFS-originated project/extent attributes.
4. `preadv2` and `pwritev2` consume `RWF_*` flags per operation.
5. `PAGEMAP_SCAN` walks a userspace address range and emits `page_region` records matching category masks.
6. `PROCMAP_QUERY` provides structured VMA lookup and optional VMA name/build-id extraction from `/proc/<pid>/maps`.

Perf trace uses these definitions to print ioctl names, struct fields where supported, and bitmask names for flags.

## State and Persistence Behavior

Many operations described by this header mutate persistent or semi-persistent state:

- Inode flags, project IDs, extent hints, CoW extent hints, labels, UUIDs, and filesystem attributes can persist on disk depending on the filesystem.
- Freeze/thaw, trim, discard, block readonly state, and tracing controls affect device or filesystem state.
- Dedupe and clone alter extent sharing, while `FICLONERANGE` and `FIDEDUPERANGE` can affect storage layout without changing logical contents.
- `RWF_*` flags are per-I/O and do not persist.
- Pagemap scan and procmap query are read/query interfaces except optional write-protection through `PM_SCAN_WP_MATCHING`.

## Dependencies and Integration Points

The header includes `linux/limits.h`, `linux/ioctl.h`, `linux/types.h`, optionally `linux/fscrypt.h` for userspace, and `linux/mount.h` outside the kernel. It refers to `struct fiemap`, blk trace setup structs, and filesystem-specific semantics provided elsewhere in the kernel source. It integrates with VFS, block layer, procfs, mm, fscrypt, fs-verity, DAX, reflink/dedupe-capable filesystems, and block metadata protection.

In perf, it is a source of ioctl command tables and symbolic masks used while decoding `ioctl`, `preadv2`, `pwritev2`, and procfs ioctl traces.

## Risks

- Some ioctl argument types are historical oddities, such as `size_t` in block ioctls and old 32-bit flag variants. Decoders must preserve ioctl numbers exactly.
- The inode flag space is nearly exhausted and doubles as on-disk encoding for ext filesystems. Renumbering or broadening flags is high risk.
- Flexible array structures require length-aware decoding to avoid reading past captured data.
- `PAGEMAP_SCAN` can both query and write-protect matching pages, so it is not purely observational when `PM_SCAN_WP_MATCHING` is set.
- `procmap_query` has multiple user buffers and in/out sizes; trace output should report addresses and sizes rather than assuming strings/build IDs are available.
- `RWF_SUPPORTED` changes as new flags are added; stale generated tables can miss newer bits such as `RWF_DONTCACHE` or `RWF_NOSIGNAL`.

## Test Signals

Useful validation signals include:

- Compile a beauty decoder using this header and compare ioctl numbers with current kernel UAPI.
- Trace representative ioctls: `FICLONE`, `FIDEDUPERANGE`, `FITRIM`, `FS_IOC_GETFLAGS`, `FS_IOC_FSGETXATTR`, `BLKGETSIZE64`, and `PAGEMAP_SCAN`.
- Unit-check symbolic expansion of `FS_*_FL`, `FS_XFLAG_*`, `RWF_*`, `PAGE_IS_*`, `PM_SCAN_*`, and `PROCMAP_QUERY_*`.
- Validate flexible-array handling for dedupe ranges, pagemap results, and procmap optional output buffers.
- Confirm `RWF_SUPPORTED` includes every defined per-I/O bit in this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/mount.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/mount.h

## Purpose

`mount.h` defines Linux mount, mount-attribute, and mount-query UAPI constants and structs. In perf trace beauty it supports symbolic decoding for legacy `mount(2)` flags, new mount API syscalls such as `open_tree`, `move_mount`, `fsopen`, `fspick`, `fsconfig`, `fsmount`, `mount_setattr`, and newer `statmount`/`listmount` style interfaces.

## Important APIs, Types, and Constants

Important groups include:

- Legacy mount flags: `MS_RDONLY`, `MS_NOSUID`, `MS_NODEV`, `MS_NOEXEC`, `MS_SYNCHRONOUS`, `MS_REMOUNT`, `MS_MANDLOCK`, `MS_DIRSYNC`, `MS_NOSYMFOLLOW`, `MS_NOATIME`, `MS_NODIRATIME`, `MS_BIND`, `MS_MOVE`, `MS_REC`, `MS_SILENT`, propagation flags, `MS_RELATIME`, `MS_STRICTATIME`, and `MS_LAZYTIME`.
- Internal/reserved superblock flags exposed in the numeric namespace: `MS_SUBMOUNT`, `MS_NOREMOTELOCK`, `MS_NOSEC`, `MS_BORN`, `MS_ACTIVE`, `MS_NOUSER`.
- Remount mask and old magic flag: `MS_RMT_MASK`, `MS_MGC_VAL`, and `MS_MGC_MSK`.
- New mount API flags: `OPEN_TREE_*`, `MOVE_MOUNT_*`, `FSOPEN_CLOEXEC`, `FSPICK_*`, `FSMOUNT_CLOEXEC`.
- `enum fsconfig_command` values: set flag/string/binary/path/fd, create, reconfigure, and create-exclusive.
- Mount attribute flags and `struct mount_attr`: `MOUNT_ATTR_RDONLY`, `NOSUID`, `NODEV`, `NOEXEC`, atime mode bits, `IDMAP`, `NOSYMFOLLOW`, plus `attr_set`, `attr_clr`, `propagation`, and `userns_fd`.
- Mount query structs: large `struct statmount` with fixed fields plus string offsets in `str[]`, and `struct mnt_id_req` for selecting mount namespace, mount id, and query/list parameters.
- `STATMOUNT_*` mask bits, `LSMT_ROOT`, `LISTMOUNT_REVERSE`, and `STATMOUNT_BY_FD`.

## Control Flow and Integration

The header is declarative, but it supports distinct syscall flows:

1. Legacy `mount(2)` receives a bitmask of `MS_*` flags and optional filesystem data.
2. `open_tree`, `move_mount`, `fsopen`, `fspick`, `fsconfig`, and `fsmount` break mount creation/reconfiguration into file-descriptor-based steps.
3. `mount_setattr` consumes `struct mount_attr`, where `attr_set` and `attr_clr` select attribute changes and `propagation` changes mount propagation.
4. `statmount` fills a caller-sized `struct statmount`, sets `mask` to supported/written fields, and writes requested strings into the variable buffer.
5. `listmount` uses `struct mnt_id_req` plus `LSMT_ROOT`/last-id parameters to enumerate mount IDs.

Perf trace should key decoding to syscall argument position because `MS_*`, `MOUNT_ATTR_*`, `STATMOUNT_*`, and move/open/fspick flags are separate namespaces.

## State and Persistence Behavior

Mount operations mutate VFS mount namespace state: they create mount trees, move mounts, change propagation, remount attributes, bind or clone trees, and attach idmapped mount state through `userns_fd`. `statmount` and `listmount` are query interfaces and only expose current state. The header itself persists no state.

## Dependencies and Integration Points

The header includes `linux/types.h` and uses `O_CLOEXEC` from the broader fcntl/open flag namespace for `OPEN_TREE_CLOEXEC`. It integrates with VFS mount code, mount namespaces, idmapped mounts, filesystem context creation, `statx`-like mask semantics, and proc mountinfo-compatible old mount IDs.

Perf integration points are syscall flag decoders for `mount`, `umount2`-adjacent code, `open_tree`, `move_mount`, `fsconfig`, `fsmount`, `mount_setattr`, `statmount`, and `listmount`.

## Risks

- Some `MS_*` flags are internal to the kernel but remain in the UAPI numeric space; decoders should display them without implying ordinary userspace should set them.
- `MS_VERBOSE` and `MS_SILENT` share the same value, with `MS_VERBOSE` deprecated. Symbol choice may affect trace readability.
- `MOUNT_ATTR__ATIME` is a mask, while `RELATIME`, `NOATIME`, and `STRICTATIME` are values inside that mask. Treating them as independent booleans can be misleading.
- `statmount` string fields are offsets into a variable buffer; decoders need size-aware handling and should respect `EOVERFLOW` semantics.
- Version macros for `mount_attr` and `mnt_id_req` matter for forward-compatible struct-size handling.

## Test Signals

Useful validation signals include:

- Decode legacy mount flags including propagation and atime variants.
- Decode `move_mount` with separate from-path and to-path flags.
- Decode `fsconfig` command values from `enum fsconfig_command`.
- Decode `mount_setattr` with `attr_set`, `attr_clr`, `propagation`, and idmap fd.
- Validate `statmount` mask names and special `LSMT_ROOT` listmount handling.
- Compile-check references to `OPEN_TREE_CLOEXEC` with the local include ordering used by perf.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/mount.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/prctl.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/prctl.h

## Purpose

`prctl.h` defines the operation numbers and sub-flags for Linux `prctl(2)`, the miscellaneous per-process and per-thread control syscall. In perf trace beauty it enables symbolic decoding of `prctl` options for process naming, signal-on-parent-death, dumpability, capabilities, seccomp, no-new-privileges, memory map changes, architecture vector controls, speculation mitigation, syscall user dispatch, core scheduling, memory deny-write-execute, RISC-V controls, shadow stacks, CFI, and other task attributes.

## Important APIs, Types, and Constants

Key operation groups include:

- Basic task controls: `PR_SET_PDEATHSIG`, `PR_GET_PDEATHSIG`, dumpability, unaligned access, keepcaps, floating-point emulation/exception controls, process timing, task name, endian mode, seccomp, capability bounding set, TSC access, securebits, timerslack, and perf event enable/disable.
- Memory and checkpoint/restore controls: `PR_MCE_KILL`, `PR_SET_MM`, `struct prctl_mm_map`, `PR_SET_PTRACER`, child subreaper, no-new-privs, TID address, THP disable, `PR_SET_VMA`, `PR_GET_AUXV`, memory merge, timer-create restore IDs, futex hash slots, and rseq slice extension.
- Architecture controls: arm64 SVE/SME vector length, pointer authentication keys, tagged address and MTE controls, RISC-V vector state and icache flush context, PowerPC DEXCR, and shadow stack status.
- Security and speculation controls: speculation variants and state bits, syscall user dispatch modes, core scheduling commands/scopes, MDWE flags, and CFI branch landing pad controls.
- Reserved removed APIs: MPX management values remain reserved.

The only struct defined is `struct prctl_mm_map`, which carries mm layout fields and auxiliary vector/exe fd metadata for checkpoint/restore-style `PR_SET_MM` operations.

## Control Flow and Integration

Runtime flow is always through `prctl(option, arg2, arg3, arg4, arg5)`, but argument meaning depends entirely on `option`. Many options are get/set pairs. Some use nested selector values, for example:

1. `PR_SET_MM` uses `arg2` to select a memory-map field or `PR_SET_MM_MAP`, with `struct prctl_mm_map`.
2. `PR_CAP_AMBIENT` uses subcommands such as raise/lower/clear.
3. `PR_GET/SET_SPECULATION_CTRL` use a speculation variant and control bits.
4. `PR_SET_SYSCALL_USER_DISPATCH` uses dispatch mode plus address range and selector pointer.
5. `PR_SCHED_CORE` uses command and scope selectors.
6. Architecture-specific controls use bit masks that may be meaningful only on supported hardware.

Perf trace must decode the first argument first, then select the correct symbolic namespace for later arguments.

## State and Persistence Behavior

Most `prctl` operations mutate current task, thread, process, or mm state:

- Task name, no-new-privs, seccomp, timerslack, dumpability, subreaper, ambient capabilities, speculation controls, syscall dispatch, MDWE, CFI, shadow stack, and architecture vector settings can persist until exec, fork, thread exit, or explicit reset depending on the option.
- Some flags explicitly control inheritance or on-exec behavior, such as SVE/SME vector length inheritance, speculation disable-on-exec, DEXCR on-exec bits, and MDWE no-inherit.
- Get operations and `PR_GET_AUXV` query state.
- `PR_SET_MM` mutates mm metadata visible through `/proc`, mainly for checkpoint/restore.

## Dependencies and Integration Points

The header includes `linux/types.h` and expects bit helpers such as `_BITUL` from the broader kernel headers in some build contexts. It integrates with signal handling, mm, credentials/capabilities, seccomp, perf, scheduler, architecture-specific task state, CRIU/checkpoint-restore, LSM behavior, and hardware mitigation controls.

In perf, it is a decoder input for the `prctl` syscall and sometimes for security/performance investigations where symbolic option names are critical.

## Risks

- `prctl` is highly multiplexed. A flat decoder for args 2-5 will be wrong for many options unless it is option-aware.
- Several constants are architecture-specific or meaningful only on selected configs. Trace output should show names but not assume the call succeeded.
- Some options use magic non-sequential values, such as `PR_SET_PTRACER`, `PR_SET_VMA`, and `PR_GET_AUXV`.
- Removed/reserved MPX values must remain reserved.
- `PR_SET_MM` and `struct prctl_mm_map` include a user pointer field and sensitive mm metadata; decoding should avoid unsafe dereference and should preserve raw addresses.

## Test Signals

Useful validation signals include:

- Decode basic `prctl(PR_SET_NAME, ...)` and `PR_GET_NAME`.
- Decode security options: `PR_SET_NO_NEW_PRIVS`, `PR_SET_SECCOMP`, `PR_CAP_AMBIENT`, `PR_SET_MDWE`, and `PR_SET_CFI`.
- Decode nested masks for speculation controls, tagged address/MTE, SVE/SME, RISC-V vector state, PowerPC DEXCR, and shadow stack.
- Trace `PR_SET_MM` and confirm subcommand names and `prctl_mm_map` size assumptions.
- Confirm unknown option values and unknown bits remain visible numerically.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/sched.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/sched.h

## Purpose

`sched.h` defines Linux task creation and scheduler UAPI constants: clone flags, `clone3` argument layout, scheduler policy values, and `sched_setattr`/`sched_getattr` flags. In perf trace beauty it supports symbolic decoding of `clone`, `clone3`, `unshare`, namespace flags, and scheduler attribute masks.

## Important APIs, Types, and Constants

Important definitions include:

- Clone signal mask: `CSIGNAL`.
- Classic clone flags: `CLONE_VM`, `CLONE_FS`, `CLONE_FILES`, `CLONE_SIGHAND`, `CLONE_PIDFD`, `CLONE_PTRACE`, `CLONE_VFORK`, `CLONE_PARENT`, `CLONE_THREAD`, namespace creation flags, TLS and TID flags, `CLONE_DETACHED`, `CLONE_UNTRACED`, `CLONE_IO`.
- 64-bit `clone3` flags: `CLONE_CLEAR_SIGHAND` and `CLONE_INTO_CGROUP`.
- `CLONE_NEWTIME`, which intersects with `CSIGNAL` and is valid for unshare/clone3-style contexts.
- `struct clone_args`, versioned by size, with aligned fields for flags, pidfd, child/parent TID pointers, exit signal, stack, stack size, TLS, set-TID array, set-TID size, and cgroup fd.
- Struct size versions: `CLONE_ARGS_SIZE_VER0`, `VER1`, and `VER2`.
- Scheduling policies: `SCHED_NORMAL`, `FIFO`, `RR`, `BATCH`, `IDLE`, `DEADLINE`, and `SCHED_EXT`.
- Scheduler flags: `SCHED_RESET_ON_FORK`, `SCHED_FLAG_RESET_ON_FORK`, `RECLAIM`, `DL_OVERRUN`, keep-policy/params, utilization clamp min/max, and aggregate masks.

## Control Flow and Integration

The header is declarative, but its constants participate in several syscall flows:

1. `clone` uses low bits as an exit signal and high bits as clone flags.
2. `clone3` passes `struct clone_args`; `flags` no longer embeds `CSIGNAL`, and `exit_signal` is a separate field.
3. `unshare` uses a subset of clone namespace and sharing flags; `CLONE_NEWTIME` is valid there even though it overlaps `CSIGNAL` in classic clone encoding.
4. `sched_setscheduler` and related calls use `SCHED_*` policy values.
5. `sched_setattr`/`sched_getattr` use `SCHED_FLAG_*` masks to preserve or change policy, reclaim deadline runtime, report deadline overrun, and set utilization clamps.

Perf trace must choose flag decoding based on syscall: classic clone, clone3, and unshare do not have exactly the same interpretation of all bits.

## State and Persistence Behavior

Clone flags create new task state and sharing relationships for VM, filesystem info, file table, signal handlers, thread groups, namespaces, cgroups, TLS, pidfds, and TID-clear/set behavior. Scheduler policies and flags persist as task scheduling state until changed or until reset-on-fork semantics apply. The header itself stores no state.

## Dependencies and Integration Points

The header includes `linux/types.h` for `__aligned_u64`. It integrates with process creation, pidfd, namespaces, cgroups, futex/TID clearing, scheduler classes, deadline scheduling, utilization clamping, and extensible scheduler policy support.

Perf integration points are syscall decoders for `clone`, `clone3`, `unshare`, `setns`-adjacent namespace analysis, `sched_setscheduler`, and `sched_setattr`.

## Risks

- `CLONE_NEWTIME` overlaps with `CSIGNAL`; decoding it as a clone flag in classic `clone` can mislabel the exit signal byte.
- `CLONE_DETACHED` is unused/ignored but still ABI-visible.
- `struct clone_args` is versioned by size; decoders should handle older shorter structs and future longer structs.
- `SCHED_EXT` may not be available or enabled on all kernels even though the value is in the UAPI mirror.
- Aggregate masks such as `SCHED_FLAG_ALL` must be updated when new scheduler flags appear.

## Test Signals

Useful validation signals include:

- Decode classic `clone` with `CLONE_VM|CLONE_THREAD|SIGCHLD` and verify signal bits are separate.
- Decode `clone3` flags plus `exit_signal` from `struct clone_args`.
- Decode `unshare(CLONE_NEWUSER|CLONE_NEWTIME)` correctly.
- Decode scheduler policies including `SCHED_DEADLINE` and `SCHED_EXT`.
- Unit-check `SCHED_FLAG_ALL`, `SCHED_FLAG_KEEP_ALL`, and `SCHED_FLAG_UTIL_CLAMP` expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/stat.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/stat.h

## Purpose

`stat.h` defines Linux file type/mode constants and the extended `statx(2)` ABI. In the perf trace beauty mirror it supports symbolic decoding for stat-like syscall masks, returned attribute masks, file type tests, permission bits, and newer direct-I/O or atomic-write query fields.

## Important APIs, Types, and Constants

Important groups include:

- File type and permission bits exposed when not hidden by a modern glibc include context: `S_IFMT`, `S_IFSOCK`, `S_IFLNK`, `S_IFREG`, `S_IFBLK`, `S_IFDIR`, `S_IFCHR`, `S_IFIFO`, setuid/setgid/sticky bits, `S_IS*` macros, and user/group/other permission masks.
- `struct statx_timestamp`: signed seconds, nanoseconds, and reserved field.
- `struct statx`: fixed 0x100-byte extended status structure with mask, block size, attributes, nlink, uid/gid, mode, inode, size, blocks, attributes mask, atime/btime/ctime/mtime, device ids, mount id, DIO alignment, subvolume id, atomic write limits, read-DIO alignment, and spare space.
- `STATX_*` request/result mask bits: type, mode, nlink, uid, gid, atime, mtime, ctime, ino, size, blocks, basic stats, btime, mount id, DIO alignment, unique mount id, subvolume, write atomic, DIO read alignment, and reserved expansion bit.
- Deprecated userspace `STATX_ALL`.
- `STATX_ATTR_*` file attribute bits: compressed, immutable, append-only, nodump, encrypted, automount, mount root, verity, DAX, and atomic-write support.

## Control Flow and Integration

`statx` callers pass a mask of `STATX_*` bits and path-resolution flags from `fcntl.h`. The kernel returns a `struct statx` and sets `stx_mask` to show which fields are valid. Unsupported fields are cleared or fabricated for compatibility. Some fields may be filled opportunistically even if not requested.

Perf trace uses this header to decode the `mask` argument to `statx` and potentially returned structures if captured. It should treat `STATX_ATTR_*` as values in `stx_attributes` and `stx_attributes_mask`, not as request-mask bits.

## State and Persistence Behavior

The header stores no state. `statx` is a query interface. It may force synchronization of attributes with a remote server when the caller combines statx with `AT_STATX_FORCE_SYNC`, but the `stat.h` masks themselves do not mutate file state.

The returned fields describe persistent file metadata, mount identity, direct I/O constraints, subvolume identity, and atomic-write capabilities at the time of query.

## Dependencies and Integration Points

The header includes `linux/types.h`. It integrates with VFS, individual filesystems, network filesystems, direct I/O, statx path flags from `fcntl.h`, fs-verity, DAX, encryption, automounts, and mount-id reporting.

In perf, the primary integration is symbolic decoding of `statx` masks and file mode/attribute bitmasks.

## Risks

- `stx_mask` reports validity; consumers must not assume a field is supported just because a request bit was set.
- `STATX_ALL` is deprecated and intentionally fixed to its old value; newer fields are outside it.
- `STATX_MNT_ID` and `STATX_MNT_ID_UNIQUE` have different semantics and can be confused if a decoder collapses names.
- Attribute bits and request bits are separate namespaces.
- The `struct statx` spare space is for ABI expansion; decoders should be size-aware and tolerate future fields.

## Test Signals

Useful validation signals include:

- Decode `statx` masks containing `STATX_BASIC_STATS|STATX_BTIME|STATX_DIOALIGN`.
- Decode newer fields `STATX_SUBVOL`, `STATX_WRITE_ATOMIC`, and `STATX_DIO_READ_ALIGN`.
- Verify `STATX_ALL` remains printed as deprecated or secondary rather than hiding newer bits.
- Unit-check file mode and `STATX_ATTR_*` bit expansion.
- Trace statx with `AT_STATX_FORCE_SYNC` and `AT_STATX_DONT_SYNC` to ensure path flags and stat masks are decoded in separate namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/usbdevice_fs.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/usbdevice_fs.h

## Purpose

`usbdevice_fs.h` defines the Linux usbdevfs userspace ABI for controlling USB devices through device files, typically under usbfs/devtmpfs. In perf trace beauty it provides ioctl names, command numbers, transfer structs, URB flags/types, capability bits, and driver/interface management structures for symbolic ioctl decoding.

## Important APIs, Types, and Constants

Important structures include:

- Transfer structs: `usbdevfs_ctrltransfer`, `usbdevfs_bulktransfer`, `usbdevfs_setinterface`, and `usbdevfs_disconnectsignal`.
- Driver and connection info: `usbdevfs_getdriver`, `usbdevfs_connectinfo`, and extensible `usbdevfs_conninfo_ex`.
- URB ABI: `usbdevfs_iso_packet_desc` and flexible-array `usbdevfs_urb`, with type, endpoint, status, flags, buffer pointer, lengths, frame/stream union, error count, completion signal, user context, and isochronous frame descriptors.
- Driver pass-through and hub data: `usbdevfs_ioctl` and `usbdevfs_hub_portinfo`.
- Claim/disconnect and streams: `usbdevfs_disconnect_claim` and `usbdevfs_streams`.

Important constants include:

- URB flags: `USBDEVFS_URB_SHORT_NOT_OK`, `ISO_ASAP`, `BULK_CONTINUATION`, `NO_FSBR`, `ZERO_PACKET`, and `NO_INTERRUPT`.
- URB types: ISO, interrupt, control, and bulk.
- Capability bits: zero packet, bulk continuation, no packet size limit, bulk scatter-gather, reap after disconnect, mmap, drop privileges, extended connection info, and suspend.
- Disconnect-claim flags for matching or excluding a driver name.
- Ioctl commands from `USBDEVFS_CONTROL` through `USBDEVFS_WAIT_FOR_RESUME`, including 32-bit compat forms for some pointer-bearing commands.

## Control Flow and Integration

Typical usbdevfs ioctl flows include:

1. Synchronous control and bulk transfers pass transfer structs with endpoint/request fields, timeout, length, and user data pointer.
2. Asynchronous I/O uses `USBDEVFS_SUBMITURB`, then `USBDEVFS_REAPURB` or nonblocking reap to receive completed URBs.
3. Userspace claims/releases interfaces, sets interfaces/configurations, disconnects or reconnects kernel drivers, and can issue interface-specific driver ioctls.
4. Capability discovery through `USBDEVFS_GET_CAPABILITIES` gates optional features such as mmap, suspend control, and extended connection info.
5. Stream allocation/free uses a flexible endpoint array.

Perf trace primarily decodes ioctl command names and top-level flags. Pointer fields should be reported as addresses unless the tracer has captured pointed data safely.

## State and Persistence Behavior

Operations can mutate USB device/interface state:

- Claimed interfaces, altsettings, configurations, endpoint halt state, reset state, suspend-forbid state, allocated streams, and driver disconnect/claim state can persist until changed, released, or the fd/device closes.
- Submitted URBs are queued kernel state until completed, discarded, or disconnected.
- Dropping usbdevfs privileges can permanently restrict operations on that fd.
- Transfer structs themselves are per-call data.

## Dependencies and Integration Points

The header includes `linux/types.h` and `linux/magic.h`, and relies on ioctl macros from the surrounding UAPI include environment. It refers to USB speed constants from `linux/usb/ch9.h`. It integrates with USB core, usbfs, kernel interface drivers, event/signal delivery, mmap support, and 32-bit compat ioctl handling.

Perf integration points are ioctl decoders for `ioctl(fd, USBDEVFS_*, arg)` and flag decoders for URBs, capabilities, disconnect-claim, and stream commands.

## Risks

- Many structs contain `void __user *` pointers and have 32-bit compat variants. Decoders must avoid assuming native pointer size for traces from compat tasks.
- `usbdevfs_urb` and `usbdevfs_streams` use flexible arrays; lengths must be checked before decoding nested entries.
- `USBDEVFS_CONNINFO_EX(len)` encodes a caller-provided length in the ioctl number, so decoders need to handle variable command values.
- Some flags are not used or are capability-gated; symbolic display does not imply kernel support.
- URB completion is asynchronous; submit success does not mean transfer success.

## Test Signals

Useful validation signals include:

- Decode `USBDEVFS_CONTROL`, `BULK`, `SUBMITURB`, `REAPURB`, `DISCARDURB`, `CLAIMINTERFACE`, `RELEASEINTERFACE`, `GET_CAPABILITIES`, `DISCONNECT_CLAIM`, `ALLOC_STREAMS`, and suspend-control ioctls.
- Verify 32-bit compat ioctl names are distinct where present.
- Unit-check URB flag/type and capability bit expansion.
- Validate variable `USBDEVFS_CONNINFO_EX(len)` decoding for several lengths.
- Trace asynchronous URB submit/reap and confirm usercontext/status fields are not confused with ioctl return status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/usbdevice_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/vhost.h -->
# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/vhost.h

## Purpose

`vhost.h` defines the userspace ioctl ABI for in-kernel virtio accelerators such as vhost-net, vhost-scsi, vhost-vsock, and vhost-vDPA. In perf trace beauty it provides symbolic ioctl names, ioctl numbers, ownership/setup sequencing, vring/eventfd controls, worker controls, backend-specific commands, vDPA management commands, feature arrays, and fork-owner controls.

## Important APIs, Types, and Constants

Important definitions include:

- `VHOST_FILE_UNBIND` for unbinding backend fds.
- Ioctl type `VHOST_VIRTIO` = `0xAF`.
- Feature negotiation: `VHOST_GET_FEATURES`, `VHOST_SET_FEATURES`, `VHOST_GET_FEATURES_ARRAY`, `VHOST_SET_FEATURES_ARRAY`, backend feature get/set.
- Ownership and memory: `VHOST_SET_OWNER`, `VHOST_RESET_OWNER`, `VHOST_SET_MEM_TABLE`, log base/fd controls.
- Worker controls: `VHOST_NEW_WORKER`, `VHOST_FREE_WORKER`, `VHOST_ATTACH_VRING_WORKER`, and `VHOST_GET_VRING_WORKER`.
- Vring setup: set/get vring num, addr, base, endian, kick/call/error eventfds, busyloop timeout.
- Backend-specific controls: `VHOST_NET_SET_BACKEND`, vhost-scsi endpoint and events missed, vhost-vsock guest CID/running, and many vhost-vDPA status/config/vring/group/ASID/suspend/resume/query commands.
- Fork-owner controls: `VHOST_FORK_OWNER_KTHREAD`, `VHOST_FORK_OWNER_TASK`, `VHOST_SET_FORK_FROM_OWNER`, and `VHOST_GET_FORK_FROM_OWNER`.

The struct types used by these ioctls come mostly from `linux/vhost_types.h`, including vhost memory tables, vring state/address/file/worker, vDPA config/ranges, SCSI target, and feature arrays.

## Control Flow and Integration

A typical vhost setup flow is:

1. Open a vhost device fd and call `VHOST_SET_OWNER`; most commands require the current process to own the fd.
2. Negotiate features and backend features.
3. Provide guest memory layout with `VHOST_SET_MEM_TABLE` and optional dirty logging setup.
4. Configure each virtqueue with size, addresses, base index, endian mode for legacy devices, and eventfd fds for kick/call/error.
5. Attach backend resources such as tap/raw socket, SCSI endpoint, vsock guest CID, or vDPA device state.
6. Optionally create extra workers and bind queues to them.
7. For migration or reset, get vring bases, suspend/resume vDPA, unbind backends, and eventually reset owner.

Perf trace uses the ioctl command definitions to print high-level vhost operation names and associated struct names.

## State and Persistence Behavior

Most vhost ioctls mutate kernel device state tied to the vhost fd:

- Ownership is exclusive until reset or close.
- Memory tables, logging base/fd, feature masks, backend fds, vring configuration, eventfd bindings, worker allocation/attachment, vDPA status/config/group mapping, and running/suspended state persist until changed or the fd is closed.
- vDPA suspend explicitly requires the device to preserve state necessary for later resume.
- Workers created by userspace are freed explicitly when unattached or implicitly when the device closes.

## Dependencies and Integration Points

The header includes `linux/vhost_types.h`, `linux/types.h`, and `linux/ioctl.h`. It integrates with virtio, eventfd, tap/raw sockets, SCSI target infrastructure, vsock, vDPA, IOMMU/address-space assignment, dirty-page logging, worker threads, cgroups/namespaces, and kernel config gates such as `CONFIG_VHOST_ENABLE_FORK_OWNER_CONTROL`.

For perf, the key integration point is ioctl decoding for `/dev/vhost-*` and vDPA device fds, especially when diagnosing virtual machine setup, migration, and dataplane performance.

## Risks

- Many commands are order-dependent; decoding a command name does not imply it was valid for the current ownership/setup state.
- Some `_IOW`/`_IOR` annotations reflect ABI transfer direction but command comments may describe read-index/write-result behavior inside a struct.
- Worker controls create kernel execution resources and are constrained by ownership, attachment, namespaces, cgroups, and `RLIMIT_NPROC`.
- vDPA commands preserve migration-critical state. Mis-decoding suspend/resume or vring base/group queries can obscure migration bugs.
- Fork-owner controls are only available with a specific kernel config.
- `VHOST_FILE_UNBIND` is `-1`, so signed fd display matters.

## Test Signals

Useful validation signals include:

- Decode ownership, feature, memory table, log, vring setup, and eventfd ioctls in a vhost-net setup trace.
- Decode backend-specific commands for net, scsi, vsock, and vDPA without conflating their struct types.
- Unit-check endian, worker, busyloop, backend feature, feature-array, suspend/resume, group/ASID, and fork-owner command names.
- Verify `VHOST_FILE_UNBIND` is printed distinctly from ordinary invalid fd errors.
- Trace a minimal QEMU vhost startup and confirm command order is visible: set owner, features, memory table, vrings, eventfds, backend bind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/vhost.h -->
