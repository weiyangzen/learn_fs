# Research Group: subset-b-008425

This grouped report covers the exact source files assigned to work item `subset-b-008425`. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/extensions/rubydomain.py -->
# sources/storage-engines/foundationdb/documentation/sphinx/extensions/rubydomain.py

## Purpose
This file implements a custom Sphinx domain named `rb` for documenting Ruby APIs in the FoundationDB documentation tree. It is adapted from an older Sphinx Ruby domain and provides directives, roles, index generation, object registration, and cross-reference resolution for Ruby modules, classes, methods, attributes, constants, globals, and exceptions.

## Important APIs, Types, and Functions
The core type is `RubyDomain`, a `sphinx.domains.Domain` subclass that registers object types, directive handlers, roles, initial domain data, and the Ruby module index. `RubyObject` is the shared `ObjectDescription` base for signature parsing, display node construction, target creation, and index entry insertion. Specialized subclasses include `RubyModulelevel`, `RubyGloballevel`, `RubyEverywhere`, `RubyClasslike`, and `RubyClassmember`. `RubyModule` and `RubyCurrentModule` are directives for changing Ruby module context. `RubyXRefRole` preprocesses role titles/targets and stores current module/class on reference nodes. `RubyModuleIndex.generate()` builds the Ruby module index from domain data.

Key helper values are `rb_sig_re` for parsing Ruby signatures, `rb_paramlist_re` for optional/parameter tokenization, `separators` for object naming, and `ruby_rsplit()` for splitting class/member names used in index text. The domain's public integration point is `setup(app)`, which calls `app.add_domain(RubyDomain)`.

## Control Flow
Sphinx calls directive handlers while parsing RST. `RubyObject.handle_signature()` parses one signature, computes module/class/fullname context from directive options and `env.temp_data`, and emits Sphinx description nodes. `add_target_and_index()` then registers unique target ids, records object metadata in `env.domaindata['rb']['objects']`, warns on duplicate descriptions, and appends index entries. `before_content()` and `after_content()` manage temporary class context for nested members.

Cross references enter through `RubyXRefRole.process_link()`, which normalizes displayed titles and marks specific searches for leading-dot targets. During resolution, `RubyDomain.resolve_xref()` first checks module references, then calls `find_obj()` with module/class context and search ordering. Module index generation sorts stored modules, strips common configured prefixes, groups submodules, and decides whether the index should start collapsed.

## State and Persistence Behavior
State is held in Sphinx build environment data, not in external files. Persistent domain state lives in `initial_data`: `objects` maps full names to `(docname, objtype)`, and `modules` maps module names to `(docname, synopsis, platform, deprecated)`. Temporary parser context lives in `env.temp_data['rb:module']` and `env.temp_data['rb:class']`. `clear_doc()` removes objects and modules for a rebuilt document so incremental builds do not retain stale entries.

## Dependencies and Integration Points
The file depends on `docutils` nodes/directives, Sphinx addnodes, roles, domain APIs, `ObjectDescription`, `make_refnode`, and doc field classes. It integrates with Sphinx configuration values such as `add_module_names` and `modindex_common_prefix`. It expects old-style Sphinx APIs such as `env.warn`, tuple-shaped index entries, and role/directive registration semantics compatible with the vendored documentation toolchain.

## Risks
The largest risk is Sphinx API drift: `env.warn`, index tuple layouts, and some imports differ across modern Sphinx releases. Signature parsing is permissive but incomplete for complex Ruby syntax; malformed optional parameter brackets raise `ValueError`, which can fail documentation builds. `ruby_rsplit()` relies on a separator regex that is hard to reason about and may mis-split unusual names. Duplicate targets only warn and overwrite domain data. Cross-reference search order has special cases for module/class prefixes and `object.` methods, so ambiguous names can resolve unexpectedly.

## Test Signals
Useful validation is a Sphinx build that exercises Ruby directives, module index generation, and cross references for globals, functions, instance methods, class methods, attributes, constants, modules, and nested classes. Regression tests should include duplicate object warnings, incremental rebuild `clear_doc()` behavior, tilde/leading-dot role handling, optional parameter parsing, and compatibility with the exact Sphinx version used by FoundationDB docs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/extensions/rubydomain.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/api-common.rst.inc -->
# sources/storage-engines/foundationdb/documentation/sphinx/source/api-common.rst.inc

## Purpose
This include file is a shared reStructuredText substitution library for FoundationDB API documentation. It centralizes cross-language wording for API versioning, transactions, futures, database and transaction options, atomic operations, tuple/subspace/directory layers, locality APIs, TLS/network options, and operational warnings.

## Important APIs, Types, and Functions
There is no executable API, but the file defines many substitution names that are consumed by language-specific documentation pages. Important substitutions include API-version guidance (`|api-version|`, `|api-version-rationale|`, multi-version warnings), transaction behavior blurbs, atomic operation descriptions, watch behavior, conflict range descriptions, network/database/transaction option text, future cancellation semantics, `fdb.open` semantics, subspace and directory layer descriptions, and locality API warnings.

## Control Flow
Sphinx expands these substitutions wherever included pages reference them. The include is passive: build behavior depends on pages including it before using its replacement names. The content is organized topically so language-specific documents can compose shared text with language-local placeholders such as `|error-type|`, `|commit-func|`, `|database-type|`, `|tuple-layer|`, and option/function names.

