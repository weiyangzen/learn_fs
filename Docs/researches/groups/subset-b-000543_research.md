# subset-b-000543 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/CMakeLists.txt -->
## sources/distributed-fs/beegfs/common/CMakeLists.txt

### Purpose
This CMake file defines the BeeGFS common userspace build. It collects a large static `beegfs-common` library, the `test-common` executable, and the dynamically loaded `beegfs_ib` RDMA socket library.

### Important APIs, Types, And Functions
The build requires `pkg-config` and `libnl-route-3.0`, adds `source` as an include root, and links `beegfs-common` with libnl, OpenSSL, and crypto. The optional test target includes focused unit tests for networking, path, locking, serialization, bit stores, striping, and `TimerQueue`. The `beegfs_ib` target contains `RDMASocketImpl`, `IBVSocket`, and `OpenTk_IBVSocket`.

### Control Flow
Configuration first resolves libnl, then declares `beegfs-common` with all common source/header inputs. Tests are added unless `BEEGFS_SKIP_TESTS` is set. The RDMA library is declared after common code and linked with `rdmacm` and `ibverbs`.

### State, Persistence, And Dependencies
This file persists build graph membership rather than runtime state. It is the integration point that decides whether common code, tests, and RDMA support compile and how they link to system libraries.

### Integration Points
All services and tools using BeeGFS common code depend on this target. `beegfs_ib` installs to `usr/lib` as component `libbeegfs-ib`, matching the runtime RDMA socket callback/plugin path.

### Risks
The static source list is easy to desynchronize from repository changes. RDMA builds require system `rdmacm`/`ibverbs`; missing development packages break `beegfs_ib`. Tests only cover a subset of common components, so build success does not validate all listed networking and config paths.

### Test Signals
Run the CMake configuration, build `beegfs-common` and `beegfs_ib`, and run `ctest` for `test-common`. `TestTimerQueue.cpp` is the direct signal for the timer component in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.cpp -->
## sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.cpp

### Purpose
`RDMASocketImpl.cpp` adapts the C-style `IBVSocket` API to the BeeGFS `RDMASocket` C++ interface. It is the object used by the stream listener and connection pools when RDMA support is enabled.

### Important APIs, Types, And Functions
The file exports `beegfs_socket_impl` with callbacks for RDMA availability, `ibv_fork_init`, and socket allocation. `RDMASocketImpl` implements `connect`, `bindToAddr`, `listen`, `accept`, `shutdown`, `send`, `sendto`, `recv`, `recvT`, `checkConnection`, `nonblockingRecvCheck`, and `checkDelayedEvents`. Under `BEEGFS_NVFS` it also exposes synchronous RDMA read/write wrappers using remote buffer keys.

### Control Flow
Construction initializes default buffer count, buffer size, service level, and an underlying `IBVSocket`. Client connections resolve through `Socket::connect(host, port, SOCK_STREAM)` then `connect(SocketAddress)`, which calls `IBVSocket_connectByIP` and adopts the receive completion fd. Listening binds an RDMA CM id and switches `fd` to the connection-manager fd. Accept wraps successful `IBVSocket_accept` results in a new `RDMASocketImpl`; ignored RDMA internal events return null. Send paths require the full payload to be accepted or throw. Receive paths translate zero, timeout, and errors into BeeGFS socket exceptions.

### State, Persistence, And Dependencies
State is in the wrapped `IBVSocket*`, inherited peer/bind fields, socket stats, `fd`, and `IBVCommConfig`. There is no durable persistence. The file depends on `AbstractApp`, `System`, `PThread`, `StringTk`, `IPAddress`, `RDMASocket`, and the `IBVSocket` implementation.

### Integration Points
`beegfs_socket_impl` is the bridge used by BeeGFS RDMA socket factory code. `StreamListener` polls the fd returned here, calls `accept`, and uses `nonblockingRecvCheck` to distinguish real RDMA data from internal completion events.

### Risks
The adapter assumes `IBVSocket_send` sends all requested bytes; partial sends are fatal. `shutdownAndRecvDisconnect` does not wait for a peer disconnect despite its name. `setBuffers` and TOS only affect unconnected sockets. Statistics are updated only on successful user-visible sends/receives.

### Test Signals
Useful tests include RDMA device absence, connect/listen/accept with real or mocked RDMA CM events, partial-send failure injection, receive timeout mapping, delayed accept-event handling, and stream listener false-alarm handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.h -->
## sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.h

### Purpose
This header declares `RDMASocketImpl`, the concrete RDMA socket implementation hidden behind the common `RDMASocket` interface.

### Important APIs, Types, And Functions
The class overrides the full stream-style socket surface: connect, bind, listen, accept, shutdown, send/receive, timeout receive, connection checks, and delayed event checks. It stores an `IBVSocket*`, the pollable fd, and `IBVCommConfig`. Inline setters configure buffer count/size, RDMA timeouts, type of service, and test-only connection rejection rate.

### Control Flow
Consumers instantiate through factory callbacks rather than constructing this class directly. Accepted sockets use a private constructor that adopts a prepared `IBVSocket` and peer identity.

### State, Persistence, And Dependencies
The header depends on `IPAddress`, `IBVSocket`, and `RDMASocket`. Runtime state is volatile socket and RDMA queue state, not persisted across process restarts.

### Integration Points
This declaration is part of the `beegfs_ib` shared library and supplies the ABI used by the common RDMA socket factory. The exported `beegfs_socket_impl` symbol is declared here for plugin lookup.

### Risks
The class owns a raw `IBVSocket*` and relies on destructor cleanup. Inline configuration methods can be called after connection, but comments warn some options no longer take effect.

### Test Signals
Compile/link tests should verify overrides match `RDMASocket`. Runtime tests should validate fd selection before and after listen/connect/accept and ensure destruction releases adopted `IBVSocket` instances exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.cpp -->
## sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.cpp

### Purpose
`IBVSocket.cpp` implements a socket-like abstraction over RDMA CM and ibverbs. It handles RDMA connection setup, accept, buffer registration, queue pair creation, flow control, completion polling, shutdown, and optional NVFS RDMA read/write operations.

