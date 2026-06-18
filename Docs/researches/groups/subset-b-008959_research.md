# subset-b-008959 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/dir_store.c -->
# sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/dir_store.c

## Purpose
This file implements the `dir_store` WiredTiger storage source extension. It is a demonstration and test storage source that treats local directories as a stand-in for cloud object storage, with an optional read cache directory and configurable artificial delay/error injection.

## Important APIs, Types, and Functions
The main extension type is `DIR_STORE`, whose first field is `WT_STORAGE_SOURCE`, so it can be registered through `WT_CONNECTION->add_storage_source`. `DIR_STORE_FILE_SYSTEM` wraps WiredTiger's native `WT_FILE_SYSTEM` while tracking bucket/cache/home directories. `DIR_STORE_FILE_HANDLE` wraps a real `WT_FILE_HANDLE` and is tracked in a `TAILQ`.

Key storage-source entry points are `dir_store_customize_file_system`, `dir_store_flush`, `dir_store_flush_finish`, `dir_store_add_reference`, and `dir_store_terminate`. File-system entry points include `dir_store_open`, `dir_store_exist`, `dir_store_size`, `dir_store_remove`, `dir_store_rename`, and directory-list helpers. File-handle methods forward reads and size calls to the underlying handle while rejecting writes.

## Control Flow
`wiredtiger_extension_init` allocates and initializes `DIR_STORE`, installs the storage-source vtable, parses extension config values, and registers the name `dir_store`. A connection later calls `ss_customize_file_system`, which parses `cache_directory`, obtains the native file system, resolves bucket/cache directories relative to the WiredTiger home, and returns a customized `WT_FILE_SYSTEM`.

On flush, the extension maps the source name to the home directory and the object name to the bucket directory, optionally delays/fails through `dir_store_delay`, then copies via `dir_store_file_copy` using a `*.TMP` temporary file and exclusive create before rename. `flush_finish` optionally hard-links the just-flushed source into the cache and makes it read-only. Opens are read-only only; if caching is enabled, `dir_store_open` copies missing bucket objects into the cache before opening the cached copy.

## State and Persistence Behavior
Persistent objects are ordinary files in `bucket_dir`; cached objects are ordinary files in `cache_dir`; source files come from `home_dir`. `dir_store_file_copy` makes destination objects read-only and avoids overwriting existing objects. Object-read/write counters and operation counters are in-memory only and are used for simulated delay/error behavior. The file handle queue is protected by `file_handle_lock`; the storage source itself uses a reference count so termination frees the shared object only after all references are released.

## Dependencies and Integration Points
The file depends on WiredTiger extension interfaces from `wiredtiger.h` and `wiredtiger_ext.h`, internal helper macros from `wt_internal.h`, POSIX filesystem calls, pthread rwlocks, and the local `queue.h`. It integrates with WiredTiger as a named storage source and with the native file system via `WT_EXTENSION_API->file_system_get`.

## Risks and Edge Cases
The implementation is POSIX-centric: it uses `link`, `chmod`, `stat`, `opendir`, pthread locks, and Unix path semantics. `dir_store_path` strips leading `./` variants but does not fully normalize paths. Cache population races are only partially tolerated through temporary/exclusive copy behavior. Hard-link based caching can fail across file systems. Artificial counters are mostly unsynchronized except for targeted TSAN suppressions. Rename is unsupported, and writes through opened object handles return `ENOTSUP`.

## Test Signals
Useful tests exercise extension loading, custom file-system creation, read-only open behavior, flush and flush_finish, cache hit/miss paths, directory listing with directory/prefix filters, object removal from both cache and bucket, delay/error config, and multi-handle close/termination cleanup. Recovery-style tests should verify that copied bucket objects are immutable and that partial temporary copies are removed after errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/storage_sources/dir_store/dir_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/fail_fs/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/ext/test/fail_fs/CMakeLists.txt

## Purpose
This CMake file builds the fail filesystem test extension as `wiredtiger_fail_fs`.

## Important APIs, Types, and Functions
It declares `fail_fs.c` as the only source, creates a `MODULE` library, adds WiredTiger source, generated include, config, and test utility include directories, applies `${COMPILER_DIAGNOSTIC_C_FLAGS}`, and links `test_util`.

## Control Flow
During configuration, CMake records the module target. During build, the target compiles `fail_fs.c` with access to WiredTiger extension headers and test utility helpers, then links the test utility library.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is a loadable module artifact used by tests.

## Dependencies and Integration Points
The target depends on generated headers under `${CMAKE_BINARY_DIR}`, core headers under `${CMAKE_SOURCE_DIR}/src/include`, and `test_util` for assertions and test support used by the source.

## Risks and Edge Cases
The extension is always built as a module here, so platforms or configurations that do not support module loading need separate handling elsewhere. Missing `test_util` or generated include directories will break the build.

## Test Signals
Build-system validation is enough for this file: the `wiredtiger_fail_fs` target should configure, compile, and produce a loadable extension in test builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/fail_fs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/fail_fs/fail_fs.c -->
# sources/storage-engines/wiredtiger/ext/test/fail_fs/fail_fs.c

## Purpose
This file implements a WiredTiger test file-system extension that injects read or write failures. It is intended for POSIX test environments and can fail after configured operation counts or under environment-variable control.

## Important APIs, Types, and Functions
`FAIL_FILE_SYSTEM` embeds `WT_FILE_SYSTEM`, stores a global pthread rwlock, fail counters, configuration flags, a file-handle queue, and the `WT_EXTENSION_API`. `FAIL_FILE_HANDLE` embeds `WT_FILE_HANDLE`, stores the owning filesystem and POSIX fd, and is queued for cleanup.

