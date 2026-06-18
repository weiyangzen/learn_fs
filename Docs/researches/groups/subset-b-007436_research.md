# Research: subset-b-007436

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/hdfs.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/hdfs.cc

## Purpose
This file is the libhdfs-compatible C binding for libhdfspp. It wraps the C++ `FileSystem` and `FileHandle` objects in opaque C handles, translates C API calls into synchronous C++ operations, exposes selected libhdfspp extensions, and normalizes errors into `errno`, negative return codes, and a thread-local last-error string.

## Important APIs, Types, And Functions
`hdfs_internal` owns a `FileSystem` and a mutex-protected working directory; `hdfsFile_internal` owns a `FileHandle`. The exported API covers connection setup (`hdfsConnect*`, `hdfsBuilderConnect`, `hdfsAllocateFileSystem`, `hdfsConnectAllocated`, `hdfsCancelPendingConnection`, `hdfsDisconnect`), file access (`hdfsOpenFile`, `hdfsCloseFile`, `hdfsRead`, `hdfsPread`, `hdfsSeek`, `hdfsTell`, read statistics, cancellation), namespace operations (`hdfsExists`, `hdfsGetPathInfo`, `hdfsListDirectory`, `hdfsCreateDirectory`, `hdfsDelete`, `hdfsRename`, `hdfsChmod`, `hdfsChown`, snapshots, `hdfsFind`), block-location helpers (`hdfsGetBlockLocations`, `hdfsGetHosts`), builder configuration getters/setters, event pre-attach hooks, and logging functions. `Error`, `ReportError`, `ReportException`, `CheckSystem`, `CheckHandle`, and `getAbsolutePath` are the main shared glue.

## Control Flow
Connection calls construct an `IoService`, create a `FileSystem` with the selected user and `Options`, attach any thread-local event callback, then either connect to an explicit namenode or the configured default filesystem. Most C functions validate opaque handles, resolve relative paths against the per-handle working directory, call the equivalent `FileSystem` or `FileHandle` method, then convert `Status` to libhdfs-style return values. The builder path loads `core-site.xml` and `hdfs-site.xml` through `ConfigurationLoader`, overlays per-builder values, and frees the builder on `hdfsBuilderConnect`. Directory/stat calls allocate C structs and strings that are later released by paired free functions. Logging installs a `CForwardingLogger` that converts C++ `LogMessage` data to the public C `LogData` layout.

## State And Persistence
State is process-local and in-memory: opaque handles own C++ objects, `hdfs_internal` stores a working directory string guarded by `wd_lock_`, `errstr` stores the last error per thread, and event callbacks are thread-local templates for subsequently opened filesystems/files. The file allocates C arrays and strings for caller-owned `hdfsFileInfo`, block-location, host, statistics, and log-copy outputs. No durable state is written; HDFS mutations are delegated to the remote namenode.

## Dependencies And Integration Points
The binding depends on libhdfspp public headers, `common/hdfs_configuration.h`, `ConfigurationLoader`, logging, `fs/filesystem.h`, `fs/filehandle.h`, x-platform basename/syscall helpers, and the event and log C extension headers. It is the compatibility boundary for existing libhdfs consumers while still exposing libhdfspp-only features such as monitor callbacks, preallocated filesystem connection, snapshot helpers, cancellation, and structured block locations.

## Risks
The file is a high-risk ownership and compatibility boundary. Many functions allocate memory manually and depend on callers invoking the matching free API. `hdfsConnectAsUser` unconditionally constructs `std::string(nn)` and `std::string(user)`, so null inputs are dangerous unless callers follow libhdfs conventions. `hdfsFreeHosts` uses `delete` for an array allocated with `new[]`, which is an allocator-pairing risk. Relative path handling intentionally lacks `.` and `..` semantics. Only read mode is meaningfully implemented; write checks are placeholders. Several functions return positive errno-like values on extension paths while classic libhdfs calls return `-1`, so callers must follow each API contract exactly.

## Test Signals
Useful tests connect through explicit namenode, default FS, builder config, and allocated-connect paths; verify thread-local error strings; read files with `hdfsRead`, `hdfsPread`, seek/tell, and cancellation; exercise path resolution after `hdfsSetWorkingDirectory`; allocate/free file info, hosts, block locations, read statistics, and log data under ASAN; run namespace mutations and snapshot calls against a mini cluster; and attach monitor/log callbacks that return normal and simulated-error responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/c/hdfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/CMakeLists.txt

## Purpose
Defines the `common_obj` object library and the concrete `common` library for the native libhdfspp common layer. It centralizes utility, configuration, status, logging, retry, auth, formatting, and lock sources used by filesystem, RPC, reader, and binding modules.

## Important APIs, Types, And Functions
The build file conditionally links `dl` through `LIB_DL`, includes Boost and public include directories, and composes `common_obj` from `status.cc`, `sasl_digest_md5.cc`, `ioservice_impl.cc`, `options.cc`, `configuration*.cc`, `hdfs_configuration.cc`, `uri.cc`, `util.cc`, `retry_policy.cc`, `cancel_tracker.cc`, `logging.cc`, `libhdfs_events_impl.cc`, `auth_info.cc`, `namenode_info.cc`, `statinfo.cc`, `fsinfo.cc`, `content_summary.cc`, `locks.cc`, and `config_parser.cc`. It also folds in `x_platform_obj` and `uriparser2_obj` for the final `common` target.

## Control Flow
CMake first sets `LIB_DL` if dynamic-loader linkage is needed, then builds an object target for reuse and a normal library target for link consumers. Private include paths point at `../../lib`, making internal headers visible to common sources and downstream modules.

## State And Persistence
There is no runtime state. Build state is encoded in target membership and transitive object inclusion.

## Dependencies And Integration Points
This is the build integration point between Boost, x-platform portability code, the URI parser object target, and higher-level native HDFS components. If a new common source is added but omitted here, dependent libraries can compile headers but fail at link time.

## Risks
The object-library composition duplicates `x_platform_obj` in both `common_obj` and `common`, so changes should preserve existing linker expectations. Conditional `dl` linkage is platform-sensitive. Missing include directories or omitted source files can surface as downstream failures far away from this CMake file.

## Test Signals
Signals are clean CMake configuration on platforms with and without `NEED_LINK_DL`, successful native-client library links, and targeted tests that instantiate symbols from every common source file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/async_stream.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/async_stream.h

## Purpose
Declares the minimal asio-compatible `AsyncStream` abstraction used by libhdfspp networking code. It lets block readers and continuations operate on stream-like objects without binding directly to `boost::asio::ip::tcp::socket`.

## Important APIs, Types, And Functions
`MutableBuffer` and `ConstBuffer` alias Boost one-buffer types. `AsyncStream` declares pure virtual `async_read_some` and `async_write_some` methods and exposes `get_executor()` returning a `boost::asio::system_executor`.

## Control Flow
Concrete streams such as `DataNodeConnectionImpl` implement the virtual methods, usually forwarding to an underlying socket. Asio continuations call these methods and receive Boost error-code and byte-count callbacks.

## State And Persistence
The class stores only a default system executor. It has no durable or remote state and no built-in synchronization; the comments state read/write calls are not thread-safe.

## Dependencies And Integration Points
It depends on Boost.Asio buffer and executor types and is consumed by DataNode connection and reader code. The abstraction is also convenient for socket mocks in tests.

## Risks
The executor returned here is a system executor, not necessarily the executor of a concrete socket, so code that assumes stream-local executor affinity can be wrong. Implementors must enforce their own lifetime, cancellation, and serialization rules.

## Test Signals
Compile-time tests should confirm socket-backed and mock streams satisfy the interface. Runtime tests should ensure read/write handlers are invoked with correct byte counts and error propagation under cancellation and short I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/async_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.cc

## Purpose
Provides the translation unit for `auth_info.h`. It currently contains no executable logic beyond including the header, giving the build a source file for auth metadata symbols if needed.

## Important APIs, Types, And Functions
All important declarations live in `auth_info.h`: `Token` and `AuthInfo`.

## Control Flow
There is no control flow in this file.

## State And Persistence
No state is introduced here.

## Dependencies And Integration Points
The file participates in the `common_obj` library and ensures auth metadata is part of the common build set.

## Risks
The practical risk is drift: future non-inline auth logic must be added here and kept listed in `common/CMakeLists.txt`.

## Test Signals
Build coverage is the main signal; auth behavior is tested through the header users and SASL/RPC integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.h

## Purpose
Defines lightweight authentication metadata passed through libhdfspp connection and RPC layers. It records whether a connection uses simple auth, Kerberos/SASL, token auth, or failure/unknown states and optionally stores a delegation token.

