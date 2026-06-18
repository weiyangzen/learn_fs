# subset-b-009669 Research

Grouped source research for mergerfs low-level filesystem wrappers, branch/path utilities, virtual inode/stat/xattr helpers, per-operation policy holders, and FUSE operation handlers. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getfl.hpp -->
# sources/user-network-fs/mergerfs/src/fs_getfl.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_getfl.hpp` provides a small `fs::getfl` wrapper around the platform `getfl` or related syscall interface. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::getfl`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies are limited to neighboring mergerfs declarations or platform libc/syscall interfaces. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_getfl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_glob.cpp -->
# sources/user-network-fs/mergerfs/src/fs_glob.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_glob.cpp` expands branch/path glob patterns with `glob(3)`, enabling brace and directory-only matching when the platform supports those flags. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::glob(pattern, vector*)`, `glob`, `glob_t`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::glob(pattern, vector*)` calls `glob`, copies returned paths, and frees `glob_t`; glob errors simply leave the vector unchanged.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_glob.hpp", <glob.h>, <cstdint>, <string>, <vector>. Used by configuration/path parsing code that accepts shell-like branch patterns. Risk is silent empty expansion when `glob` fails or platform flags are compiled to zero.

## Risks and Edge Cases

Used by configuration/path parsing code that accepts shell-like branch patterns. Risk is silent empty expansion when `glob` fails or platform flags are compiled to zero.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_glob.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_glob.hpp -->
# sources/user-network-fs/mergerfs/src/fs_glob.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_glob.hpp` contains mergerfs support code for `fs_glob`. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <vector>. Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Risks and Edge Cases

Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_glob.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_has_space.cpp -->
# sources/user-network-fs/mergerfs/src/fs_has_space.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_has_space.cpp` answers whether a branch has enough available bytes for a pending write or move. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::has_space`, `fs::statvfs`, `StatVFS::spaceavail`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::has_space` calls `fs::statvfs`, computes available bytes through `StatVFS::spaceavail`, and compares against the requested size.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_has_space.hpp", "fs_statvfs.hpp", "statvfs_util.hpp", <string>. Feeds create/move policies and ENOSPC decisions. Free-space data can race with concurrent writers.

## Risks and Edge Cases

Feeds create/move policies and ENOSPC decisions. Free-space data can race with concurrent writers.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_has_space.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_has_space.hpp -->
# sources/user-network-fs/mergerfs/src/fs_has_space.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_has_space.hpp` contains mergerfs support code for `fs_has_space`. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", <string>. Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Risks and Edge Cases

Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_has_space.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_info.cpp -->
# sources/user-network-fs/mergerfs/src/fs_info.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_info.cpp` builds a compact `fs::info_t` snapshot for one path or file descriptor. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::info`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::info` combines path classification, stat/statvfs or cached statvfs data, block accounting, readonly checks, and inode metadata into the output struct.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_info.hpp", "fs_info_t.hpp", "fs_path.hpp", "fs_stat.hpp", "fs_statvfs.hpp", "fs_statvfs_cache.hpp", "statvfs_util.hpp", <cstdint>. Used by branch selection, diagnostics, and policy scoring. Risks are stale cached statvfs values and concurrent file changes.

## Risks and Edge Cases

Used by branch selection, diagnostics, and policy scoring. Risks are stale cached statvfs values and concurrent file changes.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_info.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_info.hpp -->
# sources/user-network-fs/mergerfs/src/fs_info.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_info.hpp` declares overloads for collecting `fs::info_t` from a path or file descriptor. The source was read as a complete 31-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::info`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_info_t.hpp", <string>. Used by branch policy and status reporting paths.

## Risks and Edge Cases

Used by branch policy and status reporting paths.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_info.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_info_t.hpp -->
# sources/user-network-fs/mergerfs/src/fs_info_t.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_info_t.hpp` defines `fs::info_t`, the branch/file information record shared by policy and diagnostic code. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `struct fs::info_t`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h". It is pure data with no persistence; layout changes ripple into code consuming filesystem info snapshots.

## Risks and Edge Cases

It is pure data with no persistence; layout changes ripple into code consuming filesystem info snapshots.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_info_t.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_inode.cpp -->
# sources/user-network-fs/mergerfs/src/fs_inode.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_inode.cpp` implements mergerfs virtual inode-number calculation algorithms. The source was read as a complete 404-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `set_algo`, `get_algo`, `calc`, `ReaddirCalc::calc`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`set_algo`, `get_algo`, `calc`, and `ReaddirCalc::calc` select and apply passthrough, path hash, dev+ino hash, and hybrid variants using rapidhash.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_inode.hpp", "rapidhash/rapidhash.h", <atomic>, <sys/stat.h>. Integrated by getattr/readdir/fgetattr so FUSE sees stable inode numbers. Hash32 modes can collide; passthrough can collide across branches.

## Risks and Edge Cases

Integrated by getattr/readdir/fgetattr so FUSE sees stable inode numbers. Hash32 modes can collide; passthrough can collide across branches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_inode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_inode.hpp -->
# sources/user-network-fs/mergerfs/src/fs_inode.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_inode.hpp` declares virtual inode algorithms and helpers. The source was read as a complete 91-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `Algo`, `set_algo`, `get_algo`, `calc`, `stat`, `fuse_statx`, `ReaddirCalc`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fs_path.hpp", "fuse_kernel.h", <cstddef>, <string>, <string_view>, <sys/stat.h>. Integrated with getattr/readdir/fgetattr; tests should cover stable inode identity and collision-prone modes.

## Risks and Edge Cases

Integrated with getattr/readdir/fgetattr; tests should cover stable inode identity and collision-prone modes.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_inode.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ioctl.hpp -->
# sources/user-network-fs/mergerfs/src/fs_ioctl.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_ioctl.hpp` provides a small `fs::ioctl` wrapper around the platform `ioctl` or related syscall interface. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::ioctl`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <sys/ioctl.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_ioctl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_is_rofs.hpp -->
# sources/user-network-fs/mergerfs/src/fs_is_rofs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_is_rofs.hpp` detects read-only branch/filesystem states. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `is_mounted_rofs`, `is_rofs`, `is_rofs_but_not_mounted_ro`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_close.hpp", "fs_mktemp.hpp", "fs_path.hpp", "fs_statvfs.hpp", "fs_unlink.hpp", "statvfs_util.hpp", <fcntl.h>. Used to mark branches readonly after EROFS. Temp-file probing can leave cleanup work if close/unlink fails.

## Risks and Edge Cases

Used to mark branches readonly after EROFS. Temp-file probing can leave cleanup work if close/unlink fails.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_is_rofs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_is_same_file.hpp -->
# sources/user-network-fs/mergerfs/src/fs_is_same_file.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_is_same_file.hpp` compares two paths by device and inode without following final symlinks. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `is_same_file`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <sys/stat.h>, <unistd.h>. Useful for clone/rename safety checks. It races with path replacement like any pathname comparison.

## Risks and Edge Cases

Useful for clone/rename safety checks. It races with path replacement like any pathname comparison.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_is_same_file.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lchmod.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lchmod.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lchmod.hpp` provides symlink-aware chmod behavior with platform fallbacks. The source was read as a complete 94-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lchmod`, `fchmodat(..., AT_SYMLINK_NOFOLLOW)`, `lchmod`, `lchmod_check_on_error`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_lstat.hpp", "to_neg_errno.hpp", <string>, <sys/stat.h>, <fcntl.h>, <sys/stat.h>. Used by chmod and metadata-copy paths. Linux symlink chmod support depends on kernel/filesystem behavior.