The public vtable is filled in `wiredtiger_extension_init` and registered through `WT_CONNECTION->set_file_system`. Handle methods are `fail_file_read`, `fail_file_write`, `fail_file_size`, `fail_file_truncate`, `fail_file_sync`, `fail_file_lock`, and `fail_file_close`. Filesystem methods include open, remove, rename, exist, size, directory list/free, and terminate. `fail_fs_simulate_fail` returns `EIO` and optionally prints a backtrace.

## Control Flow
Initialization parses `environment`, `verbose`, `allow_writes`, and `allow_reads` through the WiredTiger config parser. If fixed allowances are non-zero, failures are enabled immediately. If `environment` is set, each read/write checks `WT_FAIL_FS_ENABLE` and refreshes `WT_FAIL_FS_READ_ALLOW` or `WT_FAIL_FS_WRITE_ALLOW` when failure mode is newly enabled.

Reads and writes take the global lock to update counters and decide whether to fail. If no failure is injected, the lock is released and POSIX `pread`/`pwrite` performs the actual I/O in chunks capped at 1 GiB. Opens translate WiredTiger flags into POSIX flags, support directory handles with fd `-1`, allocate a wrapper handle, install the handle vtable, and add it to the queue. Termination removes all remaining handle structures and destroys the lock.

## State and Persistence Behavior
The extension persists data through the host file system using direct POSIX calls. It does not buffer or journal data itself, and `fh_sync` is a no-op. Runtime counters and `fail_enabled` are in-memory only. Directory listing is based on the extension's open handle queue rather than scanning the underlying directory, which matches test needs but is not a full filesystem implementation.

## Dependencies and Integration Points
The file depends on `wiredtiger_ext.h`, POSIX I/O, pthread rwlocks, `execinfo.h` for backtraces, `queue.h`, and `test_util.h`. It integrates as the process-wide WiredTiger file system replacement for a connection.

## Risks and Edge Cases
This is not portable to Windows and intentionally assumes test-only behavior. `fail_file_close` returns early for directory handles without removing the handle from the queue, so directory-handle lifetime relies on later termination cleanup. `fail_fs_remove` and `fail_fs_rename` return raw POSIX results, not normalized `errno` values. Environment parsing treats invalid values as zero. Directory listing filters names against queued open handles and has a prefix comparison that does not strip the directory component.

## Test Signals
Tests should cover fixed read/write failure counts, environment-driven toggling, verbose backtrace emission, successful I/O before failure thresholds, 1 GiB chunked I/O paths, open/close queue cleanup, and registration through `set_file_system`. Failure-path tests should verify WiredTiger sees `EIO` at the expected operation count.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/fail_fs/fail_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/key_provider/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/ext/test/key_provider/CMakeLists.txt

## Purpose
This CMake file builds the WiredTiger test key-provider extension, either as a standalone module or as object files for builtin extension builds.

## Important APIs, Types, and Functions
It defines the configuration option `HAVE_BUILTIN_EXTENSION_KEY_PROVIDER`, lists `key_provider.h` and `key_provider.c`, selects `OBJECT` linkage when builtin support is enabled and `MODULE` otherwise, and adds WiredTiger generated/source include directories.

## Control Flow
At configure time, `config_bool` exposes the builtin option. The target `wiredtiger_key_provider` is then created with linkage based on that option and include paths are attached.

## State and Persistence Behavior
The file has no runtime state. Its persistent effect is the build artifact type and the generated `HAVE_BUILTIN_EXTENSION_KEY_PROVIDER` configuration symbol used by the C source.

## Dependencies and Integration Points
It integrates with the main CMake configuration through `config_bool` and with the C source through the builtin macro that suppresses the external `wiredtiger_extension_init` symbol when needed.

## Risks and Edge Cases
The target does not link extra libraries directly; it expects the surrounding build to provide extension API symbols. Misconfiguring builtin mode could lead to duplicate extension-init symbols or missing module entry points.

## Test Signals
Build tests should validate both configurations: normal module loading exports `wiredtiger_extension_init`, while builtin builds compile object files and expose `key_provider_extension_init` without symbol conflicts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/key_provider/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.c -->
# sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.c

## Purpose
This file implements a mock `WT_KEY_PROVIDER` extension for testing encryption key management, including key loading, pull-mode key rotation, push-mode key update confirmation, expiration, and registration.

## Important APIs, Types, and Functions
The central object is `KEY_PROVIDER`, declared in the header and cast to `WT_KEY_PROVIDER`. The vtable is filled with `kp_load_key`, `kp_get_key`, `kp_on_key_update`, and `kp_terminate`. `key_provider_extension_init` is the common initializer; `wiredtiger_extension_init` wraps it for module builds unless builtin mode is configured.

Important helpers are `kp_set_key`, `kp_free_key`, `kp_timestamp`, `kp_key_expired`, `kp_generate_key`, `kp_rotate_key`, `kp_configure`, and `configure_int`. Logging macros route messages through `WT_EXTENSION_API`.

## Control Flow
Initialization allocates `KEY_PROVIDER`, sets default verbosity and a 12 hour expiration, installs the default key, parses `version`, `verbose`, and `key_expires`, installs the key-provider vtable, and calls `WT_CONNECTION->set_key_provider`. The first key is marked for one-shot expiration by negating `key_expires`, which causes the next `get_key` call to rotate.

In pull mode (`version=0`), `kp_get_key` is a two-call state machine. If the caller provides no key buffer and the key expired, the provider generates a new key, reports its size, and moves from `KEY_STATE_CURRENT` to `KEY_STATE_PENDING`. The next call provides a correctly sized buffer; the provider copies key bytes and moves to `KEY_STATE_READ`. `kp_on_key_update` then confirms the LSN and returns to `KEY_STATE_CURRENT`. `kp_load_key` loads persisted checkpoint key material and resets expiration.

