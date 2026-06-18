# subset-b-000550 Research

Grouped BeeGFS source research for subset-b-000550. Each section is delimited for reconciliation into the requested source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestSerialization.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestSerialization.cpp

Purpose: This GoogleTest file pins the BeeGFS common serialization framework at the byte-layout level. It tests primitive endian layout, tuple/pair layout, padding, raw strings, backed pointers, raw blocks, object `serialize()` hooks, collection framing, atomic wrappers, base-class serialization, and string collections. It also includes BeeGFS domain types through headers such as `EntryInfo`, `PathInfo`, quota data, striping patterns, storage target info, nodes, xattrs, and fsck inodes, making the suite a compatibility sentinel for wire/storage serialization contracts.

Important APIs and helpers: `memoryEquals()` compares expected byte buffers and prints mismatch context. `testObject()` is the central round-trip harness: it checks sizing-only serialization, exact output bytes, deserialization equality, consumed size, and truncated-buffer failure. `testSimpleSerializer()` specializes that harness for `operator==` types. Modifiers such as `EnumAsMod`, `StringAlign4`, `AtomicMod`, and `serdes::backedPtr`, `serdes::rawString`, `serdes::rawBlock`, `serdes::base`, and `serdes::atomicAs` exercise adapter APIs.

Control flow: Every test constructs fixed expected byte arrays, serializes to a measured buffer, deserializes back, and verifies corrupted or short input marks the context bad. The collection tests cover both size-prefixed and non-size-prefixed modes by specializing `ListSerializationHasLength` and `MapSerializationHasLength`. String collection tests cover list/vector insertion order and set ordering.

State and persistence behavior: The file itself is stateless, but it protects persistent/wire compatibility. Risks are highest around silent format changes, signed/unsigned enum conversions, string terminators, alignment padding, buffer overflow/underflow, and collection length fields. Test signals are strong for exact binary compatibility and malformed-input rejection, but only for the handpicked expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestSerialization.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestSocket.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestSocket.cpp

Purpose: This is a minimal placeholder GoogleTest fixture for socket-related tests. It includes `common/net/sock/Socket.h` and defines `class TestSocket : public ::testing::Test`, but contains no actual test cases.

Important APIs/types/functions: The only local type is `TestSocket`, an empty fixture intended to hold shared setup or helpers for future tests. No `SetUp`, `TearDown`, or assertions are implemented.

Control flow and state: There is no runtime control flow beyond construction of the fixture type by the test binary if a future test uses it. It has no persistent state, no networking side effects, and no dependencies beyond the socket header and GoogleTest.

Dependencies and integration: The file participates in the common test target if included by the build, serving as a compile-time include check for `Socket.h`. It does not validate socket behavior, IPv4/IPv6 handling, connection setup, error paths, or polling semantics.

Risks and test signals: Current test signal is very weak. A breaking change that prevents `Socket.h` from compiling in this context would be caught, but behavioral socket regressions would not. If this file is kept, it should either be populated with focused tests or removed from manifests to avoid implying coverage that does not exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestSocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestStorageTk.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestStorageTk.cpp

Purpose: This test verifies `StorageTk::findLongestMountedPrefix()`, especially parsing of `/proc/mounts`-style escaped path components and selection of the longest valid mount prefix.

Important APIs/types/functions: The file defines `FULL_SET` as the escaped form used in mounts files and `FULL_SET_RAW` as the raw path component. The test feeds a synthetic mounts stream into `StorageTk::findLongestMountedPrefix()` and compares returned `Mount{device, mountpoint, fstype}` values.

Control flow: The test first checks rejection of empty paths, relative paths, and failed streams. It then uses a multi-line mounts fixture containing `/`, `/test/foo/bar`, `/test/fo`, an escaped all-byte component, and `/test/foo`. It verifies fallback to root for a nonmatching sibling, exact longest match for nested paths, exact match for `/test/foo`, and escaped mount decoding for raw special characters both at the mountpoint and beneath it.

State and persistence behavior: No disk is touched; all persistence-like behavior is simulated through `std::stringstream`. The test protects code that reads real mount tables and affects metadata storage compatibility decisions elsewhere.

Risks and test signals: The key risk is path-prefix false positives, for example treating `/test/fo` as a prefix of `/test/foo`, or mishandling octal escapes. Coverage is good for matching and decoding but does not cover malformed mount lines, whitespace in device names, or duplicate mount ordering beyond this fixture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestStorageTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestStringTk.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestStringTk.cpp

Purpose: This tiny test verifies `StringTk::implode()` for integer containers.

