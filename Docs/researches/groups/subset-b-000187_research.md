# subset-b-000187 research

Grouped research for the subset-b-000187 source set. Each section preserves the original source path and is split-compatible with the per-file research layout.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.pb.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.pb.go

Purpose: generated gogo/protobuf Go implementation for `networkdb.proto`, defining the wire-level gossip payloads used by Docker/libnetwork NetworkDB. It is not handwritten business logic, but it is the compiled serialization contract consumed by the gossip delegate, bulk sync, push/pull, node membership, and table event code.

Important APIs/types/functions: `MessageType` enumerates `NETWORK_EVENT`, `TABLE_EVENT`, `PUSH_PULL`, `BULK_SYNC`, `COMPOUND`, and `NODE_EVENT`; nested enum types model node/network/table event operations; structs include `GossipMessage`, `NodeEvent`, `NetworkEvent`, `NetworkEntry`, `NetworkPushPull`, `TableEvent`, `BulkSyncMessage`, `CompoundMessage`, and `CompoundMessage_SimpleMessage`. The generated methods provide `Reset`, `ProtoMessage`, `Descriptor`, `XXX_Marshal`, `XXX_Unmarshal`, getters, `GoString`, `String`, `Marshal`, `MarshalToSizedBuffer`, `Size`, and `Unmarshal`.

Control flow: callers normally construct typed payloads, marshal them through the generated `Marshal` paths, wrap them in a `GossipMessage`, and decode by message type on receive. `CompoundMessage` carries multiple already-encoded simple payloads to reduce gossip transmission overhead. Unmarshal methods parse protobuf wire fields, skip unknown fields through `skipNetworkdb`, and reject malformed length/varint/EOF cases.

State and persistence behavior: the file owns no durable state; it only serializes transient Lamport-clocked state snapshots and mutations. Persistence semantics are defined by higher-level NetworkDB maps and reaping logic, while this code preserves fields such as `LTime`, `Leaving`, `ResidualReapTime`, `Networks`, and `Payload` across peer communication.

Dependencies and integration points: imports `github.com/gogo/protobuf/proto`, `github.com/gogo/protobuf/sortkeys`, and `github.com/hashicorp/serf/serf` for Lamport time custom types. It is generated from `networkdb.proto`, so edits should happen in the proto and generator flow rather than directly here.

Risks: schema compatibility is the main risk. Field numbers and custom names must remain stable or older daemons may misinterpret cluster state. Generated code also contains hand-unfriendly large marshal/unmarshal loops, so direct modifications are fragile. Unknown fields are skipped, which helps forward compatibility but cannot repair semantic mismatches.

Test signals: direct tests are not in this file, but `networkdb_test.go`, `tableevent_test.go`, and the slow property test exercise these generated message types through real gossip encoding, compound message paths, bulk sync payloads, out-of-order table events, and cluster convergence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.proto -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.proto

Purpose: authoritative protobuf schema for NetworkDB gossip messages. It defines the versioned data model for node membership events, network membership events, table CRUD events, network push/pull sync, bulk sync, and compound message batching.

Important APIs/types/functions: `MessageType` tags envelope payload classes; `GossipMessage` is the envelope with `type` and raw `data`; `NodeEvent`, `NetworkEvent`, and `TableEvent` each carry event `type`, Lamport time, originating node, and domain-specific identifiers; `NetworkEntry` and `NetworkPushPull` represent membership snapshots; `BulkSyncMessage` carries whole-state payloads; `CompoundMessage.SimpleMessage` batches encoded payloads.

Control flow: sender code chooses a `MessageType`, marshals the matching message body, wraps it, and disseminates it through memberlist. Receivers decode the envelope, dispatch by enum, and apply Lamport ordering and ownership rules in NetworkDB. Bulk and push/pull messages provide state reconciliation outside individual event flow.

State and persistence behavior: this schema expresses state-transfer payloads rather than storing state. Lamport times are central to ordering; `leaving` distinguishes active and leaving network attachments; `residual_reap_time` communicates tombstone lifetime for table deletes during sync.

Dependencies and integration points: uses gogo/protobuf options for generated marshaler/unmarshaler/stringer/sizer code and custom Go names such as `NetworkID`. The Lamport fields use `github.com/hashicorp/serf/serf.LamportTime`, binding the schema to NetworkDB's Serf/memberlist clock model.

Risks: protobuf field numbers are compatibility-sensitive. The schema uses byte payloads for envelope and bulk sync data, so type safety depends on correct `MessageType` dispatch. Typos or semantic ambiguity in comments, such as delete text saying "updated", can mislead maintainers even if the wire format is unaffected.

Test signals: the schema is indirectly exercised by all NetworkDB cluster tests and table-event tests via generated code. There are no standalone proto compatibility tests in this subset, so regression safety comes from integration behavior rather than golden wire fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_property_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_property_test.go

Purpose: slow property-based convergence test for NetworkDB. It randomly drives clusters through joins, leaves, creates, updates, deletes, and sleeps, then asserts eventual convergence to the union of expected owned entries across joined networks.

Important APIs/types/functions: `TestNetworkDBAlwaysConverges` runs `rapid.Check`; `testConvergence` builds 2-25 NetworkDB instances and 1-5 networks; `networkDBFSM` implements rapid state-machine actions; action methods include `JoinNetwork`, `LeaveNetwork`, `CreateEntry`, `UpdateEntry`, `DeleteEntry`, and `Sleep`.

