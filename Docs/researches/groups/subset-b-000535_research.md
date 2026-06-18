# subset-b-000535 research

Grouped research report for BeeGFS client module configuration, logging, common type, and network message files. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/Config.c -->
# sources/distributed-fs/beegfs/client_module/source/app/config/Config.c

## Research
`Config.c` implements the kernel client runtime configuration loader. It initializes string ownership, loads defaults into a `StrCpyMap`, overlays mount options, optionally reloads from `cfgFile`, overlays mount options again, validates the management address, and derives implicit values. Important APIs are `Config_init`, `Config_construct`, `_Config_loadDefaults`, `_Config_applyConfigMap`, file/list loaders, and conversion helpers for cache type, inode ID style, RDMA key type, capability checks, ACL/SELinux modes, and event-log masks.

Control flow is validation-heavy: unknown but recognized obsolete values are ignored, bad scalar/list formats abort mount setup, legacy UDP/TCP port settings are merged into newer combined port settings, and auth hash setup fails unless authentication is explicitly disabled. State is in owned heap strings plus scalar fields; persistence is limited to reading config/auth/list files through kernel file APIs. Dependencies include `StringTk`, `HashTk`, `SocketTk`, `StrCpyMap`, kernel `filp_open`, `kernel_read`/`vfs_read`, and `Config.h`. Risks include silent fallback for unknown enum strings, strict auth-file requirements, line truncation at 1024 bytes, integer conversion edge cases, and keeping retry calculation synchronized with messaging retry waits. Test signals are mount success/failure, expected defaults after omitted values, config-file override precedence, auth-file hash behavior, and RDMA/buffer minimum enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/Config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/Config.h -->
# sources/distributed-fs/beegfs/client_module/source/app/config/Config.h

## Research
`Config.h` defines the public configuration object for the BeeGFS kernel client. The central `struct Config` stores mount/config-file derived values for logging, ports, RDMA, authentication, networking filters, timeouts, cache buffers, path/message buffers, file-cache mode, locking behavior, inode hash style, xattr/ACL/SELinux behavior, quota, event logging, and testing remap state. It also defines enums and string constants for `FileCacheType`, `InodeIDStyle`, `RDMAKeyType`, `CheckCapabilities`, `SELinuxRevalidateMode`, `ACLsRevalidate`, and `EventLogMask`.

The header exposes lifecycle and loader functions plus many static inline getters used throughout the client. Control flow is mostly inline access, with notable behavior in port getters that apply `connPortShift`, `Config_setConnMgmtdGrpcPort` that deliberately does not apply the shift, and `Config_setTuneRefreshOnGetAttr` that sets a runtime flag with a memory barrier. State is mutable after mount for selected values such as management gRPC port, refresh-on-getattr, and test remap status; most other fields are initialized once. Dependencies include `Common.h`, list/map helpers, `StringTk`, and `MountConfig`. Risks are ABI-like coupling: adding config fields requires matching defaults, parser logic, proc/online config handling, and user-space compatibility. Test signals are compile coverage of all inline getters and runtime validation that downstream modules observe derived numeric enum values rather than raw strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/Config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/MountConfig.c -->
# sources/distributed-fs/beegfs/client_module/source/app/config/MountConfig.c

## Research
`MountConfig.c` parses raw Linux mount option strings into a temporary `MountConfig` that later overrides `Config` defaults and config-file values. It uses a kernel `match_table_t` for string options such as `cfgFile`, `logStdFile`, `sysMgmtdHost`, preferred-node files, interface list, auth file, authentication disable, and IPv6 disable; integer options include log level, port shift, management port, and sanity-check timeout; `grpid` is a no-argument flag.

The main control flow in `MountConfig_parseFromRawOptions` splits the option buffer on commas with `strsep`, maps each token via `match_token`, copies strings with `match_strdup`, parses integers with `match_int`, and rejects unknown or invalid tokens. `MountConfig_showOptions` serializes only explicitly set fields back to a `seq_file` for mount display. State is transient and heap-owned by `MountConfig_uninit` in the header. Dependencies are Linux parser/seq APIs, `Common.h` cleanup macros, and `printk_fhgfs` diagnostics. Risks include destructive parsing of the original mount option buffer, comma-separated values being impossible for string options, and string booleans being deferred to `Config.c` rather than validated here. Test signals are successful mount-option round trips through `show_options`, rejection of unknown options, and correct override behavior versus config-file settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/MountConfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/MountConfig.h -->
# sources/distributed-fs/beegfs/client_module/source/app/config/MountConfig.h

## Research
`MountConfig.h` declares and defines the temporary mount-option container used before full client configuration exists. `struct MountConfig` stores optional string pointers, defined flags for integer options, parsed integer values, authentication/network toggles as strings, and the `grpid` mount flag. Inline lifecycle helpers zero-initialize, allocate with `os_kmalloc`, free all owned strings, and destroy with `kfree`.

Control flow is intentionally simple: `MountConfig_init` makes unset fields distinguishable via zero/NULL, parser code sets corresponding fields and defined booleans, `Config.c` later copies only present values into its config map. State is not persistent and not shared after `Config` consumes it. Dependencies are `Common.h` for allocation and safe free macros and `linux/seq_file.h` for option display declarations. Risks are ownership discipline and semantic validation split across files: this header frees string booleans but does not interpret them, so `Config` must remain the authority. Test signals are leak-free mount parse/uninit cycles, correct NULL behavior for absent options, and no double-free when options are overwritten during parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/config/MountConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/log/Logger.c -->
# sources/distributed-fs/beegfs/client_module/source/app/log/Logger.c

## Research
`Logger.c` implements the BeeGFS client kernel logger. It initializes per-topic log levels from `Config`, allocates two fixed-size buffers for formatted message and context, tracks optional client ID, and serializes output with `outputMutex`. Important APIs include formatted and topic-formatted log functions, `Logger_logTopFormattedWithEntryID`, error helpers, topic string conversion, and log-level getters.

Control flow filters messages by topic level before formatting, then `__Logger_logTopFormattedGranted` checks a per-thread recursion guard, locks output, formats with `vsnprintf`, prefixes context with client ID when present, and emits through `printk_fhgfs`. The entry-ID helper takes an inode `EntryInfo` read lock, prefixes the message with the entry ID, and delegates to the va-list path. State is in heap buffers, mutexes, topic-level array, current output PID, and copied client ID; nothing is persisted. Dependencies include `Config`, `App`, `FhgfsOpsSuper`, `FhgfsInode`, `EntryInfo`, mutex wrappers, and kernel `current`. Risks include dropped recursive logs, fixed 1000-byte truncation, allocation failure in entry-ID prefixing, and deadlock if entry-ID logging is used while holding incompatible inode locks. Test signals are per-topic filtering, recursion suppression, client ID context output, entry-ID formatting under locks, and clean uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/log/Logger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/log/Logger.h -->
# sources/distributed-fs/beegfs/client_module/source/app/log/Logger.h

## Research
`Logger.h` defines the logger API, log levels, log topics, debug macros, and `struct Logger`. The public surface includes lifecycle, printf-checked formatted logging, va-list variants, error shortcuts, topic-level accessors, and topic string parsing. Inline helpers handle copied client ID, bulk topic-level updates, per-topic updates, and simple string logging wrappers.

Control flow in the header is mostly compile-time: `LOG_DEBUG_MESSAGES` either expands debug log macros to real calls or removes them entirely. Runtime inline wrappers normalize string-only calls into formatted calls. State is the `LogTopicLevels` array, `App` pointer, output and recursion mutexes, current-output PID, two buffers, and optional client ID. Dependencies include `Config`, `App`, `Common`, `StringTk`, `Time`, and `Mutex`. Integration points are all client modules that need kernel logging and procfs code that reads/writes topic levels. Risks include adding a new topic without updating `Logger_getLogTopicStr` and procfs handlers, calling logging during teardown after levels/buffers are disabled, and relying on macros that compile away debug side effects. Test signals are compiler format-attribute warnings, topic-string conversion tests, and runtime checks that disabling levels suppresses output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/app/log/Logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/Common.h -->
# sources/distributed-fs/beegfs/client_module/source/common/Common.h

## Research
`Common.h` is the kernel-client portability and utility foundation. It pulls in Linux kernel headers, BeeGFS type definitions, socket IP types, and OS compatibility helpers; defines default messaging timeouts; provides min/max and safe free/destructor macros; centralizes `printk_fhgfs` logging prefixes; and abstracts kernel-version differences such as `set_fs`, wait-queue names, timestamps, uid/gid wrappers, file-lock field layout, RDMA availability, and fallthrough attributes.

The file also defines current user/group helpers, list and rbtree cleanup macros, generic rbtree function generators, and `BEEGFS_DATA_VERSION`, which feeds the network protocol prefix. Control flow is mainly preprocessor-gated by kernel feature macros and build flags. State is not owned, but macros mutate caller pointers and containers. Dependencies include Linux module/sched/slab/uaccess/rbtree APIs, `FhgfsTypes.h`, `IpAddress.h`, and `OsDeps.h`. Integration is global across the client module. Risks are macro side effects, kernel-version drift, unsafe assumptions in pointer cleanup, generated rbtree functions comparing keys correctly, and protocol compatibility if `BEEGFS_DATA_VERSION` changes. Test signals are successful builds across supported kernels, warnings-free compile with feature detection, and runtime logging/user-ID behavior under different credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/Common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/FhgfsTypes.h -->
# sources/distributed-fs/beegfs/client_module/source/common/FhgfsTypes.h

## Research
`FhgfsTypes.h` defines a compact BeeGFS stat structure used by the client module. `struct fhgfs_stat` carries mode, link count, uid, gid, logical size, block count, access/modification/change times as BeeGFS `Time`, and `metaVersion`. The type is a bridge between remote metadata responses and Linux inode/stat update code.

