# Research Group subset-b-009670

This grouped report covers the listed mergerfs FUSE operation, policy, command, and utility source files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_open.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_open.cpp

## Purpose

`fuse_open.cpp` implements the mergerfs FUSE `open` callback. It opens existing files through the configured search policy, creates per-handle FileInfo objects, coordinates shared open-file state by nodeid, and optionally installs Linux FUSE passthrough backing IDs.

## Important APIs, Types, and Functions

types/namespaces: `stat`, `timespec`; functions: `FUSE::open`, `FUSE::passthrough_close`, `FUSE::passthrough_open`, `FUSE::release`

## Control Flow

select a branch, adjust cache/writeback flags, break copy-on-write links when configured, open or duplicate a canonical fd, insert or visit state.open_files, and unwind fd/backing resources on races

## State and Persistence Behavior

The file has 493 source lines and 13906 bytes. Its direct include set is: `fuse_open.hpp`, `state.hpp`, `config.hpp`, `errno.hpp`, `fileinfo.hpp`, `fuse_release.hpp`, `fs_close.hpp`, `fs_cow.hpp`, `fs_fchmod.hpp`, `fs_lchmod.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: state.open_files refcounts, FileInfo ownership, fuse_file_info flags and backing_id, cfg cache/passthrough/nfsopenhack/link_cow settings. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_open.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_open.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_open.hpp

## Purpose

This header declares the `FUSE::open` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that opens existing files through the configured search policy, creates per-handle FileInfo objects, coordinates shared open-file state by nodeid, and optionally installs Linux FUSE passthrough backing IDs. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 30 source lines and 971 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: state.open_files refcounts, FileInfo ownership, fuse_file_info flags and backing_id, cfg cache/passthrough/nfsopenhack/link_cow settings.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_open.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_opendir.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_opendir.cpp

## Purpose

`fuse_opendir.cpp` implements the mergerfs FUSE `opendir` callback. It allocates a DirInfo handle for directory iteration and configures FUSE directory caching flags.

## Important APIs, Types, and Functions

functions: `FUSE::opendir`

## Control Flow

create DirInfo from the fuse path, store it in ffi->fh, suppress flushes, and enable keep_cache/cache_readdir when cfg.cache_readdir is set

## State and Persistence Behavior

The file has 47 source lines and 1255 bytes. Its direct include set is: `fuse_opendir.hpp`, `config.hpp`, `dirinfo.hpp`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: DirInfo lifetime between opendir/releasedir and cfg.cache_readdir. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_opendir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_opendir.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_opendir.hpp

## Purpose

This header declares the `FUSE::opendir` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that allocates a DirInfo handle for directory iteration and configures FUSE directory caching flags. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 30 source lines and 980 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: DirInfo lifetime between opendir/releasedir and cfg.cache_readdir.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_opendir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_passthrough.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_passthrough.hpp

## Purpose

This header declares the `FUSE::passthrough` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that declares a FUSE callback. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 43 source lines and 1217 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no owned state in the header.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_passthrough.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_poll.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_poll.cpp

## Purpose

`fuse_poll.cpp` implements the mergerfs FUSE `poll` callback. It declares that poll is not implemented for this filesystem.

## Important APIs, Types, and Functions

functions: `FUSE::poll`

## Control Flow

ignore callback arguments and return -ENOSYS so libfuse/kernel fall back cleanly

## State and Persistence Behavior

The file has 38 source lines and 1127 bytes. Its direct include set is: `fuse_poll.hpp`, `errno.hpp`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_poll.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_poll.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_poll.hpp

## Purpose

This header declares the `FUSE::poll` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that declares that poll is not implemented for this filesystem. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 31 source lines and 1012 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_poll.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_read.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_read.cpp

## Purpose

`fuse_read.cpp` implements the mergerfs FUSE `read` callback. It reads from the FileInfo fd selected by open and mirrors client I/O priority while serving either direct_io or cached handles.

## Important APIs, Types, and Functions

functions: `FUSE::read`, `FUSE::read_null`, `ioprio::SetFrom`

## Control Flow

resolve FileInfo from state, reject stale handles with -EBADF, then call fs::pread for the requested offset and size

## State and Persistence Behavior

The file has 89 source lines and 2178 bytes. Its direct include set is: `fuse_read.hpp`, `errno.hpp`, `fileinfo.hpp`, `fs_pread.hpp`, `ioprio.hpp`, `state.hpp`, `fuse.h`, `stdlib.h`, `string.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: FileInfo fd/direct_io and thread-local ioprio::SetFrom. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_read.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_read.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_read.hpp

## Purpose

This header declares the `FUSE::read` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that reads from the FileInfo fd selected by open and mirrors client I/O priority while serving either direct_io or cached handles. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 41 source lines and 1289 bytes. Its direct include set is: `fuse.h`, `sys/types.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: FileInfo fd/direct_io and thread-local ioprio::SetFrom.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_read.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir.cpp

## Purpose

`fuse_readdir.cpp` implements the mergerfs FUSE `readdir` callback. It dispatches directory listing to a runtime-selected sequential or concurrent readdir strategy.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDir`, `FUSE::ReadDirBase`, `FUSE::ReadDirFactory`, `FUSE::readdir`

## Control Flow

cfg.readdir invokes ReadDir, which swaps implementations under a shared mutex, delegates to ReadDirBase, and converts root ENOENT into a synthetic diagnostic dirent

## State and Persistence Behavior

The file has 143 source lines and 2971 bytes. Its direct include set is: `fuse_readdir.hpp`, `fuse_readdir_factory.hpp`, `dirinfo.hpp`, `fatal.hpp`, `fuse_dirents.hpp`, `config.hpp`, `cstring`, `dirent.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: ReadDir::_impl, _str, _initialized, DirInfo fusepath, and cfg.readdir. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir.hpp

## Purpose

This header declares the `FUSE::readdir` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDir`; functions: `FUSE::ReadDirBase`

## Control Flow

The declared API participates in the operation that dispatches directory listing to a runtime-selected sequential or concurrent readdir strategy. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 67 source lines and 1988 bytes. Its direct include set is: `fuse.h`, `tofrom_string.hpp`, `fuse_readdir_base.hpp`, `memory`, `mutex`, `shared_mutex`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: ReadDir::_impl, _str, _initialized, DirInfo fusepath, and cfg.readdir.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_base.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_base.hpp

## Purpose

This header declares the `FUSE::readdir_base` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDirBase`

## Control Flow

The declared API participates in the operation that declares a FUSE callback. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 39 source lines and 1157 bytes. Its direct include set is: `fuse.h`, `string_view`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no owned state in the header.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_base.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cor.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_cor.cpp

## Purpose

`fuse_readdir_cor.cpp` implements the mergerfs FUSE `readdir_cor` callback. It implements concurrent-open/concurrent-read directory merging across all branches.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirCOR`

## Control Flow

reset the output dirents, enqueue one branch task per branch in a ThreadPool, use a HashSet and mutex to deduplicate names while appending, and fold worker errors through Err

## State and Persistence Behavior

