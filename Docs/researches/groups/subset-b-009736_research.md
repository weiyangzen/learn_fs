# Research: subset-b-009736

Grouped research for the requested pyfuse3 and rclone source files. Each section preserves the original source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/tmpfs.py -->
# sources/user-network-fs/pyfuse3/examples/tmpfs.py

Purpose: Implements a complete in-memory example filesystem for pyfuse3, backed by an in-memory SQLite database. It demonstrates async FUSE operation handlers, inode metadata management, directory contents, file IO, symlinks, links, renames, truncation, statfs, and mount lifecycle.

Important APIs/types/functions: `Operations(pyfuse3.Operations)` is the main filesystem implementation. `init_tables` creates `inodes` and `contents` tables and the root inode. `get_row` enforces one-row SQL lookups. FUSE handlers include `lookup`, `getattr`, `readlink`, `opendir`, `readdir`, `unlink`, `rmdir`, `symlink`, `rename`, `link`, `setattr`, `mknod`, `mkdir`, `statfs`, `open`, `access`, `create`, `read`, `write`, and `release`. `NoUniqueValueError` and `NoSuchRowError` model internal SQL lookup failures. `parse_args` and the `__main__` block initialize logging, options, `pyfuse3.init`, `trio.run(pyfuse3.main)`, and `pyfuse3.close`.

Control flow: FUSE lookups read directory entries from `contents` and then call `getattr` to return `EntryAttributes`. Creation inserts a new inode and a directory entry, returning attributes. Removal deletes the directory entry and deletes the inode only when the link count is one and the inode is not open. Rename either updates a directory row or delegates replacement to `_replace`. Reads and writes use the file handle as the inode id and update/read the `data` blob. `release` decrements open counts and performs deferred inode deletion for unlinked but still-open files.

State and persistence: All data lives in `sqlite3.connect(':memory:')`, so it is process-local and non-persistent. Metadata is split between `inodes` rows and `contents` directory rows. `inode_open_count` tracks open handles for deferred deletion. The code does not maintain kernel lookup counts, generation numbers, or normal atime/mtime/ctime updates beyond explicit `setattr` and create-time initialization.

Dependencies and integration points: Depends on `trio`, `pyfuse3`, `sqlite3`, POSIX `errno/stat/os`, and pyfuse3 C extension types. It integrates with pyfuse3 through subclassed async operation handlers and uses `pyfuse3.readdir_reply`, `FileInfo`, `EntryAttributes`, and `StatvfsData`.

Risks: This is deliberately simple and unsuitable for significant data. Directory emptiness checks count all children, including the root's `..` row pattern; link count behavior is approximate. Write slicing does not fill sparse holes if `off` is beyond current data. SQLite writes are not explicitly committed, relying on connection behavior. It discards nonzero rename flags and does not implement permissions in `access`.

Test signals: `test/test_examples.py::test_tmpfs` mounts this example and exercises writes, mkdir, symlink, mknod, chown, chmod, utimens, rounding, links, rename, readdir, statvfs, truncation, and unlink while-open behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/examples/tmpfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/pyproject.toml -->
# sources/user-network-fs/pyfuse3/pyproject.toml

Purpose: Defines pyfuse3 packaging, build backend, runtime and development dependencies, package discovery, included package data, and static-analysis configuration.

Important APIs/types/functions: The `[build-system]` uses `setuptools>=78.1.1`, `setuptools_scm>=8.0`, `Cython`, and custom backend `build_backend` from `util`. `[project]` declares the distribution metadata and dynamic version. `[dependency-groups].dev` lists pyright, mypy, pytest, pytest-trio, ruff, sphinx, and twine. Tool sections configure setuptools, ruff/isort, mypy, pyright, codespell, and ruff formatting.

Control flow: Build frontends load `util/build_backend.py` through `backend-path`. Setuptools discovers packages under `src` and includes `pyfuse3/py.typed`. Versioning is delegated to setuptools-scm.

State and persistence: No runtime state; the file persists build and lint policy. It affects generated wheels/sdists and type-check/lint behavior across the project.

Dependencies and integration points: Integrates with the Python packaging ecosystem, Cython extension build, setuptools-scm, and type/lint tools. Runtime requires Python `>=3.10` and `trio >= 0.15`.

Risks: Build success depends on custom backend logic and system `pkg-config`/libfuse availability outside this file. Mypy and pyright exclude `util/` and `rst/conf.py`, so those files rely on runtime/testing more than type checks.

Test signals: Indirectly exercised by package builds, editable installs, and CI lint/type jobs. The configured dev dependencies are the tools expected for local validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/rst/conf.py -->
# sources/user-network-fs/pyfuse3/rst/conf.py

Purpose: Sphinx configuration for pyfuse3 documentation. It configures autodoc, intersphinx, nitpicky reference checking, project metadata, HTML output, and a workaround for Sphinx 9 native type-stub autodoc behavior.

Important APIs/types/functions: Sets `SPHINX_AUTODOC_IGNORE_NATIVE_MODULE_TYPE_STUBS=1`, enables `sphinx.ext.autodoc` and `sphinx.ext.intersphinx`, maps Python and Trio docs, sets `nitpicky=True`, derives `version`/`release` from `importlib.metadata.version('pyfuse3')`, and defines HTML theme/static behavior.

Control flow: Sphinx executes this file at doc-build startup. Environment setup occurs before extension loading. Version detection falls back to `dev` if the package is unavailable.

State and persistence: Persists documentation policy only. Build-time state is limited to environment variable initialization and module-level Sphinx settings.

Dependencies and integration points: Depends on Sphinx and a built/installable pyfuse3 package for accurate autodoc. Intersphinx links integrate with Python and Trio documentation. `make_release.py` builds docs with `sphinx-build -W`.

Risks: `nitpicky=True` makes unresolved references fatal in strict builds. Autodoc depends on the compiled extension being importable, so doc builds can fail on systems without a successful native build.

Test signals: Release automation invokes Sphinx with warnings as errors. There are no direct unit tests for this config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/rst/conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/_pyfuse3.py -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/_pyfuse3.py

Purpose: Provides the pure-Python part of pyfuse3: version discovery, public integer/bytes type aliases, an `async_wrapper` for Cython async functions passed to Trio, and the base `Operations` contract for filesystem implementations.

Important APIs/types/functions: Exports `Operations` and `async_wrapper`. Defines aliases `FileHandleT`, `FileNameT`, `FlagT`, `InodeT`, `ModeT`, and `XAttrNameT`. `Operations` exposes capability flags `supports_dot_lookup`, `enable_writeback_cache`, and `enable_acl`. Operation methods document and default to `FUSEError(errno.ENOSYS)` for lookup, getattr, setattr, readlink, create/remove/link/rename, open/read/write/flush/release/fsync, poll, opendir/readdir/releasedir/fsyncdir, statfs, xattrs, access, and create. `init`, `forget`, and `stacktrace` have non-request semantics.

Control flow: Filesystem authors subclass `Operations` and override only supported handlers. The native pyfuse3 layer dispatches kernel FUSE requests into these async methods. If a default handler raises `ENOSYS`, the FUSE kernel may stop calling that request type and use fallback behavior where available. `stacktrace` is triggered by a debug extended attribute and logs Python thread stacks.

State and persistence: The base class stores no per-instance state. It defines behavioral defaults and documentation for how implementers should manage kernel lookup counts, inode lifetime, write semantics, xattr errors, and cache invalidation.

Dependencies and integration points: Depends on `errno`, `logging`, importlib metadata, and types injected by the compiled extension. It is central to examples/tests because user filesystems subclass it.