There is no executable control flow and no persistent state. Dependencies are Linux `in.h`, `time.h`, and `common/toolkit/Time.h`. Integration points are metadata/stat message handling and filesystem inode attribute conversion, where callers need a BeeGFS-specific stat payload before translating into kernel `struct kstat` or inode fields. Risks are layout and semantic drift from server/user-space common definitions, especially `ctime` meaning attribute change time and not creation time, integer width mismatches for size/block fields, and time conversion precision. Test signals are stat/getattr paths returning expected ownership, mode, size, timestamps, and metadata version after remote operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/FhgfsTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/Types.c -->
# sources/distributed-fs/beegfs/client_module/source/common/Types.c

## Research
`Types.c` instantiates serialization and list-serialization functions for shared mapping structures declared in `Types.h`. It uses `SERDES_DEFINE_SERIALIZERS_SIMPLE` and `SERDES_DEFINE_LIST_SERIALIZERS` for `TargetMapping`, `TargetPoolMapping`, `BuddyGroupMapping`, and `TargetStateMapping`, wiring each field to `Serialization`, `NumNodeID`, `StoragePoolId`, or enum serializers.

Control flow is generated by macros from the serialization toolkit: serializers walk fields in declared wire order, and list serializers allocate/list-link elements during deserialization. State is caller-owned lists/rbtree nodes; this file owns no persistent state. Dependencies are `Types.h`, `Serialization.h`, `NumNodeID`, and `StoragePoolId`. Integration points are target mapper, storage pool mapper, buddy group mapper, and node-state update messages such as target mapping and states-and-buddy-groups responses. Risks are wire-order compatibility with user-space/server code, correct cleanup of allocated list entries by message release functions, and keeping enum serializers in sync with common library definitions. Test signals are successful deserialization of management responses, correct target-to-node mappings, and leak-free `NETMESSAGE_FREE` paths for messages containing these lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/Types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/Types.h -->
# sources/distributed-fs/beegfs/client_module/source/common/Types.h

## Research
`Types.h` declares shared target, pool, buddy-group, and state mapping types for the client module. `TargetMapping` maps a storage target ID to a `NumNodeID` and uses a union so the same object can live either in a target mapper rbtree or a serialized list. `TargetPoolMapping`, `BuddyGroupMapping`, and `TargetStateMapping` are list-oriented wire structures. The header also defines `TargetReachabilityState`, `TargetConsistencyState`, `CombinedTargetState`, and `TargetStateInfo`.

Control flow is macro-declared serialization via `SERDES_DECLARE_*` and enum serializer definitions over `uint8_t`. State is owned by containers outside this header; private list/rbtree members encode container membership expectations. Dependencies include `StoragePoolId.h` and `Serialization.h`. Integration points are node/target discovery, mirror buddy group setup, target state stores, and management response messages. Risks include using the wrong private member for a container, enum value drift from the common library, and accidental copying of objects already linked into a list/tree. Test signals are target mapper updates from `GetTargetMappingsRespMsg`, target-state refreshes, and buddy group list deserialization with cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/Types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessage.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessage.c

## Research
`NetMessage.c` implements non-inline behavior for the common BeeGFS wire-message base. `__NetMessage_deserializeHeader` validates the fixed 40-byte header, exact message length, `NETMSG_PREFIX`, known header flag bits, and then extracts type, target ID, user ID, and retry sequence fields. `__NetMessage_serializeHeader` emits the same fields in wire order. Default virtuals reject incoming processing and report no supported feature flags; dummy serialize/deserialize functions log stack traces if called.

Control flow is defensive: invalid header input marks the type `NETMSGTYPE_Invalid` early so dispatch can reject it. State is written into the caller-provided `NetMessageHeader`; no memory is allocated. Dependencies are `NetMessage.h`, serialization helpers, and `printk_fhgfs`. Integration points are every message type and the receive dispatcher. Risks include strict length equality rejecting framed buffers with extra bytes, protocol prefix/data-version drift, unsupported flag handling, and dummy ops hiding missing implementation until runtime. Test signals include malformed-header rejection, valid round-trip serialization, feature-flag compatibility checks, and dispatch behavior for invalid message types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessage.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessage.h

## Research
`NetMessage.h` defines the abstract base class for BeeGFS client network messages. It sets protocol constants such as `NETMSG_PREFIX`, `NETMSG_HEADER_LENGTH`, max sizes, default user ID, header flags, `NetMessageHeader`, `NetMessageOps`, and `NetMessage`. Inline APIs initialize messages, allocate/free via `NETMESSAGE_CONSTRUCT` and `NETMESSAGE_FREE`, extract length from receive buffers, serialize full messages, check feature compatibility, get/set header fields, and lazily compute message length by serializing into a counting context.

Control flow is virtual through the ops table: derived messages provide payload serialization, payload deserialization, optional processing, supported flags, release cleanup, and sequence-number support. State includes header fields, ops pointer, cached message length, target/user IDs, and retry sequence numbers. Dependencies include network socket/NIC types, `Serialization.h`, `Common.h`, and `NetMessageTypes.h`. Integration points span all request/response types and messaging toolkit request paths. Risks are stale cached length if payload fields change after first length calculation, missing release hooks for deserialized lists, user-ID default behavior, and using incompatible feature flags. Test signals are message-specific round trips, length-bound checks, `NETMESSAGE_FREE` cleanup, and retry/sequence behavior for messages marking `supportsSequenceNumbers`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessageTypes.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessageTypes.h

## Research
`NetMessageTypes.h` is the numeric BeeGFS protocol message registry for the client module. It defines constants for invalid, node-management, storage, session, control, monitoring, and fsck message IDs, with comments requiring synchronization with the user-space/common library. The file also conditionally includes NVFS RDMA message IDs when `BEEGFS_NVFS` is enabled.

There is no runtime control flow or state; the header is a compile-time integration contract used by every concrete message initializer and by receive-side dispatch. Dependencies are minimal, but semantic dependency on server and common library definitions is strong. Risks are severe compatibility failures if IDs are reused, renumbered, omitted, or conditionally compiled inconsistently. Because the protocol prefix includes `BEEGFS_DATA_VERSION` but message numbers remain separate, both must be considered for interoperability. Test signals are successful client-server handshakes, registration, metadata/storage requests, and dispatch tests that map wire IDs to the expected message class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/NetMessageTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.c

## Research
`SimpleInt64Msg.c` implements payload ops for messages that carry one signed 64-bit integer. `SimpleInt64Msg_Ops` uses normal serialization/deserialization functions, default incoming processing, and default feature-mask handling. `SimpleInt64Msg_serializePayload` writes `value` with `Serialization_serializeInt64`; `SimpleInt64Msg_deserializePayload` reads it with `Serialization_deserializeInt64`.

Control flow is a single field round trip and returns the serializer boolean on input. State is just the inherited `NetMessage` plus `value`, owned by the containing concrete message. Dependencies are `SimpleInt64Msg.h`, `NetMessage`, and `Serialization`. Integration points include 64-bit-valued responses such as fsync-local-file results and auth hash transport variants. Risks are signedness expectations when callers use uint64-style values through this signed container and lack of range-level validation. Test signals are payload-length correctness, negative and large-value round trips, and derived response classes reading expected `FhgfsOpsErr`/byte-count semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.h

## Research
`SimpleInt64Msg.h` declares the reusable one-int64 message wrapper. `struct SimpleInt64Msg` embeds `NetMessage` and an `int64_t value`; inline initializers set the message type and optionally the value, and `SimpleInt64Msg_getValue` returns the stored scalar. The ops are implemented in the `.c` file.

Control flow is construction-only in this header. State is non-owning and fixed-size, with no heap allocations or persistence. Dependencies are `NetMessage.h` and the shared ops object. Integration points are concrete message typedef wrappers that need a simple 64-bit result or token without custom payload code. Risks are treating the wrapper as owning external data, using it for unsigned protocol values without clear conversion, or changing message type after length caching. Test signals are derived message initializers setting the right `NETMSGTYPE_*`, and deserialization populating `value` for response handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleInt64Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.c

## Research
`SimpleIntMsg.c` implements the shared payload ops for one signed integer. The ops table points to `SimpleIntMsg_serializePayload`, `SimpleIntMsg_deserializePayload`, default incoming processing, and default feature flags. Serialization writes `value` as an int; deserialization reads it and returns success/failure from the serialization layer.

Control flow is intentionally minimal and relies on the base `NetMessage` for header handling. State is one scalar in the message instance and is not persisted. Dependencies are `SimpleIntMsg.h` and `Serialization`. Integration points include many control and response wrappers: node queries by node type, remove-node responses, lock responses, close-file responses, and generic integer result codes. Risks are mapping integer values to different semantic enums without local validation and accidental use for wire fields that require unsigned width. Test signals are round-trip payload tests and derived response handling that converts integers to `FhgfsOpsErr` or node-type values correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.h

## Research
`SimpleIntMsg.h` declares the reusable one-int message. `struct SimpleIntMsg` embeds `NetMessage` and an `int value`; inline constructors initialize the base with a caller-supplied type and optional value, and `SimpleIntMsg_getValue` returns it. The header enables many concrete messages to be defined as thin wrappers without custom serialization code.

Control flow is limited to inline initialization and access. State is fixed-size and owned by the message object. Dependencies are `NetMessage.h` and the external `SimpleIntMsg_Ops`. Integration points include simple request/response messages where the message type supplies all context and the integer encodes a node type, status code, or result. Risks are semantic ambiguity of the integer payload, lack of range checking, and missing compile-time distinction between enum domains. Test signals are correct concrete `NETMSGTYPE_*` initialization and deserialization of expected integer result values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.c

