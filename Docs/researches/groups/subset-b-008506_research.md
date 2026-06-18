# subset-b-008506 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/task_priority_support.swift -->
# sources/storage-engines/foundationdb/flow/task_priority_support.swift

Purpose: This Swift interop helper maps FoundationDB `Flow.TaskPriority` values into Swift `_Concurrency.TaskPriority` values and back to Flow/net2 priorities. It exists because Swift task priorities are byte-sized raw values while Flow priorities are the authoritative scheduler constants used by the C++ runtime.

Important APIs and types: The key API is `Flow.TaskPriority.asSwift`, backed by private `Repr: UInt8`; the `_Concurrency.TaskPriority` extension exposes static properties for each Flow priority, `rawValueNet2`, `name`, and `flowDescription`. The switch bodies enumerate scheduler priorities from `Max`, `RunLoop`, and IO/socket priorities through proxy, TLog, blob worker, restore, low, and zero priorities.

Control flow: Conversion is table-driven through exhaustive switch statements. A Flow priority becomes the corresponding byte `Repr` value for Swift scheduling; a Swift priority is matched against the static properties to recover the Flow raw value or display name. Unknown Flow enum cases and unknown Swift raw values fail fast with `fatalError` or render as `<unknown:...>` for names.

State and persistence behavior: There is no persisted state. Runtime state is only the raw priority value carried by Swift tasks. The private `Repr` enum is an ABI-adjacent compatibility table: changing it must stay synchronized with the C++/Swift bridge functions referenced in comments.

Dependencies and integration points: It imports `Flow` and integrates Swift concurrency tasks with Flow's net2 scheduler priority ordering. Callers can use `.DefaultEndpoint`, `.DiskRead`, `.LowPriorityRead`, and related properties in Swift code while preserving Flow's scheduling semantics when jobs are enqueued into the C++ runtime.

Risks: The main risk is drift between `Repr`, `Flow.TaskPriority`, and bridge functions such as `swift_priority_to_flow`/`swift_priority_to_net2`. `DefaultEndpoint` intentionally overlaps with Swift predefined priorities, so accidental use of generic Swift priorities can produce fatal errors in `rawValueNet2`. Tests should verify round-trip mappings for every priority, exact raw Flow values, unknown-value behavior, and scheduler ordering expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/task_priority_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/test_memcpy.cpp -->
# sources/storage-engines/foundationdb/flow/test_memcpy.cpp

Purpose: This Flow unit test validates the active `memcpy` implementation, including FoundationDB's included `rte_memcpy.h` and optionally `folly_memcpy.h`, across many sizes and source/destination alignments. It is a correctness guard for optimized memory-copy code used in performance-sensitive paths.

Important APIs and functions: `test_single_memcpy(off_src, off_dst, size)` fills aligned stack buffers with deterministic random data, calls `memcpy`, and verifies the return pointer plus copied and untouched regions. The `TEST_CASE("/rte/memcpy")` Flow unit test iterates all offsets from `0` to `31` and a fixed set of packet-like buffer sizes up to `8192`.

Control flow: For each alignment pair and size, the test initializes `src` and zeroes `dest`, performs the copy, checks bytes before the destination offset, checks each copied byte, and checks bytes after the copy range. Any mismatch prints a detailed failure and returns `-1`; the unit test asserts success.

State and persistence behavior: There is no persistent state. Runtime data is stack-allocated `uint8_t` buffers sized by `SMALL_BUFFER_SIZE + ALIGNMENT_UNIT`; randomness comes from Flow's deterministic random generator so failures are reproducible.

Dependencies and integration points: The file depends on Flow's unit-test framework, deterministic random support, and the chosen compile-time memcpy headers. It can be forced into the binary through `forceLinkMemcpyTests()`, which matters when unit-test registration depends on link inclusion.

Risks: The test checks non-overlapping copies only and does not validate `memmove` semantics. The post-copy bounds check assumes the configured largest buffer size is no larger than `SMALL_BUFFER_SIZE`; changing `TEST_VALUE_RANGE` or the size list must keep that invariant. Test signals are exact byte comparisons for all size/alignment combinations and the returned pointer contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/test_memcpy.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/trace_support.swift -->
# sources/storage-engines/foundationdb/flow/trace_support.swift

Purpose: This Swift wrapper provides a fluent API around C++ `Flow.TraceEvent` for Swift code. It lets callers write chained `.detail(...)` calls without relying on mutating Swift value semantics for a C++ type that mutates internally.

Important APIs and types: `STraceEvent` is a `final class` with `event: Flow.TraceEvent`, static `make(_:_:)`, and overloads of `detail` for `OptionalStdString`, `std.string`, `Float`, `Double`, `Int`, `OptionalInt64`, `UInt32`, `Int32`, `Int64`, and `UInt64`. The private `keepAlive: [std.string]` stores copied detail names and event types.

Control flow: Initialization copies the event type into `keepAlive` and constructs the C++ trace event from its unsafe C string plus `Flow.UID`. Each detail overload appends the detail key to `keepAlive`, calls the concrete C++ `addDetail` template overload, and returns `self` for chaining.

State and persistence behavior: There is no persistent state; the important runtime state is ownership of `std.string` values whose C pointers are passed into C++ code. The wrapper's lifetime must cover the trace-event mutation path so detail names remain valid.

Dependencies and integration points: It imports `Flow` and bridges Swift code to C++ tracing. The overload list works around Swift/C++ interop limitations around generic template expansion; unsupported mappings such as `Int8` are left commented out.

Risks: Lifetime bugs are possible if `Flow.TraceEvent` stores pointers longer than the wrapper's `keepAlive`. Type coverage must be expanded manually for new detail types. Tests should emit trace events from Swift, verify details appear with correct values, exercise optional values, and check that chaining and discardable `make` usage both compile and run.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/trace_support.swift -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/version.cpp -->
# sources/storage-engines/foundationdb/flow/version.cpp

Purpose: This generated-source companion exposes the build source version string through a stable C++ function. It is a tiny linkage point used by Flow/FoundationDB binaries to report the exact source revision.

Important APIs and functions: `getSourceVersion()` returns the `sourceVersion` symbol included from generated `flow/SourceVersion.h`. It includes `flow/GetSourceVersion.h` for the function declaration.

Control flow: The function is a direct constant return with no branching. Build generation is responsible for populating `SourceVersion.h` before compilation.

State and persistence behavior: There is no runtime state or persistence. The source version is compiled into the binary as static data.

Dependencies and integration points: It integrates build metadata generation with runtime status/version reporting. Any component linked against Flow can call `getSourceVersion()` without depending on the generated header directly.

Risks: If the generated header is stale or missing, binaries will report wrong metadata or fail to build. Tests should check that packaged binaries expose the expected commit/source version and that generated source-version files are refreshed during build stamping.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/version.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/xxhash.c -->
# sources/storage-engines/foundationdb/flow/xxhash.c

Purpose: This C file instantiates the xxHash implementation used by Flow by defining the implementation macros before including `flow/xxhash.h`. It provides the compiled function bodies for xxHash's header-defined algorithms.

Important APIs and types: The file enables `XXH_STATIC_LINKING_ONLY` for advanced declarations and `XXH_IMPLEMENTATION` for definitions, then includes `flow/xxhash.h`. The exported surface is determined by that header, not by this file.

Control flow: There is no local control flow beyond preprocessing. Compilation of this translation unit materializes the hashing functions for the rest of the binary.

State and persistence behavior: Hashing state is managed by xxHash functions and caller-provided state objects; this file stores no persistent state. The behavior must remain deterministic across supported platforms for checksums and hash-table uses.

Dependencies and integration points: It vendors Yann Collet's xxHash under BSD terms into the Flow build. It is linked wherever Flow needs fast non-cryptographic hashing.

Risks: Macro configuration drift can accidentally hide advanced APIs or duplicate definitions if another translation unit also defines `XXH_IMPLEMENTATION`. Tests should cover known xxHash vectors, static/dynamic linking modes, and any Flow code that persists or compares xxHash outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/xxhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/bulkload/bulk.py -->
# sources/storage-engines/foundationdb/layers/bulkload/bulk.py

Purpose: This Python 2 layer demonstrates a concurrent bulk-loading framework for moving external CSV, JSON, or blob data into FoundationDB key-value, SimpleDoc, or Blob-layer representations. It explicitly assumes the import has no atomicity or isolation requirement across the entire dataset.

Important APIs and types: `Subspace` wraps tuple prefixes; `BulkLoader` subclasses `gevent.queue.Queue` and defines `reader`, `writer`, and `produce_and_consume`. Reader classes are `ReadCSV`, `ReadJSON`, and `ReadBlob`; writer classes are `WriteKVP`, `WriteDoc`, and `WriteBlob`; combined classes include `CSVtoKVP`, `JSONtoDoc`, and `BlobToBlob`.

Control flow: Producers iterate `reader()` and enqueue transaction-sized data units while consumers dequeue and call transactional `writer` methods against the module-level gevent FDB database. CSV readers stream rows from matching files, JSON readers load one object per file with optional Unicode/number conversion, and blob readers yield `(offset, chunk)` pairs. Writers clear optional destinations, then write tuple-packed keys, SimpleDoc document updates, or blob chunks.

