# subset-b-000538 research

Grouped research for BeeGFS client module toolkit, component, worker, and fault-injection files. Each file section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.c

## Purpose
Implements metadata helper routines used by VFS-facing create and root-entry paths in the BeeGFS client module. `CreateInfo_init` normalizes create parameters, ownership, mode/umask, preferred targets, storage-pool defaults, and file-event pointers into a single request object. `MetadataTk_getRootEntryInfoCopy` constructs a heap-backed `EntryInfo` for the BeeGFS root directory using the metadata node store root owner.

## Important APIs and control flow
`CreateInfo_init` is compiled with different signatures for idmapped mounts, user namespace mounts, and legacy kernels. It computes `newMode`, maps current fsuid/fsgid through mount/superblock namespaces when enabled, applies SGID or BeeGFS `grpid` inheritance from the parent inode, fills preferred target lists from `App`, and initializes an invalid storage pool. `MetadataTk_getRootEntryInfoCopy` duplicates empty parent/name strings plus `META_ROOTDIR_ID_STR`, calls `EntryInfo_init`, and returns whether the root owner is valid.

## State, dependencies, integration
The file depends on `App`, mount config, Linux credential/idmap helpers, `NodeStoreEx`, `EntryInfo`, `StoragePoolId`, and `StringTk`. It does not persist data, but it prepares state later serialized into metadata messages.

## Risks and test signals
Ownership mapping is kernel-version-sensitive; tests should cover idmapped, userns, SGID, `grpid`, and legacy paths. Root entry callers must free duplicated `EntryInfo` values. `parentDirInode == NULL` falls back to creator gid and init/superblock namespace behavior, so create paths should ensure expected parent context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.h

## Purpose
Declares metadata helper types and inline initializers for create, open, and lookup-intent operations. It is the shared contract between VFS operations and BeeGFS metadata messages.

## Important APIs and types
Exports `CreateInfo`, `OpenInfo`, and `LookupIntentInfoIn`. `CreateInfo` carries entry name, uid/gid, mode, umask, preferred meta/storage target lists, exclusive-create flag, override storage pool, and optional `FileEvent`. `OpenInfo_init` converts Linux open flags into BeeGFS access flags through `OsTypeConv_openFlagsOsToFhgfs`. `LookupIntentInfoIn_init` records parent and name; `LookupIntentInfoIn_addEntryInfo`, `addMetaVersion`, `addOpenInfo`, and `addCreateInfo` layer optional revalidate/open/create inputs onto a lookup intent. `CreateInfo_setStoragePoolId` overrides the default invalid pool.

## State, dependencies, integration
The header integrates `EntryInfo`, `LookupIntentInfoOut`, `UInt16List`, Linux inode namespaces, and storage definitions. It holds borrowed pointers, so object lifetime is controlled by callers and outbound message construction.

## Risks and test signals
Several inline functions are non-`static` in the header, so include/link behavior depends on the build model. `LookupIntentInfoIn_init` does not initialize `metaVersion` or `isExclusiveCreate`; callers should only read those after adding the corresponding info. Tests should validate lookup-create-open combinations and flag conversion for paged versus non-paged opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/MetadataTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.c

## Purpose
Implements IP/CIDR allow-list filtering for client networking. The filter is loaded from a configured file into an array of IPv6-form entries; IPv4 rules are represented as IPv4-mapped IPv6 addresses.

## Important APIs and control flow
`NetFilter_construct`, `NetFilter_init`, `NetFilter_uninit`, and `NetFilter_destruct` manage allocation and parsed state. `NetFilter_isAllowed` allows all traffic if no entries exist and otherwise delegates to `NetFilter_isContained`. `NetFilter_isContained` always permits IPv4 and IPv6 loopback, then masks the input address and compares it to pre-masked entries. `parse_NetFilterEntry` accepts IPv4 or IPv6 text with a slash prefix, validates prefix bounds, builds masks with `beegfs_make_in6_addr_mask_from_prefix`, and stores `mask` plus `compare`. `__NetFilter_prepareArray` loads lines with `Config_loadStringListFile`, preallocates a worst-case array, and appends only successfully parsed entries.

## State, dependencies, integration
State is an in-memory `filterArray` and length. Dependencies include `Config`, `StrCpyList`, kernel `in4_pton`/`in6_pton`, `SocketTk` address helpers, and Linux IPv6 comparison helpers. `DatagramListener` uses the filter when sending UDP messages to node NICs.

## Risks and test signals
Invalid rows are logged but ignored, so a partially malformed file may silently reduce policy strictness. `kstrtou8(slash + 1, ...)` assumes parsing set `slash`; rules without a slash should be tested. Cover IPv4 `/0..32`, IPv6 `/0..128`, loopback bypass, empty filename, load failure, and malformed prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.h

## Purpose
Defines the public IP filter data structures and operations for BeeGFS kernel networking.

## Important APIs and types
`NetFilterEntry` stores an IPv6 mask and a pre-masked compare address. `NetFilter` stores a dynamically allocated array and entry count. The public API covers init/construct/uninit/destruct, `NetFilter_isAllowed`, `NetFilter_isContained`, and an inline `NetFilter_getNumFilterEntries`.

## State, dependencies, integration
The header depends on kernel IPv4/IPv6 types and `common/Common.h`. It exposes raw array ownership only to implementation code; external users should treat `NetFilter` as an opaque-ish struct and call lifecycle helpers. It is integrated through `App_getNetFilter` and datagram sending.

## Risks and test signals
Callers must not call `NetFilter_isAllowed` before successful init because the struct contains raw pointers. Empty filters are intentionally permissive. Tests should verify lifecycle cleanup, count reporting, and that filter logic remains IPv4-mapped compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NetFilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.c

## Purpose
Implements ordered filtering and prioritization of local NIC addresses. Filter rows can match interface name, IP address, address family, NIC type, and can be inverted with `!` to forbid a match.

## Important APIs and control flow
`NicAddressFilter_getPosition` walks the filter array in order and returns the first matching non-inverted position or `SIZE_MAX` for no match or inverted match. `NicAddressFilter_isAllowed` permits all NICs when the filter is empty and otherwise requires a valid position. `parse_NicAddressFilterEntry` tokenizes whitespace-delimited rows with a small `Reader`, supports `*` wildcards per column, validates interface names, parses IPv4/IPv6 addresses, accepts family `4`/`6`, and maps `tcp`/`rdma` to NIC address types. `NicAddressFilter_construct` allocates a maximal array from a `StrCpyList`, parses every row, and aborts construction on the first invalid row. `NicAddressFilter_destruct` frees the array and object.

## State, dependencies, integration
State is an ordered in-memory array of parsed match entries. Dependencies include `NicAddress`, kernel address parsers, `StrCpyListIter`, and BeeGFS NIC type definitions. The order doubles as preference ranking because callers can use returned positions.

## Risks and test signals
Unlike `NetFilter`, any malformed row fails the entire filter. Token buffers are fixed at 64 bytes and names are bounded by `IFNAMSIZ`. Test row parsing with wildcards, inverted first match, overlapping allow/deny rows, IPv4-mapped comparisons, RDMA/TCP type matching, and invalid extra columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.h

## Purpose
Declares the NIC-address filter interface used to accept, reject, and rank network interfaces.