Risks: Misimplementing the documented lookup-count and deferred-deletion contracts can cause stale inode exposure or premature deletion. The `TYPE_CHECKING` split means runtime names such as `FUSEError` are injected externally; import order and extension initialization matter.

Test signals: `test_fs.py` subclasses `pyfuse3.Operations`; `tmpfs.py` and example files rely on these contracts. API tests verify extension-level objects and copy behavior, not every default method.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/_pyfuse3.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/asyncio.py -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/asyncio.py

Purpose: Provides an asyncio compatibility shim that makes pyfuse3's internals see an object shaped enough like Trio for asyncio-based operation loops.

Important APIs/types/functions: `enable` replaces `pyfuse3.trio` with this module and aliases `lowlevel`/`from_thread`. `disable` restores real Trio. `Lock` aliases `asyncio.Lock`. `wait_readable`, `notify_closing`, `current_task`, `_Nursery`, and `open_nursery` emulate the subset of Trio low-level APIs that pyfuse3 uses.

Control flow: `wait_readable` registers a loop reader for a file descriptor, waits on a future, removes the reader on completion, and tracks waiters in `_read_futures`. `notify_closing` fails outstanding futures with `ClosedResourceError`. `_Nursery` collects tasks created by `start_soon` and waits for all on context exit.

State and persistence: `_read_futures` is process-global fd-to-future-set state. `_Nursery.tasks` is per-context state. No data persists beyond process lifetime.

Dependencies and integration points: Depends on `asyncio`, `sys`, and pyfuse3's `trio` module variable. Example `hello_asyncio.py` and users can switch pyfuse3 to asyncio mode.

Risks: This is a compatibility subset, not a full Trio implementation. `_Nursery.__aexit__` waits for task completion but does not implement Trio-like cancellation semantics. `notify_closing` indexes `_read_futures[fd]`, which creates an empty set for unknown fds.

Test signals: `test_examples.py` parametrizes `hello.py` and `hello_asyncio.py`, giving end-to-end coverage that the shim can run a mounted example.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/asyncio.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.c -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.c

Purpose: Implements a POSIX-semaphore compatibility layer for Darwin using pthread mutexes and condition variables, because unnamed POSIX semaphores are not available the same way on macOS.

Important APIs/types/functions: Implements `darwin_sem_init`, `darwin_sem_destroy`, `darwin_sem_getvalue`, `darwin_sem_post`, `darwin_sem_timedwait`, `darwin_sem_trywait`, and `darwin_sem_wait`. Internal sentinel ids `__SEM_ID_NONE` and `__SEM_ID_LOCAL` validate initialization state.

Control flow: Initialization creates a condition variable and mutex, sets count, then marks the semaphore local. Wait paths lock the mutex, validate id, block on the condition when count is zero, decrement count on success, and unlock using pthread cleanup handlers. Post increments count and signals waiters when transitioning from zero.

State and persistence: State lives in `darwin_sem_t`: id, count, mutex, and condition variable. It is in-memory synchronization state only.

Dependencies and integration points: Includes `darwin_compat.h`, `pthread`, `errno`, and `assert`. It is compiled into pyfuse3 only on Darwin by `util/build_backend.py` and is exposed through macro aliases in the header.

Risks: `darwin_sem_wait` treats a spurious wake with no count as `EINTR`; repeated spurious wakes can surface as errors. `darwin_sem_destroy` broadcasts while destroying and must not race with active users. Timed wait asserts non-timeout pthread errors as impossible.

Test signals: No direct unit tests. Darwin builds and runtime FUSE operations indirectly validate semaphore behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.h -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.h

Purpose: Declares the Darwin semaphore compatibility API and maps POSIX semaphore names to the local implementation.

Important APIs/types/functions: Defines `darwin_sem_t` with local count/mutex/condition storage, `DARWIN_SEM_VALUE_MAX`, function prototypes for the Darwin semaphore operations, `typedef darwin_sem_t sem_t`, and macros `sem_init`, `sem_destroy`, `sem_getvalue`, `sem_post`, `sem_timedwait`, `sem_trywait`, and `sem_wait`.

Control flow: This header is included instead of `<semaphore.h>` on Darwin through `pyfuse3.h`, so C/Cython code can call semaphore APIs under the standard names.

State and persistence: Defines the memory layout used by `darwin_compat.c`; no persistent state.

Dependencies and integration points: Requires `pthread.h`. It integrates with the platform selector in `pyfuse3.h` and must not be combined with the system semaphore header in the same caller.

Risks: Macro substitution can surprise code that expects real POSIX semaphore types. `DARWIN_SEM_VALUE_MAX` depends on `int32_t`, so transitive includes must provide it on all supported compilers.

Test signals: Covered only by Darwin compilation/runtime paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/gettime.h -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/gettime.h

Purpose: Provides `gettime_realtime` as a platform-independent helper for real-time clock retrieval.

Important APIs/types/functions: Static function `gettime_realtime(struct timespec *tp)` maps to `clock_gettime(CLOCK_REALTIME, tp)` on Linux/BSD and to `gettimeofday` with microsecond-to-nanosecond conversion on Darwin.

Control flow: Preprocessor branches on `PLATFORM` from `pyfuse3.h`. Unknown platforms fail compilation.

State and persistence: No state; writes the current wall-clock time into the provided `timespec`.

Dependencies and integration points: Uses `<time.h>` on Linux/BSD and `<sys/time.h>` on Darwin. Native pyfuse3 code can use this instead of conditional clock code.

Risks: Darwin fallback has microsecond resolution, so nanosecond fields are not true nanosecond precision there. Wall-clock time can jump with system clock changes.

Test signals: Timestamp rounding tests and filesystem timestamp tests indirectly exercise the native timestamp plumbing that relies on time conversions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/gettime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/macros.c -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/macros.c

Purpose: Defines platform-specific preprocessor macros for accessing nanosecond fields in `struct stat` and assigning Darwin-only or non-Darwin fields.

Important APIs/types/functions: Linux macros access `st_atim`, `st_ctim`, and `st_mtim`; BSD/Darwin macros access `st_atimespec`, `st_ctimespec`, `st_mtimespec`, and birthtime fields. `ASSIGN_DARWIN` and `ASSIGN_NOT_DARWIN` conditionally assign fields by platform.

Control flow: Compile-time `#if PLATFORM` branches select the correct struct layout. Unknown platforms fail compilation.

State and persistence: No runtime state; this is compile-time portability glue.

Dependencies and integration points: Included by native pyfuse3/Cython code that maps system stat data into Python-facing attributes.

Risks: The file uses `.c` extension despite containing macro definitions; it must be included, not independently compiled as a normal translation unit without context. Incorrect platform detection would produce invalid struct-field access.

Test signals: `test_rounding.py`, `test_api.py::test_entry_res`, and example filesystem timestamp checks are indirect signals for timestamp precision and conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/macros.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/pyfuse3.h -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/pyfuse3.h

Purpose: Central native header for platform detection, semaphore inclusion, and libfuse version gating.

Important APIs/types/functions: Defines `PLATFORM_LINUX`, `PLATFORM_BSD`, `PLATFORM_DARWIN`, sets `PLATFORM` based on compiler OS macros, includes `darwin_compat.h` on Darwin and `<semaphore.h>` elsewhere, includes `<fuse.h>`, and enforces `FUSE_VERSION >= 32`.

Control flow: Compilation fails early for unknown operating systems or libfuse versions older than 3.2.0.

State and persistence: No state; establishes compile-time constants and includes.