### Important APIs, Types, And Functions
Public C-style entry points include `IBVSocket_init`, `construct`, `destruct`, `rdmaDevicesExist`, `fork_init_once`, `connectByName`, `connectByIP`, `bind`, `bindToAddr`, `listen`, `accept`, `shutdown`, `recv`, `recvT`, `send`, `checkConnection`, `nonblockingRecvCheck`, `checkDelayedEvents`, getters, timeout/TOS setters, and test connection rejection. Key helpers include `__IBVSocket_createCommContext`, `cleanupCommContext`, `initCommDest`, `parseCommDest`, `postRecv`, `postSend`, `recvWC`, `flowControlOnRecv`, `flowControlOnSendWait`, `waitForRecvCompletionEvent`, `waitForTotalSendCompletion`, `disconnect`, `close`, and `initEpollFD`.

### Control Flow
Client connect resolves address and route, creates a communication context, posts receive buffers, sends private connection data, temporarily switches the CM fd to nonblocking mode, polls for `RDMA_CM_EVENT_ESTABLISHED` with exponential sleep, parses remote private data, and initializes epoll. Server accept consumes delayed or new CM events, validates private data, creates a child context, accepts the request, waits for the subsequent established event, then returns the child socket. Send copies user data into registered send buffers, waits for flow-control credit, posts sends, and waits for completions when all buffers are in use. Receive drains incomplete packet fragments first, waits for flow-control packets when necessary, polls receive completions, and reposts receive buffers.

### State, Persistence, And Dependencies
`IBVSocket` owns RDMA CM channel/id, local and remote `IBVCommDest`, `IBVCommContext`, epoll fd, error state, delayed CM event queue, type of service, timeout config, bind IP, and test rejection counters. `IBVCommContext` owns protection domain, memory regions, completion queues, queue pair, send/recv buffers, flow-control counters, and incomplete send/recv state. All state is process memory and registered memory; cleanup destroys QP/CQs/MRs/CM resources.

### Integration Points
`RDMASocketImpl` translates this API into BeeGFS socket exceptions. `StreamListener` relies on `getRecvCompletionFD`, `getConnManagerFD`, `nonblockingRecvCheck`, and `checkDelayedEvents`. The file depends on `rdmacm`, `ibverbs`, `epoll`, BeeGFS logging, threading app access for device removal, serialization endian helpers, and optional NVFS worker buffer definitions.

### Risks
The code is highly stateful and sensitive to RDMA event ordering. Accepted sockets may receive disconnect events through the listener channel, so cleanup and false alarms require careful coordination. Flow control uses tiny control sends and counters initialized to `bufNum - 1`; off-by-one errors can cause receiver-not-ready timeouts or hangs. Connection setup changes fd blocking mode and must restore it on all paths. `commCfg->bufSize * commCfg->bufNum` can overflow before the max check if types remain `unsigned`. NVFS memory-region caching can grow until socket destruction.

### Test Signals
High-value signals are RDMA loopback connect/listen/accept, rejected and malformed private data, route/address failures, device removal, flow-control exhaustion, partial receive continuation, nonblocking false-alarm clearing, idle disconnect checks, timeout configuration, shutdown with incomplete sends, and valgrind/resource-leak checks for MR/CQ/QP cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.h -->
## sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.h

### Purpose
This internal header defines the concrete RDMA socket data structures and helper prototypes used by `IBVSocket.cpp`.

### Important APIs, Types, And Functions
It defines work-id offsets, private-data protocol constants, `IBVIncompleteRecv`, `IBVIncompleteSend`, `IBVTimeoutConfig`, packed `IBVCommDest`, `IBVCommContext`, and `IBVSocket`. It declares helper functions for context construction, buffer registration, private-data parsing, posting recv/send/read/write work requests, flow control, completion waiting, disconnect/close, and epoll setup.

### Control Flow
The structures encode the lifecycle: CM id/channel first, communication context creation after route/connect request, local/remote destination exchange during handshake, then queue operations and completion polling after connection establishment.

### State, Persistence, And Dependencies
State includes registered memory regions, CQs, QP, buffers, flow-control counters, incomplete transfer markers, delayed CM events, and timeout settings. The header depends on BeeGFS common utilities, serialization endian conversion, sockets, polling, `infiniband/verbs.h`, and `rdma/rdma_cma.h`.

### Integration Points
Only the RDMA socket implementation should include this header. `OpenTk_IBVSocket.h` exposes the smaller public C interface to the C++ adapter.

### Risks
The packed `IBVCommDest` is a wire/private-data ABI and must remain architecture-stable. Work-id constants are used to classify completions; changing them can break send/recv/read/write accounting. Many fields are raw pointers with manual ownership.

### Test Signals
ABI-sensitive tests should verify `sizeof(IBVCommDest)`, endian conversions, work-id classification, and cleanup behavior after partial context construction failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/IBVSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/OpenTk_IBVSocket.h -->
## sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/OpenTk_IBVSocket.h

### Purpose
This header is the public C-style interface for the ibverbs socket abstraction consumed by `RDMASocketImpl`.

### Important APIs, Types, And Functions
It forward-declares `IBVSocket` and `IBVCommConfig`, defines `IBVSocket_AcceptRes`, declares construction/destruction, RDMA availability and fork initialization, connect/bind/listen/accept/shutdown, optional NVFS read/write, send/receive, connection checks, fd getters, TOS/timeouts setters, and test rejection controls. `IBVCommConfig` contains `bufNum`, `bufSize`, and `serviceLevel`.

### Control Flow
Callers construct a socket, configure buffers/timeouts/TOS before connecting or listening, then use the socket-like operations. Accept returns a tri-state result to distinguish real errors, ignored internal CM events, and successful connections.

### State, Persistence, And Dependencies
The interface hides all RDMA state behind opaque pointers. It depends only on BeeGFS `IPAddress` and system socket address declarations.

### Integration Points
This is the narrow boundary between BeeGFS common C++ sockets and the RDMA implementation library. It is included by `RDMASocketImpl.h` and compiled into `beegfs_ib`.

### Risks
The interface exposes raw pointers and C return codes, so callers must translate errors consistently and destroy sockets on every path. Buffer configuration comments are external to this header, so misuse after connection is possible.

### Test Signals
API tests should cover accept tri-state handling, fd getters before and after connection/listen, setter effects before connection, and optional NVFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/net/sock/ibvsocket/OpenTk_IBVSocket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Assert.cpp -->
## sources/distributed-fs/beegfs/common/source/common/Assert.cpp

### Purpose
`Assert.cpp` implements debug-build assertion failure reporting for the `ASSERT` macro in `Common.h`.

### Important APIs, Types, And Functions
Under `BEEGFS_DEBUG`, `beegfs_debug::assertMsg(file, line, condition)` formats the failed condition, captures a dynamic backtrace, logs with `LOG(GENERAL, ERR, ...)`, and exits the process.

