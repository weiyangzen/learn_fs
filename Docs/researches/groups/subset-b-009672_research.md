# subset-b-009672 research

Grouped research for mergerfs test and preload support files. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/tests.cpp -->
# sources/user-network-fs/mergerfs/tests/tests.cpp

## Purpose

This file is the main acutest-based C++ unit and stress test harness for several mergerfs support libraries. It is not focused on one FUSE operation; it validates low-level behavior that the filesystem runtime depends on: configuration value parsing, branch list mutation semantics, inode calculation, string and numeric helpers, random utilities, thread-pool scheduling, copyfile behavior, hash-set de-duplication, and rmdir error aggregation.

The test list at the bottom registers every test with acutest through `TEST_LIST`. That registration makes this file the integration point between the build/test runner and the support modules included from `config.hpp`, `fs_copyfile.hpp`, `fs_inode.hpp`, `from_string.hpp`, `hashset.hpp`, `num.hpp`, `rnd.hpp`, `str.hpp`, `thread_pool.hpp`, and vendored `rapidhash/rapidhash.h`.

## Important APIs, types, and functions

`wait_until` is a small polling helper for asynchronous tests. It repeatedly evaluates a predicate for up to a millisecond-based timeout and is used in thread-pool tests where work execution, queue pressure, or resizer threads need deterministic completion signals without fixed long sleeps.

The config tests exercise `ConfigBOOL`, `ConfigU64`, `ConfigINT`, `ConfigSTR`, `CacheFiles`, `InodeCalc`, `MoveOnENOSPC`, `NFSOpenHack`, `StatFS`, `StatFSIgnore`, `XAttr`, and the aggregate `Config` registry. The tested API shape is consistently `from_string`, `to_string`, comparison operators, `Config::set`, `Config::get`, `Config::has_key`, `Config::get_map`, `Config::from_stream`, `Config::from_file`, `Config::finish_initializing`, xattr-list helpers, and static recognizers/pruners for control and command xattrs.

The branch tests cover `Branch`, `Branches`, `Branches::Impl`, and `SrcMounts`. They validate branch modes `RW`, `RO`, and `NC`; per-branch and global `minfreespace`; copy and move behavior; copy-on-write snapshots through `Branches::Ptr`; string serialization; instruction prefixes for set/add/erase; fnmatch-based deletion; and path parsing where `=` may appear in the path and the last `=` is the option separator.

The inode tests use `fs::inode::set_algo`, `fs::inode::get_algo`, `fs::inode::calc`, and `fs::inode::ReaddirCalc`. The tested algorithms are `passthrough`, `path-hash`, `path-hash32`, `devino-hash`, `devino-hash32`, `hybrid-hash`, and `hybrid-hash32`.

The thread-pool tests exercise `ThreadPool` construction, `ptoken`, `enqueue_work`, token-aware enqueue, `try_enqueue_work`, `try_enqueue_work_for`, `enqueue_task`, `threads`, `add_thread`, `remove_thread`, and `set_threads`. They use `std::atomic`, `std::future`, producer threads, queue saturation, and repeated resize/churn scenarios to validate concurrency behavior.

Other targeted APIs include `fs::copyfile`, `HashSet::put`, `HashSet::size`, `str::split`, `split_to_set`, `split_on_null`, `lsplit1`, `rsplit1`, `splitkv`, `join`, prefix/suffix helpers, trimming, replacement, fnmatch erasure, `str::from` numeric parsing, `num::humanize`, `RND::rand64`, `RND::shrink_to_rand_elem`, and `rapidhash_withSeed`/`rapidhashNano_withSeed`/`rapidhashMicro_withSeed`.

`RmdirErr` is a local test replica of rmdir error-reduction behavior. It stores the first result in an `std::optional<int>`, defaults to `-ENOENT` if no branch returned a result, gives `-EEXIST` and `-ENOTEMPTY` priority, lets success replace generic errors, and prevents generic errors or success from overwriting priority errors.

## Control flow

The file is organized as independent `void test_*()` functions. Most tests construct a small object, mutate it through its public API, and assert exact return codes and serialized values with `TEST_CHECK`. The test runner invokes registered functions from `TEST_LIST`.

Configuration control flow is primarily round-trip oriented: parse a string, assert internal enum/value state through equality or getters, serialize back, and assert invalid inputs return negative errno values such as `-EINVAL`, `-EOVERFLOW`, `-ENOATTR`, `-EROFS`, or `-ERANGE`. `Config::from_stream` tests demonstrate partial progress: valid lines are applied even when a bad key causes an overall error and records diagnostics in `cfg.errs`.