## Risks and Edge Cases

Used by chmod and metadata-copy paths. Linux symlink chmod support depends on kernel/filesystem behavior.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lchmod.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lchown.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lchown.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lchown.hpp` provides symlink-aware ownership changes and verification helper. The source was read as a complete 97-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lchown`, `::lchown`, `struct stat`, `lchown_check_on_error`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_lstat.hpp", "to_neg_errno.hpp", <unistd.h>. Used by create-as and chown flows. Verification handles benign errors but can race with concurrent ownership changes.

## Risks and Edge Cases

Used by create-as and chown flows. Verification handles benign errors but can race with concurrent ownership changes.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lchown.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lgetxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lgetxattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lgetxattr.hpp` provides a small `fs::lgetxattr` wrapper around the platform `lgetxattr` or related syscall interface. The source was read as a complete 80-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::lgetxattr`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "xattr.hpp", <string>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lgetxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_link.hpp -->
# sources/user-network-fs/mergerfs/src/fs_link.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_link.hpp` provides a small `fs::link` wrapper around the platform `link` or related syscall interface. The source was read as a complete 43-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::link`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_link.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_llistxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_llistxattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_llistxattr.hpp` provides a small `fs::llistxattr` wrapper around the platform `llistxattr` or related syscall interface. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::llistxattr`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "xattr.hpp", <string>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_llistxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lremovexattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lremovexattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lremovexattr.hpp` provides a small `fs::lremovexattr` wrapper around the platform `lremovexattr` or related syscall interface. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::lremovexattr`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "xattr.hpp", <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lremovexattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lseek.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lseek.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lseek.hpp` provides a small `fs::lseek` wrapper around the platform `lseek` or related syscall interface. The source was read as a complete 42-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::lseek`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <sys/types.h>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lseek.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lsetxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lsetxattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lsetxattr.hpp` provides a small `fs::lsetxattr` wrapper around the platform `lsetxattr` or related syscall interface. The source was read as a complete 70-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::lsetxattr`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "xattr.hpp", <string>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lsetxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lstat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lstat.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lstat.hpp` provides a small `fs::lstat` wrapper around the platform `lstat` or related syscall interface. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::lstat`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <sys/stat.h>, <sys/types.h>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lstat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lstatvfs.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lstatvfs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lstatvfs.hpp` approximates statvfs without following a final symlink. The source was read as a complete 55-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lstatvfs`, `O_NOFOLLOW|O_PATH`, `fstatvfs`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "errno.hpp", "fs_close.hpp", "fs_open.hpp", "fs_fstatvfs.hpp", <cstdint>, <string>. Used when mount/filesystem data is needed for symlink paths. `O_PATH` portability is guarded by fallback defines.

## Risks and Edge Cases

Used when mount/filesystem data is needed for symlink paths. `O_PATH` portability is guarded by fallback defines.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lstatvfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lutimens.hpp -->
# sources/user-network-fs/mergerfs/src/fs_lutimens.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_lutimens.hpp` updates symlink timestamps using the project utimensat abstraction. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `lutimens`, `fs::utimensat(..., AT_SYMLINK_NOFOLLOW)`, `struct stat`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_utimensat.hpp", "fs_stat_utils.hpp". Used by metadata preservation and utimens FUSE paths. Platform timestamp support varies.

## Risks and Edge Cases

Used by metadata preservation and utimens FUSE paths. Platform timestamp support varies.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_lutimens.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mkdir.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mkdir.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mkdir.hpp` provides a small `fs::mkdir` wrapper around the platform `mkdir` or related syscall interface. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mkdir`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "fs_path.hpp", <string>, <sys/stat.h>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mkdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mkdir_as.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mkdir_as.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mkdir_as.hpp` creates or opens filesystem objects as a requested uid/gid for FUSE request ownership semantics. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mkdir_as`, `fs::mkdir`, `lchown`, `fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_mkdir.hpp", "ugid.hpp", "fs_lchown.hpp". Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Risks and Edge Cases

Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mkdir_as.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mkdirat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mkdirat.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mkdirat.hpp` provides a small `fs::mkdirat` wrapper around the platform `mkdirat` or related syscall interface. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mkdirat`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "fs_path.hpp", <fcntl.h>, <sys/stat.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mkdirat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mknod.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mknod.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mknod.hpp` provides a small `fs::mknod` wrapper around the platform `mknod` or related syscall interface. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mknod`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <fcntl.h>, <sys/stat.h>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mknod.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mknod_as.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mknod_as.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mknod_as.hpp` creates or opens filesystem objects as a requested uid/gid for FUSE request ownership semantics. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mknod_as`, `fs::mknod`, `lchown`, `fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_mknod.hpp", "ugid.hpp", "fs_lchown.hpp". Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Risks and Edge Cases

Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mknod_as.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mktemp.cpp -->
# sources/user-network-fs/mergerfs/src/fs_mktemp.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mktemp.cpp` creates hidden temporary files beside a target path. The source was read as a complete 101-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `mktemp_in_dir`, `.name_random`, `_PC_NAME_MAX`, `O_CREAT|O_EXCL`, `EEXIST`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`mktemp_in_dir` generates `.name_random` candidates bounded by `_PC_NAME_MAX`, opens with `O_CREAT|O_EXCL`, retries on `EEXIST`, and returns fd plus path.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_mktemp.hpp", "errno.hpp", "fs_open.hpp", "fs_path.hpp", "rnd.hpp", <limits.h>, <unistd.h>, <algorithm>. Used by write/copy/replace flows needing same-directory temp files. Risks are random collision after limited retries and filename truncation.

## Risks and Edge Cases

Used by write/copy/replace flows needing same-directory temp files. Risks are random collision after limited retries and filename truncation.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mktemp.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mktemp.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mktemp.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mktemp.hpp` declares temporary-file helpers returning both fd and generated path. The source was read as a complete 37-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `mktemp_in_dir`, `mktemp`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_path.hpp", <string>, <tuple>. Used where operations need hidden same-directory temp files for replacement/copy flows.

## Risks and Edge Cases

Used where operations need hidden same-directory temp files for replacement/copy flows.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mktemp.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mount.cpp -->
# sources/user-network-fs/mergerfs/src/fs_mount.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mount.cpp` mounts a target by invoking the system `mount` helper. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mount(target)`, `mount <target>`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::mount(target)` builds a subprocess command equivalent to `mount <target>` and returns the subprocess result.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_mount.hpp", "subprocess/subprocess.hpp". Used by mount-wait startup logic. It depends on system mount configuration and helper permissions.

## Risks and Edge Cases

Used by mount-wait startup logic. It depends on system mount configuration and helper permissions.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mount.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mount.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mount.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mount.hpp` contains mergerfs support code for `fs_mount`. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>. Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Risks and Edge Cases

Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mount.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mounts.cpp -->
# sources/user-network-fs/mergerfs/src/fs_mounts.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mounts.cpp` collects currently mounted filesystems. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::mounts`, `/proc/mounts`, `setmntent/getmntent`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::mounts` reads `/proc/mounts` with `setmntent/getmntent` on Linux and is an empty stub elsewhere.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_mounts.hpp", <cstdio>, <mntent.h>. Supports mount discovery/diagnostics. Non-Linux builds receive no mount data from this file.