In push mode (`version=1`), `on_key_update` accepts the confirmed key and enforces strictly increasing timestamp and LSN before adopting it. The provider registers with `set_key_provider` using `version=1`.

## State and Persistence Behavior
The provider stores current key bytes, size, LSN, timestamp, state-machine state, and key creation time in memory. It does not persist keys itself; WiredTiger persists key material in checkpoint metadata and passes it back through `load_key`. Generated test keys combine a default prefix and ISO8601 timestamp pattern repeated to a randomized size around 1024 bytes.

## Dependencies and Integration Points
The file depends on `wiredtiger_ext.h`, the `WT_KEY_PROVIDER` contract, C runtime allocation/string/time APIs, and Windows `FILETIME` support where applicable. It integrates with WiredTiger encryption/checkpoint logic through `set_key_provider`, `WT_CRYPT_KEYS`, LSN/timestamp fields, and update callbacks.

## Risks and Edge Cases
Assertions enforce state ordering, key-size matches, default-prefix expectations in pull mode, and monotonic LSN/timestamp in push mode; tests compiled without assertions may miss misuse. `localtime` and `rand` are simple test choices rather than production-grade key generation. Expiration uses `clock()` on non-Windows systems, so it measures process CPU time rather than wall-clock time. The provider has no explicit locking, so callers must respect WiredTiger's expected serialization for key-provider callbacks.

## Test Signals
Tests should cover initial one-shot expiration, unchanged-key responses, size/data paired pull-mode calls, successful and failed `on_key_update`, persisted-key loading, push-mode monotonic timestamp/LSN checks, config parsing errors, and termination freeing key memory.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.h -->
# sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.h

## Purpose
This header declares the test key provider's public structure, state enum, configuration semantics, and initialization function.

## Important APIs, Types, and Functions
`KEY_STATE` defines `KEY_STATE_CURRENT`, `KEY_STATE_PENDING`, and `KEY_STATE_READ`, documenting the pull-mode key-rotation state machine. `KEY_PROVIDER` embeds `WT_KEY_PROVIDER`, stores `WT_EXTENSION_API`, config fields (`version`, `verbose`, `key_expires`), and simulated key state (`lsn`, `timestamp`, `key_state`, `key_time`, `key_size`, `key_data`). `key_provider_extension_init` is declared for direct or builtin initialization.

## Control Flow
The comments describe valid callback sequences: unchanged current key stays current; expired current key moves to pending on size request, read on data request, and current on update confirmation; `key_load` can reload current persisted data. Push mode bypasses this state machine and relies on pushed keys and update callbacks.

## State and Persistence Behavior
The header defines only in-memory fields. Persisted key state is represented indirectly by the `WT_CRYPT_KEYS` values passed into load/update callbacks.

## Dependencies and Integration Points
It includes `wiredtiger_ext.h` and uses `extern "C"` guards for C++ compatibility. The structure layout relies on `WT_KEY_PROVIDER` being the first field so casts between interface and implementation are valid.

## Risks and Edge Cases
Any source changes that move `iface` away from the first field would break the vtable cast pattern. The header documents strict state transitions that the C file enforces mostly through assertions.

## Test Signals
Header-level validation comes from compiling module and builtin users, plus tests that include the header and call `key_provider_extension_init` directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/ext/test/key_provider/key_provider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/lang/python/CMakeLists.txt

## Purpose
This CMake file builds the WiredTiger Python API through SWIG, links it to a PIC-capable WiredTiger library, arranges the package layout, and defines a Python smoke test.

## Important APIs, Types, and Functions
The file selects `wiredtiger_static` when `ENABLE_STATIC` and `WITH_PIC` are set, otherwise `wiredtiger_shared` when `ENABLE_SHARED` is available; if neither exists, it emits a fatal error. It configures SWIG flags for Python 3, threads, optimization, no default constructors/destructors, generated include paths, and a fixed interface name `_wiredtiger`.

The target is created by `swig_add_library(wiredtiger_python TYPE SHARED LANGUAGE python SOURCES wiredtiger.i)`. Compiler-warning suppressions are selected for Clang, MSVC, or GCC-like compilers. Post-build commands copy `wiredtiger/init.py` to `wiredtiger/__init__.py` and generated `wiredtiger.py` to `wiredtiger/swig_wiredtiger.py`.

## Control Flow
Configuration chooses the link target, assembles SWIG and compiler flags, declares the SWIG module, links against WiredTiger and `Python3::Python`, copies the Python package directory into the binary tree, fixes the output name to `wiredtiger` so SWIG's underscore convention yields `_wiredtiger`, and sets `.so` suffix on Darwin. It also makes the Python module depend on `wiredtiger_ext`.

## State and Persistence Behavior
The file creates build-tree package files and a shared extension module. It does not own runtime state, but its post-build copies determine the import-time package shape used by tests and consumers.

## Dependencies and Integration Points
It depends on CMake SWIG integration, Python3, WiredTiger static/shared targets, generated `wiredtiger.h`, generated config headers, and the `wiredtiger_ext` umbrella target. The smoke test runs `examples/python/ex_access.py` with `PYTHONPATH` pointing at the binary package directory.

## Risks and Edge Cases
The Python API requires either a shared WiredTiger build or a PIC static build. SWIG warning suppressions are compiler-specific and can drift as compilers change. The fixed module names are important: changing output/copy names can break `wiredtiger.init.py` imports. Darwin suffix handling exists because dynamic loader behavior differs for Python modules.

