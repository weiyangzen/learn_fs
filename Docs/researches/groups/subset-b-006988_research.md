# subset-b-006988 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_es_query.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_es_query.cc

## Purpose
Implements RGW's small Elasticsearch query compiler. It tokenizes a restricted infix expression language, converts infix to prefix, builds a query-node tree, and emits Elasticsearch JSON through Ceph's `Formatter`/`encode_json` APIs.

## Important APIs, Types, And Functions
Core helpers include `operator_map`, `is_operator()`, `operand_value()`, `check_precedence()`, and `infix_to_prefix()`. Query tree classes are local to the implementation: `ESQueryNode`, `ESQueryNode_Bool`, typed leaf value adapters for string/int/date, comparison nodes for equality, inequality, and ranges, plus nested custom-field wrappers. `ESInfixQueryParser::*` parses tokens. `ESQueryCompiler::compile()`, `convert()`, and `dump()` are the externally relevant implementation points.

## Control Flow
`compile()` parses the source query into infix tokens, converts to prefix, recursively allocates the node tree with `alloc_node()`, then prepends any forced equality predicates by wrapping the existing root in `and` boolean nodes. `dump()` serializes the root as a `query` object. Boolean nodes emit `bool.must` or `bool.should`; equality emits `term`; inequality emits `bool.must_not.term`; range emits `range` with `lt/lte/gte/gt`.

## State And Persistence Behavior
The compiler owns an in-memory tree rooted at `query_root`; there is no persistence. Type interpretation is driven by caller-provided generic/custom `ESEntityTypeMap`s, field aliases, restricted-field sets, and a custom-field prefix. Custom fields are transformed into nested `meta.custom-{type}` queries.

## Dependencies And Integration Points
Uses Ceph JSON formatting, `strict_strtoll()`, `parse_time()`, `rgw_to_iso8601()`, and Boost string prefix matching. It integrates with RGW metadata search callers that provide field maps and then pass the compiled JSON to Elasticsearch.

## Risks
The parser is intentionally narrow: values cannot contain spaces or `)`, `and`/`or` matching is not word-boundary checked, and parse failures collapse into broad errors. The infix-to-prefix algorithm mutates the source token list by appending `)`. Unknown generic fields are rejected, while unknown custom fields silently become strings. Node ownership depends on careful handoff when nested nodes wrap existing operator nodes.

## Test Signals
Useful tests include precedence/parentheses cases, invalid operators, malformed expressions, int/date parse failures, restricted generic fields, alias expansion, custom nested string/int/date fields, and prepended equality predicates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_es_query.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_es_query.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_es_query.h

## Purpose
Declares the public surface for compiling RGW search expressions into Elasticsearch JSON: token stack, infix parser, entity type map, and compiler configuration.

## Important APIs, Types, And Functions
`ESQueryStack` wraps a `std::list<std::string>` with `peek()`, `pop()`, and `done()`. `ESInfixQueryParser` stores query text and exposes `parse()`. `ESEntityTypeMap` maps field names to `ES_ENTITY_STR`, `ES_ENTITY_INT`, or `ES_ENTITY_DATE`. `ESQueryCompiler` accepts a query, optional prepended equality conditions, and a custom metadata prefix; callers configure generic/custom type maps, field aliases, and restricted fields before calling `compile()` and `dump()`.

## Control Flow
The header establishes a two-phase API: configure compiler metadata, call `compile()` to produce a private `ESQueryNode` tree, then call `dump(Formatter*)` to serialize. Field aliasing and restricted checks are resolved during node initialization, not at parse time.

## State And Persistence Behavior
All state is transient. `ESQueryCompiler` owns `query_root`; parser and stack are embedded by value. `eq_conds` is moved from the caller-provided list, which is important for call-site ownership expectations.

## Dependencies And Integration Points
Depends on `rgw_string.h` for `ltstr_nocase`, standard containers, and `Formatter` via implementation includes. It is consumed by RGW services that expose metadata search over Elasticsearch.