### Control Flow
The function extracts a basename from the source file path, records the asserting thread name, captures backtrace frames with `backtrace`, grows the vector if exactly full, resolves symbols, logs, and calls `exit(1)`.

### State, Persistence, And Dependencies
There is no persistent state. It depends on `Common.h`, `AbstractApp`, `Logger`, `PThread`, `execinfo`, and streams.

### Integration Points
`Common.h` maps `ASSERT(condition)` to this function only in debug builds. Production builds compile assertions away.

### Risks
`backtrace_symbols` allocation is not freed because the process exits immediately. Logging during a failing assertion can itself depend on initialized logging/threading state.

### Test Signals
Debug-only tests can assert a child process exits nonzero and emits the failed condition plus a backtrace. Release builds should verify `ASSERT` has no side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Assert.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Common.h -->
## sources/distributed-fs/beegfs/common/source/common/Common.h

### Purpose
`Common.h` is a broad compatibility and utility header shared across BeeGFS common code. It centralizes includes, typedefs, timeout defaults, memory macros, compiler compatibility shims, logging type definitions, debug assertions, and data-version constants.

### Important APIs, Types, And Functions
It defines container typedefs for string and integer maps/lists/vectors/sets, `CONN_LONG_TIMEOUT`, `CONN_MEDIUM_TIMEOUT`, `CONN_SHORT_TIMEOUT`, `BEEGFS_MIN/MAX`, `SAFE_DELETE`, `SAFE_FREE`, `SAFE_ASSIGN`, `likely/unlikely`, `BEEGFS_BUG_ON`, `LogType`, compiler shims for `override`, enum class equality, `nullptr`, `noexcept`, `std::chrono::steady_clock`, `ASSERT`, `USE_READDIR_R`, `BEEGFS_FALLTHROUGH`, `BEEGFS_NODISCARD`, and `BEEGFS_DATA_VERSION`.

### Control Flow
Most content is compile-time. Runtime behavior appears in macros that free memory, log bugs/backtraces, or invoke debug assertions.

### State, Persistence, And Dependencies
The file introduces no owned state, but its constants affect network timeouts and protocol/data version compatibility. It depends on many libc, POSIX, STL, networking, pthread, and Boost headers.

### Integration Points
Almost every file in this subset includes `Common.h` directly or indirectly. Config defaults use the connection timeout constants, logging uses `LogType`, RDMA and listeners use `likely/unlikely` and safe free macros.

### Risks
Because this header is global, changes have very large blast radius. Macros evaluate arguments in conventional macro ways and can hide ownership changes. The compatibility shims for old compilers may be obsolete but still affect parsing.

### Test Signals
Build coverage is the main signal. Focused checks should cover debug assertion behavior, timeout defaults via config fallback, `BEEGFS_DATA_VERSION` compatibility, and macro use in cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/NumericID.h -->
## sources/distributed-fs/beegfs/common/source/common/NumericID.h

### Purpose
`NumericID` is a template wrapper that gives numeric identifiers strong types while preserving numeric ordering, serialization, hashing, and conversion behavior.

### Important APIs, Types, And Functions
`NumericID<T, Tag>` stores a value of type `T`, exposes `val`, decimal and uppercase hex string conversions, parsing from decimal/hex strings, serialization through `ctx % value`, comparison operators, increment/decrement, boolean validity semantics, and stream operators. It specializes `std::hash` and `std::numeric_limits` for the wrapper.

### Control Flow
The class is value-like. String parsing uses string streams, comparison and arithmetic delegate to the wrapped value, and serialization gives the framework access to the private value through the supplied object/context pattern.

### State, Persistence, And Dependencies
Each object persists only its numeric value. Serialized forms store the underlying numeric value, preserving wire/on-disk compatibility with raw numeric IDs. Dependencies are serialization and string toolkit headers plus streams.

### Integration Points
BeeGFS node IDs, target IDs, group IDs, and storage pool IDs can use distinct tags to avoid accidental cross-type assignment while remaining usable in maps, unordered maps, streams, and numeric limit contexts.

### Risks
Parsing does not report conversion failure explicitly. `operator!` treats zero as invalid, which must match every ID domain that uses the template. Extending `std::numeric_limits` is useful but broad and should remain aligned with the underlying type.

### Test Signals
Tests should cover type separation, serialization round trips, decimal/hex parsing, map and unordered_map use, bool/zero semantics, numeric_limits forwarding, and stream operators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/NumericID.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.cpp

### Purpose
`AbstractApp.cpp` implements common application runtime services: PID-file locking/updating, component shutdown waiting, out-of-memory handling, global runtime initialization/destruction, NIC logging, NIC/route propagation, and no-default-route parsing.

### Important APIs, Types, And Functions
Key functions are `createAndLockPIDFile`, `updateLockedPIDFile`, `waitForComponentTermination`, `handleOutOfMemFromNew`, `performBasicInitialRunTimeChecks`, `basicInitializations`, `basicDestructions`, `logUsableNICs`, `updateLocalNicListAndRoutes`, and `initNoDefaultRouteList`. Static `didRunTimeInit` gates app construction through the header constructor.

### Control Flow
PID setup validates absolute paths before delegating to `StorageTk`. Component termination waits two seconds, logs if still running, then joins fully. OOM handling logs stderr and BeeGFS backtrace before throwing `std::bad_alloc`. Runtime checks validate time and condition-clock support, then initialize condition attributes. NIC updates optionally reload the routing table, replace the protected local NIC list, log capabilities, and apply the list to node stores.

### State, Persistence, And Dependencies
The only durable artifact is the PID file managed by `LockFD`. In-memory state includes static runtime initialization state, local NIC list, no-default-route filter, and routing table factory. Dependencies include `StorageTk`, `NodesTk`, `Time`, `Condition`, `NetworkInterfaceCard`, `NetFilter`, logging, and thread components.

### Integration Points
All concrete BeeGFS apps derive from `AbstractApp`. Listener code calls `PThread::getCurrentThreadApp()` to access config, message factories, routing tables, and component exception handling.

### Risks
Construction before `runTimeInitsAndChecks` throws. OOM handling itself uses logging and backtrace code that may allocate or depend on locks. `basicDestructions` runs from the base destructor, so derived classes must have stopped users of static condition state.