Important APIs/types/functions: It includes `StringTk.h` and uses `std::vector<int>` inputs with a comma separator. The tested API converts iterable values into a delimiter-joined string.

Control flow: The single test case checks three cases: an empty vector produces an empty string, a one-element vector produces the element without delimiters, and a three-element vector produces `1,2,3`.

State and persistence behavior: The test is pure and has no persistent state. It exercises formatting behavior only.

Dependencies and integration: `StringTk::implode()` is commonly used for logging and config/debug output throughout BeeGFS. This test catches basic delimiter placement regressions that would make output noisy or ambiguous.

Risks and test signals: Signal is narrow. It does not cover non-vector containers, strings with delimiters, custom types, escaping, or localization. It is still useful as a simple guard against off-by-one delimiter bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestStringTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestStripePattern.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestStripePattern.cpp

Purpose: This parameterized test validates basic `Raid0Pattern` chunk mapping semantics for different chunk sizes.

Important APIs/types/functions: `Raid0PatternTest` derives from `testing::TestWithParam<unsigned>`. The test instantiates chunk sizes of `64*1024` and `1024*1024*1024`, then constructs `Raid0Pattern` with target sequence `{0,1,2,3}`.

Control flow: For ten full rotations across the target list, it computes each chunk's start and end offset. It asserts that `getStripeTargetIndex()` returns `i % targetPattern.size()` at both boundaries and that `getChunkStart()` returns the chunk's starting offset for both start and last-byte positions.

State and persistence behavior: No state is persisted. The test protects striping math used to map logical file offsets to storage targets and chunk starts.

Dependencies and integration: `Raid0Pattern` is used by metadata creation paths and serialized striping pattern state. Correct chunk math is critical for read/write routing and file layout consistency.

Risks and test signals: It covers boundary positions and very large chunk sizes but not negative offsets, overflow near `int64_t` limits, empty target vectors, default target counts, serialization, or other striping subclasses. It is a focused arithmetic regression test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestStripePattern.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestTargetCapacityPools.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestTargetCapacityPools.cpp

Purpose: This regression test exercises `TargetCapacityPools::chooseTargetsInterdomain()` after a target changes capacity pool membership, specifically with empty chooser groups.

Important APIs/types/functions: It constructs `TargetCapacityPools pools(false, ...)`, calls `addOrUpdate()` twice for target `1` on node `1`, first as `CapacityPool_NORMAL` and then as `CapacityPool_LOW`, and then asks for four interdomain targets.

Control flow: Moving the target from NORMAL to LOW must remove the stale NORMAL group from the chooser. The test then expects only one chosen target and verifies it is target `1`.

State and persistence behavior: The test mutates in-memory pool membership and chooser structures only. It protects transient allocator state that is populated from management capacity-pool syncs.

Dependencies and integration: Capacity pools influence placement decisions. The interdomain chooser depends on accurate pool-to-domain membership and must not retain empty groups that distort selection.

Risks and test signals: The test catches a specific stale-group bug. It does not cover multiple domains, buddy groups, pool thresholds, concurrent updates, or weighted/randomized choice distribution. Because the expected vector size is one after asking for four targets, it also documents graceful partial fulfillment when insufficient targets exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestTargetCapacityPools.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestTimerQueue.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestTimerQueue.cpp

Purpose: This file tests asynchronous `TimerQueue` scheduling, cancellation, and worker concurrency.

Important APIs/types/functions: `TestTimerQueue` owns a `std::unique_ptr<TimerQueue>` and starts `TimerQueue(0, 20)` in `SetUp()`. `EnqueueCancelFn` increments an `AtomicSizeT`; `EnqueueManyLongFn` sleeps for one second and increments a shared atomic counter.

Control flow: `enqueueCancel` schedules a callback after 100 ms, cancels its handle, sleeps one second, and verifies no callback ran. `enqueueManyLong` enqueues 42 callbacks after 10 ms, each sleeping one second, then waits until all complete and asserts elapsed time is under 20 seconds. With one-at-a-time execution, the test would take roughly 42 seconds, so the assertion proves parallel worker execution.

State and persistence behavior: State is in-memory atomic counters and queued callbacks. No persistence is involved.

Dependencies and integration: `TimerQueue` is used by metadata service scheduling, including client sync requeueing and disposal garbage collection in this subset. Cancellation correctness matters for shutdown and race-free delayed work.

Risks and test signals: The tests are timing-sensitive and use `sleep(1)`, so heavily loaded systems may produce noise. They provide useful behavioral signal for cancellation and parallelism but not for shutdown drain, exception handling inside callbacks, or ordering of equal deadlines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestTimerQueue.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestUiTk.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestUiTk.cpp