## Important APIs, Types, And Functions
`Token` stores `identifier` and `password`. `AuthInfo` exposes `AuthMethod`, `useSASL()`, `getUser`/`setUser`, `getMethod`/`setMethod`, `getToken`, `setToken`, and `clearToken`. The default method is `kSimple`.

## Control Flow
Callers construct `AuthInfo`, set a user/method/token while negotiating connection options, and then use `useSASL()` to choose simple protocol flow versus SASL-capable authentication.

## State And Persistence
State is per-object and in-memory. Token data is stored as strings in an `std::experimental::optional`; there is no secure wiping or persistence.

## Dependencies And Integration Points
It depends on the local optional wrapper and integrates with RPC/DataTransfer authentication setup, including DIGEST-MD5 and token-based flows.

## Risks
Token strings remain in normal heap memory. `useSASL()` treats all non-simple methods, including unknown/failure markers, as SASL candidates, so callers must validate method transitions explicitly.

## Test Signals
Unit tests should cover default simple auth, token set/clear, user propagation, and method decisions used by RPC and DataNode authentication code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/auth_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.cc

## Purpose
Implements `CancelTracker`, the shared cancellation flag used by asynchronous continuation pipelines and file read operations.

## Important APIs, Types, And Functions
The implementation provides the constructor, `CancelTracker::New()`, `is_canceled()`, and `set_canceled()`.

## Control Flow
Users create a shared tracker, pass it into asynchronous pipelines or readers, and call `set_canceled()` when the owning operation should stop. Pipelines poll `is_canceled()` between stages and convert cancellation into `Status::Canceled()`.

## State And Persistence
The only state is an `std::atomic_bool canceled_`, initialized false and flipped true permanently for a tracker instance. It is in-memory and safe for concurrent polling.

## Dependencies And Integration Points
Used by `continuation::Pipeline`, `FileHandleImpl`, and block readers to coordinate logical cancellation with socket close/cancel behavior.

## Risks
Cancellation is cooperative except where callers also close sockets. Long-running stages that do not check the flag will continue until their callback boundary.

## Test Signals
Tests should verify initial false state, one-way true transition, visibility across threads, and pipeline/file-read completion with `Status::Canceled()` after cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.h

## Purpose
Declares `CancelTracker` and the `CancelHandle` alias used to share cancellation state across asynchronous HDFS operations.

## Important APIs, Types, And Functions
`CancelTracker` derives from `enable_shared_from_this`, has `New()`, `set_canceled()`, and `is_canceled()`. `CancelHandle` is `std::shared_ptr<CancelTracker>`.

## Control Flow
Owners allocate a tracker and hand shared pointers to continuations, readers, or file handles. Consumers poll the flag before scheduling the next action.

## State And Persistence
State is an atomic cancellation bit. There is no reset API and no external persistence.

## Dependencies And Integration Points
This header is included by continuation and file-handle code and forms the cancellation contract for async operations.

## Risks
The class exposes no reason or generation counter, so reusing a canceled handle for a new operation will immediately cancel it. `enable_shared_from_this` is unused here but implies shared ownership assumptions.

## Test Signals
Compile and concurrency tests should confirm the shared handle can be passed through async code and cancellation is observed without data races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/cancel_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/config_parser.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/config_parser.cc

## Purpose
Implements the public `ConfigParser` facade over `ConfigurationLoader` and `HdfsConfiguration`. It gives clients typed access to Hadoop XML configuration values and resolved libhdfspp `Options` without exposing loader internals.

## Important APIs, Types, And Functions
`ConfigParser::impl` owns a `ConfigurationLoader` and `HdfsConfiguration`. Constructors accept no path, a vector of directories, or a colon-separated path. Public methods include `LoadDefaultResources`, `ValidateResources`, `get_int/string/bool/double/uri/options`, and `_or` variants that return caller-supplied defaults.

## Control Flow
Construction creates a new empty config, optionally sets the search path, and loads default resources. Vector paths are folded into a colon-separated search path. Getters ask `HdfsConfiguration` for an optional typed value; the `_or` helpers fall back when no value is present.

## State And Persistence
The parser owns an immutable snapshot of parsed config in memory. Move construction/assignment is defaulted; no config is written back to disk.

## Dependencies And Integration Points
It depends on `hdfspp/config_parser.h`, `HdfsConfiguration`, `ConfigurationLoader`, `Status`, and `URI`. It is a higher-level API entry for applications that need configuration parsing without creating a filesystem.

## Risks
The vector path accumulation prepends a separator before the first element, relying on `SetSearchPath` to ignore the empty component. Typed conversions inherit the permissive parsing behavior of `Configuration`, including partial numeric parses. `LoadDefaultResources` always returns true after assignment, even if no resources were found and an empty config was used.

## Test Signals
Tests should parse real `core-site.xml`/`hdfs-site.xml`, custom search paths, missing resources, typed values, defaults, URI parse failures, HA options, and move semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/config_parser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.cc

## Purpose
Implements the immutable `Configuration` value object used to store Hadoop XML properties and retrieve them as strings, integers, doubles, booleans, and URIs.

## Important APIs, Types, And Functions
`GetDefaultFilenames()` returns `core-site.xml`. `Get`, `GetWithDefault`, `GetInt`, `GetDouble`, `GetBool`, `GetUri`, and their default variants read from `raw_values_`. `fixCase()` uppercases keys so lookups are case-insensitive.

## Control Flow
Each getter normalizes the key, looks in the parsed map, and converts the raw string if needed. Numeric getters use `strtol`/`strtod`, boolean accepts case-insensitive `true`/`false`, and URI parsing catches `uri_parse_error` and returns empty optional on failure.

## State And Persistence
State is a copyable `ConfigMap` of uppercase key to `ConfigData {value, final}`. Once constructed by `ConfigurationLoader`, callers only read it; no durable writes occur.

## Dependencies And Integration Points
The class depends on `URI`, the optional wrapper, and x-platform case-insensitive comparison. `HdfsConfiguration` subclasses it to interpret HDFS-specific keys.

## Risks
Numeric parsing does not require the whole string to be consumed, so values with numeric prefixes may be accepted. `fixCase()` calls `toupper` on `char`, which can be locale/negative-char sensitive. Unsupported Hadoop config features are explicitly noted: substitutions, ranges, byte/time units, string lists, and deprecated values.

## Test Signals
Tests should cover case-insensitive lookup, missing values, invalid and range-overflow numerics, booleans, URI errors, default handling, `final` propagation through loader-created maps, and thread-safe sharing of copied configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.h

## Purpose
Declares the `Configuration` class and its protected storage contract for Hadoop-style XML configuration data.

## Important APIs, Types, And Functions
The header exposes typed getters, protected `ConfigData`, `ConfigMap`, constructors used by `ConfigurationLoader`, `GetDefaultFilenames`, `raw_values_`, and `fixCase`. It also defines `hdfs::optional<T>` as `std::experimental::optional<T>`.

## Control Flow
Runtime control flow is implemented in `configuration.cc`; this header defines the read-only public surface and grants `ConfigurationLoader` friend access to construct populated instances.

## State And Persistence
`raw_values_` stores all parsed properties. The comments document the intended immutable/thread-safe model after construction.

## Dependencies And Integration Points
Used by `ConfigurationLoader`, `HdfsConfiguration`, `ConfigParser`, and C builder configuration APIs.

## Risks
Because `raw_values_` is non-const for copyability and protected for loader/subclass construction, immutability is by convention. New subclasses must preserve that contract.

## Test Signals
Compile tests should verify loader friendship and subclass construction; behavior tests live with `configuration.cc` and loader overlays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.cc

## Purpose
Implements `ConfigurationLoader`, which searches Hadoop configuration directories, validates XML resources, and overlays property maps from files, streams, strings, or direct key/value settings.

## Important APIs, Types, And Functions
Important functions include `SetDefaultSearchPath`, `ClearSearchPath`, `SetSearchPath`, `AddToSearchPath`, `GetSearchPath`, `ValidateResources`, `UpdateMapWithFile`, `UpdateMapWithStream`, `UpdateMapWithString`, `UpdateMapWithBytes`, and `UpdateMapWithValue`. Helpers parse boolean `final` values and validate streams with RapidXML.

## Control Flow
The constructor seeds the search path from `$HADOOP_CONF_DIR` or `/etc/hadoop/conf`. Loading opens absolute paths directly or walks the search path for relative names. XML parsing requires a `<configuration>` root, then scans `<property>` children supporting both nested `<name>/<value>/<final>` nodes and attribute forms. Overlay writes uppercase keys unless an existing entry is marked final.

## State And Persistence
The loader stores only `search_path_`. Parsed maps are local copies used to construct immutable `Configuration`/`HdfsConfiguration` instances. No files are modified.

