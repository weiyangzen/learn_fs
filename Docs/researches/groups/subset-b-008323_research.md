# subset-b-008323 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Size.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Size.cpp

Purpose: Tests the size accounting contract of `blockstore::caching::QueueMap` through the shared `QueueMapTest` fixture. It verifies an empty map, pushes of one and two values, global oldest pops, keyed pops, and push-after-pop paths including reusing the same key.

Important APIs and types: Uses `QueueMapTest::push`, `pop`, `pop(key)`, and `size`, backed by `QueueMap<MinimalKeyType, MinimalValueType>`. The fixture also validates object lifetime counts after teardown.

Control flow: Each GoogleTest case constructs a fresh fixture, performs a short sequence of queue/map operations, and asserts exact `size()` after each state transition.

State and persistence behavior: State is in-memory only: the queue order, key index, and per-key removals. No filesystem persistence is involved.

Dependencies and integration points: Integrates with `QueueMapTest.h`, minimal non-default-constructible key/value types, `unique_ref`, `boost::optional`, and GoogleTest.

Risks: Off-by-one size drift after removing by key or after reinserting an existing key would break eviction policy in cache users. The tests do not cover multithreading.

Test signals: Exact sizes after every push/pop sequence and fixture teardown with zero leaked keys/values.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Size.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Values.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Values.cpp

Purpose: Verifies value-returning behavior and FIFO/keyed removal semantics of `QueueMap`. It covers empty pops, missing keyed pops, pushing one or two values, popping first or last keys, middle/first/last keyed removal from larger queues, many-value FIFO ordering, and replacing an already existing key.

Important APIs and types: Uses `QueueMapTest::push`, `pop`, `pop(key)`, and `peek`, with results represented as `boost::optional<int>`. Includes the Boost optional/gtest workaround so optional values can be asserted cleanly.

Control flow: Tests build deterministic operation traces and compare returned optional values against expected value order. Keyed pops remove a specific key while global `pop` preserves oldest remaining order.

State and persistence behavior: Only in-memory queue/index state is exercised. The fixture's minimal move-only value type catches invalid use-after-move and lifetime leaks.

Dependencies and integration points: Exercises `QueueMap` as used by the caching blockstore layer, where eviction order and key replacement must stay consistent.

Risks: Duplicate-key push behavior is a subtle integration point; stale queue entries can cause wrong value eviction or size mismatches. No concurrent access is tested.

Test signals: Optional none/value checks, FIFO ordering after keyed removal, peek stability, many-value sequence correctness, and zero leaked key/value instances at fixture teardown.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Values.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.cpp

Purpose: Implements the tiny `CacheTest` fixture adapter for cache tests using minimal key/value types. It wraps the production cache API in integer-oriented helpers to keep tests focused on behavior rather than construction details.

Important APIs and types: Defines `CacheTest::push(int,int)` and `CacheTest::pop(int)`. The wrapped cache type is `blockstore::caching::Cache<MinimalKeyType, MinimalValueType, MAX_ENTRIES>`.

Control flow: `push` converts integers into `MinimalKeyType` and `MinimalValueType` factory-created objects, then calls `_cache.push`. `pop` builds a key, calls `_cache.pop`, returns `boost::none` on misses, and converts hits back to the stored integer value.

State and persistence behavior: State is entirely in the fixture's in-memory cache. No persistent store, files, or static fixture state are updated here.

Dependencies and integration points: Includes `CacheTest.h`, which brings in GoogleTest, the cache implementation, and minimal type definitions.

Risks: Because this adapter strips values to integers, it is good for cache semantics but not for testing richer value object behavior. Ownership/lifetime checking depends on the minimal types used by the header.

Test signals: Downstream cache tests use this file's helpers to assert optional hit/miss values without exposing production template complexity.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.h

Purpose: Declares a reusable GoogleTest fixture for `blockstore::caching::Cache` tests. It standardizes cache construction with minimal key/value types and a fixed capacity so individual tests can work with plain integers.

Important APIs and types: The fixture exposes `push(int,int)`, `pop(int)`, `MAX_ENTRIES = 100`, and a `Cache` alias for `Cache<MinimalKeyType, MinimalValueType, MAX_ENTRIES>`. The private member `_cache` is constructed with name `"test"`.

Control flow: Test cases instantiate the fixture, call helper methods, and inspect optional integer results. The header itself has no runtime logic besides inline construction.

State and persistence behavior: Holds one in-memory cache per test fixture. Static lifetime tracking is delegated to `MinimalKeyType` and `MinimalValueType`.

Dependencies and integration points: Pulls in GoogleTest, production `Cache.h`, minimal type headers, and Boost optional. It is the integration boundary between production templates and readable cache behavior tests.

Risks: The comment still mentions `QueueMap`, so maintainers could confuse the fixture role. The fixed capacity hides capacity-edge behavior unless tests deliberately push over `MAX_ENTRIES`.

Test signals: Any fixture user can validate cache hits, misses, eviction, and type-lifetime behavior without constructing production template arguments manually.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CacheTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.cpp

Purpose: Defines static storage for `CopyableMovableValueType::instances`. The corresponding header implements the behavior; this file provides the single translation-unit definition required by the tests.

Important APIs and types: The only API surface is `std::atomic<int> CopyableMovableValueType::instances(0)`, used to track live object counts.

Control flow: There is no runtime control flow beyond static initialization before tests begin.

State and persistence behavior: Maintains process-local atomic live-instance count. No filesystem persistence or external state exists.

Dependencies and integration points: Includes `CopyableMovableValueType.h`; cache and queue tests can link against the static counter when checking value object lifetime.

Risks: Multiple definitions would break linking; missing definition would break tests using the static counter. The counter must be reset by tests when they depend on exact counts.

Test signals: Successful link and accurate instance-count assertions in tests that use the copyable/movable value helper.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.h -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.h

Purpose: Defines a test value type that is both copyable and movable while tracking live instances. It is used to verify cache templates with less restrictive value requirements than `MinimalValueType`.

Important APIs and types: `CopyableMovableValueType` exposes `instances`, `create(int)`, copy constructor, move constructor, destructor, and `value()`. Construction is private through `create`, which preserves the non-default-constructible property.

Control flow: Copy construction duplicates the integer value and increments the counter. Move construction copies the value, marks the source moved, and also increments the counter for the new object. Destruction decrements the counter.

State and persistence behavior: State is per-object integer value and moved flag plus a process-local atomic live-instance counter.

Dependencies and integration points: Used by cache or queue tests that need a value type satisfying copy and move requirements. It avoids external libraries beyond standard atomics.

Risks: `value()` does not assert moved-from invalidity as strongly as `MinimalValueType`, so it is a weaker misuse detector. The moved-from object's `_isMoved` state is only meaningful while it remains alive.

Test signals: Instance counter returns to zero and copied/moved values preserve the expected integer payload.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/CopyableMovableValueType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.cpp

Purpose: Provides the static live-instance counter definition for `MinimalKeyType`, the restricted key type used by cache and queue map tests.

Important APIs and types: Defines `std::atomic<int> MinimalKeyType::instances(0)`.

Control flow: Only static initialization occurs. Test fixtures reset and inspect this counter around container lifetimes.

State and persistence behavior: Process-local atomic state tracks active key objects. No persisted state exists.

Dependencies and integration points: Includes `MinimalKeyType.h`; links with tests that instantiate `QueueMap<MinimalKeyType,...>` or `Cache<MinimalKeyType,...>`.

Risks: The counter is global to the process, so tests must reset it before exact leak assertions and avoid overlapping lifetimes. Missing or duplicate definitions would break linking.

Test signals: Fixture destructors expect the counter to reach zero after cache/queue destruction, catching leaked key objects or stale internal map entries.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.h -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.h

Purpose: Defines a deliberately minimal key type for testing cache templates. It is non-default-constructible, copyable, hashable, equality-comparable, and live-counted, forcing production containers to rely only on required key operations.

Important APIs and types: `MinimalKeyType::create(int)`, copy constructor, destructor, `value()`, static `instances`, `std::hash<MinimalKeyType>`, and `operator==`.

Control flow: Keys are constructed only through the private integer constructor via `create`. Copy construction delegates to value construction, incrementing the instance count; destruction decrements it.

State and persistence behavior: Each key owns one integer. Global atomic instance count is process-local test state and is used for leak detection.

Dependencies and integration points: Integrates with `std::unordered_map` through a hash specialization and equality operator. This matches `QueueMap`/`Cache` lookup needs without default construction.

Risks: The hash is simply the integer value, adequate for deterministic tests but not collision-heavy scenarios. Static count assertions require clean fixture isolation.

Test signals: Successful compilation with non-default-constructible keys, correct keyed lookup/removal, and zero remaining instances after tested containers are destroyed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalKeyType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.cpp