## Important APIs and types
The implementation type `NicAddressFilter` is forward-declared. Public functions are `NicAddressFilter_construct`, `NicAddressFilter_destruct`, `NicAddressFilter_isAllowed`, `NicAddressFilter_getPosition`, and `NicAddressFilter_getNumFilterEntries`. Inputs are `StrCpyList` configuration rows and `NicAddress` candidates.

## State, dependencies, integration
The header depends on BeeGFS `NicAddress` and `Common` definitions. It hides the parsed entry layout, keeping callers focused on boolean allow and ordered position semantics.

## Risks and test signals
Callers must handle a `NULL` construct result for invalid configuration or allocation failure. Because `getPosition` returns `SIZE_MAX` both for no match and explicit denial, tests should assert caller handling of denied interfaces does not treat them as lowest-priority accepted NICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.c

## Purpose
Provides synchronous helper calls for downloading cluster topology from a management node and for dropping node-store connections.

## Important APIs and control flow
`NodesTk_downloadNodes` sends `GetNodesMsg`, parses `GetNodesRespMsg` into a caller-owned `NodeList`, and optionally returns root owner ID and mirror state. `NodesTk_downloadTargetMappings` sends `GetTargetMappingsMsg` and splices response mappings into a caller list. `NodesTk_downloadStatesAndBuddyGroups` sends `GetStatesAndBuddyGroupsMsg` with local node ID, then splices target states and buddy groups from the response. All request helpers use `RequestResponseArgs_prepare` and silence retry/connection logs in non-debug builds. `NodesTk_dropAllConnsByStore` iterates a `NodeStoreEx` and disconnects available streams from each node pool.

## State, dependencies, integration
The file depends on BeeGFS network messages, `MessagingTk`, `NodeStoreEx`, `NodeConnPool`, and Linux list splicing. `InternodeSyncer` uses these helpers for node sync, mapping sync, and target-state refresh.

## Risks and test signals
Callers own parsed nodes and spliced list elements. Failed communication leaves output lists untouched except for any caller initialization. Test response parsing, log flag behavior, list ownership after `RequestResponseArgs_freeRespBuffers`, and connection drop iteration with node references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.h

## Purpose
Declares node/topology download helpers and store connection cleanup.

## Important APIs and types
Exports `NodesTk_downloadNodes`, `NodesTk_downloadTargetMappings`, `NodesTk_downloadStatesAndBuddyGroups`, and `NodesTk_dropAllConnsByStore`. It uses `App`, `Node`, `NodeType`, `NodeList`, `NumNodeID`, `NodeStoreEx`, and kernel `list_head` outputs.

## State, dependencies, integration
The header has no state. Its functions integrate management-plane messages into `InternodeSyncer` and other component code that needs a refreshed local topology view.

## Risks and test signals
APIs return `bool` for communication success but do not encode partial parse details. Tests should initialize output lists before calls and verify cleanup rules for both success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/NodesTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.c

## Purpose
Wraps Linux kernel random bytes for simple integer and bounded-range random values.

## Important APIs and control flow
`Random_getNextInt` fills an `int` using `get_random_bytes` and converts negative values to non-negative by bitwise complement, avoiding `-INT_MIN` overflow. `Random_getNextInRange` applies modulo reduction over an inclusive `[min, max]` interval and adds `min`.

## State, dependencies, integration
No persistent state is stored. It depends on kernel RNG APIs and is used by `InternodeSyncer` to jitter management heartbeat retry waits.

## Risks and test signals
`Random_getNextInRange` assumes `max >= min`; invalid ranges can divide by zero or wrap. Modulo reduction introduces bias, acceptable for timing jitter but not cryptographic selection. Tests should cover boundary values and negative min ranges if callers rely on them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.h

## Purpose
Declares random helper functions for kernel-module code.

## Important APIs and types
Exports `Random_getNextInt` and `Random_getNextInRange`. The API returns signed `int` values and defines `min`/`max` as inclusive range bounds.

## State, dependencies, integration
The header depends only on BeeGFS common definitions and leaves RNG implementation to the C file.

## Risks and test signals
Callers must enforce valid ranges. Unit tests or static checks should flag any `Random_getNextInRange` call where `max - min + 1` can be zero or overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.c

## Purpose
Implements BeeGFS client-module wire serialization/deserialization helpers for strings, raw arrays, NIC lists, node lists, string lists/vectors, and integer list/vector containers.

## Important APIs and control flow
`__Serialization_deserializeNestedField` consumes a length-prefixed nested field and exposes a bounded inner context. String helpers serialize length, bytes, and terminating zero, with an aligned variant adding padding to a 4-byte boundary. NIC list serialization writes total length, count, protocol marker, address bytes, fixed-size name, NIC type, and padding; preprocess validates and slices raw list data. Node list preprocess walks variable fields to validate a buffer, while `Serialization_deserializeNodeList` constructs `Node` objects using app RDMA NIC context. List/vector serializers write total byte length and count, then payload elements; preprocess functions validate lengths before callers append decoded values.

## State, dependencies, integration
Serialization state is held in caller-provided `SerializeCtx`, `DeserializeCtx`, and `RawList`. The file depends on unaligned little-endian accessors, `NicAddressList`, BeeGFS list/vector wrappers, `Node_construct`, `App_lockNicList`, and Linux list/container helpers. It is used by network message implementations across the client.

## Risks and test signals
`__Serialization_deserializeNestedField` subtracts the header length from an unsigned length; malformed lengths below four can underflow. Node deserialization uses `.length = -1` for its inner context after preprocess, relying on prior validation. Tests should fuzz truncated buffers, invalid terminators, nested length underflow, invalid NIC protocols, large element counts, and compatibility between list and vector wire formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.h

## Purpose
Declares and partially implements the custom BeeGFS serialization framework, including primitive little-endian encoders, list/vector helpers, and macros to generate serializers for structs, lists, and enums.

## Important APIs and types
Primitive inline helpers serialize and deserialize chars, bools, uint8, short/ushort, int/uint, and int64/uint64 through `SerializeCtx` and `DeserializeCtx`. Declarations cover strings, aligned strings, char arrays, NIC lists, node lists, string copy lists/vectors, UInt8/UInt16 lists/vectors, and Int64 lists/vectors. Macro families `SERDES_DEFINE_SERIALIZERS`, `SERDES_DEFINE_SERIALIZERS_SIMPLE`, `SERDES_SERIALIZE_AS`, `SERDES_DEFINE_LIST_SERIALIZERS`, and `SERDES_DEFINE_ENUM_SERIALIZERS` generate repetitive field-order serialization code.

## State, dependencies, integration
The header depends on many BeeGFS containers and node/network types plus kernel unaligned accessors. It is a central integration point for message fields that are not protobuf-based.

## Risks and test signals
Generated serializers rely on exact field order and manual cleanup expressions. `Serialization_serializeBlock` supports a sizing pass when `ctx->data == NULL`; callers must allocate the final buffer from the computed length. Tests should compile representative macro expansions, verify endian stability, run round trips for every primitive and generated struct, and exercise allocation-failure cleanup in list deserializers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SerializationTypes.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SerializationTypes.h

## Purpose
Defines the minimal context structs used by the BeeGFS serialization layer.

## Important APIs and types
`SerializeCtx` contains a constant output data pointer and a running `length`. When `data` is `NULL`, serializers still advance `length` for sizing. `DeserializeCtx` contains a current data pointer and remaining length. `RawList` records a raw list payload pointer, byte length, and element count after preprocess.