## Test Signals
`test_ex_access` is the built-in smoke signal on POSIX. Build validation should confirm `_wiredtiger.so`, `wiredtiger/__init__.py`, and `wiredtiger/swig_wiredtiger.py` are present and importable from the binary tree.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/run-ex_access -->
# sources/storage-engines/wiredtiger/lang/python/run-ex_access

## Purpose
This shell script is a small legacy runner for the Python `ex_access.py` example.

## Important APIs, Types, and Functions
It uses `PYTHON=${PYTHON:-python3}`, recreates `WT_TEST`, then executes Python with `LD_LIBRARY_PATH`, `DYLD_LIBRARY_PATH`, and `PYTHONPATH` configured for an in-tree build.

## Control Flow
The script removes and recreates `WT_TEST`, then replaces itself with `env ... ${PYTHON} -S ${srcdir}/../../examples/python/ex_access.py`.

## State and Persistence Behavior
It deletes any existing local `WT_TEST` directory and creates a fresh one for the example. It otherwise relies on the example and WiredTiger library for persistent state.

## Dependencies and Integration Points
It depends on `/bin/sh`, `srcdir`, the Python extension in the current and source directories, and shared libraries under `../../.libs`. It is parallel in purpose to the CMake `test_ex_access` smoke test but follows autotools-style paths.

## Risks and Edge Cases
If `srcdir` is unset or the build layout does not contain `../../.libs`, the script will fail. It unconditionally removes `WT_TEST` in the current directory. It uses `-S`, so imports must work without site initialization.

## Test Signals
Successful execution of the example is the main signal. Failure to import `wiredtiger` indicates path or library-loading problems.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/run-ex_access -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/setup_pip.py -->
# sources/storage-engines/wiredtiger/lang/python/setup_pip.py

## Purpose
This setuptools script builds and packages the WiredTiger Python module for `pip`, including a CMake/Ninja WiredTiger build and the SWIG-generated Python extension.

## Important APIs, Types, and Functions
Top-level helpers are `msg`, `die`, `build_commands`, `get_compile_flags`, `get_sources_curdir`, `get_wiredtiger_versions`, and `get_library_dirs`. `BinaryDistribution` marks the package as non-pure. `WTBuildExt` runs CMake and Ninja once, guarded by `built.txt`, before invoking normal extension build. `WTInstall` runs `build_ext` and moves generated `wiredtiger.py` into the install build as `wiredtiger/swig_wiredtiger.py`.

The `Extension` is named `_wiredtiger`, compiles the generated SWIG C source for normal builds, links against `cmake_pip_build/libwiredtiger.a`, and uses generated include/config directories.

## Control Flow
The script determines whether it is running from `lang/python` or the WiredTiger root, rejects 32-bit Python and Windows, reads the WiredTiger version from `RELEASE_INFO`, defines CMake/Ninja commands for a static PIC Python-enabled build, and computes compiler/linker flags. For `sdist`, it requires Python 3, stages files from `git ls-tree`, copies package Python files to the stage root, renames `init.py` to `__init__.py`, and runs setup with a dist directory under `lang/python/dist`. For install/build, `build_ext` configures and builds the underlying WiredTiger artifacts before setuptools builds the extension.

## State and Persistence Behavior
The script creates `cmake_pip_build`, `built.txt`, source distribution staging under `lang/python/stage`, and dist artifacts. It mutates the working directory depending on invocation and removes the staging directory after `sdist`.

## Dependencies and Integration Points
It depends on setuptools, CMake, Ninja, SWIG-generated files, Git for source listing, `RELEASE_INFO`, `README`, and a POSIX shell for build commands. It integrates with the Python package layout by installing `_wiredtiger` under the `wiredtiger` package and using `swig_wiredtiger.py` as the generated Python wrapper.

## Risks and Edge Cases
The script shells out through `sh -c` for configured commands and is intentionally unsupported on Windows. `get_wiredtiger_versions` uses `exec` on trusted `RELEASE_INFO` assignment lines. `sdist` requires a Git repository and copies all tracked files, which can be large. The build sentinel can hide configuration changes unless the build directory is cleaned.

## Test Signals
Signals include `python setup_pip.py sdist`, `pip install` from the generated source distribution, successful CMake/Ninja builds, import of `wiredtiger`, and presence of `wiredtiger/swig_wiredtiger.py` in the installed package.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/setup_pip.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/fpacking.py -->
# sources/storage-engines/wiredtiger/lang/python/wiredtiger/fpacking.py

## Purpose
This module implements fixed-size WiredTiger packing/unpacking on top of Python's `struct` library.

## Important APIs, Types, and Functions
The main functions are `pack(fmt, *values)` and `unpack(fmt, s)`. The helper `__wt2struct` maps WiredTiger fixed-size format strings to Python struct format strings, defaults to big-endian/no-alignment, and maps WiredTiger record-number `r` to unsigned 64-bit `Q`.

## Control Flow
`unpack` walks the format string, accumulating fixed struct fields until it reaches special string/raw fields. `S` is unpacked as a NUL-terminated string, while `u` is either the remaining bytes when final or a length-prefixed raw byte array when followed by more fields. `pack` constructs a struct format by translating `S` to fixed string data with a terminating NUL and translating non-final `u` values into an inserted length plus bytes.

## State and Persistence Behavior
The module is stateless. Its persistent effect is byte-level compatibility with WiredTiger's fixed encoding for keys/values used by Python callers.

## Dependencies and Integration Points
It depends on Python `struct` and `wiredtiger.packing.empty_pack`. It complements `packing.py`, which implements variable-length encoding.