Purpose: Supplies the static live-instance counter definition for `MinimalValueType`, the move-only value used by queue/cache tests.

Important APIs and types: Defines `std::atomic<int> MinimalValueType::instances(0)`.

Control flow: No functions are implemented here; only static initialization is performed before test execution.

State and persistence behavior: The process-local atomic count tracks active minimal values and is checked by fixtures after container destruction.

Dependencies and integration points: Includes `MinimalValueType.h`; required at link time for all tests using the move-only value helper.

Risks: Because the counter is static, unrelated tests sharing the type can contaminate exact counts if they overlap or fail before cleanup.

Test signals: Link success and fixture leak checks reaching zero are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.h -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.h

Purpose: Defines a restrictive move-only value type for cache and queue map tests. It is non-default-constructible and non-copyable, so production templates must support move-only payloads and avoid invalid moved-from access.

Important APIs and types: `MinimalValueType::create(int)`, move constructor, move assignment, destructor, `value()`, static `instances`, and `DISALLOW_COPY_AND_ASSIGN`.

Control flow: Construction increments the count; moving copies the integer payload into a new valid object and marks the source moved; `value()` asserts the object is neither moved nor destructed; destruction asserts it has not already been destroyed and decrements the count.

State and persistence behavior: Per-object state is integer payload plus moved/destructed flags. Global atomic count is process-local test state.

Dependencies and integration points: Uses CryFS assertion/macros and is consumed by `QueueMapTest` and `CacheTest` fixtures.

Risks: The type is intentionally unforgiving; accidental access to moved-from values aborts or throws depending on assertion mode. Tests must account for move semantics rather than copy semantics.

Test signals: Move-only compilation, correct integer values returned from containers, assertion-free movement, and zero live instances at teardown.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/MinimalValueType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.cpp

Purpose: Implements the reusable `QueueMapTest` fixture for behavior tests against `blockstore::caching::QueueMap` using minimal key and move-only value types.

Important APIs and types: Implements constructor, destructor, `push`, global `pop`, keyed `pop`, `peek`, and `size`. The fixture owns `unique_ref<QueueMap<MinimalKeyType, MinimalValueType>>`.

Control flow: Construction creates a fresh `QueueMap` and resets live-instance counters. Destruction explicitly destroys the map and then asserts no key/value instances remain. Helpers translate integer inputs into minimal objects and optional production values back into optional integers.

State and persistence behavior: All state is in-memory. Explicit destruction before leak assertions ensures internal queue/map nodes are released before counters are read.

Dependencies and integration points: Uses `cpputils::make_unique_ref`, `cpputils::destruct`, Boost optional, and the production queue map template.

Risks: The fixture hides full key/value objects, so tests focus on semantics and lifetime but not object identity. Counter resets assume one fixture at a time.

Test signals: Wrapper users get deterministic integer behavior plus automatic leak detection on every test case.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.h

Purpose: Declares the shared fixture for `QueueMap` tests. It documents and exposes the minimal test operations needed to validate queue ordering, keyed lookup/removal, peek behavior, size accounting, and leak-free ownership.

Important APIs and types: `QueueMapTest` inherits `::testing::Test` and provides `push(int,int)`, `pop()`, `pop(int)`, `peek()`, and `size()`. It owns a `unique_ref` to `QueueMap<MinimalKeyType, MinimalValueType>`.

Control flow: The header declares operations; implementation in the `.cpp` performs conversions and leak checks.

State and persistence behavior: Fixture state is one in-memory map per test case. Static key/value counters are reset and checked by the implementation.

Dependencies and integration points: Includes GoogleTest, `unique_ref`, production `QueueMap.h`, minimal type headers, and Boost optional.

Risks: The fixture's integer facade is intentionally narrow and will not reveal bugs involving richer key hashing or value copy behavior. It also assumes single-threaded fixture use.

Test signals: Consumers can assert optional return values, size, and peek while the fixture enforces that no internal container nodes leak.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/testutils/QueueMapTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreTest_Specific.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreTest_Specific.cpp

Purpose: Tests `ParallelAccessBlockStore::physicalBlockSizeFromVirtualBlockSize` boundary behavior. It verifies conversion from virtual to physical block sizes across zero, positive, and negative boundaries.

Important APIs and types: Uses `ParallelAccessBlockStore` and `FakeBlockStore`, though the tested API is the static physical-size conversion helper. GoogleTest assertions check exact expected integer results.

Control flow: Independent test cases call the conversion helper with representative virtual sizes and compare returned physical sizes. The fixture class is minimal.

State and persistence behavior: No block store is persisted or mutated; the tested behavior is pure arithmetic/configuration logic.

Dependencies and integration points: Integrates the parallel-access blockstore implementation with its fake lower store include path, ensuring the test target compiles against the production API.

Risks: Boundary conversion bugs can corrupt block layout decisions or produce invalid lower-layer accesses. The test is focused on explicit examples rather than exhaustive property coverage.

Test signals: Exact results for zero physical, zero virtual, negative boundary cases, and ordinary positive conversion.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreTest_Specific.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/testutils/gtest_printers.h -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/testutils/gtest_printers.h

Purpose: Provides GoogleTest pretty-printer overloads for blockstore test types so assertion failures are readable.

Important APIs and types: Declares `PrintTo` overloads for block IDs or related blockstore value types used in tests. These free functions let GoogleTest render custom types in `EXPECT_EQ` and matcher diagnostics.

Control flow: There is no standalone execution; GoogleTest discovers the overloads through argument-dependent lookup when formatting assertion values.

State and persistence behavior: Stateless header-only formatting helpers. They do not mutate blockstore state or write files.

Dependencies and integration points: The header is included by blockstore tests and integrates with GoogleTest's custom printer mechanism.

Risks: Printer definitions must remain in the correct namespace and avoid depending on heavyweight state. Incorrect formatting does not change product behavior but can make test failures hard to debug.

Test signals: Compilation of blockstore tests and readable failure output for custom block identifiers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/testutils/gtest_printers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/utils/BlockStoreUtilsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/utils/BlockStoreUtilsTest.cpp

Purpose: Tests utility functions that operate on block stores, especially zero-filling and block copying into new or existing destination blocks.

Important APIs and types: Uses `FakeBlockStore`, `DataFixture`, `BlockStoreUtils`, and GoogleTest. Fixtures include `BlockStoreUtilsTest`, `BlockStoreUtilsTest_CopyToNewBlock`, and `BlockStoreUtilsTest_CopyToExistingBlock`.

Control flow: Tests create fake source/destination stores and deterministic data fixtures, call utility methods to fill or copy blocks, then read blocks back for equality and preservation checks. Both empty, all-zero, and nonzero data cases are covered.

State and persistence behavior: State lives in fake in-memory block stores. Copy tests verify destination mutation while the original source block remains unchanged.

Dependencies and integration points: Exercises utility logic at the boundary between generic blockstore operations and data buffer helpers.

Risks: Copying into an existing block can accidentally alias or mutate the source, and zero-fill behavior must match block size expectations. Fake stores may not expose all real backend failures.

Test signals: Destination data equality, source data unchanged, empty-block handling, zero-block handling, and successful fake-store reads/writes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/utils/BlockStoreUtilsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/CMakeLists.txt

Purpose: Defines the `cpp-utils-test` build target and its helper executables. It is the central test manifest for cpp-utils coverage across crypto, pointers, process, tempfile, IO, data, logging, assertions, system, threading, value types, and `either`.

Important APIs and types: CMake constructs `cpp-utils-test_exit_status`, `cpp-utils-test_exit_signal`, and the main `${PROJECT_NAME}` executable. It links `my-gtest-main`, `googletest`, and `cpp-utils`, adds the test to CTest, enables style warnings, and activates C++14.

Control flow: CMake enumerates source files, builds small subprocess helper binaries first, then adds them as dependencies of the main test runner.

State and persistence behavior: Build-system state only; no runtime persistence. Helper binaries are runtime dependencies for subprocess/backtrace tests.

Dependencies and integration points: Integrates unit tests with CTest and production `cpp-utils` library.

Risks: Omitting a source here silently drops test coverage. Helper executable naming is coupled to tests that call subprocesses.

Test signals: Successful configure/build, all listed sources compiled, helper binaries available, and `add_test` running the suite.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/MacrosIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/MacrosIncludeTest.cpp

Purpose: A compile-only include test for `cpp-utils/macros.h`. It ensures the public macro header can be included independently.

Important APIs and types: The file includes only `cpp-utils/macros.h` and defines no tests or runtime symbols.

Control flow: The compiler processes the header as part of the `cpp-utils-test` target. There is no runtime execution beyond successful program startup.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards the public include surface used by many helper classes, including move/copy restriction macros.