## State and Persistence Behavior
The file stores documentation state only as RST source text. It does not persist runtime data. Its most important state-like value is `.. |api-version| replace:: 800`, which documents the API version used by the generated docs. Many substitutions encode durable behavioral contracts that client bindings and documentation readers rely on: commit unknown result semantics, read-your-writes behavior, timeout/retry option retention, watch limits, conflict range semantics, and versionstamp restrictions.

## Dependencies and Integration Points
This file depends on Sphinx/reStructuredText substitution syntax and on other documentation labels such as `developer-guide-error-codes`, `multi-version-client-api`, `ACID`, `conflict-ranges`, and TLS/configuration pages. It integrates with language-specific API pages by leaving placeholders for local type names and method names. It must stay synchronized with binding implementations, generated API references, FDB API version behavior, tuple/directory layer support, and option definitions.

## Risks
Documentation drift is the key risk. The file describes subtle behavior around idempotency, retry loops, watches, snapshot reads, versionstamps, system key access, trace logging, and transaction options. If implementation changes are not mirrored here, every binding page that includes the text can become misleading. Placeholder naming is another risk: missing substitutions in a consuming document will produce broken docs. The text also includes version-specific statements, so old/new API behavior needs careful review when the API version changes.

## Test Signals
Primary validation is a full Sphinx build with warnings treated as errors, checking for unresolved substitutions and references. Content-level tests are review-based: compare option names, error codes, API version, transaction semantics, and atomic operation descriptions against binding headers/generated API metadata. Link checking should cover all `:ref:` and `:doc:` targets used in the shared text.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/api-common.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/deadlock-blurb.rst.inc -->
# sources/storage-engines/foundationdb/documentation/sphinx/source/deadlock-blurb.rst.inc

## Purpose
This include file is currently empty. Its name suggests it was reserved for shared documentation text about deadlocks, likely to be included by tutorials or API guides, but no substitutions or prose are present.

## Important APIs, Types, and Functions
There are no RST substitutions, directives, anchors, executable functions, or data definitions in the file.

## Control Flow
If included by another RST page, Sphinx will process it as an empty include and emit no content. It has no control flow and cannot affect document output except by satisfying an include path that would otherwise be missing.

## State and Persistence Behavior
No state is represented. The zero-byte file can still act as a placeholder in the source tree and as a stable include target.

## Dependencies and Integration Points
Its only integration point is any RST `include::` directive that references it. Keeping the file present may avoid broken includes in pages that conditionally or historically expected a deadlock blurb.

## Risks
The main risk is ambiguity: an empty include may indicate intentionally removed content, a placeholder for future content, or accidentally missing documentation. If callers expect a substitution from this file, Sphinx will report unresolved substitution errors in the consuming page, not here.

## Test Signals
A full Sphinx build is sufficient to verify that includes resolve and no consuming page references missing substitutions from this file. File-size checks can distinguish intentional emptiness from accidental truncation only if the project records that expectation elsewhere.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/deadlock-blurb.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/guide-common.rst.inc -->
# sources/storage-engines/foundationdb/documentation/sphinx/source/guide-common.rst.inc

## Purpose
This include file centralizes shared prose and package-name substitutions for FoundationDB getting-started and administration guides. It covers platform support, cluster file format rules, development-mode warnings, upgrade guidance, server process configuration, coordinator selection, config-file change detection, and installer package filenames.

## Important APIs, Types, and Functions
The important artifacts are RST substitutions, not code. They include `|platform-not-supported-for-production|`, `|cluster-file-rule1|` through `|cluster-file-rule3|`, `|simple-installation-mode-warnings|`, `|networking-clarification|`, `|development-use-only-warning|`, `|upgrade-client-server-warning|`, `|optimize-configuration|`, `|coordinators-auto|`, `|conf-file-change-detection|`, and package substitutions for deb, rpm, macOS, and Windows installers using `|release|`.

## Control Flow
Consuming guide pages include this file and reference substitutions inline. The file itself does not branch or execute. Its content is expanded by Sphinx at build time and relies on external substitutions such as `|release|` being defined in the broader documentation context.

## State and Persistence Behavior
The file contains static documentation state: current installer naming conventions, operational recommendations, and warnings. It does not persist runtime state. The package substitutions encode release-sensitive artifact names, so the value of `|release|` determines rendered filenames.

## Dependencies and Integration Points
This file depends on Sphinx substitution syntax and cross-reference targets such as `getting-started-linux`, `foundationdb-conf`, `configuration-choosing-coordination-servers`, and `system-requirements`. It integrates with platform-specific installation pages and cluster configuration guides. It also reflects packaging conventions from the build/release pipeline.

## Risks
Operational guidance can become stale as supported platforms, package names, storage engine defaults, or memory recommendations change. The substitutions include strong production warnings; if used on the wrong platform page they could mislead users. The package names assume specific OS/package manager naming schemes and architecture strings.

## Test Signals
Run a Sphinx build with warnings-as-errors to catch missing substitutions and references. Release validation should compare rendered package names against generated artifacts. Documentation review should verify that production-support statements and coordinator/configuration recommendations match current FoundationDB release policy.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/guide-common.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/mr-status-json-schemas.rst.inc -->
# sources/storage-engines/foundationdb/documentation/sphinx/source/mr-status-json-schemas.rst.inc