Dependencies and integration points: Used by native extension sources and paired with `util/build_backend.py`, which defines `FUSE_USE_VERSION=32` and links against `fuse3`.

Risks: Platform macro checks are strict; unsupported POSIX-like systems fail to build. The `__FreeBSD_kernel__ && __GLIBC__` branch assumes both macros can be tested safely.

Test signals: Any successful extension build validates this header for the host OS. CI matrix and package builds are the main coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/pyfuse3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/xattr.h -->
# sources/user-network-fs/pyfuse3/src/pyfuse3/xattr.h

Purpose: Provides platform-independent wrappers for extended attribute get/set operations and normalizes missing constants across Linux, BSD, and Darwin.

Important APIs/types/functions: Defines `UNUSED`, maps Linux `ENOATTR` to `ENODATA` when needed, stubs namespace/flag constants on Linux/Darwin, defines BSD `XATTR_CREATE`/`XATTR_REPLACE` as zero, and provides static `getxattr_p`/`setxattr_p` wrappers for each platform.

Control flow: Compile-time platform branches select system headers and wrapper implementations. BSD wrappers check `size >= SSIZE_MAX`, map extattr APIs, and validate full writes.

State and persistence: No state; wrappers operate on filesystem paths and xattr buffers.

Dependencies and integration points: Used by native pyfuse3 extension code for `pyfuse3.getxattr`/`setxattr` behavior. Depends on system xattr/extattr APIs.

Risks: BSD lacks create/replace semantics in this wrapper, so tests for those flags cannot be positive. Linux wrapper ignores namespace argument because Linux encodes namespace in the attribute name. Path-based xattr APIs can race with filesystem changes.

Test signals: `test_api.py::test_xattr` compares pyfuse3 xattr behavior with Python `os.getxattr`/`os.setxattr` where available and skips unsupported filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/src/pyfuse3/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/conftest.py -->
# sources/user-network-fs/pyfuse3/test/conftest.py

Purpose: Pytest configuration for pyfuse3 tests, including suspicious-output checks, source-tree import setup, logging control, warning policy, and teardown garbage collection.

Important APIs/types/functions: Registers `pytest_checklogs` plugin. Autouse fixture `register_false_checklog_pos` suppresses known deprecation and valgrind messages. `pytest_addoption` adds `--installed` and `--logdebug`. `pytest_pyfunc_call` delays after failures. `pytest_configure` updates `sys.path`/`PYTHONPATH`, enables faulthandler, configures warnings and logging. `pytest_runtest_teardown` forces `gc.collect`.

Control flow: Pytest loads this before tests. Unless `--installed` is set, source `src` is preferred for imports and subprocesses inherit the same `PYTHONPATH`. Logging defaults disable debug unless requested.

State and persistence: Mutates process environment, `sys.path`, Python warnings filters, logging levels, and per-test false-positive registries.

Dependencies and integration points: Integrates with `pytest_checklogs.py`, pyfuse3 subprocess examples, and tests that rely on clean stderr/stdout.

Risks: The source import branch checks for `setup.py`, which may be stale in a pyproject-first project; if absent, source insertion may not occur. Strict output checking can fail tests for benign new warnings unless registered.

Test signals: This file is itself test infrastructure; failures in warning/log output are surfaced by the plugin after every test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/pytest.ini -->
# sources/user-network-fs/pyfuse3/test/pytest.ini

Purpose: Stores pytest default options and marker declarations for pyfuse3 tests.

Important APIs/types/functions: Sets `addopts = --verbose --assert=rewrite --tb=native -x` and declares marker `uses_fuse`.

Control flow: Pytest reads this during configuration. `-x` stops the run on first failure, and native tracebacks make debugging extension/FUSE failures clearer.

State and persistence: Persistent test policy only; no runtime state.

Dependencies and integration points: Integrates with tests using `pytestmark = fuse_test_marker()` and the custom checklogs plugin.

Risks: `-x` can hide later failures in full-suite runs. The marker must stay declared to avoid strict-marker warnings if enabled elsewhere.

Test signals: Applies to all pytest invocations rooted in the test directory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/pytest_checklogs.py -->
# sources/user-network-fs/pyfuse3/test/pytest_checklogs.py

Purpose: Pytest plugin that fails tests on suspicious stdout/stderr text or warning-and-above log records unless explicitly registered as expected.

Important APIs/types/functions: `CountMessagesHandler`, context manager `assert_logs`, `check_test_output`, `register_output`, fixture `reg_output`, and autouse fixture `check_output`.

Control flow: `check_output` yields to the test, scans captured log records from setup/call/teardown for warning-or-higher unignored records, then scans stdout/stderr for words such as exception, error, warning, fatal, traceback, fault, crash, abort, and fishy. `assert_logs` temporarily attaches a handler that marks matching records as ignored and optionally asserts exact count.

State and persistence: Per-test state is stored on `request.node.checklogs_fp`. Log records may get `checklogs_ignore=True`. No persistent state.

Dependencies and integration points: Used by `conftest.py` as a plugin. Integrates with pytest `capfd`/`caplog` and test code that expects warnings.

Risks: Regex-based suspicious output matching can produce false positives on legitimate output. `assert_logs` matches `record.msg` before formatting, so formatted output text may not match.

Test signals: Every test using this conftest gets output/log checking automatically.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/pytest_checklogs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_api.py -->
# sources/user-network-fs/pyfuse3/test/test_api.py

Purpose: Unit tests for selected pyfuse3 public APIs that do not require mounting a FUSE filesystem.

Important APIs/types/functions: Tests `pyfuse3.listdir`, `get_sup_groups`, `syncfs`, xattr helpers, `EntryAttributes`, `SetattrFields`, `RequestContext`, `StatvfsData`, and `FUSEError` copy/pickle behavior. `_getxattr_helper` compares pyfuse3 xattr access with Python `os.getxattr`.

Control flow: Each test calls pyfuse3 APIs directly. `test_xattr` creates a temporary file, verifies missing xattrs, sets via pyfuse3, optionally sets via `os`, and compares values. `test_copy` confirms unpickleable native request structs and copyable attribute/stat structs.

State and persistence: Uses temporary files and host `/usr/bin` listing. No persistent project state.

Dependencies and integration points: Depends on a built pyfuse3 extension and host OS APIs for groups, syncfs, xattrs, and directory listings.

Risks: `/usr/bin` can change during `test_listdir`. Xattr support depends on filesystem mount options and may skip on `ENOTSUP`. Host group state and permissions affect tests.

Test signals: Provides smoke coverage for native extension wrappers, timestamp precision storage, xattr portability, and object copy semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_api.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_examples.py -->
# sources/user-network-fs/pyfuse3/test/test_examples.py

Purpose: End-to-end tests for pyfuse3 example filesystems and common filesystem operations through mounted FUSE instances.

Important APIs/types/functions: Test entry points `test_hello`, `test_tmpfs`, and `test_passthroughfs`. Helper operations include `checked_unlink`, `tst_mkdir`, `tst_symlink`, `tst_mknod`, `tst_chown`, `tst_chmod`, `tst_write`, `tst_unlink`, `tst_statvfs`, `tst_link`, `tst_rename`, `tst_readdir`, `tst_truncate_path`, `tst_truncate_fd`, `tst_utimens`, `tst_rounding`, `tst_passthrough`, and `assert_same_stats`.

Control flow: Tests spawn example scripts as subprocesses, wait for mount readiness, perform host filesystem syscalls against the mount, and unmount/cleanup. The passthrough test checks both source-to-mount and mount-to-source propagation. Rounding tests set nanosecond timestamps near a precision boundary.

