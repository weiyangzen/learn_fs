# subset-b-009713 research

Grouped research report for the requested NFS-Ganesha gtest, hashtable, and idmapper source files. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_read2_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_read2_latency.cc

## Purpose
This GoogleTest executable measures and sanity-checks FSAL read2/read latency through Ganesha's FSAL object API. It creates a per-test directory named `read2_latency`, opens one regular file with `open2`, writes data through `fsal_write`, then reads the same bytes through `fsal_read`. It compares normal MDCACHE-backed handles with direct sub-handles returned by `mdcdb_get_sub_handle`.

## Important APIs, Types, And Functions
The fixture `Read2EmptyLatencyTest` derives from `gtest::GaneshaFSALBaseTest`, uses `op_ctx->fsal_export->exp_ops.alloc_state` to allocate a `STATE_TYPE_SHARE`, opens `TEST_FILE` with `obj_ops->open2`, and closes it with `obj_ops->close2`. Test bodies allocate `struct fsal_io_arg` plus one `iovec` on the stack via `alloca`, initialize `struct async_process_data`, and call `fsal_write` and `fsal_read`. Timing uses `now` and `timespec_diff`.

## Control Flow, State, And Persistence
`SetUp` starts from the shared environment's export root and creates an opened file object under the per-test root. `TearDown` closes the state, frees it, removes the file, releases the object reference, and delegates root cleanup to the base fixture. `SIMPLE` and `LARGE_DATA_READ` verify returned bytes with `memcmp`; loop tests write a large backing buffer once and then read 64-byte slices while advancing `read_arg->offset`. The tests persist only transient filesystem objects in the configured export and remove them afterward.

## Dependencies And Integration Points
The file depends on Ganesha FSAL headers, `common_utils.h`, MDCACHE debug helpers, Boost program options, pthread condition/mutex primitives for async I/O, and `gtest.hh` for environment setup. Its `main` parses config/log/debug/export/session/event-list/profile flags and registers `gtest::Environment` with `TEST_ROOT`.

## Risks And Test Signals
`LOOP_COUNT` is one million and the loop setup can allocate or write tens of megabytes, so runtime and backend storage behavior matter. `io_data.done` is initialized but not waited on, relying on synchronous behavior from `fsal_read`/`fsal_write` when called with `true`. The bypass cases explicitly skip MDCACHE and can diverge from normal behavior. The strongest correctness signal is byte comparison in normal read paths; bypass tests only assert success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_read2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_correctness.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_correctness.cc

## Purpose
This test validates FSAL `readdir` correctness for a large directory. It creates a directory named `test_directory` under the per-test root, populates it with `DIR_COUNT` entries, records each created object's key and expected generated name, and confirms that two directory scans return every handle exactly once.

## Important APIs, Types, And Functions
`ReaddirEmptyCorrectnessTest` creates/removes the test directory. `ReaddirFullCorrectnessTest` calls `create_and_prime_many`, records object keys with `obj_ops->handle_to_key`, duplicates them with `keyDup`, and later frees the duplicated key buffers. `rd_state_t` carries the recorded keys, boolean found flags, and names into `trc_populate_dirent`. `keyEQ` compares `gsh_buffdesc` keys by length and bytes.

## Control Flow, State, And Persistence
Setup creates 100,000 regular files under the test directory and stores stable handle keys before releasing each handle reference. It then calls `mdcache_lru_release_entries(-1)` to flush extra cached entries and force a stronger correctness check across cache boundaries. The `BIG` test calls `test_dir->obj_ops->readdir` twice with `whence = 0`, callback state, and `eod`, then asserts all entries were found after each pass and resets flags.

## Dependencies And Integration Points
The test integrates with the shared FSAL fixture, MDCACHE debug support, and object handle key generation. It uses Ganesha allocation (`gsh_malloc`, `gsh_free`) for duplicated key storage and the object callback contract that requires the callback to `put_ref` each provided object.

## Risks And Test Signals
The test is memory-heavy because it stores 100,000 key descriptors and names, and the callback performs a linear scan over all expected keys for each entry, creating O(n^2) behavior. It assumes generated names match `create_and_prime_many`'s `f-%08x` pattern. The disabled bypass test documents that direct sub-handle traversal is not currently compatible with object pointer comparisons. Strong signals are duplicate detection and full-entry coverage over two scans.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_correctness.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_latency.cc

## Purpose
This executable benchmarks empty and populated directory enumeration through both direct object operations and the higher-level `fsal_readdir` helper. It includes normal MDCACHE-backed tests and sub-handle bypass tests.

## Important APIs, Types, And Functions
`ReaddirEmptyLatencyTest` creates one empty directory; `ReaddirFullLatencyTest` extends it by calling `create_and_prime_many(DIR_COUNT, NULL, test_dir)`. `populate_dirent` is the object-operation callback and releases each returned object. `FSALREADDIR` uses the `fsal_readdir` wrapper with the base fixture's static `readdir_callback`.

## Control Flow, State, And Persistence
Empty tests run one million iterations for direct and wrapper calls. Full tests create 100,000 entries and run 1,000 full directory scans. Timing encloses only the measured `readdir` calls; setup and cleanup populate and remove objects outside the measured window. `whence` is initialized to zero and reused, so the exact repeated-scan semantics depend on the FSAL's cookie handling and end-of-directory behavior.