The file has 105 source lines and 2913 bytes. Its direct include set is: `fuse_readdir_cor.hpp`, `supported_getdents64.hpp`, `config.hpp`, `dirinfo.hpp`, `error.hpp`, `fuse_readdir_cor_getdents.icpp`, `fuse_readdir_cor_readdir.icpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: ThreadPool lifetime in ReadDirCOR and per-call HashSet/mutex state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cor.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_cor.hpp

## Purpose

This header declares the `FUSE::readdir_cor` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDirCOR`; functions: `FUSE::ReadDirBase`

## Control Flow

The declared API participates in the operation that implements concurrent-open/concurrent-read directory merging across all branches. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 43 source lines and 1281 bytes. Its direct include set is: `fuse_readdir_base.hpp`, `thread_pool.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: ThreadPool lifetime in ReadDirCOR and per-call HashSet/mutex state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cor.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.cpp

## Purpose

`fuse_readdir_cosr.cpp` implements the mergerfs FUSE `readdir_cosr` callback. It implements concurrent-open/sequential-read directory listing.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirCOSR`

## Control Flow

use the thread pool to open branches, then consume the resulting DirRV futures to append merged entries to the output buffer

## State and Persistence Behavior

The file has 77 source lines and 2055 bytes. Its direct include set is: `fuse_readdir_cosr.hpp`, `config.hpp`, `dirinfo.hpp`, `supported_getdents64.hpp`, `fuse_readdir_cosr_getdents.icpp`, `fuse_readdir_cosr_readdir.icpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: ThreadPool lifetime in ReadDirCOSR and transient future list. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.hpp

## Purpose

This header declares the `FUSE::readdir_cosr` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDirCOSR`; functions: `FUSE::ReadDirBase`

## Control Flow

The declared API participates in the operation that implements concurrent-open/sequential-read directory listing. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 42 source lines and 1286 bytes. Its direct include set is: `fuse_readdir_base.hpp`, `thread_pool.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: ThreadPool lifetime in ReadDirCOSR and transient future list.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_factory.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_factory.cpp

## Purpose

`fuse_readdir_factory.cpp` implements the mergerfs FUSE `readdir_factory` callback. It parses the readdir mode string and builds seq, cosr, or cor implementations.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirBase`, `FUSE::ReadDirCOR`, `FUSE::ReadDirCOSR`, `FUSE::ReadDirFactory`, `FUSE::ReadDirSeq`

## Control Flow

match type[:concurrency[:queue-depth]], derive defaults from hardware_concurrency, bound nonpositive values, and return the matching ReadDirBase instance

## State and Persistence Behavior

The file has 121 source lines and 3244 bytes. Its direct include set is: `fuse_readdir_factory.hpp`, `fuse_readdir_cor.hpp`, `fuse_readdir_cosr.hpp`, `fuse_readdir_seq.hpp`, `array`, `cassert`, `cmath`, `cstdio`, `cstdlib`, `regex`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no global state; constructed objects own any thread pools. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_factory.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_factory.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_factory.hpp

## Purpose

This header declares the `FUSE::readdir_factory` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDirFactory`

## Control Flow

The declared API participates in the operation that parses the readdir mode string and builds seq, cosr, or cor implementations. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 35 source lines and 1076 bytes. Its direct include set is: `fuse_readdir_base.hpp`, `string`, `memory`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no global state; constructed objects own any thread pools.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_factory.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_plus.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_plus.cpp

## Purpose

`fuse_readdir_plus.cpp` implements the mergerfs FUSE `readdir_plus` callback. It marks readdir_plus unsupported.

## Important APIs, Types, and Functions

functions: `FUSE::readdir_plus`

## Control Flow

return -ENOTSUP without touching the buffer

## State and Persistence Behavior

The file has 30 source lines and 1033 bytes. Its direct include set is: `fuse_readdir_plus.hpp`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_plus.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_plus.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_plus.hpp

## Purpose

This header declares the `FUSE::readdir_plus` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that marks readdir_plus unsupported. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 29 source lines and 1002 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_plus.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_seq.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_seq.cpp

## Purpose

`fuse_readdir_seq.cpp` implements the mergerfs FUSE `readdir_seq` callback. It implements sequential branch directory listing.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirSeq`

## Control Flow

delegate to getdents64 or readdir include implementation depending on platform support and merge branch entries in order

## State and Persistence Behavior

The file has 45 source lines and 1421 bytes. Its direct include set is: `fuse_readdir_seq.hpp`, `config.hpp`, `supported_getdents64.hpp`, `fuse_readdir_seq_getdents.icpp`, `fuse_readdir_seq_readdir.icpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: transient HashSet/dirent accumulation through included implementation. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_seq.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_seq.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readdir_seq.hpp

## Purpose

This header declares the `FUSE::readdir_seq` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDirSeq`; functions: `FUSE::ReadDirBase`

## Control Flow