State and persistence: Uses pytest temporary directories as mountpoints and backing directories. Subprocess mounts are cleaned via utility helpers. A global `name_generator` creates unique names within the process.

Dependencies and integration points: Depends on FUSE availability, pyfuse3 examples, `fusermount`/`umount`, host permissions, and external OS semantics for links, ownership, chmod, utime, truncation, and statvfs.

Risks: FUSE mounts can hang or leave stale mountpoints if cleanup fails. Chown tests are skipped for passthrough unless root. Timestamp equality has CI exceptions for known libfuse/kernel precision behavior.

Test signals: This is the primary behavior signal for `examples/tmpfs.py`, passthroughfs, hello examples, writeback-cache behavior, and pyfuse3's syscall mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_examples.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_fs.py -->
# sources/user-network-fs/pyfuse3/test/test_fs.py

Purpose: Integration tests for lower-level pyfuse3 features such as cache invalidation, notify-store, poll notification, timeout behavior, and termination.

Important APIs/types/functions: Fixtures `testfs` and `pollfs` mount `Fs` or `PollTestFs` in a forked process. Tests include `test_invalidate_entry`, `test_invalidate_inode`, `test_notify_store`, `test_notify_poll`, `test_entry_timeout`, `test_attr_timeout`, and `test_terminate`. Classes `Fs` and `PollTestFs` implement minimal `Operations` handlers. `run_fs` runs pyfuse3 in the child process.

Control flow: Parent process mounts a child-process filesystem and communicates state through a multiprocessing manager namespace. Tests trigger special behavior by setting xattr `command` on the mount or file. The filesystem then calls pyfuse3 APIs such as `invalidate_entry_async`, `invalidate_inode`, `notify_store`, `terminate`, and `PollHandle.notify`.

State and persistence: Test state is in manager namespace flags (`lookup_called`, `read_called`, timeouts, poll flags), child-process operation object fields, and kernel cache state. Filesystem content is a single virtual `message` file.

Dependencies and integration points: Depends on multiprocessing fork mode, Trio, pyfuse3, host FUSE, `select.poll`, and utility mount helpers.

Risks: Uses sleeps to wait for cache invalidation semantics and poll readiness, so timing can be flaky on slow systems. Fork-based tests reject multi-threaded parent processes. Poll tests rely on platform poll support.

Test signals: Strong signal for pyfuse3 invalidation/notification APIs and operation dispatch correctness beyond basic file IO.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_fs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_rounding.py -->
# sources/user-network-fs/pyfuse3/test/test_rounding.py

Purpose: Regression test for nanosecond timestamp round-trip precision in `EntryAttributes`.

Important APIs/types/functions: `test_rounding` uses `_NANOS_PER_SEC` and `EntryAttributes`, sets `st_atime_ns`, `st_ctime_ns`, and `st_mtime_ns` to a large value ending at maximum nanosecond offset, and asserts exact equality on readback.

Control flow: Constructs one native-backed attribute object and performs direct property assignment/readback with no FUSE mount.

State and persistence: No persistent state.

Dependencies and integration points: Depends on pyfuse3 native attribute property setters/getters.

Risks: Only covers dates near 2037 and deliberately skips y2038 and BSD/macOS birthtime coverage. It detects conversion rounding but not filesystem/kernel timestamp truncation.

Test signals: Direct signal that Python-facing nanosecond properties do not lose precision due to float division or conversion bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/test_rounding.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/util.py -->
# sources/user-network-fs/pyfuse3/test/util.py

Purpose: Shared helpers for pyfuse3 tests that need FUSE capability detection, mount readiness, cleanup, and unmount validation.

Important APIs/types/functions: `fuse_test_marker`, `exitcode`, generic `wait_for`, `wait_for_mount`, `cleanup`, and `umount`. `Process` type aliases subprocess and multiprocessing process variants.

Control flow: `fuse_test_marker` checks Darwin shortcut, `fusermount`, `/dev/fuse`, setuid/root conditions, and ability to open `/dev/fuse`, returning either a skip marker or `uses_fuse`. `wait_for_mount` polls `os.path.ismount` and process exit. `cleanup` attempts lazy unmount and terminates/kills process. `umount` performs checked unmount and asserts process exits cleanly.

State and persistence: Acts on external process state and mountpoints. No internal persistent state.

Dependencies and integration points: Used by `test_examples.py` and `test_fs.py`. Depends on platform, `fusermount`, macOS `umount`, subprocess/multiprocessing APIs, and pytest failure/skip mechanisms.

Risks: Lazy unmount may mask cleanup issues. Capability checks are Linux-centric except for Darwin shortcut. Timeouts can fail on overloaded machines or leave processes if kill behavior differs.

Test signals: This file controls whether FUSE tests run and how failures are cleaned, so it is central to test reliability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/test/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/util/build_backend.py -->
# sources/user-network-fs/pyfuse3/util/build_backend.py

Purpose: Custom PEP 517 backend wrapper that configures the pyfuse3 Cython extension dynamically from `pkg-config` and platform detection before delegating to setuptools.

Important APIs/types/functions: Re-exports `setuptools.build_meta` hooks. `pkg_config` validates minimum versions and parses cflags/libs. `get_extension_modules` creates extension `pyfuse3.__init__` from `src/pyfuse3/__init__.pyx`, adds libfuse compile/link flags, appends `-lrt` on Linux/GNU kFreeBSD and `darwin_compat.c` on Darwin. `build_wheel` and `build_editable` monkey-patch `Distribution.__init__` to inject `ext_modules`; `build_sdist` delegates unchanged.

Control flow: Build frontend imports this backend. Wheel/editable builds patch setuptools distribution construction for the duration of the underlying build hook, then restore the original initializer in `finally`.

State and persistence: Temporarily mutates `setuptools.Distribution.__init__` in-process. Build artifacts are produced by setuptools; this file does not persist its own state.

Dependencies and integration points: Depends on `pkg-config`, `fuse3 >= 3.2.0`, Cython, setuptools, pthread, and platform `os.uname`. Tied to `pyproject.toml` build-backend settings.

Risks: Monkey-patching setuptools internals is brittle with future setuptools changes. `pkg_config` reads only one stdout line and assumes ASCII. Cross-compilation may be limited by `os.uname` host detection.

Test signals: Package build success is the primary validation. CI jobs that install/build pyfuse3 exercise this path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/util/build_backend.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/pyfuse3/util/make_release.py -->
# sources/user-network-fs/pyfuse3/util/make_release.py

Purpose: Automates mechanical pyfuse3 release preparation: parse changelog version, optionally rotate signify keys, commit/tag, build docs and sdist, sign tarball, and generate announcement text.

Important APIs/types/functions: Constants `ROOT`, `CHANGES`, `SIGNIFY_DIR`, `VERSION_HEADING_RE`, and `ANNOUNCEMENT_TEMPLATE`. Helpers `run`, `capture`, `parse_changes`, `signing_keys_dir`, `rotate_keys`, `contributor_list`, and `main`.

Control flow: `main` checks required tools, parses the top release heading from `Changes.rst`, finds previous tag, rotates keys for new major/minor revision, commits all changes, tags, runs `uv sync`, builds Sphinx docs and sdist, signs the tarball, and prints an announcement.

State and persistence: Mutates git history/tags, key files under `signify` and external signing key directory, `dist/` artifacts, built docs, and terminal output. It requires environment variable `PYFUSE_SIGNING_KEYS_DIR` when key rotation is needed.

Dependencies and integration points: Depends on git, signify, uv, Sphinx, pyfuse3 packaging, changelog format, and release key layout.