State and persistence behavior: Persistent state lives in FDB subspaces, SimpleDoc documents, and Blob-layer byte ranges. Queue state is in-memory and bounded by the consumer count to provide backpressure. Clearing is destructive for the configured destination subspace/document/blob.

Dependencies and integration points: The file uses `fdb.api_version(22)`, `fdb.open(event_model="gevent")`, `gevent`, `csv`, `json`, `blob`, and `simpledoc`. It is an example layer rather than a modern production loader.

Risks: It is Python 2 code (`print`, `xrange`, `unicode`, `iteritems`) and uses old API-version conventions. `WriteDoc.writer` calls `_writer_doc(db, ...)` rather than using the passed transaction, so composition expectations differ from plain `@fdb.transactional` methods. Tests should use temporary subspaces, verify row/chunk counts, clear behavior, JSON conversion, SimpleDoc array rejection, and gevent concurrency under retryable FDB errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/bulkload/bulk.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/compressedColumn/compressedColumn.py -->
# sources/storage-engines/foundationdb/layers/compressedColumn/compressedColumn.py

Purpose: This layer stores a logical column in FoundationDB while compacting adjacent rows into packed chunks. It supports point reads, streaming iteration, and a non-fully-transactional packing pass that merges unpacked rows with existing packed segments.

Important APIs and types: `Column` exposes `setRow`, `getRow`, `delete`, `getColumnStream`, and `pack`. Helper classes `_PackedData`, `_MergedData`, and `_ColumnStream` handle packed serialization, merge cursors, and streaming reads. Keys are tuple-encoded as `(columnName, "unpacked", row)` or `(columnName, "packed", startRow, endRow)`.

Control flow: Point reads first check the unpacked key, then locate the packed segment whose range covers the requested row. `pack` repeatedly opens a transaction, reads batches of unpacked rows, loads overlapping packed data, merges sorted packed/unpacked rows, deletes old unpacked and packed entries, and writes new packed chunks sized by `targetChunkSize`/`maxChunkSize`. `_ColumnStream` fetches packed and unpacked ranges incrementally and merges them into ordered result batches.

State and persistence behavior: Persistent state is divided between unpacked row keys and packed value blobs. `_PackedData` serializes a header of key length, value length, and body offset records followed by concatenated values. Packing is incremental and each chunk commit is independent, so a full column pack is not atomic.

Dependencies and integration points: It uses `fdb.api_version(16)`, tuple keys, `fdb.KeySelector`, `fdb.KeyValue`, and Python `struct`. It is a low-level FoundationDB data-model example that relies on lexicographic row-key ordering.

Risks: The code is Python 2-era and uses raw string byte handling. `pack` has a FIXME for `transaction_too_old` where overlapping packed blocks should be unpacked and retried, so long-running packing can leave work incomplete. Tests should cover point reads across packed/unpacked overlap, stream ordering, pack idempotence, chunk size boundaries, delete behavior, and recovery from retryable transaction errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/compressedColumn/compressedColumn.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/highcontention/queue.py -->
# sources/storage-engines/foundationdb/layers/containers/highcontention/queue.py

Purpose: This file implements a FoundationDB queue layer with an optional high-contention pop algorithm. The default mode trades isolated pop latency for better scaling when many clients pop concurrently.

Important APIs and types: `Subspace` provides tuple prefix helpers. `Queue` exposes `clear`, `push`, `pop`, `empty`, and `peek`; private helpers manage `item`, `pop`, and `conflict` subspaces. Values are tuple-packed, queue entries are keyed by `(index, randomID)`, and waiting pop requests are keyed with random IDs.

Control flow: `push` computes the next index from a snapshot read and writes an item with a random suffix. Simple pop reads and deletes the first item in one transaction. High-contention pop first registers behind existing waiters if needed, then repeatedly fulfills waiting pops in batches by moving item values to per-waiter result keys and polling its own result key with exponential backoff.

State and persistence behavior: Persistent state includes queued items, pending pop requests, and fulfilled-result keys. The `active` conflict behavior is encoded through reads of wait and item keys. Pop cannot be composed with arbitrary caller transactions because the high-contention path spans multiple transactions and polling.

Dependencies and integration points: It uses `fdb.api_version(22)`, tuple subspaces, `os.urandom`, Python `threading` examples, and FDB transaction retry semantics. Example functions demonstrate single-client and multi-client queue usage.

Risks: Random ID uniqueness depends on OS entropy. The high-contention code has a questionable exception path that calls transactional `_addConflictedPop(db, True)` after a failed manual transaction, and polling can leave result keys if clients exit. Tests should cover FIFO-ish behavior under same-index randomization, empty pop, waiter fulfillment, concurrent producers/consumers, cleanup of abandoned waits, and retry handling.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/highcontention/queue.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/set.py -->
# sources/storage-engines/foundationdb/layers/containers/set.py

Purpose: This Python 2 example implements a sorted set abstraction on FoundationDB using tuple-encoded keys. It mirrors many Python set operations while preserving ordered iteration.

Important APIs and types: `FdbSet` exposes `length`, `iterate`, `contains`, `issubset`, `issuperset`, `union`, `intersection`, `difference`, `symmetric_difference`, in-place update variants, `add`, `remove`, `discard`, `pop`, `clear`, and ordered seek helpers. `nextStopToNone` adapts generator exhaustion.

Control flow: Each set member is stored as key `(path, member)` with an empty value. Merge-style operations iterate two sorted key streams or use `first_greater_or_equal` to skip ahead. In-place operations delete ranges or individual keys while scanning intersections.

State and persistence behavior: The persisted set is the key range starting with the tuple prefix for `_path`. There is no metadata key for size, so `length` scans all members. `remove` raises `KeyError` when the key is absent, while `discard` is idempotent.

Dependencies and integration points: It uses `fdb.api_version(16)` and tuple keys. The file includes a destructive `test(db)` that clears the database and prints behavior, and it opens the default database at import-time.

Risks: The module-level `db = fdb.open(); test(db)` makes importing the file destructive. `_keyInRange` uses tuple-prefix string arithmetic and can be fragile for non-string paths. Tests should isolate a subspace, remove import-time side effects, and validate every set algebra operation, ordered seeking, empty pop, and range deletion behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/set.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/treap.py -->
# sources/storage-engines/foundationdb/layers/containers/treap.py

Purpose: This appears to be an early experimental FoundationDB treap implementation, storing binary-search-tree nodes with random priorities. It is incomplete and tied to a hard-coded cluster/database.

Important APIs and types: `FdbTreap` defines `updateNode`, `updateRoot`, `parent`, `balance`, and `setKey`. Nodes are intended to contain left child, right child, priority, metric, and value fields, encoded through older tuple helper APIs such as `fdb.tuple_to_key` and `fdb.key_to_tuple`.

Control flow: `setKey` searches neighboring keys to find an existing node or insertion parent, writes root/parent/self nodes, then calls `balance` to rotate the child upward when its random priority exceeds the parent's priority. `balance` finds the grandparent, rewires child links, persists changed nodes, and recurses upward.

State and persistence behavior: The tree root is stored at `_rootKey`, with nodes under `_path = path + '\x00'`. Node values contain structural child references plus payload. There is no delete path and no completed lookup API in this file.

Dependencies and integration points: It calls `fdb.init` and opens a specific cluster/database at import time, indicating historical API usage. It is not integrated with the newer `Subspace` helper used by other container examples.

Risks: The code uses `tuple(...)` as if it could build mutable nested structures, then mutates tuple elements, so it is likely non-runnable as written. Hard-coded cluster addresses and old API calls are major hazards. Test value is mostly archaeological; any revival would need unit tests for insertion, rotations, lookup, persistence, and Python/FDB API compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/treap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/vector.py -->
# sources/storage-engines/foundationdb/layers/containers/vector.py

Purpose: This file implements a sparse vector/array abstraction on FoundationDB. It stores only explicit values plus a sentinel value at the last index so vector size can be recovered without separate metadata.

Important APIs and types: `Subspace` provides tuple prefixing. `_ImplicitTransaction` supports `with vector.use_transaction(tr)` so array syntax can omit explicit transaction arguments. `Vector` exposes `size`, `push`, `back`, `front`, `pop`, `swap`, `get`, `get_range`, `set`, `empty`, `resize`, `clear`, `__getitem__`, and `__setitem__`.

Control flow: Public methods resolve either an explicit transaction or the thread-local implicit transaction, then call transactional private methods. `push` writes at current size, `pop` reads the last two explicit entries to preserve sparse default representation, `resize` clears or writes the last default sentinel, and `get_range` translates Python slice semantics into FDB range scans with synthesized default values.

State and persistence behavior: Values are tuple-packed under keys `(index)` within the vector subspace. Missing indices below the vector size read as `defaultValue`; the highest explicit key determines size. Thread-local implicit transaction state is process-local and restored on context exit.

Dependencies and integration points: It uses `fdb.api_version(22)`, tuple packing, `threading.local`, and FDB key selectors/range scans. The file includes destructive example/test functions.