Control flow: random actions mutate the model and real NetworkDB instances without stepwise assertions because the system is eventually consistent. After action generation finishes, the test computes expected per-node views, polls `WalkTable` and local network membership until actual state matches, logs mutation history, and records convergence time to `testdata/convergence_time.csv` when possible.

State and persistence behavior: model state is in `state []map[string]map[string]string`, tracking node-owned entries by network. `keysUsed` prevents immediate key reuse after deletion because replicas may not have observed tombstones yet. The test writes optional CSV timing data but treats failures to write statistics as non-fatal.

Dependencies and integration points: uses `pgregory.net/rapid`, `gotest.tools/v3/poll`, `google/go-cmp/cmp`, and helper constructors from `networkdb_test.go`. It depends on real NetworkDB clustering and gossip, not mocks.

Risks: marked `slowtests`, with up to 25 nodes and a 5-minute convergence timeout, so it is expensive and environment-sensitive. Random action traces can be noisy; the mutation log and convergence CSV are important for diagnosing flakes. The model intentionally avoids key reuse, leaving some duplicate-key edge cases to targeted tests.

Test signals: strong signal for eventual consistency across broad operation sequences. It complements deterministic unit/integration tests by exploring interleavings and timing, especially convergence after network membership churn and table mutation races.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_property_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_test.go

Purpose: primary deterministic integration test suite for NetworkDB cluster behavior, node lifecycle, network membership, table CRUD, watches, bulk sync, garbage collection, node state transitions, reincarnation, parallel writes, and island/rejoin behavior.

Important APIs/types/functions: helpers include `launchNode`, `createNetworkDBInstances`, `closeNetworkDBInstances`, `verifyNodeExistence`, `verifyNetworkExistence`, `verifyEntryExistence`, `testWatch`, and `dumpTable`. Tests cover `Join`, `JoinNetwork`, `LeaveNetwork`, `CreateEntry`, `UpdateEntry`, `DeleteEntry`, `GetEntry`, `WalkTable`, `Watch`, `findNode`, `changeNodeState`, and `purgeReincarnation`.

Control flow: tests allocate loopback-bound memberlist ports from an atomic counter, form clusters by joining each new node to the previous node, poll for full peer visibility, then exercise operations and poll for replicated state. Several tests close nodes to force leave/failure handling and restart nodes with new IDs but reused addresses to verify reincarnation cleanup.

State and persistence behavior: NetworkDB state is in in-memory cluster maps and Lamport-clocked tables; tests inspect `nodes`, `leftNodes`, `failedNodes`, `thisNodeNetworks`, and entry counters directly. `TestNetworkDBGarbageCollection` configures reaping intervals and checks tombstone count decay. `TestMain` attempts to enable IPv6 on loopback and sets debug logging.

Dependencies and integration points: uses real `memberlist`, local network sockets, `containerd/log`, `go-events`, `errdefs`, and libnetwork string IDs. These tests integrate generated protobuf messages, gossip delegates, node management, watch broadcasting, and table storage.

Risks: tests are timing- and host-network-sensitive, particularly IPv6 setup, port reuse, memberlist timing, and long GC sleeps. Direct internal map inspection gives strong coverage but can couple tests to implementation shape. Parallel create/delete tests validate single-writer success but depend on race-safe NetworkDB internals.

Test signals: broad regression coverage. Specific signals include multi-network joins/leaves, isolation of non-member nodes, 1000-entry bulk sync, medium-cluster CRUD under concurrent reads, tombstone GC, node state map transitions, reincarnation by address/port, and cluster island recovery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdbdiagnostic.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdbdiagnostic.go

Purpose: HTTP diagnostic/control surface for NetworkDB, wiring debug endpoints that join clusters, inspect peers, mutate entries, query tables, join/leave networks, and report per-network stats.

Important APIs/types/functions: `Mux` abstracts `HandleFunc`; `RegisterDiagnosticHandlers` registers `/join`, `/networkpeers`, `/clusterpeers`, `/joinnetwork`, `/leavenetwork`, `/createentry`, `/updateentry`, `/deleteentry`, `/getentry`, `/gettable`, and `/networkstats`. Handler methods call core NetworkDB APIs and return `diagnostic` response objects.

Control flow: each handler parses form parameters, logs an audit entry with remote address, caller method, and URL, validates required parameters, performs a NetworkDB operation, and replies through `diagnostic.HTTPReply`. Create/update/get/table handlers optionally base64-decode or encode values unless unsafe mode is requested by diagnostic options.

State and persistence behavior: handlers mutate live NetworkDB state through `Join`, `JoinNetwork`, `LeaveNetwork`, `CreateEntry`, `UpdateEntry`, and `DeleteEntry`. They do not persist data themselves; changes propagate through normal NetworkDB gossip and table state. Stats read `thisNodeNetworks` under read lock and report entry count plus table broadcast queue length.

Dependencies and integration points: integrates `net/http`, `containerd/log`, `daemon/libnetwork/diagnostic`, and `internal/caller`. This file is likely mounted into Docker's debug diagnostics server, so it bridges operator commands into cluster control paths.

Risks: diagnostic endpoints can mutate cluster state, so exposure must be tightly controlled by the surrounding diagnostic server. Unsafe mode may return or accept raw string values; default base64 mode is safer for arbitrary bytes. Input validation only checks presence, not semantic correctness beyond downstream NetworkDB errors.