Risks: It runs `git commit --all` and `git tag`, so dirty unrelated changes could be included if used carelessly. Key rotation renames files and deletes obsolete public keys. Changelog parser accepts only specific heading formats.

Test signals: No direct tests. Safe usage is validated by release dry runs and tool failures; because of side effects, this script should not be executed by normal tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/pyfuse3/util/make_release.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/ISSUE_TEMPLATE/config.yml -->
# sources/user-network-fs/rclone/.github/ISSUE_TEMPLATE/config.yml

Purpose: Configures GitHub issue creation behavior for rclone by disabling blank issues and directing support requests to the forum.

Important APIs/types/functions: `blank_issues_enabled: false` and one `contact_links` entry named `Rclone Forum Community Support`.

Control flow: GitHub reads this when rendering issue templates. Users cannot open blank issues through the normal UI and see the forum link.

State and persistence: Repository configuration only.

Dependencies and integration points: Integrates with GitHub Issues UI and the rclone forum.

Risks: Users with bug reports that do not match templates may be redirected away from GitHub. The forum URL is an external dependency.

Test signals: No automated tests; effect is visible in GitHub UI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/dependabot.yml -->
# sources/user-network-fs/rclone/.github/dependabot.yml

Purpose: Configures Dependabot updates for GitHub Actions used by rclone.

Important APIs/types/functions: Version 2 config with `package-ecosystem: github-actions`, root directory `/`, and daily schedule.

Control flow: Dependabot periodically scans workflow action references and proposes update PRs.

State and persistence: Repository automation policy only.

Dependencies and integration points: Integrates with GitHub Dependabot and workflow files under `.github/workflows`.

Risks: Daily action-update PRs can introduce CI changes or noise. It does not cover Go modules or Docker base images.

Test signals: Dependabot PRs and subsequent CI runs are the validation signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/build.yml -->
# sources/user-network-fs/rclone/.github/workflows/build.yml

Purpose: Main GitHub Actions workflow for rclone builds, tests, linting, vulnerability scanning, Android builds, and beta artifact deployment.

Important APIs/types/functions: Workflow `build` triggers on push, PR, manual dispatch. Jobs include matrix `build`, `lint`, and `android`. Matrix covers linux, 386, macOS amd64/arm64, Windows, other OS, and Go 1.25 compatibility. Key steps install Go, cache modules/builds, install platform libraries, run `make`, `make quicktest`, race tests, librclone tests, compile-all, deploy beta builds, run golangci-lint across OS targets, govulncheck, markdownlint, autogenerated edit checks, and Android gomobile/native builds.

Control flow: Jobs are gated to upstream repository/manual runs, avoiding most fork PR execution. Build job sets environment from matrix entries, installs OS-specific FUSE/git-annex dependencies, builds, tests, and optionally deploys. Lint job runs static checks and markdown checks. Android job builds gomobile binding and native binaries for multiple Android ABIs, then optionally uploads.

State and persistence: Uses GitHub caches for Go modules/builds and uploads beta/test artifacts when secrets are available. It trims module zip caches before save.

Dependencies and integration points: Integrates with Makefile targets, Go toolchain versions, FUSE libraries, macFUSE/WinFsp, Chocolatey/Homebrew/apt, golangci-lint action, govulncheck, markdownlint action, and rclone deployment config secrets.

Risks: Heavy matrix and external package installs can be flaky. Actions versions and requested Go versions must exist. Deployment steps depend on secrets and branch/ref gating. Cache key design trades freshness for storage efficiency.

Test signals: This is the repository's broadest CI signal: unit tests, race tests, cross-compile checks, lint, vulnerability scan, docs markdown policy, and Android builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/build_publish_docker_image.yml -->
# sources/user-network-fs/rclone/.github/workflows/build_publish_docker_image.yml

Purpose: Builds and publishes multi-platform rclone Docker images to GitHub Container Registry and Docker Hub-style tags via a digest-then-merge workflow.

Important APIs/types/functions: Workflow `Build & Push Docker Images` triggers on push and manual dispatch. `build-image` matrix covers linux/amd64, 386, arm64, arm/v7, and arm/v6. Steps free disk, checkout, derive repository/platform/cache names, extract Docker metadata, set up QEMU/buildx, use Go build cache injection, login to GHCR, build/push digest images, and upload digest artifacts. `merge-image` downloads digests, extracts metadata tags/annotations, logs into Docker Hub and GHCR, creates manifest list, inspects, and runs `rclone version`.

Control flow: Per-platform jobs push untagged digest images to GHCR. The merge job waits for all digests and assembles a final manifest with semver/ref/sha/beta tags and OCI labels/annotations.

State and persistence: Writes registry images, build cache layers, digest artifacts retained for one day, and final manifest tags.

Dependencies and integration points: Depends on Docker Buildx/QEMU, `Dockerfile`, Docker metadata action, cache-dance, GHCR permissions, Docker Hub secrets, and GitHub artifact actions.

Risks: Registry authentication, cache growth, QEMU emulation, and runner disk pressure are key failure modes. The workflow uses shell-generated quoted tag strings, so metadata content must remain shell-safe.

Test signals: Final `docker run --rm ... version` confirms the merged image starts and contains rclone.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/build_publish_docker_image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/build_publish_docker_plugin.yml -->
# sources/user-network-fs/rclone/.github/workflows/build_publish_docker_plugin.yml

Purpose: Builds and publishes rclone Docker volume plugin images for release tags or manual runs.

Important APIs/types/functions: Workflow `Release Build for Docker Plugin` triggers on published releases and manual dispatch. Job `build_docker_volume_plugin` frees disk, checks out repository, logs into Docker Hub, loops over plugin architectures amd64/arm64/arm/v7/arm/v6, and invokes `make docker-plugin` with architecture-derived tags and release-version tags, plus latest/version tags for amd64.

Control flow: Release tag is parsed from `GITHUB_REF`. Each architecture build uses Makefile plugin targets to create and push Docker plugin artifacts.

State and persistence: Publishes Docker plugin images under `rclone/docker-volume-rclone` tags and creates temporary build directories handled by Makefile targets.

Dependencies and integration points: Depends on Docker, Makefile `docker-plugin`, Docker Hub credentials, and contrib plugin build context.

Risks: Docker plugin build/push requires privileged or compatible Docker environment. Secret names differ from image workflow (`DOCKER_HUB_USER`/`DOCKER_HUB_PASSWORD`). Partial architecture push failures can leave inconsistent tag sets.

Test signals: No explicit runtime smoke test; successful `make docker-plugin` and push are the only workflow signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/build_publish_docker_plugin.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/notify.yml -->
# sources/user-network-fs/rclone/.github/workflows/notify.yml

Purpose: Sends notifications when issues receive configured labels.

Important APIs/types/functions: Workflow triggers on `issues` labeled events. Job uses `jenschelkopf/issue-label-notification-action@1.3` with `NOTIFY_ACTION_TOKEN` and recipient mapping `Support Contract=@rclone/support`.

Control flow: When an issue is labeled, the action reads label-recipient mappings and notifies the matching team/user.

State and persistence: No repository artifacts; side effect is notification delivery through GitHub/action mechanisms.

Dependencies and integration points: Depends on GitHub issue label events, an external action, token secret, and the `@rclone/support` recipient.

Risks: Misconfigured or missing token prevents notification. Label text must match exactly.

Test signals: Manual issue labeling is the practical validation path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/notify.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/winget.yml -->
# sources/user-network-fs/rclone/.github/workflows/winget.yml

Purpose: Publishes rclone releases to the Windows Package Manager repository.