The declared API participates in the operation that implements sequential branch directory listing. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 36 source lines and 1130 bytes. Its direct include set is: `fuse_readdir_base.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: transient HashSet/dirent accumulation through included implementation.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readdir_seq.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readlink.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_readlink.cpp

## Purpose

`fuse_readlink.cpp` implements the mergerfs FUSE `readlink` callback. It resolves symlink targets from the selected branch and can expose symlinkify paths for eligible regular files.

## Important APIs, Types, and Functions

types/namespaces: `stat`; functions: `FUSE::readlink`

## Control Flow

search branches for the path, optionally lstat and synthesize a target path when symlinkify applies, otherwise call fs::readlink

## State and Persistence Behavior

The file has 124 source lines and 3399 bytes. Its direct include set is: `fuse_readlink.hpp`, `config.hpp`, `errno.hpp`, `fs_lstat.hpp`, `fs_path.hpp`, `fs_readlink.hpp`, `symlinkify.hpp`, `fuse.h`, `algorithm`, `cstring`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: cfg.readlink policy, symlinkify toggle/timeout, no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readlink.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_readlink.hpp

## Purpose

This header declares the `FUSE::readlink` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that resolves symlink targets from the selected branch and can expose symlinkify paths for eligible regular files. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 33 source lines and 1055 bytes. Its direct include set is: `fuse_req_ctx.h`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: cfg.readlink policy, symlinkify toggle/timeout, no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_readlink.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_release.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_release.cpp

## Purpose

`fuse_release.cpp` implements the mergerfs FUSE `release` callback. It closes FileInfo handles and tears down shared open-file state created by fuse_open.

## Important APIs, Types, and Functions

functions: `FUSE::passthrough_close`, `FUSE::release`

## Control Flow

optionally fadvise DONTNEED twice, decrement state.open_files refcount under erase_if, close passthrough backing IDs and canonical/per-handle fds after map mutation

## State and Persistence Behavior

The file has 138 source lines and 4397 bytes. Its direct include set is: `fuse_release.hpp`, `state.hpp`, `config.hpp`, `fileinfo.hpp`, `fs_close.hpp`, `fs_fadvise.hpp`, `fuse_passthrough.hpp`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: state.open_files, FileInfo lifetime, cfg.dropcacheonclose. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_release.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_release.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_release.hpp

## Purpose

This header declares the `FUSE::release` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `FileInfo`

## Control Flow

The declared API participates in the operation that closes FileInfo handles and tears down shared open-file state created by fuse_open. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 61 source lines and 2079 bytes. Its direct include set is: `base_types.h`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: state.open_files, FileInfo lifetime, cfg.dropcacheonclose.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_release.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_releasedir.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_releasedir.cpp

## Purpose

`fuse_releasedir.cpp` implements the mergerfs FUSE `releasedir` callback. It releases DirInfo allocated by opendir.

## Important APIs, Types, and Functions

functions: `FUSE::releasedir`

## Control Flow

recover DirInfo from ffi->fh, reject invalid handles, delete it, and return success

## State and Persistence Behavior

The file has 46 source lines and 1179 bytes. Its direct include set is: `fuse_releasedir.hpp`, `config.hpp`, `dirinfo.hpp`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: DirInfo heap ownership. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_releasedir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_releasedir.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_releasedir.hpp

## Purpose

This header declares the `FUSE::releasedir` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that releases DirInfo allocated by opendir. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 29 source lines and 948 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: DirInfo heap ownership.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_releasedir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removemapping.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_removemapping.cpp

## Purpose

`fuse_removemapping.cpp` implements the mergerfs FUSE `removemapping` callback. It advertises unsupported FUSE memory mapping removal.

## Important APIs, Types, and Functions

functions: `FUSE::removemapping`

## Control Flow

return -ENOSYS

## State and Persistence Behavior

The file has 28 source lines and 933 bytes. Its direct include set is: `fuse_removemapping.hpp`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removemapping.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removemapping.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_removemapping.hpp

## Purpose

This header declares the `FUSE::removemapping` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that advertises unsupported FUSE memory mapping removal. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 27 source lines and 905 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removemapping.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removexattr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_removexattr.cpp

## Purpose

`fuse_removexattr.cpp` implements the mergerfs FUSE `removexattr` callback. It removes extended attributes from all policy-selected branch copies.

## Important APIs, Types, and Functions

functions: `FUSE::removexattr`

## Control Flow

skip control file xattrs, honor global xattr disable mode, apply lremovexattr across action branches, then reconcile partial failures against the getxattr search branch

## State and Persistence Behavior

The file has 114 source lines and 3017 bytes. Its direct include set is: `fuse_removexattr.hpp`, `config.hpp`, `errno.hpp`, `fs_lremovexattr.hpp`, `fs_path.hpp`, `policy_rv.hpp`, `fuse.h`, `vector`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: PolicyRV success/error vectors and cfg xattr policies. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removexattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removexattr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_removexattr.hpp

## Purpose

This header declares the `FUSE::removexattr` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that removes extended attributes from all policy-selected branch copies. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 30 source lines and 1005 bytes. Its direct include set is: `fuse_req_ctx.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: PolicyRV success/error vectors and cfg xattr policies.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_removexattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rename.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_rename.cpp

## Purpose

`fuse_rename.cpp` implements the mergerfs FUSE `rename` callback. It renames paths across branch copies while respecting path-preserving create policies and configured EXDEV behavior.

## Important APIs, Types, and Functions

functions: `FUSE::rename`, `FUSE::symlink`

## Control Flow

choose preserve-path or create-path algorithm, rename matching branch copies, clone destination parent paths when needed, remove stale destinations, and on EXDEV optionally stage old paths under .mergerfs_rename_exdev plus symlink

## State and Persistence Behavior

The file has 368 source lines and 9308 bytes. Its direct include set is: `fuse_rename.hpp`, `config.hpp`, `error.hpp`, `errno.hpp`, `fs_clonepath.hpp`, `fs_link.hpp`, `fs_mkdir_as.hpp`, `fs_path.hpp`, `fs_remove.hpp`, `fs_rename.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: branch filesystem contents, cfg.rename_exdev, cfg.ignorepponrename, rename/getattr/create policies. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rename.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rename.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_rename.hpp

## Purpose

This header declares the `FUSE::rename` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that renames paths across branch copies while respecting path-preserving create policies and configured EXDEV behavior. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 30 source lines and 980 bytes. Its direct include set is: `fuse_req_ctx.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: branch filesystem contents, cfg.rename_exdev, cfg.ignorepponrename, rename/getattr/create policies.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rename.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rmdir.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_rmdir.cpp

## Purpose

`fuse_rmdir.cpp` implements the mergerfs FUSE `rmdir` callback. It removes directories across policy-selected branch copies and can unlink symlink-followed pseudo-directories.

## Important APIs, Types, and Functions

types/namespaces: `RmdirErr`; functions: `FUSE::rmdir`

## Control Flow

collect action branches, call rmdir on each full path, optionally unlink on ENOTDIR when following symlinks, and prioritize ENOTEMPTY/EEXIST in RmdirErr

## State and Persistence Behavior

The file has 149 source lines and 3443 bytes. Its direct include set is: `fuse_rmdir.hpp`, `config.hpp`, `errno.hpp`, `fs_path.hpp`, `fs_rmdir.hpp`, `fs_unlink.hpp`, `fuse.h`, `string`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: RmdirErr aggregation and cfg.follow_symlinks. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rmdir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rmdir.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_rmdir.hpp

## Purpose

This header declares the `FUSE::rmdir` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that removes directories across policy-selected branch copies and can unlink symlink-followed pseudo-directories. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 29 source lines and 947 bytes. Its direct include set is: `fuse_req_ctx.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: RmdirErr aggregation and cfg.follow_symlinks.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_rmdir.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setupmapping.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_setupmapping.cpp

## Purpose

`fuse_setupmapping.cpp` implements the mergerfs FUSE `setupmapping` callback. It advertises unsupported FUSE setupmapping.

## Important APIs, Types, and Functions

functions: `FUSE::setupmapping`

## Control Flow

return -ENOSYS

## State and Persistence Behavior

The file has 34 source lines and 1207 bytes. Its direct include set is: `fuse_setupmapping.hpp`, `sys/types.h`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setupmapping.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setupmapping.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_setupmapping.hpp

## Purpose

This header declares the `FUSE::setupmapping` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that advertises unsupported FUSE setupmapping. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 33 source lines and 1200 bytes. Its direct include set is: `base_types.h`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setupmapping.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setxattr.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_setxattr.cpp

## Purpose

`fuse_setxattr.cpp` implements the mergerfs FUSE `setxattr` callback. It sets extended attributes on branch copies and implements mergerfs control xattr commands/settings.

## Important APIs, Types, and Functions

functions: `FUSE::setxattr`

## Control Flow

handle .mergerfs control keys and command xattrs, block security.capability when disabled, honor global xattr mode, apply lsetxattr across action branches, then map partial failures through getxattr policy

## State and Persistence Behavior

The file has 230 source lines and 6105 bytes. Its direct include set is: `fuse_setxattr.hpp`, `config.hpp`, `errno.hpp`, `fs_glob.hpp`, `fs_lsetxattr.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `num.hpp`, `policy_rv.hpp`, `str.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: cfg mutable options, statvfs cache timeout, PolicyRV, and control xattr command side effects. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setxattr.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setxattr.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_setxattr.hpp

## Purpose

This header declares the `FUSE::setxattr` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that sets extended attributes on branch copies and implements mergerfs control xattr commands/settings. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 35 source lines and 1143 bytes. Its direct include set is: `cstddef`, `fuse_req_ctx.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: cfg mutable options, statvfs cache timeout, PolicyRV, and control xattr command side effects.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_setxattr.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statfs.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_statfs.cpp