## State, dependencies, integration
These structs carry transient cursor state only. They are used by `Serialization.c`, `Serialization.h` inline helpers, and generated serdes macros throughout network message code.

## Risks and test signals
The context structs do not carry capacity separately from length and rely on callers to provide valid buffers. Tests should assert that deserializers reduce `length` and advance `data` consistently, and that sizing and writing passes produce identical final lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SerializationTypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.c

## Purpose
Implements socket toolkit helpers for kernel polling, address parsing, and endpoint formatting.

## Important APIs and control flow
`SocketTk_initOnce` opens `/dev/null` as a dummy file pointer required by socket poll callbacks; `SocketTk_uninitOnce` closes it. `SocketTk_poll` multiplexes BeeGFS standard and RDMA sockets: it initializes poll wait queues, loops until events/timeout/fatal signal/error, calls RDMA or raw socket poll implementations, schedules interruptibly/killably, then runs RDMA cleanup and frees wait queues. `SocketTk_getHostByAddrStr` parses IPv4 into mapped IPv6 or native IPv6 and returns `INADDR_NONE`-mapped on failure. `SocketTk_in_aton` wraps that parser. `SocketTk_ipaddrToStr` and `SocketTk_endpointToStr` format IPv4-mapped and IPv6 addresses.

## State, dependencies, integration
Global state is `SocketTkDummyFilp`. Dependencies include `StandardSocket`, `RDMASocket`, Linux poll/scheduler APIs, `TimeTk`, and BeeGFS sockaddr helpers. Messaging and datagram code use these helpers for wait and logging paths.

## Risks and test signals
Polling depends on a successfully initialized dummy filp. The function mutates per-socket `poll.revents`, so callers should clear/add sockets through `PollState_addSocket`. Test timeout behavior, fatal-signal exit, RDMA cleanup calls, invalid address parsing, and IPv6 endpoint formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.h

## Purpose
Declares socket toolkit APIs and the small `PollState` abstraction used by BeeGFS socket code.

## Important APIs and types
Exports one-time init/uninit, `SocketTk_poll`, address parsing/formatting functions, and endpoint formatting. `PollState` wraps a `list_head`; inline helpers initialize it and append sockets with requested events while resetting `revents`. `Socket_formatAddrOrPeername` formats a supplied source address or falls back to `sock->peername` into the socket's temporary buffer.

## State, dependencies, integration
The header depends on BeeGFS `Socket`, `Time`, and Linux poll types. It integrates with standard and RDMA socket implementations and log formatting.

## Risks and test signals
`Socket_formatAddrOrPeername` uses a socket-owned temp buffer and explicitly is not concurrency-safe. Tests should cover repeated formatting on the same socket, adding multiple sockets to a poll state, and ensuring callers initialize `PollState` before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SocketTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.c

## Purpose
Implements kernel-safe string utilities for splitting, boolean parsing, trimming, and formatted allocation.

## Important APIs and control flow
`StringTk_explode` splits a delimiter-separated string into a `StrCpyList`, skipping empty elements. It creates temporary substrings with `StringTk_subStr`, appends copies to the output, and frees temporaries. `StringTk_strToBool` treats empty strings and common truthy strings as `true`, and everything else as `false`. `StringTk_trimCopy` trims spaces, newlines, carriage returns, and tabs into a newly allocated string. `StringTk_kasprintf` emulates `kasprintf` by first measuring with `vsnprintf`, allocating, then formatting.

## State, dependencies, integration
No persistent state is kept. It depends on BeeGFS allocation wrappers and `StrCpyList`. Metadata, filters, and component queues use these helpers for copied IDs and configuration strings.

## Risks and test signals
`StringTk_strToBool` returning true for empty strings is intentional but easy to misuse for explicit false parsing. Allocation failures are not consistently checked by callers. Test delimiter edge cases, all-whitespace trim, truthy/falsy config values, and long format strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.h

## Purpose
Declares and implements inline string conversion, duplication, substring, and numeric helpers for the client module.

## Important APIs and types
Exports `StringTk_explode`, `StringTk_strToBool`, `StringTk_trimCopy`, and `StringTk_kasprintf`. Inline helpers include `StringTk_hasLength`, `StringTk_strncpyTerminated` via `strscpy`, numeric conversions using `simple_strto*`, `StringTk_strDup`, `StringTk_subStr`, `StringTk_intToStr`, and `StringTk_uintToStr`.

## State, dependencies, integration
The header depends on BeeGFS common allocation wrappers and `StrCpyList`. Returned strings from duplicate/substr/format helpers are heap-owned by callers.

## Risks and test signals
`StringTk_subStr` does not check allocation before writing the terminator. Numeric conversions ignore parse errors and trailing data. Tests should cover allocation failure paths where practical, non-numeric strings, zero-length substrings, and safe truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/StringTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SynchronizedCounter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SynchronizedCounter.h

## Purpose
Defines a small atomic counter plus completion barrier used to wait until a count reaches zero.

## Important APIs and control flow
`SynchronizedCounter_init` sets the atomic count to zero and initializes a completion. `SynchronizedCounter_waitForCount` subtracts the expected wait count and waits for completion. `SynchronizedCounter_incCount` and `SynchronizedCounter_incCountBy` add work completions; if the atomic result becomes zero, they complete the barrier.

## State, dependencies, integration
State is `atomic_t count` plus a Linux `completion`. It depends on kernel atomic and completion APIs. It is suited for fan-out/fan-in cases where waiters pre-decrement by expected completions and workers increment as they finish.

## Risks and test signals
The completion is one-shot unless reinitialized; reuse across multiple independent waits can be unsafe. Incorrect wait counts can deadlock or complete too early. Tests should simulate exact, under, and over completion counts and validate no missed wakeup when increments race with wait setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/SynchronizedCounter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Time.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Time.h

## Purpose
Provides a kernel-version-compatible `Time` abstraction over monotonic or real timestamps and elapsed-time helpers.

## Important APIs and control flow
`Time` aliases `timespec64` or `timespec`. `Time_setToNow` uses monotonic kernel time; `Time_setToNowReal` uses real wall-clock time. `Time_init`, `Time_initZero`, and `Time_setZero` initialize values. `Time_elapsedSinceMS`, `Time_elapsedSinceNS`, `Time_toNS`, `Time_compare`, and `Time_elapsedMS` implement elapsed and comparison helpers over seconds/nanoseconds.

## State, dependencies, integration
State is caller-owned timestamp structs. `AckManager`, `InternodeSyncer`, and delayed queues use `Time` to track age and periodic intervals.

## Risks and test signals
`Time_getIsZero` checks `tv_sec` twice and never checks `tv_nsec`, so a timestamp with zero seconds and nonzero nanoseconds is considered zero. Millisecond elapsed calculations use unsigned seconds plus signed millisecond delta and assume non-decreasing times. Tests should cover nanosecond borrow, zero detection, compare overflow for far-apart times, and 32-bit/64-bit timestamp builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/Time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/TimeTk.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/TimeTk.h

## Purpose
Provides a tiny schedulable-time conversion helper.

## Important APIs and control flow
`TimeTk_msToJiffiesSchedulable` converts milliseconds to jiffies with `msecs_to_jiffies` and caps the result to `MAX_SCHEDULE_TIMEOUT - 1`, avoiding the sentinel infinite-sleep value.