## Dependencies And Integration Points
The file relies on `gtest.hh` for export setup and bulk create/remove helpers, MDCACHE debug helpers for `mdcdb_get_sub_handle`, FSAL object callback contracts, and Boost program option parsing. The test root name is `readdir_latency`.

## Risks And Test Signals
The loop count and directory size make the test an expensive microbenchmark. Reusing `whence` and `eod` across loop iterations may measure cached end-of-directory behavior rather than a cold full scan unless the FSAL resets or ignores those values as expected. Test signals are mostly status assertions and timing output; it does not verify returned entry identity, which is covered by the separate correctness test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readdir_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readlink_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readlink_latency.cc

## Purpose
This test benchmarks FSAL symbolic-link target reads. It creates a symlink under the export root that points at the per-test root name, records its expected link content, and repeatedly invokes `readlink` through object operations, `fsal_readlink`, and MDCACHE bypass sub-handles.

## Important APIs, Types, And Functions
`ReadlinkEmptyLatencyTest` uses `fsal_create(..., SYMBOLIC_LINK, ..., TEST_ROOT, ...)`, `fsal_readlink`, `obj_ops->readlink`, `obj_ops->unlink`, and `gsh_free` for returned `utf8string` storage. `ReadlinkFullLatencyTest` primes the test root with `FILE_COUNT` regular files to measure readlink in a loaded cache/export.

## Control Flow, State, And Persistence
Setup creates `symlink_to_readlink_latency`, reads and stores its target into `bfr_content`, and releases create attributes. Simple tests read the link once and compare byte content with the stored target. Loop tests allocate a new returned target string on each iteration and free it immediately. Teardown frees the stored target string, unlinks the symlink from `root_entry`, releases the symlink handle, and delegates root cleanup to the base fixture.

## Dependencies And Integration Points
The test uses FSAL symlink creation and readlink semantics, MDCACHE sub-handle access, Ganesha memory allocation ownership for returned strings, and the shared Ganesha environment. `main` supports LTTng and profiling arguments but only configures the environment; no explicit profiling calls are used in the tests.

## Risks And Test Signals
The primary risk is allocation churn from one million `readlink` calls, each requiring `gsh_free` of returned content. `BIG_BYPASS` does not assert that `mdcdb_get_sub_handle` returned non-null before use. Correctness checks compare target contents in simple paths; loop paths assert only success and timing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readlink_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_release_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_release_latency.cc

## Purpose
This minimal latency test measures the cost of `obj_ops->release` on the per-test root object. It exists as a narrow microbenchmark for the FSAL handle release path.

## Important APIs, Types, And Functions
`ReleaseEmptyLatencyTest` inherits setup and teardown entirely from `gtest::GaneshaFSALBaseTest`. `SIMPLE` calls `test_root->obj_ops->release(test_root)`. `LOOP` repeats that call one million times and prints average nanoseconds per release with `timespec_diff`.

## Control Flow, State, And Persistence
No additional filesystem objects are created beyond the base fixture's test root. The measured call is unusual because it invokes `release` repeatedly on `test_root`, while base teardown later calls `unlink` and `put_ref` on the same object. The file explicitly notes that release cannot be bypassed.

## Dependencies And Integration Points
The test depends on the FSAL object operation table and shared Ganesha fixture. It parses the standard config/log/debug/export/session/event-list/profile options but does not use LTTng or profiler hooks directly.

## Risks And Test Signals
Repeatedly calling a release-style method on the same object can be dangerous if the operation mutates reference state, invalidates cached resources, or is not idempotent. The test signal is only that the process survives and prints timing; there is no status return or invariant assertion for `release`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_release_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_rename_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_rename_latency.cc

## Purpose
This executable benchmarks FSAL rename operations for an individual file in empty and populated directories. It compares direct object operations, the `fsal_rename` wrapper, and MDCACHE bypass sub-handles.

## Important APIs, Types, And Functions
Fixtures derive from `GaneshaFSALBaseTest`; `RenameFullLatencyTest` adds 100,000 primed entries. Tests use `fsal_create`, `obj_ops->rename`, `fsal_rename`, `obj_ops->lookup`, `fsal_remove`, and `mdcdb_get_sub_handle`. File names are held in fixed `NAMELEN` buffers and generated with `sprintf("nf-%08x", i)`.

## Control Flow, State, And Persistence
Simple tests create `original_name`, rename it to `new_name`, verify lookup returns the same handle, then remove it. Loop tests create one file and repeatedly rename that single object to a new name, updating the current-name buffer after each successful call. Full tests do the same while extra directory entries exist. Teardown for full tests removes the primed entries after the benchmark-created file is cleaned up.

## Dependencies And Integration Points
The file exercises FSAL rename semantics, wrapper-vs-object-operation layering, MDCACHE bypass handling, and directory lookup behavior. It uses the shared test root named `test_root`, which is generic and may be less distinctive than other latency tests.

## Risks And Test Signals
The loop uses `sprintf`/`strncpy` into `NAMELEN` buffers; current generated names fit, but changing name formats could truncate. `SIMPLE_BYPASS` compares lookup and sub-handle object pointers, which depends on bypass identity behavior. The main correctness signals are successful rename status and lookup identity in simple cases; loop tests assert status and leave cleanup dependent on the last tracked filename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_rename_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_reopen2_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_reopen2_latency.cc