## Purpose

`fuse_statfs.cpp` implements the mergerfs FUSE `statfs` callback. It merges statvfs information from underlying branch filesystems.

## Important APIs, Types, and Functions

types/namespaces: `stat`, `statvfs`; functions: `FUSE::statfs`

## Control Flow

stat each branch or branch/path, deduplicate by st_dev, normalize block sizes/name limits, optionally zero available counts for read-only/no-create branches, and sum totals

## State and Persistence Behavior

The file has 161 source lines and 4580 bytes. Its direct include set is: `fuse_statfs.hpp`, `config.hpp`, `errno.hpp`, `fs_lstat.hpp`, `fs_path.hpp`, `fs_lstatvfs.hpp`, `statvfs_util.hpp`, `fuse.h`, `filesystem`, `algorithm`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: transient dev-to-statvfs map and cfg.statfs/statfs_ignore. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statfs.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_statfs.hpp

## Purpose

This header declares the `FUSE::statfs` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `statvfs`

## Control Flow

The declared API participates in the operation that merges statvfs information from underlying branch filesystems. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 32 source lines and 1014 bytes. Its direct include set is: `fuse_req_ctx.h`, `sys/statvfs.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: transient dev-to-statvfs map and cfg.statfs/statfs_ignore.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statx.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_statx.cpp

## Purpose

`fuse_statx.cpp` implements the mergerfs FUSE `statx` callback. It selects the supported or unsupported statx implementation at compile time.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

include fuse_statx_supported.icpp when MERGERFS_SUPPORTED_STATX is defined, otherwise include the unsupported implementation

## State and Persistence Behavior

The file has 27 source lines and 1025 bytes. Its direct include set is: `fs_statx.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no local state; depends on platform feature macros. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statx.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_statx.hpp

## Purpose

This header declares the `FUSE::statx` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `fuse_statx`

## Control Flow

The declared API participates in the operation that selects the supported or unsupported statx implementation at compile time. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 40 source lines and 1415 bytes. Its direct include set is: `base_types.h`, `fuse.h`, `fuse_kernel.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no local state; depends on platform feature macros.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_statx.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_symlink.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_symlink.cpp

## Purpose

`fuse_symlink.cpp` implements the mergerfs FUSE `symlink` callback. It creates symlinks on selected create branches after cloning required parent paths from an existing branch.

## Important APIs, Types, and Functions

types/namespaces: `stat`; functions: `FUSE::symlink`

## Control Flow

find an existing parent branch, choose create branches, clone directory structure, create symlinks as the caller uid/gid, calculate synthetic inode data, and set cache timeouts based on follow_symlinks

## State and Persistence Behavior

The file has 195 source lines and 5258 bytes. Its direct include set is: `fuse_symlink.hpp`, `config.hpp`, `errno.hpp`, `error.hpp`, `fs_clonepath.hpp`, `fs_lstat.hpp`, `fs_path.hpp`, `fs_inode.hpp`, `fs_symlink_as.hpp`, `fuse_getattr.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: branch directory trees, returned stat/timeouts, cfg symlink/getattr policies. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_symlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_symlink.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_symlink.hpp

## Purpose

This header declares the `FUSE::symlink` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `stat`

## Control Flow

The declared API participates in the operation that creates symlinks on selected create branches after cloning required parent paths from an existing branch. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 44 source lines and 1371 bytes. Its direct include set is: `fuse.h`, `fs_path.hpp`, `string`, `sys/stat.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: branch directory trees, returned stat/timeouts, cfg symlink/getattr policies.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_symlink.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_syncfs.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_syncfs.cpp

## Purpose

`fuse_syncfs.cpp` implements the mergerfs FUSE `syncfs` callback. It advertises unsupported syncfs.

## Important APIs, Types, and Functions

functions: `FUSE::syncfs`

## Control Flow

return -ENOSYS

## State and Persistence Behavior

The file has 28 source lines and 920 bytes. Its direct include set is: `fuse_syncfs.hpp`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_syncfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_syncfs.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_syncfs.hpp

## Purpose

This header declares the `FUSE::syncfs` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that advertises unsupported syncfs. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 27 source lines and 898 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_syncfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_tmpfile.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_tmpfile.cpp

## Purpose

`fuse_tmpfile.cpp` implements the mergerfs FUSE `tmpfile` callback. It advertises unsupported tmpfile despite including create support.

## Important APIs, Types, and Functions

functions: `FUSE::tmpfile`

## Control Flow

return -ENOSYS

## State and Persistence Behavior

The file has 33 source lines and 1100 bytes. Its direct include set is: `fuse_tmpfile.hpp`, `fuse_create.hpp`, `errno.h`, `stdio.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_tmpfile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_tmpfile.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_tmpfile.hpp

## Purpose

This header declares the `FUSE::tmpfile` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that advertises unsupported tmpfile despite including create support. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 33 source lines and 1042 bytes. Its direct include set is: `fuse.h`, `sys/types.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_tmpfile.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_truncate.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_truncate.cpp

## Purpose

`fuse_truncate.cpp` implements the mergerfs FUSE `truncate` callback. It truncates all policy-selected branch copies.

## Important APIs, Types, and Functions

functions: `FUSE::truncate`

## Control Flow

apply fs::truncate to each selected branch and reconcile partial failures against the getattr policy branch

## State and Persistence Behavior

The file has 109 source lines and 2798 bytes. Its direct include set is: `fuse_truncate.hpp`, `config.hpp`, `errno.hpp`, `fs_path.hpp`, `fs_truncate.hpp`, `policy_rv.hpp`, `fuse.h`, `sys/types.h`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: PolicyRV aggregation and branch file sizes. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_truncate.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_truncate.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_truncate.hpp

## Purpose

This header declares the `FUSE::truncate` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that truncates all policy-selected branch copies. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 32 source lines and 1016 bytes. Its direct include set is: `fuse_req_ctx.h`, `sys/types.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: PolicyRV aggregation and branch file sizes.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_truncate.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_unlink.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_unlink.cpp

## Purpose

`fuse_unlink.cpp` implements the mergerfs FUSE `unlink` callback. It unlinks all policy-selected branch copies.

## Important APIs, Types, and Functions

functions: `FUSE::unlink`

## Control Flow

collect unlink action branches, call fs::unlink on each branch path, and return the folded Err result

## State and Persistence Behavior

The file has 77 source lines and 1854 bytes. Its direct include set is: `fuse_unlink.hpp`, `config.hpp`, `errno.hpp`, `error.hpp`, `fs_path.hpp`, `fs_unlink.hpp`, `fuse.h`, `vector`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: branch filesystem entries only. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_unlink.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_unlink.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_unlink.hpp

## Purpose