## Dependencies And Integration Points
Depends on RapidXML, `Status`, logging, and x-platform case-insensitive bool comparison. It is used by the C builder, `ConfigParser`, and `HdfsConfiguration` default loading.

## Risks
The search path separator is always `:`, even on Windows while file separator changes. Stream length is stored in `int`, which is unsuitable for very large files. Parse errors in normal load paths collapse to `false` without detailed `Status`. Final-value rejection returns false for that individual property but the caller often treats the overall file load as successful.

## Test Signals
Tests should cover env/default search paths, colon path parsing, absolute and relative file lookup, empty and invalid XML validation, property node and attribute styles, final overwrite prevention, multiple default resources, and Windows path behavior if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.h

## Purpose
Declares the templated `ConfigurationLoader` API for creating, loading, overlaying, and validating typed `Configuration` subclasses.

## Important APIs, Types, And Functions
The public template methods are `NewConfig`, `Load`, `LoadFromStream`, `LoadFromFile`, `OverlayResourceString`, `OverlayResourceStream`, `OverlayResourceFile`, `OverlayValue`, `LoadDefaultResources`, and `ValidateDefaultResources`. Search-path methods manage the loader's directory list. Protected methods update maps from files, streams, strings, bytes, or individual values.

## Control Flow
Template definitions are included from `configuration_loader_impl.h`, while non-template path and XML parsing logic is implemented in `configuration_loader.cc`.

## State And Persistence
`search_path_` is mutable loader state. Generated configurations receive copied maps; persistence is external to this class.

## Dependencies And Integration Points
This header is the construction gateway for `Configuration` and `HdfsConfiguration` because those constructors are protected/friend-only.

## Risks
Template users can instantiate the loader for subclasses that do not follow the expected constructor/static method contract, leading to compile errors. Search path mutation is not synchronized, so loaders should not be mutated concurrently.

## Test Signals
Build tests should instantiate all template methods for `Configuration` and `HdfsConfiguration`; behavior tests should verify overlay and validation results against concrete XML fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader_impl.h

## Purpose
Provides the inline template implementations for `ConfigurationLoader`. It converts parsed `ConfigMap` copies into typed configuration objects and implements the generic overlay/default-resource logic.

## Important APIs, Types, And Functions
Defines `NewConfig`, `Load`, `LoadFromStream`, `LoadFromFile`, `OverlayResourceFile`, `OverlayResourceStream`, `OverlayResourceString`, `OverlayValue`, `LoadDefaultResources`, and `ValidateDefaultResources`.

## Control Flow
Each overlay method copies `src.raw_values_`, updates the copy from a source, and returns an optional `T` only on success. Default-resource loading iterates `T::GetDefaultFilenames()` and succeeds if any resource updates the map. `OverlayValue` always returns a config after attempting to update one value.

## State And Persistence
No independent state exists; it operates on loader search paths and local map copies. Output configs are in-memory snapshots.

## Dependencies And Integration Points
Included at the bottom of `configuration_loader.h`, so all template logic is visible to translation units using the loader.

## Risks
`OverlayValue` ignores the boolean result from `UpdateMapWithValue`, so attempts to override a final key silently return an unchanged map. Default-resource loading treats partial success as success, which is correct for Hadoop layering but can hide missing secondary resources unless validation is called.

## Test Signals
Tests should assert optional empty results for invalid resources, final-value overlay behavior, default-resource partial loading, and direct key overlay semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/content_summary.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/content_summary.cc

## Purpose
Implements formatting for `ContentSummary`, the libhdfspp representation of HDFS content summary output.

## Important APIs, Types, And Functions
The constructor initializes length, file count, directory count, quota, consumed space, and space quota to zero. `str(bool include_quota)` renders content-summary columns, while `str_du()` renders a `du`-style line with left-padded length and path.

## Control Flow
Formatting functions build a `stringstream` from already-populated fields; `include_quota` controls whether quota columns are emitted.

## State And Persistence
State is per-object counters and path, populated elsewhere from namenode responses. No persistence or mutation beyond construction is performed here.

## Dependencies And Integration Points
Used by public content-summary APIs and CLI-style display code. Depends on `hdfspp/content_summary.h` and iostream formatting.

## Risks
The output format is positional and may be consumed by tests or clients, so spacing/column changes can break compatibility. Zero quota defaults may be ambiguous when quota is not requested.

## Test Signals
Tests should compare `str()` with and without quota and `str_du()` for empty and populated summaries, including paths with spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/content_summary.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/asio.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/asio.h

## Purpose
Defines a continuation stage that writes an Asio buffer sequence to a stream as part of libhdfspp's continuation-passing async framework.

## Important APIs, Types, And Functions
`asio_continuation::WriteContinuation<Stream, ConstBufferSequence>` stores a shared stream and buffer sequence, and `Write()` allocates the stage. `Run()` calls `boost::asio::async_write` and maps the resulting error code through `ToStatus`.

## Control Flow
When a pipeline reaches the stage, `Run()` starts an async write. The completion handler invokes the pipeline's `next` callback with OK or error status.

## State And Persistence
The continuation owns a shared pointer to the stream and a copy of the buffer sequence until completion. No persistent state exists.

## Dependencies And Integration Points
Depends on `continuation.h`, `common/util.h`, Boost.Asio write, and `Status`. It is used by RPC/DataTransfer protocol code that sends framed data asynchronously.

## Risks
The buffer sequence must reference memory that remains valid through the async write; copying the sequence does not copy pointed-to data for all buffer types. Stages are heap-allocated and owned by `Pipeline`, so callers must not reuse raw pointers.

## Test Signals
Mock-stream tests should verify successful write, error propagation, pipeline sequencing, and lifetime of shared streams and backing buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/asio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/continuation.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/continuation.h

## Purpose
Implements a small continuation-passing-style pipeline framework used to sequence asynchronous libhdfspp operations without deeply nested callbacks.

## Important APIs, Types, And Functions
`Continuation` defines `Run(const Next&)`. `Pipeline<State>` owns a state object, a vector of continuation stages, a current stage index, a user completion handler, and a `CancelHandle`. Key methods are `Create`, `Push`, `Run`, `state`, and private `Schedule`.

## Control Flow
Callers heap-create a pipeline, push stages, populate `state()`, and call `Run()`. `Schedule` checks cancellation, stops on non-OK status or end-of-stages, invokes the user handler, clears stages, and deletes the pipeline. Otherwise it runs the next stage with a bound callback back into `Schedule`.

## State And Persistence
Pipeline state and stages live only for one async operation and self-delete on completion. Cancellation is shared through `CancelTracker`; no durable state exists.

## Dependencies And Integration Points
Used by RPC and block reader flows with continuation stages from `asio.h`, `protobuf.h`, and protocol-specific code.

## Risks
Self-deletion requires every async path to call `next` at most once and never touch the pipeline afterward. A stage that never calls `next` leaks the pipeline and stalls the operation. Cancellation is only observed between stages.

## Test Signals
Tests should cover ordered stage execution, early error, cancellation before and during stages, handler state visibility, and double-callback or missing-callback defensive behavior in higher-level code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/continuation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/protobuf.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/protobuf.h

## Purpose
Provides continuation stages for reading and writing length-delimited protobuf messages over Asio streams.

## Important APIs, Types, And Functions
`ReadDelimitedPBMessageContinuation<Stream, MaxMessageSize>` reads a varint length plus message into a fixed array, then merges into a `MessageLite`. `WriteDelimitedPBMessageContinuation<Stream>` serializes a delimited protobuf with `SerializeDelimitedProtobufMessage` and writes it. Factory helpers return heap-allocated continuation stages.

## Control Flow
The read stage uses `boost::asio::async_read` with a custom completion condition that keeps requesting bytes until the varint length and payload are present. The write stage serializes first, fails immediately on serialization error, otherwise async-writes the buffer and forwards status.

## State And Persistence
Read state includes the shared stream, destination message pointer, and fixed buffer. Write state includes the shared stream, source message pointer, and serialized string buffer. No persistent state exists.

## Dependencies And Integration Points
Depends on Boost.Asio, protobuf lite, coded streams, and `common/util.h`. It is used by wire-protocol components that exchange protobuf headers/messages.

## Risks
Read parsing uses `assert` for varint/message success and message-size bounds, which disappears in release builds. The default max read buffer is only 512 bytes, so larger messages need explicit template sizing. The write factory takes a non-const message pointer even though the continuation stores a const pointer.

## Test Signals
Tests should read/write normal messages, messages near and above `MaxMessageSize`, malformed varints, serialization failures, async stream errors, and release-mode behavior when assertions are compiled out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/continuation/protobuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/fsinfo.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/fsinfo.cc

## Purpose
Implements display formatting for HDFS filesystem capacity statistics represented by `FsInfo`.