### Test Signals
Tests should cover PID path validation, locked PID update after daemonization, runtime init ordering, component join timeout logging, NIC update propagation to node stores, and invalid CIDR handling in `initNoDefaultRouteList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.h -->
## sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.h

### Purpose
This header defines the abstract base class for BeeGFS userspace applications and the runtime services exposed to common components.

### Important APIs, Types, And Functions
Concrete apps must implement `stopComponents`, `handleComponentException`, `handleNetworkInterfaceFailure`, `getCommonConfig`, `getNetFilter`, `getTcpOnlyFilter`, and `getNetMessageFactory`. The base exposes PID helpers, component wait, NIC logging, runtime initialization through `runTimeInitsAndChecks`, routing table initialization/update/access, and optional `getStreamListenerByFD`.

### Control Flow
The protected constructor verifies static runtime initialization and installs the global `new` handler. `runTimeInitsAndChecks` performs checks, initializes shared threading condition state, then marks the process ready for app construction.

### State, Persistence, And Dependencies
State includes `localNicList`, `localNicListMutex`, optional `noDefaultRouteNets`, and a `RoutingTableFactory`. The class derives from `PThread`, making the main app itself a thread context.

### Integration Points
Common components use this as their access point for configuration, filters, routing, message factories, and failure escalation. RDMA device-removal handling and listener exception handling both reach concrete apps through this interface.

### Risks
The base destructor calls `basicDestructions`; derived shutdown order must ensure no component still needs those static resources. `getLocalNicList` returns a copy, which is safe but can become stale immediately.

### Test Signals
Compile-time tests should verify concrete app implementations satisfy pure virtual methods. Runtime tests should validate initialization ordering, local NIC list locking/copy behavior, and routing table creation with no-default-route filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/AbstractApp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.cpp

### Purpose
`AbstractConfig.cpp` implements shared configuration loading, defaults, parsing, validation, authentication-file hashing, socket buffer post-processing, and network-list loading.

### Important APIs, Types, And Functions
Key methods are `initConfig`, `loadDefaults`, `applyConfigMap`, `initImplicitVals`, `initInterfacesList`, `initConnAuthHash`, `initSocketBufferSizes`, `eraseFromConfigMap`, `loadFromFile`, `loadFromArgs`, `assignKeyIfNotZero`, and free function `loadNetworkList`.

### Control Flow
Initialization first loads defaults and command-line args to discover `cfgFile`. If a config file is set, it clears the map and reloads defaults, file entries, then command-line overrides. `applyConfigMap` consumes recognized keys, maps deprecated TCP/UDP port settings into unified ports, validates timeout tuple sizes, and throws on unknown keys when enabled. Authentication hashing reads up to 1024 bytes of binary auth file content, optionally retries with elevated saved fs ids on `EACCES`, rejects missing/short files unless authentication is explicitly disabled, and computes `HashTk::authHash`.

### State, Persistence, And Dependencies
Parsed settings persist in inherited `ICommonConfig` fields and `cfgFile`; `configMap` is transient and consumed during parsing. Dependencies include `StringTk`, `StorageTk`, `MapTk`, `System`, `HashTk`, logging, and filesystem/syscall access.

### Integration Points
All concrete service configs inherit these defaults and parsing rules. Network listeners consume UDP/TCP/RDMA buffer sizes, ports, filters, authentication hash, timeout values, and RDMA TOS settings.

### Risks
Authentication now fails closed unless `connDisableAuthentication` is true, so deployments without `connAuthFile` fail early. Deprecated per-protocol ports can conflict with unified settings. Utility tools tolerate a five-field `connRDMATimeouts` value by ignoring it, which can hide misconfiguration. `assignKeyIfNotZero` rejects zero only when exception mode is enabled.

### Test Signals
Tests should cover precedence of defaults/file/args, unknown-key behavior, deprecated port reconciliation, timeout tuple validation, auth file missing/empty/permission paths, socket buffer legacy derivation, interface file/list exclusivity, and invalid CIDR logging in `loadNetworkList`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.h

### Purpose
This header declares the shared base class for BeeGFS configuration parsers.

### Important APIs, Types, And Functions
`AbstractConfig` stores `configMap`, original argc/argv, and `cfgFile`. Protected hooks include `loadDefaults`, `applyConfigMap`, `initImplicitVals`, `initInterfacesList`, `initConnAuthHash`, `initSocketBufferSizes`, `loadFromFile`, `loadFromArgs`, `eraseFromConfigMap`, and `assignKeyIfNotZero`. Inline helpers redefine keys and test key matches with optional `--` prefix and case-insensitivity.

### Control Flow
Derived constructors call `initConfig` after their own construction so virtual default/application hooks dispatch correctly.

### State, Persistence, And Dependencies
Configuration state persists in inherited `ICommonConfig` fields after `configMap` entries are consumed. Dependencies include `Common`, `MapTk`, `InvalidConfigException`, `ConnAuthFileException`, and `ICommonConfig`.

### Integration Points
Concrete app configs extend this class to add service-specific keys while reusing common networking/logging/auth settings. Free function `loadNetworkList` is declared here for consumers that need CIDR filters.

### Risks
Calling `initConfig` from the base constructor would be unsafe; the comment documents that derived classes must call it. `addDashes` changes both key shape and matching case-sensitivity, so command-line style parsers must use it intentionally.

### Test Signals
Derived config tests should verify virtual hook ordering, dashed-key matching, map cleanup of consumed keys, and that service-specific unknown keys are handled by derived `applyConfigMap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/AbstractConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ConnAuthFileException.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/ConnAuthFileException.h

### Purpose
This header defines the named exception type used for connection-authentication file configuration errors.

### Important APIs, Types, And Functions
`DECLARE_NAMEDEXCEPTION(ConnAuthFileException, "ConnAuthFileException")` expands to a BeeGFS named exception class.

### Control Flow
There is no runtime control flow in the header. `AbstractConfig::initConnAuthHash` throws this type when the auth file is missing or cannot be opened.

### State, Persistence, And Dependencies
The exception carries message state inherited from `NamedException`. Dependencies are `NamedException.h` and `Common.h`.

### Integration Points
Config initialization and app startup can catch this specific type separately from generic invalid config errors if they want auth-specific user messaging.

### Risks
The type has no extra fields, so callers must parse or preserve the message for details.

### Test Signals
Config tests should assert missing/unreadable auth file paths throw `ConnAuthFileException` rather than a generic exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ConnAuthFileException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.cpp

### Purpose
This file implements shared helper loading for simple line-based configuration files.

### Important APIs, Types, And Functions
`ICommonConfig::loadStringListFile` reads a file into a `StringList`, trimming whitespace and skipping empty lines and lines beginning with `STORAGETK_FILE_COMMENT_CHAR`.