This header declares the `FUSE::unlink` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that unlinks all policy-selected branch copies. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 29 source lines and 949 bytes. Its direct include set is: `fuse_req_ctx.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: branch filesystem entries only.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_unlink.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_utimens.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_utimens.cpp

## Purpose

`fuse_utimens.cpp` implements the mergerfs FUSE `utimens` callback. It updates timestamps on all policy-selected branch copies without following symlinks.

## Important APIs, Types, and Functions

functions: `FUSE::utimens`

## Control Flow

apply fs::lutimens to each selected branch and reconcile partial failures against the getattr policy branch

## State and Persistence Behavior

The file has 108 source lines and 2757 bytes. Its direct include set is: `fuse_utimens.hpp`, `config.hpp`, `errno.hpp`, `fs_lutimens.hpp`, `fs_path.hpp`, `policy_rv.hpp`, `fuse.h`, `fcntl.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: PolicyRV aggregation and branch inode timestamps. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_utimens.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_utimens.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_utimens.hpp

## Purpose

This header declares the `FUSE::utimens` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that updates timestamps on all policy-selected branch copies without following symlinks. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 32 source lines and 1013 bytes. Its direct include set is: `fuse_req_ctx.h`, `sys/stat.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: PolicyRV aggregation and branch inode timestamps.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_utimens.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_write.cpp -->
# sources/user-network-fs/mergerfs/src/fuse_write.cpp

## Purpose

`fuse_write.cpp` implements the mergerfs FUSE `write` callback. It writes to FileInfo fds and can migrate files to another branch on ENOSPC/EDQUOT.

## Important APIs, Types, and Functions

functions: `FUSE::write`, `FUSE::write_null`, `ioprio::SetFrom`

## Control Flow

resolve FileInfo, write with pwrite or pwriten depending on direct_io, retry under exclusive per-file mutex on space errors, move file with moveonenospc policy, dup2 the replacement fd, and finish the write

## State and Persistence Behavior

The file has 217 source lines and 5709 bytes. Its direct include set is: `fuse_write.hpp`, `config.hpp`, `errno.hpp`, `fileinfo.hpp`, `fs_close.hpp`, `fs_dup2.hpp`, `fs_movefile_and_open.hpp`, `fs_pwrite.hpp`, `fs_pwriten.hpp`, `ioprio.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: FileInfo fd/branch/fusepath/mutex, cfg.moveonenospc, thread-local ioprio. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_write.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_write.hpp -->
# sources/user-network-fs/mergerfs/src/fuse_write.hpp

## Purpose

This header declares the `FUSE::write` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`

## Control Flow

The declared API participates in the operation that writes to FileInfo fds and can migrate files to another branch on ENOSPC/EDQUOT. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 39 source lines and 1277 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: FileInfo fd/branch/fusepath/mutex, cfg.moveonenospc, thread-local ioprio.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/fuse_write.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/hashset.hpp -->
# sources/user-network-fs/mergerfs/src/hashset.hpp

## Purpose

`HashSet` is a small non-copyable 64-bit hash set used by readdir merging to deduplicate entry names without storing full strings.

## Important APIs, Types, and Functions

types/namespaces: `HashSet`

## Control Flow

`put` hashes names with rapidhash, keeps up to eight hashes inline, grows to a power-of-two open-addressed table, and returns whether the name was newly inserted.

## State and Persistence Behavior

The file has 182 source lines and 3582 bytes. Its direct include set is: `base_types.h`, `rapidhash/rapidhash.h`, `cstring`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

It stores hashes only, so correctness relies on low 64-bit collision probability; tests should cover duplicate names, inline-to-table growth, load-factor growth, and zero-hash remapping.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/hashset.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/hw_cpu.cpp -->
# sources/user-network-fs/mergerfs/src/hw_cpu.cpp

## Purpose

`hw::cpu::logical_core_count` exposes the online processor count for configuration defaults.

## Important APIs, Types, and Functions

types/namespaces: `cpu`, `hw`

## Control Flow

It calls `sysconf(_SC_NPROCESSORS_ONLN)` when available and otherwise returns 1.

## State and Persistence Behavior

The file has 36 source lines and 1024 bytes. Its direct include set is: `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are small but callers should handle zero or negative sysconf returns; tests can stub platform macros or verify positive fallback behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/hw_cpu.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/hw_cpu.hpp -->
# sources/user-network-fs/mergerfs/src/hw_cpu.hpp

## Purpose

This header declares `hw::cpu::logical_core_count`.

## Important APIs, Types, and Functions

types/namespaces: `cpu`, `hw`

## Control Flow

It is consumed by option/readdir configuration code that wants hardware-derived defaults.

## State and Persistence Behavior

The file has 28 source lines and 894 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The API is intentionally tiny and has no state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/hw_cpu.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ioprio.cpp -->
# sources/user-network-fs/mergerfs/src/ioprio.cpp

## Purpose

This file mirrors a client process I/O priority onto mergerfs worker threads on Linux.

## Important APIs, Types, and Functions

types/namespaces: `ioprio`; functions: `ioprio::SetFrom::_slow_apply`, `ioprio::SetFrom::thread_prio`, `ioprio::enable`, `ioprio::get`, `ioprio::set`

## Control Flow

`get` and `set` wrap `SYS_ioprio_get/set`; `enable` flips an atomic flag; `SetFrom::_slow_apply` reads the client pid priority and updates the current thread only when it changed.

## State and Persistence Behavior

The file has 92 source lines and 1975 bytes. Its direct include set is: `ioprio.hpp`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State is `_enabled` plus thread-local `SetFrom::thread_prio`; risks are Linux-only syscall availability and permission failures.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ioprio.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ioprio.hpp -->
# sources/user-network-fs/mergerfs/src/ioprio.hpp

## Purpose

This header declares the ioprio API and RAII-like `SetFrom` helper.

## Important APIs, Types, and Functions

types/namespaces: `SetFrom`, `ioprio`; functions: `ioprio::enabled`

## Control Flow

`SetFrom(pid)` cheaply checks the atomic enable flag and applies priority through `_slow_apply` only when enabled.

## State and Persistence Behavior

The file has 61 source lines and 1546 bytes. Its direct include set is: `atomic`, `sys/types.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Integration points are read/write paths; tests should cover disabled no-op behavior and syscall error propagation.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/ioprio.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs.cpp -->
# sources/user-network-fs/mergerfs/src/mergerfs.cpp

## Purpose

This is the primary executable entry point and app multiplexer for mergerfs, fsck.mergerfs, and mergerfs.collect-info.

## Important APIs, Types, and Functions

types/namespaces: `fuse_operations`; functions: `FUSE::access`, `FUSE::bmap`, `FUSE::chmod`, `FUSE::chown`, `FUSE::copy_file_range`, `FUSE::create`, `FUSE::destroy`, `FUSE::fallocate`, `FUSE::fchmod`, `FUSE::fchown`

## Control Flow

It builds `fuse_operations`, parses options, waits for branches, configures resources/capabilities/OOM score/signal handlers, optionally lazy-unmounts the mountpoint, and enters `fuse_main`.

## State and Persistence Behavior

The file has 398 source lines and 9809 bytes. Its direct include set is: `mergerfs.hpp`, `mergerfs_fsck.hpp`, `mergerfs_collect_info.hpp`, `caps.hpp`, `config.hpp`, `fs_path.hpp`, `fs_readahead.hpp`, `fs_umount2.hpp`, `fs_wait_for_mount.hpp`, `maintenance_thread.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State centers on global `cfg`, libfuse arguments, syslog, process resource limits, and capability/OOM side effects.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs.hpp -->
# sources/user-network-fs/mergerfs/src/mergerfs.hpp