## Risks and Edge Cases
The code assumes string-like values support `.find('\0')` and byte slicing in ways that differ between Python 2 history and Python 3. For `S`, embedded NUL data is truncated to the first NUL plus terminator. Malformed buffers can raise `struct` exceptions or produce odd slices if a NUL terminator is missing.

## Test Signals
Round-trip tests for scalar fields, endian prefixes, `r`, fixed-size strings, NUL-terminated strings with embedded NULs, final and non-final `u`, and empty formats provide useful coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/fpacking.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/init.py -->
# sources/storage-engines/wiredtiger/lang/python/wiredtiger/init.py

## Purpose
This file is installed as `wiredtiger/__init__.py`. It imports the binary `_wiredtiger` extension and the SWIG-generated Python wrapper, then re-exports wrapper symbols in the package namespace.

## Important APIs, Types, and Functions
`restart_python` restarts the current interpreter with the same arguments after modifying the environment. The module checks that its installed basename is `__init__.py` or `__init__.pyc`, rejects Python 2, appends its directory to `sys.path`, handles optional ThreadSanitizer preload setup, imports `_wiredtiger` and `swig_wiredtiger`, and copies every name from `swig_wiredtiger` onto the package module.

## Control Flow
On import, the module validates installation and Python version. If `TESTUTIL_TSAN=1`, it runs `clang --print-file-name libtsan.so.2` without `LD_PRELOAD`, updates `LD_PRELOAD` if needed, and restarts Python so the sanitizer library is loaded. If the current process already has TSan loaded, it removes that path from `LD_PRELOAD` without restarting to avoid breaking subprocesses. Finally, it imports and re-exports SWIG symbols.

## State and Persistence Behavior
The module mutates `sys.path`, `os.environ["LD_PRELOAD"]`, and the `wiredtiger` module namespace. It can replace the running process through `os.execl`.

## Dependencies and Integration Points
It depends on `_wiredtiger.so`, `swig_wiredtiger.py`, Python `os` and `sys`, and optionally `subprocess` plus `clang` for sanitizer discovery. It is tightly coupled to the CMake and pip packaging files that create the expected package layout.

## Risks and Edge Cases
Import-time process restart is powerful and can surprise embedding environments. The TSan path assumes a Clang-compatible setup and Linux-style `libtsan.so.2`. Adding the package directory to `sys.path` is a workaround for SWIG import behavior but can affect import resolution. If this file is run in the source tree instead of installed as `__init__.py`, it exits.

## Test Signals
Tests should import `wiredtiger` from the build tree and installed package, verify core SWIG symbols are visible at package level, exercise non-TSan and TSan environment branches where practical, and verify Python 2 rejection is no longer relevant but intentional.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/init.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/intpacking.py -->
# sources/storage-engines/wiredtiger/lang/python/wiredtiger/intpacking.py

## Purpose
This module implements WiredTiger's variable-length integer encoding and decoding for signed and unsigned values up to 64 bits.

## Important APIs, Types, and Functions
Constants define marker ranges for negative multi-byte, negative two-byte, negative one-byte, positive one-byte, positive two-byte, and positive multi-byte encodings. `pack_int(x)` encodes an integer into ordered bytes. `unpack_int(b)` decodes one integer and returns `(value, remaining_bytes)`. Helpers `getbits` and `get_int` manipulate bit fields and big-endian byte sequences.

## Control Flow
Small negative and positive values are encoded entirely in marker bytes or marker plus one byte. Larger values are normalized, packed as big-endian unsigned 64-bit, and trimmed of redundant leading `0xff` or `0x00` bytes. Decoding inspects the first marker byte to select the inverse transformation and consumes the corresponding number of following bytes.

## State and Persistence Behavior
The module is stateless. Its output bytes are persistent data when used to encode WiredTiger keys/values and are designed to preserve numeric ordering under byte comparison.

## Dependencies and Integration Points
It depends on Python `struct`, `math` and `sys` imports, and compatibility helpers `_chr`, `_ord`, `x00_entry`, and `xff_entry` from `packutil`. `packing.py` uses `pack_int` and `unpack_int` for variable-length integral fields and raw-length prefixes.

## Risks and Edge Cases
The self-test block uses Python 2 style `cmp` and bare `print` behavior, so it is historical and not a reliable Python 3 test without adjustment. Values outside the intended signed/unsigned 64-bit range are not explicitly rejected. Byte/string compatibility depends on `packutil` behavior.

## Test Signals
Round-trip tests should cover all marker boundaries: `NEG_2BYTE_MIN`, `NEG_1BYTE_MIN`, `-1`, `0`, `POS_1BYTE_MAX`, `POS_2BYTE_MAX`, `POS_2BYTE_MAX + 1`, and large positive/negative values. Ordering tests should compare integer order to encoded byte order.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/intpacking.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/packing.py -->
# sources/storage-engines/wiredtiger/lang/python/wiredtiger/packing.py

## Purpose
This module implements WiredTiger's variable-length format packing and unpacking for Python callers.

## Important APIs, Types, and Functions
The public functions are `pack(fmt, *values)` and `unpack(fmt, s)`. `__get_type` parses the optional format type prefix and only accepts variable-length encoding (`.`). `__unpack_iter_fmt` parses repeat counts and format characters. `__pack_iter_fmt` pairs parsed format elements with input values. The module relies on `pack_int` and `unpack_int` for integral encoding.

## Control Flow
`unpack` parses each format item. Padding advances over bytes. `S`, `s`, `U`, and `u` decode fixed-size, NUL-terminated, remaining-byte, or length-prefixed data as appropriate. `t` returns one byte as a bit field. `B` and `b` decode unsigned or signed-order-preserving bytes. Other integral fields repeatedly call `unpack_int`.