Risks: Include-order regressions, missing transitive standard headers, or syntax errors in macros would break downstream consumers. Because it is compile-only, it does not validate macro semantics.

Test signals: Successful compilation and linking of the test target with this source present.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/MacrosIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_debug_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_debug_test.cpp

Purpose: Tests the debug-build behavior of CryFS assertion macros. It verifies true assertions pass, false assertions abort or throw depending on abort-disabling mode, and assertion messages include source context and backtraces.

Important APIs and types: Uses `cpp-utils/assert/assert.h`, GoogleTest death/exception assertions, and GoogleMock matchers for message checks.

Control flow: Tests trigger `ASSERT` with true and false expressions, switch the assertion system into non-aborting mode for throw checks, and inspect generated diagnostic strings.

State and persistence behavior: State is process-local assertion configuration and captured death-test subprocess output. No files are persisted.

Dependencies and integration points: Couples assertion macros to backtrace formatting and platform-specific death-test behavior.

Risks: Death tests can be platform/compiler sensitive. Backtrace string content changes may break regex expectations even if failure reporting remains useful.

Test signals: No death for true conditions, death or exception for false conditions, expected message text, and backtrace presence.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_debug_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_release_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_release_test.cpp

Purpose: Verifies release-build assertion behavior, where failed assertions throw rather than relying on debug-only abort semantics. It also checks diagnostic message and backtrace content.

Important APIs and types: Uses `cpp-utils/assert/assert.h`, GoogleTest, GoogleMock, and regex matching for failure messages.

Control flow: Test cases call assertion macros with true and false expressions, expect no throw for true input, expect exceptions for false input, and validate that diagnostics include useful source/backtrace information.

State and persistence behavior: Only process-local assertion behavior and exception objects are involved. No persistent state is written.

Dependencies and integration points: Ensures production release builds still surface assertion failures through exceptions that higher layers can test or catch.

Risks: Release/debug mode compile flags must match the intended test binary. Backtrace formatting can vary across toolchains.

Test signals: Exception type/outcome, message content, and backtrace inclusion.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/assert_release_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/backtrace_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/backtrace_test.cpp

Purpose: Tests backtrace collection and crash/exception reporting across normal exceptions, null pointer access, signals, aborts, and unknown exit codes. It validates both direct backtrace content and subprocess crash diagnostics.

Important APIs and types: Uses `cpp-utils/assert/backtrace.h`, `cpp-utils/process/subprocess.h`, `my-gtest-main.h`, Boost filesystem, signal APIs, and platform-specific Windows branches.

Control flow: Helper functions run the `exit_signal` helper executable with different modes or signals, capture output/status, and assert that reports include stack frames, signal names, or exception messages. Direct tests also ensure caught exceptions do not crash backtrace handling.

State and persistence behavior: Runtime state is subprocess exit status and captured output. No durable files are expected beyond helper binary execution.

Dependencies and integration points: Integrates assertion backtrace code, signal handling, subprocess execution, and test-main crash hooks.

Risks: Highly platform-sensitive: signals, symbolization, line numbers, and Windows exception handling differ by OS/compiler. Tests can be flaky if stack traces are stripped.

Test signals: Expected signal names, exception text, backtrace markers, non-crashing caught-exception path, and correct subprocess failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/backtrace_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/exit_signal.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/exit_signal.cpp

Purpose: Helper executable used by backtrace tests to intentionally terminate through signals, access violations, aborts, and unhandled exceptions.

Important APIs and types: Includes `cpp-utils/assert/backtrace.h`, `<csignal>`, `<stdexcept>`, and Windows exception support where applicable. Implements `main` and signal/exception trigger helpers.

Control flow: `main` parses an argument or mode, installs backtrace handling where needed, then deliberately exits via the requested mechanism. The parent test process captures the result.

State and persistence behavior: No persistent state. It intentionally mutates process control flow by raising signals or throwing uncaught exceptions.

Dependencies and integration points: Built as `cpp-utils-test_exit_signal` and used by `backtrace_test.cpp` through subprocess utilities.

Risks: Behavior depends on OS signal semantics and compiler/runtime exception reporting. The helper must remain simple because any unrelated failure becomes a confusing backtrace-test failure.

Test signals: Parent tests observe expected nonzero exit status and diagnostic text for each termination mode.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/assert/exit_signal.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/crypto/hash/HashTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/crypto/hash/HashTest.cpp

Purpose: Tests salted hashing behavior in `cpp-utils/crypto/hash/Hash`. It verifies salt generation, deterministic hashing for identical data and salt, and changed outputs when data or salt differs.

Important APIs and types: Uses `Hash`, `DataFixture`, and GoogleTest. Test cases exercise salt generation and hash calculation over deterministic `Data` inputs.

Control flow: Each test creates fixture data and one or more salts, calls hash functions, and compares salts or digest outputs for equality or inequality.

State and persistence behavior: All state is in memory: generated salts, input buffers, and digest outputs. No keys or hashes are persisted.

Dependencies and integration points: Connects crypto hash utility code with the `Data` buffer abstraction and deterministic fixtures.

Risks: Indeterminism tests can theoretically collide, though probability should be negligible. These tests validate behavioral properties rather than known-answer vectors.

Test signals: Salt field preserved in hash output, same data/salt yields same digest, and different data or salt yields different digest.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/crypto/hash/HashTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureIncludeTest.cpp

Purpose: Compile-only public include test for `cpp-utils/data/DataFixture.h`.

Important APIs and types: Includes `DataFixture.h` without using other test utilities in this file.

Control flow: No runtime tests are defined; the build verifies that the header is self-contained enough for direct inclusion.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Protects downstream tests and users that include the fixture header directly for deterministic data generation.

Risks: Compile-only coverage cannot detect incorrect generated data, only include and dependency regressions.

Test signals: Successful compilation of the `cpp-utils-test` target with this source present.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureTest.cpp

Purpose: Tests deterministic data fixture generation for different sizes and seeds. It ensures fixtures can create empty, one-byte, and larger buffers and that seeded generation is stable.

Important APIs and types: Uses `cpputils::Data`, `DataFixture`, and GoogleTest through a `DataFixtureTest` fixture.

Control flow: Tests request fixture data of different sizes and seeds, compare repeated generation with the same seed, and compare different seeds for inequality.

State and persistence behavior: In-memory buffers only. The deterministic pseudo-random generator state is implicit in fixture construction and seed input.

Dependencies and integration points: Provides confidence for many other tests that rely on `DataFixture` as reproducible binary input.

Risks: Tests assert deterministic behavior, so changing the generator algorithm is a compatibility change even if callers only require stable size. Different-size determinism is covered by selected examples, not all sizes.

Test signals: Correct sizes, stable bytes for repeated seed/size pairs, and different bytes for distinct seeds.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataIncludeTest.cpp

Purpose: Compile-only include test for the public `cpp-utils/data/Data.h` header.

Important APIs and types: Includes `Data.h` directly and defines no tests.

Control flow: Build system compiles the translation unit to verify the header's standalone include contract.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Protects the main byte-buffer abstraction used across crypto, blockstore, serialization, and test fixtures.

Risks: Compile-only tests do not validate `Data` behavior; semantic coverage is in `DataTest.cpp`.

Test signals: Successful compilation without hidden include-order requirements.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataTest.cpp

Purpose: Broad behavioral test suite for `cpputils::Data`, the dynamic byte buffer abstraction. It covers copy isolation, zero initialization/filling, move construction/assignment, equality/inequality, large sizes, file loading, and allocator ownership.

Important APIs and types: Uses `Data`, `DataFixture`, `SerializationHelper`, `TempFile`, fstreams, GoogleMock, and a `MockAllocator` fixture to validate allocation/free calls.

Control flow: Tests construct buffers from sizes, fixtures, files, and allocators; mutate copies; move buffers; store/load bytes; and compare content. Parameterized fixtures exercise size and string/binary inputs.

State and persistence behavior: Mostly in-memory buffer ownership. File-based tests use temporary files to verify load/store behavior and cleanup through `TempFile`.

Dependencies and integration points: Critical for crypto, serialization, and blockstore code that depend on `Data` byte ownership and move semantics.

Risks: Allocator tests are sensitive to exact ownership transfer timing. Large-size tests must avoid excessive memory in constrained environments.