## Purpose

This placeholder-style header is the include anchor for the main mergerfs executable translation unit.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

It exports no local declarations; integration is by convention through `mergerfs.cpp`.

## State and Persistence Behavior

The file has 19 source lines and 817 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The main risk is accidental dependency growth if declarations are later added without separating executable-only concerns.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_api.cpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_api.cpp

## Purpose

This file implements a lightweight API for interrogating mounted mergerfs instances through `.mergerfs` and `user.mergerfs.*` xattrs.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

It detects mounts via `.mergerfs`, reads all key/value settings through `fs::xattr::get`, and exposes basepath/relpath/fullpath/allpaths by reading fixed xattr names.

## State and Persistence Behavior

The file has 112 source lines and 2767 bytes. Its direct include set is: `mergerfs_api.hpp`, `fs_xattr.hpp`, `fs_exists.hpp`, `fs_lgetxattr.hpp`, `str.hpp`, `scope_guard/scope_guard.hpp`, `array`, `cstring`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

It depends on xattr availability and a 64 KiB buffer; tests should include missing xattrs, NUL-split allpaths, and non-mergerfs paths.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_api.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_api.hpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_api.hpp

## Purpose

This header declares the public `mergerfs::api` helpers for mount detection, config reads, and path mapping.

## Important APIs, Types, and Functions

types/namespaces: `api`, `mergerfs`

## Control Flow

Callers pass fs paths or strings and receive strings/vectors/maps filled from mergerfs control xattrs.

## State and Persistence Behavior

The file has 52 source lines and 1477 bytes. Its direct include set is: `fs_path.hpp`, `map`, `string`, `vector`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

It is used by diagnostic tools and should preserve errno-style negative return contracts.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_api.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_collect_info.cpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_collect_info.cpp

## Purpose

This diagnostic command gathers support information into `/tmp/mergerfs.info.txt`.

## Important APIs, Types, and Functions

functions: `mergerfs::collect_info::main`

## Control Flow

It appends command headers/output for version, uname, lsb_release, df, lsblk, mounts, branch stat data, mergerfs settings, fstab, container/Samba versions, lshw, and recent journal entries.

## State and Persistence Behavior

The file has 243 source lines and 5136 bytes. Its direct include set is: `mergerfs_collect_info.hpp`, `mergerfs_api.hpp`, `fs_mounts.hpp`, `fs_unlink.hpp`, `CLI11/CLI11.hpp`, `fmt/core.h`, `fmt/ranges.h`, `scope_guard/scope_guard.hpp`, `subprocess/subprocess.hpp`, `stdio.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The command has host-inspection and privacy implications; tests can mock subprocess failures and verify output sections are appended safely.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_collect_info.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_collect_info.hpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_collect_info.hpp

## Purpose

This header declares `mergerfs::collect_info::main`.

## Important APIs, Types, and Functions

types/namespaces: `collect_info`, `mergerfs`

## Control Flow

It lets `mergerfs.cpp` dispatch to the collect-info command based on argv[0].

## State and Persistence Behavior

The file has 29 source lines and 928 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The interface is simple argc/argv forwarding with no persistent state.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_collect_info.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_fsck.cpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_fsck.cpp

## Purpose

This command diagnoses and optionally repairs divergent branch copies visible through a mergerfs mount.

## Important APIs, Types, and Functions

types/namespaces: `FS`, `PathStat`, `stat`; functions: `mergerfs::fsck::main`

## Control Flow

It walks the mergerfs tree, obtains `allpaths` for each entry, compares mode/uid/gid/type/mtime and optional size, then can copy file content or apply owner/mode from a manually selected/newest/largest source.

## State and Persistence Behavior

The file has 467 source lines and 10697 bytes. Its direct include set is: `mergerfs_fsck.hpp`, `fs_close.hpp`, `fs_copyfile.hpp`, `fs_is_same_file.hpp`, `fs_lchmod.hpp`, `fs_lchown.hpp`, `fs_lgetxattr.hpp`, `fs_lstat.hpp`, `fs_open.hpp`, `mergerfs_api.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are destructive repairs, root permission requirements, xattr dependency, and type mismatches requiring manual intervention.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_fsck.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_fsck.hpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_fsck.hpp

## Purpose

This header declares `mergerfs::fsck::main` for executable dispatch.

## Important APIs, Types, and Functions

types/namespaces: `fsck`, `mergerfs`

## Control Flow

The command receives argc/argv from `mergerfs.cpp` when invoked as `fsck.mergerfs`.

## State and Persistence Behavior

The file has 27 source lines and 904 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Testing should focus on CLI parsing and repair mode selection at the implementation layer.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_fsck.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_ioctl.hpp -->
# sources/user-network-fs/mergerfs/src/mergerfs_ioctl.hpp

## Purpose

This header defines the mergerfs ioctl buffer contract.

## Important APIs, Types, and Functions

types/namespaces: `mergerfs_ioctl_t`

## Control Flow

`MERGERFS_IOCTL_BUF_SIZE` is 256 KiB and `mergerfs_ioctl_t` packs a version, size, and remaining char buffer for ioctl payloads.

## State and Persistence Behavior

The file has 45 source lines and 1383 bytes. Its direct include set is: `base_types.h`, `sys/ioctl.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Consumers must keep size/version validation strict because ioctl payloads cross process/kernel-facing boundaries.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/mergerfs_ioctl.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/num.cpp -->
# sources/user-network-fs/mergerfs/src/num.cpp

## Purpose

This file formats byte counts into exact binary unit strings.

## Important APIs, Types, and Functions

types/namespaces: `num`

## Control Flow

`num::humanize` returns raw bytes unless the value is evenly divisible by K, M, G, or T, choosing the largest exact unit.

## State and Persistence Behavior

The file has 54 source lines and 1544 bytes. Its direct include set is: `ef.hpp`, `num.hpp`, `fmt/core.h`, `inttypes.h`, `stdio.h`, `stdlib.h`, `time.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Tests should include boundary values, non-even sizes, zero, and TB-scale values.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/num.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/num.hpp -->
# sources/user-network-fs/mergerfs/src/num.hpp

## Purpose

This header declares `num::humanize(cu64)`.

## Important APIs, Types, and Functions

types/namespaces: `num`

## Control Flow

It is used by option/config reporting paths that need compact byte-unit strings.

## State and Persistence Behavior

The file has 29 source lines and 917 bytes. Its direct include set is: `base_types.h`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The API is stateless and returns a `std::string`.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/num.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/oom.cpp -->
# sources/user-network-fs/mergerfs/src/oom.cpp

## Purpose

This file adjusts the current process OOM killer score through `/proc/self/oom_score_adj`.

## Important APIs, Types, and Functions

functions: `oom::get_oom_score_adj`, `oom::has_oom_score_adj`, `oom::set_oom_score_adj`