## State, dependencies, integration
No state is stored. `SocketTk_poll` uses it to compute bounded schedule timeouts for poll loops.

## Risks and test signals
Very large millisecond values saturate. Tests should cover zero, small values, and values at or above `MAX_SCHEDULE_TIMEOUT` conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/TimeTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.c

## Purpose
Implements lookup and key comparison for the acknowledgment store map.

## Important APIs and control flow
`AckStoreMap_find` calls the generic `_PointerRBTree_findElem` with a string key and wraps the result in `AckStoreMapIter`. `compareAckStoreMapElems` delegates ordering to `strcmp`.

## State, dependencies, integration
The map itself is a `PointerRBTree` configured by `AckStoreMap_init` in the header. `AcknowledgmentStore` uses it to map ack IDs to `AckStoreEntry` records while threads wait for acknowledgments.

## Risks and test signals
Keys are raw string pointers and must remain valid while in the map. Test finding present/missing ack IDs and duplicate insertion behavior through the header API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.h

## Purpose
Defines the ack ID to wait-state map used by `AcknowledgmentStore`.

## Important APIs and types
`AckStoreEntry` stores a borrowed `ackID`, pointers to the waiting and received `WaitAckMap`s, and a `WaitAckNotification`. Inline helpers initialize, allocate, and free entries. `AckStoreMap` wraps a generic `RBTree`; `AckStoreMap_insert`, `erase`, `find`, and lifecycle helpers provide string-key map behavior.

## State, dependencies, integration
State is an RB tree of `AckStoreEntry` pointers. The map does not own ack ID strings or `WaitAck` records; it only owns the small `AckStoreEntry` allocated for store indexing. It integrates directly with `AcknowledgmentStore_receivedAck`.

## Risks and test signals
`AckStoreEntry_construct` does not check allocation before initialization. Duplicate inserts leak the newly constructed entry unless the caller handles failed insert, and current registration code does not check insert results. Tests should cover duplicate ack IDs and unregister after partial registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMapIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMapIter.h

## Purpose
Provides a typed iterator wrapper over `PointerRBTreeIter` for `AckStoreMap`.

## Important APIs and control flow
`AckStoreMapIter_init` initializes the embedded RB-tree iterator. `AckStoreMapIter_value` returns the current `AckStoreEntry*`. `AckStoreMapIter_end` reports whether iteration is complete.

## State, dependencies, integration
Iterator state is a generic RB-tree iterator cast to typed accessors. It is used by acknowledgment store lookup paths.

## Risks and test signals
Calling `value` on an end iterator dereferences a null tree element through the generic iterator. Tests should assert callers check `end` before value access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMapIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.c

## Purpose
Implements a synchronized acknowledgment rendezvous store. Callers register ack IDs they are waiting for, incoming ack handlers mark arrivals, and waiters block until their wait map is empty or timeout expires.

## Important APIs and control flow
`AcknowledgmentStore_registerWaitAcks` locks the store and inserts one `AckStoreEntry` for each `WaitAck`. `unregisterWaitAcks` removes and frees store entries for outstanding wait IDs. `receivedAck` locks the store, finds an ack ID, locks the notifier mutex, moves the `WaitAck` from the wait map to the received map, broadcasts completion if the wait map becomes empty, then removes the store entry. `waitForAckCompletion` waits on the notifier condition if the wait map is non-empty and returns whether it drained.

## State, dependencies, integration
State is `storeMap` protected by `mutex`; each notifier has its own mutex/condition for wait and received maps. It depends on `AckStoreMap`, `WaitAckMap`, and BeeGFS threading primitives. Network ack handlers feed `receivedAck`; higher-level operations create wait/received maps.

## Risks and test signals
Duplicate ack IDs are not handled robustly. `unregisterWaitAcks` assumes each outstanding key exists in the store; missing entries could lead to value access on an end iterator. Tests should cover ack before timeout, timeout plus unregister, ack racing unregister, duplicate IDs, and lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.h

## Purpose
Declares the synchronized acknowledgment store and lifecycle helpers.

## Important APIs and types
`AcknowledgmentStore` contains an `AckStoreMap` and store mutex. Inline lifecycle helpers initialize/construct/uninit/destruct the store. External operations register wait maps, unregister wait maps, mark received ack IDs, and wait for completion with timeout.

## State, dependencies, integration
The store tracks live wait registrations only in memory. It depends on `Mutex`, `Condition`, `AckStoreMap`, `WaitAckMap`, and typed iterators.

## Risks and test signals
The API requires callers not to access registered wait/received maps until unregister, except under the notifier mutex. Tests should verify lifecycle cleanup with still-registered waits and that no wait maps are touched without proper locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AcknowledgmentStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.c

## Purpose
Implements find, begin, and key comparison for maps of ack IDs to caller-owned `WaitAck` objects.

## Important APIs and control flow
`WaitAckMap_find` wraps generic RB-tree lookup. `WaitAckMap_begin` returns an iterator at the first ordered element using `rb_first`. `compareWaitAckMapElems` orders ack ID strings via `strcmp`.

## State, dependencies, integration
The map state is defined in the header as a generic RB tree. `AcknowledgmentStore` iterates wait maps during registration/unregistration and moves entries between wait and received maps.

## Risks and test signals
As with other string-key tree wrappers, key string lifetimes must outlive tree entries. Test ordered iteration, missing find, and behavior after moving an element between maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.h

## Purpose
Defines wait-ack records, completion notification state, and a string-key map wrapper.

## Important APIs and types
`WaitAckNotification` contains the mutex and condition that synchronize wait and received maps during a wait phase. `WaitAck` stores a borrowed `ackID` and caller private data. `WaitAckMap` wraps `PointerRBTree` with string keys. Inline functions initialize notifications, initialize wait records, manage map lifecycle, insert/erase, get length, and clear.

## State, dependencies, integration
Wait maps and received maps are caller-owned, while `AcknowledgmentStore` temporarily indexes the same `WaitAck` objects in its store map. No `WaitAck` payload data is freed by map clear.

## Risks and test signals
`WaitAckNotification_uninit` uninitializes only the mutex, not the condition, which may be intentional if `Condition` has no uninit requirement but should be checked. Insert failure on duplicate key is silent. Tests should cover map clear not freeing `WaitAck` values and notifier wait/broadcast behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMapIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMapIter.h

## Purpose
Provides typed iterator access for `WaitAckMap`.

## Important APIs and control flow
`WaitAckMapIter_init` wraps `PointerRBTreeIter_init`. `WaitAckMapIter_next` advances to the next RB-tree element. `WaitAckMapIter_key` returns the current ack ID string, `value` returns the current `WaitAck*`, and `end` checks for null.

## State, dependencies, integration
Iterator state is embedded generic RB-tree iterator state. It is used heavily by `AcknowledgmentStore` for registration, unregistration, and ack movement.

## Risks and test signals
Iterators become invalid when their current element is erased unless callers advance or use map-specific patterns carefully. Tests should cover iteration while erasing through the owning map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/WaitAckMapIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyList.h

## Purpose
Defines a linked list of copied `int64_t` values for architectures where storing 64-bit integers directly in pointer slots is unsafe.

## Important APIs and control flow
`Int64CpyList_init` wraps `PointerList_init`. `append` allocates an `int64_t`, stores the value, and appends the pointer. `uninit` and `clear` free every value copy before clearing list nodes. `length` delegates to `PointerList_length`.