## Risks and Edge Cases

Supports mount discovery/diagnostics. Non-Linux builds receive no mount data from this file.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mounts.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mounts.hpp -->
# sources/user-network-fs/mergerfs/src/fs_mounts.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_mounts.hpp` declares mount table data structures and the mount enumeration API. The source was read as a complete 39-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::Mount`, `MountVec`, `mounts()`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_path.hpp", <vector>. Consumed by mount/branch diagnostics and platform discovery code.

## Risks and Edge Cases

Consumed by mount/branch diagnostics and platform discovery code.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_mounts.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_movefile_and_open.cpp -->
# sources/user-network-fs/mergerfs/src/fs_movefile_and_open.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_movefile_and_open.cpp` moves a file from one branch to another and reopens it on the destination branch. The source was read as a complete 148-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `movefile_and_open`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`movefile_and_open` selects a destination branch, checks original flags and size, verifies free space, clones parent directories, copies, reopens without create/truncate/excl bits, and unlinks the source.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_movefile_and_open.hpp", "base_types.h", "errno.hpp", "fs_clonepath.hpp", "fs_close.hpp", "fs_copyfile.hpp", "fs_file_size.hpp", "fs_findonfs.hpp". Used when write operations need to rebalance or satisfy policy. Copy/open/unlink is not atomic across filesystems; several failures normalize to `-ENOSPC`.

## Risks and Edge Cases

Used when write operations need to rebalance or satisfy policy. Copy/open/unlink is not atomic across filesystems; several failures normalize to `-ENOSPC`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_movefile_and_open.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_movefile_and_open.hpp -->
# sources/user-network-fs/mergerfs/src/fs_movefile_and_open.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_movefile_and_open.hpp` declares APIs that move a backing file between branches and reopen it. The source was read as a complete 43-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "branches.hpp", "fs_path.hpp", "policy.hpp", <string>. Integrated with write policy enforcement and file migration flows.

## Risks and Edge Cases

Integrated with write policy enforcement and file migration flows.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_movefile_and_open.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open.hpp -->
# sources/user-network-fs/mergerfs/src/fs_open.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_open.hpp` provides a small `fs::open` wrapper around the platform `open` or related syscall interface. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::open`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <fcntl.h>, <sys/stat.h>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open_as.hpp -->
# sources/user-network-fs/mergerfs/src/fs_open_as.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_open_as.hpp` creates or opens filesystem objects as a requested uid/gid for FUSE request ownership semantics. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::open_as`, `fs::open`, `lchown`, `fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_open.hpp", "ugid.hpp", "fs_fchown.hpp". Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Risks and Edge Cases

Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open_as.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open_fd.cpp -->
# sources/user-network-fs/mergerfs/src/fs_open_fd.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_open_fd.cpp` reopens an existing file descriptor as a new descriptor with requested flags. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::open_fd`, `/proc/self/fd/<fd>`, `O_EMPTY_PATH`, `O_NOFOLLOW`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::open_fd` opens `/proc/self/fd/<fd>` on Linux or uses `O_EMPTY_PATH` on FreeBSD, clearing `O_NOFOLLOW`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_open_fd.hpp", "fmt/core.h", "fs_openat.hpp", "fatal.hpp", "procfs.hpp", "fs_openat.hpp". Used for pathless fd reopening with modified flags. Linux depends on procfs initialization.

## Risks and Edge Cases

Used for pathless fd reopening with modified flags. Linux depends on procfs initialization.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open_fd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open_fd.hpp -->
# sources/user-network-fs/mergerfs/src/fs_open_fd.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_open_fd.hpp` contains mergerfs support code for `fs_open_fd`. The source was read as a complete 24-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies are limited to neighboring mergerfs declarations or platform libc/syscall interfaces. Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Risks and Edge Cases

Risks and tests follow the surrounding mergerfs FUSE operation conventions.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_open_fd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_openat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_openat.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_openat.hpp` provides a small `fs::openat` wrapper around the platform `openat` or related syscall interface. The source was read as a complete 74-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::openat`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_path.hpp", "to_neg_errno.hpp", <string>, <fcntl.h>, <sys/stat.h>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_openat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_opendir.hpp -->
# sources/user-network-fs/mergerfs/src/fs_opendir.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_opendir.hpp` provides a small `fs::opendir` wrapper around the platform `opendir` or related syscall interface. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::opendir`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <dirent.h>, <sys/types.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_opendir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_path.cpp -->
# sources/user-network-fs/mergerfs/src/fs_path.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_path.cpp` provides the implementation unit for the `fs::path` alias. The source was read as a complete 19-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs_path.hpp`, `std::filesystem::path`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

The file includes `fs_path.hpp`; behavior lives in `std::filesystem::path` via the alias.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_path.hpp". Keeps build targets that expect a path translation unit satisfied.

## Risks and Edge Cases

Keeps build targets that expect a path translation unit satisfied.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_path.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_path.hpp -->
# sources/user-network-fs/mergerfs/src/fs_path.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_path.hpp` centralizes mergerfs path type usage. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::path`, `std::filesystem::path`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <filesystem>. Changing this alias affects nearly every path-manipulating operation.

## Risks and Edge Cases

Changing this alias affects nearly every path-manipulating operation.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_path.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_pread.hpp -->
# sources/user-network-fs/mergerfs/src/fs_pread.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_pread.hpp` provides a small `fs::pread` wrapper around the platform `pread` or related syscall interface. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::pread`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "to_neg_errno.hpp", <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_pread.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_preadn.hpp -->
# sources/user-network-fs/mergerfs/src/fs_preadn.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_preadn.hpp` provides a read-exactly loop around positioned reads. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `preadn`, `EINTR`, `EAGAIN`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_pread.hpp". Used by copy/IO helpers needing full buffers. EOF and partial-error semantics must be tested.

## Risks and Edge Cases

Used by copy/IO helpers needing full buffers. EOF and partial-error semantics must be tested.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_preadn.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_pwrite.hpp -->
# sources/user-network-fs/mergerfs/src/fs_pwrite.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_pwrite.hpp` provides a small `fs::pwrite` wrapper around the platform `pwrite` or related syscall interface. The source was read as a complete 42-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::pwrite`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_pwrite.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_pwriten.hpp -->
# sources/user-network-fs/mergerfs/src/fs_pwriten.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_pwriten.hpp` provides a write-exactly loop around positioned writes. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `pwriten`, `err`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_pwrite.hpp". Used by copy/IO helpers needing full writes. Partial write and ENOSPC behavior are key risks.

## Risks and Edge Cases

Used by copy/IO helpers needing full writes. Partial write and ENOSPC behavior are key risks.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_pwriten.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_read.hpp -->
# sources/user-network-fs/mergerfs/src/fs_read.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_read.hpp` provides a small `fs::read` wrapper around the platform `read` or related syscall interface. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::read`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_read.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readahead.cpp -->
# sources/user-network-fs/mergerfs/src/fs_readahead.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_readahead.cpp` sets block-device readahead for a device or path. The source was read as a complete 87-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `readahead`, `/sys/class/bdi/<major>:<minor>/read_ahead_kb`, `st_dev`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`readahead` derives `/sys/class/bdi/<major>:<minor>/read_ahead_kb`, writes the requested size, or stats a path to derive `st_dev`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_readahead.hpp", "fmt/core.h", "fs_lstat.hpp", <fstream>, <string>. Called during FUSE init for mountpoint and branches. It returns success even when sysfs open/write does not happen.