Test signals: Correct byte contents, zero-filled buffers, equality results, file bytes, expected allocator calls, and no double-free after moves.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/data/FixedSizeData.h`.

Important APIs and types: Includes `FixedSizeData.h` directly.

Control flow: No runtime logic; the compiler validates header independence.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Protects callers that use fixed-length byte arrays for hashes, IDs, keys, and serialized values.

Risks: Does not validate data semantics; `FixedSizeDataTest.cpp` carries behavioral coverage.

Test signals: Successful compilation without missing transitive includes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataTest.cpp

Purpose: Tests `FixedSizeData<N>` equality, inequality, copy/assignment behavior, conversion/storage behavior, and object-size expectations.

Important APIs and types: Uses `FixedSizeData`, `Data`, `DataFixture`, parameterized GoogleTest fixtures, and helper comparisons such as `EXPECT_DATA_EQ`.

Control flow: Tests build fixed-size buffers from deterministic fixtures or binary/string parameters, copy and assign them, compare expected bytes, and assert source data is unchanged.

State and persistence behavior: All data is in-memory fixed-size byte storage. No files are persisted.

Dependencies and integration points: Fixed-size data is foundational for cryptographic identifiers and serialized binary values where size must be compile-time enforced.

Risks: The lightweight-object assertion locks in layout/performance assumptions. Parameter coverage is representative, not exhaustive for every possible size.

Test signals: Exact byte equality/inequality, copy and assignment preserving source, expected fixed object size, and successful conversion with `Data`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/SerializationHelperTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/SerializationHelperTest.cpp

Purpose: Tests typed serialization/deserialization helpers for integers, floats, doubles, structs, one-byte structs, alignment, unaligned offsets, negative values, and explicit offsets.

Important APIs and types: Uses `SerializationHelper`, `Data`, GoogleTest, and local structs `DataStructure` and `OneByteStruct`.

Control flow: Each test writes a value into a `Data` buffer at aligned or unaligned positions, reads it back, and checks equality. Signed/unsigned integer widths from 8 to 64 bits and floating-point types are covered.

State and persistence behavior: State is in-memory binary buffers. No endian conversion persistence files are produced.

Dependencies and integration points: Serialization helpers are used anywhere CryFS stores typed values inside raw `Data` buffers.

Risks: Tests generally validate roundtrip on the host platform, so cross-endian or ABI packing expectations need separate known-byte tests if required. Struct serialization depends on layout.

Test signals: Correct roundtrip for every primitive width, aligned/unaligned offset handling, struct roundtrip, and offset-specific deserialize behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/SerializationHelperTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/either_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/either_test.cpp

Purpose: Exhaustive behavioral test suite for `cpputils::either<L,R>`, including construction, factories, copy/move semantics, accessors, optional access, same-type variants, movable-only values, multi-argument construction, equality, streaming, destructor behavior, and storage size.

Important APIs and types: Uses `either`, `make_left`, `make_right`, `left/right`, `left_opt/right_opt`, `is_left/is_right`, emplace-style construction, comparison operators, stream output, `MovableOnly`, destructor callback helper classes, Boost optional, and GoogleMock.

Control flow: Matrix helper functions run the same expectations over multiple construction paths. Later tests exercise copy/move construction and assignment for left/right alternatives, mutation through accessors, equality comparisons, and destructor counts after copies/moves/assignments.

State and persistence behavior: Variant state is purely in-memory with one active alternative. Destructor tests use counters/callbacks to prove active object lifetime transitions.

Dependencies and integration points: Protects a core utility similar to `std::variant`/`Either`, used by code that needs explicit success/error or left/right results.

Risks: The suite locks in moved-from behavior and compact storage expectations. Exception-safety and noexcept tag coverage is noted as a TODO.

Test signals: Correct active side, expected access exceptions, optional values, moved/copy-preserved payloads, destructor calls, comparisons, output text, and no excess storage overhead.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/either_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/io/Console.h`.

Important APIs and types: Includes the public console abstraction header.

Control flow: No runtime tests; compilation validates public include dependencies.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects users of the console interface, which is implemented by `IOStreamConsole` and tested in console behavior suites.

Risks: Compile-only coverage does not validate prompt or IO behavior.

Test signals: Successful compilation with direct public header inclusion.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest.h

Purpose: Declares shared fixtures and async helpers for console tests. It lets tests drive an `IOStreamConsole` through pipe streams while asserting output lines and sending input lines.

Important APIs and types: Defines `ConsoleThread`, `ConsoleTest`, `print`, `EXPECT_OUTPUT_LINES`, `EXPECT_OUTPUT_LINE`, and `sendInputLine`. Uses `IOStreamConsole`, futures, threads, and `pipestream`.

Control flow: Console operations are run on a helper thread so tests can feed stdin and observe stdout in controlled order. Assertion helpers compare emitted output lines.

State and persistence behavior: State is in-memory pipes, thread/future state, and console object state. No filesystem persistence.

Dependencies and integration points: Provides the harness for ask, password, yes/no, and print console tests.

Risks: Async IO tests can deadlock if prompts or input expectations drift. The fixture must close/join threads reliably.

Test signals: Prompt output ordering, consumed input, returned answers, and no hanging helper thread.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Ask.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Ask.cpp

Purpose: Tests multi-option console prompts. It verifies option rendering, numeric selection, whitespace trimming, empty input handling, out-of-range numbers, and non-numeric retry behavior.

Important APIs and types: Uses `ConsoleTest` fixture and `IOStreamConsole::ask`-style behavior through helper methods.

Control flow: Each test starts an ask call, checks prompt output, sends one or more input lines, and asserts the returned selected option. Invalid input tests verify reprompt loops.

State and persistence behavior: State is pipe-backed stdin/stdout and the pending async console operation. No persistent state.

Dependencies and integration points: Integrates the console abstraction with user-facing CLI prompt behavior.

Risks: Text formatting and input parsing are tightly coupled to CLI UX. Tests can hang if a reprompt is missing or expected input is not consumed.

Test signals: Correct selected index/value, output line content, whitespace tolerance, crash/throw for no options, and recovery after invalid input.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Ask.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskPassword.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskPassword.cpp

Purpose: Tests password prompt input handling for non-empty and empty passwords.

Important APIs and types: Uses `ConsoleTest` and the console password prompt API. The fixture controls stdin/stdout through pipe streams.

Control flow: The test starts the password prompt asynchronously, sends an input line, and asserts the returned password string.

State and persistence behavior: Password data exists only in memory during the test. No files are written.

Dependencies and integration points: Covers CLI credential-entry behavior at the console abstraction boundary. Echo-disabling behavior is covered elsewhere.

Risks: These tests validate returned strings but not terminal echo state on real TTYs. Empty password acceptance is an explicit behavioral contract.

Test signals: Returned password matches input for ordinary and empty input without deadlock.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskPassword.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskYesNo.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskYesNo.cpp

Purpose: Tests yes/no console prompt parsing. It accepts uppercase/lowercase `yes`, `y`, `no`, and `n`, trims surrounding spaces, rejects empty input, and reprompts after wrong input.

Important APIs and types: Uses helper macros/functions `EXPECT_TRUE_ON_INPUT`, `EXPECT_FALSE_ON_INPUT`, and `EXPECT_RESULT_ON_INPUT` from the console test fixture.

Control flow: Each test starts a yes/no prompt, feeds one or more input lines, and asserts the returned boolean. Invalid input tests verify retry behavior before success.

State and persistence behavior: Only pipe-backed console state and async result futures are used.

Dependencies and integration points: Supports CLI confirmation flows that depend on robust parsing and predictable prompts.

Risks: Locale or alternative yes/no strings are not covered. Tests are sensitive to prompt/read ordering.

Test signals: Boolean result for accepted forms, whitespace trimming, retry after bad input, and no hanging async prompt.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_AskYesNo.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Print.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Print.cpp

Purpose: Tests simple console printing through the shared console fixture.

Important APIs and types: Uses `ConsoleTest::print` and output-line assertion helpers.

Control flow: The test prints content through the `IOStreamConsole` wrapper and asserts the expected output line appears.

State and persistence behavior: Output is captured through in-memory pipe streams. No files or terminal state are persisted.

Dependencies and integration points: Validates the basic output path used by CLI prompts and status messages.

Risks: Narrow coverage; formatting changes outside basic print behavior are covered by specific prompt tests.

Test signals: Captured stdout line equals expected print text.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ConsoleTest_Print.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/DontEchoStdinToStdoutRAIITest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/DontEchoStdinToStdoutRAIITest.cpp

Purpose: Smoke-tests the RAII helper that disables stdin echo to stdout. It currently verifies construction/destruction does not crash.

Important APIs and types: Uses `DontEchoStdinToStdoutRAII` through its public header and GoogleTest.

Control flow: A test creates the RAII object and lets it destruct at scope exit.

State and persistence behavior: The production object may manipulate terminal echo state, but this test does not inspect terminal attributes. No persistent state is written.

Dependencies and integration points: Supports password prompt behavior by guarding terminal echo changes.

Risks: This is weak behavioral coverage; it cannot detect whether echo was actually disabled/restored on a real TTY.

Test signals: Object construction/destruction completes without throwing or crashing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/DontEchoStdinToStdoutRAIITest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ProgressBarTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ProgressBarTest.cpp