## Research
`SimpleIntStringMsg.c` implements payload ops for a message carrying an integer plus a string. Serialization writes `intValue` followed by a length-prefixed string; deserialization reads the integer and then a borrowed string pointer/length from the deserialize buffer. The ops table uses default incoming processing and feature-mask handling.

Control flow short-circuits on either field failing to deserialize. State is an integer plus `strValue` pointer and length; deserialized strings point into the receive buffer and init-from-value strings are caller-owned references. Dependencies are `SimpleIntStringMsg.h` and `Serialization`. Integration points include `GenericResponseMsg`, where the int is a control code and the string is human-readable context. Risks are lifetime of non-owned strings, assuming NUL termination or mutability for deserialized strings, and using the type where the int and string need independent validation. Test signals include generic-response parsing, malformed short string rejection, and correct message length calculation with string payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.h

## Research
`SimpleIntStringMsg.h` declares a reusable `NetMessage` wrapper containing `intValue`, `strValue`, and `strValueLen`. Inline constructors initialize the base type and optionally bind a caller-provided string reference, measuring length with `strlen`. Accessors return the integer and string pointer.

Control flow is construction/access only. State is partly non-owning: the string must outlive serialization, and deserialized strings are receive-buffer slices. Dependencies are `NetMessage.h` and the ops object from the `.c` file. Integration points are generic response/control messages that need a numeric code and explanatory string without custom payload code. Risks include dangling string pointers, not preserving embedded NULs when initialized from C strings, and confusing buffer-slice lifetime after request handling. Test signals are response handlers reading both fields before freeing receive buffers and serializers producing the expected int-then-string wire order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleIntStringMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.c

## Research
`SimpleMsg.c` implements payload ops for header-only messages. `SimpleMsg_serializePayload` intentionally emits nothing, while `SimpleMsg_deserializePayload` always returns true because the message type and common header carry all information. The ops table delegates incoming processing and feature flags to `NetMessage` defaults unless a derived wrapper overrides the ops pointer.

Control flow is no-op payload handling. State is only the inherited `NetMessage` header. Dependencies are `SimpleMsg.h` and base message functions. Integration points include heartbeat requests, target mapping requests, and other protocol requests where the `NETMSGTYPE_*` alone identifies the action. Risks are accidentally choosing `SimpleMsg` for a wire type that later gained payload fields, and accepting extra payload bytes because no message-specific content is consumed. Test signals are header-only message length equal to `NETMSG_HEADER_LENGTH` and dispatch paths that override processing where needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.h

## Research
`SimpleMsg.h` declares the minimal header-only message wrapper. `struct SimpleMsg` embeds `NetMessage`, and `SimpleMsg_init` initializes it with a caller-specified message type and `SimpleMsg_Ops`. It is used when all semantics come from the message type and common header fields.

Control flow is only inline initialization; serialization/deserialization behavior is in the `.c` file. State is fixed-size and has no owned payload resources. Dependencies are `NetMessage.h`. Integration points include request wrappers that do not require payload data, and receive-side messages that override `ops` after initializing as a simple message. Risks are missing an ops override for messages with custom `processIncoming`, and future protocol changes adding payload without updating derived wrappers. Test signals are message length checks and successful server handling of header-only requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleStringMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleStringMsg.c

## Research
`SimpleStringMsg.c` implements payload ops for messages that carry one string. Serialization writes a length-prefixed string from `valueLen` and `value`; deserialization stores the received length and a pointer to the buffer slice. The ops table otherwise uses the base default incoming behavior and feature-mask support.

Control flow is direct serializer return handling, with no extra validation of string content. State is a non-owning string pointer plus length in the message instance. Dependencies are `SimpleStringMsg.h` and serialization helpers. Integration points include acknowledgement messages carrying ack IDs or short text values. Risks are string lifetime and NUL-termination assumptions, using `strlen`-based initialization for binary data, and accepting empty strings where a concrete protocol might require a non-empty value. Test signals are ack-message round trips, malformed length rejection, and correct message length for empty and non-empty strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleStringMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleStringMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleStringMsg.h

## Research
`SimpleStringMsg.h` declares a reusable single-string `NetMessage` wrapper. `struct SimpleStringMsg` embeds the base message plus `value` and `valueLen`; inline constructors initialize with a message type and optionally bind a caller-provided C string reference. `SimpleStringMsg_getValue` exposes the pointer.

Control flow is construction and access only. State is non-owning and fixed-size, with no release hook. Dependencies are `NetMessage.h` and the external ops object. Integration points are concrete control messages such as `AckMsgEx` and any simple string request/response types. Risks include dangling references, deserialized buffer-slice lifetime, and no validation that the string matches a semantic format such as an ack ID. Test signals are derived type initialization to the correct message ID and successful deserialization before receive-buffer reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleStringMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleUInt16Msg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleUInt16Msg.c

## Research
`SimpleUInt16Msg.c` implements payload ops for a single unsigned 16-bit integer. The serializer writes `value` with `Serialization_serializeUShort`, and the deserializer reads it with `Serialization_deserializeUShort`. The ops table uses default base processing and feature-mask behavior.

Control flow is a one-field round trip and returns the deserialization success status. State is one scalar in the object and is not persisted. Dependencies are `SimpleUInt16Msg.h` and serialization helpers. Integration points are protocol messages whose payload is a target ID, group ID, port, or other compact 16-bit value. Risks are insufficient semantic validation of zero/reserved IDs and accidental truncation if callers pass wider values before initialization. Test signals are derived messages preserving `uint16_t` values over serialization and rejecting short buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleUInt16Msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleUInt16Msg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleUInt16Msg.h

## Research
`SimpleUInt16Msg.h` declares the reusable single-`uint16_t` message wrapper. It embeds `NetMessage`, stores `value`, initializes with a caller-specified message type and shared ops, and provides `SimpleUInt16Msg_getValue`. The type is a compact building block for protocol wrappers that only need a 16-bit value.

Control flow is inline initialization and access. State is fixed-size and has no owned resources. Dependencies are `NetMessage.h` and `SimpleUInt16Msg_Ops`. Integration points are small request/response message definitions that map wire semantics onto a target, group, or port-sized number. Risks are domain ambiguity and lack of validation around zero or out-of-range conversions before assignment. Test signals are correct message type setup and round-trip serialization of boundary values 0 and 65535 where valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/SimpleUInt16Msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/AckMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/AckMsgEx.h

## Research
`AckMsgEx.h` defines the acknowledgement control message as a thin `SimpleStringMsg` wrapper with type `NETMSGTYPE_Ack`. It provides initializers for empty/deserialization use and for a specific string value, plus `AckMsgEx_getValue` to retrieve the ack ID or text.

Control flow is entirely inline delegation to `SimpleStringMsg`. State is the inherited simple-string state, so the string is a non-owned reference for outgoing messages and a receive-buffer slice for incoming messages. Dependencies are `SimpleStringMsg.h` and `NetMessageTypes.h` through the simple wrapper. Integration points are `MsgHelperAck`, lock grant acknowledgements, heartbeat/remove/map/refresh request ack paths, and request retry synchronization. Risks are empty ack IDs being treated as no-op by helper code, string lifetime, and no local validation that the ack corresponds to a registered wait. Test signals are ack request/response paths waking waiters and not sending responses when no ack ID is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/AckMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/AuthenticateChannelMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/AuthenticateChannelMsg.h

## Research
`AuthenticateChannelMsg.h` defines the channel-authentication message as a `SimpleInt64Msg` wrapper using `NETMSGTYPE_AuthenticateChannel`. The outgoing value is the connection authentication hash produced by `Config` from the configured auth file.

Control flow is inline initialization only: empty init prepares deserialization/receive structure, and init-from-value stores the hash. State is the inherited 64-bit scalar, with no owned resources or persistence. Dependencies are `SimpleInt64Msg.h` and protocol message IDs. Integration points are connection setup and authentication negotiation, tied to `connAuthHash` and `connDisableAuthentication` behavior. Risks include representing a `uint64_t` hash through the signed int64 wrapper, mismatched auth-file hashing between peers, and treating zero as both disabled and a possible scalar unless higher layers enforce semantics. Test signals are successful authenticated connection setup, rejection on mismatched hashes, and correct behavior when authentication is explicitly disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/AuthenticateChannelMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/GenericResponseMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/GenericResponseMsg.h

## Research
`GenericResponseMsg.h` defines a generic internal control response as a `SimpleIntStringMsg` with message type `NETMSGTYPE_GenericResponse`. It declares `GenericRespMsgCode` values for retry advice, indirect communication errors, and new sequence-number base negotiation, and accessors for the control code and human-readable log string.

Control flow is consumed by messaging request/response helpers rather than ordinary callers: requestors may receive this control message instead of the expected response, and messaging toolkit logic interprets it internally. State is inherited integer-plus-string payload; no resources are owned. Dependencies are `SimpleIntStringMsg.h`. Integration points are retry handling, forwarding errors, and sequence-number recovery after client restart. Risks include callers accidentally seeing or mishandling generic responses, string lifetime, and adding control codes without updating request-handling logic. Test signals are request-response paths retrying on `TRYAGAIN`, surfacing indirect communication errors correctly, and sequence-number reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/GenericResponseMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.c

## Research
`PeerInfoMsg.c` implements serialization for a peer identity control message. The payload is an unsigned node type followed by a serialized `NumNodeID`. Deserialization reads the type into a temporary unsigned and assigns it to the `NodeType` field after reading the numeric ID.

Control flow is linear field serialization/deserialization with combined boolean success on input. State is `PeerInfoMsg.type` and `.id`; no heap state or persistence exists. Dependencies are `PeerInfoMsg.h`, `Serialization`, and `NumNodeID` serializers. Integration points are connection/channel metadata exchange so a peer can tell the client which node type and numeric ID it represents. Risks are weak validation of the node type enum and type-width assumptions between `unsigned` and `NodeType`. Test signals are peer-info round trips and connection setup logic routing metadata/storage/management peers correctly after reading this message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.h