Purpose: This test verifies yes/no prompt parsing in `uitk::userYNQuestion()`.

Important APIs/types/functions: `testQuestion()` wraps a `std::stringstream` around an answer string and passes it, plus an optional default answer, to `uitk::userYNQuestion("Test", defaultAnswer, input)`.

Control flow: The test asserts affirmative parsing for `Y`, `y`, and `Yes`; negative parsing for `N`, `n`, and `No`; default behavior for empty input with true and false defaults; and explicit answers overriding defaults.

State and persistence behavior: No persistent state exists. Input is supplied through an in-memory stream, making the test deterministic and independent of terminal state.

Dependencies and integration: This helper is relevant to setup or administrative tools that ask interactive confirmation questions. Correct defaults are important because empty input can imply destructive or enabling actions.

Risks and test signals: The test covers common English responses but not whitespace, invalid retries, EOF handling, localized strings, multi-character mixed-case variants beyond `Yes`/`No`, or prompt output formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestUiTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestUint128.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestUint128.cpp

Purpose: This suite validates BeeGFS `uint128_t` helpers for construction, formatting, byte-order conversion, hashing, ordering, and streaming.

Important APIs/types/functions: It uses `uint128::make`, `upper64`, `lower64`, `toHexStr`, `uint128::Hash`, `HOST_TO_LE_128`, `HOST_TO_BE_128`, `LE_TO_HOST_128`, and `operator<<`. The fixture table covers zero, all-ones, high-only, low-only, and a mixed-value case with expected normal and reversed byte order strings.

Control flow: Tests loop over the fixture table to verify high/low extraction, hex formatting, endian conversions conditional on host byte order, insertion/lookup in `std::unordered_map` and `std::map`, and stream concatenation output.

State and persistence behavior: All state is local in maps and values. The behavior matters for serialized IDs, checksums, and map keys that may persist or cross process boundaries.

Dependencies and integration: It includes `StringTk` and serialization byteswap helpers. Correct 128-bit hashing and ordering are necessary when these values are used as keys in containers.

Risks and test signals: Coverage is solid for powers of two and representative constants. It does not cover parsing from strings, arithmetic beyond repeated doubling, overflow behavior, or ABI representation on compilers without native 128-bit support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestUint128.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestUnitTk.cpp -->
# sources/distributed-fs/beegfs/common/tests/TestUnitTk.cpp

Purpose: This test locks down binary unit conversion behavior in `UnitTk`.

Important APIs/types/functions: It covers `gibibyteToByte`, `mebibyteToByte`, `kibibyteToByte`, `byteToXbyte`, and `xbyteToByte`. Expected values use powers of two: KiB = 1024, MiB = 1048576, GiB = 1073741824.

Control flow: The first three tests convert representative doubles, including fractional `10.598`, to integer bytes and compare exact truncation/rounding results. `byteToXbyte` checks automatic unit choice and the optional display rounding flag. `xbyteToByte` validates reverse conversion for KiB, MiB, and GiB.

State and persistence behavior: No persistence is involved. The output affects config parsing and human-readable capacity display, which can influence operational decisions.

Dependencies and integration: `UnitTk::strHumanToInt64()` is used by metadata config parsing for buffer sizes, chunk sizes, and persistent file-event queue size. These tests indirectly protect that convention by pinning lower-level conversion math.

Risks and test signals: Signal is good for binary units and representative fractions. It does not cover invalid unit strings, decimal SI units, negative values, overflow, very small fractions, or full human-string parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/tests/TestUnitTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/CMakeLists.txt -->
# sources/distributed-fs/beegfs/meta/CMakeLists.txt

Purpose: This CMake file defines the BeeGFS metadata server build. It creates the static `meta` library from metadata-specific application, network message, storage, session, component, resync, chunk-balancer, and fsck support sources; links it to `beegfs-common`, `dl`, `pthread`, and `blkid`; creates the `beegfs-meta` executable; and optionally builds `test-meta`.

Important build targets: `meta` is the central library. `beegfs-meta` links `source/program/Main.cpp` plus `meta`. `test-meta` is enabled unless `BEEGFS_SKIP_TESTS` is set and links `meta` with `gtest_main`. Installation rules place the daemon under `usr/sbin`, setup scripts under `usr/sbin`, systemd units under `${CMAKE_INSTALL_LIBDIR}/systemd/system`, default config under `etc/beegfs`, and the shell wrapper under `opt/beegfs/sbin`.