Purpose: Tests progress bar output behavior, including rendering at start, intermediate progress, completion, and likely edge values.

Important APIs and types: Uses `cpp-utils/io/ProgressBar` with GoogleTest and captured output expectations.

Control flow: Tests construct a progress bar, update progress amounts, and compare emitted console/output strings or lack of crashes depending on scenario.

State and persistence behavior: State is in-memory progress counters and captured output. No persistent state.

Dependencies and integration points: Progress bar output is user-facing in CLI flows; this test guards formatting and update behavior.

Risks: Progress formatting can be terminal-width or carriage-return sensitive. Tests may be brittle if presentation changes intentionally.

Test signals: Expected output for progress states and successful handling of boundary progress values.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/io/ProgressBarTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/ConditionBarrierIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/ConditionBarrierIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/lock/ConditionBarrier.h`.

Important APIs and types: Includes the condition barrier public header.

Control flow: No runtime tests are defined.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects thread synchronization helpers used by subprocess and thread tests.

Risks: Does not test blocking/wakeup semantics, only header self-containment.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/ConditionBarrierIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/LockPoolIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/LockPoolIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/lock/LockPool.h`.

Important APIs and types: Includes the public lock-pool header.

Control flow: No runtime logic; the translation unit validates direct inclusion.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Lock pools are used where keyed synchronization is needed without manually managing many mutexes.

Risks: Does not validate lock identity, lifetime, or concurrency semantics.

Test signals: Header compiles independently.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/LockPoolIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/MutexPoolLockIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/MutexPoolLockIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/lock/MutexPoolLock.h`.

Important APIs and types: Includes the mutex-pool lock public header.

Control flow: No runtime test cases are declared.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards an RAII lock wrapper used with pooled mutexes.

Risks: Compile-only coverage cannot catch deadlock, unlock, or keyed mutex selection bugs.

Test signals: Successful direct header compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/lock/MutexPoolLockIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/logging/Logger.h`.

Important APIs and types: Includes the logger public header.

Control flow: No runtime tests are defined.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects logging interface consumers from hidden include-order requirements.

Risks: Does not validate emitted log lines or logger state; behavior tests cover that separately.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerTest.cpp

Purpose: Tests basic `Logger` object behavior, likely including construction, naming, and level/output integration.

Important APIs and types: Uses `cpp-utils/logging/Logger` and GoogleTest.

Control flow: Test cases construct logger objects and assert observable behavior through logging helpers or captured output.

State and persistence behavior: Logger state is in-memory configuration and emitted messages. Persistent files are not central in this file.

Dependencies and integration points: Complements broader logging tests by validating the lower-level logger class directly.

Risks: Logger tests can be sensitive to global logging sinks or levels shared across the process.

Test signals: Expected logger construction and output/level behavior without cross-test contamination.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggerTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingIncludeTest.cpp

Purpose: Compile-only include test for the aggregate `cpp-utils/logging/logging.h` header.

Important APIs and types: Includes the public logging facade header.

Control flow: No runtime test cases.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards the header most callers use for logging macros/facade functions.

Risks: Does not validate macro expansion or runtime filtering; other logging tests cover semantics.

Test signals: Successful direct include compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingLevelTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingLevelTest.cpp

Purpose: Tests logging-level parsing, ordering, formatting, or filtering behavior. It protects the contract for severity levels used by the logging facade.

Important APIs and types: Uses logging level types/functions from cpp-utils and GoogleTest/GoogleMock.

Control flow: Test cases compare levels, convert between enum/string forms, and validate which messages should be emitted or suppressed for configured levels.

State and persistence behavior: Process-local logging configuration may be changed during tests. No durable persistence is expected.

Dependencies and integration points: Logging levels influence CLI verbosity, diagnostics, and test log capture throughout CryFS.

Risks: Global logging state must be reset between tests. String names are user-facing and compatibility-sensitive.

Test signals: Exact level conversions, ordering comparisons, and enabled/disabled message behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingLevelTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingTest.cpp

Purpose: Tests the higher-level logging facade/macros, including emitted message content, level filtering, logger names, and captured output behavior.

Important APIs and types: Uses cpp-utils logging headers, `LoggingTest` helpers, GoogleTest, and captured output utilities.

Control flow: Tests configure logging, emit messages at different levels or through different loggers, and assert captured output matches expected content or suppression.

State and persistence behavior: Runtime logging configuration and sink/capture state are process-local. No persistent log file is central unless the production API writes one under test.

Dependencies and integration points: Logging is used across CLI and library diagnostics, so facade behavior affects observability and tests that capture stderr/stdout.

Risks: Global logging state can leak across tests. Formatting expectations can become brittle when timestamps or prefixes change.

Test signals: Expected log text, level filtering, logger selection, and clean restoration of logging state.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/LoggingTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/testutils/LoggingTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/testutils/LoggingTest.h

Purpose: Declares shared utilities for logging tests, centralizing setup, capture, and assertions around global logging behavior.

Important APIs and types: Provides a `LoggingTest` fixture/helper around logger setup and expected output checks. It integrates with GoogleTest and cpp-utils logging classes.

Control flow: Downstream tests use the fixture to configure logging state, emit messages, and restore state after assertions.

State and persistence behavior: Manages process-global logging sinks/levels during test scope. No durable persistence is required.

Dependencies and integration points: Supports `LoggerTest`, `LoggingLevelTest`, and `LoggingTest` suites by preventing duplicated global setup.

Risks: Any missed teardown can contaminate later tests. Helpers must avoid hiding important behavior such as exact output destinations.

Test signals: Tests using the helper should see isolated logging state and deterministic captured output.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/logging/testutils/LoggingTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_include_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/pointer/cast.h`.

Important APIs and types: Includes the pointer cast helper header.

Control flow: No runtime tests in this file.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards public pointer casting helpers used in ownership/conversion code.

Risks: Does not validate cast safety or runtime checks; `cast_test.cpp` covers behavior.

Test signals: Successful direct header inclusion.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_include_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_test.cpp

Purpose: Tests pointer casting helpers for raw pointers and smart/ownership wrappers, including valid up/down casts and invalid cast handling.

Important APIs and types: Uses `cpp-utils/pointer/cast.h`, GoogleTest, and local base/derived test classes.

Control flow: Test cases construct objects through different pointer forms, call cast helpers, and assert resulting object identity/value or failure behavior.

State and persistence behavior: In-memory object ownership and pointer identity only. No persistent state.

Dependencies and integration points: These helpers support safe conversions in code using `unique_ref`, `unique_ptr`, and related pointer abstractions.

Risks: Cast behavior may differ with RTTI settings or polymorphic base requirements. Ownership-preserving casts must avoid leaks and double deletes.

Test signals: Correct pointer identity after valid casts, expected failure on invalid casts, and ownership transfer without leaks.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/cast_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_include_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/pointer/optional_ownership_ptr.h`.

Important APIs and types: Includes the optional ownership pointer public header.

Control flow: No runtime tests are declared.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects code using a pointer abstraction that may or may not own its pointee.

Risks: Compile-only coverage does not validate lifetime semantics.

Test signals: Header compiles independently.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_include_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_test.cpp

Purpose: Tests `optional_ownership_ptr`, a pointer wrapper that can either own or non-own a pointee while presenting pointer-like access.

Important APIs and types: Uses the optional ownership pointer header, GoogleTest, and local test objects/destructor counters.

Control flow: Tests create owning and non-owning instances, dereference/access pointees, move or reset wrappers, and verify destruction behavior matches ownership mode.

State and persistence behavior: In-memory pointer ownership and object lifetime. Destructor counters or flags provide test state.

Dependencies and integration points: Useful where APIs optionally assume responsibility for object deletion without changing call syntax.

Risks: The key risk is double-free or leak when ownership mode changes or wrappers move. Non-owning pointers also risk dangling references outside the test's controlled lifetime.

Test signals: Correct dereference values, expected destructor calls for owning pointers, no destructor call for non-owning pointers, and valid move behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/optional_ownership_ptr_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround_include_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround_include_test.cpp

Purpose: Compile-only include test for the Boost optional/GoogleTest workaround supporting `unique_ref` values.

Important APIs and types: Includes `cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h`.

Control flow: No runtime logic.

State and persistence behavior: No state or persistence.

Dependencies and integration points: This workaround is included by tests that compare `boost::optional<unique_ref<...>>` or related optional pointer-like values.