## Research
`PeerInfoMsg.h` declares a concrete `NetMessage` carrying peer node type and `NumNodeID`. `PeerInfoMsg_init` sets `NETMSGTYPE_PeerInfo`, installs `PeerInfoMsg_Ops`, and stores the caller-supplied identity fields.

Control flow is inline construction and the `.c` payload ops. State is fixed-size and owned by the message instance. Dependencies include `NetMessage.h` and `Node.h` for `NodeType` and `NumNodeID`. Integration points are connection establishment and peer classification for node connection pools. Risks are missing validation for zero node IDs or invalid node types in the header itself, and keeping the wire order synchronized with server/common implementations. Test signals are successful peer-info exchange and rejection or safe handling of invalid peer identities in higher layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/SetChannelDirectMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/SetChannelDirectMsg.h

## Research
`SetChannelDirectMsg.h` defines `NETMSGTYPE_SetChannelDirect` as a thin `SimpleIntMsg` wrapper. It can be initialized empty or from an integer value, which higher layers use to request or signal direct-channel behavior.

Control flow is inline delegation to `SimpleIntMsg` constructors. State is a single integer payload with no owned memory. Dependencies are `SimpleIntMsg.h`. Integration points are channel setup/control paths that need a compact value-bearing message without custom payload code. Risks are the integer value being semantically opaque in this file, so invalid modes must be checked by the receiver. Test signals are channel setup messages carrying expected values and default `NetMessage_processIncoming` preventing accidental unhandled receive-side processing in the client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/control/SetChannelDirectMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.c

## Research
`GetHostByNameMsg.c` implements payload serialization for helper-daemon hostname lookup requests. The payload is a single length-prefixed hostname string stored in `hostname` and `hostnameLen`. Deserialization reads the same string from the receive buffer.

Control flow is direct: serialize the string, deserialize the string, return false on malformed input. State is a non-owning string pointer/length; deserialized state points into the receive buffer. Dependencies include `App.h`, `SocketTk.h`, `GetHostByNameMsg.h`, and serialization helpers, though the app/socket includes are not used in the current functions. Integration points are helper daemon DNS/name-resolution flows, useful because kernel code should avoid ordinary user-space resolver behavior. Risks include string lifetime, no hostname syntax validation, and possible stale includes. Test signals are helperd request serialization, malformed string rejection, and hostname-to-address response matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.h

## Research
`GetHostByNameMsg.h` declares the helper-daemon hostname lookup request. `struct GetHostByNameMsg` embeds `NetMessage` and stores `hostnameLen` plus non-owned `hostname`. Inline init sets `NETMSGTYPE_GetHostByName`, while `initFromHostname` binds a caller-provided C string and computes its length.

Control flow is construction and later payload ops in the `.c` file. State is non-owning and not persisted. Dependencies are `NetMessage.h`. Integration points are client code that asks a helper process to resolve a management or peer hostname into an address string. Risks are dangling hostname pointers, inability to carry embedded NULs, and no local validation for empty names. Test signals are correct message type and length when resolving configured hostnames and safe failure for malformed receive buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameRespMsg.c

## Research
`GetHostByNameRespMsg.c` implements receive-only parsing for helper-daemon hostname lookup responses. Its ops use `_NetMessage_serializeDummy` because the client only deserializes this response type. The payload parser reads a single address string into `hostAddrLen` and `hostAddr`.

Control flow returns false if the string cannot be deserialized. State is a receive-buffer pointer/length with no owned allocation. Dependencies include `GetHostByNameRespMsg.h` and serialization helpers. Integration points are helperd DNS responses that feed socket/address setup logic. Risks are dummy serialization being called accidentally, address string lifetime after receive-buffer reuse, and lack of address-format validation in the message class. Test signals are successful resolution of configured hostnames, malformed response rejection, and correct higher-layer parsing of returned IPv4/IPv6 string forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameRespMsg.h

## Research
`GetHostByNameRespMsg.h` declares the receive-side response for helper daemon name lookup. It embeds `NetMessage`, stores a length-prefixed `hostAddr` string from deserialization, initializes with `NETMSGTYPE_GetHostByNameResp`, and provides `GetHostByNameRespMsg_getHostAddr`.

Control flow is init plus deserialization in the `.c` file. State is non-owning and tied to the receive buffer lifetime. Dependencies are `NetMessage.h`. Integration points are name-resolution request paths that consume a returned address string. Risks include returning a pointer that must be consumed before buffer disposal, no representation of detailed resolver errors beyond string content, and dummy serialization if used incorrectly. Test signals are helperd lookup round trips and higher-layer validation that the returned address can be parsed by socket utilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/GetHostByNameRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.c

## Research
`LogMsg.c` implements helper-daemon log-entry message payload handling. The payload wire order is log level, thread ID, thread name string, context string, and log message string. Serialization writes all fields; deserialization reads them in order and fails on the first malformed field.

Control flow is sequential and field-oriented. State includes integer fields plus non-owned string pointers/lengths; deserialized strings are receive-buffer slices. Dependencies include `LogMsg.h`, `Node.h`, `ListTk`, `NodeStoreEx`, and socket/app headers, although the active functions use mainly serialization. Integration points are legacy/helperd log forwarding paths where kernel/client logs are transported to a helper process. Risks are fixed string lifetime, large log truncation before this message type, no local validation of log level range, and stale includes. Test signals are helper log request/response behavior, round-trip preservation of thread/context/message fields, and malformed string rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.h

## Research
`LogMsg.h` declares a helper-daemon log entry message. `struct LogMsg` embeds `NetMessage` and stores log level, thread ID, and length-prefixed thread name, context, and message pointers. `LogMsg_initFromEntry` binds caller-owned string references and computes lengths with `strlen`.

Control flow is inline construction, with payload ops in the `.c` file. State is non-owning and must remain valid during serialization; no release hook is needed. Dependencies are `NetMessage.h`. Integration points are code that forwards log records to helperd rather than printing directly. Risks include dangling references, inability to carry embedded NULs, no range checks on level/thread ID, and message-length growth against `NETMSG_MAX_MSG_SIZE`. Test signals are correct serialization of representative log entries and response handling via `LogRespMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogRespMsg.h

## Research
`LogRespMsg.h` defines the helper-daemon log response as a `SimpleIntMsg` wrapper with type `NETMSGTYPE_LogResp`. It provides an initializer and `LogRespMsg_getValue` to retrieve the integer response/result value.

Control flow is inline delegation to the simple integer message implementation. State is one integer payload and inherited header fields. Dependencies are `SimpleIntMsg.h`. Integration points are helperd log forwarding request paths that need an acknowledgement or result code after sending a log entry. Risks are semantic ambiguity of the integer result and the default simple ops not validating higher-level success values. Test signals are log-forwarding tests that receive `NETMSGTYPE_LogResp` and interpret the integer according to helperd expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/helperd/LogRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h

## Research
`GetMirrorBuddyGroupsMsg.h` declares a request for mirror buddy group mappings. It is a `SimpleIntMsg` wrapper initialized with `NETMSGTYPE_GetMirrorBuddyGroups`, and the integer payload is the requested `NodeType`.

Control flow is a single inline constructor that stores the node type. State is inherited `SimpleIntMsg` state with no resources. Dependencies are `SimpleIntMsg.h` and `NodeType` visibility from included common headers. Integration points are management-node queries used to populate metadata or storage buddy group mappers. Risks are invalid node type values and no local validation of whether the requested group class supports mirroring. Test signals are successful management responses and correct mapper updates for metadata versus storage groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesMsg.h

## Research
`GetNodesMsg.h` declares the request used to ask management for nodes of a given type. It wraps `SimpleIntMsg` with `NETMSGTYPE_GetNodes`; `GetNodesMsg_initFromValue` stores a `NODETYPE_*` integer.

Control flow is inline initialization only. State is a single integer payload. Dependencies are `SimpleIntMsg.h`. Integration points are node discovery during startup, heartbeat handling, and syncer refreshes that need metadata, storage, management, or client node lists. Risks are invalid node-type values and relying on callers to choose the correct response parser. Test signals are successful `GetNodesRespMsg` parsing, root metadata owner discovery, and node-store population after management queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.c

## Research
`GetNodesRespMsg.c` implements receive-only deserialization for node-list responses. Its ops install dummy serialization and parse a preprocessed raw node list, root metadata numeric ID, and `rootIsBuddyMirrored` boolean.

Control flow is sequential and stops on failed node-list, `NumNodeID`, or boolean parsing. State includes `rootNumID`, `rootIsBuddyMirrored`, and a `RawList` slice that is later materialized by `GetNodesRespMsg_parseNodeList`. Dependencies are `GetNodesRespMsg.h`, node-list serialization helpers, and `NumNodeID`. Integration points are management-node discovery and root-owner initialization. Risks include receive-buffer lifetime for `rawNodeList`, no release hook because parsing into `NodeList` is caller-managed, and dummy serialization misuse. Test signals are management responses with multiple nodes, root buddy-mirror flag propagation, and malformed list rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.h

## Research
`GetNodesRespMsg.h` declares the receive-side node-list response. It embeds `NetMessage`, stores root owner metadata and a raw serialized node list, initializes with `NETMSGTYPE_GetNodesResp`, and provides `GetNodesRespMsg_parseNodeList` to convert the raw list into a `NodeList` using app context.

Control flow is init, deserialization, then explicit caller-triggered parse. State in `rawNodeList` references the receive buffer until parsed; `rootNumID` defaults to zero. Dependencies include `NetMessage.h` and `NodeList.h`. Integration points are node stores, root owner setup, and client startup/sync paths. Risks are forgetting to call `parseNodeList`, using raw data after buffer lifetime ends, and missing serialization support. Test signals are node discovery populating stores and root owner fields matching server responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetNodesRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.c

## Research
`GetStatesAndBuddyGroupsMsg.c` implements the request payload for combined target states and buddy groups. It serializes `nodeType` as an int and `requestedByClientID` as a `NumNodeID`, and deserializes the same fields.

Control flow is linear, with boolean chaining on deserialize. State is fixed-size: requested node type and client numeric ID. Dependencies are `GetStatesAndBuddyGroupsMsg.h`, serialization helpers, and `NumNodeID`. Integration points are management queries that return both mirror group membership and target state information in one response, typically used by client syncers. Risks are casting `NodeType` through `int32_t*` during deserialization, invalid node type values, and relying on server/client wire-order agreement. Test signals are request construction with local client ID and correct response matching through `GetStatesAndBuddyGroupsRespMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h