## Purpose
This test benchmarks changing open mode on an already opened FSAL file via `reopen2`. It exercises both direct object operations and the `fsal_reopen2` wrapper.

## Important APIs, Types, And Functions
`Reopen2EmptyLatencyTest` allocates a share state with `alloc_state`, opens `test_file` using `obj_ops->open2` with `FSAL_O_RDWR`, closes with `close2`, and releases the state with `free_state`. Tests call `obj_ops->reopen2`, `fsal_reopen2`, and bypass `sub_hdl->obj_ops->reopen2`.

## Control Flow, State, And Persistence
Setup creates and opens a file under `reopen2_latency`. `SIMPLE` reopens it as read-only once. Loop tests run one million iterations, alternating `FSAL_O_READ` and `FSAL_O_WRITE` to force real mode transitions. Teardown closes the file with the same state, removes it, releases the object reference, and removes the test root.

## Dependencies And Integration Points
The file depends on FSAL state management, open2/reopen2/close2 object semantics, MDCACHE debug access, and shared Ganesha setup. It is sensitive to whether the sub-handle implementation accepts the same state object allocated from the outer export.

## Risks And Test Signals
Alternating modes is a useful signal for catching no-op reopen paths, but the tests do not verify access mode after each call. Bypass tests may mix MDCACHE and sub-FSAL state assumptions. Correctness is limited to `status.major == 0` plus teardown success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_reopen2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_setattr2_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_setattr2_latency.cc

## Purpose
This executable measures `setattr2` and `fsal_setattr` latency on cached and many-object access patterns. It updates attributes on one test file and on many looked-up files in a primed directory.

## Important APIs, Types, And Functions
`Setattr2EmptyLatencyTest` creates `setattr2_test_file` with `fsal_create` and removes it with `fsal_remove`. `Setattr2FullLatencyTest` primes 100,000 entries. Tests call `obj_ops->setattr2`, `fsal_setattr`, `obj_ops->lookup`, and `mdcdb_get_sub_handle`. Attributes come from the base fixture's `attrs`, initialized with mode, owner, and group.

## Control Flow, State, And Persistence
Simple tests set attributes once through normal and bypass handles. `FSAL_SETATTR` loops over the wrapper on the same file. `BIG_CACHED` repeatedly mutates the same file in a large directory. `BIG_UNCACHED` first looks up all primed file handles and cycles through them for one million attribute updates. Bypass uncached tests map each looked-up object to a sub-handle before timing.

## Dependencies And Integration Points
The test integrates with FSAL attribute lists, lookup/reference ownership, MDCACHE bypass, and the base helper's `create_and_prime_many` naming scheme. It exercises both wrapper and direct object operation layers.

## Risks And Test Signals
The uncached variants keep 100,000 object references and sub-handle pointers, which can stress memory and reference accounting. The test repeatedly applies the same attributes, so backends may optimize away changes after the first call. There is no postcondition verifying attribute values; status assertions and cleanup are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_setattr2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_symlink_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_symlink_latency.cc

## Purpose
This test benchmarks creating symbolic links through direct object operations and the `fsal_create` wrapper. It also verifies simple created-link lookup and target content.

## Important APIs, Types, And Functions
The fixture creates an initial `test_symlink` pointing at `TEST_ROOT` so expected content is available in `bfr_content`. Tests use `obj_ops->symlink`, `fsal_create(..., SYMBOLIC_LINK, ...)`, `obj_ops->lookup`, `obj_ops->readlink`, `fsal_remove`, `nfs_export_get_root_entry`, and `mdcdb_get_sub_handle`.

## Control Flow, State, And Persistence
Setup creates a baseline symlink under `root_entry`, reads its content, and stores the returned buffer. Simple tests create `symlink_to_symlink_latency`, verify lookup identity, read and compare target content, free the returned target, release handles, and remove the created link. Loop tests create one million uniquely named symlinks and then remove them in a second loop. Full tests do the same while a 100,000-file test root exists.

## Dependencies And Integration Points
The file exercises root-level symlink creation rather than creation inside `test_root`, and depends on Ganesha memory ownership for readlink buffers. Bypass tests use sub-root handles and refresh the root entry via `nfs_export_get_root_entry`.

## Risks And Test Signals
Creating and removing one million symlinks is expensive and may leave large cleanup work after failure. The bypass simple path compares a lookup from `root_entry` with a symlink created through a sub-handle, which may not have identical object identity across stack layers. Correctness signals include lookup identity, target byte comparison, status checks, and cleanup success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_symlink_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_unlink_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_unlink_latency.cc

## Purpose
This executable measures file removal/unlink latency using direct object operations, `fsal_remove`, and MDCACHE bypass handles. It creates hard links to one file so the benchmark can remove many directory entries without creating separate file contents.

## Important APIs, Types, And Functions
Tests use `fsal_create`, `obj_ops->open2`, `obj_ops->close`, `obj_ops->link`, `obj_ops->unlink`, `obj_ops->lookup`, `fsal_remove`, and `mdcdb_get_sub_handle`. `gtws_subcall` temporarily switches `op_ctx->fsal_export` to the sub-export for bypass `open2`.

## Control Flow, State, And Persistence
Simple tests create one file, unlink it, then assert lookup returns `ERR_FSAL_NOENT`. `FSALREMOVE` and full tests create a base file and one million hard links named `fl-%08x`; timing encloses removal of those links only. Full bypass creates links and removes them through sub-root/sub-object handles. After the benchmark, the original base file is removed and its handle reference is released.