Risks: Only catches include breakage; semantic failures would appear in tests using optional `unique_ref` values.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround_include_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_include_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/pointer/unique_ref.h`.

Important APIs and types: Includes the public non-null unique ownership wrapper header.

Control flow: No runtime tests.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects a widely used ownership abstraction across CryFS code.

Risks: Does not test ownership behavior; `unique_ref_test.cpp` provides broad semantic coverage.

Test signals: Successful direct header compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_include_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_test.cpp

Purpose: Comprehensive test suite for `unique_ref`, CryFS's non-null unique ownership wrapper. It verifies creation, conversion to base classes and standard smart pointers, nullcheck conversion from `unique_ptr`, dereference/get/arrow, move construction/assignment, validity after moves, swap, containers, comparisons, hashing, ordering, and type aliases.

Important APIs and types: Uses `unique_ref`, `make_unique_ref`, `nullcheck`, conversions to `unique_ptr`/`shared_ptr`, `is_valid`, `swap`, comparison/hash operators, STL containers, and local base/child/value classes.

Control flow: Tests construct objects with zero/one/two constructor parameters, transfer ownership through moves and conversions, intentionally inspect moved-from invalid state, place refs in sequence/ordered/unordered containers, and compare pointer identity/order/hash behavior.

State and persistence behavior: In-memory object ownership only. The wrapper can become invalid after move, which is explicitly tested.

Dependencies and integration points: Many CryFS components use `unique_ref` for non-null ownership while interoperating with standard smart pointers.

Risks: Moved-from invalid access, base-class conversions, and hash/order behavior are subtle. Container support can accidentally require copyability.

Test signals: Correct payload access, ownership transfer without leaks, invalid moved-from state, standard pointer conversion, container compatibility, and comparison/hash results.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/pointer/unique_ref_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalCatcherTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalCatcherTest.cpp

Purpose: Tests scoped signal-catching behavior for SIGINT and SIGTERM. It verifies absence of a catcher causes death, active catchers intercept configured signals, multiple/nested catchers route signals correctly, and expired catchers restore previous behavior.

Important APIs and types: Uses `cpp-utils/process/SignalCatcher.h`, GoogleTest death tests, and `<csignal>`.

Control flow: Helper `raise_signal` triggers signals under different catcher scopes. Tests assert death or caught state depending on active catcher stack and signal order.

State and persistence behavior: Mutates process signal handlers during test scope and restores them through RAII. No persistent state.

Dependencies and integration points: Supports graceful CLI/process shutdown logic that reacts to interrupt/termination signals.

Risks: Signal tests are platform- and test-runner-sensitive. Global signal handlers require careful restoration to avoid contaminating later tests.

Test signals: Expected death without catcher, correct catcher notified for each signal, nested handler precedence, and restored default behavior after scope exit.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalCatcherTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalHandlerTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalHandlerTest.cpp

Purpose: Tests lower-level signal handler registration for SIGINT and SIGTERM, including no-handler death, single-handler catch, wrong-signal death, combined handlers, and multiple handlers for one signal.

Important APIs and types: Uses `cpp-utils/process/SignalHandler.h`, GoogleTest death tests, and helper callbacks.

Control flow: Tests register handlers in scope, raise signals, and assert callback invocation or process death. Multiple-handler tests verify the active handler selection.

State and persistence behavior: Temporarily modifies global process signal handlers. No durable persistence.

Dependencies and integration points: `SignalCatcher` and CLI shutdown flows depend on this lower-level signal handling contract.

Risks: Global signal state can leak if RAII restoration fails. Death-test behavior varies by platform and test runner.

Test signals: Correct callback for configured signals, death for unhandled signals, and expected behavior with multiple handlers.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SignalHandlerTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SubprocessTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SubprocessTest.cpp

Purpose: Tests subprocess invocation helpers for checked and unchecked calls, output capture, exit code handling, arguments containing spaces, command lookup through PATH, and calls from threads.

Important APIs and types: Uses `cpp-utils/process/subprocess.h`, Boost filesystem, `ConditionBarrier`, `LoopThread`, and `my-gtest-main` helpers. It depends on the `cpp-utils-test_exit_status` helper executable.

Control flow: Tests call helper commands that exit with success or specific errors, capture stdout/stderr, assert thrown exceptions for checked failures, inspect returned status/output for unchecked calls, and exercise threaded invocation.

State and persistence behavior: Runtime state is child process execution, captured output, exit status, environment/PATH lookup, and synchronization primitives. No intended persistent files.

Dependencies and integration points: Backtrace tests and CLI tests depend on reliable subprocess behavior.

Risks: PATH resolution, quoting, spaces in arguments, and threaded calls are platform-sensitive. Helper binary availability is coupled to CMake dependencies.

Test signals: Exact exit codes, output strings, expected exceptions, successful threaded execution, and correct handling of spaced arguments.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/SubprocessTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/daemonize_include_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/daemonize_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/process/daemonize.h`.

Important APIs and types: Includes daemonization public header.

Control flow: No runtime daemonization is performed.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards CLI/process code that includes daemonization helpers.

Risks: Does not validate fork/session/stdout behavior, only header self-containment.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/daemonize_include_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/exit_status.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/exit_status.cpp

Purpose: Helper executable for subprocess tests. It exits with requested status codes and emits predictable output so parent tests can validate capture and error handling.

Important APIs and types: Uses standard `iostream` and `cstdlib`; implements `main`.

Control flow: `main` reads command-line arguments, optionally prints output, and returns the requested code.

State and persistence behavior: No persistent state; only process exit status and stdout/stderr are observed.

Dependencies and integration points: Built as `cpp-utils-test_exit_status` and used by `SubprocessTest.cpp`.

Risks: Any change to output text or argument handling must be coordinated with subprocess assertions.

Test signals: Parent tests observe expected output and exit codes across success and failure cases.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/exit_status.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/subprocess_include_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/subprocess_include_test.cpp

Purpose: Compile-only include test for `cpp-utils/process/subprocess.h`.

Important APIs and types: Includes the public subprocess helper header.

Control flow: No runtime subprocess is launched in this file.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects consumers of subprocess utilities from hidden include-order dependencies.

Risks: Does not validate execution semantics; `SubprocessTest.cpp` provides behavioral coverage.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/process/subprocess_include_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/random/RandomIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/random/RandomIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/random/Random.h`.

Important APIs and types: Includes the public random helper header.

Control flow: No runtime random generation is performed.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards users of random utilities, including crypto/test fixture code that may include the header directly.

Risks: Does not validate entropy quality or deterministic behavior.

Test signals: Successful direct header compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/random/RandomIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/EnvTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/EnvTest.cpp

Purpose: Tests environment variable helper functions for setting, reading, and unsetting values, including values with spaces.

Important APIs and types: Uses `cpp-utils/system/env.h`, `std::string`, and GoogleTest.

Control flow: Tests set an environment variable, read it back, repeat with a spaced value, unset it, and verify the read result is empty.

State and persistence behavior: Mutates the process environment. Changes are process-local but can affect later tests if variable names collide or cleanup fails.

Dependencies and integration points: CLI and system utilities use environment helpers for home/config and runtime behavior.

Risks: Environment mutation is global to the process. Platform differences in unset/get semantics may matter.

Test signals: Exact value returned after set, spaced value preserved, and empty result after unset.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/EnvTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/FiletimeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/FiletimeTest.cpp

Purpose: Tests file timestamp get/set helpers by applying a known time to a temporary file and reading it back.

Important APIs and types: Uses `cpp-utils/system/filetime.h`, `TempFile`, platform `timespec` handling, and GoogleTest.

Control flow: Creates a temp file, sets its modification/access time, retrieves it, and compares expected timestamp fields.

State and persistence behavior: Mutates metadata of a temporary file that is cleaned up after the test.

Dependencies and integration points: Timestamp helpers are relevant for filesystem metadata preservation and platform abstraction.

Risks: Filesystem timestamp precision differs by platform and filesystem. Tests must account for truncation/rounding.

Test signals: Retrieved timestamp equals the expected time within the semantics encoded by the helper.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/FiletimeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/GetTotalMemoryTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/GetTotalMemoryTest.cpp

Purpose: Smoke-tests total system memory detection.

Important APIs and types: Uses `cpp-utils/system/get_total_memory.h` and GoogleTest.

Control flow: Tests call the memory query function and assert it does not crash and returns a nonzero value.

State and persistence behavior: Reads system information only; no persistence or mutation.

Dependencies and integration points: Memory detection can drive cache sizing or resource decisions in production code.

Risks: Nonzero is a weak semantic assertion; containerized or unusual platforms may report constrained values.

Test signals: Function completes and returns greater than zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/GetTotalMemoryTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/HomedirTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/HomedirTest.cpp

Purpose: Tests home-directory and application-data directory helpers, including fake home directory RAII overrides.

Important APIs and types: Uses `cpp-utils/system/homedir.h`, `TempDir`, and GoogleTest.

Control flow: Tests verify the real home directory exists, app-data path is valid, fake home directory scopes set and reset home/appdata values, and temp fake home uses distinct home/appdata directories.

State and persistence behavior: Reads real environment/system home paths and temporarily overrides process-level home directory behavior. Temporary directories are created and cleaned up.

Dependencies and integration points: CryFS CLI/config code depends on reliable home and app-data paths.

Risks: Platform differences in home/appdata conventions and environment variables can affect expectations. Fake overrides must restore global state.

Test signals: Existing home path, valid appdata path, correct fake path during scope, restored path after scope, and distinct temp fake dirs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/HomedirTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/MemoryTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/MemoryTest.cpp

Purpose: Smoke-tests memory locking helpers with small and large allocation requests.

Important APIs and types: Uses `cpp-utils/system/memory.h`, standard smart pointers, compatibility helpers, and GoogleTest.

Control flow: Tests request locked memory regions or lock operations and assert they complete without crashing for small and large cases.

State and persistence behavior: Temporarily allocates/locks process memory. No persistent state.

Dependencies and integration points: Secure-memory or key-handling code may rely on these helpers to reduce swapping of sensitive data.

Risks: Actual lock success can depend on OS permissions and resource limits; these tests focus on no-crash behavior rather than guaranteed mlock.

Test signals: Locking calls complete without throwing/crashing for representative sizes.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/MemoryTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/PathTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/PathTest.cpp

Purpose: Tests path helper behavior for detecting drive-letter-only paths and non-Windows expectations.

Important APIs and types: Uses `cpp-utils/system/path.h` and GoogleTest.

Control flow: Tests call path classification helpers with drive-letter-style and platform-specific path strings.

State and persistence behavior: Pure string/path logic; no filesystem mutation.

Dependencies and integration points: CLI option parsing and filesystem path normalization depend on correct platform path handling.

Risks: Windows vs non-Windows behavior must stay gated correctly. Path syntax edge cases beyond drive letters are not covered here.

Test signals: Correct boolean classification for drive-letter paths and expected non-Windows behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/PathTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/TimeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/TimeTest.cpp

Purpose: Tests time helper functions for current time retrieval, monotonic/nondecreasing behavior, change after pause, and comparison operators.

Important APIs and types: Uses `cpp-utils/system/time.h`, `std::chrono`, `std::thread`, platform `timespec` comparisons, and GoogleTest.

Control flow: Tests fetch current time, compare it against a year-2010 lower bound, read consecutive times, sleep briefly, and assert relational operators for prepared values.

State and persistence behavior: Reads system clock only. No persistent state.

Dependencies and integration points: Time helpers are used in logging, retry/timeout logic, and filesystem metadata.

Risks: Wall-clock adjustments can affect nondecreasing assumptions if not using a monotonic source. Sleep-based tests can be timing-sensitive on slow systems.

Test signals: Current time sane, nondecreasing reads, increased after pause, and correct `<`, `>`, `<=`, `>=`, `==`, `!=` behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/system/TimeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/tempfile/TempDir.h`.