### Control Flow
The function opens an `ifstream`, throws `InvalidConfigException` on open failure, loops through lines until EOF/failure, trims each line, appends meaningful non-comment lines, and closes the stream.

### State, Persistence, And Dependencies
It does not persist state; it fills the caller-provided list. Dependencies include `StringTk`, `StorageTk`, and `ICommonConfig`.

### Integration Points
Used by interface list loading, network filter loading, and any common config path that takes newline-separated files.

### Risks
Inline comments after values are not stripped; only full-line comments are ignored. Stream failures after partial reads are not surfaced except through omitted lines.

### Test Signals
Tests should cover missing file, whitespace trimming, empty lines, full-line comments, and values containing comment characters not in column zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.h

### Purpose
`ICommonConfig.h` defines the shared configuration interface and storage fields used by BeeGFS common components.

### Important APIs, Types, And Functions
It stores logging settings, service ports and port shift, RDMA/TCP/UDP connection settings, buffer sizes, authentication fields, network filter files, routing restrictions, IPv6 flag, messaging and RDMA timeouts, management host, state update interval, and test connection rejection rate. It exposes getters that apply port shift and setters for the rejection rate.

### Control Flow
Most methods are simple accessors. Port getters return zero when the base port is zero, otherwise add `connPortShift`.

### State, Persistence, And Dependencies
Concrete config classes populate the protected fields during startup. These values are process configuration state consumed by listeners, connection pools, logging, and management code. Dependencies are `Common` and `InvalidConfigException`.

### Integration Points
`AbstractApp::getCommonConfig` exposes this interface to `StreamListener`, `AbstractDatagramListener`, RDMA socket setup, logger creation, and other common components.

### Risks
Fields are protected and mutable by subclasses; invariants depend on `AbstractConfig::applyConfigMap`. `connectionRejectionRate` is test-oriented but visible in the common config interface.

### Test Signals
Tests should check port shift behavior, getter defaults after `AbstractConfig` parsing, RDMA timeout propagation, authentication hash access, and reset of rejection count when setting rejection rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/InvalidConfigException.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/InvalidConfigException.h

### Purpose
This header defines the named exception type used for invalid BeeGFS configuration.

### Important APIs, Types, And Functions
`DECLARE_NAMEDEXCEPTION(InvalidConfigException, "InvalidConfigException")` creates the exception class with BeeGFS named-exception behavior.

### Control Flow
There is no local control flow. Config parsing, PID-file setup, and logger setup throw this type when validation fails.

### State, Persistence, And Dependencies
The exception stores its inherited message only. Dependencies are `NamedException.h` and `Common.h`.

### Integration Points
It is the primary error type for startup configuration failures across common app/config code.

### Risks
No structured error codes are attached, so callers must rely on catch type and message text.

### Test Signals
Startup/config tests should assert invalid values, unknown keys, bad files, and PID path problems throw `InvalidConfigException` where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/InvalidConfigException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/LogContext.h -->
## sources/distributed-fs/beegfs/common/source/common/app/log/LogContext.h

### Purpose
`LogContext` is a lightweight contextual logging helper that captures a context string and forwards messages/backtraces to the global `Logger`.

### Important APIs, Types, And Functions
It defines debug logging macros controlled by `LOG_DEBUG_MESSAGES`, backtrace array size, constructors, `log` overloads by topic/level, `logErr`, and `logBacktrace`. A protected constructor and `setLogger` support derived context providers.

### Control Flow
Construction snapshots `Logger::getLogger()`. Logging methods return silently if no logger is available. `logBacktrace` captures stack frames with `backtrace`, resolves symbols, logs them, and frees symbol storage if logging proceeds.

### State, Persistence, And Dependencies
State is a context string and raw `Logger*`. Dependencies include `Logger`, `AbstractApp`, `PThread`, `Common`, and `execinfo`.

### Integration Points
Used throughout app, config, listener, assertion, and component code for stable context names without passing logger references everywhere.

### Risks
Because the logger pointer is captured at construction, contexts created before logger initialization will not start logging later unless reset. In `logBacktrace`, if no logger exists after `backtrace_symbols`, the function returns without freeing symbols.

### Test Signals
Tests should cover logging with initialized and missing logger, context string propagation, backtrace logging, and debug macro compilation in debug and non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/LogContext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/log/Logger.cpp

### Purpose
`Logger.cpp` implements the global BeeGFS logger, including topic names, stderr fallback formatting, syslog/file output, timestamp formatting, backtrace emission, and line-count based log rotation.

### Important APIs, Types, And Functions
The file defines `Logger::logger`, `Logger::LogTopics`, syslog level mapping, constructor/destructor, `logStdErr`, `logGrantedUnlocked`, `logGranted`, `logBacktraceGranted`, `getTimeStr`, `prepareLogFiles`, `rotateLogFile`, and `rotateStdLogChecked`.

### Control Flow
Construction initializes topic log levels, rwlock, time format, file pointers, and log files. Normal logging takes a read lock, writes either file/stdout or syslog, increments line count, unlocks, then checks rotation. Rotation takes a write lock, closes the current file, renames old files through suffixes, opens a new file, and resets line count. `logStdErr` provides pre-singleton fallback.

### State, Persistence, And Dependencies
Persistent artifacts are log files and rotated `.old-N` files. In-memory state includes singleton ownership, log levels, file handles, rwlock, line counters, and rotation settings. Dependencies include `StringTk`, `PThread`, `TimeAbs`, `syslog`, pthread rwlocks, and config exception types.

### Integration Points
`Logger.h` macros, `LogContext`, assertions, config, RDMA, and listeners all use this singleton. Config values determine log type, date inclusion, file path, max lines, and rotated file count.

### Risks
The rwlock favors readers, so heavy logging can delay rotation. File rotation ignores rename failures. If opening a configured file fails during construction, it throws after falling back to stdout. `logTopicFromName` compares `const char*` entries to `std::string`; this relies on overloaded comparison and should be kept clear in reviews.

### Test Signals
Tests should cover stderr fallback, file logging, syslog mode where feasible, rotation thresholds, topic name mapping, invalid log file path handling, timestamp formatting, and concurrent logging during rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.h -->
## sources/distributed-fs/beegfs/common/source/common/app/log/Logger.h

### Purpose
`Logger.h` declares BeeGFS logging levels, topics, helper formatting types, the `Logger` singleton, and the `LOG`/`LOG_CTX` macro family.