## Risks
The API uses raw pointers for maps/sets and the query root, so callers must keep configured maps alive through compilation. `is_restricted()` checks exact set membership after aliasing. `ESQueryStack::assign()` swaps away the caller's list contents, which is efficient but destructive.

## Test Signals
Header-level tests should instantiate a compiler with aliases, type maps, restricted fields, and prepended equality conditions, then verify `compile()` behavior and emitted JSON through a formatter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_es_query.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_file.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_file.cc

## Purpose
Implements the C librgw file API that presents RGW buckets and objects as a POSIX/NFS-like filesystem. It maps mount, lookup, readdir, create, mkdir, unlink, rename, read, write, stat, and xattr operations onto RGW frontend requests and SAL objects.

## Important APIs, Types, And Functions
Internal methods on `RGWLibFS` implement object discovery and mutation: `stat_bucket()`, `stat_leaf()`, `fake_leaf()`, `read()`, `readlink()`, `unlink()`, `rename()`, `mkdir()`, `create()`, `symlink()`, `getattr()`, `setattr()`, xattr operations, `update_fh()`, `close()`, and `gc()`. `RGWFileHandle` methods implement encoding/decoding Unix attrs, readdir state, writes, close, invalidation, and cache reclamation. The `extern "C"` section exports `rgw_mount*`, `rgw_umount`, `rgw_statfs`, `rgw_lookup*`, `rgw_fh_rele`, `rgw_getattr`, `rgw_setattr`, `rgw_open`, `rgw_close`, `rgw_readdir*`, `rgw_read*`, `rgw_write*`, `rgw_commit`, and xattr APIs.

## Control Flow
Mount allocates `RGWLibFS`, authorizes access keys, registers the FS with the lib frontend process, and exposes the root handle. Lookup distinguishes root bucket lookup from object lookup. Bucket and object stats are fetched through synthetic RGW op requests, then materialized as cached `RGWFileHandle`s. Readdir issues either `RGWListBucketsRequest` or `RGWReaddirRequest`, updates link counts, markers, and invalidation events. Writes start a continued `RGWWriteRequest`, stream contiguous chunks through `exec_continue()`, and complete on close or stateless write timeout.

## State And Persistence Behavior
Persistent file metadata is stored as RGW object attrs `RGW_ATTR_UNIX_KEY1` and `RGW_ATTR_UNIX1`; etag and ACL attrs are preserved across setattr/write flows. `fh_key` values are deterministic hashes of tenant/bucket/object names. `RGWLibFS` maintains an intrusive FH cache plus LRU, close flags, invalidate callback, queued readdir events, and a write timer. Directory entries are not persistent handles by themselves; placeholder directory objects use trailing slash names.

## Dependencies And Integration Points
This file is deeply integrated with RGW REST/op classes, SAL driver/user/bucket/object APIs, `RGWLibFrontend`, RADOS cluster stat ops, xattrs, compression, checksums, perf counters, Ceph timers, and Ganesha-style librgw file structs from `include/rados/rgw_file.h`.

## Risks
Several operations are explicitly non-atomic: rename is copy-then-delete, stat of leaf directory/file can require multiple round trips, and fast attrs can synthesize handles from readdir data. Initial writes must be contiguous from offset zero unless stateless V3 overlap handling applies. `rgw_truncate()`, `rgw_fsync()`, and vector read/write are effectively unsupported or stubs. `tmp_fh` decode comments note unsound historical versioning logic. Xattrs are rejected on root/buckets, and exposed attrs are special-cased.

## Test Signals
Coverage should exercise mount authorization, bucket root lookup, object and directory lookup with/without fast attrs, create/mkdir/symlink conflicts, delete non-empty directories, copy-delete rename failure modes, contiguous and non-contiguous writes, close-triggered completion, readdir marker continuation, namespace GC invalidation callback, xattr prefix/exposed attr behavior, statfs cluster stats, and stale/deleted handle returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_file_int.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_file_int.h