Important APIs/types/functions: Triggered on release `released`. Uses `vedantmgoyal2009/winget-releaser@v2` with identifier `Rclone.Rclone`, installer regex `-windows-\w+\.zip$`, and `WINGET_TOKEN`.

Control flow: On release, the action finds matching Windows zip installers and submits/updates the WinGet manifest.

State and persistence: Side effects occur in the WinGet packaging ecosystem, not in this repository.

Dependencies and integration points: Depends on release assets, GitHub token secret, and the winget-releaser action.

Risks: Regex must match current asset naming. Token permissions and external WinGet validation can fail after release.

Test signals: Action success and downstream WinGet PR/manifest publication are the validation signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.github/workflows/winget.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.golangci.yml -->
# sources/user-network-fs/rclone/.golangci.yml

Purpose: Defines rclone's golangci-lint v2 linter, formatter, issue, and run settings.

Important APIs/types/functions: Disables default linter selection and explicitly enables `errcheck`, `govet`, `ineffassign`, `staticcheck`, `unused`, `gocritic`, `misspell`, `revive`, and `unconvert`. Configures govet all-minus-fieldalignment/shadow, staticcheck exclusions, gocritic enabled checks plus ruleguard rules, revive rules, goimports formatter, unlimited issue counts, and 10-minute timeout.

Control flow: The GitHub build workflow runs golangci-lint action for Linux, Windows, macOS, FreeBSD, and OpenBSD targets. Local `make check` also invokes `golangci-lint run`.

State and persistence: Static lint policy only.

Dependencies and integration points: Depends on golangci-lint v2 config schema, custom ruleguard file `bin/rules.go`, and Go build tags from Makefile/CI.

Risks: Version drift in golangci-lint can change rule behavior. Explicit linter lists require maintenance as linters are deprecated or renamed.

Test signals: CI lint job reports issues across several `GOOS` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/.markdownlint.yml -->
# sources/user-network-fs/rclone/.markdownlint.yml

Purpose: Defines markdownlint style policy for selected rclone documentation.

Important APIs/types/functions: Enforces ATX headings, dash unordered lists, `---` horizontal rules, fenced code blocks with backticks, asterisks for emphasis/strong, sibling-only duplicate heading check, relaxed line length for code/tables, front-matter-aware single-title rule, disabled link fragment validation, and a restricted set of fenced code languages.

Control flow: The CI build workflow invokes `DavidAnson/markdownlint-cli2-action` against selected docs. The Makefile's `check` target runs `bin/markdown-lint`.

State and persistence: Static documentation style policy.

Dependencies and integration points: Depends on markdownlint rule names/schema and Hugo/GitHub compatible language identifiers.

Risks: Restricting fenced languages can fail docs using valid but unlisted identifiers. Disabling fragment checks avoids Hugo/GitHub mismatch but can miss broken anchors.

Test signals: CI markdown lint step and local `make check` enforce this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/.markdownlint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/Dockerfile -->
# sources/user-network-fs/rclone/Dockerfile

Purpose: Multi-stage Docker build for the rclone container image.

Important APIs/types/functions: Builder stage uses `golang:alpine`, optional `ARG CGO_ENABLED=0`, installs make/bash/gawk/git, copies `go.mod`/`go.sum`, downloads and verifies modules, copies source, builds with `make`, and runs `./rclone version`. Final stage uses `alpine:latest`, installs ca-certificates/fuse3/tzdata, enables `user_allow_other`, copies rclone binary to `/usr/local/bin`, creates `rclone` user/group id 1009, sets `ENTRYPOINT ["rclone"]`, `WORKDIR /data`, and `XDG_CONFIG_HOME=/config`.

Control flow: Docker build caches module download before full source copy. BuildKit cache mount stores Go build cache. Final image contains only runtime dependencies and the compiled binary.

State and persistence: Image layers persist module/build dependencies in builder layers and runtime binary/config defaults in final image. Runtime config is expected under `/config`.

Dependencies and integration points: Used by Docker image workflow and Makefile indirectly. Depends on Alpine packages, Go modules, and Makefile build target.

Risks: `alpine:latest` is moving and can change runtime behavior. FUSE use inside containers requires host capabilities/devices. `CGO_ENABLED=0` default may differ from builds requiring mount/cmount features.

Test signals: Docker image workflow runs `rclone version` during build and after final multi-platform manifest creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/Makefile -->
# sources/user-network-fs/rclone/Makefile

Purpose: Central build, test, lint, documentation, release, beta, upload, dependency, website, and Docker plugin automation for rclone.

Important APIs/types/functions: Variables derive branch, release tag, version, next versions, beta path/url, build tags, and ldflags embedding `fs.Version`. Core targets include `rclone`, `test_all`, `quicktest`, `racequicktest`, `compiletest`, `check`, dependency update targets, docs (`MANUAL`, commanddocs, backenddocs, rcdocs), install/clean/website/upload, release artifacts (`tarball`, `vendorball`, `sign_upload`, `check_sign`, `upload`, `upload_github`, `cross`, `beta`, `ci_upload`, `ci_beta`), development version bumps (`startdev`, `startstable`), and Docker plugin targets.

Control flow: Default `rclone` target builds with Go, embeds version via ldflags, handles Windows resources, and installs to `GOPATH/bin` atomically. CI targets wrap cross-compile and upload scripts. Documentation targets generate files from commands and content. Docker plugin targets build plugin rootfs and push/remove plugin images.

State and persistence: Writes binaries, build directories, docs outputs, release archives, checksums, tags, generated version files, and Docker plugin build directories. Some targets upload to configured remotes.

Dependencies and integration points: Integrates with Go, rclone's bin scripts, Hugo, pandoc, tidy, gpg, docker, cross-compile tooling, CI secrets/config, and Git.

Risks: Many targets have destructive or external side effects (`rm -rf`, uploads, git commits/tags, Docker pushes). Version derivation depends on git state and `VERSION`. Release targets assume external tools and remote configs.

Test signals: CI invokes `make`, `quicktest`, `racequicktest`, `compile_all`, `ci_beta`, `release_dep_linux`, Docker plugin targets, and docs/lint paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/alias/alias.go -->
# sources/user-network-fs/rclone/backend/alias/alias.go

Purpose: Implements rclone's `alias` backend, a virtual provider that redirects an alias remote to another configured remote/path.

Important APIs/types/functions: Registers `fs.RegInfo{Name:"alias", NewFs: NewFs}` with required option `remote`. `Options` contains `Remote string`. `NewFs` parses config with `configstruct.Set`, validates non-empty remote, rejects aliases pointing at themselves with `strings.HasPrefix(opt.Remote, name+":")`, and returns `cache.Get(ctx, fspath.JoinRootPath(opt.Remote, root))`.

Control flow: When rclone opens `aliasName:some/root`, `NewFs` joins the configured target remote with the requested root and returns the actual wrapped Fs directly, not an alias wrapper type.

State and persistence: No backend state after construction; configuration persists in rclone config. Fs caching is delegated to `fs/cache`.

Dependencies and integration points: Depends on rclone core `fs`, `cache`, config mapping/struct parsing, and `fspath.JoinRootPath`. Integrates with all target backends because it returns the target Fs.

Risks: Self-reference check only detects direct `name:` prefix, not longer alias cycles. Errors from the target remote surface as alias creation errors. Returning the target Fs means alias identity/features are those of the target.

Test signals: `alias_internal_test.go` covers empty remote, invalid remote, root/list path joining, relative path behavior, and local backend listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/alias/alias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/alias/alias_internal_test.go -->
# sources/user-network-fs/rclone/backend/alias/alias_internal_test.go