## Risks and Edge Cases

Called during FUSE init for mountpoint and branches. It returns success even when sysfs open/write does not happen.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readahead.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readahead.hpp -->
# sources/user-network-fs/mergerfs/src/fs_readahead.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_readahead.hpp` declares readahead setters by major/minor, device id, or path. The source was read as a complete 40-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", <string>. Used during FUSE init for mountpoint and branch tuning.

## Risks and Edge Cases

Used during FUSE init for mountpoint and branch tuning.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readahead.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readdir.hpp -->
# sources/user-network-fs/mergerfs/src/fs_readdir.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_readdir.hpp` provides a small `fs::readdir` wrapper around the platform `readdir` or related syscall interface. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::readdir`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <dirent.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readlink.hpp -->
# sources/user-network-fs/mergerfs/src/fs_readlink.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_readlink.hpp` provides a small `fs::readlink` wrapper around the platform `readlink` or related syscall interface. The source was read as a complete 43-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::readlink`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_readlink.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_realpath.hpp -->
# sources/user-network-fs/mergerfs/src/fs_realpath.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_realpath.hpp` provides a small `fs::realpath` wrapper around the platform `realpath` or related syscall interface. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::realpath`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <limits.h>, <stdlib.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_realpath.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_realpathize.cpp -->
# sources/user-network-fs/mergerfs/src/fs_realpathize.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_realpathize.cpp` canonicalizes a vector of path strings in place. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::realpathize`, `fs::realpath`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::realpathize` calls `fs::realpath` for each entry and replaces only entries that resolve successfully.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_realpathize.hpp", "fs_realpath.hpp", <string>, <vector>. Used by branch/config normalization. Failed resolution leaves original paths intact.

## Risks and Edge Cases

Used by branch/config normalization. Failed resolution leaves original paths intact.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_realpathize.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_realpathize.hpp -->
# sources/user-network-fs/mergerfs/src/fs_realpathize.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_realpathize.hpp` declares vector in-place canonicalization for path strings. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `std::vector<std::string>`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <vector>. Used in path normalization after glob/config parsing.

## Risks and Edge Cases

Used in path normalization after glob/config parsing.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_realpathize.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_remove.hpp -->
# sources/user-network-fs/mergerfs/src/fs_remove.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_remove.hpp` provides a small `fs::remove` wrapper around the platform `remove` or related syscall interface. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::remove`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <stdio.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_remove.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_rename.hpp -->
# sources/user-network-fs/mergerfs/src/fs_rename.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_rename.hpp` provides a small `fs::rename` wrapper around the platform `rename` or related syscall interface. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::rename`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <stdio.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_rename.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_rmdir.hpp -->
# sources/user-network-fs/mergerfs/src/fs_rmdir.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_rmdir.hpp` provides a small `fs::rmdir` wrapper around the platform `rmdir` or related syscall interface. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::rmdir`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_rmdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_sendfile.cpp -->
# sources/user-network-fs/mergerfs/src/fs_sendfile.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_sendfile.cpp` selects the platform sendfile implementation at compile time. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

Includes the Linux implementation on Linux and an unsupported implementation elsewhere.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_sendfile_linux.icpp", "fs_sendfile_unsupported.icpp". Provides backend transfer support; behavior depends on the included `.icpp`.

## Risks and Edge Cases

Provides backend transfer support; behavior depends on the included `.icpp`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_sendfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_sendfile.hpp -->
# sources/user-network-fs/mergerfs/src/fs_sendfile.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_sendfile.hpp` declares the project sendfile wrapper signature. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <sys/types.h>. Integrated with copy/data-transfer helpers.

## Risks and Edge Cases

Integrated with copy/data-transfer helpers.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_sendfile.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_setfl.cpp -->
# sources/user-network-fs/mergerfs/src/fs_setfl.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_setfl.cpp` sets file status flags on an open descriptor. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::setfl`, `F_SETFL`, `fs_setfl.hpp`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::setfl` uses the project fcntl wrapper to apply `F_SETFL` semantics declared by `fs_setfl.hpp`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_setfl.hpp", "fs_fcntl.hpp". Used when open/write paths adjust descriptor flags. Risks mirror `fcntl` support and flag validity.

## Risks and Edge Cases

Used when open/write paths adjust descriptor flags. Risks mirror `fcntl` support and flag validity.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_setfl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_setfl.hpp -->
# sources/user-network-fs/mergerfs/src/fs_setfl.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_setfl.hpp` declares file status flag setting. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::setfl(fd, flags)`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <fcntl.h>. Used by descriptor mode adjustment code.

## Risks and Edge Cases

Used by descriptor mode adjustment code.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_setfl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_stat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_stat.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_stat.hpp` provides a small `fs::stat` wrapper around the platform `stat` or related syscall interface. The source was read as a complete 53-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::stat`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <sys/stat.h>, <sys/types.h>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_stat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_stat_utils.hpp -->
# sources/user-network-fs/mergerfs/src/fs_stat_utils.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_stat_utils.hpp` provides portable helpers for reading and writing stat timestamp fields. The source was read as a complete 79-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `st_atim/st_mtim`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <sys/stat.h>, <sys/types.h>, <unistd.h>. Important for timestamp code portability; wrong field selection breaks utimens behavior.

## Risks and Edge Cases

Important for timestamp code portability; wrong field selection breaks utimens behavior.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_stat_utils.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statvfs.hpp -->
# sources/user-network-fs/mergerfs/src/fs_statvfs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_statvfs.hpp` provides a small `fs::statvfs` wrapper around the platform `statvfs` or related syscall interface. The source was read as a complete 51-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::statvfs`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <sys/statvfs.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statvfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statvfs_cache.cpp -->
# sources/user-network-fs/mergerfs/src/fs_statvfs_cache.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_statvfs_cache.cpp` provides a process-global timeout-based statvfs cache. The source was read as a complete 148-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `statvfs_cache`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`statvfs_cache` delegates directly when timeout is zero; otherwise a shared mutex allows concurrent reads and unique locked refreshes by path.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_statvfs_cache.hpp", "fs_statvfs.hpp", "statvfs_util.hpp", <mutex>, <shared_mutex>, <string>, <unordered_map>, <sys/statvfs.h>. Used by free-space and readonly checks. Staleness can affect branch selection; cache state is process-local.

## Risks and Edge Cases

Used by free-space and readonly checks. Staleness can affect branch selection; cache state is process-local.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statvfs_cache.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statvfs_cache.hpp -->
# sources/user-network-fs/mergerfs/src/fs_statvfs_cache.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_statvfs_cache.hpp` declares global statvfs cache controls and helpers. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", <sys/statvfs.h>, <string>. Used by branch scoring and space checks; timeout setting is process-global.

## Risks and Edge Cases

Used by branch scoring and space checks; timeout setting is process-global.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statvfs_cache.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statx.hpp -->
# sources/user-network-fs/mergerfs/src/fs_statx.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_statx.hpp` wraps Linux `statx` when build support is available. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::statx`, `fuse_statx`, `struct statx`, `MERGERFS_SUPPORTED_STATX`, `-ENOSYS`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", "fuse_kernel.h", <string>, <fcntl.h>, <sys/stat.h>, "supported_statx.hpp". Used by richer getattr paths. ABI compatibility between `fuse_statx` and `struct statx` is critical.