Risks: Python iterator support is incomplete in the shown code because `_print_vector` iterates `for v in vector` without a visible `__iter__`. `_resize` calls `self.size()` from inside a transactional method without passing `tr`, relying on implicit state that may not exist. Tests should cover sparse expansion/shrink, negative and stepped ranges, swaps with default elements, pop edge cases, implicit transaction nesting, and Python 2/3 compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/containers/vector.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/ps_prompt.py -->
# sources/storage-engines/foundationdb/layers/pubsub/ps_prompt.py

Purpose: This is an interactive prompt bootstrap for manually experimenting with the pub/sub layer against a remote FoundationDB database. It imports bindings, opens a named database, and creates a `PubSub` instance.

Important APIs and types: It imports `fdb` and `PubSub` from `pubsub_bigdoc`, then exposes `db` and `ps` in an interactive Python session due to the `#!/usr/bin/python -i` shebang.

Control flow: On execution it prepends a local bindings path, opens `10.0.3.1:2181/bbc` database `TwitDB`, and constructs `ps = PubSub(db)`. There are no functions or guards.

State and persistence behavior: The script does not mutate state directly, but the exposed `ps` object can mutate the configured remote database from the prompt. The hard-coded connection string is persistent operational configuration embedded in source.

Dependencies and integration points: It depends on a `pubsub_bigdoc` module not included in this listed subset and on legacy multi-argument `fdb.open` semantics. It is a developer convenience wrapper, not a reusable library.

Risks: Running it in the wrong environment points at a hard-coded remote database. Tests are not appropriate beyond smoke-checking import/open against a test cluster; safer usage would parameterize the cluster/database and avoid import-time connection side effects.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/ps_prompt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/ps_test.py -->
# sources/storage-engines/foundationdb/layers/pubsub/ps_test.py

Purpose: This interactive Python 2 script is a manual end-to-end test for the pub/sub layer. It creates feeds and inboxes, subscribes them, posts messages, and prints feed and inbox contents.

Important APIs and types: It imports `PubSub` from `pubsub_bigdoc`, uses `fdb.api_version(14)`, opens a hard-coded cluster file/database, and calls `create_feed`, `create_inbox`, `create_subscription`, `post_message`, `print_feed_stats`, `list_inbox_messages`, and `get_feed_messages`.

Control flow: The script clears the entire database, creates three feeds and three inboxes, asserts four subscriptions, posts four messages, prints stats for each feed, lists inbox messages, and iterates messages by one feed.

State and persistence behavior: It destructively deletes all keys with `del db[:]` before seeding pub/sub state. Persistent objects include feed, inbox, subscription, and message records managed by `pubsub_bigdoc`.

Dependencies and integration points: It uses local bindings path manipulation, Python 2 print syntax, and the historical API-version 14. It is closer to a smoke/demo script than an automated test suite.

Risks: Hard-coded `/home/bbc/fdb.cluster` and full database clearing are dangerous outside an isolated test database. It references `pubsub_bigdoc`, while the current listed implementation is `pubsub.py`. Test signals are printed output and assertions for subscription creation, but there are no structured result checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/ps_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/ps_tutorial.py -->
# sources/storage-engines/foundationdb/layers/pubsub/ps_tutorial.py

Purpose: This tutorial script documents the basic pub/sub concepts and walks through creating a feed, an inbox, a subscription, and two messages. It is intended for interactive learning rather than automated validation.

Important APIs and types: It imports `PubSub` from `pubsub_bigdoc`, sets `fdb.api_version(14)`, opens the default database, and uses `create_feed`, `create_inbox`, `create_subscription`, `post_message`, and `get_inbox_messages`.

Control flow: Execution creates Alice's feed and Bob's inbox, subscribes Bob to Alice, posts two messages, and prints messages visible to Bob. The optional database clear is commented out.

State and persistence behavior: The script mutates the default FDB database by adding pub/sub objects and messages. Because it does not clear by default, repeated runs can accumulate or interact with prior tutorial state depending on `pubsub_bigdoc` naming semantics.

Dependencies and integration points: It demonstrates the higher-level pub/sub layer but depends on an older module name and API version. The tutorial text explains feeds, inboxes, and subscriptions inline.

Risks: It is Python 2-era and not isolated. Tests should treat it as documentation; executable checks would need a temporary database/subspace and assertions on returned message lists rather than printed output.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/ps_tutorial.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub.py -->
# sources/storage-engines/foundationdb/layers/pubsub/pubsub.py

Purpose: This is the current SimpleDoc-backed FoundationDB PubSub layer in this subset. It models feeds, inboxes, subscriptions, and retroactive message delivery where an inbox can see historical messages from feeds it subscribes to.

Important APIs and types: Global SimpleDoc handles include `feeds`, `inboxes`, `messages`, and ordered index `feed_messages`. Transactional helpers implement feed/inbox creation, subscriptions, posting, listing, dirty-feed copying, subscription listing, clearing, and printing. `PubSub` wraps those helpers as methods on a database-bound object.

Control flow: Creating a subscription records the feed under `inbox.subs` and marks the feed dirty for that inbox. Posting prepends a message, sets its `fromfeed`, marks currently watching inboxes dirty, and clears the feed's watcher list. Reading inbox messages first copies messages from dirty feeds into `inbox.messages`, re-registers the inbox as watching those feeds, clears dirty markers, updates `latest_message`, then returns recent message values up to the limit.

State and persistence behavior: Persistent state is a SimpleDoc tree under `root.feeds`, `root.inboxes`, and `root.messages`. Inbox state includes subscriptions, dirty feeds, cached message IDs, and the latest message marker; feed state includes watching inboxes. Clearing wipes the SimpleDoc root.

Dependencies and integration points: It depends on `simpledoc` and its `OrderedIndex`, not raw FDB tuples directly. The bottom of the file embeds a random threaded sample workload using `fdb.api_version(22)` when run as `__main__`.

Risks: The embedded sample relies on globals `ps`, `random`, `threading`, and `time` only initialized in the main block. `get_inbox_subscriptions` accepts a limit but does not enforce it. Message ordering and `latest_message` comparisons depend on SimpleDoc child ordering and prepend ID semantics. Tests should cover retroactive subscriptions, dirty/watching transitions, repeated reads, limits, concurrent posts and reads, and `clear_all_messages` isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub_example.py -->
# sources/storage-engines/foundationdb/layers/pubsub/pubsub_example.py

Purpose: This standalone example drives `pubsub.PubSub` with a randomized threaded topology. It is a demonstration of feeds posting messages and inboxes polling for received messages.

Important APIs and functions: It creates a module-level `ps = PubSub(db)` and defines `setup_topology`, `feed_driver`, `get_and_print_inbox_messages`, `inbox_driver`, `run_threads`, and `sample_pubsub`.

Control flow: The script clears all pub/sub state, creates a requested number of feeds and inboxes, randomly subscribes each inbox to at least one feed, starts one thread per feed to post messages with random sleeps, and starts one thread per inbox to poll until no changes are observed for a wait limit.

State and persistence behavior: It mutates the default FDB database through the PubSub layer and clears all messages at startup. Runtime state is Python thread lists and polling variables; persistent state is the SimpleDoc-backed pub/sub tree.

Dependencies and integration points: It uses `fdb.api_version(22)`, Python `random`, `threading`, and `time`, and the local `pubsub` module. It listens to no external input other than the hard-coded sample sizes in `__main__`.

Risks: Output is nondeterministic due to random topology and sleep timing. It is Python 2 syntax and not an automated test. Test signals are visual logs; a real test should assert expected message counts and subscription coverage with deterministic random seeds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub_example.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub_orig.py -->
# sources/storage-engines/foundationdb/layers/pubsub/pubsub_orig.py

Purpose: This is an older raw-key prototype of the pub/sub layer. It documents the intended data model and implements feed, inbox, subscription, posting, listing, and feed-stat operations using explicit tuple keys and binary IDs.

Important APIs and types: Key builder functions generate feed, inbox, subscription, watcher, message, and count keys. Transactional internals include `_create_feed_internal`, `_create_inbox_internal`, `_create_subscription_internal`, `_post_message_internal`, `_list_messages_internal`, and `_print_internal`. `PubSub` wraps those with random 64-bit feed/inbox IDs.

Control flow: Feed and inbox creation initialize metadata and count keys. Subscription creation checks existence via count keys, writes inbox subscription and feed subscriber keys, increments counts, and adds the inbox as a watcher. Posting creates a descending global message ID, stores message contents, associates it with the feed, increments the feed message count, and has commented-out watcher dirtying code. Listing scans inbox subscriptions, then each feed's message keys, and loads message bodies.

State and persistence behavior: Persistent state is raw FDB keyspace partitions with prefixes `f`, `i`, and `m`, plus big-endian packed IDs. Counts are manually maintained in separate keys. Watcher/stale-feed state is partly modeled but not fully active in `post_message`.

Dependencies and integration points: It prepends a local bindings path, imports `fdb`, `struct`, `os`, and `sys`, and uses older APIs such as `fdb.tuple_to_key` and `get_range_startswith`. It predates the SimpleDoc implementation.