Test signals: no direct tests in this subset. Coverage is indirect through core NetworkDB API tests, but HTTP parameter parsing, base64 behavior, and diagnostic response formatting would benefit from focused handler tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdbdiagnostic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/nodemgmt.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/nodemgmt.go

Purpose: internal node state management for NetworkDB. It tracks movement of nodes between active, left, and failed sets, cleans entries when nodes leave or fail, and detects reincarnated nodes that reuse the same network address/port with a different name.

Important APIs/types/functions: `nodeState` constants model `nodeNotFound`, `nodeActiveState`, `nodeLeftState`, and `nodeFailedState`; `nodeStateName` supports logging; `findNode` searches `nodes`, `leftNodes`, and `failedNodes`; `changeNodeState` moves nodes across maps; `purgeReincarnation` marks old incarnations left; `estNumNodes` reads the atomic active-node estimate.

Control flow: `changeNodeState` finds the current map, no-ops if already in target state, deletes from old map, inserts into target map, updates `estNodes`, logs the transition, and for left/failed transitions sets `reapTime` and deletes node-owned network/table entries. `purgeReincarnation` scans active, failed, then left nodes for matching address/port and different name, then moves the old node to left.

State and persistence behavior: all state is in-memory NetworkDB membership maps and node reap timers. Entry cleanup triggers table/network tombstone behavior elsewhere. `estNodes` is an atomic derived count of active nodes.

Dependencies and integration points: uses `memberlist.Node` for address/port identity and `containerd/log` for transition logs. It relies on NetworkDB methods `deleteNodeFromNetworks` and `deleteNodeTableEntries`, which are outside this subset.

Risks: callers must hold appropriate locks when mutating maps; this file does not lock internally. Reincarnation detection by address/port can incorrectly retire a previous node if address reuse is ambiguous, but it is necessary for fast recovery after daemon/node ID changes. Unknown `nodeState` values are silently ignored after a TODO.

Test signals: `TestFindNode`, `TestChangeNodeState`, `TestNodeReincarnation`, `TestNetworkDBNodeLeave`, and island recovery tests validate map transitions, reaping timer setup, entry deletion, and address/port reincarnation handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/nodemgmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/tableevent_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/tableevent_test.go

Purpose: targeted tests for table event ordering, watch synthesis, filtering, and leave/rejoin races in NetworkDB. It focuses on subtle Lamport and tombstone behavior that broad cluster tests may not isolate.

Important APIs/types/functions: tests include `TestWatch_out_of_order`, `TestWatch_filters`, and `TestLeaveRejoinOutOfOrder`; helpers include `messageBuffer`, `Append`, `Compound`, `Reset`, and `tableEventHelper`. The tests exercise `eventDelegate.NotifyJoin`, `delegate.NotifyMsg`, `makeCompoundMessage`, `encodeMessage`, `Watch`, and `WalkTable`.

Control flow: tests manually build compound gossip payloads with specific Lamport times, inject them into a single NetworkDB instance, then drain watch channels or table state. The out-of-order test creates cases such as create/delete gaps, hidden recreates, update-before-create, and stale delete/create pairs.

State and persistence behavior: the tests inspect in-memory table entries and watch queue output. Synthetic initial watch events exclude local entries and deleted entries. Leave/rejoin regression verifies that rebroadcast or bulk-sync table events do not lose valid state when network leave/join events arrive around them.

Dependencies and integration points: integrates generated protobuf event types, memberlist node notification, Serf Lamport times, docker/go-events channels, and helpers from the broader networkdb package.

Risks: the tests encode exact event sequences, so changing watch semantics or event ordering must update expected event lists carefully. Manual message injection bypasses some memberlist paths, which is good for determinism but not full end-to-end coverage.

Test signals: high-value regression signal for watchers. Expected behavior includes deletes reporting the last observed value, updates to unknown/deleted keys surfacing as creates, stale create/delete suppression, table/network filters, and correct state after leave/rejoin out-of-order delivery.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/tableevent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/watch.go -->
## sources/cloud-native/moby/daemon/libnetwork/networkdb/watch.go

Purpose: watch API for NetworkDB table changes. It exposes filtered event streams to consumers and synthesizes initial create events for existing remote entries so watchers start with a coherent view.

Important APIs/types/functions: `WatchEvent` carries table, network ID, key, current value, and previous value; methods `IsCreate`, `IsUpdate`, `IsDelete`, and `String` classify events; `NodeTable` and `NodeAddr` represent node join/leave table notifications; `(*NetworkDB).Watch` creates an `events.Channel` plus cancellation function.

Control flow: `Watch` optionally builds an `events.Matcher` for table/network filters, wraps an events queue in a filter, locks NetworkDB, walks either `byNetwork` or `byTable` radix indexes to emit synthetic create events for non-deleting entries not owned by this node, registers the sink with `nDB.broadcaster`, and returns a cleanup closure that removes and closes the sink/channel.

State and persistence behavior: no durable state is introduced, but watch registration adds an event sink to the NetworkDB broadcaster. Initial state is read under `RLock` to avoid racing table mutation while synthetic events are generated. Local entries are excluded from initial watch state.

Dependencies and integration points: uses `github.com/docker/go-events`, `net`, string path parsing, and NetworkDB indexes keyed by table/network. It is consumed by libnetwork code that needs to react to remote distributed table changes.