## Dependencies And Integration Points
The file depends on hard-link support, FSAL lookup/no-entry semantics, sub-export context switching, and the base fixture's large-directory priming for full tests. It directly exercises link/unlink interaction and wrapper removal semantics.

## Risks And Test Signals
The million-link setup can exceed backend link-count or directory scalability limits and may be expensive to clean up on early assertion failure. The bypass simple test uses lower-level `close` rather than `close2`, matching the direct sub-handle open path. Signals include no-entry lookup after simple unlink, status checks for every link and remove, and successful final cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_unlink_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_write2_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_write2_latency.cc

## Purpose
This latency test measures FSAL write2/write behavior for small, large, stable, unstable, and bypass write paths. It writes to one open file under `write2_latency`.

## Important APIs, Types, And Functions
`Write2EmptyLatencyTest` allocates FSAL share state, opens `test_file` with `open2`, closes it with `close2`, and removes it. Tests allocate `struct fsal_io_arg` with a single `iovec`, populate `async_process_data`, and call `fsal_write` on either the MDCACHE handle or `mdcdb_get_sub_handle(test_file)`.

## Control Flow, State, And Persistence
Single-call tests cover 64-byte unstable, 64-byte stable, 2 MiB unstable, and 2 MiB stable writes. Loop tests write 64-byte buffers one million times while advancing the offset by 64 bytes, producing a large sparse or contiguous file depending on backend behavior. Teardown removes the file after close and state free.

## Dependencies And Integration Points
The file integrates FSAL I/O argument conventions, asynchronous process data with pthread condition/mutex pointers, MDCACHE bypass access, and shared Ganesha environment setup. Stable write behavior depends on the FSAL honoring `fsal_stable`.

## Risks And Test Signals
The test does not read data back, so it measures write success rather than persistence correctness. Large and loop tests can generate significant storage I/O. As with read tests, it initializes async completion state but does not explicitly wait for callbacks, relying on synchronous invocation. Success status and teardown are the key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_write2_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/gtest.hh -->
# sources/user-network-fs/nfs-ganesha/src/gtest/gtest.hh

## Purpose
This header provides the shared C++ GoogleTest harness for Ganesha FSAL integration tests. It starts and stops a real Ganesha server thread, creates a per-test export root directory, initializes operation context, provides bulk file creation/removal helpers, and optionally controls LTTng trace events.

## Important APIs, Types, And Functions
`gtest::Environment` wraps `nfs_libmain` in `std::thread`, calls `admin_halt` on destruction, and stores LTTng session, test root name, and export id. `GaneshaBaseTest` provides `enableEvents` and `disableEvents` for all or comma-selected tracepoints. `GaneshaFSALBaseTest` creates `root_entry`, `test_root`, `req_op_context`, and default `fsal_attrlist attrs`; it also defines `create_and_prime_many`, `remove_many`, and `readdir_callback`. The macro `gtws_subcall` temporarily switches `op_ctx->fsal_export` to a stackable sub-export.

## Control Flow, State, And Persistence
Environment construction starts Ganesha and sleeps five seconds for initialization. Fixture setup obtains the configured export, root entry, initializes a simple op context, prepares default owner/group/mode attributes, and creates the named test root directory. Teardown unlinks the test root, releases object references, clears export pointers, and releases op context. Bulk creation uses `fsal_create` and primes cache with `fsal_readdir`; removal releases optional object references before `fsal_remove`.

## Dependencies And Integration Points
The header bridges C++ tests with C Ganesha headers, liburcu, LTTng control APIs, gperftools, NFS export management, and FSAL operations. It is included by most FSAL latency tests and by `gtest_nfs4.hh`.

## Risks And Test Signals
`gtest::Environment* env` is defined in the header, which can be fragile if included in multiple translation units for one executable. The startup sleep is a fixed timing assumption. `create_and_prime_many` does not assert the final priming `fsal_readdir` status. The helper centralizes cleanup, so failures here affect all dependent tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/gtest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/gtest_nfs4.hh -->
# sources/user-network-fs/nfs-ganesha/src/gtest/gtest_nfs4.hh

## Purpose
This header extends the FSAL test harness with NFSv4 COMPOUND operation state and argument-building helpers. It allows unit tests to invoke individual NFSv4 operation handlers directly while still using real FSAL object handles and export context.

## Important APIs, Types, And Functions
`gtest::GaeshaNFS4BaseTest` derives from `GaneshaFSALBaseTest` and allocates `compound_data_t`, `nfs_arg_t`, one `nfs_argop4`, and one `nfs_resop4`. Helpers include `setCurrentFH`, `setSavedFH`, `set_saved_export`, `setup_lookup`, `cleanup_lookup`, `setup_putfh`, `cleanup_putfh`, `setup_rename`, `swap_rename`, `cleanup_rename`, `setup_link`, and `cleanup_link`.

## Control Flow, State, And Persistence
Setup initializes compound data, zeroes arguments/responses, creates a one-operation arg array, sets minor version zero, and defaults the single op to `NFS4_OP_PUTROOTFH` so teardown can safely free XDR structures. Teardown clears current entry, frees one compound response, frees compound data, XDR-frees `COMPOUND4args`, and then runs FSAL fixture cleanup. File-handle helpers convert FSAL handles to NFSv4 file handles with `nfs4_FSALToFhandle` and update compound current/saved entries.