## Risks and Edge Cases

Used by richer getattr paths. ABI compatibility between `fuse_statx` and `struct statx` is critical.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_statx.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_symlink.hpp -->
# sources/user-network-fs/mergerfs/src/fs_symlink.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_symlink.hpp` provides a small `fs::symlink` wrapper around the platform `symlink` or related syscall interface. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::symlink`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_symlink.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_symlink_as.hpp -->
# sources/user-network-fs/mergerfs/src/fs_symlink_as.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_symlink_as.hpp` creates or opens filesystem objects as a requested uid/gid for FUSE request ownership semantics. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::symlink_as`, `fs::symlink`, `lchown`, `fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_symlink.hpp", "ugid.hpp", "fs_lchown.hpp". Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Risks and Edge Cases

Used by create, mkdir, mknod, and symlink handlers. Failure after creation can leave an object created but ownership adjustment failed.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_symlink_as.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_truncate.hpp -->
# sources/user-network-fs/mergerfs/src/fs_truncate.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_truncate.hpp` provides a small `fs::truncate` wrapper around the platform `truncate` or related syscall interface. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::truncate`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <sys/types.h>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_truncate.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_umount2.hpp -->
# sources/user-network-fs/mergerfs/src/fs_umount2.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_umount2.hpp` provides a small `fs::umount2` wrapper around the platform `umount2` or related syscall interface. The source was read as a complete 58-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::umount2`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "errno.hpp", "to_neg_errno.hpp", <string>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_umount2.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_unlink.hpp -->
# sources/user-network-fs/mergerfs/src/fs_unlink.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_unlink.hpp` provides a small `fs::unlink` wrapper around the platform `unlink` or related syscall interface. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::unlink`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_unlink.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat.hpp -->
# sources/user-network-fs/mergerfs/src/fs_utimensat.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_utimensat.hpp` selects the platform utimensat implementation header. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_utimensat_linux.hpp", "fs_utimensat_freebsd.hpp", "fs_utimensat_generic.hpp". Central portability entry point for timestamp updates.

## Risks and Edge Cases

Central portability entry point for timestamp updates.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat_freebsd.hpp -->
# sources/user-network-fs/mergerfs/src/fs_utimensat_freebsd.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_utimensat_freebsd.hpp` wraps FreeBSD `utimensat` with negative errno normalization. The source was read as a complete 56-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::utimensat`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <fcntl.h>, <sys/stat.h>. Used by lutimens/futimens abstractions on FreeBSD.

## Risks and Edge Cases

Used by lutimens/futimens abstractions on FreeBSD.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat_freebsd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat_generic.hpp -->
# sources/user-network-fs/mergerfs/src/fs_utimensat_generic.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_utimensat_generic.hpp` implements a generic utimensat/futimens fallback using older timeval APIs. The source was read as a complete 294-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `UTIME_NOW`, `UTIME_OMIT`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

Validates flags and timespec values, handles `UTIME_NOW`/`UTIME_OMIT`, reads current timestamps when needed, and delegates through fstatat/futimesat/lutimens helpers.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_fstat.hpp", "fs_fstatat.hpp", "fs_futimesat.hpp", "fs_lutimens.hpp", "fs_stat_utils.hpp", <string>, <fcntl.h>, <sys/stat.h>. High-risk portability code: subtle conversion bugs can change timestamps unexpectedly.

## Risks and Edge Cases

High-risk portability code: subtle conversion bugs can change timestamps unexpectedly.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat_generic.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat_linux.hpp -->
# sources/user-network-fs/mergerfs/src/fs_utimensat_linux.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_utimensat_linux.hpp` wraps Linux `utimensat` with negative errno normalization. The source was read as a complete 56-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::utimensat`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <string>, <fcntl.h>, <sys/stat.h>. Used by lutimens/futimens abstractions on Linux.

## Risks and Edge Cases

Used by lutimens/futimens abstractions on Linux.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_utimensat_linux.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_wait_for_mount.cpp -->
# sources/user-network-fs/mergerfs/src/fs_wait_for_mount.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_wait_for_mount.cpp` waits for branch paths to become mounted and optionally triggers mounts. The source was read as a complete 171-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `wait_for_mount`, `fs::mount`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`wait_for_mount` detects marker xattrs/files or device-number changes, calls `fs::mount` for unready targets, polls until timeout, and logs readiness.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_wait_for_mount.hpp", "syslog.hpp", "fs_mount.hpp", "fs_exists.hpp", "fs_lgetxattr.hpp", "fs_lstat.hpp", "fs_stat.hpp", <functional>. Used during startup for branch readiness. Marker semantics and timeout tuning are operational risks.

## Risks and Edge Cases

Used during startup for branch readiness. Marker semantics and timeout tuning are operational risks.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_wait_for_mount.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_wait_for_mount.hpp -->
# sources/user-network-fs/mergerfs/src/fs_wait_for_mount.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_wait_for_mount.hpp` declares startup mount-wait orchestration. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fs_path.hpp", <chrono>, <vector>. Used by startup code that needs branches ready before serving requests.

## Risks and Edge Cases

Used by startup code that needs branches ready before serving requests.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_wait_for_mount.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_write.hpp -->
# sources/user-network-fs/mergerfs/src/fs_write.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_write.hpp` provides a small `fs::write` wrapper around the platform `write` or related syscall interface. The source was read as a complete 41-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::write`, `to_neg_errno`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "to_neg_errno.hpp", <unistd.h>. Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Risks and Edge Cases

Integrated by FUSE handlers and higher-level fs helpers. Pay attention to negative-errno conversion, symlink-following behavior, and platform ifdefs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_write.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_xattr.cpp -->
# sources/user-network-fs/mergerfs/src/fs_xattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_xattr.cpp` implements higher-level extended-attribute list/get/set/copy helpers. The source was read as a complete 361-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fs::xattr::*`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`fs::xattr::*` uses size-probe retry loops, converts NUL-separated attr lists to vector/string/map forms, sets maps one attr at a time, and copies attrs between fds or paths.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fs_xattr.hpp", "errno.hpp", "fs_close.hpp", "fs_fgetxattr.hpp", "fs_flistxattr.hpp", "fs_fsetxattr.hpp", "fs_lgetxattr.hpp", "fs_llistxattr.hpp". Shared by FUSE xattr operations and metadata-copy flows. Xattr changes between probe and read can force retries or partial copies.

## Risks and Edge Cases

Shared by FUSE xattr operations and metadata-copy flows. Xattr changes between probe and read can force retries or partial copies.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_xattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_xattr.hpp -->
# sources/user-network-fs/mergerfs/src/fs_xattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fs_xattr.hpp` declares high-level xattr list/get/set/copy overloads. The source was read as a complete 82-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include the small project-namespaced API described by the file name. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include <string>, <vector>, <map>. Shared by metadata copy and FUSE xattr handlers.

## Risks and Edge Cases

Shared by metadata copy and FUSE xattr handlers.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fs_xattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/func.cpp -->
# sources/user-network-fs/mergerfs/src/func.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/func.cpp` parses configured policy names for FUSE operation policy slots. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `Func::Base::{Action,Create,Search}::from_string`, `to_string`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`Func::Base::{Action,Create,Search}::from_string` looks up a policy implementation and `to_string` returns the selected policy name.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "func.hpp". Integrated by config parsing. Unknown policy names return `-EINVAL`.