Risks: synthetic event generation depends on index path formats and `strings.SplitN` tuple lengths. The channel is unbuffered at creation but wrapped in a queue; slow consumers can still create backpressure or queue growth depending on go-events behavior. Correct cancellation is required to avoid leaked broadcaster sinks.

Test signals: `TestNetworkDBWatch`, `TestWatch_out_of_order`, and `TestWatch_filters` validate create/update/delete classification, synthetic initial state, filter combinations, local-entry exclusion, and out-of-order event behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/watch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/nlwrap/nlwrap_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/nlwrap/nlwrap_linux.go

Purpose: Linux netlink wrapper that makes selected vishvananda/netlink operations more robust against interrupted dumps and namespace thread contamination. It provides a drop-in-ish `Handle` wrapper plus package-level helpers for calls that libnetwork commonly uses.

Important APIs/types/functions: `Handle` embeds `*netlink.Handle`; constructors `NewHandle` and `NewHandleAt`; lifecycle `Close`; retry helpers `retryOnIntr` and `discardErrDumpInterrupted`; wrapped operations include `AddrList`, `ConntrackDeleteFilters`, `ConntrackTableList`, `LinkByName`, `LinkList`, `LinkSubscribeWithOptions`, `RouteList`, `XfrmPolicyList`, and `XfrmStateList`.

Control flow: wrapped calls retry up to `maxAttempts` when `netlink.ErrDumpInterrupted` is returned, then log and discard that error to preserve older netlink behavior that returned possibly inconsistent results. `NewHandleAt` and namespaced `LinkSubscribeWithOptions` create sockets on a locked OS thread, restore the original namespace when possible, and intentionally keep the goroutine locked if restoration fails so the Go runtime does not reuse a tainted thread.

State and persistence behavior: no persistent state. It creates netlink sockets and temporary goroutines/threads. Handles must be closed by callers. The thread-lock behavior is defensive process state management around Linux network namespaces.

Dependencies and integration points: wraps `github.com/vishvananda/netlink` and `netns`, uses `runtime.LockOSThread`, `containerd/log`, and `pkg/errors`. OSL namespace and interface code depend on these wrappers for safer namespace operations.

Risks: after repeated `ErrDumpInterrupted`, callers receive data that may be inconsistent, trading strictness for compatibility. Namespace restoration failure behavior is subtle and must not unlock contaminated threads. `LinkSubscribeWithOptions` requires callers to close `done` to stop netlink goroutines cleanly.

Test signals: no direct tests in this subset. Indirect coverage comes from namespace/interface tests and any libnetwork integration tests running in real namespaces. Rootless namespace contamination is a key scenario that should have focused regression coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/nlwrap/nlwrap_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ns/init_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/ns/init_linux.go

Purpose: initializes and exposes process-wide handles for the initial or detached host network namespace and a default netlink handle with supported netlink families.

Important APIs/types/functions: `NetlinkSocketsTimeout` sets a 3-second socket timeout; `initNamespace` memoizes `initHandles` via `sync.OnceValues`; public accessors are `NsHandle`, `NlHandle`, and test-only `ResetHandles`; support probes include `getSupportedNlFamilies`, `checkXfrmSocket`, and `checkNfSocket`.

Control flow: `initHandles` checks rootless detached netns configuration. If detached, it opens that namespace and creates a netlink handle inside it via `nlwrap.NewHandleAt`; otherwise it uses current namespace and `nlwrap.NewHandle`. It probes XFRM and netfilter support, attempts module loading for conntrack, sets socket timeout, and panics if the default netlink handle cannot be created.

State and persistence behavior: process-global namespace and netlink handles are cached. `ResetHandles` reinitializes them for tests and closes previous handles, explicitly warning it is unsafe with concurrent users.

Dependencies and integration points: depends on `rootless.DetachedNetNS`, libnetwork `modprobe`, `nlwrap`, `netns`, Linux `syscall`, and containerd logging. OSL code uses `ns.NsHandle()` to move links back to the host namespace and `ns.NlHandle()` for host-side operations.

Risks: global handle lifetime is sensitive; closing or resetting while in use can break callers. Panicking on netlink handle creation is intentional but harsh. Module probing may log warnings depending on kernel capabilities. Rootless detached namespace behavior depends on correct thread-safe `nlwrap.NewHandleAt`.

Test signals: no direct tests here in the subset, but OSL tests and rootless networking flows exercise these handles. `ResetHandles` exists specifically to enable clean test state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ns/init_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/options/options.go -->
## sources/cloud-native/moby/daemon/libnetwork/options/options.go

Purpose: reflection-based utility for converting unstructured option maps into strongly typed configuration structs while reporting typed errors for unknown, unsettable, or mismatched fields.

Important APIs/types/functions: error types `NoSuchFieldError`, `CannotSetFieldError`, and `TypeMismatchError`; `Generic map[string]any`; generic function `GenerateFromModel[T any](options Generic) (T, error)`.

Control flow: `GenerateFromModel` determines whether `T` is a pointer, allocates a new value of the target struct type, iterates map entries, locates fields by exact name, validates settable/exported status and exact type equality, sets values through reflection, then returns either the pointer or value form matching `T`.

State and persistence behavior: stateless conversion. The returned object is freshly allocated/populated; the input map is not mutated.