## Purpose
This include file documents the shape of FoundationDB machine-readable status JSON by embedding a large `javascript` code block. It acts as an example schema/reference for fields returned under `cluster` and `client`, including process status, roles, storage metrics, recovery state, workload counters, configuration, consistency scan, storage wiggler, backup-related configuration, and client/coordinator status.

## Important APIs, Types, and Functions
There is no executable code, but important documented structures include `cluster.storage_wiggler`, `cluster.consistency_scan`, `cluster.processes`, per-role metrics, RocksDB metrics, latency statistics and bands, `logs`, `fault_tolerance`, `qos`, lag summaries, `clients`, `messages`, `recovery_state`, `workload`, `configuration`, `data`, `machines`, `idempotency_ids`, `version_epoch`, and `client.coordinators/database_status/messages/cluster_file`. Enum placeholders document allowed values for process classes, role types, storage engines, recovery states, redundancy modes, satellite/remote redundancy modes, data states, and status message names.

## Control Flow
Sphinx renders the block as documentation. The snippet is not strict JSON: it uses comments and placeholder keys such as `$map_key=...` and `$enum`. Readers should treat it as schema-like documentation, not as parseable sample output. There is no runtime control flow in the file.

## State and Persistence Behavior
The file captures an expected status surface at documentation time. It describes both persistent cluster configuration fields and ephemeral metrics/counters. Many fields are optional or absent depending on protocol compatibility, explicit configuration, role assignment, storage engine, health state, backup features, and client version.

## Dependencies and Integration Points
This file integrates with the status documentation page that includes it and with the implementation that generates `status json` output in FoundationDB. It also reflects storage engines (`ssd-redwood-1`, RocksDB variants, memory variants), multi-region configuration, backup worker settings, ratekeeper/qos reasons, gray failure state, TSS counts, and idempotency metadata. Consumers may include operators, tooling authors, dashboards, and tests that compare documentation to emitted status fields.

## Risks
The primary risk is drift from actual `status json`. Because the block is hand-maintained documentation with comments and placeholders, new status fields can be omitted and removed fields can linger. Tool authors may incorrectly copy it as valid JSON. Optional fields are documented mostly through comments, so automated validation is limited. The file is large and semantically dense, making review errors likely when status output changes.

## Test Signals
Useful validation includes building docs, comparing documented field names/enums against generated or sampled `status json`, and checking that storage engine/redundancy/recovery enum values match implementation constants. If possible, a doc-generation test should produce this include from a source schema or verify it against representative status fixtures from simulation and real clusters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/sphinx/source/mr-status-json-schemas.rst.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/CMakeLists.txt -->
# sources/storage-engines/foundationdb/documentation/tutorial/CMakeLists.txt

## Purpose
This CMake file builds the Flow tutorial and exercise executables used by FoundationDB documentation/tutorial code. It wires six `.actor.cpp` sources into standalone binaries and links each against `fdbclient`.

## Important APIs, Types, and Functions
The important build API is `add_flow_target(EXECUTABLE ...)`, which runs the Flow actor compiler integration for actor sources. Targets are `tutorial`, `print_in_order`, `make_h2o`, `dining_philosophers`, `play`, and `play_network`. Each target uses `target_link_libraries(... PUBLIC fdbclient)`.

## Control Flow
CMake defines a source variable for each executable, invokes `add_flow_target`, then links the resulting target. There is no conditional logic. Build ordering and generated-source handling are delegated to the project-level `add_flow_target` macro/function.

## State and Persistence Behavior
The file contributes build-system state only. It does not create install rules or tests. Generated actor compiler outputs and executable artifacts are produced in the build tree by the broader FoundationDB build system.

## Dependencies and Integration Points
It depends on FoundationDB's CMake helpers and on the `fdbclient` target. It integrates with documentation tutorial sources that include `flow/actorcompiler.h`, use Flow runtime globals, and require actor compilation rather than plain C++ compilation.

## Risks
If `add_flow_target` behavior changes, all tutorial binaries can fail together. Because all targets link `fdbclient`, even examples that only use Flow primitives inherit the larger client dependency. There are no tests attached here, so breakage may only surface in full build or manual tutorial runs.

## Test Signals
Build the six targets and run simple smoke tests: `play`, `print_in_order`, selected `tutorial` actors, and client/server examples for `play_network` or `dining_philosophers`. CI coverage depends on whether the documentation tutorial targets are included in normal builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/dining_philosophers.actor.cpp -->
# sources/storage-engines/foundationdb/documentation/tutorial/dining_philosophers.actor.cpp

## Purpose
This tutorial program demonstrates a distributed Flow actor solution to the Dining Philosophers problem. It models forks as resources owned by a network server and philosophers as clients that request, wait for, use, and release two forks before eating.

## Important APIs, Types, and Functions
`DPServerInterface` exposes `getInterface`, `getFork`, and `releaseFork` request streams. Request/response payloads include `GetInterfaceRequest`, `ForkState`, `GetForkRequest`, and `ReleaseForkRequest`, all with Flow serialization and file identifiers. `dpClient()` runs philosopher behavior. `dpServerLoop()` owns fork state and pending requests. `main()` parses `-p portNum` for server mode or `-s serverAddress` for client mode, initializes Flow networking, binds when serving, and runs either server or five clients.