## Dependencies And Integration Points
The header depends on `gtest.hh`, `nfs_file_handle.h`, `nfs_proto_functions.h`, XDR free routines, Ganesha compound state, and export reference management. It is the common support layer for NFSv4 lookup, PUTFH, RENAME, and LINK latency tests.

## Risks And Test Signals
The class name is misspelled as `GaeshaNFS4BaseTest`, so dependent tests must use that exact spelling. The single-op allocation assumes each test directly calls one handler rather than full compound dispatch. Helpers free and replace union members manually, making cleanup correctness important when tests repeatedly rebuild operation arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/gtest_nfs4.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/CMakeLists.txt

## Purpose
This CMake file builds four NFSv4 latency test executables: lookup, putfh, rename, and link. Each executable is compiled from its matching `.cc` file and linked against the Ganesha server and test/runtime libraries.

## Important APIs, Types, And Functions
Targets are `test_nfs4_lookup_latency`, `test_nfs4_putfh_latency`, `test_nfs4_rename_latency`, and `test_nfs4_link_latency`. Each target uses `add_executable`, `add_sanitizers`, `target_link_libraries`, and `set_target_properties(... COMPILE_FLAGS "${UNITTEST_CXX_FLAGS}")`.

## Control Flow, State, And Persistence
The file is declarative build configuration. For each test it sets a `_SRCS` variable with one source file, defines the executable, adds sanitizer instrumentation, links required libraries, and applies unit-test C++ flags. It creates no runtime state itself.

## Dependencies And Integration Points
All targets link `ganesha_nfsd`, `${LIBTIRPC_LIBRARIES}`, `${UNITTEST_LIBS}`, `${LTTNG_LIBRARIES}`, `${LTTNG_CTL_LIBRARIES}`, and `${GPERFTOOLS_LIBRARIES}`. This aligns the NFSv4 latency tests with direct Ganesha server symbols, RPC/XDR support, GoogleTest, LTTng event control, and optional profiling.

## Risks And Test Signals
The file repeats nearly identical target definitions, which is simple but easy to drift if a new common dependency is added. Since each executable links `ganesha_nfsd`, build failures here often signal missing server symbols or library configuration rather than test logic issues. Sanitizer attachment is a useful build-time signal for memory and undefined-behavior checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_link_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_link_latency.cc

## Purpose
This NFSv4 latency test measures the `LINK` operation handler by creating hard links to existing objects in a populated test directory. It invokes `nfs4_op_link` directly with prepared compound current and saved file handles.

## Important APIs, Types, And Functions
`LinkFullLatencyTest` derives from `GaeshaNFS4BaseTest`, creates 100,000 files into `objs`, and calls `set_saved_export`. Tests use `setup_link`, `setCurrentFH(test_root)`, `setSavedFH(objs[n])`, `nfs4_op_link`, `cleanup_link`, `fsal_remove`, `enableEvents`, `disableEvents`, and optional `ProfilerStart/ProfilerStop`.

## Control Flow, State, And Persistence
`BIG_SINGLE` creates one new hard link for `objs[DIR_COUNT / 5]`, measures a single call, and removes the link. `BIG` loops one million times, cycling source objects and generating link names `d-%08x-%08x`; cleanup removes every created link after timing. Fixture teardown removes the original primed files.

## Dependencies And Integration Points
The test depends on NFSv4 compound state from `gtest_nfs4.hh`, FSAL hard-link support, LTTng event controls, gperftools, and Ganesha FSAL cleanup. The saved file handle identifies the existing source object; current file handle identifies the destination directory.

## Risks And Test Signals
The test creates one million hard links, which can exceed filesystem limits or make cleanup expensive. It does not call `nfs4_Compound_FreeOne` inside the loop, so handler response ownership must remain safe for repeated direct calls or be handled by the fixture teardown. The primary signals are `NFS4_OK` per operation, timing output, profiling traces, and successful removal of created links.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_link_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_lookup_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_lookup_latency.cc

## Purpose
This test benchmarks the NFSv4 `LOOKUP` operation handler for both the per-test root and entries in a large populated directory. It validates that the handler updates compound current object state to the expected FSAL handle.

## Important APIs, Types, And Functions
Fixtures derive from `GaeshaNFS4BaseTest`; `LookupFullLatencyTest` creates 100,000 files and stores handles in `objs`. Tests use `setup_lookup`, `cleanup_lookup`, `setCurrentFH`, `nfs4_op_lookup`, `enableEvents`, optional profiler calls, and comparisons against `data->current_obj`.

## Control Flow, State, And Persistence
`SIMPLE` and `LOOP` set the current file handle to `root_entry` and look up `TEST_ROOT`. Full tests set current file handle to `test_root` and look up generated names `f-%08x`. The big loop rebuilds the lookup name each iteration, cycles through all stored handles, validates `NFS4_OK`, checks current object identity, and cleans the lookup argument.

## Dependencies And Integration Points
The test integrates direct NFSv4 handler invocation with FSAL handles created by the base fixture. It uses the generated naming convention from `create_and_prime_many` and optional LTTng/gperftools instrumentation.

## Risks And Test Signals
Object identity checks depend on cached handles matching those stored during setup. Repeated direct operation calls can accumulate response state if handler allocation is not idempotent until fixture teardown. The strongest signals are `NFS4_OK`, exact `data->current_obj` comparison, and successful full cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_lookup_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_putfh_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_putfh_latency.cc