## Important APIs, Types, And Functions
The constructor zero-initializes capacity, used, remaining, under-replicated, corrupt, missing, missing-replication-one, and future-block counters. `str(fs_name)` prints a two-line table with filesystem, size, used, available, and use percentage.

## Control Flow
`str` computes column widths from labels and values, calculates `used * 100 / capacity`, and formats a header plus one data line.

## State And Persistence
State is per-object counters populated by namenode stats calls. No persistence exists.

## Dependencies And Integration Points
Used by C binding capacity/used APIs and any CLI-like display of `GetFsStats`.

## Risks
If `capacity` is zero, `str()` divides by zero. Formatting only covers a subset of stored counters, so callers needing under-replication or corruption data must read fields directly.

## Test Signals
Tests should cover nonzero stats formatting, large values, long filesystem names, and the zero-capacity edge case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/fsinfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.cc

## Purpose
Implements HDFS-specific interpretation of generic Hadoop configuration into libhdfspp `Options`, including default resource names, HA nameservice parsing, authentication mode, timeouts, retries, failover limits, default filesystem, and block size.

## Important APIs, Types, And Functions
`HdfsConfiguration::GetDefaultFilenames()` adds `hdfs-site.xml` to `core-site.xml`. Helpers include `OptionalSet`, `SplitOnComma`, `RemoveSpaces`, `PrependHdfsScheme`, and `LookupNameService`. `GetOptions()` is the main exported behavior.

## Control Flow
`GetOptions()` starts from default `Options`, overlays known numeric/URI keys, parses `dfs.nameservices`, and for each service reads `dfs.ha.namenodes.<service>` plus `dfs.namenode.rpc-address.<service>.<node>`. Missing schemes are prefixed with `hdfs://`. Authentication is mapped to Kerberos only when the configured value matches `kerberos`; otherwise simple auth is used.

## State And Persistence
The object is an immutable config snapshot. Derived `Options` is a new value containing HA service maps and scalar settings. No files are written.

## Dependencies And Integration Points
Depends on `Configuration`, `Options`, `NamenodeInfo`, `URI`, and logging. It feeds `FileSystem::New`, C builder connection paths, and HA failover code.

## Risks
Only selected Hadoop keys are honored. HA parse failures clear the nameservice list and log errors rather than returning a structured failure. `RemoveSpaces` removes only literal spaces, not other whitespace. Multiple nameservices are parsed, but downstream behavior must still choose the correct service. Authentication values other than exact Kerberos fall back to simple.

## Test Signals
Tests should cover default-only options, every supported key, HA service parsing with multiple namenodes and missing keys, scheme prefixing, whitespace in namenode lists, Kerberos/simple auth values, and malformed RPC address URIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.h

## Purpose
Declares `HdfsConfiguration`, the HDFS-specific subclass of `Configuration` that converts Hadoop XML properties into libhdfspp runtime `Options`.

## Important APIs, Types, And Functions
The public API is `Options GetOptions()`. The header declares constants for supported keys such as `fs.defaultFS`, socket/connect retry timeouts, authentication, block size, and failover limits. Private constructors are friend-only for `ConfigurationLoader`, and `LookupNameService` handles HA service expansion.

## Control Flow
Implementation in `hdfs_configuration.cc` reads the inherited property map and constructs `Options`.

## State And Persistence
State is inherited `raw_values_`. The class is intended as an immutable parsed configuration snapshot.

## Dependencies And Integration Points
Used by the C builder, `ConfigParser`, and filesystem construction. It is the bridge from Hadoop config naming to libhdfspp option names.

## Risks
Adding supported Hadoop keys requires changes in both this header and implementation. Constructor privacy means new loaders/tests must use `ConfigurationLoader`.

## Test Signals
Compile tests should confirm loader instantiation, and behavior tests should verify every declared key affects `Options` as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/hdfs_configuration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.cc

## Purpose
Implements `IoServiceImpl`, libhdfspp's wrapper around `boost::asio::io_service` with managed worker threads and exception containment for async callbacks.

## Important APIs, Types, And Functions
`IoService::New()` and `MakeShared()` construct `IoServiceImpl`. `InitDefaultWorkers`, `InitWorkers`, `AddWorkerThread`, `PostTask`, `Run`, `Stop`, `GetRaw`, and `GetWorkerThreadCount` implement the public `IoService` contract. `WorkerDeleter` joins worker threads and detects deletion from a worker callback.

## Control Flow
Default initialization uses hardware concurrency unless concurrent workers are disabled by compile flags. Each worker calls `ThreadStartHook`, then `Run`, then `ThreadExitHook`. `Run()` holds a work object and repeatedly calls `io_service_.run()`, catching exceptions thrown by user callbacks so the worker thread does not terminate the process.

## State And Persistence
State includes the underlying `io_service_`, a vector of joined-on-destruction worker threads, and a mutex protecting thread vector/logging hooks. All state is process-local.

## Dependencies And Integration Points
Used by filesystem, namenode resolution, DataNode sockets, and C allocated filesystem connection. Depends on Boost.Asio, logging, and common lock typedefs.

## Risks
`Run()` creates a local work guard, so threads can stay alive until `Stop()` is called. `WorkerDeleter` logs a fatal condition if a worker tries to destroy the pool from within itself but still calls `join`, which would deadlock or fail. Thread creation failures are not caught around `new std::thread`.

## Test Signals
Tests should cover default and explicit worker counts, posting tasks, exception-throwing callbacks, stop behavior, destruction from non-worker threads, and worker-count reporting under concurrent initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.h

## Purpose
Declares `IoServiceImpl`, the concrete libhdfspp `IoService` implementation backed by Boost.Asio and owned worker threads.

## Important APIs, Types, And Functions
The class overrides worker initialization, task posting, run/stop, raw Asio access, worker addition, and worker count. It uses `MEMCHECKED_CLASS`, `state_lock_`, `io_service_`, and `WorkerPtr` with `WorkerDeleter`.

## Control Flow
Runtime behavior is implemented in `ioservice_impl.cc`; this header establishes the inheritance and ownership model.

## State And Persistence
State is in-memory Asio runtime and worker thread ownership. No durable state exists.

## Dependencies And Integration Points
Included by components that need the concrete `GetRaw()` Asio service for sockets/resolvers. The public base interface lives in `hdfspp/ioservice.h`.

## Risks
Because `GetRaw()` exposes the underlying service, callers can post operations that bypass wrapper invariants. Worker-thread lifetime is tied to object destruction and must be coordinated with filesystem shutdown.

## Test Signals
Compile and integration tests should instantiate through both `New` and `MakeShared`, use raw Asio sockets/resolvers, and validate worker shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.cc

## Purpose
Implements `LibhdfsEvents`, a callback registry and safe dispatcher for filesystem and file-level event hooks.

## Important APIs, Types, And Functions
The class supports `set_fs_callback`, `set_file_callback`, `clear_fs_callback`, `clear_file_callback`, and two overloads of `call`: one for filesystem events and one for file events.

## Control Flow
`call` checks whether a callback is present. If absent, it returns `event_response::make_ok()`. If present, it invokes the callback and catches both `std::exception` and unknown throws, converting them to event responses instead of allowing user code to unwind through libhdfspp internals.

## State And Persistence
State is two optional function objects stored per `LibhdfsEvents` instance. It is in-memory and copyable through the compiler-generated copy constructor used by `FileHandleImpl`.

## Dependencies And Integration Points
Used by `hdfs.cc` event pre-attach glue, `FileSystem`, `FileHandleImpl`, `DataNodeConnectionImpl`, and block readers to emit connect/read/write events and optional simulated errors.

## Risks
Callback storage is not internally synchronized; callers should replace callbacks before concurrent event dispatch. Exceptions are converted to responses, but normal callbacks can still block worker threads.

## Test Signals
Tests should cover no-op dispatch, filesystem and file callback invocation, callback clearing, exception conversion, copied event registries, and simulated-error paths under non-disabled test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.h

## Purpose
Declares the `LibhdfsEvents` callback registry used to decouple low-level libhdfspp code from C-facing event hook storage.

## Important APIs, Types, And Functions
The class stores optional `fs_event_callback` and `file_event_callback` values and exposes setter, clearer, and dispatcher overloads.

## Control Flow
Implementation dispatches callbacks and converts exceptions in `libhdfs_events_impl.cc`.

## State And Persistence
State is per-instance optional callback data. No persistence exists.

## Dependencies And Integration Points
Included by C bindings, filesystem/filehandle, DataNode connection, and reader code that emits libhdfspp events.

## Risks
There is no locking in the class declaration, so callback mutation during event emission is unsafe unless guarded externally.

## Test Signals
Compile tests should verify both callback signatures; behavior tests should exercise dispatch through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/libhdfs_events_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/locks.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/locks.cc