Control flow and integration: The file enumerates source paths explicitly, so adding/removing metadata code requires updating this list. It includes `source/`, making project-local includes like `<app/App.h>` available. The test target copies `build/dist/etc/beegfs-meta.conf` into `dist/etc/` before running `test-meta --compiler`.

State and persistence behavior: Build-time only, but it controls packaging of persistent config and service units. Missing files here can silently exclude code from the daemon or tests.

Risks and test signals: The explicit source list is easy to drift. There are duplicate/near-duplicate entries for some storage message files with inconsistent indentation, which is mostly cosmetic but can hide maintenance errors. The build tests cover config/serialization/buddy mirroring but not the full runtime daemon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/App.cpp -->
# sources/distributed-fs/beegfs/meta/source/app/App.cpp

Purpose: `App.cpp` implements the BeeGFS metadata daemon lifecycle. It owns startup, configuration, storage initialization, node registration, management-state download, component creation, shutdown, session persistence, and signal handling.

Important APIs/functions: `run()` constructs `Config` and maps exceptions to app result codes. `runNormal()` sequences the daemon: optional NUMA bind, `preinitStorage()`, logging, UUID check, local node ID loading, data object creation, network setup, metadata layout creation, root/disposal dir loading or creation, signal registration, daemonization, RDMA discovery, mgmtd wait/preregistration, local node setup, management info download, optional `FileEventLogger`, session restore, component startup/join, session store, and final client sync. Initialization helpers create node stores, target mappers, state stores, capacity pools, queues, `MetaStore`, hashed metadata directories, and listeners/workers/syncers. Shutdown helpers stop and join components in dependency order.

Control flow: Startup is deliberately staged so disk locks happen before logging, RDMA device opening happens after daemon fork, mgmtd registration precedes state downloads, and worker shutdown follows modification-event and resync shutdown. `stopComponents()` avoids blocking because it may run from a signal handler.

State and persistence behavior: Persistent state includes the metadata directory, storage format file, node number ID file, registration token, root/disposal inodes, session backup files, optional event queue, and filesystem UUID check. It writes session files on clean shutdown and removes restored session files after startup.

Dependencies/integration: The app integrates common networking, `NetMessageFactory`, `MetaStore`, `SessionStore`, `InternodeSyncer`, `DatagramListener`, stream listeners, workers, `BuddyResyncer`, `ChunkBalancerJob`, timers, and file-event logging. Risks include startup ordering regressions, double deletion (`timerQueue` is deleted through `SAFE_DELETE` and later raw `delete timerQueue` in the destructor), partial shutdown from signal context, stale session-file handling, and mismatched target UUID or storage format.

Test signals: Direct tests are not in this file. Coverage comes from component tests, config tests, serialization tests, and integration/runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/App.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/App.h -->
# sources/distributed-fs/beegfs/meta/source/app/App.h

Purpose: `App.h` declares the metadata daemon's central application object and exposes accessors used by nearly every metadata component.

Important APIs/types: `App` derives from `AbstractApp` and overrides `run()`, `stopComponents()`, component exception handling, network-interface failure handling, and `getStreamListenerByFD()`. It defines result codes, worker/listener container typedefs, and a large object graph: config/logging, local node, node stores, root info, capacity pools, target and buddy mappers, state stores, storage pools, work queues, message factory, metadata store, root/disposal dirs, sessions, acknowledgments, stats, metadata path objects, datagram/stream listeners, syncers, timers, workers, buddy resyncer, chunk balancer, quota stores, and file-event logger.

Control flow contract: Private methods are grouped by lifecycle phase: init logging/data/network/storage/components, start/stop/join/delete workers and listeners, mgmtd registration/download, daemonization, signal handling, and session restore/store/delete. Public getters make these shared objects globally available through `Program::getApp()`.

State and persistence behavior: The header documents ownership of persistent metadata paths (`inodes`, `dentries`, buddy-mirror variants), root/disposal inodes, session stores, and file-event logger state. Most members are raw pointers with destructor-managed ownership; `storagePoolStore` and `fileEventLogger` are `unique_ptr`s.

Dependencies/integration: Because many components reach into `App`, this header is a high-coupling integration point. It mediates access to network filters, node stores, target states, queues, and timers.

Risks and test signals: Raw-pointer ownership and broad public access increase lifetime and ordering risk. `getStreamListenerByFD()` assumes `numStreamListeners > 0` and a populated vector. Tests need integration coverage because many invariants are cross-member rather than local.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/App.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/config/Config.cpp -->
# sources/distributed-fs/beegfs/meta/source/app/config/Config.cpp

Purpose: `Config.cpp` implements metadata-server-specific configuration defaults, parsing, implicit value derivation, and validation.