## Purpose
Internal header for librgw file support. It defines the handle model, filesystem object, cache machinery, request adapters, and inline RGWOp subclasses used by `rgw_file.cc`.

## Important APIs, Types, And Functions
`fh_key` encodes hashed bucket/object identity and supports ordering/equality. `RGWFileHandle` wraps public `rgw_file_handle`, state/stat fields, directory/file variants, parent/bucket pointers, flags, LRU hooks, and methods such as `stat()`, `full_object_name()`, `make_fhk()`, `readdir()`, `write()`, `write_finish()`, `close()`, `encode_attrs()`, `decode_attrs()`, and `invalidate()`. `RGWLibFS` owns root state, user/key authorization data, FH cache/LRU, invalidate callbacks, write timer, and operation methods. Request adapters include list buckets, list bucket, rmdir check, create/delete bucket, put/get/delete/stat object, stat bucket/leaf, continued write, copy object, get/set/remove attrs, and cluster stat.

## Control Flow
Public C API calls enter `RGWLibFS` and create request objects declared here. Each request initializes a synthetic `req_state` with method/op/URI, overrides parameter and response hooks, then executes through `g_rgwlib->get_fe()`. File handles are found or inserted through `lookup_fh()`, which latches cache partitions, refs through LRU, and handles deletion/retry races.

## State And Persistence Behavior
`RGWFileHandle::State` mirrors Unix stat data, while persistent metadata is serialized by `encode_attrs()` into RGW attrs. Directories keep last marker and last readdir timestamp; files keep an active `RGWWriteRequest`. `RGWLibFS::State` queues namespace invalidation events. `RGWWriteRequest` owns streaming write pipeline state including SAL writer, compression filter, MD5 etag, byte counters, and timer id.

## Dependencies And Integration Points
Includes RGW lib, LDAP/token auth, put object processors, AIO throttle, compression, perf counters, checksums, common LRU/timer, and SAL driver/user classes. The request classes inherit existing RGW ops and rely on `RGWHandler::driver` setup by the lib frontend.

## Risks
The header is large and behavior-heavy, so inline changes affect ABI-like internal contracts. Locking mixes cache latches, FH mutexes, and LRU refs. Flags are dense; `FLAG_SYMBOLIC_LINK = 0x0009` overlaps other bits and is marked suspicious. Many request `header_init()` methods use synthetic URI/request fields with comments noting rough edges. Continued writes reject out-of-order chunks and rely on close/timer completion.

## Test Signals
Tests should stress FH cache ref/reclaim, locked/unlocked lookup paths, deleted-handle retries, attr encode/decode compatibility, directory marker continuation, request header setup, xattr prefixing, continued write start/continue/finish, and auth fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_file_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_flight.cc

## Purpose
Implements RGW's experimental Arrow Flight server. It registers Parquet object metadata as Flights and serves selected objects through Arrow Flight `DoGet` by reading RGW objects through SAL and converting Parquet to Arrow record batches.

## Important APIs, Types, And Functions
`FlightKeyToTicket()` and `TicketToFlightKey()` translate between internal keys and Flight tickets. `FlightData` stores object identity, schema, metadata, row/object sizes, and temporary user id. `MemoryFlightStore` provides in-memory keyed storage. `FlightServer` implements `ListFlights()` and `DoGet()`; `GetFlightInfo()` and `GetSchema()` are placeholders. Local classes `OwnedBuffer` and `RandomAccessObject` adapt RGW object reads to Arrow IO.

## Control Flow
`ListFlights()` returns a custom listing that iterates `FlightStore::after_key()` and builds `FlightInfo` descriptors from tenant, bucket, object key parts, endpoints, schema, row count, and object size. `DoGet()` parses the ticket, looks up `FlightData`, loads the RGW bucket, gets the object, wraps it in `RandomAccessObject`, opens a Parquet reader, reads the full table, converts the table to record batches, and returns a `RecordBatchStream`.