Risks: The global message ID logic appears inconsistent: it reads `first_greater_than` from `message(0)` but checks `last_key` value at `sys.maxint`, so edge cases are suspect. Dirty watcher propagation is commented out, limiting scalability semantics. Tests should verify ID ordering, counts, subscription existence checks, list output, duplicate subscription idempotence, and missing feed/inbox behavior if this code is still used.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub_orig.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub_simpledoc.py -->
# sources/storage-engines/foundationdb/layers/pubsub/pubsub_simpledoc.py

Purpose: This is an intermediate SimpleDoc implementation of PubSub, similar to `pubsub.py` but with older naming and some unused parameters. It stores feeds, inboxes, messages, subscriptions, dirty feeds, and watcher relationships in SimpleDoc.

Important APIs and types: It defines `feed_messages`, `feed_watching_inboxes`, `feeds`, `inboxes`, and `messages`. Transactional helpers create feeds/inboxes, create subscriptions, post messages, list messages, get feed messages, copy dirty feeds, get inbox subscriptions/messages, clear all messages, and print internals. `PubSub` exposes these helpers as methods.

Control flow: Subscriptions mark feeds dirty for inboxes. Posting prepends a message, records `fromfeed`, marks watching inboxes dirty, and clears watcher records. Inbox reads copy messages from dirty feeds into the inbox cache, register the inbox as watching each feed, clear dirty markers, update `latest_message`, and return message values.

State and persistence behavior: Persistent SimpleDoc state mirrors the current implementation: root children for feeds, inboxes, and messages; per-inbox `subs`, `dirtyfeeds`, `messages`, and `latest_message`; per-feed `watchinginboxes`. The `message_id` generated by `PubSub.post_message` is not used by `_post_message_internal`.

Dependencies and integration points: It imports `fdb` and `simpledoc` but does not call `fdb.api_version` locally. It is a historical layer variant that informs the current `pubsub.py`.

Risks: `message_ids = message_ids[:max(limit, len(message_ids))]` does not enforce the intended limit when the list is longer than `limit`. `feed_watching_inboxes` duplicates the same index definition as `feed_messages` and is unused. Tests should compare behavior against `pubsub.py`, especially message limits, watcher transitions, and retroactive subscription semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/pubsub_simpledoc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/remoteload.py -->
# sources/storage-engines/foundationdb/layers/pubsub/remoteload.py

Purpose: This command-line utility bulk-creates paired users for a remote pub/sub benchmark: each user gets both an inbox and a feed. It is meant to seed a remote FoundationDB database before subscription/message workloads.

Important APIs and functions: It parses `--zkAddr`, `--database`, `--userStart`, and `--userCount`, opens `fdb.open(args.zkAddr, args.database)`, constructs `PubSub`, and calls `create_inbox_and_feed` with zero-padded user names.

Control flow: The script loops from `userStart` to `userCount - 1`, creates each user, prints progress every 100 users, then prints done. A transactional done-marker block is present but commented out.

State and persistence behavior: Persistent state is whatever `pubsub_bigdoc.PubSub.create_inbox_and_feed` writes for each user. There is no rollback across the whole range; partial loads remain if the script fails.

Dependencies and integration points: It uses argparse, legacy local bindings path insertion, and `pubsub_bigdoc`. It is one component of the remote pub/sub benchmark trio with `remotesubscribe.py` and `remotesend.py`.

Risks: Argument names reflect old ZooKeeper-style cluster addressing. Range semantics may surprise users because `userCount` is an exclusive end, not a count from start. Tests should run against an isolated database and assert created feed/inbox counts and idempotence for repeated ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/remoteload.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/remotesend.py -->
# sources/storage-engines/foundationdb/layers/pubsub/remotesend.py

Purpose: This remote benchmark client mixes pub/sub message posting and inbox reads using gevent concurrency. It simulates many clients sending or checking messages against a preloaded user population.

Important APIs and functions: It parses `--zkAddr`, `--database`, `--totalUsers`, `--messages`, and `--threads`, opens FDB with `event_model="gevent"`, constructs `PubSub`, and spawns `message_client` greenlets.

Control flow: Each greenlet sleeps a random initial delay, then loops until it has sent its share of messages. On each iteration it chooses a random user; with 10 percent probability it posts to that user's feed, otherwise it reads that user's inbox. All jobs are joined before printing done.

State and persistence behavior: Persistent state is pub/sub message records and inbox cache/dirty-feed updates. Runtime state is only greenlet counters and random choices.

Dependencies and integration points: It uses gevent monkey patching for threads, local bindings path insertion, Python `random`, and `pubsub_bigdoc`. It expects users already created by `remoteload.py` and subscriptions by `remotesubscribe.py`.

Risks: The message body references `i`, which is the loop variable from greenlet creation and may not be defined as intended inside `message_client` under Python scoping. Integer division of messages by threads can drop remainder messages. Tests should use deterministic seeds, validate total posts, and catch missing-user and scoping errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/remotesend.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/remotesubscribe.py -->
# sources/storage-engines/foundationdb/layers/pubsub/remotesubscribe.py

Purpose: This command-line utility creates random follower subscriptions among preloaded pub/sub users. It is part of the remote pub/sub benchmark setup.

Important APIs and functions: It parses `--zkAddr`, `--database`, `--totalUsers`, and `--followers`, opens the remote database, constructs `PubSub`, and calls `create_subscription(get_feed_by_name(...), get_inbox_by_name(...))`.

Control flow: For each follower edge, it chooses two random user IDs between zero and `totalUsers`; if they differ, it subscribes the second user's inbox to the first user's feed. Progress is printed every 100 attempted edges.

State and persistence behavior: Persistent state is subscription records and any dirty-feed/watch state maintained by `pubsub_bigdoc`. Duplicate random pairs are possible and self-pairs are skipped, so the final edge count can be less than `followers`.

Dependencies and integration points: It uses argparse, local binding path insertion, Python `random`, and `pubsub_bigdoc`. It expects users to exist in the same zero-padded name format created by `remoteload.py`.

Risks: `random.randint(0, args.totalUsers)` includes `totalUsers`, while `remoteload.py` creates up to `userCount - 1`, so the script can reference a non-existent user. Tests should bound IDs, assert subscription counts, handle duplicates, and verify missing user behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/pubsub/remotesubscribe.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/taskbucket/__init__.py -->
# sources/storage-engines/foundationdb/layers/taskbucket/__init__.py

Purpose: This package implements a FoundationDB TaskBucket layer for distributed task queues plus a Future/FutureBucket mechanism for dependency tracking and callbacks. It lets multiple clients claim tasks, run them, finish them, and requeue timed-out work.

Important APIs and types: `Subspace`, `TaskTimedOutException`, `TaskBucket`, `TaskDispatcher`, `FutureBucket`, and `Future` are the main public types. `TaskBucket` exposes `clear`, `add`, `addIdle`, `get_one`, `is_empty`, `is_busy`, `finish`, `is_finished`, `check_active`, `extend`, and `check_timeouts`. `TaskDispatcher` registers task functions and dispatches dictionaries; `Future` supports `is_set`, `on_set_add_task`, `on_set`, `set`, `join`, and `joined_future`.

Control flow: `TaskBucket.add` writes task dictionary fields under `available`. `get_one` chooses a random-ish available task by snapshot key selector, moves fields into `timeouts` under a read-version-based timeout, deletes the available record, and returns task metadata. `finish` deletes timeout records or raises if they already expired. `check_timeouts` scans expired timeout records and restores them to available. Futures store block keys; setting a future clears blocks and performs stored callback task dictionaries through the dispatcher.

State and persistence behavior: Persistent task state is split into available tasks, timeout/lock records, an active marker, future block records, and future callback records. Task dictionaries are stored field-by-field and may include packed custom values. System-key access can be enabled for special deployments.

Dependencies and integration points: It uses `fdb.api_version(200)`, UUID random keys, tuple subspaces, read versions as timeout clocks, and transaction options for system keys. It integrates with user-defined Python functions through `TaskDispatcher.taskType`.

Risks: `extend` is unimplemented, and `TaskDispatcher.do_one` dispatches but does not call `finish`; task functions must finish themselves or tasks remain locked until timeout. Timeout math depends on read versions and a configured millisecond-like value. Tests should cover claim/finish/requeue, idle tasks, timeout exceptions, future joins/callbacks, system-key options, and task functions that fail before finishing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/taskbucket/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/taskbucket/test.py -->
# sources/storage-engines/foundationdb/layers/taskbucket/test.py

Purpose: This Python 2 script is an executable demonstration of TaskBucket and FutureBucket. It creates a small task graph that says hello to 20 names and then schedules a final completion task.

Important APIs and types: It imports `taskbucket`, `Subspace`, and `TaskTimedOutException`, creates `TaskDispatcher`, `TaskBucket`, and `FutureBucket`, and registers `say_hello`, `say_hello_to_everyone`, and `said_hello` task functions.

Control flow: The script clears the database, creates an `all_done` future, clears the task bucket, adds the root `say_hello_to_everyone` task, and attaches `said_hello` as a callback task. The root task creates 20 child futures/tasks and joins them into `done`; each child prints a greeting, sets its future, and finishes itself. The main loop repeatedly calls `do_one`, sleeping when no task is available, and catches timed-out tasks.

State and persistence behavior: It destructively clears the key range `""` to `"\xff"`, then persists task and future state under `backup-agent`. Task functions finish their own task records inside transactions.