## Purpose
Implements lock abstractions used by libhdfspp, especially the globally configurable GSSAPI mutex required to serialize non-thread-safe security library calls.

## Important APIs, Types, And Functions
`LockGuard` locks a `Mutex*` in its constructor and unlocks in its destructor. `DefaultMutex` wraps `std::mutex`. Static `LockManager` state includes default test and GSSAPI mutexes, `_state_lock`, and `_finalized`. `InitLocks`, `getGssapiMutex`, `TEST_get_default_mutex`, and `TEST_reset_manager` manage global lock state.

## Control Flow
Clients call `LockManager::InitLocks` once to replace the GSSAPI mutex before use. After finalization, subsequent init attempts fail. `getGssapiMutex` returns the active mutex under state lock; `LockGuard` then applies RAII locking to it.

## State And Persistence
State is process-global pointers to mutex implementations plus finalization flag. It is not durable and test reset can reopen initialization.

## Dependencies And Integration Points
Depends on `hdfspp/locks.h` and C++ mutexes. Security/authentication code should use `getGssapiMutex` around GSSAPI calls.

## Risks
`InitLocks` stores a raw pointer and leaves lifetime management to the caller. `TEST_reset_manager` is not protected by `_state_lock`, so it is only safe in isolated tests. Swapping lock proxies after use is explicitly risky.

## Test Signals
Tests should cover null mutex rejection in `LockGuard`, one-shot initialization, failed second initialization, custom mutex use, default reset in tests, and concurrent `getGssapiMutex` access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/locks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.cc

## Purpose
Implements libhdfspp's lightweight logging backend, including global log filtering, default stderr formatting, and streamed message construction.

## Important APIs, Types, And Functions
`LogManager` owns static `logger_impl_`, `impl_lock_`, `component_mask_`, and `level_threshold_`. It implements component enable/disable, level setting, message writing, and logger replacement. `StderrLogger::Write` formats metadata and message text. `LogMessage` destructor emits the message and overloads `operator<<` for strings, booleans, integers, pointers, endpoints, and thread IDs.

## Control Flow
Logging macros check `LogManager::ShouldLog` before constructing a `LogMessage`. The temporary accumulates text through stream-like operators, then destructor calls `LogManager::Write`. The default logger prints to stderr with level, component, timestamp, thread id, file path, line, and text.

## State And Persistence
Logging configuration is process-global and protected by a mutex. Messages are transient; the default sink writes to stderr only. C bindings can replace the logger with a callback-forwarding implementation.

## Dependencies And Integration Points
Used throughout libhdfspp common, RPC, filesystem, reader, connection, and C binding code. Integrates with `hdfsSetLogFunction`, component masks, and public log constants.

## Risks
`ShouldLog` locks on every enabled/disabled check, which can affect hot paths. `StderrLogger::Write` uses `std::localtime`, which is not thread-safe, although calls are serialized by the log manager. `operator<<(const std::string*)` streams the pointer value instead of dereferencing the string, likely surprising. Logger callbacks execute under the global logging lock and can deadlock if they re-enter logging.

## Test Signals
Tests should verify level/component filtering, stderr formatting, custom logger replacement, C callback forwarding, multithreaded logging, null string handling, and no recursive logging deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.h

## Purpose
Declares libhdfspp logging levels, components, macros, logger interfaces, global manager, default stderr logger, and `LogMessage` streaming API.

## Important APIs, Types, And Functions
`LogLevel` covers trace through error. `LogSourceComponent` is a bitmask for unknown, RPC, block reader, file handle, file system, and async runtime. Macros `LOG_TRACE` through `LOG_ERROR` guard construction. `LoggerInterface`, `StderrLogger`, `LogManager`, and `LogMessage` define the logging extension points and message metadata.

## Control Flow
Macros call `LogManager::ShouldLog`; implementation writes through the active logger in `logging.cc`.

## State And Persistence
Static manager state is declared here and defined in the implementation. Messages are stack temporaries emitted at destruction.

## Dependencies And Integration Points
Every native subsystem includes this header for diagnostics. The C binding maps public log constants to these internal enums.

## Risks
The macro form requires call sites to use the unusual `LOG_INFO(component, << "text")` pattern. Direct `LogMessage` construction bypasses filtering. Component values must remain aligned with public C API validation.

## Test Signals
Compile tests should cover every macro and overload; integration tests should validate public component and level constants against this enum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.cc

## Purpose
Implements namenode endpoint resolution and resolved-namenode formatting for HA and default filesystem connection logic.

## Important APIs, Types, And Functions
`ResolvedNamenodeInfo::operator=` copies base `NamenodeInfo` fields. `str()` formats nameservice, node name, URI, host, port, scheme, and resolved endpoints. `ResolveInPlace` refreshes one resolved node. `BulkResolve` asynchronously resolves all input nodes. Internal `ScopedResolver` owns an Asio resolver and promise/future status bridge.

## Control Flow
`BulkResolve` creates one `ScopedResolver` per namenode, starts async resolution for all of them on the supplied `IoService`, then joins each future and copies endpoints into the corresponding result if resolution succeeded. `ResolveInPlace` delegates to `BulkResolve` and copies endpoints back when exactly one node resolves with non-empty endpoints.

## State And Persistence
Resolved endpoints are stored in returned `ResolvedNamenodeInfo` values. `ScopedResolver` state is temporary and cancels the resolver on destruction.

## Dependencies And Integration Points
Depends on `NamenodeInfo`, `IoService`, Boost.Asio DNS resolver, logging, and `ToStatus`. It feeds filesystem failover and connection selection.

## Risks
Resolution requires `IoService` worker activity; otherwise `Join()` can block forever. `BulkResolve` logs failures but still returns entries with empty endpoints, despite the header comment saying only successful lookups will be placed in the result set. The callback captures `this`, so resolver lifetime must outlive completion, which is enforced only by joining before destruction.

## Test Signals
Tests should resolve localhost and invalid hosts, verify parallel resolution with multiple nodes, check empty endpoint behavior, exercise `ResolveInPlace`, and run with stopped or unstarted `IoService` to catch hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.h

## Purpose
Declares resolved namenode metadata and resolver helpers used by connection and failover code.

## Important APIs, Types, And Functions
`ResolvedNamenodeInfo` extends `NamenodeInfo` with a vector of Boost TCP endpoints plus assignment and `str()`. Free functions `BulkResolve` and `ResolveInPlace` perform asynchronous DNS resolution using an `IoService`.

## Control Flow
Implementation lives in `namenode_info.cc`; callers pass configured namenodes and receive endpoint-populated copies.

## State And Persistence
State is returned in value objects. No persistent cache is declared here.

## Dependencies And Integration Points
Used by filesystem connection logic after `HdfsConfiguration` parses `NamenodeInfo` records from Hadoop XML.

## Risks
The header comment for `BulkResolve` does not perfectly match implementation behavior for failed resolutions, so callers should check `endpoints`.

## Test Signals
Tests should validate endpoint vectors and string formatting for resolved and unresolved nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/namenode_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/new_delete.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/new_delete.h

## Purpose
Defines `MEMCHECKED_CLASS`, a debug-only allocation macro that overwrites object or array memory on delete to help expose use-after-free bugs.

## Important APIs, Types, And Functions
`mem_struct` stores array allocation size. In non-`NDEBUG` builds, `MEMCHECKED_CLASS(clazz)` injects custom scalar and array new/delete operators; release builds expand to nothing.

## Control Flow
Scalar delete zeros `sizeof(clazz)` bytes before freeing. Array new stores size in a prepended header, and array delete recovers the header, zeros the payload, and frees the original allocation.

## State And Persistence
No runtime state is kept beyond per-allocation headers for arrays in debug builds.

## Dependencies And Integration Points
Used by classes such as `IoServiceImpl`, `DataNodeConnection`, and `FileHandleImpl` for debug memory hygiene.

## Risks
Custom allocation operators must remain correctly paired. Scalar delete assumes the object allocation size equals `sizeof(clazz)`, which is true for normal scalar objects but can be risky with inheritance if deleting through a base without a virtual destructor. The macro uses C allocation routines and bypasses standard new-handler behavior.

## Test Signals
Debug ASAN/unit tests should allocate and delete scalar and array instances of memchecked classes and check for allocator mismatches or crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/new_delete.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/optional_wrapper.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/optional_wrapper.h

## Purpose
Wraps the third-party `optional.hpp` compatibility header and suppresses selected Clang diagnostics around it.

## Important APIs, Types, And Functions
The file conditionally pushes Clang diagnostics, defines `TR2_OPTIONAL_DISABLE_EMULATION_OF_TYPE_TRAITS` for older Clang handling, includes `<optional.hpp>`, then restores diagnostics.

## Control Flow
There is no runtime flow; it is a compile-time compatibility shim.

## State And Persistence
No state exists.