## State, dependencies, integration
State is a `PointerList` whose node values own heap-allocated `int64_t` copies. Serialization helpers use this list for int64 list wire formats.

## Risks and test signals
Allocation results are not checked before dereference. Tests should cover append/clear/uninit ownership and behavior on simulated allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyListIter.h

## Purpose
Provides typed iteration over `Int64CpyList`.

## Important APIs and control flow
The iterator wraps `PointerListIter`. `init` starts at the list head, `next` advances, `value` dereferences the stored `int64_t*`, and `end` checks for completion.

## State, dependencies, integration
Iterator state is generic list iterator state. Serialization uses it to emit int64 list contents.

## Risks and test signals
`value` is invalid on end iterators or after current node removal. Tests should verify iteration order and no use-after-free during list clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDList.h

## Purpose
Defines a list of `NumNodeID` values backed by `PointerList` without per-value allocation.

## Important APIs and control flow
`NumNodeIDList_append` casts the numeric ID value through `size_t` into a pointer slot. Lifecycle and clear operations only manage list nodes. `length` delegates to the underlying pointer list.

## State, dependencies, integration
Used by node-sync code to report added/removed node IDs. Values are embedded in pointer fields rather than owned heap objects.

## Risks and test signals
The representation assumes `NumNodeID.value` fits in `size_t`; this is fine for current numeric IDs but should remain explicit. Tests should cover zero IDs and round-trip through iterator value conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDListIter.h

## Purpose
Provides typed iteration over `NumNodeIDList`.

## Important APIs and control flow
Wraps `PointerListIter`; `value` converts the pointer slot back into `NumNodeID`. `init`, `next`, and `end` mirror the generic iterator.

## State, dependencies, integration
Used by `InternodeSyncer` logging of added/removed nodes and any other node-list consumers.

## Risks and test signals
As with pointer-cast value lists, this is not suitable for values wider than pointer size. Tests should verify ordered iteration and correct reconstruction of IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerList.h

## Purpose
Implements the generic doubly linked list used by many BeeGFS kernel containers.

## Important APIs and control flow
`PointerList_init/uninit/clear` manage list nodes. `addHead`, `addTail`, and `append` allocate a `PointerListElem` and link it. Internal helpers support inserting/removing an existing node without freeing it, used by `moveToHead` and `moveToTail`. `removeHead`, `removeTail`, and `removeElem` unlink and free nodes. `getHead`, `getTail`, and `length` expose structure state.

## State, dependencies, integration
The list owns only element nodes, not `valuePointer` payloads. Many wrappers add ownership semantics above it: string-copy and int64-copy lists free payloads; raw string/pointer lists do not.

## Risks and test signals
Allocation failures are not checked. Removing from an empty list is guarded only in debug builds. Moving the sole element removes then re-adds with length transitions. Tests should cover head/tail/middle remove, move operations, clear payload ownership expectations, and failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerListIter.h

## Purpose
Defines the generic iterator for `PointerList`.

## Important APIs and control flow
`PointerListIter_init` starts at the head. `next` advances to `elem->next`. `value` returns the current payload pointer. `end` checks for null. `remove` returns a new iterator pointing after the erased element while deleting the old current node.

## State, dependencies, integration
The iterator stores a list pointer and current element pointer. Component queues use the remove-return pattern while processing mutable queues.

## Risks and test signals
`next` and `value` assume the iterator is not at end. Tests should cover removal of head, tail, middle, and last element while iterating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyList.h

## Purpose
Defines an owning string-copy list built on `StringList`.

## Important APIs and control flow
`StrCpyList_addHead` and `append` allocate a copy of the input C string, then store it in the underlying list. `uninit` and `clear` free all copied strings before clearing list nodes. `length` delegates to `StringList_length`.

## State, dependencies, integration
The list owns copied string payloads. Config loading, string splitting, filters, and serialization use it for mutable lists of independent strings.

## Risks and test signals
Allocation failures are not checked before `memcpy`. Tests should cover copy independence from source buffers, clear/uninit freeing, empty strings, and allocation-failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyListIter.h

## Purpose
Provides typed iteration over owning copied-string lists.

## Important APIs and control flow
Wraps `StringListIter` to return `char*` values. `init`, `next`, `value`, and `end` mirror the underlying iterator.

## State, dependencies, integration
Used by filter parsing and serialization to walk configuration string rows.

## Risks and test signals
Returned strings are owned by the list and become invalid after list clear/uninit. Tests should cover iteration over empty and multi-element lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringList.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringList.h

## Purpose
Defines a non-copying list of `char*` pointers.

## Important APIs and control flow
`StringList_init/uninit/clear` delegate to `PointerList`. `StringList_addHead` and `append` store the provided string pointer without copying. `length` returns node count.

## State, dependencies, integration
The list owns only list nodes; string payload ownership remains with callers. `StrCpyList` layers copying/freeing semantics on top.

## Risks and test signals
Using `StringList` when copied ownership is needed can create dangling pointers. Tests should verify clear does not free payloads and that `StrCpyList` is used for config-loaded strings that need ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringList.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringListIter.h

## Purpose
Provides typed iteration over `StringList`.

## Important APIs and control flow
Wraps `PointerListIter`, returning `char*` values and exposing `init`, `next`, and `end`.

## State, dependencies, integration
Used directly by string list consumers and indirectly by `StrCpyListIter`.

## Risks and test signals
Iterator values are borrowed payload pointers. Tests should cover empty-list end behavior and iteration order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16List.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16List.h

## Purpose
Defines a `uint16_t` value list backed by pointer-slot casts rather than per-value allocation.

## Important APIs and control flow
Lifecycle and clear delegate to `PointerList`. `UInt16List_append` casts the value through `size_t` into a node payload pointer. `length` returns node count.

## State, dependencies, integration
Used for preferred target lists and UInt16 serialization. The list owns nodes only.

## Risks and test signals
This pattern is safe for 16-bit values but not for arbitrary pointer payloads. Tests should cover zero, max `UINT16_MAX`, and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16List.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16ListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16ListIter.h

## Purpose
Provides typed iteration over `UInt16List`.

## Important APIs and control flow
Wraps `PointerListIter`; `value` converts the pointer slot back to `uint16_t`.

## State, dependencies, integration
Used by serialization and target-list consumers.

## Risks and test signals
Call `end` before `value`. Tests should verify max-value round trips through append and iterator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16ListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8List.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8List.h

## Purpose
Defines a `uint8_t` value list backed by pointer-slot casts.

## Important APIs and control flow
`UInt8List_append` stores the byte value in a pointer slot through `size_t`. Lifecycle, clear, and length delegate to `PointerList`.

## State, dependencies, integration
Used by serialization for compact byte lists. The list owns nodes only and does not allocate separate byte payloads.

## Risks and test signals
Tests should cover zero, 255, clear behavior, and deserialization appending exact byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8List.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8ListIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8ListIter.h

## Purpose
Provides typed iteration over `UInt8List`.

## Important APIs and control flow
Wraps `PointerListIter`; `value` converts the pointer slot back to `uint8_t`.

## State, dependencies, integration
Used by UInt8 list deserialization/serialization and consumers of byte-list data.

## Risks and test signals
End iterator value access is invalid. Test ordered byte iteration and max/min values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt8ListIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.c