## State And Persistence Behavior
Flights are process-local only. `next_flight_key` is atomic but monotonic and not persisted. `MemoryFlightStore::remove_flight()` and `expire_flights()` are stubs, so entries accumulate for the lifetime of the frontend. `RandomAccessObject` owns a SAL read op and tracks current position/closed state.

## Dependencies And Integration Points
Depends on Arrow, Arrow Flight, Parquet Arrow reader, RGW SAL driver/bucket/object APIs, and Flight metadata produced by `FlightGetObj_Filter` in the frontend file.

## Risks
`GetFlightInfo()` and `GetSchema()` return OK without data. `DoGet()` reads an entire Parquet table into memory before streaming batches. Error paths after bucket load failures are incomplete. Authorization is TODO and user id is only carried as a placeholder. `MemoryFlightStore` returns copies of `FlightData`, and expiration/removal are unimplemented.

## Test Signals
Tests should cover ticket parse errors, missing flight keys, listing order, DoGet on valid Parquet objects, bucket/object load failures, partial/short reads, Parquet metadata compatibility, large object memory usage, and concurrent add/list/get.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_flight.h

## Purpose
Declares the Arrow Flight data model, store abstraction, server class, and utility owning string view used by RGW Flight support.

## Important APIs, Types, And Functions
`FlightData` records a Flight key, URI, tenant/bucket/object identity, record and object counts, Arrow schema, Parquet key/value metadata, and user id. `FlightStore` abstracts add/get/iterate/remove/expire. `MemoryFlightStore` implements the abstraction with a mutex-protected map. `FlightServer` derives from `arrow::flight::FlightServerBase` and declares `ListFlights()`, `GetFlightInfo()`, `GetSchema()`, and `DoGet()`. `OwningStringView` owns a heap buffer while presenting `std::string_view`.

## Control Flow
The header's intended flow is: frontend creates `MemoryFlightStore` and `FlightServer`, GET filters add `FlightData`, and Arrow Flight RPCs use `FlightServer` methods to list or retrieve registered Flights.

## State And Persistence Behavior
The declared `lifespan` constant suggests planned expiry, but expiration is not enforced by this header's concrete implementation. Store contents are in-memory only.

## Dependencies And Integration Points
Includes Arrow type/Flight server headers, Ceph context/time/logging, `rgw_frontend.h`, and `rgw_flight_frontend.h` for `FlightKey`. `FlightServer` holds `RGWProcessEnv`, SAL driver pointer, `DoutPrefix`, and `FlightStore`.

## Risks
The header exposes raw `FlightStore*` ownership through `FlightServer`; frontend lifecycle must delete in the right order. `OwningStringView` inherits from `std::string_view`, which is unusual and demands care with moves and destructor ownership.

## Test Signals
Compile and unit tests should cover `OwningStringView::make()/shrink()`, store polymorphism, Flight server construction, and lifecycle with frontend teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.cc

## Purpose
Implements the RGW frontend wrapper for Arrow Flight and a GET object filter that detects Parquet schema metadata while normal GET responses flow through RGW.

## Important APIs, Types, And Functions
`null_flight_key` is defined as zero. `FlightFrontend` constructs/deletes `MemoryFlightStore` and `FlightServer`, initializes server location/options, starts `ServeAlt()` in a named thread, shuts down and joins. `FlightGetObj_Filter` buffers GET data to a temporary file, reads Parquet metadata on completion, and adds a `FlightData` entry.

## Control Flow
Frontend construction installs store/server pointers into `RGWProcessEnv`. `init()` chooses port 8077 by default, parses `grpc+tcp://localhost:<port>`, and initializes Arrow Flight options with client verification disabled. `run()` spawns the server thread. `stop()` calls `Shutdown()` and `Wait()`. The filter writes each data buffer to a temp file, and after expected object size is reached, opens the file with Arrow, reads Parquet metadata/schema, and registers a flight.