`pack` mirrors this logic. It emits padding bytes, truncates or pads fixed-size strings, NUL-terminates unsized `S`, length-prefixes non-final `u` and internal `U`, validates bit-field width/value, translates signed bytes by adding `0x80`, and variable-encodes all other integers.

## State and Persistence Behavior
The module is stateless. Packed bytes are persistent application data and must remain compatible with WiredTiger's C encoding semantics.

## Dependencies and Integration Points
It depends on `packutil` for Python 2/3 byte compatibility and `intpacking` for variable integer encoding. It is part of the `wiredtiger` package exported through `init.py`.

## Risks and Edge Cases
Only variable-length encoding is supported; other prefixes raise `ValueError`. `pack` returns `()` for empty formats, while `empty_pack` is bytes elsewhere, which callers must tolerate. String handling mixes `str`, `bytes`, and `.encode()` decisions. Malformed packed input can exhaust bytes or raise low-level exceptions. Bit fields larger than 8 bits are rejected.

## Test Signals
Round-trip tests should cover every documented format character, repeat counts, empty formats, string truncation/padding, NUL-terminated `S`, final versus non-final `u`, `U`, bit-field validation, signed byte ordering, and rejection of non-variable prefixes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/packing.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/packutil.py -->
# sources/storage-engines/wiredtiger/lang/python/wiredtiger/packutil.py

## Purpose
This module provides byte/string compatibility helpers and constants for WiredTiger Python packing code.

## Important APIs, Types, and Functions
It defines `x00`, `xff`, `x00_entry`, `xff_entry`, and `empty_pack`. For Python 3, `_ord` returns an integer byte unchanged, `_chr` returns `bytes`, `_is_string` checks `str`, and `_string_result` decodes bytes. The Python 2 branch uses `ord`, `chr`, `unicode`, and string returns.

## Control Flow
At import, `_python3` selects one of two helper implementations. Packing modules call these helpers instead of directly using Python-version-specific byte operations.

## State and Persistence Behavior
The module has no mutable runtime state. It standardizes byte output for the persistent encodings emitted by `packing.py` and `intpacking.py`.

## Dependencies and Integration Points
It depends only on `sys`. It is imported by `packing.py` and `intpacking.py`.

## Risks and Edge Cases
Although `init.py` rejects Python 2, this module still carries Python 2 code. `_string_result` decodes with the default UTF-8 codec, which can fail for arbitrary binary data if used on non-text strings. `_chr` supports at most two byte arguments, matching current callers but not a general byte builder.

## Test Signals
Tests should verify helper return types under Python 3, constants, `_chr` one- and two-byte forms, `_ord` on indexed bytes, and text decoding behavior for packed string fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/lang/python/wiredtiger/packutil.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/oss/apple/ulock.h -->
# sources/storage-engines/wiredtiger/oss/apple/ulock.h

## Purpose
This header provides Apple `ulock` declarations, operation codes, flags, and masks used by code that needs private Apple unfair-lock or compare-and-wait primitives.

## Important APIs, Types, and Functions
Under `PRIVATE`, it declares `__ulock_wait`, `__ulock_wait2`, and `__ulock_wake` for user space when not compiling the kernel. It defines operation codes such as `UL_COMPARE_AND_WAIT`, `UL_UNFAIR_LOCK`, 64-bit/shared variants, obsolete aliases, and debug-only operation IDs. It defines wait flags, wake flags, generic flags, and masks including `UL_OPCODE_MASK`, `UL_FLAGS_MASK`, `ULF_WAIT_MASK`, and `ULF_WAKE_MASK`.

`ulock_owner_value_to_port_name` maps a user-space owner value to a Mach port name; kernel-private builds call `ipc_entry_name_mask`, while non-kernel private code ORs in low bits.

## Control Flow
The header is almost entirely declarative. Preprocessor branches select kernel-private versus non-kernel declarations and inline conversion behavior.

## State and Persistence Behavior
There is no owned state or persistence. The constants define ABI-level bit layouts for syscall operation values.

## Dependencies and Integration Points
It depends on Mach port types, `sys/cdefs.h`, and fixed-width integer types. It is an imported Apple OSS compatibility header and integrates with Darwin-specific synchronization code elsewhere in the tree.

## Risks and Edge Cases
Most content is gated by `PRIVATE`; consumers must compile with the expected Apple feature macros. These are private OS interfaces and may vary across macOS releases. Miscombining operation and flag bits can call the wrong kernel operation.

## Test Signals
Compile coverage on Darwin is the primary signal. Runtime tests belong to the synchronization layer that includes this header, verifying wait/wake behavior and flag combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/oss/apple/ulock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_addr.c -->
# sources/storage-engines/wiredtiger/src/block/block_addr.c

## Purpose
This file implements block address-cookie packing, unpacking, validation, string formatting, and checkpoint-cookie encoding/decoding for WiredTiger's block manager.

## Important APIs, Types, and Functions
`__wt_block_addr_pack` and `__wt_block_addr_unpack` convert between offset/size/checksum/object-id tuples and variable-length address cookies. `__wt_block_addr_invalid` validates cookies against file size and, in diagnostic builds, extent-list placement. `__wt_block_addr_string` formats cookies for diagnostics.

Checkpoint functions include internal `__block_ckpt_unpack`, public/internal `__wti_block_ckpt_unpack`, external utility `__wt_block_ckpt_decode`, `__wti_block_ckpt_pack`, and `__wti_ckpt_verbose`. `WT_BLOCK_COOKIE_FILEID` marks optional appended object IDs.