## Purpose
Implements find and begin operations for integer-key maps backed by `PointerRBTree`.

## Important APIs and control flow
`IntMap_find` casts the integer search key through `size_t` to a pointer key and wraps the matching tree element in `IntMapIter`. `IntMap_begin` starts at the first RB-tree node.

## State, dependencies, integration
The tree state and comparator are set in the header. This map is a utility container for code needing ordered integer keys with pointer values.

## Risks and test signals
Pointer ordering is used for integer comparison through casts. Test negative keys, zero, and large positive keys if callers use signed domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.h

## Purpose
Defines an integer-key map facade over the generic pointer red-black tree.

## Important APIs and types
`IntMap` contains an `RBTree`. Inline lifecycle helpers initialize the generic tree with `PointerRBTree_keyCompare`. `IntMap_insert` stores integer keys directly in pointer slots and stores caller-provided `char*` values without copying. `erase`, `length`, and `clear` delegate to the generic tree.

## State, dependencies, integration
The map owns only tree elements, not value payloads. It is used as a simple utility map where caller ownership is explicit.

## Risks and test signals
Signed integer to pointer casts can be problematic for negative values. Duplicate inserts return false without replacing. Tests should cover value ownership, duplicate keys, and clear semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMapIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMapIter.h

## Purpose
Provides typed iteration over `IntMap`.

## Important APIs and control flow
Wraps `PointerRBTreeIter`; `key` casts the current tree key back to `int`, `value` returns the stored `char*`, and `next` advances in RB-tree order.

## State, dependencies, integration
Iterator state is the generic RB-tree iterator. It is valid until the current tree element is erased.

## Risks and test signals
End iterator dereference is invalid. Tests should cover sorted iteration order and iterator behavior after erasing non-current entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMapIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.c

## Purpose
Implements exported begin/find wrappers for the generic pointer-key red-black tree.

## Important APIs and control flow
`PointerRBTree_find` calls `_PointerRBTree_findElem` and wraps the result in an `RBTreeIter`. `PointerRBTree_begin` finds the first node with `rb_first` and initializes an iterator or end iterator.

## State, dependencies, integration
The generic tree stores `void*` keys/values and a comparator defined at init. Typed maps such as `IntMap`, `StrCpyMap`, `AckStoreMap`, and `WaitAckMap` layer semantics above it.

## Risks and test signals
The generic iterator exposes raw values. Tests should cover empty tree begin, missing find, and sorted begin for each comparator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.h

## Purpose
Defines and mostly implements a generic red-black tree mapping `void*` keys to `void*` values.

## Important APIs and control flow
`PointerRBTree_init` sets an empty `rb_root`, length zero, and comparator. `_PointerRBTree_findElem` descends left/right based on comparator results. `PointerRBTree_insert` walks to an insertion point, rejects duplicate keys, allocates an `RBTreeElem`, links it, colors it, and increments length. `PointerRBTree_erase` finds, erases, frees the element, and decrements length. `clear` repeatedly erases the root. `PointerRBTree_keyCompare` compares raw pointer values.

## State, dependencies, integration
State is an RB root, length, and comparator. The tree owns only `RBTreeElem` nodes; key/value ownership is left to typed wrappers or callers.

## Risks and test signals
Allocation failure is not checked before storing key/value. Pointer comparison is only meaningful for pointer-cast value maps. Tests should cover duplicate rejection, erase missing key, clear with wrapper-owned keys, and allocation-failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTreeIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTreeIter.h

## Purpose
Provides generic in-order iteration over `PointerRBTree`.

## Important APIs and control flow
`PointerRBTreeIter_init` stores the tree and current element. `next` advances with `rb_next` and returns the new element pointer. `key`, `value`, and `end` expose current element state.

## State, dependencies, integration
Used directly by generic callers and wrapped by typed map iterators. Iterator validity depends on the underlying tree not erasing the current element unexpectedly.

## Risks and test signals
`next`, `key`, and `value` require a non-end current element. Tests should validate in-order traversal and safe caller patterns around erase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTreeIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.c -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.c

## Purpose
Implements lookup, begin, and comparison functions for the copied-string map.

## Important APIs and control flow
`StrCpyMap_find` wraps generic RB-tree lookup by string key. `StrCpyMap_begin` starts iteration at `rb_first`. `compareStrCpyMapElems` orders keys using `strcmp`.

## State, dependencies, integration
The owning key/value behavior is implemented in the header. This C file supplies non-inline wrappers needed by users.

## Risks and test signals
Tests should cover lookup by a different string pointer with equal contents, because comparison is content-based.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.h

## Purpose
Defines an owning string-to-string map on top of `PointerRBTree`.

## Important APIs and control flow
`StrCpyMap_insert` allocates copies of both key and value, inserts them, and frees copies on duplicate failure. `StrCpyMap_erase` finds the element, remembers key/value pointers, erases the tree node, then frees both copies. `clear` repeatedly erases root keys until empty. Lifecycle initializes and uninitializes the generic tree.

## State, dependencies, integration
The map owns copied key and value strings plus generic tree nodes. It is a utility for configuration and metadata-style string maps.

## Risks and test signals
Allocation failures are not checked before `memcpy`. `StrCpyMap_uninit` calls `StrCpyMap_clear` and then `PointerRBTree_uninit`, whose clear is harmless on empty but redundant. Tests should cover duplicate insert, erase missing, clear freeing all strings, and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMapIter.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMapIter.h

## Purpose
Provides typed iteration over `StrCpyMap`.

## Important APIs and control flow
Wraps `PointerRBTreeIter`; `key` and `value` return the copied strings, `next` advances, and `end` checks completion.

## State, dependencies, integration
Returned key/value pointers are owned by the map and valid until erasure or clear.

## Risks and test signals
Tests should validate sorted string order and ensure callers do not retain returned pointers after erasing map entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMapIter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/Int64CpyVec.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/Int64CpyVec.h

## Purpose
Defines an append-only vector facade for copied int64 values, combining list ownership with array indexing.

## Important APIs and control flow
`init` initializes the underlying `Int64CpyList` and allocates an initial pointer array of four. `append` appends to the list, doubles the pointer array when needed, and stores the newest list element's value pointer at the matching index. `at` returns the dereferenced value. `clear` clears the list but does not reset or rebuild the vector array.

## State, dependencies, integration
State includes the owning list plus `int64_t** vecArray` and capacity. Serialization reuses list-compatible wire format while consumers can index values.

## Risks and test signals
After `clear`, old array entries point to freed values until new appends overwrite them; `length` prevents valid access but stale pointers remain. Allocation failures are unchecked. Tests should cover growth, clear-then-append, bounds checks in debug builds, and uninit freeing both array and list values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/Int64CpyVec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/StrCpyVec.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/StrCpyVec.h

## Purpose
Defines an append-only vector facade over an owning copied-string list.

## Important APIs and control flow
`init` initializes `StrCpyList` and a four-slot `char**` array. `append` copies a string into the list, grows the array by doubling when length exceeds capacity, and stores the latest copied string pointer at its index. `at` returns the indexed string. `clear` clears list contents.

## State, dependencies, integration
State is an owning string list plus an index array. Serialization treats it as list-compatible; indexed users use `at`.

## Risks and test signals
Array entries become stale after `clear` until overwritten. Allocation failures are unchecked. Tests should cover growth, copy independence, list/vector wire compatibility, and bounds behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/StrCpyVec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt16Vec.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt16Vec.h