## State And Persistence Behavior
State is frontend-process local. Temporary files are created with `tmpnam`, removed in the destructor, and only used to discover schema/row metadata. Registered flights persist in memory until frontend teardown because store expiration is not implemented.

## Dependencies And Integration Points
Depends on Arrow Flight, Arrow file IO, Parquet metadata/schema conversion, RGW op filter chain, `req_state`, process env, and `rgw_flight.h`.

## Risks
The code contains a compile-time warning for `tmpnam`, which is insecure and race-prone. The filter writes the entire object to local disk before metadata extraction. Server binds localhost only and disables client verification. Pause/resume ignores config changes. Error handling for temp-file open failure is minimal.

## Test Signals
Tests should verify lifecycle init/run/stop/join, invalid port/location handling, Parquet GET filter registration, temp-file cleanup on success/failure, schema failure behavior for non-Parquet data, and concurrent GETs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.h

## Purpose
Declares the Arrow Flight frontend and GET filter types that plug Flight support into RGW's frontend/process environment.

## Important APIs, Types, And Functions
`FlightKey` is a `uint32_t`, with `null_flight_key` defined externally. `FlightFrontend` implements `RGWFrontend` methods for lifecycle management. `FlightGetObj_Filter` derives from `RGWGetObj_Filter` and overrides `handle_data()`.

## Control Flow
The frontend is configured and owned like other RGW frontends. The filter is intended to be inserted into object GET response pipelines so data can be observed, metadata extracted, and then forwarded to the next filter.

## State And Persistence Behavior
`FlightFrontend` owns a server thread and references process env. `FlightGetObj_Filter` tracks offsets, expected size, object identity, temp-file stream/name, schema status, and user id for eventual `FlightData` creation.

## Dependencies And Integration Points
Includes `rgw_frontend.h`, `rgw_op.h`, Arrow status, and common forward/thread definitions. Integrates with `RGWProcessEnv` fields `flight_store` and `flight_server`.

## Risks
The filter stores a const reference to process env and an ofstream, so destruction order and filter lifetime matter. Auth is marked TODO. Namespace and object instance handling are noted as incomplete.

## Test Signals
Compile-time tests should ensure frontend polymorphism and filter chaining. Runtime tests should verify handle_data forwards data and registers flights only after complete objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_formats.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_formats.cc

## Purpose
Implements RGW-specific formatters: a legacy/plain formatter for simple responses and an HTML formatter for Swift static website directory listings.

## Important APIs, Types, And Functions
`RGWFormatter_Plain` implements `Formatter` methods for opening/closing sections, dumping scalar values, buffering output, flushing, and reset. `write_data()` handles dynamic buffer growth around `vsnprintf()`. `HTMLHelper` exposes XML escaping. `RGWSwiftWebsiteListingFormatter` generates header/footer rows and object/subdir rows.

## Control Flow
Plain formatter tracks a section stack and prints only the first value at the minimum stack level unless `use_kv` is enabled. Dumps append to an internal null-terminated buffer and `flush()` writes it to an output stream. Swift listing formatter writes a complete HTML table with optional stylesheet link, parent row, escaped/link-encoded object names, sizes, and mtimes.

## State And Persistence Behavior
All state is in-process formatting state: buffer pointer/length/capacity, stack, `min_stack_level`, `use_kv`, and `wrote_something`. No persistence.

## Dependencies And Integration Points
Uses Ceph `Formatter`, `XMLFormatter`, RGW common/rest helpers, URL encoding, XML escaping, `dump_time_to_str()`, and Boost format. Used by RGW response paths that need plain, key/value, or Swift website listing output.