## Purpose
This NFSv4 test measures the `PUTFH` operation handler, which sets the compound current file handle and current object. It covers one root object, one populated-file object, and a one-million-iteration loop over many file handles.

## Important APIs, Types, And Functions
`PutfhEmptyLatencyTest` uses the base compound fixture without extra entries. `PutfhFullLatencyTest` stores 100,000 created file handles. Tests call `setup_putfh`, `cleanup_putfh`, `nfs4_op_putfh`, and compare `data->current_obj` with the expected FSAL object.

## Control Flow, State, And Persistence
`SIMPLE` prepares a PUTFH argument for `test_root`, executes one handler call, and checks success/current object. `LOOP` reuses the same PUTFH argument for one million calls. Full tests generate a new serialized file handle for each selected object and clean it after each big-loop iteration. Fixture teardown frees compound/XDR allocations and removes all test files.

## Dependencies And Integration Points
The file depends on `nfs4_FSALToFhandle` through the setup helper, NFSv4 handler state in `compound_data_t`, the shared FSAL test root, LTTng event controls, and gperftools profiling.

## Risks And Test Signals
The big loop repeatedly allocates and frees NFSv4 file-handle buffers, so it measures both handler cost and argument setup overhead inside the timed region. The empty loop reuses one handle, giving a different signal. Assertions on `data->current_obj` are important for catching stale or failed handle resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_putfh_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_rename_latency.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_rename_latency.cc

## Purpose
This test benchmarks the NFSv4 `RENAME` operation handler for the per-test root and for entries in a large directory. It uses prepared current and saved file handles as source and destination directories.

## Important APIs, Types, And Functions
`RenameFullLatencyTest` derives from `GaeshaNFS4BaseTest`, creates 100,000 file handles, and calls `set_saved_export`. Tests use `setup_rename`, `swap_rename`, `cleanup_rename`, `setCurrentFH`, `setSavedFH`, `nfs4_op_rename`, LTTng event controls, and optional profiler calls.

## Control Flow, State, And Persistence
Empty tests rename the test root between `nfs4_rename_latency` and `nfs4_rename_latency2`, swapping names so the final state is restored. Full single test renames one file to an `r-%08x` name, measures one operation, then swaps it back. The big loop cycles through all files and alternates direction per full pass over the file set so names remain recoverable for teardown.

## Dependencies And Integration Points
The test exercises NFSv4 rename semantics directly, while relying on FSAL object setup, export references, and generated file naming from `create_and_prime_many`. It integrates with LTTng/gperftools instrumentation in the same way as the other NFSv4 latency tests.

## Risks And Test Signals
Renaming the fixture's own test root in empty tests is sensitive because base teardown expects the original root name; the even loop count and explicit swap-back are essential. Failure mid-loop may leave files under `r-*` names, causing `remove_many` to miss them. Signals are `NFS4_OK`, timing, and successful restoration/cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/nfs4/test_nfs4_rename_latency.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/test_ci_hash_dist1.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/test_ci_hash_dist1.cc

## Purpose
This appears to be an early or incomplete integration test for creating a Ganesha export-backed directory named `ci_hash_dist1`. Despite the name, active code does not perform hash distribution validation; related random/checksum code is disabled under `#if 0`.

## Important APIs, Types, And Functions
The file defines global Ganesha config variables, `req_op_context`, `fsal_attrlist object_attributes`, export/root/test handles, and a `ganesha_server` wrapper around `nfs_libmain`. Tests `CI_HASH_DIST1.INIT` and `CI_HASH_DIST1.CREATE_ROOT` call `get_gsh_export`, `nfs_export_get_root_entry`, `init_op_context_simple`, and `root_entry->obj_ops->mkdir`.

## Control Flow, State, And Persistence
`main` parses config/log/debug/export options, initializes GoogleTest, starts a Ganesha server thread, sleeps five seconds, runs all tests, and then joins the server thread. The tests initialize export state and create a directory. There is no visible cleanup, `admin_halt`, object release, or op-context release in this file.

## Dependencies And Integration Points
The test links C++ GoogleTest with Ganesha C headers, liburcu, Boost program options, export manager, NFS exports, SAL data, and FSAL APIs. It pre-dates or bypasses the later shared `gtest.hh` environment.

## Risks And Test Signals
The server thread is joined without a shutdown call, so the executable may hang unless `nfs_libmain` exits independently. `attrs_out` is a null pointer passed to `mkdir`, which may be acceptable by contract or a bug depending on implementation. There is no cleanup for the created directory. Signals are limited to non-null export/root/test handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/test_ci_hash_dist1.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/test_example.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/test_example.cc

## Purpose
This is a minimal GoogleTest example or smoke-test skeleton. It verifies that the unit-test framework can build and run a trivial assertion without involving Ganesha runtime state.

## Important APIs, Types, And Functions
The file includes standard C++ headers and `gtest/gtest.h`, declares an unused namespace-local boolean `global_decls`, defines `TEST(EXAMPLE, INIT)` with `ASSERT_EQ(0, 0)`, and uses a conventional `main` that calls `InitGoogleTest` and `RUN_ALL_TESTS`.

## Control Flow, State, And Persistence
There is no external state, no filesystem access, no Ganesha server initialization, and no persistence. Execution consists only of GoogleTest initialization and one always-true assertion.