## Risks and Edge Cases

Integrated by config parsing. Unknown policy names return `-EINVAL`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/func.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/func.hpp -->
# sources/user-network-fs/mergerfs/src/func.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/func.hpp` defines configurable per-operation policy holder classes. The source was read as a complete 184-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `ToFromString`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "policy.hpp", "policies.hpp", "tofrom_string.hpp", <string>. It is the bridge between textual config and runtime `Policy::*` callables.

## Risks and Edge Cases

It is the bridge between textual config and runtime `Policy::*` callables.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/func.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/funcs.hpp -->
# sources/user-network-fs/mergerfs/src/funcs.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/funcs.hpp` aggregates all configured FUSE operation policies. The source was read as a complete 46-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `Funcs`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "func.hpp". Stored in global config and consulted by FUSE handlers.

## Risks and Edge Cases

Stored in global config and consulted by FUSE handlers.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/funcs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_access.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_access.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_access.cpp` implements FUSE `access` by checking the branch selected by access policy. The source was read as a complete 66-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::access`, `fs::eaccess`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::access` searches policy branches for the path and calls `fs::eaccess` on the selected backing path.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_access.hpp", "config.hpp", "errno.hpp", "fs_eaccess.hpp", "fs_path.hpp", <string>, <vector>. Depends on configured access/search policy and branch permissions; races with chmod/unlink are normal filesystem races.

## Risks and Edge Cases

Depends on configured access/search policy and branch permissions; races with chmod/unlink are normal filesystem races.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_access.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_access.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_access.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_access.hpp` declares the FUSE `access` operation entry point. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `access`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_access.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_bmap.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_bmap.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_bmap.cpp` declares bmap unsupported for mergerfs. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::bmap`, `-ENOSYS`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::bmap` ignores request fields and returns `-ENOSYS`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_bmap.hpp", "errno.hpp". Signals to callers that physical block mapping is unavailable for pooled files.

## Risks and Edge Cases

Signals to callers that physical block mapping is unavailable for pooled files.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_bmap.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_bmap.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_bmap.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_bmap.hpp` declares the FUSE `bmap` operation entry point. The source was read as a complete 34-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `bmap`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse_req_ctx.h", <cstddef>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_bmap.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chmod.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_chmod.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_chmod.cpp` applies chmod across policy-selected branch instances of a pooled path. The source was read as a complete 118-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::chmod`, `fs::lchmod`, `PolicyRV`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::chmod` runs `fs::lchmod` for each action branch, records successes/errors in `PolicyRV`, and reports the error relevant to the active getattr branch after partial success.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_chmod.hpp", "config.hpp", "errno.hpp", "fs_lchmod.hpp", "fs_path.hpp", "policy_rv.hpp", "fuse.h", <cstring>. Partial success can leave branch metadata divergent.

## Risks and Edge Cases

Partial success can leave branch metadata divergent.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chmod.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chmod.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_chmod.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_chmod.hpp` declares the FUSE `chmod` operation entry point. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `chmod`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h", <sys/stat.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chmod.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chown.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_chown.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_chown.cpp` applies owner/group changes across policy-selected branch instances. The source was read as a complete 115-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::chown`, `fs::lchown`, `PolicyRV`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::chown` runs `fs::lchown` on each action branch and uses `PolicyRV` to collapse partial errors relative to the active branch.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_chown.hpp", "config.hpp", "errno.hpp", "fs_lchown.hpp", "fs_path.hpp", "policy_rv.hpp", "fuse.h", <string>. Branch divergence is possible when only some underlying files accept chown.

## Risks and Edge Cases

Branch divergence is possible when only some underlying files accept chown.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chown.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chown.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_chown.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_chown.hpp` declares the FUSE `chown` operation entry point. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `chown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h", <unistd.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_chown.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_copy_file_range.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_copy_file_range.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_copy_file_range.cpp` implements FUSE `copy_file_range` for two open mergerfs file handles. The source was read as a complete 78-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::copy_file_range`, `FileInfo`, `fs::copy_file_range`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::copy_file_range` resolves source and destination `FileInfo` objects from state and delegates to `fs::copy_file_range` with explicit offsets.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_copy_file_range.hpp", "errno.hpp", "fileinfo.hpp", "fs_copy_file_range.hpp", "state.hpp", "fuse.h", <stdio.h>. Requires both handles to be valid and opened on backing files. Cross-branch/kernel copy semantics determine performance and errors.

## Risks and Edge Cases

Requires both handles to be valid and opened on backing files. Cross-branch/kernel copy semantics determine performance and errors.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_copy_file_range.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_copy_file_range.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_copy_file_range.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_copy_file_range.hpp` declares the FUSE `copy_file_range` operation entry point. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `copy_file_range`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h", "fuse.h", <unistd.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_copy_file_range.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_create.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_create.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_create.cpp` implements FUSE create/open for new files with cache and passthrough support. The source was read as a complete 355-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::create`, `FileInfo`, `state.open_files`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::create` chooses cache flags, adjusts writeback flags, clones parent paths, creates as request uid/gid, stores `FileInfo` in `state.open_files`, and may attach a passthrough backing id.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_create.hpp", "state.hpp", "config.hpp", "fs_readlink.hpp", "errno.hpp", "fileinfo.hpp", "fs_acl.hpp", "fs_close.hpp". Central integration with config policies, branches, ACL umask handling, procfs process names, and passthrough. Impossible nodeid collisions are treated as critical errors.

## Risks and Edge Cases

Central integration with config policies, branches, ACL umask handling, procfs process names, and passthrough. Impossible nodeid collisions are treated as critical errors.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_create.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_create.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_create.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_create.hpp` declares the FUSE `create` operation entry point. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `create`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h", <sys/types.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_create.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_destroy.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_destroy.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_destroy.cpp` provides the FUSE destroy hook. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::destroy`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::destroy` is intentionally empty; process teardown handles owned state elsewhere.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_destroy.hpp". Safe only while cleanup remains owned by other lifecycle paths.

## Risks and Edge Cases

Safe only while cleanup remains owned by other lifecycle paths.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_destroy.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_destroy.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_destroy.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_destroy.hpp` declares the FUSE `destroy` operation entry point. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `destroy`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies are limited to neighboring mergerfs declarations or platform libc/syscall interfaces. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_destroy.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fallocate.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_fallocate.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fallocate.cpp` implements fallocate on an open file handle. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fallocate`, `FileInfo`, `fs::fallocate`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fallocate` looks up `FileInfo` from state and delegates to `fs::fallocate`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fallocate.hpp", "state.hpp", "errno.hpp", "fileinfo.hpp", "fs_fallocate.hpp", "fuse.h". No branch policy is consulted after open; errors reflect the backing filesystem.

## Risks and Edge Cases