## Control Flow
Clients obtain the server interface from a well-known endpoint, choose fork order, then loop forever: request first fork, request second fork, eat for a randomized delay, release both forks, wait, and repeat. Deadlock avoidance is implemented by asymmetric acquisition order: odd philosophers request left then right, even philosophers request right then left. The server loop uses `choose` over interface, get, and release request streams. It grants available forks immediately, stores one pending request per fork when busy, and on release either acknowledges the release or transfers ownership to the pending requester before replying.

## State and Persistence Behavior
All state is in memory. Server state consists of `forkOwners` mapping fork number to owner id and `pending` mapping fork number to a pending `GetForkRequest`. Client state tracks selected forks, request objects, randomized delays, and meal counts. There is no durable storage or FoundationDB transaction use despite linking with `fdbclient`.

## Dependencies and Integration Points
The file depends on Flow actors, `RequestStream`, `ReplyPromise`, `Endpoint::wellKnown`, `FlowTransport`, `NetworkAddress`, deterministic randomness, `fmt`, and the actor compiler. It integrates with the tutorial CMake target `dining_philosophers` and with Flow network runtime initialization through `platformInit()`, `newNet2()`, and `FlowTransport::createInstance()`.

## Risks
The protocol assumes at most one pending waiter per fork and asserts if a second pending request appears. That holds for the fixed five-philosopher problem but is not a general resource scheduler. The server has no fairness queue, cancellation cleanup, or client disconnect handling for pending requests. `CAUSE_DEADLOCK` is a local bool for demonstration, not a runtime option. Infinite loops mean manual termination is expected. Release error cases log without replying in some invalid ownership paths, which can leave a bad client blocked.

## Test Signals
Run a server and client set locally and confirm repeated eating/release logs with no deadlock when `CAUSE_DEADLOCK` is false. Flip the flag for manual deadlock demonstration. Build tests should ensure actor serialization compiles. Runtime tests can verify that all five philosophers make progress over a time window and that bind failures return exit code 2.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/dining_philosophers.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/make_h2o.actor.cpp -->
# sources/storage-engines/foundationdb/documentation/tutorial/make_h2o.actor.cpp

## Purpose
This tutorial program demonstrates Flow actor synchronization through a solution to the "Building H2O" concurrency exercise. Hydrogen actors wait on promises, oxygen actors consume two waiting hydrogen ids, and the orchestrator creates balanced batches.

## Important APIs, Types, and Functions
Global state includes `h_seqno`, `o_seqno`, `h_queue`, and `wakeup`, mapping hydrogen ids to promise pointers. `hydrogen(AsyncTrigger*)` registers itself, pushes its id, triggers readiness, and waits for an oxygen id. `oxygen(AsyncTrigger*)` waits on the trigger, consumes queued hydrogens, sends its id through their promises, and returns after binding two hydrogens. `orchestrate()` creates randomized batches, balances H/O counts to a 2:1 ratio, triggers wakeups, waits for all actors, and repeats. `main()` initializes the Flow network and runs `orchestrate()`.

## Control Flow
The orchestrator randomly starts hydrogen or oxygen actors until a batch size threshold is reached. It then adds whichever actor type is needed to satisfy `h_threads == 2 * o_threads`, triggers the hydrogen-ready signal, and waits for every actor in the batch. Hydrogen actors block on their private future. Oxygen actors wake when the trigger fires and drain `h_queue` until they have bound two hydrogens.

## State and Persistence Behavior
All state is process-local and transient. Promise pointers stored in `wakeup` point to actor-local `Promise<int>` state and must be erased before the actor returns. `h_queue` and `wakeup` should be empty between balanced batches. There is no external persistence.

## Dependencies and Integration Points
The file uses Flow actors, `AsyncTrigger`, `Promise`, `Future`, `waitForAll`, deterministic randomness, `fmt`, and Flow network initialization. It is built by the tutorial CMake target `make_h2o` and linked with `fdbclient`.

## Risks
The code is intentionally educational and notes possible non-idiomatic behavior. It uses global mutable containers and stores raw pointers to actor-local promises, which is safe only if the actors remain alive until erased. Trigger semantics can create stop-and-go behavior; the comments acknowledge potential deadlocks if the final trigger/wait is removed or misused. Large batch counts make failures expensive to debug. The loop has no cancellation handling.

## Test Signals
A smoke run should finish without assertions, with `wakeup.size()` returning to zero after each batch. Smaller batch settings are useful for debugging. Build coverage validates actor compiler integration. Runtime assertions check duplicate hydrogen ids and exact 2:1 H/O batch balance.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/make_h2o.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/play.actor.cpp -->
# sources/storage-engines/foundationdb/documentation/tutorial/play.actor.cpp

## Purpose
This file is a minimal Flow actor playground. It gives developers a boilerplate executable for experimenting with Flow code without adding permanent tutorial logic.

## Important APIs, Types, and Functions
The only actor is `foo()`, which logs entry, waits one second with `delay(1)`, logs exit, and returns `Void`. `main()` calls `platformInit()`, creates a Flow network with `newNet2(TLSConfig(), false, true)`, schedules `foo()`, wraps `waitForAll` with `stopAfter`, and runs `g_network`.

## Control Flow
Program startup initializes platform and network state, creates a vector of futures, starts `foo()`, and enters the Flow event loop. When `foo()` completes, `waitForAll(all)` becomes ready, `stopAfter()` stops the network, and `g_network->run()` returns.

## State and Persistence Behavior
The file has no persistent state. Runtime state is limited to the global Flow network pointer and the future vector in `main()`. No database or filesystem operations are performed.