## Dependencies And Integration Points
Included by common headers that use `std::experimental::optional`, including configuration, auth, and event code.

## Risks
The wrapper assumes the project-provided `optional.hpp` is on the include path. Compiler-specific warning suppression may become stale as toolchains change.

## Test Signals
Build matrix coverage across Clang and GCC, especially older Clang versions, is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/optional_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/options.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/options.cc

## Purpose
Defines out-of-line constants and constructors for libhdfspp `Options` and simple `NamenodeInfo` accessors.

## Important APIs, Types, And Functions
The file provides storage for static defaults such as RPC timeout, retry counts, host exclusion duration, failover limits, and block size. `Options::Options()` initializes runtime defaults. `NamenodeInfo::get_host()` and `get_port()` expose host/port from the contained `URI`.

## Control Flow
Constructing `Options` copies default constants into scalar fields, initializes default URI/services state, sets default authentication, block size, and I/O thread count. `get_port()` returns the URI port as a string or `-1` when absent.

## State And Persistence
Each `Options` is an in-memory value object. Static constants have process lifetime.

## Dependencies And Integration Points
Used by filesystem construction, configuration parsing, bad DataNode tracking, and retry policy selection.

## Risks
Out-of-line constant definitions must match declarations in `hdfspp/options.h`. Returning `-1` as a port string is useful as a sentinel but can be passed accidentally into resolver/connect paths if callers skip validation.

## Test Signals
Tests should assert default option values, configuration override behavior, and `NamenodeInfo` host/port output for URIs with and without ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/options.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.cc

## Purpose
Implements retry policy decisions for RPC communication, including no-retry, fixed-delay retry, and fixed-delay retry with HA failover.

## Important APIs, Types, And Functions
`FixedDelayRetryPolicy::ShouldRetry`, `NoRetryPolicy::ShouldRetry`, and `FixedDelayWithFailover::ShouldRetry` return `RetryAction` values based on status, retry count, failover count, and configured limits.

## Control Flow
No-retry always fails. Fixed-delay retries until total retries plus failovers reaches `max_retries_`. Failover policy triggers failover on timeout or StandbyException while under the failover limit, retries while both retry/failover budgets remain, fails over after local retries are exhausted, and grants one last retry when failover count reaches the max.

## State And Persistence
Policies store delay and retry/failover limits as immutable object state. Counters are supplied by callers; no policy persists progress internally.

## Dependencies And Integration Points
Depends on `Status`, Boost.Asio timeout error codes, and logging. Used by RPC connection and namenode failover loops.

## Risks
`max_failover_conn_retries_` is accepted but not used, so connection-timeout-specific behavior described in comments is incomplete. Idempotency is ignored by all policies. Boundary conditions around `retries <= max_retries_` and final retry/failover can be subtle.

## Test Signals
Tests should table-drive retry/failover decisions for OK/error statuses, timeout, StandbyException, permission/auth failures, exact budget boundaries, delay values, and currently ignored idempotency/max-failover-connection settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.h

## Purpose
Declares retry policy types and action values used by libhdfspp RPC and failover logic.

## Important APIs, Types, And Functions
`RetryAction` stores `FAIL`, `RETRY`, or `FAILOVER_AND_RETRY`, a delay, and an optional reason, with static factories and `decision_str()`. `RetryPolicy` is the abstract base. Concrete policies are `FixedDelayWithFailover`, `FixedDelayRetryPolicy`, and `NoRetryPolicy`.

## Control Flow
Callers ask `ShouldRetry` after a failed operation and then either fail, sleep/retry, or switch namenodes and retry.

## State And Persistence
Policy instances store configured delays and limits only. Retry counters remain caller state.

## Dependencies And Integration Points
Included by RPC connection code and configured from `Options` populated by `HdfsConfiguration`.

## Risks
The base default constructor leaves limit fields uninitialized if a subclass used it incorrectly. `decision_str()` includes a defensive default that should be unreachable.