## Research
`GetStatesAndBuddyGroupsMsg.h` declares a concrete `NetMessage` for requesting target states and buddy group mappings. The structure stores `NodeType nodeType` and `NumNodeID requestedByClientID`, and the inline initializer sets `NETMSGTYPE_GetStatesAndBuddyGroups` with the corresponding ops.

Control flow is initialization plus serializer/deserializer in the `.c` file. State is fixed-size and non-owning. Dependencies include `NetMessage.h`, `NumNodeID.h`, and `Node.h`. Integration points are internode syncer and management communication code that refreshes target states and mirror buddy groups. Risks are invalid enum values and synchronization requirements with response list types in `Types.h`. Test signals are management query success for metadata/storage states and correct local client ID propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.c

## Research
`GetStatesAndBuddyGroupsRespMsg.c` implements receive-only deserialization and cleanup for combined buddy group and target state responses. The release hook frees deserialized `BuddyGroupMapping` and `TargetStateMapping` list elements with `BEEGFS_KFREE_LIST`. Payload deserialization reads a buddy group mapping list followed by a target state mapping list.

Control flow is list-deserialize then list-deserialize; failure leaves any already allocated list entries to be cleaned by message release. State is two Linux list heads owned by the message after deserialization. Dependencies are `GetStatesAndBuddyGroupsRespMsg.h`, `Types.h` list serializers, and `Common.h` cleanup macros. Integration points are mirror buddy group mapper and target state store updates. Risks are memory leaks if the release hook is bypassed, partial-deserialization cleanup, and wire-order drift. Test signals are `NETMESSAGE_FREE` releasing both lists, correct mapper/state-store updates, and malformed list failure without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h

## Research
`GetStatesAndBuddyGroupsRespMsg.h` declares the receive-side response carrying two maps: buddy group ID to primary/secondary target IDs, and target ID to reachability/consistency state. It embeds `NetMessage` and owns two `struct list_head` containers for `BuddyGroupMapping` and `TargetStateMapping`.

Control flow initializes both lists and relies on the `.c` ops for deserialization and release. State is owned list elements allocated by serializers. Dependencies include `NetMessage.h`, `Common.h`, and `Types.h`. Integration points are management-sync logic, `MirrorBuddyGroupMapper`, and `TargetStateStore`. Risks are using the lists after message free, forgetting release, and keeping the structure wire-compatible with server common code. Test signals are list contents matching management state and cleanup under kmemleak or fault-injection tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsMsg.h

## Research
`GetTargetMappingsMsg.h` declares a header-only request for target-to-node mappings. It wraps `SimpleMsg` and initializes `NETMSGTYPE_GetTargetMappings`.

Control flow is a single inline initializer. State is only the inherited message header. Dependencies are `SimpleMsg.h`. Integration points are management queries used to populate the client `TargetMapper` before routing storage IO. Risks are protocol evolution adding payload fields without updating this wrapper, and caller confusion with other target-state requests. Test signals are management response pairing with `GetTargetMappingsRespMsg` and correct target mapper population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.c

## Research
`GetTargetMappingsRespMsg.c` implements receive-only deserialization and cleanup for target mapping responses. `GetTargetMappingsRespMsg_deserializePayload` reads a `TargetMappingList` into the message-owned `mappings` list, and the release hook frees every `TargetMapping` list element.

Control flow is simple but ownership-sensitive: successful or partial deserialization must be followed by `NETMESSAGE_FREE` to run the release hook. State is a list of `TargetMapping` objects allocated by the list serializer. Dependencies are `GetTargetMappingsRespMsg.h`, `Types.h` serializers, `TargetMapper.h`, and `Common.h` cleanup macros. Integration points are target mapper refresh and storage IO target routing. Risks are leaks without release, using list entries after message free, and wire compatibility of `TargetMapping`. Test signals are target ID mapping updates, malformed list rejection, and cleanup verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.h

## Research
`GetTargetMappingsRespMsg.h` declares a receive-only target mapping response. It embeds `NetMessage`, owns a `struct list_head mappings` containing `TargetMapping` elements, initializes the list, and relies on the `.c` release hook for cleanup.

Control flow is initialization, deserialization, caller iteration, and message free. State is list-owned deserialized mapping elements. Dependencies include `NetMessage.h` and `Common.h`; the concrete mapping type comes from `Types.h` through serializers. Integration points are the `TargetMapper` that maps storage target IDs to node numeric IDs. Risks are absent serialization support, lifetime mistakes around the list, and not handling duplicate target IDs in the consumer. Test signals are management mapping responses and correct downstream target selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.c

## Research
`HeartbeatMsgEx.c` implements heartbeat serialization, deserialization, and incoming processing. Payload fields include instance and NIC-list versions, node type, string node ID, aligned ack ID, node/root numeric IDs, root buddy-mirror flag, UDP/TCP ports, NIC list, and machine UUID. Incoming processing validates node numeric ID, selects the correct node store by type, parses NICs, constructs or updates a `Node`, sets local NIC capabilities on its connection pool, logs new nodes, applies root metadata owner information, and responds to ack requests.

Control flow has explicit rejection paths for zero numeric IDs and invalid node types, but still reaches ack handling. State changes are significant: node stores, connection pool NIC capabilities, and root owner may be updated. Dependencies include `App`, `Node`, `NodeStoreEx`, `NodeConnPool`, `ListTk`, `MsgHelperAck`, `Config`, socket formatting, and serialization. Risks include cleanup of `nicList`/`localNicList` on all paths, trusting heartbeat-provided node data, root-owner races, and handling allocation failure from `Node_construct`. Test signals are heartbeat receive/update tests, new-node log events, root owner setting from metadata heartbeats, ack behavior, and RDMA NIC capability propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.h

## Research
`HeartbeatMsgEx.h` declares the concrete heartbeat message. It stores node identity, type, numeric IDs, root information, versions, ports, ack ID, machine UUID, a non-owned outgoing NIC list, and a raw deserialized NIC list. Inline helpers initialize node-data heartbeats, parse NIC lists, get identity fields, and set/get ports.

Control flow is construction and accessor logic; complex receive behavior is in the `.c` file. State is mixed ownership: outgoing strings/NIC lists are caller-owned, deserialized strings/raw lists are receive-buffer backed. Dependencies are `NetMessage.h` and `NetworkInterfaceCard.h`. Integration points are heartbeat request responses, node discovery, datagram listener processing, and internode sync. Risks include lifetime of aliases/NIC lists during serialization, zero/undefined ports, root fields being meaningful only for metadata nodes, and typo-prone reserved version fields. Test signals are serialized heartbeat payload order, NIC list parse correctness, and node-store updates after receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.c

## Research
`HeartbeatRequestMsgEx.c` handles incoming heartbeat requests. The ops use `SimpleMsg` payload handling but override `processIncoming`. On receive, it gets config and local node data, clones the local NIC list and alias, builds a `HeartbeatMsgEx` for the client node, sets the client port from `Config`, serializes into the provided response buffer, and sends either through `DatagramListener_sendto_kernel` for datagrams or `Socket_sendto_kernel` for streams.

Control flow logs serialization/send errors but returns true after cleanup. State is temporary except for reading local node/config state. Dependencies include `App`, `Config`, `Node`, `DatagramListener`, `Socket`, `ListTk`, and `HeartbeatMsgEx`. Integration points are discovery/probing flows where other nodes ask the client to identify itself. Risks include response buffer sizing, cleanup of cloned NIC list, alias lifetime during serialization, and transport-specific send paths. Test signals are heartbeat request round trips over UDP/TCP, response payload matching local node identity, and cleanup under serialization failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.h

## Research
`HeartbeatRequestMsgEx.h` declares a header-only heartbeat request that overrides processing. It embeds `SimpleMsg`, initializes as `NETMSGTYPE_HeartbeatRequest`, then replaces the simple ops table with `HeartbeatRequestMsgEx_Ops` so incoming processing sends a heartbeat response.