## Dependencies and Integration Points
It includes Flow runtime headers, `NativeAPI.actor.h`, `Arena`, platform/TLS headers, and the actor compiler. It is built as the `play` tutorial target and links against `fdbclient`, mostly to match tutorial boilerplate.

## Risks
The program is intentionally a template. Its main risk is being used as scratch space and accidentally committed with experimental code. It does not parse arguments or handle errors. Because it initializes the network, it must follow Flow runtime expectations even though the example actor is trivial.

## Test Signals
Build and run the `play` target. Expected output is `foo enter`, a delay, then `foo exit`, followed by clean process termination.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/play.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/play_network.actor.cpp -->
# sources/storage-engines/foundationdb/documentation/tutorial/play_network.actor.cpp

## Purpose
This file is a minimal client/server Flow network playground. It demonstrates well-known endpoints, request streams, reply promises, serialization, command-line mode selection, and network transport binding with a simple reverse-string service.

## Important APIs, Types, and Functions
`PlayServerInterface` exposes `getInterface` and `play` streams. `GetInterfaceRequest` returns the interface, and `PlayRequest` carries a string `msg` plus a `ReplyPromise<std::string>`. The `server()` actor handles interface requests and play requests. The `client()` actor resolves the server endpoint, sends `"Hello World"`, and prints the reversed response. `actors` maps `serverActor` and `clientActor` names to actor factories. `main()` parses `-s port` for server mode and `-c address` for client mode.

## Control Flow
The server creates a well-known endpoint and loops over request streams. The client constructs a request stream to `serverAddress`, fetches the interface, sends a `PlayRequest`, waits for the response, and returns. `main()` initializes Flow networking, creates `FlowTransport` as server or client, binds the server address when needed, starts requested actors, and stops after all selected actors complete.

## State and Persistence Behavior
State is transient. The server holds only its interface object, and the client holds the resolved interface and request/response strings. There is no durable storage.

## Dependencies and Integration Points
The file depends on Flow networking primitives, `RequestStream`, `ReplyPromise`, `Endpoint::wellKnown`, `FlowTransport`, `NetworkAddress`, TLS config, and actor compiler output. It integrates with the `play_network` tutorial target.

## Risks
There is a command-line parsing bug: actor names are only looked up in the `else` branch that currently calls `assert(false)`, so normal documented invocations with `-s 6666 serverActor` or `-c addr clientActor` will assert when processing the actor name in debug builds. Error messages for missing `-s`/`-c` arguments mention the opposite flag in places. The program is a template and lacks robust usage output. Server actors loop forever, so `waitForAll` never completes in server mode without external termination.

## Test Signals
Build the target and run documented server/client commands. A useful regression test should verify command-line actor selection works, the client receives `dlroW olleH`, and server bind failures are reported. Current parsing should be reviewed before treating the usage block as reliable.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/play_network.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/print_in_order.actor.cpp -->
# sources/storage-engines/foundationdb/documentation/tutorial/print_in_order.actor.cpp

## Purpose
This tutorial file demonstrates ordering asynchronous Flow actors for the "Print in Order" concurrency exercise. It launches three actors with randomized delays but uses promises and waits to force output order.

## Important APIs, Types, and Functions
`print_msg_when_ready(Future<Void> ready, std::string msg)` waits a random delay, then waits on a readiness future before printing. `orchestrate()` creates three promises/futures, starts three print actors, sends each promise only after the previous actor finishes, and returns. `main()` initializes the Flow network, schedules `orchestrate()`, and stops after it completes.

## Control Flow
All three print actors start immediately and sleep for random durations. They cannot print until their associated readiness future is fulfilled. The orchestrator sends `p_first`, waits for `first`, then sends `p_second`, waits for `second`, then sends `p_third` and waits for `third`. This serializes observable output regardless of initial random delays.

## State and Persistence Behavior
State is local to actors: promises, futures, random delay values, and strings. No data is persisted externally.

## Dependencies and Integration Points
The file uses Flow `Promise`, `Future`, `delay`, `waitForAll`, deterministic randomness, platform/TLS initialization, and actor compiler support. It is wired by the tutorial CMake target `print_in_order`.

## Risks
This is didactic code and not a reusable synchronization library. If promises are sent in parallel, as the commented block shows, output order becomes nondeterministic. The final `wait(delay(0.1))` is cosmetic and can affect timing-sensitive tests. Several includes are inherited from broader tutorial boilerplate and are not strictly needed.

## Test Signals
Run the target repeatedly with different deterministic random seeds if supported; output should always be `First`, `Second`, `Third` in that order. Build validation ensures Flow actor syntax remains compatible.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/print_in_order.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/tutorial.actor.cpp -->
# sources/storage-engines/foundationdb/documentation/tutorial/tutorial.actor.cpp

## Purpose
This is the main Flow tutorial executable. It demonstrates timers, futures, promises, triggers, network request/reply interfaces, streaming replies, an in-memory key-value service, multiple concurrent clients, and simple real FoundationDB range workloads selected by command-line actor names.