Important APIs/functions: The constructor initializes `sysTargetAttachmentMap` and calls `initConfig()`. `loadDefaults()` overlays metadata defaults such as `storeMetaDirectory`, xattr/ACL flags, worker/listener counts, chunk defaults, NUMA options, lock retry tuning, target chooser, quota options, file-event logging settings, daemonization, and PID file. `applyConfigMap()` parses string values into typed fields, validates `logType`, enforces `sysTargetOfflineTimeoutSecs >= 30`, preserves compatibility for `tuneDefaultNumStripeNodes`, and throws on unknown keys when requested. `initImplicitVals()` derives worker/comm-slave counts, chooser enum, interface list, socket buffers, auth hash, and target-attachment map.

Control flow: Parsing iterates the inherited config map, handles known keys, erases consumed entries, and optionally reports unknown entries. The target attachment map is loaded from a file into a string map and converted to `TargetMap`. `initTuneTargetChooserNum()` maps string names to enum values and rejects unsupported values, including `randomintranode`.

State and persistence behavior: The object stores runtime config only. It reads optional files: config file, interface list, auth file through the base class, and `sysTargetAttachmentFile`. `createDefaultCfgFilename()` uses `/etc/beegfs/beegfs-meta.conf` if present.

Dependencies/integration: `App` consumes almost every getter. `UnitTk` parses human sizes; `StringTk` parses booleans/integers; `MapTk` and `StorageTk` load attachment files. Risks include silent truncation because several byte-size fields are stored as `unsigned` after `int64_t` parsing, invalid target chooser names preventing startup, and ACL requiring xattrs checked later in `App`.

Test signals: Metadata config tests in the build target likely cover parts of this, but this subset does not include them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/config/Config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/config/Config.h -->
# sources/distributed-fs/beegfs/meta/source/app/config/Config.h

Purpose: `Config.h` declares metadata daemon configuration fields and typed getters.

Important APIs/types: `TargetChooserType` enumerates randomized, round-robin, random-robin, random-inter-node, and random-intra-node chooser modes, though the implementation disallows random-intra-node. `Config` derives from `AbstractConfig` and overrides `loadDefaults()`, `applyConfigMap()`, and `initImplicitVals()`. It exposes getters for network interface filters, metadata storage paths and UUID, xattr/ACL behavior, worker/listener/buffer tuning, default striping, NUMA, lock retry policy, mirror behavior, disposal GC period, chunk balancing, quota, offline timeout, user set pattern, daemonization, PID file, xattr-list limiting, and file-event logging target/persistence.

Control flow contract: Private helpers derive the target attachment map and target chooser enum. Public setters are intentionally limited: quota enforcement and xattr-list limit can be changed after parsing.

State and persistence behavior: Persistent inputs referenced by the config include metadata directory, filesystem UUID, target attachment file, auth/interface files from the base class, PID file, and file-event persistence directory. The owned `TargetMap* sysTargetAttachmentMap` is deleted by the destructor.

Dependencies/integration: `App`, `InternodeSyncer`, file-event logging, disposal GC, worker creation, and storage initialization all depend on these accessors. The header acts as the stable contract for metadata service tuning.

Risks and test signals: Many related settings are independent booleans or unsigned integers, so cross-field validation is split between `Config.cpp` and `App.cpp`. The raw `TargetMap*` requires careful ownership. Human-size values exposed as unsigned or uint64 can mask negative/overflow errors if not validated at parse time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/app/config/Config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DatagramListener.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/DatagramListener.cpp

Purpose: This file implements the metadata server UDP/datagram listener's message dispatch policy.

Important APIs/functions: The constructor forwards listener name, network filter, local NIC list, acknowledgment store, UDP port, and outbound-interface restriction to `AbstractDatagramListener`. `handleIncomingMsg()` resolves a sender socket, builds a `NetMessage::ResponseContext`, and dispatches only message types valid for metadata datagram handling.

Control flow: Incoming messages are rejected if no sender socket exists. Valid message types include Ack, Dummy, heartbeat request/response, target mapping, capacity publish/refresh, node removal, storage pool refresh, target state refresh, and mirror buddy group updates. For valid types, `processIncoming()` is called and failures are logged. All other message types are logged as invalid in this context.

State and persistence behavior: The listener maintains inherited socket/send-buffer state and uses `AcknowledgmentStore` for UDP acknowledgments. It does not persist data directly; processed messages can mutate node stores, mappings, capacity pools, or target states through their handlers.