Important APIs and types: Includes the temporary directory RAII header.

Control flow: No runtime tests.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Guards direct inclusion for tests and production utilities that need temporary directories.

Risks: Does not validate cleanup behavior; `TempDirTest.cpp` covers that.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirTest.cpp

Purpose: Tests `TempDir` RAII behavior: directory creation, initial emptiness, writability, and deletion after scope exit.

Important APIs and types: Uses `TempDir`, fstream, GoogleTest, and helper functions to count entries and create files.

Control flow: Tests construct a `TempDir`, inspect its path, create files inside it, verify write access, then leave scope and assert deletion.

State and persistence behavior: Creates real temporary directories and files, then relies on RAII cleanup to remove them.

Dependencies and integration points: Many tests use temporary directories for safe filesystem state isolation.

Risks: Cleanup can fail due to open handles or permissions, especially on Windows. Counting entries can be platform-sensitive if hidden/system files appear.

Test signals: Directory exists, starts empty, accepts writes, and no longer exists after destructor.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempDirTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileIncludeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/tempfile/TempFile.h`.

Important APIs and types: Includes the temporary file RAII header.

Control flow: No runtime tests.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Protects tests and utilities that create temporary files.

Risks: Does not validate file creation or cleanup; behavior is covered in `TempFileTest.cpp`.

Test signals: Successful compilation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileIncludeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileTest.cpp

Purpose: Tests `TempFile` RAII behavior across default paths, explicit paths, create-now versus do-not-create modes, readability, writability, emptiness, creatability, and deletion after use.

Important APIs and types: Uses `TempFile`, `TempDir`, fstream, GoogleTest, and helper `CreateFile`.

Control flow: Tests construct temp files under different options, inspect existence and contents, open them for reading/writing, optionally create missing files manually, and assert cleanup after scope.

State and persistence behavior: Creates real temporary files in temp directories and removes them via RAII. Explicit path tests create files under a controlled `TempDir`.

Dependencies and integration points: Used throughout tests that require filesystem-backed temporary data.

Risks: File deletion can fail with open handles. Explicit-path behavior must avoid deleting unrelated files if API is misused.

Test signals: Expected existence/non-existence, readable/writable empty file, manual creatability when not pre-created, and deletion after destructor.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/tempfile/TempFileTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/LeftRightTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/LeftRightTest.cpp

Purpose: Tests the `LeftRight` concurrency helper, which allows reads and writes with a double-buffer-like synchronization model. It covers integer/vector state, return values, concurrent reads, read/write concurrency, write exclusion, and exception safety.

Important APIs and types: Uses `cpp-utils/thread/LeftRight.h`, GoogleTest, vectors, local `MyException`, and threaded reader/writer lambdas.

Control flow: Tests perform read and write transactions, run concurrent readers/writers, and deliberately throw exceptions inside read or write callbacks to verify propagation and state recovery.

State and persistence behavior: State is in-memory protected data. Write exception tests validate whether old state is restored or new state kept depending on which phase fails.

Dependencies and integration points: Useful for thread-safe shared state with high read concurrency.

Risks: Concurrency tests can be timing-sensitive and may not exhaustively expose races. Exception-safety behavior is subtle and compatibility-sensitive.

Test signals: Correct visible state after writes, concurrent reads allowed, writes serialized, reads concurrent with writes as designed, returned values, propagated exceptions, and state rollback/commit semantics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/LeftRightTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/debugging_test.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/debugging_test.cpp

Purpose: Tests thread debugging helpers for setting and getting thread names from main and child threads.

Important APIs and types: Uses `cpp-utils/thread/debugging.h`, assertions, `ConditionBarrier`, GoogleTest, and `std::thread`.

Control flow: Tests set/get the main thread name, spawn child threads, set names inside or outside the child, synchronize with barriers, and assert retrieved names.

State and persistence behavior: Mutates OS/thread-local thread name state during the process. No persistent state.

Dependencies and integration points: Thread names improve diagnostics and backtraces for concurrent code.

Risks: Thread name APIs differ by platform and may truncate names. Outside-thread name retrieval can be OS-specific.

Test signals: No crashes setting names, correct name observed from inside child/main threads, and expected name when reading child thread from outside.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/thread/debugging_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/value_type/ValueTypeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/value_type/ValueTypeTest.cpp

Purpose: Tests macro/template-generated value types for IDs, ordered IDs, quantities, and flags. It validates strong typing, constexpr behavior, comparisons, hashing/containers, arithmetic, and flag operations.

Important APIs and types: Defines local types such as `MyIdValueType`, `MyOrderedIdValueType`, `MyQuantityValueType`, and `MyFlagsValueType` using `ValueType.h`. Uses GoogleTest plus `set` and `unordered_set`.

Control flow: Typed test suites and static/constexpr checks instantiate value wrappers, compare values, insert them into containers, and exercise operations allowed by each category.

State and persistence behavior: All state is in-memory wrapped primitive values. No persistence.

Dependencies and integration points: Strong value types prevent accidental mixing of IDs, sizes, and flags across CryFS APIs.

Risks: Macros can produce broad API surfaces; tests must ensure unwanted operations are unavailable as well as wanted operations working. Compile-time-only failures are not always visible as runtime tests.

Test signals: Correct equality/order/hash behavior, constexpr construction, arithmetic for quantities, bitwise flag semantics, and container compatibility.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cpp-utils/value_type/ValueTypeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CMakeLists.txt

Purpose: Defines the `cryfs-cli-test` target and its test source manifest. It wires CLI behavior tests, program-options tests, version checking, integrity checks, and unmount tests into CTest.

Important APIs and types: CMake lists sources, creates the executable, links `my-gtest-main`, `googletest`, `cryfs-cli`, `cryfs-unmount`, and `fspp-fuse`, registers `add_test`, enables style warnings, and activates C++14.

Control flow: During build, all listed CLI test sources are compiled into one runner. CTest runs the executable as `cryfs-cli-test`.

State and persistence behavior: Build-system state only. Runtime persistence is owned by individual tests that create temp basedirs/mountpoints.

Dependencies and integration points: Integrates CLI library, unmount CLI, and FUSE test support.

Risks: Missing a source removes coverage silently. Linking FUSE-related libraries can make the test target platform-sensitive.

Test signals: Successful build/link and CTest registration of the CLI test runner.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CallAfterTimeoutTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CallAfterTimeoutTest.cpp

Purpose: Tests `CallAfterTimeout`, a timer helper that invokes a callback after a delay unless reset. It verifies one-shot behavior and reset behavior.

Important APIs and types: Uses `cryfs-cli/CallAfterTimeout.h`, `unique_ref`, atomics, and GoogleTest. Fixture helper `callAfterTimeout` likely constructs the timer with a test callback and timeout.

Control flow: Tests start a timer, optionally reset it once or twice, wait enough time, and assert callback count/state. `DoesntCallTwice` ensures callbacks are not repeated after firing.

State and persistence behavior: State is in-memory timer/thread state and atomic callback counters. No persistence.

Dependencies and integration points: Supports CLI auto-unmount or idle-timeout behavior.

Risks: Timing tests can be flaky under scheduler delays. Reset races are the key correctness concern.

Test signals: Callback fires after no reset, fires only once, and delayed firing follows one or two resets.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CallAfterTimeoutTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_IntegrityCheck.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_IntegrityCheck.cpp

Purpose: Tests CryFS CLI integrity protections around filesystem ID, filesystem key, rollback of basedir contents, and rollback while mounted.

Important APIs and types: Uses `CliTest`, `CryConfigFile`, `ErrorCodes`, `Scrypt`, `DataFixture`, `TempDir`, `CachingFsBlobStore`, and a `FakeCryKeyProvider`. Helper methods modify config fields, write/read files, recursively copy basedirs, and verify reads.

Control flow: Tests create or mount a test filesystem, tamper with config or basedir state, run CLI mount/integrity paths, and assert expected failures or unmount behavior when rollback is detected.

State and persistence behavior: Uses real temporary basedir/mountdir/config state and blobstore contents. The rollback tests intentionally copy and restore filesystem directory snapshots.

Dependencies and integration points: Integrates CLI setup, config encryption/KDF, blobstore caching, filesystem IDs/keys, and error-code handling.

Risks: These tests are filesystem- and mount-sensitive. Tampering helpers must modify the intended metadata without corrupting unrelated setup.

Test signals: Mount fails for incorrect filesystem ID/key, basedir rollback is rejected, and rollback while mounted causes unmount/error behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_IntegrityCheck.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_Setup.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_Setup.cpp

Purpose: Tests CLI setup behavior for ordinary startup, log/config options, automatic basedir/mountpoint creation, FUSE options, and commas in basedir paths.

Important APIs and types: Uses `testutils/CliTest.h` and CLI fixture helpers for running CryFS with temporary directories.

Control flow: Tests run the CLI with different option combinations, inspect success/failure, and verify created directories or accepted paths/options. Failure cases cover autocreate permissions or impossible targets.

State and persistence behavior: Creates and mutates temporary basedirs, mountpoints, config/log paths, and possibly FUSE mount state through the fixture.

Dependencies and integration points: Covers the end-to-end CLI setup path from parsed options to filesystem/mount preparation.

Risks: Mount/FUSE availability and filesystem permissions can be environment-sensitive. Path parsing with commas is a regression-prone FUSE option boundary.

Test signals: Expected run success/error, created directories/files, accepted config/logfile options, passed FUSE options, and comma-containing basedir support.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_Setup.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_ShowingHelp.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_ShowingHelp.cpp

Purpose: Tests CLI help/usage display and exit behavior for long/short help options, help mixed with other options, and missing required directory arguments.

Important APIs and types: Uses `CliTest` fixture and CLI run helpers.

Control flow: Each test invokes the CLI with a specific argument set and asserts success or invalid-argument behavior plus usage output as appropriate.

State and persistence behavior: No significant filesystem state beyond fixture setup; tests focus on argument handling and output.

Dependencies and integration points: Complements parser tests by validating user-facing CLI behavior through the higher-level runner.

Risks: Help output formatting changes can break strict output checks. Mixed help/options behavior is a compatibility contract.

Test signals: Correct exit/error code and usage/help output for `--help`, `-h`, help with other args, missing all options, and missing mount dir.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_ShowingHelp.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_WrongEnvironment.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_WrongEnvironment.cpp

Purpose: Tests CLI behavior in invalid filesystem environments, especially permission combinations and environment variables. It defines table-driven helpers for success/error expectations.

Important APIs and types: Uses `CliTest`, `cpp-utils/system/env.h`, local `TestConfig`, permission helpers `SetAllPermissions`, `SetNoReadPermission`, `SetNoWritePermission`, `SetNoExePermission`, `SetNoPermission`, and helper tests `Test_Run_Success`/`Test_Run_Error`.

Control flow: The suite constructs configurations for basedir/mountdir/log/config paths, changes permissions, sets environment values when needed, runs the CLI, and asserts success or error.

State and persistence behavior: Mutates real temp directory permissions and process environment. Cleanup/restoration is critical for isolation.

Dependencies and integration points: Exercises OS permission handling, CLI validation, and environment-dependent setup.

Risks: Permission tests are platform- and user-sensitive, especially if run as root or on Windows. Global environment changes can leak.

Test signals: Expected CLI success/error for each permission/config matrix and correct restoration after tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CliTest_WrongEnvironment.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CryfsUnmountTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CryfsUnmountTest.cpp

Purpose: Tests the CryFS unmount CLI path by mounting a test filesystem and then unmounting it successfully.

Important APIs and types: Uses `CliTest`, `cryfs-cli/Cli.h`, `cryfs-unmount/Cli.h`, and helper `unmount`.

Control flow: The test creates/mounts a filesystem through the fixture, invokes the unmount CLI on the mount point, and asserts success.

State and persistence behavior: Uses real temporary mount/basedir state managed by the CLI fixture. The important persistent effect is the mount being removed.

Dependencies and integration points: Integrates main CryFS CLI mount behavior with the separate `cryfs-unmount` command.

Risks: Requires working mount/unmount support in the test environment. Cleanup failure can affect later tests.

Test signals: Mounted filesystem unmounts with success code and fixture teardown observes no lingering mount.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/CryfsUnmountTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ParserTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ParserTest.cpp

Purpose: Tests command-line parsing for CryFS CLI options. It covers missing arguments, help, cipher listing, absolute/relative basedir and mountdir, foreground mode, filesystem upgrade, auto-create flags, logfile/config paths, cipher validation, idle unmount, blocksize, integrity options, and direct/indirect FUSE options.

Important APIs and types: Uses `Parser`, `ProgramOptions`, `ProgramOptionsTestBase`, `CryCiphers::supportedCipherNames`, `CryfsException`, `ErrorCode`, `CaptureStderrRAII`, Boost optional/filesystem, and gitversion support.

Control flow: `parse` builds an argv vector and calls `Parser(...).parse(...)`. Tests assert returned `ProgramOptions` fields or catch `CryfsException` and validate error code/output. FUSE option tests verify ordering before and after `--`.

State and persistence behavior: Parser state is in-memory. Relative paths depend on `boost::filesystem::current_path`. Captured stderr is process-local.

Dependencies and integration points: This is the contract between user CLI syntax and executable setup behavior.

Risks: Ordering of FUSE options, relative path normalization, and help/error output are compatibility-sensitive. Float idle values and boolean integrity parsing need precise conversion.

Test signals: Exact option fields, optional none/value states, invalid cipher error text, usage/cipher output, and FUSE option vector ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ParserTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ProgramOptionsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ProgramOptionsTest.cpp

Purpose: Tests the `ProgramOptions` value object directly. It verifies constructor/storage accessors for base/mount dirs, optional config/log/cipher/blocksize/idle settings, foreground and create flags, filesystem upgrade, integrity violation flags, and FUSE options.

Important APIs and types: Uses `ProgramOptions`, `ProgramOptionsTestBase`, Boost optional/gtest workaround, and GoogleTest.

Control flow: Tests construct `ProgramOptions` through fixture helpers with selected fields set or unset, then assert each getter returns the expected value.

State and persistence behavior: Pure in-memory immutable or value-like option state. No filesystem access beyond path object values.

Dependencies and integration points: Parser tests and CLI setup tests depend on this object faithfully carrying parsed configuration.

Risks: Defaults are important: false vs true and `none` vs explicit value must stay stable. Getter changes can ripple into CLI behavior.

Test signals: Exact path values, optional none/some states, boolean flags, numeric settings, integrity option combinations, and empty/non-empty FUSE option vectors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/ProgramOptionsTest.cpp -->