## Important APIs, Types, and Functions
Flow primitive examples include `simpleTimer()`, `someFuture()`, `promiseDemo()`, `eventLoop()`, and `triggerDemo()`. Network examples define `EchoServerInterface`, `EchoRequest`, `ReverseRequest`, `StreamRequest`, `StreamReply`, `echoServer()`, and `echoClient()`. The toy KV service defines `SimpleKeyValueStoreInterface`, `GetKVInterface`, `GetRequest`, `SetRequest`, `ClearRequest`, `kvStoreServer()`, `connect()`, `kvSimpleClient()`, `kvClient()`, `throughputMeasurement()`, and `multipleClients()`. FDB examples include `logThroughput()`, `fdbClientStream()`, `fdbClientGetRange()`, and `fdbClient()`. `actors` maps command names to actor factories.

## Control Flow
`main()` parses `-p` for server port, `-s` for server address, `-C` for cluster file, and actor names. It initializes the platform, Flow network, and `FlowTransport`; binds in server mode; starts all selected actors; then stops when all selected futures complete. Individual actors demonstrate Flow control patterns: `choose` races delay and future readiness, triggers wake event loops, servers loop over request streams, streaming replies enforce byte limits and end with `end_of_stream`, and FDB workloads retry through `tx.onError(e)`.

## State and Persistence Behavior
Most examples are in-memory and transient. `kvStoreServer()` stores keys in a process-local `std::map`. `multipleClients()` shares an operation counter through `std::shared_ptr<uint64_t>`. FDB examples persist mutations to the database referenced by `clusterFile`, using keys under `"/tut/"` in `fdbClient()`. Range readers keep `next` keys and byte counters in actor state. Network interfaces are serialized over Flow transport but not durable.

## Dependencies and Integration Points
The file depends heavily on Flow actors, Flow transport, request streams, reply promises, reply promise streams, deterministic randomness, FoundationDB native API types (`Database`, `Transaction`, `Key`, `RangeResult`, `KeySelector`, `normalKeys`), `CLIENT_KNOBS`, `fmt`, and actor compiler output. It integrates with the `tutorial` CMake target and the local `fdb.cluster` default unless `-C` is provided.

## Risks
The tutorial intentionally favors demonstration over production robustness. Several actors loop forever, so selected combinations may not terminate. The toy KV store is single-process, has no persistence, and returns `io_error` for missing keys. `kvClient()` clears lexicographic string ranges, so numeric string ordering may surprise readers. `fdbClient()` writes real data under `/tut/` after a 30-second delay and should not be run against an important cluster without understanding the workload. Streaming and request payload comments note undocumented constraints around `ReplyPromise` types and field names. Command-line parsing does not require at least one actor, so an empty invocation exits after starting no work.

## Test Signals
Smoke tests should run finite actors such as `promiseDemo`, `triggerDemo`, `echoClient` against `echoServer`, and `kvSimpleClient` against `kvStoreServer`. FDB-specific actors require a valid cluster file and should be isolated. Build coverage must include actor compiler generation and serialization file identifiers. Runtime tests can assert echo/reverse output, stream sequence ordering, and KV set/get behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/documentation/tutorial/tutorial.actor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdb.cluster.cmake -->
# sources/storage-engines/foundationdb/fdb.cluster.cmake

## Purpose
This is a CMake-configured template for a local FoundationDB cluster file. It renders a connection string using the configured cluster description and a loopback coordinator at port 4000.

## Important APIs, Types, and Functions
The only content is `${CLUSTER_DESCRIPTION1}:${CLUSTER_DESCRIPTION1}@127.0.0.1:4000`. In FoundationDB cluster file terms, this corresponds to `description:id@coordinator`.

## Control Flow
There is no executable control flow. CMake substitutes `CLUSTER_DESCRIPTION1` during configuration to create an actual `fdb.cluster`-style file.

## State and Persistence Behavior
The rendered file is persistent configuration consumed by FoundationDB clients and tools. It identifies the expected cluster id/description and coordinator address. Changing the rendered value changes what local cluster clients connect to.

## Dependencies and Integration Points
It depends on CMake variable substitution and FoundationDB client cluster-file parsing. It integrates with local development/test clusters that listen on `127.0.0.1:4000`, including tutorial programs whose default `clusterFile` is `fdb.cluster`.

## Risks
This template is only suitable for local single-machine development defaults. If copied into production, it points all clients to loopback and has a placeholder-like description/id. The coordinator address and cluster id must match the actual cluster connection string.

## Test Signals
Configuration tests should verify the generated cluster file contains no unsubstituted `${...}` placeholders. Runtime smoke tests can open a local FoundationDB database using the generated file when a matching local cluster is running.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdb.cluster.cmake -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/CMakeLists.txt -->
# sources/storage-engines/foundationdb/fdbbackup/CMakeLists.txt

## Purpose
This CMake file defines backup-related executables and tests: `fdbbackup`, `fdbconvert`, `fdbdecode`, renamed/symlinked client tools, unit-style test binaries, and shell integration tests for backup/restore flows.

## Important APIs, Types, and Functions
Targets are built with `add_flow_target`. `fdbbackup` uses `Decode.cpp` and `backup.cpp`; `fdbconvert` uses `FileConverter.cpp`; `fdbdecode` uses `Decode.cpp` and `FileDecoder.cpp`. All include `fdbbackup/include` and link `fdbclient`. Install rules install or package `fdbbackup` and expose it under names `backup_agent`, `fdbrestore`, `dr_agent`, and `fdbdr`. Test targets include `backup_tests` with `EXCLUDE_MAIN_FUNCTION=1` and `fdbdecode_tests` with `EXCLUDE_MAIN_FUNCTION=1`. Shell tests include directory backup, blob backup restore, and S3 bulk dump/load.