Dependencies/integration: It depends on `AbstractDatagramListener`, `NetMessage` dispatch, IP address handling, and message type definitions. `App` creates it before `InternodeSyncer` and `ModificationEventFlusher`; the flusher uses it to send fsck modification-event messages.

Risks and test signals: The allowlist is a security and correctness boundary. New UDP control messages must be added intentionally, otherwise they will be rejected. There is no local unit test in this subset for dispatch allowlisting or missing socket behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DatagramListener.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DatagramListener.h -->
# sources/distributed-fs/beegfs/meta/source/components/DatagramListener.h

Purpose: The header declares the metadata-specific `DatagramListener`, a thin subclass of `AbstractDatagramListener`.

Important APIs/types: The constructor accepts `NetFilter*`, `NicAddressList&`, `AcknowledgmentStore*`, UDP port, and `restrictOutboundInterfaces`. The protected override `handleIncomingMsg(struct sockaddr*, NetMessage*)` provides metadata-server dispatch filtering.

Control flow and state: Most runtime behavior and state live in the abstract base class. This subclass exists to name the component and restrict/dispatch incoming message types according to metadata server context.

Dependencies/integration: `App` owns a `DatagramListener*`, exposes it via `getDatagramListener()`, updates its NIC list on interface changes, and stops it during shutdown with `sendDummyToSelfUDP()` to wake the receive loop. `InternodeSyncer` and `ModificationEventFlusher` use the datagram listener for UDP-with-ack communication.

Risks and test signals: The narrow header makes ownership and lifetime the main risk: consumers store raw pointers, so the listener must outlive users like the modification flusher. Behavioral coverage depends on tests for the `.cpp` dispatch and base listener.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DatagramListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.cpp

Purpose: This component function performs periodic cleanup of disposal-directory entries owned by the local metadata node.

Important APIs/functions: `disposalGarbageCollector()` is the scheduled entry point. It obtains `App` through `Program::getApp()`, builds a node vector containing the local metadata node, constructs `DisposalCleaner` with the metadata buddy-group mapper, and calls `dc.run()` with callbacks. `deleteFile()` wraps `DisposalCleaner::unlinkFile()` and logs communication, in-use, and other errors while counting successful unlinks. `handleError()` logs run-level failures.

Control flow: A run logs start, unlinks eligible entries through the cleaner, logs finish with the unlinked count, and re-enqueues itself on `app->getGcQueue()` after `tuneDisposalGCPeriod` seconds if the period remains nonzero and the queue still exists. The cleaner receives a termination predicate tied to `gcQueue->getSelfTerminate()`.

State and persistence behavior: This code deletes metadata/storage-disposal entries through normal BeeGFS cleanup mechanisms. It does not store its own state; scheduling state is held by `TimerQueue`.

Dependencies/integration: `App::startComponents()` enqueues this function when disposal GC is configured. Shutdown deletes `gcQueue`, so the null check before requeue matters.

Risks and test signals: `deleteFile()` currently returns `FhgfsOpsErr_SUCCESS` even when `unlinkFile()` failed, relying on logging rather than propagating per-file failure. The run references the local node handle and app queues, so shutdown races are a concern. No direct tests cover requeueing or error propagation here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.h -->
# sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.h

Purpose: This header exposes the disposal garbage collector scheduling entry point.

Important APIs/types: It declares a single function, `void disposalGarbageCollector();`.

Control flow and state: The header intentionally carries no state or class. The implementation function is scheduled on `App`'s `gcQueue` and requeues itself based on configuration.

Dependencies/integration: Consumers only need this header to schedule the GC function, as `App.cpp` does when `tuneDisposalGCPeriod` is nonzero. The implementation depends on `Program::getApp()`, `DisposalCleaner`, and metadata node stores.

Risks and test signals: The minimal API leaves lifecycle management implicit. Callers must ensure the global `App` and `gcQueue` are valid for the duration of the callback. No header-level tests are meaningful; behavioral tests should target the `.cpp` cleanup and requeue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/DisposalGarbageCollector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.cpp

Purpose: This file implements persistent metadata file-event logging and a Unix-socket streaming protocol for downstream listeners.

Important APIs/types/functions: Public entry points are `createFileEventLogger()`, `destroyFileEventLogger()`, `logEvent()`, and `makeEventContext()`. Internally it defines `Timer`, `UnixAddr`, `SocketState`, packet types and close reasons, `PacketBuffer`, ring-style `PacketQueue`, `PacketWriter`/`PacketReader`, `MessageStream`, `Subscriber`, `EventLoggerShared`, `EventLoggerWorker`, `EventQ_Worker_Thread`, and serialized `FileEventLogItem`.