## Risks
`dump_stream()` aborts. Manual malloc/realloc/free and null-termination require care. `close_section()` assumes a non-empty stack. Plain formatting is documented as a hack and may not match structured formatter semantics. HTML output must continue escaping names to avoid injection.

## Test Signals
Tests should cover scalar dumps in plain and key/value modes, nested sections, buffer growth beyond 4096 bytes, flush/reset reuse, object/subdir HTML escaping, CSS path URL encoding, and parent row generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_formats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_formats.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_formats.h

## Purpose
Declares RGW formatter helpers used by REST and website-listing response code.

## Important APIs, Types, And Functions
`plain_stack_entry` records array/object state and item count. `RGWFormatter_Plain` derives from `Formatter` and exposes plain dump/flush/reset methods. `RGWSwiftWebsiteListingFormatter` emits website listing HTML. `RGWFormatterFlusher` abstracts delayed formatter flushing; `RGWStreamFlusher` writes to an `ostream`; `RGWNullFlusher` discards flushes.

## Control Flow
Callers write through `Formatter` methods, then `RGWFormatterFlusher::start()` and `flush()` coordinate response start/flush. Website callers generate header, object/subdir rows, then footer.

## State And Persistence Behavior
Only transient formatting state. `RGWFormatterFlusher` records whether output was started/flushed, which response code can inspect.

## Dependencies And Integration Points
Depends on Ceph `Formatter`, standard strings/streams/lists, and `rgw_bucket_dir_entry` from included RGW headers in implementation contexts.

## Risks
`RGWNullFlusher` has a null formatter pointer, so callers must not dereference it. Plain formatter owns a raw char buffer. The header notes the plain formatter is misnamed and legacy.

## Test Signals
Compile tests should validate polymorphic formatter use; behavior tests should cover flush state transitions and null flusher use in paths that intentionally suppress body output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_formats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_frontend.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_frontend.cc

## Purpose
Implements common RGW frontend configuration parsing and process frontend shutdown behavior.

## Important APIs, Types, And Functions
`RGWFrontendConfig::parse_config()` tokenizes a frontend config string, stores the first token as framework, and parses subsequent tokens as key/value or key-only multimap entries. `set_default_config()` merges defaults. `get_val()` overloads read optional, string, and integer values. `RGWProcessFrontend::stop()` closes the process fd and signals its control thread.

## Control Flow
Frontend config construction calls `init()`, which invokes `parse_config()`. Callers then query framework and config values. Process frontend shutdown calls `pprocess->close_fd()` and sends `SIGUSR1` to wake/stop the worker thread.

## State And Persistence Behavior
State is transient: raw config string, parsed multimap, and framework name.

## Dependencies And Integration Points
Uses `get_str_vec()` and `parse_key_value()` from Ceph string helpers, `strict_strtol()` through included headers, global Ceph logging, and `RGWProcessFrontend` objects declared in `rgw_frontend.h`.

## Risks
`get_val(int)` returns `bool` but returns `-EINVAL` on parse error, which converts to true and can confuse callers. Config splitting is whitespace-based and does not support quoted values with spaces. `parse_config()` logs at level 0 for every key.

## Test Signals
Tests should cover framework-only configs, key-only entries, key/value parsing, defaults merging without overwriting, invalid integer values, and stop behavior with a live process thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_frontend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_frontend.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_frontend.h

## Purpose
Declares the shared RGW frontend abstraction, process frontend base, loadgen frontend, and realm reload pauser.

## Important APIs, Types, And Functions
`RGWFrontendConfig` owns parsed config and retrieval helpers. `RGWFrontend` is the lifecycle interface. `RGWProcessFrontend` owns `RGWProcess`, `RGWProcessEnv`, and a control thread. `RGWLoadGenFrontend` initializes loadgen process credentials. `RGWFrontendPauser` pauses/resumes all frontends during realm reload.