## Dependencies And Integration Points
The only functional dependency is GoogleTest. The empty `extern "C"` block labeled for Ganesha headers indicates the file is a template for tests that may later include C headers.

## Risks And Test Signals
The test provides a build/link smoke signal for the gtest environment but no product behavior coverage. The unused `global_decls` variable may trigger warnings depending on compiler flags, though local settings likely tolerate it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/test_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/test_rbt.cc -->
# sources/user-network-fs/nfs-ganesha/src/gtest/test_rbt.cc

## Purpose
This benchmark-style GoogleTest measures red-black-tree lookup, removal, and insertion throughput for a sliding window of RPC-like transaction IDs. It is not tied to FSAL exports; it targets Ganesha's `opr_rbtree` infrastructure.

## Important APIs, Types, And Functions
`struct rbt_item` embeds `opr_rbtree_node`, stores a `uint32_t xid`, and includes a 64 KiB pad to reduce cache friendliness. `rbt_item_xid_cmpf` compares embedded xids. `RBTLatency1` allocates `item_wsize` entries, initializes `call_replies` with `opr_rbtree_init`, and inserts the initial window. The test uses `opr_rbtree_lookup`, `opr_rbtree_remove`, and `opr_rbtree_insert`.

## Control Flow, State, And Persistence
Setup fills a tree with 100,000 sequential xids. `RUN1` performs one million iterations: look up the oldest xid, remove it, update that item to the next xid, reinsert it, and advance both counters. Timing covers only this sliding-window loop. Teardown deletes the allocated array.

## Dependencies And Integration Points
The file includes Ganesha core headers, `misc/rbtree_x.h`, queue/intrinsic helpers, LTTng, and gperftools. Optional profiling is controlled by the namespace-local `profile_out` pointer, currently null.

## Risks And Test Signals
The lookup result is not checked for null before `opr_containerof`, so tree corruption or lookup failure will crash. The reported `fprintf` format appears to provide fewer arguments than format specifiers for the final `reqs/s` message, which is a correctness risk in diagnostics. The main signal is timing and process survival under heavy tree mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/test_rbt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/hashtable/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/hashtable/CMakeLists.txt

## Purpose
This CMake file defines the `hashtable` object library for Ganesha's partitioned hash table implementation.

## Important APIs, Types, And Functions
It sets `hashtable_STAT_SRCS` to `hashtable.c`, creates `add_library(hashtable OBJECT ...)`, applies `add_sanitizers(hashtable)`, and sets `COMPILE_FLAGS` to `-fPIC`.

## Control Flow, State, And Persistence
The file has no runtime behavior. Its build-time flow creates an object library suitable for inclusion in other shared/static targets.

## Dependencies And Integration Points
When `USE_LTTNG` is enabled, the target depends on `gsh_trace_header_generate` and includes generated LTTng file properties from the build directory. This ensures trace headers/properties are generated before compiling the hashtable object.

## Risks And Test Signals
The object-library form means downstream targets control final linkage. Build failures here usually indicate sanitizer integration, trace-generation ordering, or missing headers. The explicit `-fPIC` flag is important for shared-library consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/hashtable/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/hashtable/hashtable.c -->
# sources/user-network-fs/nfs-ganesha/src/hashtable/hashtable.c

## Purpose
This file implements Ganesha's generic concurrent hash table. The structure partitions keys across an array of red-black trees, locks each partition separately, stores opaque key/value buffer descriptors, and optionally accelerates repeated lookup with a small direct-mapped cache per partition.

## Important APIs, Types, And Functions
Public functions include `hashtable_init`, `hashtable_destroy`, `hashtable_acquire_latch`, `hashtable_getlatch`, `hashtable_releaselatched`, `hashtable_setlatched`, `hashtable_deletelatched`, `hashtable_delall`, `hashtable_log`, `hashtable_test_and_set`, `hashtable_getref`, `hashtable_for_each`, and `hash_table_err_to_str`. Internal helpers include `cache_page_size`, `cache_offsetof`, `compute`, and `key_locate`. Key types are `struct hash_table`, `struct hash_partition`, `struct hash_latch`, `struct hash_data`, `struct gsh_buffdesc`, and `rbt_node_t`.

## Control Flow, State, And Persistence
`compute` maps each key to a partition index and an RB-tree hash using either a combined hash callback or separate index/tree callbacks. `key_locate` checks the optional cache slot, validates actual key equality, then searches the partition RB tree for the leftmost matching hash and scans collisions until the exact key is found. `hashtable_getlatch` computes location, acquires a read or write lock, performs lookup, optionally returns the value, and either records latch state or unlocks on failure. `hashtable_setlatched` consumes a write latch, overwrites an existing descriptor or allocates pooled node/data objects and inserts into the partition tree. `hashtable_deletelatched` removes the latched node, clears cache, returns stored descriptors if requested, frees pooled storage, decrements count, and leaves the lock held for caller workflows that reuse the latch. `hashtable_delall` drains all trees partition by partition and invokes a caller-supplied free callback for stored contents.

## Dependencies And Integration Points
The implementation depends on `hashtable.h` contracts, Ganesha logging, atomic pointer operations, pthread rwlocks, memory/pool helpers, and RB-tree macros. Callers own the memory behind key/value buffer descriptors; the table stores descriptor pointers/lengths, not deep copies. Optional display callbacks integrate with debug logging.