Control flow: Logger creation initializes a PMQ under `sysFileEventPersistDirectory` or `<storeMetaDirectory>/eventq`, starts an `EventQ-Worker`, and configures a Unix `SOCK_SEQPACKET` target. Producers call `logEvent()`, serialize a versioned event item, enqueue into PMQ, request periodic flush, and wake the reader. The worker waits for shutdown, flush deadlines, PMQ messages, and socket reconnect deadlines. It performs handshake response, processes subscriber requests for newest MSN, message range, stream start, and close, streams PMQ messages with MSNs, and resets the subscriber after termination.

State and persistence behavior: PMQ stores events durably up to configured size. `pmq_sync()` is performed by the worker or by producers when enqueue needs space. Event items include format version 2, flags, link count, event type/path fields, user ID, and nanosecond timestamp. Socket state reconnects indefinitely and logs repeated failures sparingly.

Dependencies/integration: `App` creates the logger when `sysFileEventLogTarget` is set and passes node/buddy IDs. Metadata operation handlers call `logEvent()`. Serialization tests indirectly protect the event item format.

Risks and test signals: Risks include blocking Unix `connect()`, one-subscriber limitation, packet-size truncation/`uint16_t` message size, PMQ corruption/out-of-bounds handling, producer stalls when PMQ is full, and protocol-version compatibility. No local tests in this subset exercise the protocol, PMQ persistence, reconnects, or shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.h -->
# sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.h

Purpose: This header defines the public file-event logging API used by metadata operations and `App`.

Important APIs/types: `EventContext` carries entry ID, parent ID, user ID, target parent ID, link count, timestamp, and bit flags for mirrored and secondary events. `makeEventContext()` constructs that context from `EntryInfo` and operation details. `FileEventLoggerIds` identifies the metadata node and buddy group to subscribers. `FileEventLoggerParams` configures the target address and IDs. `FileEventLogger` is opaque; callers use `createFileEventLogger()`, `destroyFileEventLogger()`, and `logEvent()`.

Control flow contract: Callers create one logger when configured, pass file events with context to `logEvent()`, and destroy the logger on shutdown. Opaqueness keeps PMQ/socket/thread internals out of operation code.

State and persistence behavior: The header exposes enough context for persistent event records. The timestamp is stored in the context rather than generated only at serialization time, preserving operation timing semantics.

Dependencies/integration: It includes `FileEvent` and `EntryInfo`. `App` owns the logger in a `unique_ptr` with `destroyFileEventLogger` deleter and exposes `getFileEventLogger()`.

Risks and test signals: The API accepts a raw `FileEventLogger*`; callers must handle a null logger when logging is disabled. Context correctness depends on operation code supplying parent/target/link details. Direct tests should validate flag construction and serialized event compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/FileEventLogger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.cpp

Purpose: `InternodeSyncer.cpp` implements the metadata daemon's periodic cluster synchronization loop and related static startup helpers.

Important APIs/functions: The constructor initializes force flags, offline-wait logic, local consistency state, and resync flag. `syncLoop()` periodically checks network interfaces, re-registers the local node, downloads nodes/mappings/storage pools/states, updates capacity pools, sweeps metadata cache, drops idle connections, resets ID counters, publishes target state changes, and publishes capacity. Static helpers perform startup registration, node/client sync, target mapping sync, storage pool sync, target state and buddy group sync, capacity-pool download/update, quota-exceeded list download, and client-session cleanup.

Control flow: `syncLoop()` runs every three seconds and gates work by elapsed timers or atomic force flags. State publishing uses management-node compare/change semantics with retries to avoid overwriting concurrent mgmtd updates. Client sync removes sessions for clients no longer registered and, when remote communication is allowed, unlocks waiters, closes storage chunk files, closes metadata state, and unlinks disposable files.

State and persistence behavior: It mutates node stores, target mappings, buddy groups, state stores, capacity pools, storage pools, quota stores, sessions, locks, connection pools, metadata cache flush state, and local consistency state. It reads capacity from the metadata path and uses override files through `StorageTk`.

Dependencies/integration: It is tightly coupled to `App`, `NodesTk`, `MessagingTk`, `BuddyCommTk`, `SessionStore`, `MetaStore`, and management-node message types. `App::downloadMgmtInfo()` calls several static helpers before constructing the running syncer.

Risks and test signals: Risks include mgmtd unavailability causing POFFLINE marking, racey state transitions around buddy resync/offline waits, expensive client cleanup, and sync functions returning true even after partial download failures in some paths. There are no direct unit tests here; operational integration tests are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.h -->
# sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.h

Purpose: This header declares the metadata service's internode synchronization thread and static synchronization helpers.