Branch mutation tests model an instruction language. A bare string or `=` replaces the branch list, `+` and `+>` append, `+<` prepends, `->` removes the last branch, `-<` removes the first branch, and `-pattern` removes fnmatch matches. Several tests explicitly verify atomic failure: if one path in a multi-path add or set is invalid, the previous branch list remains unchanged.

Thread-pool control flow ranges from simple enqueue-and-wait tests to stress tests with concurrent producers and resizers. Queue backpressure tests deliberately occupy the only worker and fill a depth-one queue, then assert non-blocking enqueue fails, timed enqueue times out, and blocking enqueue waits until a slot opens. Destructor behavior is covered by queuing work inside a scope and asserting all queued work completed after the pool is destroyed.

`fs::copyfile` tests create temporary directories under `/tmp`, open source files with POSIX APIs, write sparse endpoints, call `fs::copyfile`, then verify size and boundary bytes. The mutation test updates source timestamps concurrently during copy and then checks that cleanup removed temporary destination-prefixed files.

## State and persistence behavior

Most tests are in-memory, but they cover state that controls live filesystem behavior. `Config` owns a map of mutable/readonly runtime options; tests verify key normalization between underscores and hyphens for `get`/`set`, readonly enforcement before and after initialization, alias behavior for remember/noforget options through global `fuse_cfg.remember_nodes`, and xattr-form key enumeration as NUL-separated `user.mergerfs.*` strings.

`Branches` state is copy-on-write through pointer snapshots. Tests ensure each mutation produces a new implementation pointer while old snapshots remain unchanged. The most sensitive persistence-like behavior is the relation between a branch's `_minfreespace` variant and the containing `Branches::Impl` default: copy and move assignment must relink pointer-backed branch defaults to the destination impl's default, not leave dangling or cross-linked pointers.

Thread-pool tests validate live concurrent state: worker count, queue occupancy, producer tokens, futures, resize operations, exception handling, and destructor draining. These tests are important because regressions can produce hangs rather than clean assertion failures.

Filesystem state appears in the copyfile tests only. Temporary files are created with `mkdtemp`, source files are truncated and written, destinations are inspected with `stat`/`pread`, and all test directories are removed with `std::filesystem::remove_all`. The cleanup test also treats leftover hidden temporary files as a failure signal.

## Dependencies and integration points

The file integrates with the acutest framework through `acutest/acutest.h` and `TEST_LIST`. It depends on mergerfs internal headers for configuration, inode, string, numeric, random, hash-set, copyfile, and thread-pool behavior. It also uses POSIX headers and syscalls (`open`, `ftruncate`, `pwrite`, `pread`, `stat`, `fstat`, `utimensat`, `mkdtemp`, `close`) plus C++ standard library concurrency, filesystem, stream, and container facilities.

The config tests are directly tied to runtime control surfaces: config file parsing, runtime xattrs, mutable and readonly mount options, branch lists, and FUSE node-remember behavior. The inode tests connect to directory listing and stable inode reporting. The thread-pool tests connect to any mergerfs subsystem using pooled work, especially where runtime resizing is exposed through configuration. The copyfile tests connect to clone/copy fallback behavior used when moving or materializing data across branches.

## Risks and edge cases

Branch parsing is a high-risk area. The tests document strict uppercase mode parsing, byte/K/M/G/T suffix behavior, rejection of negative and overflowing minfreespace, support for lowercase size suffixes, preservation of paths containing `=`, atomic failure semantics, and the fact that empty string and `=` both clear the list.

Global and per-branch `minfreespace` ownership is subtle. Pointer-backed branches intentionally track a global default live, copied pointer-backed `Branch` instances share the pointer, and `Branches::Impl` assignment must relink default pointers. A regression here could corrupt runtime branch free-space policy or leave stale pointers.

Thread-pool tests expose deadlock and race risks: blocking enqueue under full queues, timed enqueue duration, exceptions from worker functions including non-`std::exception` throws, concurrent enqueue with resize, add/remove churn, destructor draining, FIFO ordering with one worker, and move-only callables passed through futures.

Config risks include alias drift, inconsistent underscore normalization, readonly enforcement mistakes, xattr buffer sizing and `-ERANGE` handling, partial config-file error reporting, and global `fuse_cfg` side effects. Tests restore `fuse_cfg.remember_nodes` after mutation, but failures before restoration would affect later tests.