## Test Signals
Compile tests should use polymorphic policy pointers; behavior tests live with `retry_policy.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/retry_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_authenticator.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_authenticator.h

## Purpose
Declares the DIGEST-MD5 SASL authenticator used for HDFS DataTransferProtocol token authentication.

## Important APIs, Types, And Functions
`DigestMD5Authenticator` exposes a constructor taking username/password and optional test nonce behavior, plus `EvaluateResponse`. Private helpers parse the first challenge, generate a client nonce, generate the first response, compute the response value, and tokenize challenge payloads.

## Control Flow
The server challenge is parsed, nonce/qop/realm fields are stored, a client nonce is generated, and a SASL response string is produced.

## State And Persistence
Per-authenticator state includes username, password, nonce, cnonce, realm, qop, and nonce count. It is in-memory and not wiped after use.

## Dependencies And Integration Points
Implemented in `sasl_digest_md5.cc` and used by DataNode/block reader authentication flows when token auth requires SASL.

## Risks
The header documents incomplete RFC 2831 support: no ISO-8859-1 conversion, weak challenge validation, fixed authzid/digest-uri/maxbuf behavior, and only `auth` QOP support. Password/token material remains in strings.

## Test Signals
Unit tests should cover known RFC-style challenge/response vectors, invalid challenges, unsupported QOP, deterministic mock nonce, and password/realm quoting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_authenticator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_digest_md5.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_digest_md5.cc

## Purpose
Implements the specialized DIGEST-MD5 SASL response generator for HDFS DataTransferProtocol authentication.

## Important APIs, Types, And Functions
`EvaluateResponse` calls `ParseFirstChallenge` then `GenerateFirstResponse`. `NextToken` tokenizes challenge key/value pairs. `GenerateCNonce` uses OpenSSL `RAND_bytes` and base64. `GenerateFirstResponse` builds the SASL response fields. `GenerateResponseValue` computes RFC 2831 MD5-sess response. Helpers quote strings, compute MD5 digests, and hex-encode binary data.

## Control Flow
The challenge parser walks tokens through lvalue, equals, rvalue, comma/end states and requires `algorithm=md5-sess`, `charset=utf-8`, and `nonce`. Response generation rejects non-`auth` QOP, emits fixed `digest-uri=hdfs/0`, max buffer 65536, optional realm, incremented nonce count, and a computed response hash.

## State And Persistence
The authenticator stores parsed server challenge fields, generated cnonce, and nonce count. Credentials and derived values remain in memory for the object's lifetime.

## Dependencies And Integration Points
Depends on OpenSSL RAND/MD5/ERR, `Base64Encode`, and `Status`. It integrates with block reader/DataNode SASL negotiation.

## Risks
OpenSSL MD5 APIs are deprecated in newer OpenSSL versions. Challenge validation is minimal, token parsing accepts a narrow character set, and release builds do not add extra safety. The fixed digest URI and authzid may not match every deployment. Response size is capped at 4096 after construction.

## Test Signals
Tests should cover valid HDFS token challenge responses, nonce-count increments, deterministic cnonce mode, RAND failure, unsupported qop, invalid/missing nonce, quoting embedded quotes, and OpenSSL 3 build warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/sasl_digest_md5.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/statinfo.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/statinfo.cc

## Purpose
Implements human-readable formatting for HDFS `StatInfo`, analogous to an `ls -l` line.

## Important APIs, Types, And Functions
The constructor zero-initializes file metadata fields. `StatInfo::str()` formats file type, permission bits, replication, owner, group, length, modification time, and full path.

## Control Flow
`str()` builds a 10-character permissions string from POSIX mode bits, converts modification time from milliseconds to seconds, formats local time, and writes aligned columns to a stream.

## State And Persistence
State is per-object file metadata populated from namenode responses. No persistence exists.

## Dependencies And Integration Points
Used by listing/stat display code and C API conversion in `hdfs.cc`. Depends on x-platform stat permission constants.

## Risks
`localtime` is not thread-safe. Unknown file types are rendered as regular-file style unless handled elsewhere. Formatting width choices can truncate or misalign unusual values.

## Test Signals
Tests should cover files, directories, zero replication, permissions, time formatting, long owner/group/path values, and concurrent formatting if used from multiple threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/statinfo.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/status.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/status.cc

## Purpose
Implements libhdfspp `Status`, including generic error codes, server exception mapping, retry classification, string formatting, and factory helpers.

## Important APIs, Types, And Functions
Known Hadoop exception class names map to internal codes such as access control, not-a-directory, snapshot protocol, standby, authentication failed, path not found, file exists, and non-empty directory. Factories include `OK`, `InvalidArgument`, `PathNotFound`, `ResourceUnavailable`, `PathIsNotDirectory`, `Unimplemented`, `Exception`, `Error`, `AuthenticationFailed`, `AuthorizationFailed`, `Canceled`, `InvalidOffset`, and `MutexError`. `ToString` and `notWorthRetry` expose status behavior.

## Control Flow
Constructors store code/message/exception class and remap recognized server exception classes. `Exception` maps Java exception names to more specific status categories where possible. `notWorthRetry` checks a static set of permission/auth-related codes.

## State And Persistence
Each `Status` owns its code, message, and exception class strings. Static maps/sets live for process lifetime. No durable state exists.

## Dependencies And Integration Points
Used throughout libhdfspp and converted to `errno` by the C binding. Retry policy, filesystem operations, RPC, and block readers all depend on consistent codes.

## Risks
`MutexError` constructs a formatted string but returns `msg`, losing the prefix. `kInvalidOffset` is later mapped oddly in `hdfs.cc` to its numeric status code as errno. Exception mappings are incomplete and require maintenance as Hadoop server exceptions evolve.

## Test Signals
Tests should cover every factory, Java exception remapping, `ToString`, retry classification, C errno mapping, unknown exceptions, null messages, and `MutexError` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/status.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/uri.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/uri.cc

## Purpose
Implements URI parsing, encoding/decoding, construction, query manipulation, and debug formatting for libhdfspp.

## Important APIs, Types, And Functions
Core APIs include `URI::parse_from_string`, `encode`, `decode`, `str`, `has_authority`, `build_authority`, scheme/host/port/path/query/fragment getters and setters, `add_path`, `add_query`, `remove_query`, `from_encoded`, `to_encoded`, and `GetDebugString`. Internal helpers copy uriparser ranges, parse ports, path segments, user info, and query lists.

## Control Flow
Parsing delegates to `uriparser2`, copies parsed components into encoded internal fields, parses user info and queries, and throws `uri_parse_error` on failure. Formatting reconstructs a URI from fields, optionally decoding output. Path and query setters encode inputs unless marked already encoded.

## State And Persistence
Each `URI` stores scheme, host, user, password, path vector, query vector, fragment, and `_port` sentinel `-1`. No global or durable state exists.

## Dependencies And Integration Points
Used by configuration parsing, namenode info, options, and filesystem connection code. Depends on `uriparser2`.

## Risks
`parse_user_info` appears to compute username length as `colon_loc - begin - 1`, dropping one character before the colon. `parse_from_string` calls `uriFreeUriMembersA` both inside and after the success block, a potential double-free risk depending on uriparser behavior. `set_path` appends parsed elements without clearing existing path. Port parsing rejects the maximum uint16 value because it uses `< max`.

## Test Signals
Tests should parse and round-trip schemes, authorities, users/passwords, ports, paths, queries, fragments, encoded characters, invalid URIs, repeated `set_path`, query removal, and edge ports 0/65535.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/uri.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.cc

## Purpose
Implements common utility functions for status conversion, protobuf framing, random client naming, base64 encoding, safe socket shutdown, high-bit tests, and C protobuf shutdown.

## Important APIs, Types, And Functions
Functions include `ToStatus`, `ReadDelimitedPBMessage`, `SerializeDelimitedProtobufMessage`, `DelimitedPBMessageSize`, `GetRandomClientName`, `Base64Encode`, `SafeDisconnect`, `IsHighBitSet`, and `ShutdownProtobufLibrary_C`.

## Control Flow
Boost errors become OK or status with error value/message. Protobuf helpers read/write Java-compatible varint-delimited messages. Random client names combine process id, thread id, and OpenSSL random bytes. `SafeDisconnect` tries socket shutdown and close separately and returns a first error string instead of throwing.

## State And Persistence
No persistent state is kept. Random output depends on OpenSSL RNG. Protobuf library shutdown affects process-global protobuf state.

## Dependencies And Integration Points
Used by continuations, RPC, block reader, DataNode connection, C utility API, and client identity creation.

## Risks
`ReadDelimitedPBMessage` ignores the return value of `ReadVarint32` and can parse invalid streams poorly. Base64 is custom code and should be tested against standard vectors. `GetRandomClientName` returns null on RNG failure and callers must handle that path. `ShutdownProtobufLibrary_C` is process-global and unsafe if called while protobuf is still in use.

## Test Signals
Tests should cover protobuf round trips and malformed input, Boost error conversion, random-name uniqueness/failure handling, base64 vectors, socket close error strings, high-bit checks, and C protobuf shutdown placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.h

## Purpose
Declares common utility APIs and small templates shared across libhdfspp networking, protobuf, callback, and synchronization code.

## Important APIs, Types, And Functions
The header defines `mutex_guard`, status/protobuf/base64/random/safe-disconnect/high-bit declarations, `lock_held`, `get_asio_socket_ptr` with a specialization for real TCP sockets, and `SwappableCallbackHolder<CallbackType>`.

## Control Flow
Most functions are implemented in `util.cc`. `SwappableCallbackHolder` enforces a one-time set, optional one-time swap before access, and one-time access pattern under a mutex, logging invariant violations.

## State And Persistence
Utility functions are stateless. `SwappableCallbackHolder` stores one callback and three boolean lifecycle flags.

## Dependencies And Integration Points
Used by async runtime, RPC, block reader, DataNode connection, and tests with mock sockets/callbacks.

## Risks
`lock_held` is only a heuristic and can perturb lock state if used incorrectly. `SwappableCallbackHolder::AtomicSwapCallback` can continue after invariant violations and still return/set values in some branches; callers must check the `swapped` flag. Callback retrieval returns copies and does not guard callback execution.

## Test Signals
Tests should cover socket pointer specialization, callback holder valid/invalid sequences, lock-held behavior, and declarations against implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util_c.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util_c.h

## Purpose
Declares the C ABI wrapper for shutting down the protobuf library from C or mixed-language consumers.

## Important APIs, Types, And Functions
`ShutdownProtobufLibrary_C()` is declared inside `extern "C"` when compiled as C++.

## Control Flow
The implementation in `util.cc` calls `google::protobuf::ShutdownProtobufLibrary()`.

## State And Persistence
Calling the function mutates protobuf process-global state; the header itself stores no state.

## Dependencies And Integration Points
Used by C-facing libraries or tests that need an unmangled shutdown hook.

## Risks
The function should only be called when no protobuf messages/descriptors are still in use. Repeated or premature calls can break later protobuf operations in the same process.

## Test Signals
C and C++ link tests should verify symbol visibility; integration tests should call it only at process teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/util_c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/CMakeLists.txt

## Purpose
Defines the build target for the libhdfspp DataNode connection layer.

## Important APIs, Types, And Functions
The file creates `connection_obj` from `datanodeconnection.cc`, adds a dependency on generated protobuf target `proto`, and creates the `connection` library from the object target.

## Control Flow
CMake ensures protobuf classes are generated before compiling DataNode connection code that includes `ClientNamenodeProtocol.pb.h`.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
Connects the connection module to generated protobufs and higher-level fs/reader libraries.

## Risks
If new connection sources are added but omitted here, link errors or missing behavior will result. The target does not declare include dirs locally, so it relies on parent/global include configuration.

## Test Signals
Signals are successful CMake generation, protobuf dependency ordering, and link of consumers using `DataNodeConnectionImpl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.cc

## Purpose
Implements `DataNodeConnectionImpl`, the socket-backed `AsyncStream` used by block readers to connect to and communicate with one HDFS DataNode.

## Important APIs, Types, And Functions
The constructor builds a TCP socket from an `IoService`, extracts DataNode transfer endpoint and UUID from `DatanodeInfoProto`, and optionally copies a block token. `Connect` starts `boost::asio::async_connect`. `Cancel` safely disconnects the socket. `async_read_some` and `async_write_some` emit event callbacks and forward to the socket.

## Control Flow
Callers construct the connection, call `Connect`, and receive a status plus shared connection in the handler. Read/write operations lock briefly around posting socket async operations. Cancellation closes the socket so pending operations should complete with errors.

## State And Persistence
State includes the socket, one endpoint, copied token, UUID, event handler pointer, and a mutex. It is per-connection and in-memory.

## Dependencies And Integration Points
Depends on Boost.Asio, generated HDFS protobufs, `IoService`, `AsyncStream`, `LibhdfsEvents`, logging, and `SafeDisconnect`. Created by `FileHandleImpl` for block reads and consumed by `BlockReaderImpl`.

## Risks
The endpoint is built from `ipaddr()` with `address::from_string`, so hostnames or invalid IP strings throw during construction. Event handler pointer is raw and must outlive the connection. The derived class declares its own `uuid_`, hiding the base member of the same name; callers through a base pointer may observe the base value instead of the derived value. Async read/write serialization is minimal and does not make simultaneous operations fully safe.

## Test Signals
Tests should cover successful and failed connect, invalid IP input, token copy, cancellation during connect/read/write, event emission counts, base-pointer UUID visibility, and ASAN lifetime checks for event handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.h