## Control Flow
CMake first declares source lists and executable targets. Under `NOT OPEN_FOR_IDE`, it adds install behavior, symlinks, test executables, and CTest entries. Debug package generation chooses whether installs use target files or stripped package binaries. Optional `GPERFTOOLS_FOUND` adds compile definitions and linkage. Non-Windows non-IDE builds enable tests and attach sanitizer environment settings to shell tests.

## State and Persistence Behavior
The file creates build-system state, install artifacts, symlinks, and CTest registrations. It does not manipulate backup data directly. The renamed binaries all point to the same executable, so runtime behavior is likely selected by argv/tool mode inside `backup.cpp`.

## Dependencies and Integration Points
It depends on project CMake helpers (`add_flow_target`, `fdb_install`, `symlink_files`), `fdbclient`, optional gperftools, sanitizer environment variables, and shell scripts under `fdbbackup/tests`. It integrates backup tools into client packages and test suites.

## Risks
Multiple installed tool names share one binary, so packaging mistakes can break several commands. Test registration is skipped under `OPEN_FOR_IDE` and Windows shell integration tests are disabled. `fdbdecode_tests` only compiles the decoder test main, so coverage depends on `EXCLUDE_MAIN_FUNCTION` blocks. Non-debug install path depends on `strip_only_fdbbackup` and package-bin layout.

## Test Signals
Build all three executables and test targets. Run `BackupTests`, `FileDecoderTests`, `dir_backup_tests`, `blob_backup_restore_tests`, and `s3_backup_bulkdump_bulkload_tests` where environment credentials and platform support are available. Packaging validation should inspect installed aliases and symlinks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/Decode.cpp -->
# sources/storage-engines/foundationdb/fdbbackup/Decode.cpp

## Purpose
This file implements `decode_hex_string`, a utility used by backup decoder tooling to turn escaped ASCII/hex key prefix strings into binary strings for filtering.