Dependencies and integration points: It manipulates local bindings/layers import paths, uses FDB API version 200, and opens the default database. It demonstrates how TaskBucket composes with Future callbacks.

Risks: The loop structure has an unreachable `break` because the inner loop is infinite unless interrupted, and full database clearing is hazardous. It is a demo, not a deterministic test. Structured tests should assert that all child futures are set, the final task runs once, and no available or timeout records remain.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/layers/taskbucket/test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-clients/postinst -->
# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-clients/postinst

Purpose: This Debian client-package post-install script runs linker cache maintenance and initializes the shared FoundationDB system user/group and configuration directory on first install.

Important operations: On `configure`, it calls `ldconfig`. When there is no previously configured version (`$2` empty), it creates system group `foundationdb`, creates system user `foundationdb` with disabled login and `/var/lib/foundationdb` home, then sets `/etc/foundationdb` ownership and mode `775`.

Control flow: The script only acts for the `configure` maintainer-script action. Upgrade or abort actions fall through successfully.

State and persistence behavior: It persists OS-level passwd/group entries and directory ownership/permissions. It does not create a cluster file.

Dependencies and integration points: It depends on Debian tools `getent`, `addgroup`, `adduser`, `chown`, `chmod`, and `ldconfig`. The server package defensively repeats user/group creation.

Risks: Permission mode `775` allows group writes to `/etc/foundationdb`, which is intentional for the service group but security-sensitive. Tests should run package install in a container and verify idempotence for fresh install versus upgrade.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-clients/postinst -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postinst -->
# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postinst

Purpose: This Debian server-package post-install script initializes service directories, creates a default cluster file for fresh installs, starts FoundationDB, registers init defaults, and configures a new single-memory database when needed.

Important operations: It creates the `foundationdb` user/group if needed, owns `/var/lib/foundationdb` and `/var/log/foundationdb`, locks down data/log directories to `0700`, generates `/etc/foundationdb/fdb.cluster` if absent, starts via `deb-systemd-invoke`/`systemctl` or init.d, calls `update-rc.d`, and runs `fdbcli configure new single memory; status` for a new database.

Control flow: All behavior is under `configure`. First-install-only blocks are gated by empty `$2`; service start runs on configure for both fresh install and upgrade.

State and persistence behavior: It persists OS user/group, data/log ownership, cluster file contents, init registration, service state, and potentially a newly configured FDB database. Existing cluster files are preserved.

Dependencies and integration points: It integrates Debian maintainer scripts with systemd/init.d, `fdbcli`, `/etc/foundationdb/fdb.cluster`, and package-created directories.

Risks: Automatically configuring `single memory` is suitable for local first install but not a production cluster. Random cluster token generation uses filtered `/dev/urandom`. Tests should verify fresh install, upgrade with existing cluster file, systemd and non-systemd paths, and failure behavior when `fdbcli` cannot configure within timeout.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postinst -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postrm -->
# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postrm

Purpose: This Debian server-package post-removal script unregisters the init service on remove/purge and deliberately preserves database, log, and cluster files on purge.

Important operations: For `remove` or `purge`, it runs `update-rc.d -f foundationdb remove || :`. For `purge`, it prints instructions for manually deleting `/var/lib/foundationdb`, `/var/log/foundationdb`, and `/etc/foundationdb/fdb.cluster`.

Control flow: Action handling is simple conditional branching on `$1`. Destructive deletion commands and user deletion are commented out.

State and persistence behavior: Init registration is removed, but data/log/config state remains. This conservative behavior protects user data even on package purge.

Dependencies and integration points: It uses Debian `update-rc.d` and shell output. It complements `preinst`/`prerm` service stop behavior.

Risks: Users expecting purge to remove all package state may be surprised, but deleting database files automatically would be dangerous. Tests should verify no data/config removal occurs and that service registration is removed idempotently.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/postrm -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/preinst -->
# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/preinst

Purpose: This Debian server-package pre-install script stops the running service during upgrades, removes an obsolete bundled argparse file, and blocks installation over an old monolithic `foundationdb` package unless that package is purged.

Important operations: On `upgrade`, it runs `invoke-rc.d foundationdb stop || :` and removes `/usr/lib/foundationdb/argparse.py`/`.pyc`. It then checks `dpkg-query -s foundationdb`; if present, it prints a warning and exits with status 1.

Control flow: Upgrade-specific cleanup happens first; the old-package conflict check happens for all invocations.

State and persistence behavior: It can stop service processes and delete obsolete Python files. It does not alter database files directly, but it refuses installation when old package state could conflict.

Dependencies and integration points: It uses Debian `invoke-rc.d`, `dpkg-query`, and package filesystem paths. It coordinates package migration from older packaging layouts.

Risks: The message says purging the old package will erase databases, so this guard intentionally forces an operator decision. Tests should simulate upgrade and fresh install with/without the old package registered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/preinst -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/prerm -->
# sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/prerm

Purpose: This Debian pre-removal script stops FoundationDB before package removal or deconfiguration.

Important operations: For `remove` or `deconfigure`, it runs `invoke-rc.d foundationdb stop || :`.

Control flow: Other maintainer-script actions are ignored. The stop failure is tolerated to avoid blocking package operations on an already-stopped service.

State and persistence behavior: It changes only runtime service state. Database, logs, and configuration are untouched.

Dependencies and integration points: It uses Debian init policy via `invoke-rc.d` and pairs with post-install service start and post-removal init unregistering.

Risks: If stop fails silently, package removal can proceed while processes remain alive. Tests should verify remove/deconfigure actions stop services and that failed-upgrade/upgrade paths behave according to Debian policy expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/DEBIAN-foundationdb-server/prerm -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/builddebs.sh -->
# sources/storage-engines/foundationdb/packaging/deb/builddebs.sh

Purpose: This build script assembles FoundationDB server and client Debian packages from an existing build output tree. It creates temporary package roots, installs files with correct modes, computes installed sizes, and invokes `dpkg-deb`.

Important operations: The server package copies maintainer scripts, config, init script, `fdbserver`, `fdbmonitor`, `make_public.py`, README, and creates data/log/config directories. The client package installs `fdbcli`, `libfdb_c.so`, `libfdb_c_shim.so`, C headers/options, README, `fdbbackup`, and symlinks for backup/restore/DR commands.

Control flow: The script builds server first and client second, accumulating failure count in `status`. Each package uses `mktemp -d`, `fakeroot dpkg-deb --build`, and cleanup with `rm -r`.

State and persistence behavior: It writes package artifacts under `packages` and temporary staging directories. It does not modify system package state.

Dependencies and integration points: It expects to run from a FoundationDB build tree with `bin`, `lib`, `bindings`, `fdbclient`, and `packaging` paths available. It depends on `fakeroot`, `dpkg-deb`, `dos2unix`, and standard Unix install tools.

Risks: Missing build artifacts produce package failures, but cleanup still removes staging directories. The script suppresses `dpkg-deb` stderr, which can hide diagnostics. Tests should verify package contents, modes, symlinks, installed-size fields, maintainer script permissions, and failure reporting for missing inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/builddebs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/foundationdb-clients.control.in -->
# sources/storage-engines/foundationdb/packaging/deb/foundationdb-clients.control.in

Purpose: This Debian control template defines metadata for the `foundationdb-clients` package. Build tooling substitutes `VERSION-RELEASE` before packaging.

Important fields: It declares package name, version placeholder, database section, optional priority, `amd64` architecture, conflict with old `foundationdb (<< 0.1.4)`, dependency on `libc6` and `adduser`, maintainer, homepage, and description.

Control flow: There is no executable control flow; Debian tooling reads the generated control file during package build/install.

State and persistence behavior: Package metadata affects dependency resolution and installed package identity, not application runtime state.

Dependencies and integration points: It integrates with `builddebs.sh` and Debian packaging conventions. The clients package contains utilities, headers, and libraries used by applications and by the server package dependency.

Risks: Architecture is fixed to `amd64`, which must match artifact builds. Dependency versions may become stale for newer distributions. Tests should render the template and validate it with `dpkg-deb`/`lintian` or package install smoke tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/foundationdb-clients.control.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/foundationdb-init -->
# sources/storage-engines/foundationdb/packaging/deb/foundationdb-init

Purpose: This is a SysV init script for managing `fdbmonitor` as the FoundationDB process monitor on non-systemd or init.d-compatible systems.

Important functions: `do_start` checks whether `fdbmonitor` is already running and starts it daemonized with `--conffile`, `--lockfile`, and `--daemonize`. `do_stop` stops the process with TERM/KILL retry and removes the pidfile. The case statement supports `start`, `stop`, `status`, `restart`, and `force-reload`.

Control flow: The script exits early if `/usr/sbin/fdbmonitor` is not executable, sources `/lib/init/vars.sh`, then dispatches on the command argument and logs daemon messages when verbose mode allows.

State and persistence behavior: It manages runtime process state and `/var/run/fdbmonitor.pid`. It reads `/etc/foundationdb/foundationdb.conf` but does not write it.

Dependencies and integration points: It uses `start-stop-daemon`, LSB init conventions, and package-installed `fdbmonitor`. `postinst`, `prerm`, and `postrm` call into this service path when systemd is not available.