## Purpose
Declares the abstract DataNode connection stream and the concrete socket-backed implementation used by HDFS block readers.

## Important APIs, Types, And Functions
`DataNodeConnection` derives from `AsyncStream`, stores public UUID/token members, and declares `Connect` and `Cancel`. `SocketDeleter` safely disconnects sockets before deletion. `DataNodeConnectionImpl` owns a unique TCP socket, one endpoint, event handler pointer, state mutex, and overrides connect/read/write/cancel.

## Control Flow
Implementation creates sockets and forwards async I/O in `datanodeconnection.cc`.

## State And Persistence
Per-object socket, endpoint, token, UUID, and callback pointer state is in-memory. No durable state exists.

## Dependencies And Integration Points
Included by `FileHandleImpl`, block reader code, and tests/mocks. It depends on protobuf, `IoService`, `AsyncStream`, events, logging, utilities, and debug allocation helpers.

## Risks
The public base data members and duplicate derived `uuid_` make object state easy to misuse. Raw event handler ownership is not expressed in the type. Since it derives from `enable_shared_from_this`, `Connect` must only be called on shared-owned instances.

## Test Signals
Compile tests should mock `DataNodeConnection`; runtime tests should instantiate through `make_shared`, call `Connect`, and validate destructor/socket cleanup under cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/connection/datanodeconnection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/CMakeLists.txt

## Purpose
Defines the build target for the libhdfspp filesystem layer.

## Important APIs, Types, And Functions
The file builds `fs_obj` from `filesystem.cc`, `filesystem_sync.cc`, `filehandle.cc`, `bad_datanode_tracker.cc`, and `namenode_operations.cc`, includes x-platform objects, adds private include path `../lib`, depends on `proto`, and creates the `fs` library.

## Control Flow
CMake ensures generated protobufs exist before compiling filesystem sources and packages object files for higher-level library links.

## State And Persistence
No runtime state exists.

## Dependencies And Integration Points
This target integrates filesystem operations, synchronous wrappers, file handles, bad DataNode tracking, namenode operation glue, x-platform helpers, and protobuf-generated protocol classes.

## Risks
New fs sources must be added here. The relative include path is sensitive to source-tree layout. Object-library reuse can hide missing transitive link dependencies until final link.

## Test Signals
Signals are successful build ordering, complete fs symbol linkage, and filesystem/open/read tests against a mini cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.cc

## Purpose
Implements DataNode exclusion rules used by file reads to avoid recently failed DataNodes and user-specified excluded nodes.

## Important APIs, Types, And Functions
`BadDataNodeTracker` implements `AddBadNode`, `IsBadNode`, `TimeoutExpired`, and `TEST_set_clock_shift`. `ExclusionSet` implements `IsBadNode` over a fixed set. `NodeExclusionRule` has an out-of-line virtual destructor.

## Control Flow
When reads fail with statuses worth excluding, `FileHandleImpl` calls `AddBadNode`. Future `AsyncPreadSome` calls ask `IsBadNode`; if the timestamp has expired, the node is erased and allowed again, otherwise it is skipped. `ExclusionSet` directly checks set membership.

## State And Persistence
`BadDataNodeTracker` stores a mutex-protected map from DataNode UUID to steady-clock insertion time, timeout duration from `Options`, and a test clock shift. State is per tracker and not persisted.

## Dependencies And Integration Points
Used by `FileHandleImpl` DataNode selection. Timeout defaults come from `Options::host_exclusion_duration`; rule interface comes from public `hdfspp.h`.

## Risks
The map is cleaned lazily only when a specific node is queried. `TEST_set_clock_shift` is not synchronized. Exclusion is by UUID, so callers must pass consistent identifiers.

## Test Signals
Tests should mark nodes bad, verify immediate exclusion, shift/advance time to expire entries, test concurrent add/check, and validate `ExclusionSet` with known UUID sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.h

## Purpose
Declares the DataNode exclusion interfaces used during block reads.

## Important APIs, Types, And Functions
`ExclusionSet` wraps a fixed `std::set<std::string>` of excluded UUIDs. `BadDataNodeTracker` tracks failed DataNodes with timeout-based eviction and exposes `AddBadNode`, `IsBadNode`, and test clock shifting.

## Control Flow
File read logic supplies either a caller-provided `NodeExclusionRule` or the shared bad-node tracker to DataNode selection.

## State And Persistence
`BadDataNodeTracker` owns a timestamp map and mutex; `ExclusionSet` owns an immutable set. Neither persists to disk.

## Dependencies And Integration Points
Depends on public options and `NodeExclusionRule` declarations from `hdfspp/hdfspp.h`. Integrated with `FileHandleImpl::AsyncPreadSome`.

## Risks
The timeout is fixed at construction, so option changes do not affect existing trackers. Test-only clock shifting is part of the public class surface.

## Test Signals
Tests should cover both dynamic tracker and fixed set behavior through direct calls and through file read DataNode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/bad_datanode_tracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.cc

## Purpose
Implements `FileHandleImpl`, the object coordinating reads from one HDFS file, including synchronous reads, positioned reads, DataNode selection, block-reader creation, cancellation, read statistics, and file event callbacks.

## Important APIs, Types, And Functions
Key methods are async and sync `PositionRead`, `Read`, `Seek`, `AsyncPreadSome`, `CancelOperations`, `SetFileEventCallback`, `get_event_handlers`, `get_bytes_read`, `clear_bytes_read`, `CreateBlockReader`, and `CreateDataNodeConnection`. `FileHandle::ShouldExclude` decides whether a failed read should mark a DataNode bad.

## Control Flow
Positioned reads check cancellation, wrap completion to update bad-node tracking and byte counters, and call `AsyncPreadSome`. The synchronous overload bridges async completion through `std::promise`/`future`. Sequential `Read` uses the current offset and advances it on success. `Seek` computes a new offset from beginning/current/end and validates bounds. `AsyncPreadSome` validates EOF/offset/client name, finds the containing located block, picks the first non-excluded DataNode, computes block-relative offset and bounded read size, creates a DataNode connection and block reader, connects, emits events, and starts `AsyncReadBlock`.

## State And Persistence
The handle stores cluster name, path, shared `IoService`, random client name, immutable `FileInfo` with located blocks, shared bad-node tracker, current sequential offset, cancel tracker, `ReaderGroup`, event handlers, and atomic bytes-read counter. State is in-memory per open file; HDFS file data remains remote.

## Dependencies And Integration Points
Depends on block reader, DataNode connection, continuation cancellation, events, logging, generated namenode protobufs, x-platform types, and bad-node tracking. It is wrapped by the C API and created by `FileSystem::Open`.

## Risks
The class comment says most operations are not thread-safe except `PositionRead`, but `offset_` and event handler replacement are unsynchronized. The sync read path blocks until async completion, requiring active `IoService` workers. `AsyncPreadSome` captures iterators/references into `file_info_`; this is safe only because `file_info_` is shared immutable and the lambda owns the shared handle context indirectly through captured objects. It chooses the first available DataNode without locality/rack ranking. Cancellation relies on both a flag and reader socket cancellation.

## Test Signals
Tests should read zero bytes at EOF, reject offsets past EOF, read across block boundaries via repeated calls, seek from all origins, run concurrent positioned reads, simulate DataNode failure and bad-node exclusion, cancel slow reads, verify event callbacks and simulated errors, validate bytes-read statistics, and ensure sync reads complete with active worker threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.h

## Purpose
Declares `FileHandleImpl`, the concrete libhdfspp file handle for HDFS reads.

## Important APIs, Types, And Functions
The class implements `FileHandle` methods for asynchronous positioned read, synchronous positioned read, sequential read, seek, partial async pread with exclusion rules, cancellation, file event callback replacement, event handler access, read statistics, and protected factories for block readers and DataNode connections.

## Control Flow
Implementation in `filehandle.cc` uses located block metadata to select DataNodes and delegates protocol work to `BlockReaderImpl`.

## State And Persistence
Members capture cluster/path identity, shared async runtime, client name, immutable file/block metadata, bad-node tracker, current offset, cancellation state, live readers, event handlers, and atomic bytes-read count.

## Dependencies And Integration Points
Included by C bindings and filesystem code. It depends on reader group/block reader types, `IoService`, async stream/cancellation/events, bad DataNode tracking, generated protocol classes, and x-platform types.

## Risks
The documented threading model is restrictive; callers must avoid concurrent sequential `Read`, `Seek`, and callback replacement. Protected factories are test seams and must preserve reader registration/cancellation semantics when overridden.

## Test Signals
Tests should instantiate with mock file info and DataNode connections, override factories for deterministic block reads, and validate cancellation/statistics/seek behavior exposed through the public `FileHandle` API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/fs/filehandle.h -->