## Control Flow

It checks for procfs support, reads the current score, and writes a formatted score value.

## State and Persistence Behavior

The file has 68 source lines and 1428 bytes. Its direct include set is: `oom.hpp`, `fs_exists.hpp`, `fmt/core.h`, `fstream`, `tuple`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are permission failures and errno after iostream errors; tests should use an injectable path or filesystem sandbox.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/oom.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/oom.hpp -->
# sources/user-network-fs/mergerfs/src/oom.hpp

## Purpose

This header declares OOM score helper functions.

## Important APIs, Types, and Functions

types/namespaces: `oom`

## Control Flow

It is integrated by `mergerfs.cpp` startup to reduce the daemon's OOM kill likelihood.

## State and Persistence Behavior

The file has 27 source lines and 937 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The interface has process-global side effects through procfs.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/oom.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/option_parser.cpp -->
# sources/user-network-fs/mergerfs/src/option_parser.cpp

## Purpose

This file converts command-line/libfuse options and non-option operands into global mergerfs configuration.

## Important APIs, Types, and Functions

types/namespaces: `fuse_opt`, `options`

## Control Flow

It uses `fuse_opt_parse`, feeds recognized key/value options to `cfg.set`, interprets branch and mountpoint operands, adds default FUSE options, derives fsname/subtype, validates mount loops, warns about unsupported overrides, and normalizes passthrough-related settings.

## State and Persistence Behavior

The file has 352 source lines and 8635 bytes. Its direct include set is: `config.hpp`, `ef.hpp`, `errno.hpp`, `fmt/core.h`, `fs_glob.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `hw_cpu.hpp`, `num.hpp`, `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State is global `cfg` and `fuse_cfg`; risks include operand ordering, passthrough/cache incompatibilities, and preserving unknown options for libfuse.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/option_parser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/option_parser.hpp -->
# sources/user-network-fs/mergerfs/src/option_parser.hpp

## Purpose

This header declares `options::parse(fuse_args*)`.

## Important APIs, Types, and Functions

types/namespaces: `options`

## Control Flow

The parser mutates global configuration and the libfuse argument vector in place.

## State and Persistence Behavior

The file has 28 source lines and 893 bytes. Its direct include set is: `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Tests should cover option retention/discard behavior and required branches/mountpoint errors.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/option_parser.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policies.cpp -->
# sources/user-network-fs/mergerfs/src/policies.cpp

## Purpose

This file instantiates all policy singleton objects and implements name lookup for action, create, and search categories.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

The `IFERT` macro lists every registered policy and `find` returns the matching singleton pointer or null.

## State and Persistence Behavior

The file has 136 source lines and 5481 bytes. Its direct include set is: `policies.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are registry drift when adding a policy and static initialization assumptions.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policies.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policies.hpp -->
# sources/user-network-fs/mergerfs/src/policies.hpp

## Purpose

This header centralizes policy class includes and declares the `Policies::{Action,Create,Search}` registries.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `Policies`, `Search`

## Control Flow

It exposes singleton instances and `find` functions for policy names configured by users.

## State and Persistence Behavior

The file has 125 source lines and 4320 bytes. Its direct include set is: `policy_all.hpp`, `policy_epall.hpp`, `policy_epff.hpp`, `policy_eplfs.hpp`, `policy_eplus.hpp`, `policy_epmfs.hpp`, `policy_eppfrd.hpp`, `policy_eprand.hpp`, `policy_erofs.hpp`, `policy_ff.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Integration is broad: option parsing stores selected policy implementations in `cfg.func.*`.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policies.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy.hpp -->
# sources/user-network-fs/mergerfs/src/policy.hpp

## Purpose

This header defines the abstract policy model used by branch-selection code.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `ActionImpl`, `Create`, `CreateImpl`, `Policy`, `Search`, `SearchImpl`

## Control Flow

`ActionImpl`, `CreateImpl`, and `SearchImpl` are virtual implementations; lightweight `Action`, `Create`, and `Search` wrappers hold raw singleton pointers, forward calls, expose names, and for create expose `path_preserving`.

## State and Persistence Behavior

The file has 197 source lines and 3785 bytes. Its direct include set is: `branches.hpp`, `strvec.hpp`, `fs_path.hpp`, `string`, `memory`, `vector`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Null wrappers can be converted to false but most callers assume configured non-null implementations.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_all.cpp -->
# sources/user-network-fs/mergerfs/src/policy_all.cpp

## Purpose

`policy_all.cpp` implements the `all` branch-selection policy. It select all writable non-no-create branches for creation, and delegates action/search to epall so existing-path operations touch every branch copy.

## Important APIs, Types, and Functions

The file implements `Policy::All::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 85 source lines and 2482 bytes. Its direct include set is: `policy_all.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `policy.hpp`, `policies.hpp`, `policy_error.hpp`, `strvec.hpp`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_all.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_all.hpp -->
# sources/user-network-fs/mergerfs/src/policy_all.hpp

## Purpose

This header declares the `all` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `All`, `Create`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy select all writable non-no-create branches for creation, and delegates action/search to epall so existing-path operations touch every branch copy.

## State and Persistence Behavior

The file has 67 source lines and 1812 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_all.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epall.cpp -->
# sources/user-network-fs/mergerfs/src/policy_epall.cpp

## Purpose

`policy_epall.cpp` implements the `epall` branch-selection policy. It existing-path all: action/create/search only include branches where the path already exists; create additionally enforces writable, non-NC, min-free-space checks.

## Important APIs, Types, and Functions

The file implements `Policy::EPAll::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 142 source lines and 3603 bytes. Its direct include set is: `policy_epall.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_epall.hpp`, `policy_error.hpp`, `strvec.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epall.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epall.hpp -->
# sources/user-network-fs/mergerfs/src/policy_epall.hpp

## Purpose

This header declares the `epall` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPAll`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path all: action/create/search only include branches where the path already exists; create additionally enforces writable, non-NC, min-free-space checks.

## State and Persistence Behavior

The file has 70 source lines and 1840 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epall.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epff.cpp -->
# sources/user-network-fs/mergerfs/src/policy_epff.cpp

## Purpose

`policy_epff.cpp` implements the `epff` branch-selection policy. It existing-path first-found: choose the first branch where the path exists and passes the relevant writability checks.

## Important APIs, Types, and Functions

The file implements `Policy::EPFF::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 140 source lines and 3547 bytes. Its direct include set is: `policy_epff.hpp`, `branches.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_error.hpp`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epff.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epff.hpp -->
# sources/user-network-fs/mergerfs/src/policy_epff.hpp

## Purpose

This header declares the `epff` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPFF`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path first-found: choose the first branch where the path exists and passes the relevant writability checks.

## State and Persistence Behavior

The file has 67 source lines and 1815 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epff.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplfs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_eplfs.cpp

## Purpose

`policy_eplfs.cpp` implements the `eplfs` branch-selection policy. It existing-path least-free-space: among existing copies, choose the branch with the smallest available space that still passes create/action constraints.

## Important APIs, Types, and Functions