Important APIs/types: `InternodeSyncer` derives from `PThread`. Public static APIs include `registerNode()`, `updateMetaStatesAndBuddyGroups()`, `syncClients()`, `downloadAndSyncNodes()`, `downloadAndSyncTargetMappings()`, `downloadAndSyncStoragePools()`, `downloadAndSyncTargetStatesAndBuddyGroups()`, `downloadAndSyncClients()`, capacity-pool updates, exceeded-quota downloads, and sync-result logging. Instance methods expose force flags for pools, target states, capacity publishing, storage pools, and network checks; local consistency state accessors; and resync-in-progress flags.

Control flow contract: `run()` delegates to `syncLoop()`. Atomic force flags allow other components and message handlers to request refresh work without blocking. `nodeConsistencyStateMutex` protects consistency state transitions, while `buddyResyncInProgress` uses an atomic wrapper.

State and persistence behavior: The class owns no persistent files directly but orchestrates updates to persistent-adjacent runtime state: quota stores, state stores, node stores, session cleanup, cache sweeping, and capacity publication based on storage stats.

Dependencies/integration: It includes node stores, capacity pool messages, quota data, `NodeOfflineWait`, and threading primitives. `App` owns one syncer and exposes it for force-update calls.

Risks and test signals: The broad static API makes it callable during both startup and steady state, including before an instance exists. Callers must account for that split. Tests should focus on state transition decisions, forced refresh handling, and session cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/InternodeSyncer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.cpp -->
# sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.cpp

Purpose: This file implements asynchronous fsck modification-event delivery over UDP with acknowledgments.

Important APIs/functions: The constructor initializes the thread, log context, datagram listener, worker list, dummy fsck node, local NIC capabilities, and missed-event flag. `run()` waits for buffered events and calls `sendToFsck()`. `add()` applies backpressure when the event list reaches `MODFLUSHER_MAXSIZE_EVENTLIST`, appends event type and entry ID, and wakes the flusher. `sendToFsck()` splices up to `MODFLUSHER_SEND_AT_ONCE` events into local lists, sends `FsckModificationEventMsg` with the missed-event flag, and disables logging locally if fsck does not acknowledge.

Control flow: The thread sleeps on `eventsAddedCond` with a two-second timeout while empty. Producers wait on `eventsFlushedCond` if the queue is full. Sending uses small UDP batches and waits up to `MODFLUSHER_WAIT_FOR_ACK_MS` with configured retries. Failed delivery sets `fsckMissedEvent` and stops further logging until re-enabled.

State and persistence behavior: State is in-memory only: event type list, entry ID list, logging flag, fsck node address, and missed-event marker. It does not persist missed events, so fsck must treat missed-event notification as a consistency signal.

Dependencies/integration: `App` creates and starts the flusher. Worker stalling in the header is used to synchronize logging-enable/disable visibility across workers.

Risks and test signals: Risks include producer blocking if fsck is unreachable, event loss on failed ACK, deadlocks if worker stalling is called from the wrong context, and UDP size constraints. No direct tests cover these concurrency paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.h -->
# sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.h

Purpose: This header declares the fsck modification-event flusher thread and its worker-synchronization controls.

Important APIs/types: `ModificationEventFlusher` derives from `PThread`. Public APIs are the constructor, `run()`, `add()`, `enableLogging()`, `disableLogging()`, `isLoggingEnabled()`, and `getFsckMissedEvent()`. Constants define max queue size, per-send batch size, flush interval, ACK wait, and ACK retries.

Control flow contract: `enableLogging()` clears buffers, sets fsck node address, marks logging enabled, and stalls all workers so they observe the state change. `disableLogging()` clears the logging flag and can flush/clear the queue while waiting for workers. `stallAllWorkers()` enqueues counter work on each worker's personal queue, with special handling when called from a worker thread to avoid self-deadlock.

State and persistence behavior: It owns the buffered event lists, mutexes/conditions for producer/flusher coordination, an atomic logging flag, fsck node handle, and missed-event flag. No durable queue exists.

Dependencies/integration: It reaches into `App` for worker list and work queue, uses `DatagramListener` for UDP ACK sends, and depends on BeeGFS worker work items such as `IncSyncedCounterWork`.

Risks and test signals: Worker-stalling is subtle and can deadlock if worker counts or thread identity are wrong. Queue clearing during disable avoids blocked producers but drops pending events, relying on `fsckMissedEvent`. Tests should cover enable/disable from worker and non-worker contexts, backpressure, and failed fsck acknowledgments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/components/ModificationEventFlusher.h -->