## Purpose
Defines an indexed append-only vector for `uint16_t` values while retaining list compatibility.

## Important APIs and control flow
`init` initializes the underlying `UInt16List` and a four-element array. `append` appends to the list, grows the array by doubling when needed, and writes the new value at index `length - 1`. `at` returns an indexed value. `clear` clears the list but keeps the allocated vector array.

## State, dependencies, integration
State is a pointer-cast value list plus a `uint16_t*` index array. Used by serialization and preferred-target style arrays.

## Risks and test signals
After `clear`, array contents are stale but inaccessible through valid length. Allocation failures are unchecked. Tests should cover capacity growth, max value, clear/reuse, and list/vector serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt16Vec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt8Vec.h -->
# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt8Vec.h

## Purpose
Defines an indexed append-only vector for `uint8_t` values while keeping list-compatible storage semantics.

## Important APIs and control flow
`init` allocates an initial four-byte array. `append` appends the byte to the underlying `UInt8List`, grows the array by doubling when needed, and writes the value at the last index. `at`, `length`, `clear`, and `uninit` provide access and cleanup.

## State, dependencies, integration
State is a `UInt8List`, byte array, and array capacity. Serialization code reuses UInt8 list wire format for vectors.

## Risks and test signals
Unchecked allocation and stale array contents after clear are the main risks. Tests should cover byte min/max, growth, clear/reuse, and deserialization into a vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt8Vec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/AckManager.c -->
# sources/distributed-fs/beegfs/client_module/source/components/AckManager.c

## Purpose
Implements the reliable TCP-based acknowledgment sender thread for metadata server acks queued by client operations.

## Important APIs and control flow
`AckManager_init` initializes the thread, app/config pointers, a 4096-byte vmalloc serialization buffer, queue mutex/condition, and pointer queue. `_AckManager_requestLoop` waits up to 2.5 seconds for entries and then processes the queue. `__AckManager_processAckQueue` locks the queue, references the target metadata node, serializes `AckMsgEx`, temporarily unlocks during socket acquisition/send, retries once, removes later queued acks for the same node if communication ultimately fails, frees the current entry, and advances safely with `PointerListIter_remove`. `AckManager_addAckToQueue` copies node ID and ack ID, appends an entry, and signals the condition.

## State, dependencies, integration
State is a thread, app/config pointers, static send buffer, mutex/condition, and `PointerList` of `AckQueueEntry`s. It depends on `NodeStoreEx`, `NodeConnPool`, `AckMsgEx`, `Socket_send_kernel`, and `StringTk`.

## Risks and test signals
Entries are dropped after send failure to avoid blocking later acks indefinitely. Queue uninit frees pending entries but assumes the thread is stopped. Tests should cover retry, missing node removal, serialization failure, concurrent enqueue while processing, and queue-size locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/AckManager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/AckManager.h -->
# sources/distributed-fs/beegfs/client_module/source/components/AckManager.h

## Purpose
Declares the ack manager thread and queue structures.

## Important APIs and types
`AckQueueEntry` stores creation time, metadata node ID, and copied ack ID. `AckManager` embeds `Thread`, app/config pointers, vmalloc message buffer, queue mutex/condition, and a `PointerList` queue. Exports lifecycle, request-loop, processing helpers, queue add, node-removal helper, entry-free helper, and queue-size getter.

## State, dependencies, integration
The queue is protected by `ackQueueMutex`; only the manager removes entries to preserve iterator assumptions. Integrated with metadata operations that require reliable ack transmission.

## Risks and test signals
The header includes itself (`<components/AckManager.h>`), relying on include guards to avoid recursion. Tests should verify queue ownership and that `ackID` is always copied/freed exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/AckManager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.c -->
# sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.c

## Purpose
Implements the UDP datagram listener/sender thread for management heartbeats, node updates, locking notifications, target-state refresh, and other lightweight messages.

## Important APIs and control flow
`__DatagramListener_run` allocates NUMA-local buffers and enters `__DatagramListener_listenLoop`. The loop receives datagrams with timeout, ignores empty/timeout cases, rejects localhost-origin datagrams on the same UDP port, constructs a `NetMessage`, validates header length/sequence, and dispatches allowed message types through `processIncoming`. Ack messages are explicitly ignored to avoid noisy false errors. `__DatagramListener_initSock` creates a UDP socket, enables broadcast, sets receive buffer size, and binds. `DatagramListener_sendMsgToNode` serializes a message and sends it to every standard NIC of a node that passes `NetFilter`. Send calls are mutex-serialized through header inlines.

## State, dependencies, integration
State includes UDP socket, local node, net filter, send/receive buffers, UDP port, and send mutex. It integrates with `InternodeSyncer` for heartbeat send/receive and with message handlers for cluster updates.

## Risks and test signals
`NetMessageFactory_createFromBuf` is assumed to return a non-null message object. Localhost filtering depends on local NIC list and UDP port. Tests should cover invalid headers, ignored ack messages, allowed/disallowed message types, net-filtered sends, bind failure cleanup, and self-datagram suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.h -->
# sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.h

## Purpose
Declares the UDP datagram listener component and send helpers.

## Important APIs and types
`DatagramListener` embeds `Thread` and stores app, receive buffer, local node, net filter, UDP socket/port, send buffer, and send mutex. Inline lifecycle helpers initialize the thread, socket, filter pointers, and mutex; destructors close the socket and free buffers. Inline `DatagramListener_sendto_kernel` serializes send access with `sendMutex`, and `sendtoIP_kernel` builds a sockaddr from IP/port.

## State, dependencies, integration
The component references app-owned local node and net filter and owns its socket and buffers. It is used by `InternodeSyncer` and message processing paths.

## Risks and test signals
Buffers are allocated in the run method, so send paths should not use `sendBuf` before the thread initializes it unless message send allocates its own buffer. Tests should cover initialization error paths and destruction when socket or buffers are null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/Flusher.c -->
# sources/distributed-fs/beegfs/client_module/source/components/Flusher.c

## Purpose
Implements the background buffered-cache flusher thread for files that need asynchronous cache flush retries.

## Important APIs and control flow
`Flusher_init` initializes the thread. `_Flusher_requestLoop` wakes every five seconds until termination and calls `__Flusher_flushBuffers`. The flush loop removes inodes from `InodeRefStore`, calls `FhgfsOpsHelper_flushCacheNoWait`, drops references on success, re-adds inodes when busy or retryable, performs a final forced flush for unrecoverable errors on closed files, logs discarded buffers, and respects termination between items.

## State, dependencies, integration
State is only the thread and app pointer. It integrates with `InodeRefStore`, `FhgfsInode`, and filesystem helper flush operations.

## Risks and test signals
Reference handling is central: success and discard paths call `iput`, while re-add paths transfer or drop references through `InodeRefStore_addOrPutInode`. Tests should cover busy lock retry, communication failure on open versus closed files, final flush failure logging, and shutdown mid-queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/Flusher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/Flusher.h -->
# sources/distributed-fs/beegfs/client_module/source/components/Flusher.h

## Purpose
Declares the asynchronous cache flusher component.

## Important APIs and types
`Flusher` embeds `Thread` and stores `App*`. Exports lifecycle functions, request loop, run function, and `__Flusher_flushBuffers`.