Dependencies and integration points: uses Go `reflect` and `fmt`. It is a generic helper likely used by libnetwork components accepting loose option bags while wanting typed internal models.

Risks: requires exact Go field names and exact dynamic value types, so aliases, assignable-but-not-identical types, pointer/value mismatch, and numeric widening are rejected. Map iteration order means when multiple invalid options exist, the reported first error is nondeterministic. It assumes `T` or `*T` is a struct-like target; non-struct use may panic or fail unexpectedly.

Test signals: `options_test.go` covers value and pointer models plus all three error classes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/options/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/options/options_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/options/options_test.go

Purpose: unit tests for the generic options-to-struct reflection helper.

Important APIs/types/functions: tests include `TestGenerate`, `TestGeneratePtr`, `TestGenerateMissingField`, `TestFieldCannotBeSet`, and `TestTypeMismatchError`.

Control flow: tests build small local model structs, pass `Generic` maps, call `GenerateFromModel` with value and pointer type parameters, and assert either deep equality or exact error strings/types.

State and persistence behavior: no state beyond test-local maps and structs. The unexported `foo` field case verifies that reflection respects settability.

Dependencies and integration points: uses `gotest.tools/v3/assert` and comparison helpers. It directly validates `options.go` without external libnetwork dependencies.

Risks: tests do not cover non-struct model types, nil values, assignable-but-not-identical types, embedded fields, or multiple simultaneous bad options. Exact error-string checks protect user-facing diagnostics but may make wording changes breaking.

Test signals: good coverage for intended happy path and primary validation errors, including pointer model support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/options/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux.go

Purpose: Linux implementation of libnetwork sandbox interface management. It creates/moves/renames/configures links in network namespaces, assigns addresses/routes/sysctls, brings links up, waits for readiness, advertises addresses with unsolicited ARP/NA, and removes interfaces.

Important APIs/types/functions: `Interface` stores source/destination names, master, MAC, IPv4/IPv6/link-local addresses, routes, sysctls, advertisement settings, and namespace pointer. Key methods/functions include `newInterface`, accessors, `Statistics`, `Namespace.AddInterface`, `createInterface`, `generateIfaceName`, `waitForIfUpped`, `waitForBridgePort`, `waitForMcastRoute`, `advertiseAddrs`, `prepAdvertiseAddrs`, `RemoveInterface`, `configureInterface`, `setInterfaceMAC/IP/IPv6/Master/LinkLocalIPs/Routes/Name`, `setSysctls`, and `checkRouteConflict`.

Control flow: `AddInterface` opens the target netns if needed, builds an `Interface`, moves or creates the link, configures it, retries `LinkSetUp`, adds non-default connected routes, waits for link-up events, waits for bridge forwarding/multicast route where relevant, then sends ARP/NA advertisements. On configuration failure it tries to rename and move the link back to host namespace.

State and persistence behavior: mutates kernel network namespace state and tracks configured interfaces in `Namespace.iFaces` under lock. `Interface.stopCh` cancels background advertisement sends on removal. Sysctls write `/proc/sys/net/...` inside the namespace. IPv6 address state may be cleared from `Interface` if sysctl settings remove it.

Dependencies and integration points: heavy integration with `nlwrap`, global `ns` handles, vishvananda/netlink/netns, OpenTelemetry spans, `l2disco` unsolicited ARP/NA helpers, libnetwork `types`, and Linux `/sys/class/net` bridge files.

Risks: high-risk kernel-facing code. Races around interface readiness, namespace movement, bridge forwarding, multicast routes, and sysctl effects can affect container connectivity. Error recovery after partial configuration is best effort. `checkRouteConflict` is conservative and may reject overlapping routes. Background ARP/NA sends must stop when interfaces are removed.

Test signals: `interface_linux_test.go` covers generated name gaps and parallel `AddInterface` name allocation. Broader integration tests are needed for real link movement, address assignment, route conflicts, sysctls, neighbor advertisements, and removal behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux_test.go

Purpose: Linux tests for OSL interface name generation and concurrent interface addition.

Important APIs/types/functions: `TestGenerateIfaceName` validates gap-filling suffix generation; `TestAddInterfaceInParallel` creates a named netns and dummy links, then concurrently calls `Namespace.AddInterface` with `WithCreatedInContainer(true)`.

Control flow: the parallel test locks the OS thread, creates a named namespace, creates a namespaced netlink handle, adds ten dummy interfaces, launches ten goroutines through `sync.WaitGroup.Go`, then lists links and expects `eth0` through `eth9`.

State and persistence behavior: creates real Linux named network namespaces and dummy netlink devices, then deletes/closes the namespace through defers. It mutates kernel network state and requires permissions/capabilities suitable for netns operations.

Dependencies and integration points: uses `netns`, `netlink`, `nlwrap`, `sliceutil`, `runtime.LockOSThread`, and gotest assertions. It directly exercises `Namespace.AddInterface`, `generateIfaceName`, and namespace handle behavior.

Risks: environment-sensitive and likely requires root or CAP_NET_ADMIN. The final `nlwrap.LinkList()` call lists the current namespace, so correctness depends on thread namespace context and the handle setup. It does not test address/route/sysctl setup.

Test signals: strong targeted signal that interface naming is concurrency-safe and fills numeric gaps without duplicate names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/interface_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/interface_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/interface_unsupported.go

Purpose: non-Linux build stub defining `Interface` for platforms where Linux interface operations are unavailable.