No branch policy is consulted after open; errors reflect the backing filesystem.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fallocate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fallocate.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_fallocate.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fallocate.hpp` declares the FUSE `fallocate` operation entry point. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fallocate`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fallocate.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchmod.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_fchmod.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fchmod.cpp` implements fchmod on an open file handle. The source was read as a complete 60-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fchmod`, `FileInfo`, `fs::fchmod`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fchmod` resolves `FileInfo` and calls `fs::fchmod` on the backing fd.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fchmod.hpp", "errno.hpp", "fileinfo.hpp", "fs_fchmod.hpp", "state.hpp", "fuse.h". Only affects the opened backing file, not every duplicate across branches.

## Risks and Edge Cases

Only affects the opened backing file, not every duplicate across branches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchmod.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchmod.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_fchmod.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fchmod.hpp` declares the FUSE `fchmod` operation entry point. The source was read as a complete 35-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fchmod`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h", "fuse_req_ctx.h", <sys/stat.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchmod.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchown.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_fchown.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fchown.cpp` implements fchown on an open file handle. The source was read as a complete 64-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fchown`, `FileInfo`, `fs::fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fchown` resolves `FileInfo` and calls `fs::fchown` on the backing fd.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fchown.hpp", "errno.hpp", "fileinfo.hpp", "fs_fchown.hpp", "state.hpp", "fuse.h", <unistd.h>. Only the opened branch instance changes; permission/capability failures pass through.

## Risks and Edge Cases

Only the opened branch instance changes; permission/capability failures pass through.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchown.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchown.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_fchown.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fchown.hpp` declares the FUSE `fchown` operation entry point. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fchown`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fchown.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fgetattr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_fgetattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fgetattr.cpp` implements getattr for an open file handle. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fgetattr`, `fstat`, `fs::inode::calc`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fgetattr` calls `fstat`, rewrites inode through `fs::inode::calc`, and fills FUSE cache timeouts from config.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fgetattr.hpp", "config.hpp", "errno.hpp", "fileinfo.hpp", "fs_fstat.hpp", "fs_inode.hpp", "state.hpp", "fuse.h". Keeps open-unlinked files stattable through the fd. Inode algorithm changes can affect observed identity.

## Risks and Edge Cases

Keeps open-unlinked files stattable through the fd. Inode algorithm changes can affect observed identity.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fgetattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fgetattr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_fgetattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fgetattr.hpp` declares the FUSE `fgetattr` operation entry point. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fgetattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h", <sys/stat.h>, <sys/types.h>, <unistd.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fgetattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_flush.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_flush.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_flush.cpp` implements FUSE flush using the close-of-dup pattern. The source was read as a complete 61-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::flush`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::flush` duplicates the backing fd and closes the duplicate so close-time writeback errors can surface without closing the real handle.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_flush.hpp", "errno.hpp", "fileinfo.hpp", "fs_close.hpp", "fs_dup.hpp", "state.hpp", "fuse.h". Returns `-EIO` if dup fails; otherwise errors mirror close on the duplicate.

## Risks and Edge Cases

Returns `-EIO` if dup fails; otherwise errors mirror close on the duplicate.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_flush.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_flush.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_flush.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_flush.hpp` declares the FUSE `flush` operation entry point. The source was read as a complete 29-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `flush`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_flush.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsync.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_fsync.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fsync.cpp` implements fsync/fdatasync on an open file handle. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fsync`, `FileInfo`, `fs::fdatasync`, `fs::fsync`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fsync` resolves `FileInfo` and calls `fs::fdatasync` or `fs::fsync` depending on the datasync flag.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fsync.hpp", "errno.hpp", "fileinfo.hpp", "fs_fdatasync.hpp", "fs_fsync.hpp", "state.hpp", "to_neg_errno.hpp", "fuse.h". Only syncs the opened backing file; storage guarantees depend on the branch filesystem.

## Risks and Edge Cases

Only syncs the opened backing file; storage guarantees depend on the branch filesystem.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsync.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsync.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_fsync.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fsync.hpp` declares the FUSE `fsync` operation entry point. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fsync`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsync.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsyncdir.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_fsyncdir.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fsyncdir.cpp` declares directory fsync unsupported after validating the directory handle. The source was read as a complete 50-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::fsyncdir`, `fh`, `DirInfo`, `-EBADF`, `-ENOSYS`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::fsyncdir` converts `fh` to `DirInfo`, returns `-EBADF` if invalid, otherwise `-ENOSYS`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_fsyncdir.hpp", "errno.hpp", "dirinfo.hpp", "fs_fsync.hpp", "fuse.h", <string>, <vector>. Callers must tolerate unsupported directory fsync.

## Risks and Edge Cases

Callers must tolerate unsupported directory fsync.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsyncdir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsyncdir.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_fsyncdir.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_fsyncdir.hpp` declares the FUSE `fsyncdir` operation entry point. The source was read as a complete 30-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `fsyncdir`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_fsyncdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ftruncate.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_ftruncate.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_ftruncate.cpp` implements truncate by open file handle. The source was read as a complete 60-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::ftruncate`, `FileInfo`, `fs::ftruncate`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::ftruncate` resolves `FileInfo` and delegates to `fs::ftruncate` with the requested size.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_ftruncate.hpp", "errno.hpp", "fileinfo.hpp", "fs_ftruncate.hpp", "state.hpp", "fuse.h". Only changes the opened branch instance; ENOSPC/EINVAL behavior comes from the backing fs.

## Risks and Edge Cases

Only changes the opened branch instance; ENOSPC/EINVAL behavior comes from the backing fs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ftruncate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ftruncate.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_ftruncate.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_ftruncate.hpp` declares the FUSE `ftruncate` operation entry point. The source was read as a complete 34-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `ftruncate`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h", <sys/types.h>, <unistd.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ftruncate.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_futimens.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_futimens.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_futimens.cpp` implements timestamp updates by open file handle. The source was read as a complete 62-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::futimens`, `FileInfo`, `fs::futimens`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::futimens` resolves `FileInfo` and delegates to `fs::futimens` with the supplied timespec array.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_futimens.hpp", "errno.hpp", "fileinfo.hpp", "fs_futimens.hpp", "state.hpp", "fuse.h", <sys/stat.h>. Timestamp semantics depend on platform futimens support and UTIME_NOW/OMIT handling below the wrapper.

## Risks and Edge Cases

Timestamp semantics depend on platform futimens support and UTIME_NOW/OMIT handling below the wrapper.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_futimens.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_futimens.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_futimens.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_futimens.hpp` declares the FUSE `futimens` operation entry point. The source was read as a complete 33-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `futimens`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h", <sys/stat.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_futimens.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getattr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_getattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getattr.cpp` implements path-based FUSE getattr and synthetic attrs for root/control files. The source was read as a complete 239-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::getattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::getattr` selects a branch, applies symlink-follow behavior, optional symlinkify conversion, virtual inode calculation, and cache timeout selection.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_getattr.hpp", "config.hpp", "errno.hpp", "fs_fstat.hpp", "fs_inode.hpp", "fs_lstat.hpp", "fs_path.hpp", "fs_stat.hpp". Core lookup path; risks are stale cache timeouts, symlink policy surprises, and inode collision/identity tradeoffs.

## Risks and Edge Cases

Core lookup path; risks are stale cache timeouts, symlink policy surprises, and inode collision/identity tradeoffs.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getattr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_getattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getattr.hpp` declares the FUSE `getattr` operation entry point. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `getattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h", "fs_path.hpp", <sys/types.h>, <sys/stat.h>, <unistd.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getxattr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_getxattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getxattr.cpp` implements FUSE getxattr including mergerfs virtual attributes. The source was read as a complete 205-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::getxattr`, `security.capability`, `user.mergerfs.*`, `lgetxattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::getxattr` handles control-file config xattrs, optional `security.capability` hiding, xattr mode, virtual `user.mergerfs.*` values, and fallback `lgetxattr`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_getxattr.hpp", "config.hpp", "errno.hpp", "fs_findallfiles.hpp", "fs_lgetxattr.hpp", "fs_path.hpp", "fs_statvfs_cache.hpp", "str.hpp". Exposes configuration and branch paths intentionally. Buffer-size handling follows xattr probe conventions and can return `-ERANGE`.

## Risks and Edge Cases

Exposes configuration and branch paths intentionally. Buffer-size handling follows xattr probe conventions and can return `-ERANGE`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getxattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_getxattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_getxattr.hpp` declares the FUSE `getxattr` operation entry point. The source was read as a complete 34-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `getxattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h", <cstddef>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_getxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_init.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_init.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_init.cpp` negotiates FUSE connection capabilities and logs runtime configuration. The source was read as a complete 244-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::init`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::init` initializes procfs/readdir config, requests supported capabilities, adjusts max-pages/sysfs limits, spawns detached readahead setup, validates passthrough/cache combinations, and logs config.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_init.hpp", "config.hpp", "fs_readahead.hpp", "procfs.hpp", "state.hpp", "syslog.hpp", "fs_path.hpp", "fs_exists.hpp". Startup-critical; risks include sysfs permissions, detached readahead timing, and kernel capability mismatches.