## State, dependencies, integration
The component uses `InodeRefStore` through the app at runtime. It exists to keep flush retry delays out of foreground filesystem operations.

## Risks and test signals
The header documents the reason for a dedicated thread: retries while a server is unreachable should not block other threads. Tests should verify thread lifecycle and app/ref-store interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/Flusher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.c -->
# sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.c

## Purpose
Implements the main client background synchronization thread for management discovery, registration, topology refresh, target states, delayed remote cleanup, NIC changes, and idle connection cleanup.

## Important APIs and control flow
Startup initializes app stores, delayed queues, force-state mutex, and target-state timeout. `__InternodeSyncer_run` performs management init, enters the periodic request loop, signals init completion on exit, and unregisters if registered. `_InternodeSyncer_requestLoop` runs timed tasks: retry management init, check network changes and force reregistration, reregister heartbeats, download/sync nodes and target mappings, update metadata/storage states and buddy groups, retry delayed close/unlock queues, and drop idle connections. Management init waits for heartbeat via UDP, downloads topology/state, registers over request/response, and repeats downloads to avoid notification races. Registration updates local numeric node ID, management gRPC port, and fs UUID.

## State, dependencies, integration
State includes management/meta/storage node stores, datagram listener, `mgmtInitDone` condition, `nodeRegistered`, forced target-state update flag, last successful state update time, and three delayed operation queues. It integrates with `NodesTk`, `MessagingTk`, `DatagramListener`, `TargetMapper`, `TargetStateStore`, `MirrorBuddyGroupMapper`, `FhgfsOpsRemoting`, and `NodeConnPool`.

## Risks and test signals
Target-state failure transitions all states to probably-offline, then offline after configured timeout. Delayed queues copy `EntryInfo` and file handle IDs and retry only communication errors. Tests should cover management absent/present, hostname resolution failure, registration response with zero ID, NIC list change, forced state update, state sync timeout, delayed close/unlock retry/removal, and shutdown deregistration failure logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.h -->
# sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.h

## Purpose
Declares the internode synchronization component, delayed-operation entry types, and force-update controls.

## Important APIs and types
Delayed entries store `Time ageT`, duplicated `EntryInfo`, copied file handle IDs, and operation-specific fields: close access flags, append-lock cleanup, max target index, optional file event; entry unlock client FD; range unlock owner PID. `InternodeSyncer` embeds `Thread`, app/config, datagram listener, node stores, management init condition, registration flag, forced target-state flag, state-update timing, and three mutex-protected `PointerList` queues. Public APIs include lifecycle, waiting for management init, adding delayed close/entry-unlock/range-unlock work, queue-size getters, and force-target-state update setters.

## State, dependencies, integration
The header ties together networking, target state, file-event, remoting IO, and threading abstractions. Queue comments make the ownership model explicit: the syncer removes entries to keep iterators valid.

## Risks and test signals
`mgmtInitDone` means initialization phase finished, not necessarily that registration succeeded forever. `InternodeSyncer_setForceTargetStatesUpdate` is edge-triggered and consumed by the loop. Tests should validate delayed entry copying/freeing and forced-update reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/InternodeSyncer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.c -->
# sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.c

## Purpose
Implements asynchronous read/write page work items for BeeGFS chunk page vectors using a kernel workqueue.

## Important APIs and control flow
`RWPagesWork_initworkQueue`, `destroyWorkQueue`, and `flushWorkQueue` manage the global workqueue. `RWPagesWork_init` records app/inode/page vector/RW type, references the file handle with `_RWPagesWork_initReferenceFile`, fills `RemotingIOInfo`, and initializes `kernelWork`. `RWPagesWork_createQueue` constructs a work item, queues it, and marks all pages failed if construction or queueing fails. `RWPagesWork_process` casts the `work_struct` to `RWPagesWork` because it is the first struct member, then `RWPagesWork_processQueue` calls `FhgfsOpsRemoting_rwChunkPageVec`, logs result, and destructs the work item.

## State, dependencies, integration
Global state is `rwPagesWorkQueue`. Each work item owns the page vector and a referenced file handle until destruction. It depends on `FhgfsInode`, `FhgfsOpsPages`, `FhgfsOpsRemoting`, and kernel workqueue APIs.

## Risks and test signals
The cast from `work_struct*` to `RWPagesWork*` relies on `kernelWork` being the first member. Queueing before global init would dereference a null workqueue. Tests should cover read/write failure marking, reference acquire/release, queue failure, workqueue flush/destroy, and layout assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.h -->
# sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.h

## Purpose
Declares the asynchronous page read/write work item and workqueue lifecycle.

## Important APIs and types
`RWPagesWork` stores `work_struct`, app, page vector, remoting IO info, file handle type, RW type, and inode. Inline constructor allocates and initializes a work item, marks pages failed if initialization cannot reference the file, and returns null. `RWPagesWork_uninit` destroys the page vector and releases the inode file handle. Public functions create queued work, initialize/destroy/flush the global workqueue, and process work callbacks.

## State, dependencies, integration
The work item bridges the VM/page layer and BeeGFS remoting. It owns page-vector cleanup and file-handle release.

## Risks and test signals
Destructing a partially initialized work item after `RWPagesWork_init` failure can call uninit paths that assume fields are valid; current flow calls `RWPagesWork_destruct` after failed init. Tests should exercise reference failure with instrumentation and verify no double page failure/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/components/worker/RWPagesWork.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.c -->
# sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.c

## Purpose
Implements debugfs fault-injection attributes for BeeGFS debug builds with kernel fault injection enabled.

## Important APIs and control flow
Under `BEEGFS_DEBUG && CONFIG_FAULT_INJECTION`, the file declares fault attributes for readpage, writepage, cache-bypass forcing, communication timeouts, and read/write data timeout injection. `beegfs_fault_inject_init` creates `/sys/kernel/debug/<module>/fault`, registers each fault attribute with `fault_create_debugfs_attr`, and removes the debugfs tree on failure. `beegfs_fault_inject_release` releases optional dentry names on kernels that need it and removes the debugfs tree recursively.

## State, dependencies, integration
State is static `debug_dir`, `fault_dir`, and generated `fault_attr` objects. Other code uses `BEEGFS_SHOULD_FAIL` from the header to trigger injected failures.

## Risks and test signals
Initialization failure after some attributes are created relies on recursive debugfs cleanup. Release should be safe after successful init. Tests require debug kernel configs; verify debugfs entries appear, configured probabilities affect call sites, and cleanup removes all entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.h -->
# sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.h

## Purpose
Declares BeeGFS fault-injection hooks with no-op fallbacks for non-debug or non-fault-injection builds.

## Important APIs and types
When enabled, includes kernel fault injection, requires debugfs and fault-injection debugfs configs, declares `fault_attr` externs, defines `BEEGFS_SHOULD_FAIL(name, size)` as `should_fail`, and exports init/release. When disabled, `BEEGFS_SHOULD_FAIL` is constant false and init/release are inline no-ops.

## State, dependencies, integration
The header is included by code paths that need conditional failure injection without carrying config-specific preprocessor logic at each call site.

## Risks and test signals
Builds with `BEEGFS_DEBUG` and fault injection but missing debugfs configs intentionally fail preprocessing. Tests should compile both enabled and disabled configurations and validate call sites remain type-correct when the macro collapses to false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/client_module/source/fault-inject/fault-inject.h -->