### Important APIs, Types, And Functions
It defines `LogLevel`, `LogTopic`, `beegfs::logging::SystemError`, `InBase`, `LogInfos`, and class `Logger`. Public methods include `log` overloads, `logBacktrace`, log level getters/setters, topic name conversion, singleton create/destroy/get/isInitialized, and stderr fallback. Macros support structured key/value log items, optional level-gated items, `sysErr`, `hex`, and `oct` formatting helpers.

### Control Flow
The macro path first checks the global logger and topic threshold. It builds a message with optional structured fields, then dispatches either to the singleton or `logStdErr` if no logger exists.

### State, Persistence, And Dependencies
The class owns singleton logger state declared in the cpp file. Header dependencies include config exceptions, storage errors, atomics, pthread/threading, Boost preprocessor, Boost ios state, and system error utilities.

### Integration Points
Every file in this subset that logs uses either `LOG`, `LOG_CTX`, or `LogContext`, making this header the common logging contract.

### Risks
The macro layer is complex and compile-time fragile. `setLogLevel` and `getLogLevels` are explicitly not thread-safe. Topic enum and `LogTopics` array must stay in sync. Macros evaluate streamed values only when the level passes, but arguments must still compile.

### Test Signals
Compile tests should exercise one-, two-, and three-part structured items, topic thresholds, no-logger fallback, bool/error_code/SystemError formatting, topic string conversion, and debug macro elision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/benchmark/StorageBench.h -->
## sources/distributed-fs/beegfs/common/source/common/benchmark/StorageBench.h

### Purpose
This header defines shared constants and enums for BeeGFS storage benchmark control and status reporting.

### Important APIs, Types, And Functions
It declares error code macros, `StorageBenchResultsMap` keyed by target ID with throughput values, `StorageBenchAction`, `StorageBenchType`, `StorageBenchStatus`, and `STORAGEBENCHSTATUS_IS_ACTIVE`.

### Control Flow
There is no executable control flow. The active-status macro classifies running, finishing, and stopping as active benchmark states.

### State, Persistence, And Dependencies
No local state is stored. The types define protocol/control state used by benchmark operators and messages elsewhere. Dependency is `Common.h`.

### Integration Points
Storage benchmark management messages and workers use these values to coordinate start, stop, status, cleanup, and error reporting.

### Risks
These are preprocessor constants and unscoped enums, so names are global. Numeric values may be externally visible through network messages or user output and should not change casually.

### Test Signals
Tests should verify active status classification, error propagation through benchmark messages, and compatibility of enum numeric values if serialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/benchmark/StorageBench.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.cpp

### Purpose
`AbstractDatagramListener.cpp` implements the shared UDP datagram listener for BeeGFS messages, including socket binding, interface-restricted sending, receive parsing, ack retry helpers, and self-wakeup.

### Important APIs, Types, And Functions
Core methods are `configSocket`, `initSocks`, `initBuffers`, `findSenderSock`, `findSenderSockUnlocked`, `setLocalNicList`, `run`, `listenLoop`, `sendToNodesUDP`, `sendToNodesUDPwithAck`, `sendToNodeUDPwithAck`, `sendBufToNode`, `sendMsgToNode`, `sendDummyToSelfUDP`, `incAckCounter`, and `isDGramFromSelf`.

### Control Flow
Construction initializes sockets immediately and throws on failure. Runtime allocates aligned send/receive buffers, then loops on `recvfromT`. Incoming datagrams from local addresses/port are ignored; remaining buffers are parsed by the app net message factory, validated for type, length, and sequence fields, then dispatched to subclass `handleIncomingMsg`. Sending selects either a wildcard UDP socket or a per-interface socket based on routing-table matches when outbound restriction is enabled. Ack sends register wait IDs, send to remaining nodes, wait, retry, and unregister.

### State, Persistence, And Dependencies
State includes UDP socket group, per-interface sockets, destination-to-source cache, routing table, local NIC list, net filter, ack store, aligned buffers, receive timeout, mutex, and ack counter. No durable state is written. Dependencies include `PThread`, `AbstractApp`, `MessagingTk`, serialization, `DummyMsg`, `StandardSocket`, node stores, and routing.

### Integration Points
Derived listeners such as `RegistrationDatagramListener` implement message policy. Nodes and management flows use UDP multicast-style sends and ack tracking for control-plane messages.

### Risks
The listener uses a single mutex for intertwined send/routing/socket state; long socket operations under this lock can affect concurrency. `sendto` wrappers return positive errno constants like `ENETUNREACH` rather than negative error returns, so callers treat only `>0` as sent in some paths. `initBuffers` ignores allocation failures and could leave null buffers. Cached route choices must be cleared when local NICs change, which `initSocks` does only in restricted mode.

### Test Signals
Tests should cover unrestricted and restricted binding, route cache invalidation on NIC updates, self-datagram filtering, invalid message rejection, ack retry/unregister behavior, net filter exclusion, dummy self-wakeup, and allocation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.h -->
## sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.h

### Purpose
This header declares the abstract UDP datagram listener base used by BeeGFS components that receive and send datagram messages.

### Important APIs, Types, And Functions
It defines UDP buffer sizes, `StandardSocketMap`, public send helpers, ack send helpers, `sendDummyToSelfUDP`, `sendto` wrappers, receive timeout setter, UDP port getter, and `setLocalNicList`. Subclasses must implement `handleIncomingMsg`.

### Control Flow
The class derives from `PThread`; `run` and `listenLoop` are private base behavior, while subclass control is limited to handling already parsed incoming messages.

### State, Persistence, And Dependencies
The class stores sockets, interface maps, routing/source cache, buffers, ack store, net filter, local NICs, and synchronization state. Dependencies include logging, atomics, threading, standard sockets, acknowledgeable messages, node stores, and component exceptions.

### Integration Points
Registration and service-specific datagram listeners inherit this base. Friend work classes can access send mutex for efficient notification batching.

### Risks
The public inline `sendto` overloads expose the unusual `ENETUNREACH`/`EAFNOSUPPORT` positive return behavior. Buffer pointers are raw and initialized after thread start, so message handlers rely on `run` calling `initBuffers` first.