## Important APIs, Types, and Functions
`std::string decode_hex_string(std::string line, bool& err)` accepts an input such as `\x15\x1b` and returns decoded bytes. It recognizes escaped `"`, `\`, space, and `;` by removing the backslash. It recognizes `\xNN` sequences by parsing two hex digits with `strtoul` and replacing the four-character escape with the decoded byte. It reports invalid syntax to `std::cerr`, sets `err = true`, and returns the current partial result.

## Control Flow
The function scans `line` with index `i`. On backslash, it validates that a following escape exists, then handles simple escapes or `\x` escapes. On normal characters, it advances. Edits are performed in place on `line`, so decoded bytes replace textual escapes as scanning proceeds. At the end it returns `line.substr(0, i)`.

## State and Persistence Behavior
There is no persistent state. The caller owns the `err` flag and should initialize or inspect it. Diagnostic output goes to stderr.

## Dependencies and Integration Points
The function is declared in `fdbbackup/Decode.h` and used by `FileDecoder.cpp` for `--hex-prefix` and prefix-filter files. It depends on C string parsing through `strtoul` and standard library strings/iostream.

## Risks
The loop condition is `while (i <= line.length())`, so it can read `line[i]` at `i == length`; this relies on `std::string` null terminator behavior and is brittle. Bounds checks use `>` rather than `>=` around escape lengths, so edge cases deserve scrutiny. `err` is only set on failure and not cleared on success. The parser accepts unescaped normal characters even though comments say this is not recommended. In-place mutation while scanning can make reasoning about indices difficult.

## Test Signals
Tests should cover valid hex, escaped separators (`\;`), escaped backslashes/quotes/spaces, invalid short escapes, non-hex digits, empty input, plain text, and multiple prefixes through `FileDecoder` parsing. Sanitizer runs are useful because of boundary-sensitive indexing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/Decode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/FileConverter.cpp -->
# sources/storage-engines/foundationdb/fdbbackup/FileConverter.cpp

## Purpose
`FileConverter.cpp` implements the `fdbconvert` tool, which reads partitioned backup mutation log files from a backup container over a version range and writes a converted log file in the older backup log format. It is a migration/debug utility for backup file formats.

## Important APIs, Types, and Functions
CLI helpers are `printConvertUsage()`, `printBuildInformation()`, `parseCommandLine()`, and `ConvertParams`. Log selection is handled by `getRelevantLogFiles()`. `VersionedData` stores a `LogMessageVersion`, serialized mutation bytes, and the backing arena. `MutationFilesReadProgress` coordinates reading multiple log files and exposes `openLogFiles()` and `getNextMutation()`. Nested `FileProgress` tracks one file's descriptor, offset, EOF state, and buffered mutations, with `decodeBlock()` parsing `PARTITIONED_MLOG_VERSION` blocks. `LogFileWriter` writes old-format mutation log key/value blocks with `getBlockKey()`, `writeKV()`, and `addMutation()`. The main async flow is `convert(ConvertParams)`.

## Control Flow
`main()` parses options, enables trace options, initializes platform/network, and runs `stopAfter(convert(param))`. `convert()` opens the backup container, lists and describes backup files, filters relevant logs by version, opens all files, decodes until the begin version is reached, then repeatedly selects the next mutation across all files by `LogMessageVersion`. Mutations are grouped by commit version into a `MutationList`; when the version changes, the accumulated list is written to the output log file. At the end, the output file is finished.

## State and Persistence Behavior
Read progress is in memory: each file has an offset, EOF flag, and buffered decoded mutations. Output persistence is a new backup log file written through `IBackupContainer::writeLogFile(begin, end, blockSize)`. `LogFileWriter` maintains block boundaries and pads old-format blocks with `0xFF` data when needed. No FoundationDB database transactions are used; all persistence is in the backup container.

## Dependencies and Integration Points
The converter depends on backup container abstractions, `BackupAgent`, `MutationList`, Flow async file APIs, serialization helpers, client knobs, trace logging, and command-line option definitions from `FileConverter.h`. It integrates with `fdbbackup/CMakeLists.txt` as the `fdbconvert` target and with backup file formats described in backup documentation and writer code.

## Risks
The conversion assumes input files are well-formed partitioned mutation logs with compatible protocol serialization. Corrupt blocks throw restore errors. `getRelevantLogFiles()` duplicate removal compares adjacent sorted files and may not handle all overlap patterns. The code reads block-by-block but buffers mutations and opens all selected files, so large ranges with many files can consume memory and descriptors. It prints every mutation to stdout, which can be expensive and leak sensitive key/value structure. CLI `--build-flags` and `--help` return an error status by design, which may surprise scripts.

## Test Signals
Tests should construct backup containers with partitioned logs spanning multiple versions and parts, duplicated/subset files, corrupt blocks, and boundary versions. Validate that output old-format files can be decoded/restored, that begin/end filters are exclusive/inclusive as intended, and that trace/log options work. Build and run the `fdbconvert` target against small file-system containers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/FileConverter.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/FileDecoder.cpp -->
# sources/storage-engines/foundationdb/fdbbackup/FileDecoder.cpp

## Purpose
`FileDecoder.cpp` implements the `fdbdecode` tool for inspecting FoundationDB backup mutation logs and range files. It can list files, decode log mutations, decode range key/value files, filter by file name, key prefix, and version range, save downloaded files locally, configure TLS/blob credentials, adjust knobs, and handle encrypted backup containers.

## Important APIs, Types, and Functions
CLI and configuration are centered on `DecodeParams`, `printDecodeUsage()`, `parseDecodeCommandLine()`, `parsePrefixesLine()`, and `parsePrefixFile()`. Filtering APIs include `DecodeParams::overlap()`, `validVersionFilters()`, `updateRangeMap()`, and `matchFilters()` overloads for mutations, ranges, and key-values. `DecodeProgress` loads and decodes one mutation log file, grouping chunks by version until complete `VersionedMutations` batches are available. `DecodeRangeProgress` loads and decodes range files into key/value blocks. Output helpers include `hexStringRef()`, `process_file()`, and `process_range_file()`. `getRangeFiles()` uses snapshot metadata for range-file selection. `decode_logs()` orchestrates container opening, listing, filtering, and sequential processing.

## Control Flow
`main()` parses options, updates filters, validates version filters, configures tracing and TLS, initializes platform/network, applies knob overrides after network setup, opens trace files/blob credentials, then runs `decode_logs()`. The orchestrator opens the backup container, dumps file lists, removes partitioned logs under `plogs/`, describes the backup, sets encryption block size, filters log/range files, optionally returns for list-only mode, then processes selected log files followed by selected range files. Log processing reads a file into memory, decodes blocks into mutation chunks, emits complete versions, filters mutations, and prints matching mutation records. Range processing decodes blocks and prints matching key/value pairs.

## State and Persistence Behavior
Most state is transient and in memory. `DecodeProgress` stores decoded blocks and `mutationBlocksByVersion`, which can hold incomplete version chunks until all parts arrive. `DecodeRangeProgress` stores decoded range blocks. Optional `--save` persists downloaded backup files to local paths matching their container names, creating directories as needed and writing with mode `0600`. Trace logs are written when logging is enabled. The tool never writes to the source database.

## Dependencies and Integration Points
The decoder depends on backup container implementations, filesystem backup containers for keyspace snapshot metadata, backup TLS configuration, encryption key file support, Flow async runtime, trace logging, mutation/range decoding helpers from `fileBackup`, system data helpers, client knobs, command-line option definitions, and `decode_hex_string()` from `Decode.cpp`. It is built as `fdbdecode`; with `EXCLUDE_MAIN_FUNCTION=1`, it builds a small test main for version-filter validation.

## Risks
The tool reads each selected file fully into memory, so very large backup files can cause high memory usage. `getRangeFiles()` uses `dynamic_cast<BackupContainerFileSystem*>` without a null check, so range decoding appears filesystem-container-specific despite the generic container URL. Saving files locally uses container filenames as local paths, which can create nested directories and overwrite local files. Default `log_enabled` is true, so decode sessions create trace output unless changed by option defaults elsewhere. Prefix parsing inherits `decode_hex_string()` boundary risks. Filtering correctness is important because missed clear ranges or prefix intersections can mislead operators; `--validate-filters` helps assert RangeMap behavior but is slower.

## Test Signals
`FileDecoderTests` currently validates `validVersionFilters()` for defaults and begin/end order. Broader tests should cover CLI parsing, prefix parsing, log and range decoding against known backup fixtures, list-only mode, begin/end version filtering, prefix filtering for single-key and clear-range mutations, `--save` behavior, encrypted containers, TLS/blob credential setup, corrupt file handling, and filesystem vs non-filesystem range-file behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbbackup/FileDecoder.cpp -->