## Risks and Edge Cases

Startup-critical; risks include sysfs permissions, detached readahead timing, and kernel capability mismatches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_init.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_init.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_init.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_init.hpp` declares the FUSE `init` operation entry point. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `init`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_init.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ioctl.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_ioctl.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_ioctl.cpp` implements ioctl pass-through for open files and directories with safety filters. The source was read as a complete 207-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::ioctl`, `FS_IOC_*`, `fs::ioctl`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::ioctl` rejects btrfs ioctls, works around `FS_IOC_*` size issues, opens directory targets by policy, and delegates to `fs::ioctl`.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_ioctl.hpp", "fuse_getxattr.hpp", "fuse_setxattr.hpp", "config.hpp", "dirinfo.hpp", "endian.hpp", "errno.hpp", "fileinfo.hpp". Big-endian systems reject problematic flag/version ioctls. Directory ioctl depends on `FUSE_IOCTL_DIR` and open policy.

## Risks and Edge Cases

Big-endian systems reject problematic flag/version ioctls. Directory ioctl depends on `FUSE_IOCTL_DIR` and open policy.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ioctl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ioctl.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_ioctl.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_ioctl.hpp` declares the FUSE `ioctl` operation entry point. The source was read as a complete 35-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `ioctl`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "base_types.h", "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_ioctl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_link.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_link.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_link.cpp` implements hard-link creation across mergerfs branches with configurable EXDEV handling. The source was read as a complete 350-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::link`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::link` attempts path-preserving or create-policy hard links, clones parent dirs when needed, gets final attributes, and can convert EXDEV into symlinks per config.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_link.hpp", "config.hpp", "errno.hpp", "fs_clonepath.hpp", "fs_link.hpp", "fs_lstat.hpp", "fs_path.hpp", "fuse_getattr.hpp". Hard links cannot cross filesystems; symlink fallback disables cache because the visible type differs from the requested regular link.

## Risks and Edge Cases

Hard links cannot cross filesystems; symlink fallback disables cache because the visible type differs from the requested regular link.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_link.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_link.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_link.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_link.hpp` declares the FUSE `link` operation entry point. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `link`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse.h". Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_link.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_listxattr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_listxattr.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_listxattr.cpp` implements FUSE listxattr across policy-selected branch instances. The source was read as a complete 168-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::listxattr`, `llistxattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::listxattr` lists config keys for control files, honors global xattr mode, and concatenates each branch `llistxattr` result.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_listxattr.hpp", "config.hpp", "errno.hpp", "fs_llistxattr.hpp", "xattr.hpp", "fuse.h", <filesystem>, <string>. Duplicate names can appear from multiple branches; size can change between probe and fill.

## Risks and Edge Cases

Duplicate names can appear from multiple branches; size can change between probe and fill.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_listxattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_listxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_listxattr.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_listxattr.hpp` declares the FUSE `listxattr` operation entry point. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `listxattr`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h", <cstddef>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_listxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mkdir.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_mkdir.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_mkdir.cpp` implements FUSE mkdir with branch create policy and ACL-aware umask handling. The source was read as a complete 167-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::mkdir`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::mkdir` finds an existing parent branch, selects create branches, clones parent paths, applies umask only without default ACLs, creates as request uid/gid, and retries after read-only refresh.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_mkdir.hpp", "config.hpp", "errno.hpp", "error.hpp", "fs_acl.hpp", "fs_clonepath.hpp", "fs_mkdir_as.hpp", "fs_path.hpp". Partial branch creation can leave namespace divergence; readonly detection is refreshed after `-EROFS`.

## Risks and Edge Cases

Partial branch creation can leave namespace divergence; readonly detection is refreshed after `-EROFS`.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mkdir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mkdir.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_mkdir.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_mkdir.hpp` declares the FUSE `mkdir` operation entry point. The source was read as a complete 32-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `mkdir`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h", <sys/stat.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mkdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mknod.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_mknod.cpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_mknod.cpp` implements FUSE mknod with branch create policy and ACL-aware mode handling. The source was read as a complete 177-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `FUSE::mknod`, `mknod_as`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

`FUSE::mknod` mirrors mkdir flow for node creation: parent search, create-branch selection, clonepath, `mknod_as`, and retry after read-only refresh.

## State and Persistence Behavior

No file-backed persistence is introduced by this file. State changes are either process-local globals/caches, open file descriptors, branch filesystem metadata, or kernel-visible FUSE responses as described above.

## Dependencies and Integration Points

Direct dependencies include "fuse_mknod.hpp", "config.hpp", "errno.hpp", "error.hpp", "fs_acl.hpp", "fs_mknod_as.hpp", "fs_clonepath.hpp", "fs_path.hpp". Special file creation depends on privileges and backing filesystem support; partial success can diverge branches.

## Risks and Edge Cases

Special file creation depends on privileges and backing filesystem support; partial success can diverge branches.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mknod.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mknod.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_mknod.hpp

## Purpose

`sources/user-network-fs/mergerfs/src/fuse_mknod.hpp` declares the FUSE `mknod` operation entry point. The source was read as a complete 34-line file for this report.

## Important APIs, Types, and Functions

Important visible APIs/types/functions include `mknod`. The file belongs to mergerfs' low-level fs and FUSE adapter layer, where helpers conventionally return non-negative success values or negative errno values.

## Control Flow

This header has no standalone runtime control flow; callers include it to compile against the declared inline wrapper, type, or FUSE operation signature.

## State and Persistence Behavior

No durable state is owned here. Any state is caller-owned data, file descriptors, branch vectors, config policy objects, or kernel/FUSE structures passed through the API.

## Dependencies and Integration Points

Direct dependencies include "fuse_req_ctx.h", <sys/stat.h>. Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Risks and Edge Cases

Implemented by the paired `.cpp` and registered in the FUSE operation table; compile tests should catch signature drift.

## Test Signals

Useful test signals include build coverage, operation-level FUSE tests against temporary branches, errno-path checks, and platform-specific tests for Linux/FreeBSD behavior where applicable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_mknod.hpp -->