### Test Signals
Compile tests should ensure derived classes implement `handleIncomingMsg`. Runtime tests should validate send path selection, mutex behavior, receive timeout updates, and self-wakeup through `sendDummyToSelfUDP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/ComponentInitException.h -->
## sources/distributed-fs/beegfs/common/source/common/components/ComponentInitException.h

### Purpose
This header defines the named exception thrown when a BeeGFS component cannot initialize.

### Important APIs, Types, And Functions
`DECLARE_NAMEDEXCEPTION(ComponentInitException, "ComponentInitException")` declares the component initialization exception type.

### Control Flow
No local control flow. Constructors for listeners and other components throw this type on socket, pipe, epoll, or related initialization failures.

### State, Persistence, And Dependencies
The exception carries inherited message state only. Dependencies are `NamedException.h` and `Common.h`.

### Integration Points
`StreamListener`, `AbstractDatagramListener`, and `StatsCollector`-adjacent components include this for startup error reporting to `AbstractApp::handleComponentException` or app startup code.

### Risks
No structured component identifier is stored; messages need to include enough context.

### Test Signals
Initialization-failure tests should assert listener socket/epoll failures raise `ComponentInitException` with actionable text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/ComponentInitException.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.cpp

### Purpose
This file implements the minimal datagram listener used during registration, before full application data structures are safe for general message handling.

### Important APIs, Types, And Functions
The constructor forwards setup to `AbstractDatagramListener` with thread name `RegDGramLis`. `handleIncomingMsg` permits only `Ack`, `Heartbeat`, and `Dummy` messages and builds a `NetMessage::ResponseContext` using the sender socket and shared send buffer.

### Control Flow
On each parsed message, it finds a sender socket for the source IP. If none exists, it logs a warning and returns. Allowed message types call `processIncoming`; failures are logged. Other valid messages are logged as invalid in the current registration context.

### State, Persistence, And Dependencies
No additional state beyond the base datagram listener. The method creates temporary high-resolution stats, sender socket references, and response contexts. Dependencies include `IPAddress`, `StandardSocket`, `NetMessage`, and message type constants.

### Integration Points
Used during node/service registration to receive management heartbeats and acknowledgments without allowing broader operations to touch partially initialized app state.

### Risks
The send buffer comes from the base listener and must have been allocated by `run`. The listener intentionally drops otherwise valid messages, so startup sequencing must replace it with the full listener when ready.

### Test Signals
Tests should send heartbeat, ack, dummy, and disallowed message types; verify only allowed types call `processIncoming`, missing route/socket logs a warning, and response context uses the correct source address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.h -->
## sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.h

### Purpose
This header declares the restricted datagram listener used during BeeGFS registration.

### Important APIs, Types, And Functions
`RegistrationDatagramListener` derives from `AbstractDatagramListener`, forwards construction parameters for filters, NICs, ack store, UDP port, and outbound-interface restriction, and overrides `handleIncomingMsg`.

### Control Flow
The header establishes that only incoming-message policy differs from the base listener; all socket and send behavior remains inherited.

### State, Persistence, And Dependencies
No new fields are declared. Dependencies include `IPAddress`, `AbstractDatagramListener`, and `Common`.

### Integration Points
Registration code can instantiate this class where a full datagram listener would be unsafe before local node/app state is complete.

### Risks
The minimal class relies on comments and implementation to enforce allowed message types; future additions should avoid broadening startup behavior accidentally.

### Test Signals
Compile-time and runtime tests should ensure construction succeeds with the same inputs as the base and dispatch remains restricted to registration-safe message types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.cpp

### Purpose
`StatsCollector.cpp` implements periodic collection of high-resolution work-queue statistics and bounded in-memory history retrieval.

### Important APIs, Types, And Functions
Implemented methods are constructor, destructor, `run`, `collectLoop`, virtual `collectStats`, and `getStatsSince`.

### Control Flow
The thread registers signal handling, loops until self-termination with `waitForSelfTerminateOrder(collectIntervalMS)`, and calls `collectStats`. Default collection locks the stats list, calls `workQ->getAndResetStats`, stamps current time in milliseconds, trims history to configured length, and pushes newest stats to the front. Retrieval copies entries newer than `lastStatsMS` to the output list in iteration order.

### State, Persistence, And Dependencies
State is mutex-protected `HighResStatsList`, `MultiWorkQueue*`, interval, and history length. No durable persistence. Dependencies include `TimeAbs`, `PThread`, `AbstractApp`, `LogContext`, and work queue stats types.

### Integration Points
Service components expose recent operation stats through this collector. Derived classes can override `collectStats` for non-work-queue stats sources.

### Risks
The default `collectStats` assumes `workQ` is non-null. `getStatsSince` pushes newest-to-oldest into `outStatsList` despite the comment saying newer stats are pushed to the back; callers should verify ordering expectations.

### Test Signals
Tests should cover interval collection, bounded history, timestamp filtering, work queue reset semantics, null `workQ` behavior in derived classes, and output ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.h -->
## sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.h

### Purpose
This header declares the statistics collector thread and its default history sizing constants.

### Important APIs, Types, And Functions
It defines `STATSCOLLECTOR_COLLECT_INTERVAL_MS`, `STATSCOLLECTOR_HISTORY_LENGTH`, class `StatsCollector`, constructor/destructor, `getStatsSince`, virtual `collectStats`, private `run` and `collectLoop`, and protected state for logging, mutex, stats list, work queue, interval, and history length.

### Control Flow
The class is a `PThread`; execution is internal, with extension through `collectStats` override.

### State, Persistence, And Dependencies
State is in-memory stats history and collection configuration. Dependencies include logging, app/threading, work queue, component exception, net message stats types, and `Common`.

### Integration Points
Common services can embed or subclass this collector to report recent high-resolution operational statistics.

### Risks
Thread-safety depends on all history access taking the mutex. Subclasses overriding `collectStats` need to preserve locking and history bounds if they use shared `statsList`.

### Test Signals
Compile tests for subclass overrides and runtime tests for locking/history behavior under concurrent collection and reads are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StatsCollector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/StreamListener.cpp

### Purpose
`StreamListener.cpp` implements the TCP/RDMA stream acceptor and event dispatcher. It accepts incoming connections, watches active sockets with epoll one-shot edge-triggered events, hands sockets to worker queues, and re-arms returned sockets.

### Important APIs, Types, And Functions
Key methods are constructor/destructor, `initSockReturnPipe`, `initSocks`, `run`, `listenLoop`, `onIncomingStandardConnection`, `onIncomingRDMAConnection`, `onIncomingData`, `onSockReturn`, `rdmaConnIdleCheck`, `applySocketOptions`, `isFalseAlarm`, and `deleteAllConns`.

### Control Flow
Construction creates epoll, a nonblocking return pipe, RDMA listen socket if local capabilities allow, and a TCP listen socket. The listen loop waits on epoll, dispatches listen sockets to accept handlers, dispatches returned socket pipe events to re-arm sockets, and dispatches data sockets to workers. TCP accepts apply TCP options and add accepted sockets with `EPOLLONESHOT | EPOLLET`. RDMA accept loops through delayed CM events and ignores internal events. Incoming data on RDMA first calls `nonblockingRecvCheck` to avoid blocking on false alarms. Real data creates `IncomingDataWork`, marks activity, queues direct or indirect work, and removes the socket from `pollList` until a worker returns it via pipe.

### State, Persistence, And Dependencies
State includes listen sockets, work queue, epoll fd, `PollList`, return pipe, RDMA idle-check timer/counter, and log context. No durable persistence. Dependencies include `AbstractApp`, `IncomingDataWork`, `StandardSocket`, `RDMASocket`, `Pipe`, `PollList`, `NetworkInterfaceCard`, and epoll.

### Integration Points
This is the main network ingress for stream messages. Worker code must return sockets through `sockReturnPipe` after processing so epoll can be re-armed. RDMA behavior depends on `RDMASocketImpl` and `IBVSocket` false-alarm semantics.

### Risks
Ownership moves between `pollList`, worker queue, and return pipe; double deletion or lost sockets are the key hazards. `onSockReturn` reads batches of raw socket pointers and has delicate partial-pointer handling. RDMA idle check deletes inactive RDMA sockets without active probing. RDMA accept currently loops only while `checkDelayedEvents()` returns true, so behavior depends on that function detecting the current readiness event. Edge-triggered one-shot use requires every return path to re-arm correctly.

### Test Signals
Tests should cover TCP accept and socket option failures, RDMA accept ignore/success paths, false-alarm rearming, worker handoff and return pipe batching, epoll rearm failure cleanup, idle RDMA disposal, destructor cleanup, and stress with many simultaneous events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.h -->
## sources/distributed-fs/beegfs/common/source/common/components/StreamListener.h

### Purpose
This header declares the stream listener thread responsible for TCP/RDMA accept and incoming stream socket dispatch.

### Important APIs, Types, And Functions
`StreamListener` exposes constructor/destructor, `getSockReturnFD`, and `getWorkQueue`. Private methods cover socket/pipe initialization, the run loop, incoming connection/data handlers, socket return handling, RDMA idle checks, socket option application, false alarm checks, and cleanup.

### Control Flow
As a `PThread`, the listener owns its event loop internally. External workers interact by writing returned socket pointers to `getSockReturnFD()`.

### State, Persistence, And Dependencies
State includes log context, TCP/RDMA listen sockets, `MultiWorkQueue`, epoll fd, `PollList`, `Pipe`, and RDMA idle-check counters. Dependencies include logging, work queues, component exceptions, socket classes, net messages, nodes, threading, poll utilities, and `Common`.

### Integration Points
Used by BeeGFS services to accept stream connections and dispatch `IncomingDataWork`. It bridges low-level sockets and worker queues.

### Risks
Raw pointer ownership is central and not encoded in types. Public return-pipe fd exposes a low-level protocol: writers must send exact `Socket*` values back.

### Test Signals
Tests should validate construction/destruction ownership, worker return protocol, TCP-only and RDMA-capable startup, and poll list consistency as sockets move between listener and workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.cpp

### Purpose
`TimerQueue.cpp` implements delayed function scheduling backed by a manager thread and an elastic pool of timer worker threads.

### Important APIs, Types, And Functions
Implemented pieces include `TimerWorkList::enqueue/deque/waitingItems`, `TimerWorker` construction/destruction/start/stop/run`, `TimerQueue` construction/destruction, `enqueue`, `cancel`, `run`, `requestWorkers`, and `deactivateWorker`.