Important APIs/types/functions: under `//go:build !linux`, it declares an empty `Interface` type.

Control flow: no runtime behavior. It exists to satisfy package type references when Linux-specific files are excluded.

State and persistence behavior: none.

Dependencies and integration points: pairs with platform-specific namespace/sandbox stubs so libnetwork can compile on unsupported platforms with reduced functionality.

Risks: code that assumes Linux `Interface` methods must be build-tagged or otherwise unavailable on non-Linux. The empty type intentionally provides no operations.

Test signals: no tests in this subset; build coverage on non-Linux is the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/interface_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs.go

Purpose: shared kernel knob model used by platform-specific OS tweak application.

Important APIs/types/functions: `conditionalCheck` function type; `OSValue` pairs a desired sysctl value with an optional predicate; `propertyIsValid` decides whether a new value should be applied.

Control flow: `propertyIsValid` returns true if no check function is supplied or if the predicate accepts the old and new values. Linux `ApplyOSTweaks` uses this before writing `/proc/sys`.

State and persistence behavior: no state. It is a pure helper around desired kernel configuration values.

Dependencies and integration points: used by `knobs_linux.go` and by `Namespace.ApplyOSTweaks` for ingress/load-balancer IPVS settings.

Risks: predicate semantics are broad; a misleading check function can prevent required sysctl updates or apply unsafe ones. There are no tests here for custom predicates.

Test signals: indirect only through Linux knob tests and any consumers that pass non-nil checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux.go

Purpose: Linux implementation of applying kernel sysctl tweaks under `/proc/sys`.

Important APIs/types/functions: `writeSystemProperty`, `readSystemProperty`, and `ApplyOSTweaks`.

Control flow: keys such as `net.ipv4.vs.conn_reuse_mode` are converted to `/proc/sys/net/ipv4/vs/conn_reuse_mode`; `ApplyOSTweaks` reads the old value, skips missing keys, logs read errors, checks whether the desired value should apply, writes the new value, and logs either warning or debug output.

State and persistence behavior: mutates live kernel sysctl state. Changes are process-external and may affect host networking/IPVS behavior until changed again or rebooted depending on sysctl persistence outside Docker.

Dependencies and integration points: called by OSL namespace `ApplyOSTweaks` for load-balancer and ingress sandboxes. Uses `os` file IO and containerd logging.

Risks: writes to host `/proc/sys`, requiring privileges and correct kernel module availability. Missing files are silently skipped; write failures are warnings, not fatal. The code writes raw value strings without newline normalization.

Test signals: `knobs_linux_test.go` reads/writes selected neighbor GC thresholds when available and restores old values, providing basic sysctl IO coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux_test.go

Purpose: Linux test for reading and writing kernel sysctl knob files.

Important APIs/types/functions: `TestReadWriteKnobs` exercises `readSystemProperty` and `writeSystemProperty` for IPv4 neighbor GC threshold sysctls.

Control flow: for each configured key, the test tries to read the current value, skips unavailable paths with a warning, writes `10000`, reads back and asserts equality, then restores the original value.

State and persistence behavior: mutates host kernel sysctls during the test and attempts restoration. If restoration fails, the host setting may be left changed.

Dependencies and integration points: uses containerd logging and gotest assertions. It requires a Linux environment with writable `/proc/sys/net/ipv4/neigh/default/*`.

Risks: privileged and environment-sensitive. It tests raw IO helpers rather than `ApplyOSTweaks` conditional behavior. Running in constrained CI may skip paths or fail writes.

Test signals: basic end-to-end confirmation that sysctl path translation, trimming, writing, and restoration work on available kernels.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_unsupported.go

Purpose: non-Linux no-op implementation of OS tweak application.

Important APIs/types/functions: build-tagged `ApplyOSTweaks(osConfig map[string]*OSValue)` that does nothing.

Control flow: no-op for all input.

State and persistence behavior: no state and no system mutation.

Dependencies and integration points: keeps callers portable when Linux `/proc/sys` is unavailable.

Risks: platform behavior diverges; callers expecting network sysctls to be applied must not assume this works outside Linux.

Test signals: build coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/kernel/knobs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/namespace_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/namespace_linux.go

Purpose: Linux network namespace sandbox implementation for libnetwork. It creates, opens, restores, mutates, and destroys namespace-backed sandboxes and exposes namespace-scoped operations used by interface, neighbor, and route code.

Important APIs/types/functions: `SetBasePath`, `GenerateKey`, `NewSandbox`, `GetSandboxForExternalKey`, `createNetworkNamespace`, `createNamespaceFile`, `Namespace`, `Interfaces`, `InterfaceBySrcName`, `AddAliasIP`, `RemoveAliasIP`, `DisableARPForVIP`, `InvokeFunc`, `Key`, `Destroy`, `RestoreInterfaces`, `RestoreRoutes`, `RestoreGateway`, `IPv6LoEnabled`, `RefreshIPv6LoEnabled`, `ApplyOSTweaks`, and `setIPv6`.

Control flow: sandbox creation bind-mounts a thread's network namespace to a file under the base path, optionally via `unshare.Go(CLONE_NEWNET)`, then opens a namespace-specific netlink handle and brings loopback up. `InvokeFunc` runs callbacks on a locked OS thread inside the sandbox namespace and restores the original namespace. Restore paths reconstruct interface metadata by scanning links and addresses, then send neighbor advertisements.