Risks: The script comments out `/lib/lsb/init-functions`, but still calls `log_daemon_msg`, `log_end_msg`, and `status_of_proc`, which may be undefined depending on environment. Tests should run start/stop/status under target distributions and verify pidfile cleanup and restart semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/foundationdb-init -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/foundationdb-server.control.in -->
# sources/storage-engines/foundationdb/packaging/deb/foundationdb-server.control.in

Purpose: This Debian control template defines metadata for the `foundationdb-server` package. Build tooling substitutes the `VERSION-RELEASE` placeholder.

Important fields: It declares package name, version, database section, optional priority, `amd64` architecture, conflict with old monolithic FoundationDB packages, exact dependency on matching `foundationdb-clients`, `adduser`, `libc6`, recommendation for Python, maintainer, homepage, and description.

Control flow: There is no executable flow; Debian package tools consume this metadata.

State and persistence behavior: The metadata controls installation dependencies and package identity. Runtime state is managed by maintainer scripts and installed binaries, not this template.

Dependencies and integration points: It ties server package installation to the same-version clients package, ensuring `fdbcli` and client libraries are available for post-install configuration and operation.

Risks: Fixed `amd64` architecture and Python recommendation may age poorly. Tests should validate rendered control syntax, dependency resolution, and install/upgrade behavior with the paired clients package.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/deb/foundationdb-server.control.in -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/Dockerfile -->
# sources/storage-engines/foundationdb/packaging/docker/Dockerfile

Purpose: This multi-stage Dockerfile builds the family of FoundationDB container images: base tools, Go build stages, AWS S3 credentials sidecar, FoundationDB runtime, Kubernetes monitor, Kubernetes sidecar, Mako, and YCSB runner.

Important stages: `base` installs Rocky Linux troubleshooting tools and verified `tini`; `go-build` builds `fdb-kubernetes-monitor`; `go-credentials-fetcher-build` builds the S3 credential fetcher; `foundationdb-base` creates user `fdb`, downloads FoundationDB binaries and client libraries for `TARGETARCH`, and sets multiversion library layout. Later targets add monitor entrypoints, sidecar Python/watchdog support, runtime scripts, FlameGraph tools, Mako, Java/kubectl/AWS CLI, and YCSB.

Control flow: Build args choose FoundationDB version, library versions, website URL, and architecture. Architecture branches map Docker `amd64`/`arm64` to release artifact names. Several downloads are checksum-verified before installation.

State and persistence behavior: Images persist binaries, scripts, `/var/fdb` directory structure, multiversion client libraries, environment defaults, and declared volumes for data/input/output/logs. Runtime containers write cluster files, data, logs, trace logs, or credential files depending on target.

Dependencies and integration points: It integrates GitHub release artifacts, local `website` build context, Go sources, sidecar scripts, `fdb.bash`, `run_ycsb.sh`, Kubernetes monitor config, AWS CLI, and YCSB FoundationDB binding.

Risks: External pinned downloads can break or become stale; Python 3.9 sidecar has an explicit EOL note. `foundationdb-base` copies client libraries into both `/usr/lib/fdb/multiversion` and `/var/fdb/lib`, so version layout must match clients. Tests should build all targets for both architectures, verify checksums, run `fdbserver`/`fdbcli`, start sidecars, and execute YCSB smoke workloads.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/build-images.sh -->
# sources/storage-engines/foundationdb/packaging/docker/build-images.sh

Purpose: This Bash helper builds and optionally pushes the FoundationDB Docker image set from local or Artifactory-provided build artifacts. It is tailored to the FoundationDB team's development environment and exits by default outside that context.

Important functions: `create_fake_website_directory` prepares a local `website` tree containing release-like binaries and client libraries from stripped/unstripped Artifactory or local build outputs. `compile_ycsb` clones or syncs YCSB and builds the FoundationDB binding. `build_and_push_images` loops over image targets, constructs tags, runs `docker build` with labels and build args, and pushes selected images.

Control flow: The script sets strict mode, logs start, derives build output/source/version/commit metadata, defines image lists, and branches on `OKTETO_NAMESPACE`. In Okteto/AWS it discovers region/account, selects build output, builds regular and debug images, and pushes them; otherwise it prints a warning and exits 1.

State and persistence behavior: It creates and deletes `packaging/docker/website`, creates `YCSB`, builds Docker images/tags, and may push to ECR or Docker registries. It does not commit anything to source control.

Dependencies and integration points: It depends on Docker, curl, tar, rsync, git, Maven, AWS metadata/CLI in Okteto, CMakeCache metadata, local build outputs, Artifactory, and the adjacent Dockerfile.

Risks: The script contains a typo `source_code_diretory`, but uses that variable consistently. Defaults are intentionally not portable. Tests should use shellcheck, dry-run builds with fake website artifacts, Okteto/ECR integration checks, and verification that debug/regular images receive correct tags and labels.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/build-images.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/entrypoint.bash -->
# sources/storage-engines/foundationdb/packaging/docker/entrypoint.bash

Purpose: This entrypoint belongs to the Kubernetes sidecar image. It optionally sources additional environment variables, then execs the Python sidecar process.

Important operations: If `ADDITIONAL_ENV_FILE` is non-empty, it runs `source $ADDITIONAL_ENV_FILE`; then it executes `/sidecar.py $*`.

Control flow: There is no validation or fallback. `exec` replaces the shell so signals go to `sidecar.py`, with `tini` configured as the image entrypoint parent in the Dockerfile.

State and persistence behavior: It does not persist state directly; sourced environment can alter sidecar runtime behavior. The sidecar writes output files according to its own configuration.

Dependencies and integration points: It depends on `/sidecar.py` and optional environment files mounted into the container. It is used by the `foundationdb-kubernetes-sidecar` Docker target.

Risks: Unquoted `source $ADDITIONAL_ENV_FILE` and `$*` can break paths/arguments with spaces and can source unintended files. Tests should run entrypoint with and without an env file and verify signal/argument propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/entrypoint.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/fdb-aws-s3-credentials-fetcher/fdb-aws-s3-credentials-fetcher.go -->
# sources/storage-engines/foundationdb/packaging/docker/fdb-aws-s3-credentials-fetcher/fdb-aws-s3-credentials-fetcher.go

Purpose: This Go sidecar continuously writes FoundationDB blob-storage S3 credential JSON from AWS SDK credentials. It is intended for EKS/IRSA or other AWS credential sources so FDB processes can authenticate to S3.

Important APIs and types: `BlobCredentials` contains account mappings to `Account` records with `secret`, `api_key`, and `token`. `writeCredentialsFile` writes `s3_blob_credentials.json`; `refreshCredentials` loads AWS default config and retrieves credentials; `main` parses pflag options including `--region`, `--dir`, `--bucket`, `--run-once`, and `--expiry-threshold`.

Control flow: The program validates `--dir`, creates it, computes the credential file path, optionally refreshes once and exits, or starts a 5-minute ticker loop. Each refresh loads AWS config for the region, retrieves credentials, and writes account entries for regional S3 host, `:443`, bucket regional host, and bucket `:443`.

State and persistence behavior: Persistent state is the JSON credential file under the configured directory, mode `0644`. It rewrites credentials each interval rather than comparing expiry. No in-memory secret cache survives process exit.

Dependencies and integration points: It uses AWS SDK v2 config loading, `spf13/pflag`, Kubernetes/EKS credential providers via the default chain, and FoundationDB blob credential file conventions.

Risks: `expiryThreshold` is parsed but not used in refresh decisions. The default bucket contains a specific account-like name, which may not fit other deployments. File mode `0644` exposes credentials to same-container users. Tests should validate JSON shape, host-key variants, run-once behavior, AWS config failures, region/bucket overrides, and credential file permissions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/fdb-aws-s3-credentials-fetcher/fdb-aws-s3-credentials-fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/fdb.bash -->
# sources/storage-engines/foundationdb/packaging/docker/fdb.bash

Purpose: This runtime script starts an `fdbserver` process inside the standard FoundationDB container. It creates the cluster file from environment variables, chooses public IP based on networking mode, and launches the server.

Important functions: `create_cluster_file` writes `FDB_CLUSTER_FILE` from `FDB_CLUSTER_FILE_CONTENTS`, a resolved `FDB_COORDINATOR`, or errors. `create_server_environment` writes `/var/fdb/.fdbenv` with `PUBLIC_IP`, sets default cluster-file contents for self-coordination, and calls `create_cluster_file`.

Control flow: The script creates environment state, sources it, logs the listen address, then execs `fdbserver` with listen/public address, data/log directories, locality IDs from hostname, process class, and `--knob_disable_posix_kernel_aio=1`.

State and persistence behavior: It writes the cluster file, `/var/fdb/.fdbenv`, data under `/var/fdb/data`, and logs under `/var/fdb/logs`. The server process owns ongoing database state.

Dependencies and integration points: It uses `dig`, `hostname`, environment variables from Docker/Compose/Kubernetes, and the `foundationdb` Docker target's entrypoint.

Risks: Coordinator DNS must resolve before startup. Host networking mode always uses `127.0.0.1`, which is suitable for local mapping but not multi-host clusters. Tests should cover cluster-file-content override, coordinator DNS path, host/container modes, missing coordinator error, and server process argument construction.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/fdb.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/fdb_single.bash -->
# sources/storage-engines/foundationdb/packaging/docker/fdb_single.bash