### Control Flow
`TimerQueue::enqueue` inserts actions keyed by due time and sequence number, then signals the manager. The manager waits until the next due action or idle timeout, moves due actions into `TimerWorkList`, and requests enough inactive workers for queued work. Workers try an immediate dequeue, then wait up to ten seconds; non-keepalive workers exit when idle, while keepalive workers remain. Destruction stops the manager, wakes/stops workers, and enqueues empty functions to break waits.

### State, Persistence, And Dependencies
State includes a mutex/condition, monotonic-clock queue, sequence counter, work list, worker pool, and inactive-worker map. All state is in-memory. Dependencies include `Condition`, `PThread`, `StringTk`, chrono, map, deque, and function.

### Integration Points
`CMakeLists.txt` includes `TestTimerQueue.cpp`, showing this component has unit coverage. Other BeeGFS components can schedule deferred callbacks without tying up the manager thread.

### Risks
`EntryHandle::cancel` assumes the handle still points to a live queue; handles outliving `TimerQueue` are unsafe. Worker function exceptions are not caught in `TimerWorker::run`, so an action can terminate a worker thread unexpectedly. Worker startup failures cause short retry loops through `workerRetryTimeout`.

### Test Signals
Tests should cover delayed execution ordering, same-time sequence ordering, cancellation before due time, zero-delay self-requeue termination behavior, min/max pool behavior, idle worker deactivation, destructor wakeup, and action exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.h -->
## sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.h

### Purpose
This header declares the delayed task scheduler, worker list, worker threads, and cancellation handle used by BeeGFS common code.

### Important APIs, Types, And Functions
`TimerWorkList` provides thread-safe ready-work enqueue/dequeue/count. `TimerWorker` is a `PThread` with start/stop/run, keepalive behavior, id, and atomic state. `TimerQueue` is a `PThread` with `EntryHandle`, constructor/destructor, `enqueue`, `cancel`, manager `run`, worker request, and worker deactivation.

### Control Flow
`EntryHandle::cancel` delegates to its owning queue. `TimerQueue` manages scheduled actions and workers; workers execute ready actions outside the queue mutex through `TimerWorkList`.

### State, Persistence, And Dependencies
Types encode in-memory scheduler state only. `QueueType` uses `std::chrono::steady_clock` and sequence numbers for deterministic ordering; a static assertion requires millisecond-or-better clock precision.

### Integration Points
Common components can include this header to schedule `std::function<void()>` callbacks. Unit tests are registered through the common CMake file.

### Risks
`TimerQueue` is noncopyable/nonmovable but `EntryHandle` is lightweight and can become dangling if retained after queue destruction. Callback execution is unconstrained; long-running callbacks occupy worker threads.

### Test Signals
Header-level tests should verify API usability with lambdas, move-only captures wrapped in `std::function` where supported, cancellation handle behavior, and pool sizing boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/TimerQueue.h -->