Control flow is inline init plus receive behavior in the `.c` file. State is only inherited simple-message state. Dependencies are `SimpleMsg.h`. Integration points are datagram/stream listeners that dispatch heartbeat requests to produce `HeartbeatMsgEx` responses. Risks are forgetting the ops override, which would leave default no-op/false processing, and protocol changes adding request payload. Test signals are dispatch invoking `__HeartbeatRequestMsgEx_processIncoming` and response message type `NETMSGTYPE_Heartbeat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/HeartbeatRequestMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.c

## Research
`MapTargetsMsgEx.c` implements receive-only target mapping updates pushed to the client. Deserialization reads a `TargetPoolMappingList`, a node numeric ID, and an ack ID. Processing iterates the pool mappings and maps each target ID to the provided node ID in the app `TargetMapper`, logs new mappings in debug builds, and sends an ack response when requested. The release hook frees the deserialized pool mapping list.

Control flow is list parse, map update loop, ack response, and cleanup via `NETMESSAGE_FREE`. State changes are persistent in the client target mapper; pool IDs are deserialized but not used by this client-side mapping operation. Dependencies include `App`, `TargetMapper`, `Types.h` list serializers, `MsgHelperAck`, `SocketTk`, and `Common.h`. Risks are ignoring storage pool IDs, duplicate/remapped target behavior, release-hook requirements, and accepting mappings from untrusted/invalid node IDs. Test signals are management push updates changing target mapper contents and ack response behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.h

## Research
`MapTargetsMsgEx.h` declares the receive-only map-targets message. It embeds `NetMessage`, stores a `NumNodeID`, ack ID pointer/length, and a list of `TargetPoolMapping` entries. Initialization sets `NETMSGTYPE_MapTargets` and initializes the list head.

Control flow is init and accessor use; receive processing and release are in the `.c` file. State includes owned deserialized list entries and receive-buffer-backed ack string. Dependencies are `NetMessage.h`, `Common.h`, and `StoragePoolId.h`. Integration points are management-driven target mapping updates into the client `TargetMapper`. Risks are serialization intentionally unimplemented, list lifetime, and consumer assumptions that all mappings refer to the same node ID. Test signals are deserialization of multiple target mappings and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.c

## Research
`RefreshTargetStatesMsgEx.c` implements receive-only processing for a management request that forces target-state refresh. Deserialization reads a string ack ID. Processing obtains the app `InternodeSyncer`, sets its force-target-states-update flag, logs debug source information, and sends an ack response when requested.

Control flow is direct and always returns true after setting the syncer flag and attempting ack. State changes are persistent in the syncer scheduling/force flag, not in the message. Dependencies include `App`, `InternodeSyncer`, `MsgHelperAck`, `SocketTk`, and serialization helpers. Integration points are management notifications that target states changed and the client should refresh. Risks include ack ID lifetime, no validation of sender authority in this file, and relying on the syncer to coalesce/perform the actual update. Test signals are receiving this message causing the next syncer cycle to fetch target states and ack behavior with empty/non-empty IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.h

## Research
`RefreshTargetStatesMsgEx.h` declares the receive-only refresh-target-states message. It embeds `NetMessage`, stores an ack ID pointer/length, initializes with `NETMSGTYPE_RefreshTargetStates`, and exposes `RefreshTargetStatesMsgEx_getAckID`.

Control flow is init and accessor use; deserialization and processing are in the `.c` file. State is a receive-buffer-backed string with no owned resources. Dependencies are `NetMessage.h` and `Common.h`. Integration points are management-driven target state refresh notifications and `InternodeSyncer`. Risks are accidental serialization use, empty ack IDs, and no payload versioning beyond the message type. Test signals are deserialized ack IDs and forced syncer refresh after dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RefreshTargetStatesMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.c

## Research
`RegisterNodeMsg.c` implements outgoing serialization for client node registration. The payload includes instance version, NIC-list version, node ID string, NIC list, node type, node numeric ID, root numeric ID, root buddy-mirror flag, UDP/TCP ports, and machine UUID. Deserialization is deliberately dummy because the client sends this request.

Control flow is fixed wire-order serialization only. State is caller-provided identity/NIC fields from `RegisterNodeMsg.h`. Dependencies include `RegisterNodeMsg.h`, serialization helpers, `NumNodeID`, and NIC list serialization. Integration points are management registration during client startup, obtaining assigned numeric IDs and management gRPC port via `RegisterNodeRespMsg`. Risks are wire-order drift, non-owned pointer lifetimes, default zero fields that are "undefined" on the client but still serialized, and missing sequence/feature behavior. Test signals are successful registration with management, response numeric ID assignment, and server acceptance of serialized NIC list/ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.h

## Research
`RegisterNodeMsg.h` declares the outgoing node registration message. The struct embeds `NetMessage` and stores non-owned node ID, numeric ID, root info, node type, non-owned NIC list, UDP/TCP ports, version fields, and machine UUID. `RegisterNodeMsg_initFromNodeData` fills client-relevant fields, sets root info and TCP/machine UUID to client defaults, and initializes `NETMSGTYPE_RegisterNode`.

Control flow is construction followed by serialization in the `.c` file. State is non-owning for strings and NIC list; no release hook exists. Dependencies are `NetMessage.h`, `NetworkInterfaceCard.h`, and `BitStore.h`. Integration points are registration with management and local-node identity setup. Risks include using stack/temporary alias strings or NIC lists beyond their lifetime, zero default fields being interpreted differently by servers, and no deserialization support. Test signals are startup registration success and `RegisterNodeRespMsg` carrying assigned IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeRespMsg.c

## Research
`RegisterNodeRespMsg.c` implements receive-only parsing for management registration responses. It deserializes assigned `nodeNumID`, management gRPC port as an unsigned short, and filesystem UUID string. Serialization is dummy because the client only receives this response.

Control flow stops on the first failed field parse. State is the numeric ID, `grpcPort`, and receive-buffer-backed `fsUUID`. Dependencies are `RegisterNodeRespMsg.h`, `NumNodeID`, and serialization helpers. Integration points are client startup configuration, where the assigned node ID and gRPC port are stored into app/config state and the fsUUID identifies the filesystem. Risks include string lifetime, port width limits, missing validation for zero node ID, and dummy serialization misuse. Test signals are registration assigning non-zero IDs, `Config_setConnMgmtdGrpcPort` receiving the returned port, and fsUUID matching expected management state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeRespMsg.h

## Research
`RegisterNodeRespMsg.h` declares the receive-side registration response. It embeds `NetMessage`, stores `NumNodeID nodeNumID`, `grpcPort`, filesystem UUID pointer/length, initializes `NETMSGTYPE_RegisterNodeResp`, and provides getters for all three public values.

Control flow is init and access; payload parsing is in the `.c` file. State is fixed-size plus receive-buffer-backed fsUUID. Dependencies are `NetMessage.h`. Integration points are local client identity assignment and management gRPC endpoint configuration after registration. Risks are using fsUUID after receive-buffer disposal, no local validation of returned ID/port, and keeping field order synchronized with management. Test signals are startup registration consuming all fields correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.c

## Research
`RemoveNodeMsgEx.c` implements remove-node message serialization, deserialization, and incoming processing. Payload fields are node type, node numeric ID, and ack ID. On receive, it logs debug details, deletes metadata or storage nodes from the corresponding `NodeStoreEx`, warns for invalid node types, and sends either an ack response or a `RemoveNodeRespMsg` fallback response.

Control flow branches by node type and by whether `MsgHelperAck_respondToAckRequest` handled the response. State changes remove nodes from app node stores, affecting future routing and connection use. Dependencies include `App`, `NodeStoreEx`, `DatagramListener`, `Socket`, `MsgHelperAck`, `RemoveNodeRespMsg`, and serialization helpers. Risks are deleting active nodes while operations are in flight, invalid node-type handling, fallback response serialization buffer size, and no support for management/client node deletion here. Test signals are management remove notifications removing nodes from stores, ack behavior, fallback response send path, and invalid-type logging without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.h

## Research
`RemoveNodeMsgEx.h` declares the remove-node message. It embeds `NetMessage`, stores `NumNodeID nodeNumID`, `int16_t nodeType`, and ack ID pointer/length. Inline initialization sets `NETMSGTYPE_RemoveNode`, and `initFromNodeData` fills node identity fields and defaults ack ID to an empty string.

Control flow is init/access plus the `.c` serializer/deserializer/processor. State is fixed-size and non-owning for ack ID. Dependencies are `NetMessage.h` and `NodeType` from common node definitions. Integration points are management removal notifications and node-store maintenance. Risks are truncating `NodeType` into int16, empty ack semantics, and serialization support even though client mostly receives this message. Test signals are round-trip parse of node type/ID and node-store deletion after processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeRespMsg.h

## Research
`RemoveNodeRespMsg.h` defines remove-node responses as a `SimpleIntMsg` wrapper with type `NETMSGTYPE_RemoveNodeResp`. It supports empty initialization and initialization from an integer result value.

Control flow is inline delegation to `SimpleIntMsg`. State is a single integer payload. Dependencies are `SimpleIntMsg.h`. Integration points are fallback response handling in `RemoveNodeMsgEx` when no ack response is sent. Risks are unclear result-code semantics, no validation, and inconsistent use if most paths prefer ack-based responses. Test signals are fallback response serialization and receiver interpretation of the integer value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RemoveNodeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.c

## Research
`SetMirrorBuddyGroupMsgEx.c` implements receive-only processing for mirror buddy group updates. Deserialization reads node type, primary target ID, secondary target ID, buddy group ID, allow-update boolean, and ack ID. Processing chooses the storage or metadata buddy group mapper, passes the storage target mapper when needed, calls `MirrorBuddyGroupMapper_addGroup`, logs success or detailed failure, and responds to ack requests.

Control flow rejects invalid node types by returning false before ack. State changes are persistent in metadata or storage mirror buddy group mapper state. Dependencies include `App`, `MirrorBuddyGroupMapper`, `TargetMapper`, `MsgHelperAck`, `FhgfsOpsErr`, and serialization helpers. Risks include invalid node type skipping ack, target IDs not yet mapped, update policy mistakes with `allowUpdate`, and no serialization support. Test signals are management buddy-group push updates, mapper contents after add/update, expected error logging, and ack responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.h

## Research
`SetMirrorBuddyGroupMsgEx.h` declares the receive-only mirror buddy group update message. It embeds `NetMessage` and stores node type, primary/secondary target IDs, buddy group ID, allow-update flag, and ack ID. Inline getters expose each field, and initialization sets `NETMSGTYPE_SetMirrorBuddyGroup`.

Control flow is init/access plus `.c` deserialization/processing. State is fixed-size, with ack ID referencing the receive buffer. Dependencies are `NetMessage.h`. Integration points are storage and metadata mirror group mapper updates initiated by management. Risks include no outgoing serialization, invalid node-type handling, and lifetime of ack ID. Test signals are deserialization of all fields and correct mapper selection for storage versus metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.c

## Research
`BumpFileVersion.c` implements outgoing serialization for file-version bump requests. The payload always serializes `EntryInfo`; if `BUMPFILEVERSIONMSG_FLAG_HASEVENT` is set, it also serializes a `FileEvent`. The ops mark the message as supporting sequence numbers and use dummy deserialization.

Control flow is feature-flag gated around the optional event payload. State is non-owned `EntryInfo` and optional `FileEvent` pointers from the header. Dependencies include `BumpFileVersion.h`, `EntryInfo`, `FileEvent`, and `NetMessage`. Integration points are metadata/session paths that update cache invalidation or persistent file version counters after file events. Risks include feature flag mismatch with payload presence, non-owned pointer lifetime, and sequence-number retry semantics causing duplicate persistent bumps if server handling is not idempotent. Test signals are serialized payload with/without event, response handling through `BumpFileVersionRespMsg`, and retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.h

## Research
`BumpFileVersion.h` declares the outgoing `BumpFileVersionMsg`. It defines feature flags for persistent file-version changes and optional file-event logging, embeds `NetMessage`, and stores non-owned `EntryInfo` and optional `FileEvent` pointers. The inline initializer sets `NETMSGTYPE_BumpFileVersion`, stores pointers, and sets feature flags according to `persistent` and event presence.

Control flow is construction and flag setup; serialization is in the `.c` file. State is non-owning and no release hook exists. Dependencies are `NetMessage.h`, `EntryInfo.h`, and `FileEvent.h`. Integration points are metadata operations that need to bump file version counters for cache invalidation and event logging. Risks are dangling pointers, forgetting the event flag when event data is present, and persistent version semantics under retries. Test signals are feature flags matching payload layout and server response values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersionResp.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersionResp.h

## Research
`BumpFileVersionResp.h` defines the bump-file-version response as a `SimpleIntMsg` wrapper using `NETMSGTYPE_BumpFileVersionResp`. The integer payload is the operation result, typically interpreted as an `FhgfsOpsErr`-style status by callers.

Control flow is inline initialization only. State is a single integer response value inherited from `SimpleIntMsg`. Dependencies are `SimpleIntMsg.h`. Integration points are callers of `BumpFileVersionMsg` that need to know whether metadata accepted the version bump. Risks are relying on integer status without a typed accessor and no local validation of success/error domains. Test signals are response deserialization after version-bump requests and correct error propagation to callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/BumpFileVersionResp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.c

## Research
`FSyncLocalFileMsg.c` implements outgoing serialization for storage-server fsync requests. The payload contains client numeric ID, aligned file handle ID string, and target ID. The ops use dummy deserialization and default processing.

Control flow is fixed wire-order serialization. State is set by `FSyncLocalFileMsg_initFromSession`: non-owned file handle string plus scalar client/target IDs. Dependencies are `FSyncLocalFileMsg.h`, `NumNodeID`, and serialization helpers. Integration points are close/fsync/session code paths that ask storage targets to flush a local chunk file. Header feature flags in the `.h` support no-sync, session-check, and buddy-mirror target semantics. Risks include target ID meaning target versus buddy group based on flags, file handle lifetime, and absent sequence-number support here compared with open/close/lock messages. Test signals are fsync request serialization, response value via `FSyncLocalFileRespMsg`, and correct flag handling in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.h

## Research
`FSyncLocalFileMsg.h` declares the outgoing fsync-local-file storage message. It defines flags for no-sync, session checking, buddy-mirror group target IDs, and secondary selection. The struct embeds `NetMessage`, stores `NumNodeID clientNumID`, non-owned file handle ID pointer/length, and target ID. The inline session initializer fills these fields with `NETMSGTYPE_FSyncLocalFile`.

Control flow is construction plus serialization in the `.c` file. State is non-owning for the file handle and fixed-size otherwise. Dependencies are `NetMessage.h`. Integration points are storage session synchronization and mirrored target flush handling. Risks are flag/target mismatch, using stale file handles, and no local validation of target ID. Test signals are correct payload layout and server responses for normal, no-sync, session-check, and buddy-mirror cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileRespMsg.h

## Research
`FSyncLocalFileRespMsg.h` defines fsync-local-file responses as `SimpleInt64Msg` with type `NETMSGTYPE_FSyncLocalFileResp`. `FSyncLocalFileRespMsg_getValue` exposes the 64-bit response value, which can represent a result/status domain chosen by the storage protocol.

Control flow is inline init and accessor only. State is one int64 payload. Dependencies are `SimpleInt64Msg.h`. Integration points are fsync request paths that need storage-server completion status. Risks include ambiguous signed 64-bit semantics and no typed conversion to `FhgfsOpsErr` in this wrapper. Test signals are response parsing for successful and failed storage fsync operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/FSyncLocalFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.c

## Research
`GetFileVersionMsg.c` implements outgoing serialization for querying a file version. The payload is just serialized `EntryInfo`; deserialization is dummy because the client sends this request and expects `GetFileVersionRespMsg`.

Control flow is one serializer call through `EntryInfo_serialize`. State is a non-owned `EntryInfo` pointer in the message. Dependencies are `GetFileVersionMsg.h` and storage entry serialization. Integration points are cache invalidation/version checking code that asks metadata for the current file version. Risks are dangling entry info, no sequence-number support, and relying on server-side result/version pairing. Test signals are serialized entry info matching target file and response version updating caller state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.h

## Research
`GetFileVersionMsg.h` declares an outgoing metadata request to fetch a file version. It embeds `NetMessage`, stores a non-owned `EntryInfo` pointer, and initializes `NETMSGTYPE_GetFileVersion` with the shared ops.

Control flow is inline construction, with payload serialization in the `.c` file. State is non-owning and has no release hook. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are file-version/cache-coherency logic and metadata request handling. Risks are using an `EntryInfo` whose lifetime ends before serialization and no local validation of entry type. Test signals are metadata response version values and error propagation through `GetFileVersionRespMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionRespMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionRespMsg.c