State and persistence behavior: persistent-ish sandbox identity is the namespace bind mount file. `Namespace` keeps interface metadata, gateways, default-route source names, static routes, IPv6 loopback cache, and netlink handle. Destroy closes the handle, detaches the mount, and removes the namespace file. Sysctls and alias IPs mutate namespace-local kernel state.

Dependencies and integration points: depends on rootless support, unshare, `nlwrap`, global `ns` handles, kernel knobs, netlink/netns, and Linux syscalls. It is the central object used by OSL interface, route, and neighbor modules.

Risks: namespace/thread handling is delicate; failure to restore thread netns can contaminate runtime threads, mitigated by locked goroutine behavior. File bind mounts and unmounts require privileges and cleanup. `Destroy` assumes no running process still uses the namespace. Restore heuristics for interface names can be ambiguous for vxlan/veth and address matches.

Test signals: interface tests exercise namespace creation and AddInterface. Broader sandbox lifecycle, rootless, external-key, restore, IPv6, and sysctl behavior need integration tests with real kernel capabilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/namespace_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/namespace_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/namespace_unsupported.go

Purpose: unsupported-platform namespace stub for non-Linux, non-Windows, non-FreeBSD builds.

Important APIs/types/functions: empty `Namespace`, no-op `Destroy`, and `GetSandboxForExternalKey` returning nils.

Control flow: no real behavior; it compiles references where OSL functionality is not implemented.

State and persistence behavior: none.

Dependencies and integration points: complements platform-specific files selected by build tags.

Risks: callers must not expect functional sandboxing on these platforms. Returning `(nil, nil)` can be hazardous if higher layers do not guard platform support.

Test signals: build-only coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/namespace_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/namespace_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/namespace_windows.go

Purpose: Windows namespace/sandbox stub for this OSL package.

Important APIs/types/functions: `GenerateKey` returns the container ID unchanged; empty `Namespace`; no-op `Destroy`; `NewSandbox` and `GetSandboxForExternalKey` return nils.

Control flow: no namespace creation or mutation occurs in this file.

State and persistence behavior: none. Windows networking is handled elsewhere or not through this Linux-style OSL implementation.

Dependencies and integration points: selected by Windows build tags to satisfy package references.

Risks: returning `(nil, nil)` requires callers to be platform-aware. Behavior differs from FreeBSD, which truncates keys, and Linux, which creates bind-mounted netns paths.

Test signals: build-only coverage in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/namespace_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/neigh_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/neigh_linux.go

Purpose: Linux neighbor table management for OSL sandboxes, adding and deleting permanent neighbor entries for endpoint reachability.

Important APIs/types/functions: `NeighborSearchError` formats already-present/not-found errors; `Namespace.AddNeighbor`, `Namespace.DeleteNeighbor`, internal `neigh` options holder, and `nlNeigh` for netlink neighbor construction.

Control flow: options set link name and address family. `nlNeigh` creates a permanent `netlink.Neigh`, sets `NTF_SELF` when family is specified, resolves source link names to destination interface names through `findDst`, and fills link index. Add calls `NeighAdd` and maps `os.ErrExist` to `NeighborSearchError`. Delete calls `NeighDel`, maps missing entries to `NeighborSearchError`, and for family-specific bridge entries also tries deleting a dynamic `NTF_MASTER` entry.

State and persistence behavior: mutates namespace neighbor tables. Entries are permanent until deleted or namespace teardown. The file itself stores no persistent Go state.

Dependencies and integration points: uses `Namespace.nlHandle`, OSL interface mapping, vishvananda/netlink, and `NeighOption` functions from `options_linux.go`.

Risks: add/delete must use the same parameters to identify entries. Link-name resolution depends on `Namespace.iFaces` metadata. Bridge family behavior is specialized and may leave dynamic entries if deletion fails. Error mapping depends on netlink errors wrapping `os.ErrExist`/`os.ErrNotExist`.

Test signals: no direct tests in this subset. Integration tests should verify bridge and non-bridge neighbor add/delete, duplicate handling, missing delete handling, and link-specific entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/neigh_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/neigh_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/neigh_unsupported.go

Purpose: non-Linux stub for the internal neighbor option storage type.

Important APIs/types/functions: build-tagged empty `neigh` type.

Control flow: no behavior. It enables shared option type declarations to compile without Linux neighbor implementation.

State and persistence behavior: none.

Dependencies and integration points: pairs with `sandbox.go` `NeighOption` and Linux-only option functions.

Risks: neighbor operations are unavailable on unsupported platforms; build tags must prevent Linux-only methods from being referenced.

Test signals: build coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/neigh_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/netlinkutil_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/netlinkutil_linux.go

Purpose: small Linux debug utility for formatting network device flags into readable names.

Important APIs/types/functions: `deviceFlags` type, `deviceFlagStrings` mapping from `unix.IFF_*` bits to names, and `deviceFlags.String`.

Control flow: `String` iterates over 32 bits, appends known flag names, accumulates unknown bits as a hex mask, and returns a `deviceFlags(...)` string joined by ` | `.

State and persistence behavior: stateless formatting.

Dependencies and integration points: used in `waitForIfUpped` logging to make netlink link update flags understandable. Depends on `golang.org/x/sys/unix`.

Risks: only checks 32 bits, which matches current flag width assumptions. Unknown flags are preserved as hex, preventing silent loss but not naming newer constants.