Purpose: This variant starts a single-node FoundationDB container and automatically configures it as `single memory`. It is useful for demos and local samples.

Important functions: It shares `create_cluster_file` and `create_server_environment` logic with `fdb.bash`, adds `start_fdb` to launch `fdbserver` in the background, and `configure_fdb_single` to run `fdbcli --exec 'configure new single memory'` followed by `status`.

Control flow: Strict mode and job control are enabled. The script starts the server, waits five seconds, configures the database, then foregrounds the server job so the container stays alive.

State and persistence behavior: It writes the same cluster/data/log/env files as `fdb.bash` and persists a configured single-memory database in the data volume.

Dependencies and integration points: It depends on `fdbserver`, `fdbcli`, DNS tools, and container environment variables. Samples or developers can use it when they want self-configuration.

Risks: Fixed sleep can race slow startup, and repeated runs against an already configured database may fail the `configure new` step. Tests should run fresh and existing-data containers, verify foreground signal handling, and check cluster file creation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/fdb_single.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/kubernetes/test_config.yaml -->
# sources/storage-engines/foundationdb/packaging/docker/kubernetes/test_config.yaml

Purpose: This Kubernetes manifest demonstrates running FoundationDB processes with the `fdb-kubernetes-monitor` image in a StatefulSet. It is explicitly a development/test example, not a recommended production deployment.

Important resources: The file defines a 5-replica StatefulSet with `foundationdb` and `foundationdb-sidecar` containers, a ConfigMap containing `fdb.cluster` and monitor `config.json`, a ServiceAccount, Role, and RoleBinding. It uses PVCs for data and emptyDir volumes for logs/shared binaries/dynamic config.

Control flow: The main container runs monitor mode with input dir and log path. The sidecar runs `--mode sidecar`, copies `fdbserver` and `fdbcli`, and writes shared binaries. The monitor config builds fdbserver arguments from environment variables and process numbers, including public/listen addresses, datadirs, locality, logs, and JSON trace format.

State and persistence behavior: StatefulSet PVCs persist `/var/fdb/data`; logs and shared binaries are ephemeral. The ConfigMap seed cluster file is initially empty, while runtime cluster file is under the data volume.

Dependencies and integration points: It integrates Kubernetes downward API, RBAC permissions on pods, `fdb-kubernetes-monitor`, sidecar binary sharing, and FoundationDB process configuration.

Risks: Image tags are fixed at `7.3.73` and may drift from built images. `runProcesses` is false in config, so behavior depends on monitor sidecar coordination. Tests should apply this manifest to a disposable namespace, verify pod readiness, binary copying, generated process args, RBAC sufficiency, and cluster formation.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/kubernetes/test_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/run_ycsb.sh -->
# sources/storage-engines/foundationdb/packaging/docker/run_ycsb.sh

Purpose: This script is the Kubernetes-context entrypoint for the YCSB FoundationDB benchmark image. It waits for peer YCSB pods, runs the requested workload, and uploads histogram files to S3.

Important operations: It reads the current namespace from the service account, waits until pods with labels `name=ycsb,run=$RUN_ID` are running, runs `./bin/ycsb.sh "$MODE" foundationdb -s -P workloads/$WORKLOAD $YCSB_ARGS`, then syncs `/tmp/histogram.*` to `s3://$BUCKET/ycsb_histograms/$namespace/$POD_NAME` with KMS SSE.

Control flow: Strict mode and an error trap print run metadata and environment on failure. Logging uses UTC timestamps. The script blocks before running until the requested `NUM_PODS` are running.

State and persistence behavior: YCSB writes local temporary histograms, and the script persists them to S3. It does not create an FDB cluster file; the container environment is expected to supply dynamic client configuration.

Dependencies and integration points: It depends on Kubernetes service-account files, `kubectl`, AWS CLI, YCSB, and environment variables such as `RUN_ID`, `WORKLOAD`, `MODE`, `NUM_PODS`, `POD_NAME`, and `BUCKET`.

Risks: The pod readiness loop parses `kubectl` output with `grep -cv NAME`, which is fragile. Unquoted `$YCSB_ARGS` is passed as one shell word because it is inside quotes, limiting multi-arg behavior. Tests should run in a test namespace, verify wait logic, workload execution, failure trap output, and S3 upload path.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/run_ycsb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/run_ycsb_standalone.sh -->
# sources/storage-engines/foundationdb/packaging/docker/run_ycsb_standalone.sh

Purpose: This script runs the same YCSB FoundationDB workload outside Kubernetes. It creates an FDB cluster file from environment variables, then launches YCSB.

Important functions: `create_cluster_file` mirrors the Docker server script: it writes `FDB_CLUSTER_FILE` from explicit contents, DNS-resolved coordinator and port, or exits with an error. The main path runs `./bin/ycsb.sh "$MODE" foundationdb -s -P workloads/$WORKLOAD $YCSB_ARGS`.

Control flow: Strict mode and an error trap print run metadata and environment. It logs workload start, creates the cluster file, runs YCSB, then logs completion.

State and persistence behavior: It writes a cluster file to the configured path and YCSB may write local benchmark artifacts. No S3 upload occurs in this standalone variant.

Dependencies and integration points: It depends on `dig`, YCSB, FoundationDB Java binding configuration, and environment variables for coordinator and workload selection.

Risks: Like the Kubernetes version, `YCSB_ARGS` quoting can collapse multiple arguments. DNS lookup failures abort the run. Tests should cover cluster-file-content override, coordinator path, missing coordinator failure, and a small workload smoke test.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/run_ycsb_standalone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/Dockerfile -->
# sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/Dockerfile

Purpose: This Dockerfile builds the Go sample application image that talks to a FoundationDB Docker cluster. It installs FDB clients into a Go build image and compiles the sample HTTP app.

Important operations: It uses an `FDB_VERSION` build arg, references the FoundationDB image as a stage, starts from `golang:1.22`, installs `ca-certificates` and `dnsutils`, downloads the matching `foundationdb-clients` Debian package from GitHub releases, installs it with `dpkg`, copies the app, runs `go get` and `go install`, and sets `/start.bash` as the command.

Control flow: Build-time steps are linear and depend on release artifact availability for the requested version.

State and persistence behavior: The image persists installed FDB client libraries/tools, Go source/build output, and the start script. Runtime persistence is handled by the FDB cluster, not this image.

Dependencies and integration points: It integrates with the adjacent Go `main.go`, `start.bash`, and sample `docker-compose.yml`. `dnsutils` supports cluster-file creation in the start script.

Risks: It downloads only `amd64` Debian packages while compose forces `linux/amd64`; multi-arch users need changes. `go get` during build can be non-reproducible without pinned modules. Tests should build for the sample version and hit the `/counter` endpoint against the compose cluster.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/main.go -->
# sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/main.go

Purpose: This Go sample exposes a minimal HTTP counter backed by FoundationDB. It demonstrates opening FDB from container environment and performing a transactional read-modify-write.

Important APIs and functions: `main` parses `FDB_API_VERSION`, calls `fdb.MustAPIVersion`, opens the database from `FDB_CLUSTER_FILE`, registers `/counter`, and starts `http.ListenAndServe`. `incrementCounter` runs `db.Transact`, reads key `my-counter`, increments a big-endian uint32, writes it back, and returns the new value.

Control flow: Each request to `/counter` performs one FDB transaction. Missing values initialize to zero before incrementing. Errors from the transaction call `log.Fatalf`, terminating the server.

State and persistence behavior: Persistent state is a single FDB key `my-counter` encoded as 4-byte big-endian unsigned integer. The global `db` holds the database connection.

Dependencies and integration points: It uses the FoundationDB Go binding, Go `net/http`, environment variables from Docker Compose, and helper functions for binary conversion.

Risks: The counter overflows at `uint32` limits and fatal request errors kill the whole process. Only GET-like `/counter` increments; there is no read-only route. Tests should cover first increment, concurrent increments, transaction retry behavior, bad env parsing, and overflow if relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/start.bash -->
# sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/start.bash

Purpose: This start script prepares the Go sample container's FoundationDB cluster connection, configures a new single-memory database if needed, and starts the compiled app.

Important operations: It relies on `FDB_CLUSTER_FILE`, calls `fdbcli -C $FDB_CLUSTER_FILE --exec status --timeout 3`, and if status fails, runs `configure new single memory ; status`. It then runs `/go/bin/fdb-demo-golang`.

Control flow: The script only configures when the status check fails. Failure to configure exits with status 1.

State and persistence behavior: It can mutate cluster configuration by creating a new single-memory database. The application then persists the counter key in FDB.

Dependencies and integration points: It depends on the cluster file generated by the base FoundationDB image/scripts, `fdbcli`, and the compiled Go binary installed by the Dockerfile.

Risks: The excerpt assumes `FDB_CLUSTER_FILE` already points at a valid cluster file; if not, status will fail for connection reasons indistinguishable from unconfigured database. Tests should run the sample compose from empty and already configured clusters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/app/start.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/docker-compose.yml -->
# sources/storage-engines/foundationdb/packaging/docker/samples/golang/docker-compose.yml