## Research
`GetFileVersionRespMsg.c` implements receive-only parsing for file-version responses. It deserializes an integer result and an unsigned 32-bit version, stores the result as `FhgfsOpsErr`, and returns false if either field is missing.

Control flow is a combined two-field parse. State is fixed-size result plus version. Dependencies are `GetFileVersionRespMsg.h` and serialization helpers. Integration points are callers that query metadata for a file version and then update cache-coherency state. Risks include converting a raw int to `FhgfsOpsErr` without range validation, version wraparound semantics, and dummy serialization if misused. Test signals are success/error responses and version field propagation to caller state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionRespMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionRespMsg.h

## Research
`GetFileVersionRespMsg.h` declares the file-version response. It embeds `NetMessage` as `base`, stores `FhgfsOpsErr result` and `uint32_t version`, and initializes with `NETMSGTYPE_GetFileVersionResp`.

Control flow is init plus deserialization in the `.c` file. State is fixed-size and has no owned resources. Dependencies are `NetMessage.h` and `StorageErrors.h`. Integration points are file cache/version validation paths. Risks are no inline getters, direct field access by callers, and raw int-to-enum conversion in deserialization. Test signals are callers observing correct success/error and version after response parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/GetFileVersionRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.c

## Research
`FLockAppendMsg.c` implements outgoing serialization for append-lock requests. The payload contains client numeric ID, client-wide file descriptor ID, owner PID, lock type flags, serialized `EntryInfo`, aligned file handle ID, and aligned lock ack ID. Deserialization is dummy.

Control flow is fixed field order. State is non-owned `EntryInfo`, file handle, and lock ack ID, plus scalar lock identity fields. Dependencies are `FLockAppendMsg.h`, `EntryInfo`, `NumNodeID`, and serialization helpers. Integration points are global append-lock code paths that coordinate append serialization across clients/storage. Risks include non-owned pointer lifetime, owner PID being informative only and shared across fork, lockAckID correctness for asynchronous lock grants, and lack of sequence-number support unlike entry/range locks. Test signals are server lock response handling, lock grant ack wakeups, and correct serialization of aligned strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.h

## Research
`FLockAppendMsg.h` declares the outgoing append-lock request. It embeds `NetMessage` and stores client ID, non-owned file handle, non-owned entry info, client-wide FD identity, owner PID, lock type flags, and non-owned lock ack ID. The inline session initializer fills all fields and computes string lengths.

Control flow is construction and later serialization. State is non-owning for pointers, fixed-size for lock metadata. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are append locking and asynchronous lock-grant acknowledgement machinery. Risks are stale file handle/entry info, wrong lock type flags, empty ack IDs preventing waiters from waking, and no local validation of range/append semantics. Test signals are append lock request/response behavior and `LockGrantedMsgEx` matching the lockAckID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendRespMsg.h

## Research
`FLockAppendRespMsg.h` defines append-lock responses as a receive-only `SimpleIntMsg` wrapper using `NETMSGTYPE_FLockAppendResp`. The integer represents a storage/metadata result code, with `StorageErrors.h` included for the expected status domain.

Control flow is inline initialization only; deserialization is inherited from `SimpleIntMsg`. State is one integer payload. Dependencies are `SimpleIntMsg.h` and `StorageErrors.h`. Integration points are append-lock request callers that decide whether the lock was granted immediately, denied, or will arrive asynchronously. Risks are no typed accessor/conversion in this header and semantic mismatch if status values change. Test signals are lock response parsing and correct waiting behavior for delayed grants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockAppendRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.c

## Research
`FLockEntryMsg.c` serializes outgoing whole-entry lock requests. Payload order is client numeric ID, client-wide FD identity, owner PID, lock type flags, entry info, aligned file handle ID, and aligned lock ack ID. The ops mark the message as supporting sequence numbers and use dummy deserialization.