Purpose: Tests alias backend path resolution and error handling against the local backend.

Important APIs/types/functions: `prepare` installs config and sets `TestAlias` type/remote. `TestNewFS` table-drives combinations of configured remote root, requested Fs root, and list path, asserting entry names, sizes, and directory flags. `TestNewFSNoRemote` and `TestNewFSInvalidRemote` assert construction errors.

Control flow: Each table row converts fixture paths under `test/files` to absolute local paths, configures alias, opens `TestAlias:<fsRoot>`, lists `fsList`, sorts entries, and compares with expected entries.

State and persistence: Mutates test rclone config via `configfile.Install` and `config.FileSetValue`. Reads local fixture files; no persistent writes.

Dependencies and integration points: Imports local backend for registration, rclone config APIs, `fs.NewFs`, and testify `require`.

Risks: Tests rely on fixture layout and local path semantics, including `..` traversal behavior. They do not cover alias cycle chains.

Test signals: Provides focused validation that alias preserves list paths and rejects absent/invalid target config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/alias/alias_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/all/all.go -->
# sources/user-network-fs/rclone/backend/all/all.go

Purpose: Imports all active rclone backend packages for side-effect registration.

Important APIs/types/functions: The package contains blank imports for alias, archive, cloud/object storage, transfer protocols, wrapping backends, local/memory, and many provider-specific backends.

Control flow: When `backend/all` is imported, each backend package `init` runs and calls `fs.Register`, making all providers available.

State and persistence: Populates global backend registry through side effects. No local state.

Dependencies and integration points: Integrates all listed backend packages with command builds/tests that need every backend registered.

Risks: Adding a backend here increases binary dependencies and initialization side effects. Missing imports make a backend unavailable in builds that rely on `backend/all`.

Test signals: Compile-all and normal rclone builds catch broken imports. Backend integration tests depend on registration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/all/all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive.go -->
# sources/user-network-fs/rclone/backend/archive/archive.go

Purpose: Implements rclone's `archive` wrapper backend for reading archive files inside another remote as virtual directories, with `.zip` and `.sqfs` archivers registered by side-effect imports.

Important APIs/types/functions: Registers backend `archive` with optional `remote`. `Options` has `Remote`. `Fs` wraps an upstream `fs.Fs`, tracks root/features/wrapper, and caches discovered `archive` instances in `archives`. Helpers `findArchive`, `subArchive`, `(*archive).init`, `NewFs`, `findFs`, `List`, and `NewObject` define archive discovery and lazy opening. It implements many optional interfaces by delegating to the wrapped Fs: `Purge`, `Copy`, `Move`, `DirMove`, `ChangeNotify`, `DirCacheFlush`, `Put`, `PutStream`, `About`, `Shutdown`, `PublicLink`, `PutUnchecked`, `MergeDirs`, `CleanUp`, `OpenWriterAt`, `OpenChunkWriter`, `UserInfo`, and `Disconnect`.

Control flow: `NewFs` parses the configured remote/root, detects if the requested path is inside an archive by walking parent paths, opens the underlying remote via `cache.Get`, creates wrapper features by masking with the upstream, and either returns an initialized archive Fs when the root itself is an archive or returns the wrapper Fs. `List` delegates to the relevant sub-Fs and replaces recognized archive objects with directory entries. `NewObject` routes object lookup to the wrapped Fs or an initialized archive Fs based on the containing directory.

State and persistence: Maintains `archives` map of discovered archive paths and each archive's lazily initialized Fs under mutexes. Underlying remote state is external. Archive contents are read-only from concrete archiver implementations.

Dependencies and integration points: Depends on rclone `fs`, `cache`, `fspath`, config parsing, hash interfaces, archive `archiver` registry, and side-effect imports for squashfs/zip. Integrates with VFS through concrete archivers.

Risks: Archive lookup uses linear searches and an unordered map; comments note nested archive longest-prefix handling may be wrong. Archive writes are mostly delegated to underlying remote, which can make wrapper semantics subtle. Plan9 is unsupported by build tags.

Test signals: `archive_internal_test.go` creates zip/squashfs archives and checks list/read/range/seek behavior. `archive_test.go` runs fstests over local/memory archive configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive_internal_test.go -->
# sources/user-network-fs/rclone/backend/archive/archive_internal_test.go

Purpose: End-to-end tests for archive backend reading zip and squashfs archives, including full trees, subdirectories, single files, range reads, seek reads, sizes, modtimes, and root-above-archive listing.

Important APIs/types/functions: Helper `run` executes external commands. `checkTree` opens archive and source remotes, runs `operations.Check` and `CheckDownload`, then verifies `NewObject`, contents, `SeekOption`, `RangeOption`, modtime precision, size, and string identity for every source object. `testArchive` creates random test files with `rclone test makefiles`, builds an archive via callback, and runs several `checkTree` scenarios. `TestArchiveZip` uses external `zip`; `TestArchiveSquashfs` uses `mksquashfs`.

Control flow: Tests create local temp input trees, generate 1000 files, create archive output, open `:archive:<archivePath>` and compare against source. Subdirectory and single-file paths validate rooting inside archives; root listing validates archive file replacement as directory.

State and persistence: Uses temporary directories and external archive files. Rclone cache is used via `cache.Get`. No persistent repo state.

Dependencies and integration points: Depends on local backend, external `rclone`, `zip`, and `mksquashfs` executables, operations package, filters, fstest helpers, and testify.

Risks: External command availability controls skips/failures. Generating 1000 files can be slow. The tests do not cover write operations because archive contents are read-only.

Test signals: Strong behavioral signal for archive path mapping and concrete zip/squashfs read support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive_test.go -->
# sources/user-network-fs/rclone/backend/archive/archive_test.go

Purpose: Runs rclone's standard filesystem integration test suite against the archive backend.

Important APIs/types/functions: Defines `unimplementableFsMethods` and `unimplementableObjectMethods` expected not to work. `TestIntegration` runs against `-remote` if provided. `TestLocal` and `TestMemory` configure archive remotes wrapping a temp local directory or `:memory:` and run `fstests.Run` with `QuickTestOK`.

Control flow: Tests skip remote-specific cases depending on `fstest.RemoteName`. Extra config items create archive remotes for local and memory tests.

State and persistence: Uses temp local directory or in-memory backend. Standard fstests create/remove test objects in those remotes.

Dependencies and integration points: Imports local and memory backends, `fstest`, and `fstests`. Validates archive backend against rclone's generic Fs contract while acknowledging unsupported methods.

Risks: Since archive contents are read-only but wrapper delegates writes to underlying remotes, some generic tests may not cover actual archive file contents. Unimplementable lists must stay in sync with backend capabilities.

Test signals: Broad interface-compatibility signal for archive as a wrapper backend.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive_unsupported.go -->
# sources/user-network-fs/rclone/backend/archive/archive_unsupported.go

Purpose: Provides a buildable `archive` package stub on unsupported Plan 9 platforms.

Important APIs/types/functions: Build tag `//go:build plan9`; only declares package `archive`.

Control flow: On Plan 9, this file is selected while `archive.go` is excluded, preventing "no buildable Go source files" errors.

State and persistence: No state.

Dependencies and integration points: Integrates with Go build constraints and packages that import `backend/archive`.

Risks: Archive backend functionality is absent on Plan 9. Callers expecting registration will not get the real backend there.

Test signals: Cross-compilation/compile-all tests for Plan 9 are the signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archive_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archiver/archiver.go -->
# sources/user-network-fs/rclone/backend/archive/archiver/archiver.go

Purpose: Defines the registry used by archive format implementations to plug into the archive backend.