File-copy tests rely on `/tmp`, sparse file support, timestamp mutation, and cleanup of temporary files. They can be more environment-sensitive than pure unit tests. Thread stress tests also use timing and may be sensitive on heavily loaded systems, though `wait_until` reduces fixed-sleep flakiness.

## Test signals

Primary signals are exact acutest assertions: return codes, serialized strings, enum equality, preserved values after invalid writes, expected errors for missing/unknown keys, exact thread counts, nonzero and unique worker ids, future values or propagated exceptions, queue-full failures, timeout lower bounds, total executed work counters, absence of leftover copy temporary files, hash-set duplicate return values, and deterministic hash equality against `rapidhash_internal`.

The breadth of `TEST_LIST` is itself a signal: if a new helper or option is added without registration, it will not run. The registered names also provide a useful map from failing test output back to a subsystem: `branches_*`, `config_*`, `tp_*`, `fs_inode_*`, `fs_copyfile_*`, `hashset_*`, `str_*`, `rnd_*`, and `rapidhash_*`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tests/tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/tools/preload.c -->
# sources/user-network-fs/mergerfs/tools/preload.c

## Purpose

This file implements a small LD_PRELOAD-style interposer that transparently redirects regular-file opens from the mergerfs mount path to the underlying branch file path. It opens the requested path normally first, asks mergerfs for the backing path through the `user.mergerfs.fullpath` extended attribute, and, when available, reopens the backing file directly. The result is a file descriptor or `FILE*` that bypasses the FUSE layer for subsequent I/O while preserving fallback behavior for unsupported paths or failures.

The interposed entry points are `open`, `open64`, `openat`, `openat64`, `fopen`, `fopen64`, `creat`, and `creat64`. The non-64 variants are compiled only when `_FILE_OFFSET_BITS` is not defined, avoiding duplicate symbol conflicts in large-file builds where libc may map the base names to 64-bit variants.

## Important APIs, types, and functions

`LOAD_FUNC(func)` lazily resolves the next libc symbol with `dlsym(RTLD_NEXT, #func)` and stores it in a static function pointer such as `_libc_open`, `_libc_open64`, `_libc_fopen`, or `_libc_creat64`. It asserts that resolution succeeded, so preload initialization or symbol mismatches fail loudly in debug/runtime assertion-enabled builds.

`get_underlying_filepath` calls `fgetxattr(fd, "user.mergerfs.fullpath", filepath, filepath_size)` and returns the byte count or `-1`. On Linux it includes `<sys/xattr.h>`; on FreeBSD it includes `<sys/extattr.h>`, although the function body still uses the Linux-style `fgetxattr` name. The requested buffer is typically `PATH_MAX`.

`strip_exec` copies an `fopen` mode string while removing any `x` characters. This matters because the original `fopen` may have used exclusive creation mode against the mergerfs path; the second open is against the already-created backing path and should not fail solely because exclusive creation is still present.

The file declares an `IOCTL_BUF`, `IOCTL_APP_TYPE`, and `IOCTL_FILE_INFO`, but these ioctl definitions are unused in the current implementation. The active path discovery mechanism is the mergerfs fullpath xattr.

## Control flow

The `open` and `open64` wrappers follow the same sequence. They resolve libc, extract a variadic `mode_t` when `O_CREAT` or `O_TMPFILE` is present, and call the real libc open on the user path. If the first open fails, the wrapper returns `-1`. If the flags indicate `O_DIRECTORY`, `O_PATH`, or `O_TMPFILE`, the original descriptor is returned immediately. Otherwise the wrapper `fstat`s the descriptor, requires a regular file, asks for `user.mergerfs.fullpath`, clears `O_EXCL` and `O_CREAT`, and opens the real path through libc. If the second open succeeds, it closes the original FUSE descriptor and returns the backing descriptor; if any step fails, it returns the original descriptor.

`openat` and `openat64` mirror the same logic but call `_libc_openat`/`_libc_openat64`. They pass the original `dirfd` to the second `openat` call even when `real_pathname` is populated from an xattr and is expected to be an absolute backing path. If `real_pathname` is absolute this is harmless because `dirfd` is ignored; if it is relative, behavior depends on the caller's directory file descriptor.

`fopen` and `fopen64` open the requested stream normally, get its file descriptor with `fileno`, require a regular file, obtain the fullpath xattr, strip `x` from the original mode string, and open a new stream directly on the underlying path. On success they `fclose` the original stream and return the backing stream; on failure they return the original stream. They do not filter directory-like flags because `fopen` modes target stream files.