Control flow is fixed field serialization. State is non-owned entry/file/ack strings and scalar lock metadata. Dependencies are `FLockEntryMsg.h`, `EntryInfo`, `NumNodeID`, and serialization. Integration points are global flock/fcntl entry-lock paths where retries and sequence numbers help avoid duplicate or reordered operations. Risks include retry semantics, stale non-owned pointers, lock type flag correctness, and asynchronous grant ack ID coordination. Test signals are lock acquisition/release request serialization, delayed lock grants, and sequence-number behavior under retry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.h

## Research
`FLockEntryMsg.h` declares the outgoing whole-entry lock message. It embeds `NetMessage` and stores client numeric ID, non-owned file handle, non-owned `EntryInfo`, client-wide FD ID, owner PID, lock type flags, and non-owned lock ack ID. The inline session initializer sets lengths and scalar fields.

Control flow is construction plus serialization in the `.c` file. State is non-owning and not persisted in the message. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are distributed file locking and lock-grant acknowledgment handling. Risks are non-owned lifetime, ambiguous `clientFD` identity, incorrect lock flags, and empty/stale ack IDs. Test signals are entry lock request/response flows, delayed grant delivery, and sequence-number retry correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryRespMsg.h

## Research
`FLockEntryRespMsg.h` defines whole-entry lock responses as a `SimpleIntMsg` wrapper with type `NETMSGTYPE_FLockEntryResp`. It is receive-oriented, and the integer value is expected to map to storage error/result codes.

Control flow is inline initialization; inherited simple-int ops handle payload. State is one integer result. Dependencies are `SimpleIntMsg.h` and `StorageErrors.h`. Integration points are entry-lock callers and lock wait logic. Risks are lack of typed result accessor and relying on higher layers to interpret wait/grant/error codes. Test signals are immediate lock responses and delayed-grant paths being distinguished correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockEntryRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.c

## Research
`FLockRangeMsg.c` serializes outgoing byte-range lock requests. The payload contains client numeric ID, start offset, end offset, owner PID, lock type flags, entry info, aligned file handle ID, and aligned lock ack ID. The ops support sequence numbers and use dummy deserialization.

Control flow is fixed serialization. State is non-owned file/entry/ack data plus scalar range and lock metadata. Dependencies are `FLockRangeMsg.h`, `EntryInfo`, `NumNodeID`, and serialization helpers. Integration points are distributed POSIX byte-range locking. Risks include inclusive/exclusive range interpretation, start/end overflow or invalid ordering, non-owned lifetimes, ack ID matching, and retry semantics for lock operations. Test signals are range lock requests for shared/exclusive/unlock flags, server responses, and delayed lock grant acknowledgements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.h

## Research
`FLockRangeMsg.h` declares the outgoing byte-range lock message. It stores client numeric ID, non-owned file handle, non-owned `EntryInfo`, owner PID, lock type flags, `uint64_t start` and `end`, and non-owned lock ack ID. The inline initializer computes string lengths and records all range/lock fields.

Control flow is construction plus serialization in the `.c` file. State is non-owning for pointers, fixed-size for range and lock fields. Dependencies are `NetMessage.h` and `EntryInfo.h`. Integration points are fcntl range-lock handling and asynchronous lock-grant tracking. Risks are invalid ranges, mismatch with Linux `file_lock` semantics, string lifetime, and wrong ack ID association. Test signals are byte-range lock/unlock operations across clients and delayed grant wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeRespMsg.h

## Research
`FLockRangeRespMsg.h` defines byte-range lock responses as a `SimpleIntMsg` wrapper with type `NETMSGTYPE_FLockRangeResp`. It is intended for incoming/deserialized responses and includes `StorageErrors.h` for status interpretation.

Control flow is inline initialization only. State is one integer payload. Dependencies are `SimpleIntMsg.h` and `StorageErrors.h`. Integration points are range-lock callers that decide whether to proceed, fail, or wait for a `LockGrantedMsgEx`. Risks are semantic ambiguity of the integer and no local validation of status domains. Test signals are range-lock response handling and correct behavior for immediate and delayed grants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/FLockRangeRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.c

## Research
`LockGrantedMsgEx.c` implements receive-only handling for asynchronous lock grant notifications. The payload contains aligned lock ack ID, aligned ack ID, and granter node numeric ID. Processing records the lock ack in `AcknowledgmentStore`; if a waiter was registered, it sends an ack response and queues an ack through `AckManager` for the granter node.

Control flow intentionally sends acknowledgement only when a waiter still exists, simplifying interrupted lock waits. State changes occur in the acknowledgment store and ack manager queue. Dependencies include `App`, `AckManager`, `AcknowledgmentStore`, `MsgHelperAck`, `SocketTk`, and `NumNodeID`. Risks include lost grants if ack IDs mismatch, not acking after interrupted waits by design, receive-buffer string lifetime, and duplicate grant messages. Test signals are blocked lock waiters waking, ack queue entries for granter nodes, and no response when no waiter remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.h

## Research
`LockGrantedMsgEx.h` declares the incoming lock-granted notification. It embeds `NetMessage` and stores receive-buffer-backed lock ack ID, ack ID, and `NumNodeID granterNodeID`. Inline getters expose all fields, and init sets `NETMSGTYPE_LockGranted`.

Control flow is init/access plus deserialization/processing in the `.c` file. State is non-owning for strings and fixed-size for the granter ID. Dependencies are `NetMessage.h`. Integration points are distributed lock wait queues, acknowledgment store, and ack manager. Risks are string lifetime, empty ack IDs, and no outgoing serialization support. Test signals are matching lockAckID values waking the correct waiter and granter acknowledgements being queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/locking/LockGrantedMsgEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileMsg.c

## Research
`CloseFileMsg.c` serializes outgoing close-file metadata/session requests. The payload contains client numeric ID, aligned file handle ID, serialized entry info, max used node index, and optional `FileEvent` when `CLOSEFILEMSG_FLAG_HAS_EVENT` is set. The ops mark the message as supporting sequence numbers and use dummy deserialization.

Control flow is feature-flag gated around optional event serialization. State is non-owned file handle, entry info, and optional event plus scalar client/max-node fields. Dependencies are `CloseFileMsg.h`, `EntryInfo`, `FileEvent`, and serialization helpers. Integration points are file close paths, append-lock cancellation, early close response behavior, and file-event logging. Risks are retry/sequence idempotency, optional event flag mismatch, non-owned pointer lifetime, and `maxUsedNodeIndex` correctness for striped files. Test signals are close requests with/without events, early-response flags from callers, and `CloseFileRespMsg` result handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileMsg.h

## Research
`CloseFileMsg.h` declares outgoing close-file messages. It defines flags for early response, append-lock cancellation, and optional file-event payload. The struct embeds `NetMessage`, stores client ID, non-owned file handle, max used node index, non-owned `EntryInfo`, and optional non-owned `FileEvent`. The inline session initializer sets fields and the event flag when needed.

Control flow is construction/flag setup plus serialization in the `.c` file. State is non-owning and fixed-size. Dependencies include `NetMessage.h`, `EntryInfo.h`, and `FileEvent.h`. Integration points are VFS close/release handling, metadata close requests, event logging, and append-lock cleanup. Risks are stale session handles, incorrect flags causing server behavior changes, event pointer lifetime, and retry duplication. Test signals are close success/failure responses, event-log side effects, and behavior with early-close enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileRespMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileRespMsg.h

## Research
`CloseFileRespMsg.h` defines close-file responses as `SimpleIntMsg` with type `NETMSGTYPE_CloseFileResp`. It provides an initializer and getter for the integer result value.

Control flow is inline delegation to `SimpleIntMsg`; inherited ops handle deserialization. State is one integer response. Dependencies are `SimpleIntMsg.h`. Integration points are file close/release paths that need metadata close status. Risks are integer result semantics not being typed in this wrapper and callers deciding whether close errors should be propagated or logged only. Test signals are close response parsing for success and storage/metadata error values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/CloseFileRespMsg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.c -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.c

## Research
`OpenFileMsg.c` serializes outgoing metadata open-file requests. The payload contains client numeric ID, access flags, serialized entry info, and optional file-event information when `OPENFILEMSG_FLAG_HAS_EVENT` is set. The ops support sequence numbers and use dummy deserialization.

Control flow is fixed field order with feature-flag gated event serialization. State is non-owned `EntryInfo` and optional `FileEvent`, plus access flags and client ID. Dependencies are `OpenFileMsg.h`, `EntryInfo`, `FileEvent`, and serialization helpers. Integration points are VFS open paths, quota/access-check flags, event logging, and metadata session establishment. Risks include access flag mismatch with Linux open flags, optional event flag/payload mismatch, non-owned lifetime, and sequence-number idempotency under retries. Test signals are open responses with file handle/path/pattern, bypass-access-check flag behavior, and event logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.h -->
# sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.h

## Research
`OpenFileMsg.h` declares outgoing open-file metadata requests. It defines feature flags for quota information, file event payload, and bypassing metadata access checks. The struct embeds `NetMessage`, stores client numeric ID, non-owned `EntryInfo`, access flags, and optional non-owned `FileEvent`. The inline initializer sets `NETMSGTYPE_OpenFile`, stores fields, and sets the event flag when event data is present.

Control flow is construction and flag setup, with serialization in the `.c` file. State is non-owning for entry/event pointers. Dependencies include `EntryInfo.h`, `FileEvent.h`, and `NetMessage.h`. Integration points are VFS open/create workflows, session tracking, quota/access policy, and file-event logging. Risks are the unused `sessionIDLen` field suggesting legacy drift, stale entry info pointers, incorrect bypass flag use, and retry semantics. Test signals are open request serialization and `OpenFileRespMsg` parsing under normal, denied, and event-logging cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/net/message/session/opening/OpenFileMsg.h -->