## Control Flow
Address packing stores offset as allocation units minus one, size as allocation units, and checksum as a variable integer. A zero size encodes an invalid/empty address. Non-zero object IDs append a flag byte and packed object ID. Unpacking reverses this process and can optionally skip object-ID parsing when checkpoint cookies pass address-cookie size zero.

Checkpoint cookies start with a version byte, then four address blocks for root, alloc, avail, and discard extent lists, then file size and checkpoint size. One optional object ID at the end applies to all four address blocks. Verbose formatting cracks a checkpoint and builds a readable string with empty/non-empty extent descriptions.

## State and Persistence Behavior
The packed cookies are persistent on-disk metadata. Their compact encoding depends on `block->allocsize`, so unpacking must use the correct block handle. Object IDs support tiered storage references while preserving compatibility for object ID zero.

## Dependencies and Integration Points
The file depends on `wt_internal.h`, WiredTiger variable integer packing helpers, `WT_BLOCK`, `WT_BLOCK_CKPT`, extent-list structures, and verbose infrastructure. It is used by block I/O, checkpoint management, verify, salvage, compaction, and external utilities that decode checkpoints.

## Risks and Edge Cases
Address-cookie compatibility is critical: changing flag semantics or allocation-unit math can make existing files unreadable. The checkpoint special case where address-cookie size zero suppresses object-ID parsing is subtle. Validation only checks current-object file bounds; addresses for other objects are not bounded by `block->size`. Future cookie flags must preserve the assertion rules around consumed bytes.

## Test Signals
Tests should round-trip address cookies with empty addresses, object ID zero, non-zero object IDs, multiple allocation sizes, and maximum-ish offsets. Checkpoint tests should round-trip full cookies, reject unsupported versions, verify verbose output, and validate file-size boundary errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_addr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_ckpt.c -->
# sources/storage-engines/wiredtiger/src/block/block_ckpt.c

## Purpose
This file owns block-manager checkpoint lifecycle: loading/unloading checkpoint extent state, writing new checkpoint cookies, deleting and merging old checkpoint extent lists, maintaining incremental-backup block-modification bitmaps, and resolving checkpoint completion.

## Important APIs, Types, and Functions
Public/internal entry points include `__wti_block_ckpt_init`, `__wti_block_ckpt_destroy`, `__wt_block_checkpoint_load`, `__wt_block_checkpoint_unload`, `__wt_block_checkpoint_start`, `__wt_block_checkpoint`, `__wt_block_checkpoint_resolve`, and `__wti_block_checkpoint_extlist_dump`.

Major helpers are `__ckpt_process`, `__ckpt_validate_state`, `__ckpt_read_deletion_extlists`, `__ckpt_delete_and_merge`, `__ckpt_update_live`, `__ckpt_update`, `__ckpt_live_blkmods`, `__ckpt_add_blk_mods_ext`, and `__ckpt_mod_blkmod_entry`.

## Control Flow
Loading initializes either a temporary checkpoint structure or `block->live`, unpacks the checkpoint cookie, optionally sets up verify, returns the root page address, reads the live avail list, and truncates writable files to the checkpoint file size. Unloading the live checkpoint truncates to current size, destroys live extent lists, and clears `live_open`.

A normal checkpoint starts by moving `ckpt_state` from `WT_CKPT_NONE` to `WT_CKPT_INPROGRESS`. `__wt_block_checkpoint` writes the root page if present, switches to first-fit allocation, preallocates extent structures, and calls `__ckpt_process`. Processing validates state and changes it to `WT_CKPT_PANIC_ON_FAILURE`, reinitializes checkpoint lists, reads deletion extent lists before taking `live_lock`, records incremental backup bits, merges deleted checkpoints into subsequent checkpoints, updates affected checkpoint cookies, updates the live checkpoint, and leaves newly reusable blocks in `ckpt_avail` until resolve.

Resolve runs after upper layers have written checkpoint metadata durably. If the checkpoint succeeded, it merges `ckpt_avail` into the live avail list and frees checkpoint-temporary lists; if the failure occurs after the panic-on-failure point, it panics and marks the block manager readonly.

## State and Persistence Behavior
Checkpoint cookies persist root addresses, extent-list addresses, file size, and checkpoint size. Live state includes alloc, avail, discard, and checkpoint-temporary extent lists. The two-phase protocol prevents blocks freed by deleted checkpoints from being reused until the new checkpoint locations are durable. Incremental backup state is persisted as block-modification bitmaps in checkpoint structures. The code also maintains `created_during_backup`, `live_open`, and `ckpt_state` as in-memory coordination state.

## Dependencies and Integration Points
The file depends on block extent-list APIs, block write/truncate/allocation/free functions, metadata checkpoint-list conversion, verify checkpoint hooks, spin locks, diagnostic flags, stats, and backup block-modification structures. It sits between the btree checkpoint layer and low-level block allocation.

## Risks and Edge Cases
The fatal section in `__ckpt_process` cannot safely roll back merged extent lists, so errors panic the system. Tiered storage object IDs require skipping non-local checkpoint extent lists. Intermediate checkpoint rewrite has a documented file-size limitation if an API ever rolls forward intermediate checkpoints. Correct lock ownership around `block->live_lock` is essential. Bitmap granularity clearing only clears full ranges and must avoid off-by-one errors at range edges.

## Test Signals
Coverage should include empty and non-empty roots, load/unload of live and readonly checkpoints, deletion of one or multiple checkpoints, fake checkpoint entries, tiered/non-local checkpoint skipping, resolve success/failure, incremental backup bitmap set/clear behavior, diagnostic extent overlap checks, and simulated failures after entering the fatal checkpoint window.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_ckpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_ckpt_scan.c -->
# sources/storage-engines/wiredtiger/src/block/block_ckpt_scan.c