Purpose: This Compose file launches a three-process FoundationDB cluster plus the Go counter application. It demonstrates app-to-cluster connectivity in containers.

Important services: `fdb-coordinator`, `fdb-server-1`, and `fdb-server-2` use `foundationdb/foundationdb:${FDB_VERSION}` with coordinator/networking environment. `app` builds from `app`, passes `FDB_VERSION`, exposes port 8080, and sets `FDB_COORDINATOR` and `FDB_API_VERSION`.

Control flow: Server containers start with dependency ordering, and the app depends on all three FDB services. The coordinator exposes port 4500 to the host.

State and persistence behavior: The Compose file does not define persistent volumes, so database state is container-local/ephemeral unless Docker image defaults create volumes elsewhere. The app persists counter state in the cluster while it exists.

Dependencies and integration points: It relies on the FoundationDB Docker image's environment contract and the Go app Dockerfile/start script. It forces `linux/amd64` platform for all services.

Risks: `depends_on` does not wait for FDB readiness, so the app start script must handle configuration races. Tests should run `docker compose up`, wait for `/counter`, and verify multi-container cluster status.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/golang/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/local/docker-compose.yml -->
# sources/storage-engines/foundationdb/packaging/docker/samples/local/docker-compose.yml

Purpose: This Compose file runs a one-node FoundationDB cluster that is accessible from the host. It is the minimal local sample.

Important service: `fdb` uses image `foundationdb:6.1.8`, maps `$FDB_PORT` to the same container port, and sets `FDB_NETWORKING_MODE=host`, `FDB_COORDINATOR_PORT`, and `FDB_PORT`.

Control flow: Compose starts only the FDB service. Companion `start.bash` and `stop.bash` handle cluster-file creation and lifecycle.

State and persistence behavior: No explicit volumes are declared, so state is ephemeral unless Docker image volumes are retained. The host cluster file is written by `start.bash`, not by this YAML.

Dependencies and integration points: It integrates with local Docker Compose and host `fdbcli`. It pins an old sample image version.

Risks: The image tag lacks the `foundationdb/foundationdb` namespace used in newer samples and may not exist locally. Host networking mode here is represented through environment, not Docker `network_mode`. Tests should run the companion scripts and verify host `fdbcli` can connect through the generated cluster file.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/local/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/local/start.bash -->
# sources/storage-engines/foundationdb/packaging/docker/samples/local/start.bash

Purpose: This helper starts the local one-node Docker Compose sample, writes a host cluster file, and configures the database if needed.

Important operations: It defaults `FDB_CLUSTER_FILE=docker.cluster` and `FDB_PORT=4550`, runs `docker-compose up -d fdb`, writes `docker:docker@127.0.0.1:$FDB_PORT`, checks `fdbcli status`, and if needed runs `configure new single memory ; status`.

Control flow: Strict mode is enabled. Failure to configure prints an error and exits 1; success prints connection instructions.

State and persistence behavior: It creates/overwrites the host cluster file and may configure the FDB database. Docker container state is created by Compose.

Dependencies and integration points: It depends on `docker-compose`, host `fdbcli`, and the adjacent compose file. It is intended for developers with local FDB client tools installed.

Risks: The generated cluster file is overwritten on every start. Status failure can mean startup lag, networking failure, or unconfigured database. Tests should cover default and custom port/cluster-file values and idempotent reruns.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/local/start.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/local/stop.bash -->
# sources/storage-engines/foundationdb/packaging/docker/samples/local/stop.bash

Purpose: This helper stops the local Docker Compose FoundationDB sample.

Important operations: It defaults `FDB_PORT=4550`, passes that environment to `docker-compose down`, and prints that the cluster is down.

Control flow: Strict mode is enabled; any Compose failure aborts the script.

State and persistence behavior: It removes/stops Compose-managed containers and networks according to `docker-compose down`. It does not delete the generated host cluster file.

Dependencies and integration points: It depends on `docker-compose` and the adjacent compose file. The `FDB_PORT` environment matches `start.bash`.

Risks: It does not remove volumes explicitly, so Docker-managed volume behavior depends on the compose/image configuration. Tests should verify it stops the service and leaves or removes state as intended.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/local/stop.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/app/Dockerfile -->
# sources/storage-engines/foundationdb/packaging/docker/samples/python/app/Dockerfile

Purpose: This Dockerfile builds the Python Flask sample application image for FoundationDB. It installs FDB client libraries/tools and optional multiversion client libraries.

Important operations: It copies `libfdb_c.so`, `fdbcli`, and `create_cluster_file.bash` from the FoundationDB image stage, installs `dnsutils` and `curl`, downloads additional client libraries listed in `FDB_ADDITIONAL_VERSIONS`, installs Python requirements, copies `start.bash` and `server.py`, and sets Flask environment variables.

Control flow: Build-time loops over additional versions and writes them under `/usr/lib/fdb-multiversion`, with `FDB_NETWORK_OPTION_EXTERNAL_CLIENT_DIRECTORY` pointing there.

State and persistence behavior: The image persists the Python app, FDB client library/tools, and multiversion client libraries. Runtime state is in FDB.

Dependencies and integration points: It integrates with the FoundationDB Docker image, the Python binding requirements file, Flask server, and Compose environment.

Risks: The additional client library URL uses `FDB_WEBSITE` defaulting to `https://www.foundationdb.org` download paths, which differs from the GitHub release pattern elsewhere. Tests should build with no additional versions and with one version, then run the Flask counter routes against compose.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/app/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/app/server.py -->
# sources/storage-engines/foundationdb/packaging/docker/samples/python/app/server.py

Purpose: This Flask sample exposes read and increment endpoints for a FoundationDB-backed counter. It demonstrates Python binding setup and transactional mutation from a web service.

Important APIs and functions: It sets `fdb.api_version(int(os.getenv("FDB_API_VERSION")))`, opens the default database, defines `COUNTER_KEY = fdb.tuple.pack(("counter",))`, implements `_increment_counter(tr)`, and exposes `GET /counter` plus `POST /counter/increment`.

Control flow: `GET /counter` reads the key directly and returns `0` when absent. `POST /counter/increment` calls `_increment_counter(db)`, relying on the binding's transactional decorator behavior for functions accepting a transaction-like first argument.

State and persistence behavior: Persistent state is one tuple-packed counter key storing a tuple-packed integer. The Flask process holds a global database object.

Dependencies and integration points: It uses Flask and the FoundationDB Python binding. The start script prepares cluster connectivity and starts `flask run`.

Risks: The increment helper lacks an explicit `@fdb.transactional` decorator in this file, so correctness depends on binding behavior when passing `db` to an undecorated function; in standard bindings this would not make `tr[COUNTER_KEY]` valid unless `db` supports direct reads. Tests should verify POST actually commits, concurrent increments are atomic, and missing/invalid `FDB_API_VERSION` fails clearly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/app/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/app/start.bash -->
# sources/storage-engines/foundationdb/packaging/docker/samples/python/app/start.bash

Purpose: This start script prepares cluster connectivity for the Python sample and launches the Flask app.

Important operations: It checks whether `FDB_CLUSTER_FILE` is unset or empty; if so, it runs `/app/create_cluster_file.bash`, sets the default cluster-file path, checks `fdbcli status`, and configures `single memory` if needed. It then runs `FLASK_APP=server.py flask run --host=0.0.0.0`.

Control flow: Strict tracing mode `set -xe` is enabled. Configuration only happens when the script had to create or locate the cluster file.

State and persistence behavior: It can create a cluster file and configure a new database. It does not persist Flask state outside FDB.

Dependencies and integration points: It depends on `create_cluster_file.bash` copied from the FoundationDB image, `fdbcli`, Flask CLI, and environment variables from Compose.

Risks: If an existing cluster file points at an unconfigured database, the script skips the status/configure block because it only runs inside the cluster-file creation branch. Tests should cover both empty and pre-mounted cluster-file cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/app/start.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/docker-compose.yml -->
# sources/storage-engines/foundationdb/packaging/docker/samples/python/docker-compose.yml

Purpose: This Compose file launches a three-process FoundationDB cluster plus the Python Flask counter app. It is the Python counterpart to the Go sample.

Important services: Three FoundationDB services share coordinator/networking environment, with the coordinator exposing port 4500. The `app` service builds from `app`, passes `FDB_VERSION` and `FDB_ADDITIONAL_VERSIONS`, exposes port 5000, and sets `FDB_COORDINATOR` and `FDB_API_VERSION`.

Control flow: Compose dependency ordering starts the app after the three FDB services are created, but readiness is handled by the app start script and FDB client retries.

State and persistence behavior: No explicit volumes are declared, so database state is sample-ephemeral unless image volumes are retained. The Flask app persists the counter key in the running cluster.

Dependencies and integration points: It depends on the FoundationDB Docker image environment contract, Python app Dockerfile/start script, Flask, and FDB client libraries.

Risks: `depends_on` is not a readiness gate. Additional client library versions must be downloadable at build time. Tests should run compose, hit `GET /counter` and `POST /counter/increment`, and verify cluster status with `fdbcli`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/docker/samples/python/docker-compose.yml -->