## Control Flow
Concrete frontends call `init()`, `run()`, `stop()`, and `join()` through `RGWFrontend`. `RGWProcessFrontend::run()` starts `RGWProcessControlThread`; pause/resume delegates to the process. Loadgen init reads `num_threads`, `prefix`, and required `uid`, loads the user, selects an access key, and configures the process.

## State And Persistence Behavior
No persistent state. Frontend instances own process/thread pointers and borrowed config/env pointers. Pauser holds references to a frontend vector and optional nested pauser.

## Dependencies And Integration Points
Depends on RGW request/process/process env, realm reloader, auth registry, SAL RADOS, and dmclock forward declarations.

## Risks
Ownership is raw-pointer based in `RGWProcessFrontend`. `join()` assumes `thread` is valid. Loadgen requires a user with an access key and returns errors for missing credentials. Pauser resumes frontends before optional nested pauser, which is an ordering contract worth preserving.

## Test Signals
Tests should cover lifecycle ordering, pause/resume propagation, loadgen missing uid, missing access keys, failed user load, and default config lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_frontend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_gc_log.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_gc_log.h

## Purpose
Declares helper functions that encode RGW garbage-collection queue operations into `librados::ObjectWriteOperation`s.

## Important APIs, Types, And Functions
The functions are `gc_log_init2()`, `gc_log_enqueue1()`, `gc_log_enqueue2()`, `gc_log_defer1()`, and `gc_log_defer2()`. They operate on `cls_rgw_gc_obj_info` entries with expiration values and queue sizing/deferred parameters.

## Control Flow
Callers prepare an object write operation, invoke one of these helpers to append cls_rgw GC operations, and submit the write through RADOS. The `1` helpers are comments-described as omap-oriented legacy operations, while `2` helpers target the cls_rgw GC queue.

## State And Persistence Behavior
This header does not hold state; persistence occurs when the resulting object write operation is submitted to RADOS/cls_rgw.

## Dependencies And Integration Points
Depends on `include/rados/librados.hpp` and `cls/rgw/cls_rgw_types.h`. It integrates RGW object deletion/lifecycle cleanup paths with the cls_rgw garbage collection log.

## Risks
Only declarations are present here, so callers depend on implementation semantics elsewhere. Version suffixes can be confusing without knowing which on-disk queue format is expected.

## Test Signals
Tests should verify encoded operations initialize queue sizing, enqueue expiration/object info, defer existing entries, and remain compatible with cls_rgw queue readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_gc_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_hex.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_hex.h

## Purpose
Provides small inline helpers for converting binary buffers to lowercase hex and hex strings back to bytes.

## Important APIs, Types, And Functions
`buf_to_hex(input_range, output_iterator)` writes two lowercase hex chars per input byte. `buf_to_hex(std::array<unsigned char, N>)` returns a null-terminated `std::array<char, N*2+1>`. `hexdigit()` parses one hex digit. `hex_to_buf()` decodes a null-terminated hex string into a fixed-size output buffer and returns bytes written or negative errno.

## Control Flow
Encoding casts each input element to `uint8_t`, emits high and low nibbles through the static hex table, and returns the advanced iterator. Decoding loops over pairs of chars, validates each digit, checks destination capacity, and rejects odd-length input.

## State And Persistence Behavior
No state or persistence; all helpers are inline/stateless.

## Dependencies And Integration Points
Uses C++20 ranges/output iterator constraints, `std::array`, ctype, errno values, and standard integer types. RGW write code uses `buf_to_hex()` for MD5 etag formatting.

## Risks
`hexdigit()` passes `char` to `toupper()` without unsigned conversion; non-ASCII signed chars are theoretically unsafe, though hex input should be ASCII. `hex_to_buf()` requires a null-terminated input and cannot decode embedded nulls.

## Test Signals
Tests should cover empty arrays, all byte values, uppercase/lowercase decode, odd-length strings, invalid characters, output buffer too small, and iterator return position.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_hex.h -->