`creat` and `creat64` call the libc creation function first, request the underlying fullpath xattr on the returned descriptor, then call libc `creat` again on the underlying path. On success they close the original descriptor and return the backing descriptor. On xattr or second-open failure they return the original descriptor.

## State and persistence behavior

The only persistent process state is the set of static libc function pointers cached after first resolution. The wrappers do not maintain per-file metadata, caches, or locks. They operate entirely on the file descriptor or stream returned by the first libc call and the backing path returned by mergerfs.

Filesystem state can be changed before redirection completes. For creation paths, the original `open`/`creat` against mergerfs may create the file or choose a branch according to mergerfs policy. The second open clears creation and exclusive flags for `open*`, or recreates/truncates through `creat*`, against the backing path. If the second open fails, the caller still receives the original mergerfs descriptor, preserving the visible operation. If the second open succeeds, subsequent I/O is direct to the branch file.

The wrappers deliberately skip `O_TMPFILE`, `O_DIRECTORY`, and `O_PATH` descriptors because they are not normal pathname-backed regular file handles suitable for fullpath redirection. They also skip any descriptor whose `fstat` does not report `S_IFREG`.

## Dependencies and integration points

The preload object depends on dynamic linking (`dlfcn.h`, `RTLD_NEXT`), POSIX file APIs (`open`, `openat`, `creat`, `close`, `fstat`, `fileno`, `fopen`, `fclose`), variadic mode handling, extended attributes, `PATH_MAX`, and standard file status bits. It also relies on mergerfs exposing the `user.mergerfs.fullpath` xattr for opened files.

The integration point is external to mergerfs proper: applications load this object with the dynamic loader so libc file-opening calls are intercepted. Mergerfs still makes initial policy decisions for file creation and path resolution, but the final descriptor can bypass FUSE for read/write I/O. This makes correctness dependent on the runtime config for xattr support and on the kernel/libc symbol names available on the target platform.

## Risks and edge cases

The wrappers use `assert` after `dlsym`; if assertions are disabled, a failed symbol lookup would leave a null function pointer and likely crash when called. There is no synchronization around lazy function-pointer initialization; concurrent first calls may race to write the same pointer, which is usually benign but not formally protected.

`fgetxattr` does not guarantee NUL termination when the value exactly fills the buffer. The code passes `real_pathname` directly to libc open functions without explicitly appending `'\0'` based on the returned byte count. Correctness depends on mergerfs returning a NUL-terminated path or a path shorter than `PATH_MAX` with existing zeroed stack contents, but the stack buffer is not initialized.

`strip_exec` writes into a fixed 64-byte buffer without bounding against unusually long mode strings. Normal `fopen` mode strings are tiny, but a malicious or accidental long mode string could overflow `new_mode`.

For `open*`, the second open removes `O_CREAT` and `O_EXCL` but preserves other flags such as `O_TRUNC`, `O_APPEND`, `O_CLOEXEC`, and access mode. Preserving `O_TRUNC` means a created file may be truncated again on the backing path; normally this is equivalent, but it matters for races. For `creat*`, the backing `creat` also truncates. The gap between original and backing opens can expose races if another process renames, removes, or changes the file.

The FreeBSD include branch is incomplete-looking because it includes `<sys/extattr.h>` but calls `fgetxattr`, and `O_PATH` may not exist on non-Linux platforms. The file defines `O_TMPFILE` to zero on FreeBSD, but not `O_PATH`, so portability depends on platform headers or build flags.

`openat*` passes `dirfd_` for the second open. This is safe for absolute backing paths but could be surprising if the xattr value is relative. The unused ioctl declarations suggest either a previous or planned fullpath lookup method and should not be mistaken for active behavior.

## Test signals

This file has no direct tests in the same source. Useful test signals would include an LD_PRELOAD integration test that opens regular files through a mergerfs mount and verifies `/proc/self/fd/<fd>` or equivalent resolves to a branch path; fallback tests where the xattr is unavailable; creation tests for `O_CREAT`, `O_EXCL`, `O_TRUNC`, `creat`, and `fopen` modes containing `x`; and negative tests for directories, `O_PATH`, `O_TMPFILE`, non-regular files, and paths longer than or equal to `PATH_MAX`.

Because the code is failure-tolerant by design, tests should verify both success redirection and exact fallback behavior. The most important safety signals are no descriptor leaks when the second open succeeds, no close of the original descriptor when the second open fails, correct propagation of libc `errno` for initial failures, and correct behavior when `user.mergerfs.fullpath` is missing or disabled by xattr configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/tools/preload.c -->