## Risks And Test Signals
The latch API is powerful but easy to misuse: callers must match write/read intent, understand which calls release locks, and avoid using stale `latch->locator` after delete. `hashtable_delall` assumes `free_func` is non-null and successful; a failure exits with some entries already removed. Cache invalidation is coarse and disabled comparison by default, so cache correctness relies on clearing by hash slot during delete and exact-key validation during lookup. The `assert(*index < index_size)` protects hash functions only in assert-enabled builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/hashtable/hashtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/CMakeLists.txt

## Purpose
This CMake file builds the `idmap` object library, which contains Ganesha's NFSv4 owner/group ID mapping implementation and its caches, monitoring, and directory-service wrappers.

## Important APIs, Types, And Functions
It conditionally adds include directories for `${WBCLIENT_INCLUDE_DIR}` under `_MSPAC_SUPPORT` and `${DBUS_INCLUDE_DIRS}` under `USE_DBUS`. `idmap_STAT_SRCS` includes `idmapper.c`, `idmapper_cache.c`, `idmapper_negative_cache.c`, `idmapper_monitoring.c`, `pwnam_wrappers.c`, and `sss_nss_idmap.c`. The target is created with `add_library(idmap OBJECT ...)`, instrumented with `add_sanitizers`, and compiled with `-fPIC`.

## Control Flow, State, And Persistence
This is build configuration only. It selects include paths based on feature flags, defines the object library source set, and wires LTTng generated trace dependencies when tracing is enabled.

## Dependencies And Integration Points
The object library feeds Ganesha components that need UID/GID, owner string, cache, and monitoring logic. Feature flags integrate optional Winbind/MSPAC, DBus statistics, and generated LTTng trace support.

## Risks And Test Signals
Conditional includes must align with source-level `#ifdef` branches in `idmapper.c`; missing feature-specific headers will surface as build failures. Because the target is an object library, final link dependencies for DBus, Winbind, and libnfsidmap must be supplied by consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper.c

## Purpose
This file implements Ganesha's NFSv4 ID mapping lifecycle and conversion logic. It maps UID/GID values to NFSv4 owner/group strings, maps owner/group strings and GSS principals back to numeric IDs, manages positive and negative idmapper caches, records external lookup metrics, and exposes optional DBus auth statistics.

## Important APIs, Types, And Functions
Lifecycle functions include `idmapper_init`, `set_idmapping_status`, `idmapper_cleanup`, `idmapper_reaper_init`, and `cache_reaper_run`. Encoding functions are `xdr_encode_nfs4_owner`, `xdr_encode_nfs4_group`, and internal `xdr_encode_nfs4_princ`. Decoding functions include `name2uid`, `name2gid`, internal `name2id`, `pwentname2id`, `idmapname2id`, `atless2id`, `name_to_uid`, `name_to_gid`, and `string_to_numeric_uid_gid`. Principal support includes `is_root_principal` and `principal2uid` under GSSAPI. Stats functions include `winbind_stats_update`, `gc_stats_update`, `dns_stats_update`, `reset_auth_stats`, and optional DBus `all_auth_stats`.

## Control Flow, State, And Persistence
Initialization creates rwlocks, initializes positive and negative caches, optionally starts a `fridgethr` looper to reap expired idmapper and uid2grp cache entries, registers cleanup, and initializes monitoring. `set_idmapping_status` serializes enable/disable changes, selects the pwnam wrapper implementation, sets or clears the owner domain, and clears idmapper/uid2grp state when disabling. Encoding first returns numeric strings when idmapping is off or numeric-only mode is set; otherwise it checks caches, copies `owner_domain` under lock, resolves through pwutils or libnfsidmap, falls back to numeric or `nobody`, caches the result, and XDR-encodes it. Decoding checks positive cache, then negative cache, then parses mutable owner strings, validates domains, resolves through pwutils/libnfsidmap/numeric fallback, caches success, and caches anonymous fallbacks negatively. Principal mapping handles configured root principals, pwutils name resolution, libnfsidmap `nfs4_gss_princ_to_ids`, and optional MSPAC/Winbind SID resolution.

## Dependencies And Integration Points
The file depends on global `nfs_param` configuration, libnfsidmap when `USE_NFSIDMAP` is enabled, NSS-style pw/gr wrappers, uid2grp cache, idmapper positive/negative cache modules, `fridgethr`, Ganesha logging, LTTng tracepoints, monitoring, DBus, and optional Winbind/MSPAC support. It uses `owner_domain.lock` to guard the configured owner domain and separate locks for user, group, negative-cache, and auth-stat state.

## Risks And Test Signals
The code has many configuration-dependent branches, so behavior can differ sharply between `use_getpwnam`, libnfsidmap, numeric-owner, fully-qualified-name, GSSAPI, MSPAC, and DBus builds. Owner-domain handling intentionally copies under lock to avoid holding it during external calls, but zero-length domains cause mapping failure in several paths. Buffer sizing grows for ERANGE in NSS calls, but external directory services can still be slow; monitoring captures latency. Negative cache entries deliberately map failures to anonymous IDs, which can hide transient directory-service outages until cache expiry. Tests should cover numeric parsing rules, domain validation, cache hit/miss behavior, disabled idmapping, root principal mapping, and external lookup failure fallbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper.c -->