## Purpose
This file supports standalone recovery/import of WiredTiger files by embedding final metadata/checkpoint information in the last avail-list block and scanning a file to recover the newest such checkpoint.

## Important APIs, Types, and Functions
`__wti_block_checkpoint_final` appends write generation, placeholder file size, metadata, checkpoint-list string, and incomplete checkpoint cookie to the final avail-list buffer. `__wt_block_checkpoint_last` scans the file for the latest final checkpoint block and returns recovered metadata, checkpoint list, and corrected checkpoint cookie. `__block_checkpoint_update` patches the recovered checkpoint cookie with the actual avail-list address/checksum and file size.

`struct saved_block_info` tracks write generation, block address, file size, metadata, checkpoint list, and checkpoint cookie while scanning.

## Control Flow
During checkpoint writing, `__wti_block_checkpoint_final` extends the avail-list buffer, writes an incremented btree write generation, reserves `WT_INTPACK64_MAXSIZE` bytes for final file size, appends length-prefixed metadata and checkpoint-list strings, appends the incomplete checkpoint cookie, aligns capacity to allocation size, and returns a pointer to the reserved file-size field for later patching before checksum/write.

During scanning, `__wt_block_checkpoint_last` initializes scratch buffers, marks the session quiet for corrupt-file reads, walks the file by block sizes, reads candidate blocks, validates checksums through `__wti_block_read_off`, filters for block-manager pages containing extent lists with `WT_BLOCK_EXTLIST_VERSION_CKPT`, unpacks write generation and appended strings/cookie, and keeps the highest generation fully read. It then patches the checkpoint cookie and returns owned metadata/checkpoint strings to the caller.

## State and Persistence Behavior
The appended final checkpoint payload is persistent inside a block-manager extent-list page. It provides enough metadata to open a standalone file if the database metadata is missing. The scan is read-only but allocates owned strings and scratch buffers.

## Dependencies and Integration Points
The file depends on block page headers, extent-list pair encoding, variable integer packing, block read/checksum validation, metadata checkpoint format, session progress reporting, and checkpoint packing from `block_addr.c`.

## Risks and Edge Cases
Scanning intentionally ignores many corrupt or invalid blocks and leaves deeper corruption to verification. Tiered tables are not supported (`objectid` is fixed to zero). The design relies on the historic extent-list version marker behavior and on write generation monotonicity. Partial appended payloads are skipped unless fully readable. The file-size placeholder must be patched before final checksum or recovered metadata will be wrong.

## Test Signals
Tests should create files with multiple final checkpoint blocks and verify the highest generation is selected, recover metadata/checkpoint strings from standalone files, handle corrupt candidate blocks, reject files with no final checkpoint, and validate that patched avail address/checksum/file-size fields match the scanned block.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_ckpt_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_compact.c -->
# sources/storage-engines/wiredtiger/src/block/block_compact.c

## Purpose
This file implements block-manager compaction decisions, progress estimation, page rewrite support, and verbose file-space diagnostics.

## Important APIs, Types, and Functions
Public entry points are `__wt_block_compact_start`, `__wt_block_compact_end`, `__wt_block_compact_get_progress_stats`, `__wt_block_compact_skip`, `__wt_block_compact_page_skip`, `__wt_block_compact_page_rewrite`, and `__wt_block_compact_progress`.

Important helpers include `__block_compact_trim_extent`, `__block_compact_skip_internal`, `__block_compact_estimate_remaining_work`, `__compact_page_skip`, `__block_dump_file_stat`, and `__block_dump_bucket_stat`.

## Control Flow
Compaction start rejects concurrent compaction on the same block, switches allocation to first-fit, resets progress counters, records the session id, and notifies background compaction when applicable. Skip logic ignores small files, optionally enforces configured free-space targets, stops if the file grew between passes, and checks whether enough free space exists in the first 80 or 90 percent of the file to move data out of the last 20 or 10 percent.

For each page, `__compact_page_skip` unpacks or receives the block address, checks if the page lies beyond the selected compaction limit and whether a suitable earlier free extent exists, updates reviewed/skipped/rewritten counters, and triggers work estimation after at least 1000 reviewed pages. Rewriting reads the old block, allocates a new first-fit block, writes the same bytes at the new offset, frees the original extent, repacks the address cookie, updates stats, and frees the replacement block on error.

## State and Persistence Behavior
Compaction changes persistent block layout by moving pages to earlier offsets and freeing old extents; final truncation opportunities are reflected through checkpoint/avail-list behavior elsewhere. In-memory state on `WT_BLOCK` tracks reviewed/rewritten/skipped pages and bytes, expected rewrite counts, selected compaction percentage, previous size, and owning session. Dry-run mode estimates and cancels without rewriting.

## Dependencies and Integration Points
The file depends on address-cookie unpack/pack, block allocation/free/read/write functions, live extent lists, compact session configuration, background compaction hooks, stats, verbose logging, and `live_lock` synchronization. It is called by higher btree compaction traversal code for page-level decisions.

## Risks and Edge Cases
Compaction decisions are heuristic and can race with concurrent file growth, which causes later passes to skip. Estimation assumes reviewed pages are representative and approximates internal-page overhead. `__compact_page_skip` increments rewrite counters before the actual rewrite succeeds, so counters are progress estimates rather than strict durable moves. Rewriting preserves the original checksum while moving bytes unchanged, so any accidental data modification would be missed until read verification.

## Test Signals
Tests should cover skip thresholds, files under 1 MiB, free-space target behavior, no-progress skip behavior, dry-run cancellation after estimation, successful page rewrite and address update, allocation failure cleanup, background compaction start/end hooks, progress stats, and verbose bucket accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/block/block_compact.c -->