Test signals: no direct unit tests, but behavior is simple and used in debug logs during interface setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/netlinkutil_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/options_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/options_linux.go

Purpose: Linux OSL functional options for configuring neighbor entries and sandbox interfaces.

Important APIs/types/functions: `processNeighOptions`; neighbor options `WithLinkName` and `WithFamily`; interface options `WithIsBridge`, `WithMaster`, `WithMACAddress`, `WithIPv4Address`, `WithIPv6Address`, `WithLinkLocalAddresses`, `WithRoutes`, `WithSysctls`, `WithAdvertiseAddrNMsgs`, `WithAdvertiseAddrInterval`, and `WithCreatedInContainer`.

Control flow: each option closes over a value and mutates `neigh` or `Interface` when applied by `newInterface` or `nlNeigh`. Advertisement options validate configured counts and intervals against min/max constants before accepting them.

State and persistence behavior: options only populate in-memory configuration structs; later interface/neighbor methods turn those settings into kernel state.

Dependencies and integration points: used by network drivers and restore paths that call `Namespace.AddInterface`, `RestoreInterfaces`, `AddNeighbor`, and `DeleteNeighbor`.

Risks: most options store references or slices directly without cloning, so caller mutation after option application can affect interface state. The error message in `WithAdvertiseAddrInterval` names `AdvertiseAddrNMsgs`, which is misleading. Validation is limited to advertisement ranges.

Test signals: indirect through interface tests and any driver integration tests. No focused tests for option validation or slice aliasing in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/options_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/route_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/route_linux.go

Purpose: Linux/FreeBSD route and gateway management for OSL namespaces.

Important APIs/types/functions: accessors `Gateway`, `GatewayIPv6`, `StaticRoutes`; mutators `SetGateway`, `UnsetGateway`, `SetGatewayIPv6`, `UnsetGatewayIPv6`, `AddStaticRoute`, `RemoveStaticRoute`, `SetDefaultRouteIPv4`, `SetDefaultRouteIPv6`, `UnsetDefaultRouteIPv4`, and `UnsetDefaultRouteIPv6`; helpers `programGateway`, `programRoute`, `removeRoute`, `setDefaultRoute`, and `unsetDefaultRoute`.

Control flow: gateway programming first resolves a direct route to the gateway/next-hop through `RouteGet`, then adds or deletes a universe-scope route with the resolved link index. Connected default route methods look up an `Interface` by source name, find an unspecified route matching IPv4 or IPv6, resolve the link by destination name, and add/delete link-scope default route.

State and persistence behavior: mutates namespace routing tables through netlink and mirrors selected state in `Namespace` fields (`gw`, `gwv6`, `staticRoutes`, `defRoute4SrcName`, `defRoute6SrcName`). Accessors return copies for static routes but raw `net.IP` values for gateways.

Dependencies and integration points: depends on `Namespace.nlHandle`, OSL interface metadata, libnetwork `types.StaticRoute`, and vishvananda/netlink. Interface setup uses routes attached to `Interface`; restore paths repopulate route state.

Risks: route programming depends on `RouteGet` returning usable link indexes. `RemoveStaticRoute` removes by pointer identity, not semantic route equality. Gateway accessors return mutable `net.IP` slices, so callers could mutate stored values. FreeBSD build tag shares this file despite netlink dependency, implying package build context must provide compatible files or tags.

Test signals: no direct route tests in this subset. Integration tests should cover gateway add/remove, default connected routes, static route pointer removal, and IPv6 route behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/route_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox.go

Purpose: shared OSL type declarations for sandbox classification, interface restore metadata, and functional option signatures.

Important APIs/types/functions: `SandboxType` enum with `SandboxTypeIngress` and `SandboxTypeLoadBalancer`; `Iface` struct containing `SrcName`, `DstPrefix`, and `DstName`; option function types `IfaceOption` and `NeighOption`.

Control flow: no runtime logic. The types are consumed by platform-specific namespace/interface/neighbor implementations.

State and persistence behavior: no state. `Iface` acts as a serializable/restorable identity tuple for interfaces.

Dependencies and integration points: `Namespace.ApplyOSTweaks` switches on `SandboxType`; `RestoreInterfaces` consumes `map[Iface][]IfaceOption`; Linux option functions implement `IfaceOption`/`NeighOption`.

Risks: enum uses repeated `iota` assignments; current values are distinct but style is unusual. `Iface` contains only names, so restore logic must infer actual links/addresses from options and namespace state.

Test signals: indirect through namespace restore and OS tweak behavior; no direct tests needed beyond compile coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_freebsd.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_freebsd.go

Purpose: FreeBSD sandbox stub providing key generation and placeholder sandbox constructors.

Important APIs/types/functions: `GenerateKey` truncates container IDs to 12 characters; `NewSandbox` and `GetSandboxForExternalKey` return nils.

Control flow: only key truncation has behavior; sandbox creation is unimplemented.

State and persistence behavior: none.

Dependencies and integration points: selected for FreeBSD builds, alongside shared OSL declarations. It preserves Docker-style short sandbox keys but does not implement namespace management.

Risks: returning `(nil, nil)` can hide unsupported functionality if callers do not check platform capabilities. FreeBSD route file build tags overlap with this platform, so build integration should be watched.

Test signals: build-only coverage; no functional tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_freebsd.go -->