The file implements `Policy::EPLFS::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 177 source lines and 4318 bytes. Its direct include set is: `policy_eplfs.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policies.hpp`, `policy.hpp`, `policy_error.hpp`, `limits`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplfs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_eplfs.hpp

## Purpose

This header declares the `eplfs` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPLFS`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path least-free-space: among existing copies, choose the branch with the smallest available space that still passes create/action constraints.

## State and Persistence Behavior

The file has 67 source lines and 1819 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplus.cpp -->
# sources/user-network-fs/mergerfs/src/policy_eplus.cpp

## Purpose

`policy_eplus.cpp` implements the `eplus` branch-selection policy. It existing-path least-used-space: among existing copies, choose the branch with the smallest used-space value.

## Important APIs, Types, and Functions

The file implements `Policy::EPLUS::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 173 source lines and 4248 bytes. Its direct include set is: `policy_eplus.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_error.hpp`, `limits`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplus.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplus.hpp -->
# sources/user-network-fs/mergerfs/src/policy_eplus.hpp

## Purpose

This header declares the `eplus` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPLUS`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path least-used-space: among existing copies, choose the branch with the smallest used-space value.

## State and Persistence Behavior

The file has 67 source lines and 1819 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eplus.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epmfs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_epmfs.cpp

## Purpose

`policy_epmfs.cpp` implements the `epmfs` branch-selection policy. It existing-path most-free-space: among existing copies, choose the branch with the greatest available space.

## Important APIs, Types, and Functions

The file implements `Policy::EPMFS::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 175 source lines and 4259 bytes. Its direct include set is: `policy_epmfs.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_epmfs.hpp`, `policy_error.hpp`, `limits`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epmfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epmfs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_epmfs.hpp

## Purpose

This header declares the `epmfs` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPMFS`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path most-free-space: among existing copies, choose the branch with the greatest available space.

## State and Persistence Behavior

The file has 70 source lines and 1840 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_epmfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eppfrd.cpp -->
# sources/user-network-fs/mergerfs/src/policy_eppfrd.cpp

## Purpose

`policy_eppfrd.cpp` implements the `eppfrd` branch-selection policy. It existing-path proportional free random distribution: weight eligible existing branches by available space and randomly choose one.

## Important APIs, Types, and Functions

The file implements `Policy::EPPFRD::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector. Random policies then reduce the eligible set through `RND` helpers.

## State and Persistence Behavior

The file has 251 source lines and 5867 bytes. Its direct include set is: `policy_eppfrd.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_error.hpp`, `rnd.hpp`, `strvec.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eppfrd.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eppfrd.hpp -->
# sources/user-network-fs/mergerfs/src/policy_eppfrd.hpp

## Purpose

This header declares the `eppfrd` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPPFRD`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path proportional free random distribution: weight eligible existing branches by available space and randomly choose one.

## State and Persistence Behavior

The file has 67 source lines and 1823 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eppfrd.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eprand.cpp -->
# sources/user-network-fs/mergerfs/src/policy_eprand.cpp

## Purpose

`policy_eprand.cpp` implements the `eprand` branch-selection policy. It existing-path random: delegate to epall then shrink the result to a random eligible branch.

## Important APIs, Types, and Functions

The file implements `Policy::EPRand::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector. Random policies then reduce the eligible set through `RND` helpers.

## State and Persistence Behavior

The file has 69 source lines and 2010 bytes. Its direct include set is: `policy_eprand.hpp`, `errno.hpp`, `policies.hpp`, `policy.hpp`, `policy_eprand.hpp`, `rnd.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eprand.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eprand.hpp -->
# sources/user-network-fs/mergerfs/src/policy_eprand.hpp

## Purpose

This header declares the `eprand` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPRand`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path random: delegate to epall then shrink the result to a random eligible branch.

## State and Persistence Behavior

The file has 67 source lines and 1823 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_eprand.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_erofs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_erofs.cpp

## Purpose

`policy_erofs.cpp` implements the `erofs` branch-selection policy. It error read-only filesystem: every policy category fails with -EROFS.

## Important APIs, Types, and Functions

The file implements `Policy::ERoFS::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 49 source lines and 1586 bytes. Its direct include set is: `policy_erofs.hpp`, `errno.hpp`, `policy.hpp`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_erofs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_erofs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_erofs.hpp

## Purpose

This header declares the `erofs` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `ERoFS`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy error read-only filesystem: every policy category fails with -EROFS.

## State and Persistence Behavior

The file has 67 source lines and 1820 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_erofs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_error.hpp -->
# sources/user-network-fs/mergerfs/src/policy_error.hpp

## Purpose

This header defines shared policy error-priority logic.

## Important APIs, Types, and Functions

types/namespaces: `policy`

## Control Flow

`error_and_continue` updates the current error and continues; `calc_error` lets ENOENT be replaced by more specific ENOSPC/EROFS and lets later higher-priority errors win.

## State and Persistence Behavior

The file has 51 source lines and 1417 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Policy tests should verify returned errors when all branches fail for mixed missing, no-space, and read-only causes.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_error.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_ff.cpp -->
# sources/user-network-fs/mergerfs/src/policy_ff.cpp

## Purpose

`policy_ff.cpp` implements the `ff` branch-selection policy. It first-found: create/search choose the first usable branch, while action delegates to epff for existing-path mutation.

## Important APIs, Types, and Functions

The file implements `Policy::FF::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 94 source lines and 2518 bytes. Its direct include set is: `policy_ff.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `policies.hpp`, `policy.hpp`, `policy_error.hpp`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_ff.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_ff.hpp -->
# sources/user-network-fs/mergerfs/src/policy_ff.hpp

## Purpose

This header declares the `ff` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `FF`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy first-found: create/search choose the first usable branch, while action delegates to epff for existing-path mutation.

## State and Persistence Behavior

The file has 68 source lines and 1809 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_ff.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lfs.cpp -->
# sources/user-network-fs/mergerfs/src/policy_lfs.cpp

## Purpose

`policy_lfs.cpp` implements the `lfs` branch-selection policy. It least-free-space: create can choose any writable branch with the lowest free space; action/search delegate to eplfs.

## Important APIs, Types, and Functions

The file implements `Policy::LFS::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 96 source lines and 2644 bytes. Its direct include set is: `policy_lfs.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `policies.hpp`, `policy.hpp`, `policy_error.hpp`, `strvec.hpp`, `limits`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lfs.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lfs.hpp -->
# sources/user-network-fs/mergerfs/src/policy_lfs.hpp

## Purpose

This header declares the `lfs` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `LFS`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy least-free-space: create can choose any writable branch with the lowest free space; action/search delegate to eplfs.

## State and Persistence Behavior

The file has 67 source lines and 1808 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lfs.hpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lup.cpp -->
# sources/user-network-fs/mergerfs/src/policy_lup.cpp

## Purpose

`policy_lup.cpp` implements the `lup` branch-selection policy. It least-used-percent: choose the branch with the lowest used/total ratio, avoiding floating division by cross-multiplying totals.

## Important APIs, Types, and Functions

The file implements `Policy::LUP::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 245 source lines and 5498 bytes. Its direct include set is: `policy_lup.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `policies.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_error.hpp`, `base_types.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/policy_lup.cpp -->