Important APIs/types/functions: `Archiver` struct contains `New func(ctx, f, remote, prefix, root) (fs.Fs, error)` and `Extension string`. Package-global `Archivers []Archiver` stores registered implementations. `Register` appends one or more archivers.

Control flow: Concrete packages call `archiver.Register` in `init`. `archive.go` scans `Archivers` to detect file extensions and instantiate the matching archive Fs lazily.

State and persistence: Global in-process registry; append order follows package initialization order.

Dependencies and integration points: Depends on rclone `fs` and context. Used by `backend/archive/zip` and `backend/archive/squashfs`.

Risks: Registry is a mutable slice with no locking; it is safe during init but not designed for concurrent runtime modification. Extension matching is suffix-based and linear.

Test signals: Archive tests indirectly validate that zip and squashfs are registered and discoverable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/archiver/archiver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/base/base.go -->
# sources/user-network-fs/rclone/backend/archive/base/base.go

Purpose: Provides a skeletal read-only archive Fs/Object implementation intended as common base code for concrete archivers, though its main read methods are placeholders.

Important APIs/types/functions: `Fs` stores wrapped Fs, wrapper, name, features, VFS, archive node, remote, prefix, and root. `New` builds a VFS, stats the archive object, sets features, and returns `*Fs`. Methods implement `fs.Fs`, `fs.UnWrapper`, and `fs.Wrapper`; `List`, `NewObject`, and `Object.Open` return internal `errNotImplemented`. Mutating methods return `vfs.EROFS`; hashes return none. `Object` exposes default remote/size/modtime/hash/update/remove behavior.

Control flow: `New` opens enough state to represent an archive file but does not parse a format. Consumers would embed or adapt this to implement format-specific listing and object reads.

State and persistence: Holds VFS and archive node handles plus path metadata. No writes are permitted through this base.

Dependencies and integration points: Depends on rclone `fs`, `hash`, and `vfs`. Shares design with concrete zip/squashfs implementations.

Risks: Placeholder methods make direct use invalid for real archivers. Default object `Size=-1` and `ModTime=time.Now()` are not suitable for stable listings.

Test signals: No direct tests visible in this subset. Concrete archivers duplicate rather than directly use most behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/base/base.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/squashfs/cache.go -->
# sources/user-network-fs/rclone/backend/archive/squashfs/cache.go

Purpose: Implements a `backend.Storage` adapter for go-diskfs squashfs reading over an rclone VFS node, with a small file-handle cache optimized for `ReadAt` offsets.

Important APIs/types/functions: `cache` stores a `vfs.Node`, mutex, and slice of cached handles. `cacheHandle` records expected next offset and handle. `newCache`, `open`, `close`, `ReadAt`, `Close`, and stub methods `WriteAt`, `Seek`, `Read`, `Stat`, `Sys`, `Writable` satisfy `backend.Storage`.

Control flow: `ReadAt` obtains a handle whose cached offset matches the request if possible, otherwise reuses the first cached handle or opens the node. After reading, it caches the handle with next offset `off+len(p)`. `Close` closes all cached handles.

State and persistence: Maintains in-memory pool of VFS handles and offsets. Does not persist data or write to archives.

Dependencies and integration points: Bridges `github.com/diskfs/go-diskfs/backend.Storage` with rclone `vfs.Node`/`vfs.Handle`. Used by `squashfs.New` to feed `squashfs.Read`.

Risks: Handle pool can grow with concurrent access until `Close`. Offset caching is heuristic; a reused nonmatching handle relies on underlying `ReadAt` correctness. Stub methods return internal errors if diskfs unexpectedly needs them.

Test signals: Squashfs archive tests indirectly validate parallel/random reads through this adapter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/squashfs/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/squashfs/squashfs.go -->
# sources/user-network-fs/rclone/backend/archive/squashfs/squashfs.go

Purpose: Implements the `.sqfs` archiver for rclone's archive backend, exposing squashfs contents as a read-only rclone Fs.

Important APIs/types/functions: Registers `.sqfs` in `init`. `Fs` stores wrapped Fs, VFS, squashfs filesystem handle, cache, archive node, prefix/root, and features. `New` creates VFS with zero read wait, stats the archive, builds cache, calls `squashfs.Read`, adjusts root when pointing to a single file, and sets features. Path helpers `toNative`, `fromNative`, `objectFromFileInfo`, `newObjectNative`. Fs methods `List`, `NewObject`, `Precision`, read-only mutators, `Hashes`, unwrap/wrap. `Object` stores size, modtime, and `squashfs.FileStat`; `Open` supports `SeekOption` and `RangeOption`.

Control flow: Listings translate rclone remotes into native squashfs paths, read directory entries from go-diskfs, create dirs or regular file objects, and skip non-regular files. Object lookup reads parent directory and finds a matching leaf. Opening an object calls the squashfs file stat's `Open`, seeks if needed, and wraps limited reads for ranges.

State and persistence: Keeps parsed squashfs handle and VFS/cache state in memory. Archive contents are read-only; mutations return `vfs.EROFS`. Hashes are unsupported.

Dependencies and integration points: Depends on go-diskfs squashfs, archive registry, rclone fs/hash/log/readers/vfs/vfscommon. Instantiated through `archive.go` when `.sqfs` is discovered.

Risks: Non-regular entries are skipped. Some comments indicate unfinished single-object handling and blocksize tuning. Path translation must correctly handle prefix/root or objects can disappear. Cache close lifecycle is not visibly tied to Fs shutdown in this file.

Test signals: `TestArchiveSquashfs` validates generated squashfs archives, subdirectory/single-file roots, range/seek reads, modtimes, sizes, and full-tree checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/squashfs/squashfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/zip/zip.go -->
# sources/user-network-fs/rclone/backend/archive/zip/zip.go

Purpose: Implements the `.zip` archiver for rclone's archive backend, exposing zip entries as a read-only rclone Fs.

Important APIs/types/functions: Registers `.zip` in `init`. `Fs` stores wrapped Fs, VFS, archive node, prefix/root, features, and `dirtree.DirTree`. `New` stats the zip file and calls `readZip`. `readZip` opens the archive node, creates `zip.NewReader`, normalizes paths, filters by root, builds directory/object tree, detects single-object roots, checks parent dirs, and sorts. Fs methods include `List`, `NewObject`, `Precision`, read-only mutators, `Hashes` returning CRC32, and unwrap/wrap. `Object` exposes size, modtime, CRC32 hash, and `Open` with seek/range support by discarding bytes or limiting the reader.

Control flow: Opening a zip eagerly scans the central directory into `dirtree`. Listing is a lookup in `dt[dir]`. `NewObject` finds an entry and rejects directories. Object open starts a fresh zip file reader, discards offset bytes for seek/range, and limits output when requested.

State and persistence: Maintains an in-memory dirtree of zip entries. Archive contents are immutable through this backend; mutators return `vfs.EROFS`. Hash state comes from zip CRC32 headers.

Dependencies and integration points: Depends on Go `archive/zip`, rclone archive registry, `dirtree`, fs/hash/log/readers/vfs, and VFS access to the underlying archive object. Instantiated by `archive.go` for `.zip` paths.

Risks: Requires known archive size; unknown-size remotes fail. Seeking is implemented by read-and-discard, which can be inefficient for large offsets. Path normalization with `path.Clean` may collapse unusual zip names. Eager central-directory reading means very large archives consume memory proportional to entry count.

Test signals: `TestArchiveZip` validates created zip archives through operations check/download, object reads, range/seek reads, modtimes, sizes, and root/subroot behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/archive/zip/zip.go -->
