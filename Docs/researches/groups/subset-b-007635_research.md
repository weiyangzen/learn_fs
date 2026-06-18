# subset-b-007635 Research

Grouped research report for the LizardFS protocol, tools, unittest, and uraft files in this work item. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocl_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/cstocl_unittest.cc

Purpose: Exercises chunkserver-to-client packet helpers from `protocol/cstocl.h`, focused on read data prefix handling and simple status replies. The tests build serialized buffers, verify packet type headers, strip headers, and deserialize back into typed fields.

Important APIs/types/functions: GoogleTest cases `ReadData`, `ReadStatus`, and `WriteStatus`; `cstocl::readData::serializePrefix`/`deserializePrefix`; `cstocl::readStatus`; `cstocl::writeStatus`; `LIZARDFS_DEFINE_INOUT_PAIR`; `verifyHeader`; `removeHeaderInPlace`.

Control flow: Each test defines input/output pairs, serializes into a `std::vector<uint8_t>`, optionally appends CRC and block data, verifies the LizardFS packet type, removes the header, then deserializes and compares values. `ReadData` deliberately tests prefix parsing rather than full block payload parsing.

State and persistence: No persistent state. Buffers are in-memory packet fixtures; the only state mutation is replacement of output variables by deserialization.

Dependencies and integration: Depends on packet constants from `MFSCommunication.h`, block size constants, CRC serialization, and unittest packet helpers. It validates contracts consumed by clients reading from chunkservers.

Risks and test signals: Gives good coverage for field order and packet type, but only covers selected cstocl messages. It does not validate malformed packets, short payloads, or actual data block CRC verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocl_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocs.h -->
# sources/distributed-fs/lizardfs/src/protocol/cstocs.h

Purpose: Defines chunkserver-to-chunkserver wire helpers for asking another chunkserver about chunk block availability and returning that availability/status. It supports both legacy standard/XOR chunk part encoding and newer `ChunkPartType` encoding for erasure-coded chunks.

Important APIs/types/functions: `cstocs::getChunkBlocks::{serialize,deserialize}`; `cstocs::getChunkBlocksStatus::{serialize,deserialize}`; packet versions `kStandardAndXorChunks = 0` and `kECChunks = 1`; packet types `LIZ_CSTOCS_GET_CHUNK_BLOCKS` and `LIZ_CSTOCS_GET_CHUNK_BLOCKS_STATUS`.

Control flow: Callers choose overloads by `legacy::ChunkPartType` or `ChunkPartType`. Serializers emit versioned LizardFS packets; deserializers first verify the expected packet version and then fully deserialize chunk id, version, part type, and for responses block count/status.

State and persistence: Stateless inline serialization layer. It only transforms typed fields into message buffers and back.

Dependencies and integration: Uses `common/chunk_part_type.h`, `protocol/MFSCommunication.h`, and `protocol/packet.h`. It integrates with chunk repair/replication paths that need per-part block information from peer chunkservers.

Risks and test signals: Version mismatch throws `IncorrectDeserializationException`, protecting against decoding legacy and EC layouts interchangeably. Risks are wire compatibility if field order or version constants change; `cstocs_unittest.cc` covers the EC overloads for both request and response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocs_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/cstocs_unittest.cc

Purpose: Unit tests for chunkserver-to-chunkserver packet serialization in `cstocs.h`. It validates the EC `ChunkPartType` paths for block requests and block-status replies.

Important APIs/types/functions: Test cases `GetChunkBlocks` and `GetChunkBlocksStatus`; `cstocs::getChunkBlocks`; `cstocs::getChunkBlocksStatus`; constants from `unittests/chunk_type_constants.h`; packet helpers `verifyHeader`, `removeHeaderInPlace`.

Control flow: The tests serialize known chunk ids, versions, chunk part types, block counts, and status bytes, then remove packet headers and deserialize into output variables. `LIZARDFS_VERIFY_INOUT_PAIR` asserts round-trip equality.

State and persistence: No persistence; all state is local test data in vectors and scalar pairs.

Dependencies and integration: Depends on GTest, LizardFS packet helpers, and chunk type constants. It supports confidence in peer chunkserver replication/repair messaging.

Risks and test signals: Positive round-trip tests catch field-order and version errors for the EC overloads. They do not exercise the legacy overloads, corrupted buffers, or version rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstocs_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstoma.h -->
# sources/distributed-fs/lizardfs/src/protocol/cstoma.h

Purpose: Defines chunkserver-to-master packet contracts for chunkserver registration, space/label reporting, chunk lifecycle status replies, chunk damage/loss reporting, and load status. It is a macro-heavy header that centralizes the wire format for chunkserver reports to the master.

Important APIs/types/functions: `cstoma::overwriteStatusField`; packet families `chunkNew`, `registerHost`, `registerChunks`, `registerSpace`, `registerLabel`, `setVersion`, `deleteChunk`, `createChunk`, `truncate`, `duplicateChunk`, `duptruncChunk`, `replicateChunk`, `chunkDamaged`, `chunkLost`, and `status`. Multiple families expose legacy standard/XOR versions and EC versions.

Control flow: `LIZARDFS_DEFINE_PACKET_SERIALIZATION` generates build/serialize/deserialize helpers for each message. Callers select overloads through field types and packet versions. `overwriteStatusField` mutates an already serialized packet status byte using a fixed offset that assumes chunk id and chunk type precede status.

State and persistence: Stateless serialization except for explicit in-place buffer mutation in `overwriteStatusField`. No disk persistence; messages report master-visible chunkserver state such as chunks, space, and failures.

Dependencies and integration: Depends on chunk type wrappers, chunk-with-version structs, `chunks_with_type`, serialization macros, and packet constants. It is integrated by chunkserver code that announces inventory and operation results to the master.

Risks and test signals: The fixed status offset is fragile and depends on field order and serialized size of `ChunkPartType`; comments on `replicateChunk` warn status must remain the third field. Tests cover registration, status overwrite, register-space, lifecycle replies, replication, and load status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstoma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstoma_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/cstoma_unittest.cc

Purpose: Exercises selected chunkserver-to-master packet helpers from `cstoma.h`, including the special in-place status overwrite helper.

Important APIs/types/functions: Test cases `OverwriteStatusField`, `RegisterHost`, `RegisterChunks`, `RegisterSpace`, `SetVersion`, `DeleteChunk`, `Replicate`, and `Status`; `cstoma::overwriteStatusField`; chunk type constants; `LIZARDFS_VERIFY_INOUT_PAIR`.

Control flow: Tests serialize a packet, validate its type header, strip the header, and deserialize the payload into output variables. The overwrite test mutates a serialized `setVersion` status byte before deserialization to prove the hard-coded status offset is correct for that layout.

State and persistence: Uses only local vectors and scalar test variables. It models wire state but does not touch network sockets or persistent metadata.

Dependencies and integration: Depends on GTest, `common/mfserr.h` for status codes, chunk constants, and generic packet test utilities. It validates contracts used by chunkservers reporting to masters.

Risks and test signals: Strong signal for selected packet field order and EC chunk type round trips. Coverage is not exhaustive for all packet families in `cstoma.h`, and negative validation of wrong versions/short payloads is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/cstoma_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/directory_entry.h -->
# sources/distributed-fs/lizardfs/src/protocol/directory_entry.h

Purpose: Defines serializable directory listing entries used in master-to-client getdir responses. It keeps both a legacy format and a newer indexed format.

Important APIs/types/functions: `legacy::DirectoryEntry` with `inode`, `name`, and `Attributes`; non-legacy `DirectoryEntry` with `index`, `next_index`, `inode`, `name`, and `Attributes`; `LIZARDFS_DEFINE_SERIALIZABLE_CLASS`.

Control flow: There is no executable control flow beyond generated serialization methods. Consumers deserialize vectors of entries from packet payloads.

State and persistence: Represents transient directory entries in network messages. It mirrors metadata attributes but is not a persistence format by itself.

Dependencies and integration: Depends on `common/attributes.h` and serialization macros. Used by `matocl::fuseGetDirLegacy` and `matocl::fuseGetDir` responses in `matocl.h`.

Risks and test signals: Compatibility risk is between legacy and indexed response versions; callers must select the correct packet version before deserializing. No direct unit test in this subset targets this struct alone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/directory_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/input_packet.h -->
# sources/distributed-fs/lizardfs/src/protocol/input_packet.h

Purpose: Provides `InputPacket`, a small state machine used by servers to incrementally read a packet header and payload from a socket while enforcing a maximum payload length.

Important APIs/types/functions: `InputPacketTooLongException`; constructor with `maxPacketSize`; `reset`; `bytesToBeRead`; `pointerToBeReadInto`; `increaseBytesRead`; `hasHeader`; `getHeader`; `hasData`; `getData`.

Control flow: Before the header is complete, callers read into the fixed header buffer. Once `increaseBytesRead` reaches `PacketHeader::kSize`, the header is deserialized, length is checked against `maxPacketSize_`, and `data_` is resized to the payload length. Subsequent reads fill `data_`; `hasData` becomes true when no bytes remain.

State and persistence: Maintains in-memory read state: serialized header bytes, payload buffer, byte count, and max length. It is reset between packets and has no persistence.

Dependencies and integration: Uses `protocol/packet.h`, common exception and assertion infrastructure. It is suitable for event-loop socket readers that need a stable pointer/count pair for `read`.

Risks and test signals: The caller must call `increaseBytesRead` only after successful reads and must handle zero-length reads externally. `getHeader` aborts on impossible deserialization failure. No direct unit test in this subset covers partial-read edge cases or packet-too-long behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/input_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/lock_info.h -->
# sources/distributed-fs/lizardfs/src/protocol/lock_info.h

Purpose: Defines serializable lock-related constants and structures shared by FUSE lock operations and lock management packets.

Important APIs/types/functions: Lock flags `kUnlock`, `kShared`, `kExclusive`, `kInterrupt`, `kNonblock`, `kRelease`; enum class `lzfs_locks::Type`; serializable class `lzfs_locks::Info`; structs `InterruptData` and `FlockWrapper`.

Control flow: No runtime control flow beyond generated serialization. `FlockWrapper` captures Linux `struct flock` fields except `l_whence`, which FUSE normalizes to `SEEK_SET`.

State and persistence: Represents transient lock state on the wire: owner, inode, session id, range, type, request id, and flock fields. It is not a durable lock table implementation.

Dependencies and integration: Used by `matocl` lock responses including `fuseGetlk`, `manageLocksList`, and likely matching `cltoma` requests. It depends on serialization macros.

Risks and test signals: Wire compatibility depends on fixed integer widths and field ordering. Sign handling for offsets is preserved in `FlockWrapper`, but consumers must interpret zero length and inclusive/exclusive range semantics consistently. No direct tests in this subset isolate lock serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/lock_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocl.h -->
# sources/distributed-fs/lizardfs/src/protocol/matocl.h

Purpose: Central master-to-client protocol header. It defines versioned responses for FUSE operations, quota/goal/eattr/trash tools, chunk and tape information, admin commands, metadata server status, lock management, directory listings, task control, and chunk read/write location replies.

Important APIs/types/functions: Packet families include `updateCredentials`, `fuseMknod`, `fuseMkdir`, ACL get/set/delete, quota get/set/delete, `fuseGetGoal`, `fuseSetGoal`, `listGoals`, `chunksHealth`, `cservList`, `metadataserversList`, `chunksInfo`, admin responses, `tapeInfo`, `listTapeservers`, truncate and lock responses, `wholePathLookup`, `recursiveRemove`, `fuseGetDir`, reserved/trash listings, `listTasks`, `stopTask`, `requestTaskId`, `snapshot`, `listDefectiveFiles`, `fuseReadChunk`, `fuseWriteChunk`, and `fuseWriteChunkEnd`.

Control flow: Macro-generated helpers serialize and deserialize typed payloads. Several message families have status and success response versions; callers inspect `PacketVersion` first and then select the matching deserialize overload. Read/write chunk helpers are hand-written to hide message id during deserialization and support legacy server lists and EC-aware server lists.

State and persistence: Stateless serialization definitions. The payloads convey master state such as metadata version, quota entries, directory entries, chunk locations, tape copies, and task ids, but the header does not store state.

Dependencies and integration: Pulls in many common serializable types, including ACLs, attributes, chunk addresses, quota structs, lock info, directory entries, job info, metadata server entries, and tape info. It is consumed by FUSE clients, admin tools, and `src/tools` commands through `ServerConnection`.

Risks and test signals: Biggest risks are version drift, overload ambiguity, and status-vs-response decoding mistakes. Constants such as `chunksInfo::kMaxNumberOfResultEntries` and `fuseGetDir::kMaxNumberOfDirectoryEntries` limit response sizing. `matocl_unittest.cc` covers chunk read/write variants, chunk health, and ACL packets, while tools exercise quota/goal/task packets indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocl_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/matocl_unittest.cc

Purpose: Unit tests for selected master-to-client packet helpers, mainly chunk read/write responses, chunk health state, and ACL-related responses.

Important APIs/types/functions: Tests `FuseReadChunkData`, `FuseReadChunkStatus`, `FuseWriteChunkData`, `FuseWriteChunkStatus`, `FuseWriteChunkEnd`, `XorChunksHealth`, `FuseDeleteAcl`, `FuseGetAclStatus`, `FuseGetAclResponse`, and `FuseSetAcl`.

Control flow: Each packet test constructs a payload, verifies the header type, removes the header, verifies the packet version when meaningful, deserializes fields, and asserts round-trip equality. `XorChunksHealth` populates availability and replication state across goals and part counts, serializes it, and compares per-goal/per-part counters after deserialization.

State and persistence: Test-only in-memory state. No socket, filesystem, or metadata persistence.

Dependencies and integration: Depends on chunk address/type structures, ACL classes, replication/availability state classes, GTest, and shared packet test helpers. It protects critical client-side decoding of master responses.

Risks and test signals: Good positive coverage for EC chunk server lists and ACL serialization. It does not cover most of the large `matocl.h` packet surface, wrong-version rejection, or malformed responses. There is a minor copy/paste signal in the write-status version check using the read chunk status constant, currently equal in value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocl_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocs.h -->
# sources/distributed-fs/lizardfs/src/protocol/matocs.h

Purpose: Defines master-to-chunkserver command packets for chunk lifecycle operations: set version, delete, create, truncate, duplicate, duplicate-and-truncate, and replicate.

Important APIs/types/functions: Packet families `matocs::setVersion`, `deleteChunk`, `createChunk`, `truncateChunk`, `duplicateChunk`, `duptruncChunk`, `replicateChunk`; versions `kStandardAndXorChunks` and `kECChunks`; `replicateChunk::deserializePartial`.

Control flow: Serializers choose legacy or EC layout by chunk type. Deserializers verify version and fully consume buffers. `deserializePartial` decodes the fixed prefix of a replicate request and returns a pointer to the source list payload for code that wants to parse sources separately.

State and persistence: Stateless wire helpers. The messages command chunkserver state changes but do not persist anything directly.

Dependencies and integration: Depends on `common/chunk_type_with_address.h`, `protocol/packet.h`, and serialization macros. Used by master scheduling code to tell chunkservers how to mutate chunk replicas.

Risks and test signals: These operations can cause data movement or deletion, so field order and version correctness are high risk. Partial deserialization has pointer lifetime and buffer-layout assumptions. `matocs_unittest.cc` covers set-version, delete, and replicate EC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocs_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/matocs_unittest.cc

Purpose: Tests representative master-to-chunkserver packet serialization in `matocs.h`.

Important APIs/types/functions: Tests `SetVersion`, `DeleteChunk`, and `Replicate`; `matocs::setVersion`, `matocs::deleteChunk`, `matocs::replicateChunk`; `ChunkTypeWithAddress` vectors for replication sources.

Control flow: Tests serialize EC chunk commands, verify headers and versions where checked, remove headers, deserialize, and compare inputs to outputs. The replicate test includes multiple server addresses and chunk part types.

State and persistence: No persistence; local packet fixtures only.

Dependencies and integration: Uses GTest, packet helpers, and chunk type constants. Validates commands that master scheduling sends to chunkservers.

Risks and test signals: Positive coverage catches basic field-order regressions for critical commands. It does not cover all lifecycle command families, legacy overloads, partial replicate decoding, or error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matocs_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matoml.h -->
# sources/distributed-fs/lizardfs/src/protocol/matoml.h

Purpose: Defines master-to-metalogger or master-to-shadow packets for shadow registration responses, changelog apply errors, and session termination.

Important APIs/types/functions: `matoml::registerShadow` with status and response versions; `matoml::changelogApplyError`; `matoml::endSession`.

Control flow: Macro-generated helpers serialize status-only registration failures or successful responses containing package version and metadata version. Changelog errors carry a status byte; end session has no payload.

State and persistence: Stateless wire definitions. Payloads reflect metadata replication state but do not persist data directly.

Dependencies and integration: Depends on `protocol/packet.h` and serialization macros. It pairs with metalogger/shadow registration messages from `mltoma.h`.

Risks and test signals: Version handling is the main compatibility risk. No direct unit test in this subset covers these packets, so regressions may surface only in integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matoml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matots.h -->
# sources/distributed-fs/lizardfs/src/protocol/matots.h

Purpose: Defines master-to-tapeserver packets for tapeserver registration responses and tape file placement instructions.

Important APIs/types/functions: `matots::registerTapeserver` status and response packet versions; `matots::putFiles` carrying `std::vector<TapeKey>`.

Control flow: Registration can return a status-only failure or a response containing master version. `putFiles` sends a vector of tape keys for files that the tapeserver should place/store.

State and persistence: Stateless serialization; it conveys tape archive work and registration state but does not manage tape state itself.

Dependencies and integration: Uses packet serialization macros and `TapeKey` through included common headers. It integrates with tapeserver/master tape-copy coordination.

Risks and test signals: Main risks are missing direct tests and vector size/format compatibility for tape contents. Consumers must inspect packet version before decoding registration responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/matots.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/mltoma.h -->
# sources/distributed-fs/lizardfs/src/protocol/mltoma.h

Purpose: Defines metalogger/shadow-to-master packets for shadow registration, changelog apply errors, and publishing the client-facing master port.

Important APIs/types/functions: `mltoma::registerShadow` with version, timeout, and metadata version; `mltoma::changelogApplyError`; `mltoma::matoclport`.

Control flow: Macro-generated helpers encode sender state for the master. Registration announces client version, desired timeout, and known metadata version; later packets report apply errors or matocl port.

State and persistence: Stateless wire helpers. Messages describe replication metadata state and port state.

Dependencies and integration: Uses serialization macros and packet constants. It complements `matoml.h` response packets in master/metalogger communication.

Risks and test signals: No direct tests in this subset. Compatibility depends on fixed field order and version semantics matching master-side handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/mltoma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/named_inode_entry.h -->
# sources/distributed-fs/lizardfs/src/protocol/named_inode_entry.h

Purpose: Defines a small serializable `{name, inode}` tuple for responses that list special named inode entries.

Important APIs/types/functions: `NamedInodeEntry` generated by `LIZARDFS_DEFINE_SERIALIZABLE_CLASS` with `std::string name` and `uint32_t inode`.

Control flow: No explicit runtime flow. Generated serialization methods are used inside vector payloads.

State and persistence: Represents transient listings, not durable metadata.

Dependencies and integration: Used by `matocl::fuseGetReserved` and `matocl::fuseGetTrash` responses. Depends only on serialization macros and platform header.

Risks and test signals: Low complexity, but string encoding and vector bounds depend on common serialization. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/named_inode_entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/packet.cc -->
# sources/distributed-fs/lizardfs/src/protocol/packet.cc

Purpose: Implements `receivePacket`, a blocking helper that reads a full LizardFS/MooseFS packet from a TCP socket into a header and data buffer.

Important APIs/types/functions: `receivePacket(PacketHeader&, std::vector<uint8_t>&, int sock, uint32_t timeout_ms)`; `tcptoread`; `tcpclose`; `deserializePacketHeader`; `kMaxDeserializedBytesCount`.

Control flow: The function asserts the output data buffer is empty, reads exactly the serialized header size, deserializes it, rejects oversized payload lengths, resizes the buffer to the payload length, and reads exactly that payload. On short reads it closes the socket and throws `Exception`.

State and persistence: No persistence. It mutates caller-provided `header` and `data`, and it may close the socket on read failure.

Dependencies and integration: Depends on common socket helpers and `packet.h`. It is a synchronous receive utility for protocol clients/servers that want one complete packet before dispatch.

Risks and test signals: It casts payload length to `int32_t` after bounds check; size limits depend on `kMaxDeserializedBytesCount`. Closing the socket inside the helper is a side effect callers must expect. No direct behavior tests in this subset beyond header-size validation in `packet_unittest.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/packet.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/packet.h -->
# sources/distributed-fs/lizardfs/src/protocol/packet.h

Purpose: Defines the core LizardFS packet header, packet version type, message buffer type, and generic serialization/deserialization helpers for both legacy MooseFS packets and versioned LizardFS packets.

Important APIs/types/functions: `PacketHeader`; `PacketVersion`; `MessageBuffer`; `serializePacket`; `buildPacket`; `serializePacketPrefix`; `serializeMooseFsPacket`; `buildMooseFsPacket`; `serializeMooseFsPacketPrefix`; `deserializePacketHeader`; `deserializePacketVersionNoHeader`; `deserializePacketVersionSkipHeader`; data deserialization helpers; `verifyPacketVersionNoHeader`; `receivePacket`.

Control flow: Serializers compute payload length from serialized fields, then prepend `PacketHeader` and optionally packet version. Versioned packet helpers assert type is in the LizardFS range; MooseFS helpers assert old packet range. Deserializers either skip or preserve headers, optionally require full buffer consumption, and throw on trailing bytes or version mismatches.

State and persistence: Stateless helpers over byte buffers. The format is the durable network ABI for protocol messages but this header does not store persistent data.

Dependencies and integration: Uses `MFSCommunication.h` for packet type ranges and `common/serialization.h` for field encoding. Every protocol header in this subset builds on these helpers.

Risks and test signals: Compatibility relies on `PacketHeader::kSize == 8`, old/new packet type ranges, and length semantics where version is included in LizardFS payload length. `packet_unittest.cc` verifies header size; broader malformed-buffer behavior is tested elsewhere if at all.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/packet_unittest.cc -->
# sources/distributed-fs/lizardfs/src/protocol/packet_unittest.cc

Purpose: Minimal unit test validating the serialized size constant for packet headers.

Important APIs/types/functions: `TEST(PacketTests, PacketHeaderSize)`; `PacketHeader::kSize`; `serializedSize(PacketHeader)`.

Control flow: Constructs a packet header, copies the constant to a local variable for GTest compatibility, and asserts serialized size equals the constant.

State and persistence: None.

Dependencies and integration: Depends on GTest and `protocol/packet.h`. It protects a core ABI invariant used by socket readers and packet helpers.

Risks and test signals: The test is narrow but high value: a header-size mismatch would break all packet framing. It does not cover packet range predicates, length semantics, or deserialization helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/packet_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/quota.h -->
# sources/distributed-fs/lizardfs/src/protocol/quota.h

Purpose: Defines serializable quota owner, key, and entry types used in client-master quota APIs.

Important APIs/types/functions: Enums `QuotaRigor` (`kSoft`, `kHard`, `kUsed`), `QuotaResource` (`kInodes`, `kSize`), `QuotaOwnerType` (`kUser`, `kGroup`, `kInode`); classes `QuotaOwner`, `QuotaEntryKey`, `QuotaEntry`.

Control flow: No explicit control flow beyond generated serialization. The nested structure encodes owner, rigor, resource, and limit.

State and persistence: Represents quota state in request/response packets. Master-side quota persistence lives elsewhere.

Dependencies and integration: Used by `matocl::fuseGetQuota`, `cltoma::fuseSetQuota`, and tools `quota_rep.cc`/`quota_set.cc`. Depends on serialization macros.

Risks and test signals: Enum ordering is significant because tools index tables by enum cast. Wire compatibility and quota table interpretation can break if enum values change. No direct serialization tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/tstoma.h -->
# sources/distributed-fs/lizardfs/src/protocol/tstoma.h

Purpose: Defines tapeserver-to-master packets for tapeserver registration and reporting available tape files.

Important APIs/types/functions: `tstoma::registerTapeserver` with version and name; `tstoma::hasFiles` with `std::vector<TapeKey>`; `tstoma::endOfFiles`.

Control flow: Macro-generated serialization emits registration, file-list batches, and an empty end marker. Master-side handlers use these to build tape availability state.

State and persistence: Stateless wire definitions. Payloads describe tapeserver identity and tape contents.

Dependencies and integration: Depends on `common/tape_key.h`, packet helpers, and serialization macros. Pairs with `matots.h` master-to-tapeserver responses.

Risks and test signals: No direct tests. Risks include unbounded vector payloads if callers do not cap batches and compatibility around `TapeKey` serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/protocol/tstoma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/tools/CMakeLists.txt

Purpose: Builds and installs the `lizardfs` tools executable plus compatibility symlinks for historical `mfs*` command names.

Important APIs/types/functions: `collect_sources(TOOLS)`; executable `lizardfs`; target link to `mfscommon`; `MFSTOOL_LINKS`; installation of `mfstools.sh`; custom targets that create symlinks to the wrapper script.

Control flow: CMake collects sources, builds one binary from tool sources, installs it, installs the wrapper script, and creates/install symlinks named like `mfsgetgoal`, `mfsfileinfo`, and `mfsrepquota`.

State and persistence: Build-system state only. It writes generated symlink files in the build directory and installs files into `${BIN_SUBDIR}`.

Dependencies and integration: Depends on repository CMake helpers and `mfscommon`. Integrates command dispatch in `main.cc` with legacy executable names through `mfstools.sh`.

Risks and test signals: Symlink creation assumes `ln -sf` and Unix semantics. Missing a tool from `MFSTOOL_LINKS` can break compatibility even if the command exists in `lizardfs`. Build/install tests would catch target/link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/append_file.cc -->
# sources/distributed-fs/lizardfs/src/tools/append_file.cc

Purpose: Implements `lizardfs appendchunks`, which appends chunk references from one or more source files into a destination file, creating the destination if needed.

Important APIs/types/functions: `append_file_run`; static `append_file_usage`; static `append_file`; legacy packet `CLTOMA_FUSE_APPEND`; response `MATOCL_FUSE_APPEND`; `open_master_conn`.

Control flow: The run function parses no options, creates/opens the destination locally, then calls `append_file` for each source. `append_file` opens master connections for destination and source, verifies both are regular files, sends a legacy packed request with destination inode, source inode, uid, and gid, then expects query id 0 and one status byte.

State and persistence: Mutates filesystem metadata/chunk layout through the master. Locally it may create the destination file before contacting the master.

Dependencies and integration: Uses legacy `datapack`, socket wrappers, `tools_common_functions`, and master registration. Integrates with master FUSE append operation.

Risks and test signals: It mixes two `open_master_conn` calls and relies on the global current-master socket, so connection lifetime is subtle. It manually allocates response buffers by server-provided length. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/append_file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/check_file.cc -->
# sources/distributed-fs/lizardfs/src/tools/check_file.cc

Purpose: Implements `lizardfs checkfile`, a read-only report of chunk copy counts for one or more files.

Important APIs/types/functions: `check_file_run`; static `check_file`; `CLTOMA_FUSE_CHECK`; `MATOCL_FUSE_CHECK`; `print_number`; human-readable flags `-n`, `-h`, `-H`.

Control flow: Parses formatting flags, opens a master connection per file, sends a legacy check request with inode, reads a response, validates query id and length, then prints either compact 3-byte copy/count entries or an 11-entry 32-bit count table.

State and persistence: Read-only against master state. Mutates only global `humode` for formatting and local buffers.

Dependencies and integration: Depends on `datapack`, `mfserr`, socket helpers, and common tool connection logic. It reports master chunk health/copy accounting.

Risks and test signals: Manual response length interpretation has two protocol formats and rejects unexpected sizes. Buffer allocation trusts the header length. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/check_file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/dir_info.cc -->
# sources/distributed-fs/lizardfs/src/tools/dir_info.cc

Purpose: Implements `lizardfs dirinfo`, a directory statistics reporter for LizardFS objects.

Important APIs/types/functions: `dir_info_run`; static usage and per-path query helpers; legacy master request/response packing; number formatting through `print_number`.

Control flow: The command parses human-readable output flags, resolves each target through `open_master_conn`, sends the directory-info request to the master, validates response type/query id/status, and prints counts/sizes for files, directories, chunks, and storage usage.

State and persistence: Read-only. It reflects master metadata and chunk accounting but does not mutate state.

Dependencies and integration: Uses legacy socket/datapack helpers, `tools_common_functions`, and `mfserr`. It fits the same command dispatch path as the other tools.

Risks and test signals: Like other legacy tools, it hand-parses response length and fields, so protocol drift can produce wrong output or rejection. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/dir_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/file_info.cc -->
# sources/distributed-fs/lizardfs/src/tools/file_info.cc

Purpose: Implements `lizardfs fileinfo`, which reports tape replicas and per-chunk storage locations/parts for a file.

Important APIs/types/functions: `file_info_run`; static `file_info`; static `chunks_info`; `chunkTypeToString`; `cltoma::tapeInfo`; `matocl::tapeInfo`; `cltoma::chunksInfo`; `matocl::chunksInfo`; `ChunkCopiesCalculator`.

Control flow: For each file, the command opens a master connection, requests tape info and decodes status-or-response packet versions, then pages through chunk info in batches of 100 until fewer than 100 entries are returned. For each chunk it prints id/version, sorted chunk part addresses/labels, and redundancy warnings.

State and persistence: Read-only; uses master metadata, chunk location state, and tape-copy state. Formatting state is local.

Dependencies and integration: Uses the newer typed protocol helpers and `ServerConnection`-style framing manually through `tcpwrite`/`tcptoread`. It integrates with tape server and chunkserver reporting through `matocl` payloads.

Risks and test signals: Timeout behavior is controlled by `-l` (10 seconds vs simulated 10 days). Manual packet-version handling must match `matocl.h`. The code warns about no valid copies/not enough parts but does not repair. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/file_info.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/file_repair.cc -->
# sources/distributed-fs/lizardfs/src/tools/file_repair.cc

Purpose: Implements `lizardfs filerepair`, a mutation tool that asks the master to repair files, optionally only restoring previous versions and never erasing.

Important APIs/types/functions: `file_repair_run`; static `file_repair`; `CLTOMA_FUSE_REPAIR`; `MATOCL_FUSE_REPAIR`; option `-c`; number formatting flags.

Control flow: Parses formatting flags and `-c`, opens a read-write master connection for each file, sends a legacy repair request with inode, uid, gid, and correct-only flag, then expects either a status byte or three counters: not changed, erased, repaired. It prints the repair outcome counts.

State and persistence: Mutates file metadata/chunk state through the master. The usage text warns it may make files readable by filling missing data with zeros unless `-c` is used.

Dependencies and integration: Uses legacy packet packing, `mfserr`, and common master connection helpers. It integrates with master-side repair logic.

Risks and test signals: High operational risk because it can erase/fill data under some conditions. Manual response parsing and server-provided buffer length are additional risks. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/file_repair.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/get_eattr.cc -->
# sources/distributed-fs/lizardfs/src/tools/get_eattr.cc

Purpose: Implements `lizardfs geteattr`, reporting extra attributes on objects either directly or recursively.

Important APIs/types/functions: `get_eattr_run`; static `get_eattr`; `CLTOMA_FUSE_GETEATTR`; `MATOCL_FUSE_GETEATTR`; modes `GMODE_NORMAL` and `GMODE_RECURSIVE`; `eattrtab` and `eattrdesc`.

Control flow: Parses recursive and number-format options, sends a legacy get-extra-attributes request with inode and mode, validates response length, then either prints a comma-separated attribute set for a single object or aggregates recursive file/directory counts for each attribute bit.

State and persistence: Read-only master query. Uses global formatting mode and global eattr name tables.

Dependencies and integration: Uses common tool helpers, legacy datapack protocol, and master-defined extra attribute constants. Integrates with `set_eattr.cc` as the read side of the eattr tool pair.

Risks and test signals: Response length and count validation is strict but manual. Unknown attribute bits are printed as unknown in recursive mode. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/get_eattr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/get_goal.cc -->
# sources/distributed-fs/lizardfs/src/tools/get_goal.cc

Purpose: Implements `lizardfs getgoal` and deprecated `rgetgoal`, reporting storage goal names for objects or recursively for subtrees.

Important APIs/types/functions: `get_goal_run`; `rget_goal_run`; `gene_get_goal_run`; static `get_goal`; `cltoma::fuseGetGoal`; `matocl::fuseGetGoal`; `FuseGetGoalStats`.

Control flow: Parses recursive and formatting flags, opens a read-only master connection, sends typed `fuseGetGoal`, inspects the response packet version, throws on status packets, and prints either one goal name or recursive counts for files and directories per goal.

State and persistence: Read-only master query. Global `humode` controls formatting.

Dependencies and integration: Uses `ServerConnection`, `cltoma` builders, `matocl` deserializers, and common master connection helpers. It is paired with `set_goal.cc`.

Risks and test signals: Normal mode expects exactly one stats entry; protocol changes could break that invariant. Exceptions close the master connection as failed. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/get_goal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/get_trashtime.cc -->
# sources/distributed-fs/lizardfs/src/tools/get_trashtime.cc

Purpose: Implements `lizardfs gettrashtime` and deprecated recursive wrapper, reporting trash retention time for objects.

Important APIs/types/functions: `get_trashtime_run`; `rget_trashtime_run`; static `get_trashtime`; `CLTOMA_FUSE_GETTRASHTIME`; `MATOCL_FUSE_GETTRASHTIME`.

Control flow: Parses recursive and number-format flags, sends a legacy request with inode and mode, validates the response, prints one trashtime in normal mode, or sorts and prints recursive file/directory count buckets by trashtime.

State and persistence: Read-only. Uses global output formatting state.

Dependencies and integration: Uses `datapack`, `mfserr`, and shared master connection helpers. It complements `set_trashtime.cc`.

Risks and test signals: Manual length validation must match master protocol, including normal-mode length of 16 bytes after query id. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/get_trashtime.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/main.cc -->
# sources/distributed-fs/lizardfs/src/tools/main.cc

Purpose: Main entry point and interactive shell for the `lizardfs` tools executable.

Important APIs/types/functions: `main`; `split`; `print_prefix`; `getCommand`; `set_humode`; `force_master_conn_close`.

Control flow: With command-line arguments, it dispatches `argv[1]` to the command registry. With no arguments, it enters a simple prompt loop, tokenizes input on whitespace, dispatches commands, closes any cached master connection after each command, resets human-readable mode from the environment, and prints a new prompt.

State and persistence: Maintains process status, static path buffer, and command-line parsing state (`optind` reset in interactive mode). No persistent state.

Dependencies and integration: Depends on `tools_commands` registry and common formatting setup. The interactive shell also supports built-in `cd`, `ls`, `exit`, and `quit` via the registry.

Risks and test signals: The tokenizer does not handle quotes or escapes; interactive command arguments split only on whitespace. `isspace` is used on `char` values. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/master_functions.cc -->
# sources/distributed-fs/lizardfs/src/tools/master_functions.cc

Purpose: Implements common master connection discovery, registration, and close helpers for tool commands.

Important APIs/types/functions: `open_master_conn`; `close_master_conn`; `force_master_conn_close`; static `master_register`; static `master_connect`; static `read_master_info`; thread-local `gCurrentMaster`; `master_info_t`.

Control flow: `open_master_conn` resolves a path, optionally rejects read-only filesystems, stats the object for inode/mode, closes any previous cached master socket, then walks upward looking for the special `.masterinfo` file. After reading ip/port/cuid/version, it connects with exponential-ish retry timeouts, registers as `REGISTER_TOOLS`, maps mount root inode to `SPECIAL_INODE_ROOT`, caches the socket, and returns it.

State and persistence: Maintains a thread-local current master socket. Reads `.masterinfo` special files from the mounted filesystem but does not write persistent state.

Dependencies and integration: Uses common serialization, socket helpers, special inode constants, and low-level legacy registration packets. All tools depend on this to locate and authenticate to the active master.

Risks and test signals: The global cached socket means multiple opens in one command must be reasoned about carefully. Path walking mutates a fixed-size `PATH_MAX` buffer. Registration is legacy-packed manually. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/master_functions.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/mfstools.sh -->
# sources/distributed-fs/lizardfs/src/tools/mfstools.sh

Purpose: Compatibility wrapper for legacy `mfs*` tool executable names.

Important APIs/types/functions: Bash `basename $0`; parameter expansion `${tool/lizardfs/lizardfs }`; final command invocation with `"$@"`.

Control flow: The script derives its invoked basename, rewrites the first occurrence of `lizardfs` in the name to `lizardfs `, and runs the resulting command with original arguments. With the listed `mfs*` symlink names, that pattern does not match `lizardfs`, so the wrapper appears to re-invoke the symlink name unless install-time behavior changes the basename/path semantics.

State and persistence: No persistent state.

Dependencies and integration: Installed by `CMakeLists.txt` and used through generated symlinks. Depends on Bash.

Risks and test signals: The substitution expression is terse and appears mismatched with `mfs*` compatibility names, creating a recursion risk. It also does not quote the expanded command word, though installed tool names are controlled. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/mfstools.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/quota_rep.cc -->
# sources/distributed-fs/lizardfs/src/tools/quota_rep.cc

Purpose: Implements `lizardfs repquota`, reporting user, group, all, or per-directory quota usage and limits.

Important APIs/types/functions: `quota_rep_run`; static `quota_rep`; `quota_print_rep`; `quota_print_entry`; `quota_putc_plus_or_minus`; `cltoma::fuseGetQuota`; `matocl::fuseGetQuota`; `QuotaEntry`; `QuotaDatabase::Limits`.

Control flow: Parses mutually exclusive selector modes (`-u`/`-g`, `-a`, or `-d`) and formatting flags, opens a master connection, verifies root path for user/group/all quota unless directory quota is requested, builds requested `QuotaOwner`s, sends a typed get-quota request, handles status-vs-response packet versions, sorts entries, groups limits by owner, and prints a quota table.

State and persistence: Read-only. It materializes quota entries into local tables for printing.

Dependencies and integration: Uses `ServerConnection`, quota protocol structs, master quota database table shape, and common formatting helpers. It is the reporting counterpart to `quota_set.cc`.

Risks and test signals: Enum values are cast to table indices, so protocol enum ordering matters. Usage validation uses XOR logic to enforce exactly one selector family. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/quota_rep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/quota_set.cc -->
# sources/distributed-fs/lizardfs/src/tools/quota_set.cc

Purpose: Implements `lizardfs setquota`, setting soft and hard limits for a user, group, or directory.

Important APIs/types/functions: `quota_set_run`; static `quota_set`; `QuotaOwner`; `QuotaEntry`; `cltoma::fuseSetQuota`; `matocl::fuseSetQuota`; `my_get_number`.

Control flow: Parses exactly one owner mode (`-u`, `-g`, or `-d`), four numeric limits, and a directory path. For directory quotas it replaces owner id with the target inode; for user/group quotas it verifies the path is the mount root. It builds four quota entries for soft/hard inodes and size, sends the request, and expects OK status.

State and persistence: Mutates master quota state. No local persistence.

Dependencies and integration: Uses typed quota protocol, `ServerConnection`, master quota types, and shared master connection logic.

Risks and test signals: Unit parsing and owner selection must be exact because the command changes limits. The command trusts master response status after typed deserialization. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/quota_set.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/recursive_remove.cc -->
# sources/distributed-fs/lizardfs/src/tools/recursive_remove.cc

Purpose: Implements `lizardfs rremove`, a long-running recursive delete command with task-id based cancellation support.

Important APIs/types/functions: `recursive_remove_run`; static `recursive_remove`; `cltoma::requestTaskId`; `matocl::requestTaskId`; `cltoma::recursiveRemove`; `matocl::recursiveRemove`; shared `signalHandler`.

Control flow: Resolves the target path, opens a master connection on its parent, requests a task id, starts a signal-handling thread bound to that job id, sends the recursive remove request, waits for the first non-NOP response with configurable timeout, deserializes status, joins the signal thread via `LambdaGuard`, and prints success or error.

State and persistence: Mutates namespace state through the master by deleting subtrees. Maintains temporary process signal mask/thread state and a master-side task id.

Dependencies and integration: Uses `ServerConnection`, `cltoma`/`matocl` task packets, `lambda_guard`, and common master connection helpers. Integrates with master async task infrastructure.

Risks and test signals: High operational risk due to deletion. Cancellation relies on signals and a secondary master connection in `signalHandler`. Timeout defaults to 60 seconds unless `-l` simulates long wait. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/recursive_remove.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/set_eattr.cc -->
# sources/distributed-fs/lizardfs/src/tools/set_eattr.cc

Purpose: Implements `lizardfs seteattr` and `lizardfs deleattr`, changing extra attribute bits for objects, optionally recursively.

Important APIs/types/functions: `set_eattr_run`; `del_eattr_run`; static `set_eattr`; `CLTOMA_FUSE_SETEATTR`; `MATOCL_FUSE_SETEATTR`; option `-f attrname`; modes for set/delete and recursive behavior.

Control flow: Command parsing accumulates attribute bits from repeated `-f` options, parses recursive and formatting flags, validates at least one attribute and one target, then sends a legacy set-extra-attribute request with inode, uid, bitmask, and mode. The response is either status or changed/not-changed/not-permitted counters.

State and persistence: Mutates master metadata extra attribute bits. Global `humode` affects output only.

Dependencies and integration: Uses `eattrtab` names from common tool helpers, legacy packet packing, and master connection logic. Complements `get_eattr.cc`.

Risks and test signals: Attribute name parsing must reject unknown names and combine masks correctly. Recursive mode can touch many inodes. Manual response parsing has no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/set_eattr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/set_goal.cc -->
# sources/distributed-fs/lizardfs/src/tools/set_goal.cc

Purpose: Implements `lizardfs setgoal` and deprecated `rsetgoal`, changing storage goal names for objects.

Important APIs/types/functions: `set_goal_run`; `rset_goal_run`; `gene_set_goal_run`; static `set_goal`; `cltoma::fuseSetGoal`; `matocl::fuseSetGoal`; option `-l`.

Control flow: Parses formatting, recursive, and long-wait flags, rejects old `+`/`-` goal modifiers, then for each path opens a read-write master connection and sends typed `fuseSetGoal`. It handles status-vs-response packet versions and prints either direct goal result or recursive changed/not changed/not permitted counters.

State and persistence: Mutates master metadata goal assignment. No local persistence.

Dependencies and integration: Uses `ServerConnection`, typed protocol builders, common master connection, and formatting helpers.

Risks and test signals: Changing goals can trigger later replication/deletion work. Long-running recursive changes default to a 30-second timeout unless `-l` is used. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/set_goal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/set_trashtime.cc -->
# sources/distributed-fs/lizardfs/src/tools/set_trashtime.cc

Purpose: Implements `lizardfs settrashtime` and deprecated recursive wrapper, changing trash retention time for objects.

Important APIs/types/functions: `set_trashtime_run`; `rset_trashtime_run`; static `set_trashtime`; `CLTOMA_FUSE_SETTRASHTIME`; `MATOCL_FUSE_SETTRASHTIME`; modes `SMODE_SET`, increase, decrease, recursive mask; option `-l`.

Control flow: Parses formatting, recursive, and long-wait flags, parses a numeric seconds argument with optional trailing `+` or `-`, sends a legacy set-trashtime request with inode, uid, value, and mode, then prints direct result or recursive counters.

State and persistence: Mutates master metadata trashtime values. No local persistence.

Dependencies and integration: Uses legacy datapack protocol, common master connection helpers, `my_get_number`-style formatting support, and `mfserr`.

Risks and test signals: Numeric parsing is manual and must catch malformed suffixes and overflow. Recursive mode can affect many inodes. Infinite timeout is represented as `-1` for `tcptoread`. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/set_trashtime.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/snapshot.cc -->
# sources/distributed-fs/lizardfs/src/tools/snapshot.cc

Purpose: Implements `lizardfs makesnapshot`, creating lazy-copy snapshots for one or more sources into a destination.

Important APIs/types/functions: `snapshot_run`; static `snapshot`; static `make_snapshot`; `cltoma::requestTaskId`; `cltoma::snapshot`; `matocl::snapshot`; `signalHandler`; options `-o`, `-f`, `-l` and internal batch/ignore-missing support.

Control flow: The outer `snapshot` function resolves source/destination combinations, validates same device, handles existing/non-existing destinations and directory targets, and calls `make_snapshot`. `make_snapshot` opens destination directory read-write, requests a task id, starts cancellation signal handling, sends the snapshot request with source inode, destination inode/name, uid/gid, overwrite and batching flags, and waits for status.

State and persistence: Mutates namespace and metadata by creating snapshots. Maintains transient task id and signal thread state.

Dependencies and integration: Uses `cltoma`/`matocl`, `ServerConnection`, `MooseFsString`, common path helpers, and master connection logic. Integrates with master async task system.

Risks and test signals: High impact command; path resolution, symlink handling, overwrite semantics, and same-device checks are critical. Cancellation relies on signal masking and thread cleanup. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_commands.cc -->
# sources/distributed-fs/lizardfs/src/tools/tools_commands.cc

Purpose: Command registry and usage printer for the unified `lizardfs` tool executable and interactive shell.

Important APIs/types/functions: `printUsage`; `printTools`; `getCommand`; `printArgs`; static built-ins `cd_func`, `ls_func`, `exit_func`; map `lizard_commands`.

Control flow: `printUsage` prints general usage or dispatches a named command with a single `help` argument. `getCommand` looks up command names in an unordered map. Built-ins implement shell-like `cd`, `ls`, and process exit.

State and persistence: The command map is static process state. `cd_func` changes current working directory; `exit_func` terminates the process.

Dependencies and integration: Exposes all `*_run` tool entry points declared in `tools_commands.h`. Used by `main.cc` and installed wrapper names.

Risks and test signals: `ls_func` builds a shell command by concatenating arguments, which is command-injection-prone in interactive use. `printUsage` calls target functions with `argc=1`, relying on each command to show usage. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_commands.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_commands.h -->
# sources/distributed-fs/lizardfs/src/tools/tools_commands.h

Purpose: Declares command lookup/usage helpers and every tool entry point implemented under `src/tools`.

Important APIs/types/functions: `getCommand`; `printUsage`; `printTools`; `printArgs`; `append_file_run`, `check_file_run`, `dir_info_run`, `file_info_run`, `file_repair_run`, `snapshot_run`, eattr/goal/trashtime/quota/remove command functions.

Control flow: Header only declarations; runtime dispatch is implemented in `tools_commands.cc`.

State and persistence: None.

Dependencies and integration: Includes standard function/map/string/vector-related headers and is included by every command implementation and `main.cc`.

Risks and test signals: Adding a new command requires updating both this header and the registry/usage text. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_common_functions.cc -->
# sources/distributed-fs/lizardfs/src/tools/tools_common_functions.cc

Purpose: Implements shared output formatting, path helpers, signal cancellation, and master connection helpers declared in `tools_common_functions.h`.

Important APIs/types/functions: Global `humode`, `eattrtab`, `eattrdesc`; `signalHandler`; `check_usage`; `set_humode`; `print_number`; `my_get_number`; basename/dirname helpers; connection functions are completed in `master_functions.cc`.

Control flow: `set_humode` reads `MFSHRFORMAT`. `print_number` prints fixed-width, IEC, or SI numbers and placeholder dashes. `signalHandler` waits for termination signals, opens a master connection, sends `cltoma::stopTask`, and prints cancellation outcome. Parsing/path functions support command implementations.

State and persistence: Maintains process-global output mode and static attribute name arrays. Signal handling opens transient master connections but stores no persistent state.

Dependencies and integration: Uses human-readable formatting, `mfserr`, `ServerConnection`, `cltoma`, `matocl`, socket helpers, and common path/system utilities. Long-running commands `snapshot` and `recursive_remove` use `signalHandler`.

Risks and test signals: Signal handling performs network operations after signals are routed through `sigwait`, so setup must block signals in calling threads. Global `humode` makes formatting process-wide. Numeric/path parsing edge cases can affect many commands. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_common_functions.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_common_functions.h -->
# sources/distributed-fs/lizardfs/src/tools/tools_common_functions.h

Purpose: Shared declarations and small inline usage printers for LizardFS tools.

Important APIs/types/functions: Macros `tcpread`/`tcpwrite`; extern `humode`, `eattrtab`, `eattrdesc`; `check_usage`; `set_humode`; `print_number`; `my_get_number`; path helpers; `open_master_conn`; close helpers; `signalHandler`; inline printers for number format, recursive option, and extra attributes.

Control flow: Header provides declarations and inline functions that print common help text. Implementations live in `tools_common_functions.cc` and `master_functions.cc`.

State and persistence: Declares process-global formatting state and master connection functions. No direct persistence.

Dependencies and integration: Included by most tool commands. Depends on sockets and `MFSCommunication.h` constants for eattr metadata.

Risks and test signals: The `tcpread`/`tcpwrite` macros bake in 10-second timeouts for legacy tools. Shared globals can make command behavior order-dependent in interactive mode if not reset. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/tools/tools_common_functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/unittests/CMakeLists.txt

Purpose: Build configuration for the shared `mfsunittests` support library.

Important APIs/types/functions: `collect_sources(UNITTESTS)`; `add_library(mfsunittests ${UNITTESTS_SOURCES})`.

Control flow: CMake collects unittest support sources and builds them into a library consumed by test binaries.

State and persistence: Build-system state only.

Dependencies and integration: Integrates helper sources such as packet helpers, constants, plan tester, and mocks into the test build.

Risks and test signals: Missing files from source collection can break downstream tests. No runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/TemporaryDirectory.h -->
# sources/distributed-fs/lizardfs/src/unittests/TemporaryDirectory.h

Purpose: RAII helper that creates a unique temporary directory for tests and removes it recursively in the destructor.

Important APIs/types/functions: `TemporaryDirectory` constructor; destructor; `name()`.

Control flow: Constructor rejects comments containing `/`, builds a directory name from prefix, timestamp, microseconds, pid, and optional comment, then creates the directory. Destructor calls `boost::filesystem::remove_all` with ignored error code.

State and persistence: Creates real filesystem state for a test lifetime and deletes it on destruction. The directory name is stored in `name_`.

Dependencies and integration: Uses `boost::filesystem`, `boost::format`, `gettimeofday`, and `getpid`. Useful for tests needing isolated directories.

Risks and test signals: Constructor throws `new std::runtime_error`, which throws a pointer rather than an exception object. Directory creation errors are not checked. Destructor suppresses cleanup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/TemporaryDirectory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.cc -->
# sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.cc

Purpose: Defines reusable `ChunkPartType` constants for standard and XOR chunk layouts used in protocol and read-plan tests.

Important APIs/types/functions: Constants `standard`, `xor_1_of_2` through `xor_p_of_9`, built from `slice_traits::standard::ChunkPartType` and `slice_traits::xors::ChunkPartType`.

Control flow: Static constant initialization only.

State and persistence: Process-static test constants; no persistence.

Dependencies and integration: Implements declarations from `chunk_type_constants.h`; used by protocol serialization tests and other unit tests requiring stable chunk part fixtures.

Risks and test signals: Constants must match production `slice_traits` encoding. Only XOR levels listed here are available to tests; EC constants are not provided in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.h -->
# sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.h

Purpose: Declares shared chunk part constants for tests.

Important APIs/types/functions: `extern const ChunkPartType` declarations for standard and XOR data/parity parts across levels 2, 3, 4, 6, 7, and 9.

Control flow: No runtime control flow.

State and persistence: Declares process-static constants defined in the `.cc`.

Dependencies and integration: Included by packet serialization tests to avoid repeated chunk type construction.

Risks and test signals: Header and implementation must stay synchronized. Missing declarations limit test coverage for newer chunk layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/chunk_type_constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/inout_pair.h -->
# sources/distributed-fs/lizardfs/src/unittests/inout_pair.h

Purpose: Provides small macros for defining input/output variables and verifying serialization round trips in unit tests.

Important APIs/types/functions: `LIZARDFS_DEFINE_INOUT_PAIR`; `LIZARDFS_DEFINE_INOUT_VECTOR_PAIR`; `LIZARDFS_VERIFY_INOUT_PAIR`.

Control flow: Macro expansion creates `nameIn`/`nameOut` variables and emits `EXPECT_EQ` assertions with helpful labels.

State and persistence: Test local variables only.

Dependencies and integration: Used throughout protocol unit tests to reduce boilerplate.

Risks and test signals: Macros depend on naming convention and equality operators for tested types. They hide variable declarations, which can make failures harder to trace in complex tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/inout_pair.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/main.cc -->
# sources/distributed-fs/lizardfs/src/unittests/main.cc

Purpose: Common GoogleTest main for LizardFS unit tests.

Important APIs/types/functions: `main`; `testing::InitGoogleTest`; `RUN_ALL_TESTS`; `setupApplicationName`; `setup_local_empty_lizardfs_info`.

Control flow: Initializes application name and local LizardFS info, initializes GTest, and runs all tests.

State and persistence: Process initialization only. It may set common application metadata for logging/config behavior.

Dependencies and integration: Linked into test binaries needing a standard main. Depends on GTest and common setup functions.

Risks and test signals: Minimal risk. Any setup side effects apply to every test binary using this main.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/unittests/mocks/CMakeLists.txt

Purpose: Build configuration for the `mfsunittests-mocks` library.

Important APIs/types/functions: `collect_sources(UNITTESTS_MOCKS)`; `add_library(mfsunittests-mocks ${UNITTESTS_MOCKS_SOURCES})`.

Control flow: CMake collects mock sources and packages them into a library for tests.

State and persistence: Build-system state only.

Dependencies and integration: Supplies `ModuleMock`, `ChunkConnectorMock`, and related mock tests to the test build.

Risks and test signals: Source collection must include both mock implementations and any mock-specific tests expected by the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.cc -->
# sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.cc

Purpose: Implements a mock chunk connector that maps logical chunkserver addresses to `ModuleMock` localhost servers for tests.

Important APIs/types/functions: `ChunkConnectorMock` constructor; `ChunkConnectorMock::startUsingConnection`; `Modules` map from `NetworkAddress` to `ModuleMock*`; base `ChunkConnector::startUsingConnection`.

Control flow: The constructor stores the provided module map and calls `init()` on each `ModuleMock`. `startUsingConnection` looks up the requested logical server address, translates it to localhost plus the mock's listening port, and delegates to the production `ChunkConnector`; missing mappings throw `ChunkserverConnectionException`.

State and persistence: Maintains an in-memory address-to-mock map and starts mock listener threads. No persistent state.

Dependencies and integration: Used in tests that require a `ChunkConnector`-like object without network side effects.

Risks and test signals: Tests get real TCP connection behavior against mocks, but only for addresses explicitly registered in the map. Lifetime depends on the referenced `ModuleMock` objects staying alive while connections are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.h -->
# sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.h

Purpose: Declares `ChunkConnectorMock`, a test connector that redirects chunkserver connection attempts to `ModuleMock` instances.

Important APIs/types/functions: Class `ChunkConnectorMock`; typedef `Modules`; constructor accepting an initializer list of logical address/mock pairs; override `startUsingConnection`.

Control flow: The header defines a mapping-based connector interface; the `.cc` starts each module and delegates mapped connections to the base connector using the mock's actual localhost port.

State and persistence: Stores the address-to-module map. No persistence; real sockets are opened by the modules and base connector during tests.

Dependencies and integration: Depends on production chunk connector types and network/chunk identifiers. Used by unit tests that need to inject a connector.

Risks and test signals: The mock is realistic enough for socket framing tests but only models configured servers. Unmapped addresses throw, which is useful test signal for missing fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/chunk_connector_mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.cc -->
# sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.cc

Purpose: Implements `ModuleMock`, a nonblocking TCP server test double that accepts clients, receives framed packets, and can queue responses.

Important APIs/types/functions: Constructor/destructor; `init`; `port`; `address`; `operator()` event loop; `serveFd`; `respondToCurrentClient`; `disconnectCurrentClient`; `signal`.

Control flow: `init` creates a nonblocking localhost listening socket and starts a thread. The event loop polls the listener and client sockets, accepts clients, feeds incoming bytes into `MessageReceiveBuffer`, calls virtual hooks for new connections/messages/end, counts received packets, and drains queued response buffers via `MultiBufferWriter`.

State and persistence: Maintains socket fd, background thread, termination flag, connected client records, current client fd, packet counters, signal counters, mutex and condition variable. No persistent storage.

Dependencies and integration: Uses common socket wrappers, `MessageReceiveBuffer`, `MultiBufferWriter`, `NetworkAddress`, and packet headers. Tests subclass it to simulate modules in integration-style unit tests.

Risks and test signals: Destructor assumes `init` started a joinable thread. Callbacks can disconnect current clients while message processing is active, so the implementation checks map membership. Poll timeout controls responsiveness. `module_mock_unittest.cc` exercises basic connection/message/response behaviors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.h -->
# sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.h

Purpose: Declares `ModuleMock`, a reusable threaded network module mock for unit tests.

Important APIs/types/functions: Virtual hooks `onNewConnection`, `onIncomingMessage`, `onConnectionEnd`; waits `waitForPacketReceived`, `waitForPacketsReceived`, `waitForSignal`; `init`; `port`; `address`; protected `respondToCurrentClient`, `disconnectCurrentClient`, `signal`; nested `ClientRecord`.

Control flow: Templated wait helpers use a `Timeout`, mutex, and condition variable to consume packet/signal counters with timeout. The event loop and socket serving are defined in the implementation file.

State and persistence: Declares all runtime server/client state, receive buffers, write queues, and synchronization counters. No persistent state.

Dependencies and integration: Used by tests that need realistic packet framing over TCP without launching full modules.

Risks and test signals: Wait helpers consume counters, so repeated waits require care. The mock is single-current-client oriented for response helpers. Header design encourages subclass hooks for assertions and scripted responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock_unittest.cc -->
# sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock_unittest.cc

Purpose: Tests the `ModuleMock` TCP mock behavior.

Important APIs/types/functions: Test subclasses overriding hooks; tests for connection, packet receipt, queued responses, disconnection, and signal/wait helpers; socket helpers and packet builders.

Control flow: Test cases initialize a mock, connect a client socket, send LizardFS-framed packets, wait for packet counters or signals, and verify responses or connection events as appropriate.

State and persistence: Test-only sockets and mock counters. No persistent filesystem state.

Dependencies and integration: Depends on GTest, common socket helpers, packet serialization, and `ModuleMock`.

Risks and test signals: Provides practical coverage for the threaded mock, which many higher-level tests may rely on. It is still timing-sensitive because waits use real timeouts and background polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/mocks/module_mock_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/packet.h -->
# sources/distributed-fs/lizardfs/src/unittests/packet.h

Purpose: Provides packet assertion helpers for protocol unit tests.

Important APIs/types/functions: `verifyHeader`; `removeHeaderInPlace`; `verifyVersion`; overloads using `std::vector<uint8_t>` and packet constants.

Control flow: Helpers deserialize packet headers/versions, assert expected type or version, and erase header bytes from buffers so tests can feed payloads to deserializers.

State and persistence: Mutates test buffers in-place when removing headers. No persistence.

Dependencies and integration: Included by protocol unit tests in this subset. Depends on GTest assertions and `protocol/packet.h`.

Risks and test signals: Header removal changes buffer indexing, so tests must call helpers in the correct order. These helpers centralize common packet test idioms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/plan_tester.cc -->
# sources/distributed-fs/lizardfs/src/unittests/plan_tester.cc

Purpose: Implements `ReadPlanTester`, a simulator for executing read plans against synthetic standard, XOR, and erasure-coded chunk-part data.

Important APIs/types/functions: `executePlan`; `readDataFromChunkServer`; `startReadOperation`; `startReadsForWave`; `checkPlan`; `buildXorData`; `buildStdData`; `buildECData`; `compareBlocks`.

Control flow: `executePlan` allocates the output buffer, validates plan invariants in debug builds, runs read waves up to 10, records available parts or networking failures, stops when the plan is readable, and runs post-processing. Data builders generate deterministic block-offset payloads; XOR parity is computed with `blockXor`, and EC parity with `ReedSolomon`.

State and persistence: Maintains `available_parts_`, `networking_failures_`, and `output_buffer_` for a simulated execution. No persistence.

Dependencies and integration: Depends on `ReadPlan`, `slice_traits`, `block_xor`, `ReedSolomon`, and chunk constants. Used by read-plan unit tests to verify reconstruction logic without real chunkservers.

Risks and test signals: The simulator asserts non-overlapping read outputs and range bounds in debug builds. It may not model all network behaviors, latency, or partial reads. EC generation must stay aligned with production coding rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/plan_tester.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/plan_tester.h -->
# sources/distributed-fs/lizardfs/src/unittests/plan_tester.h

Purpose: Declares `unittests::ReadPlanTester`, a helper for read-plan execution and synthetic chunk data generation.

Important APIs/types/functions: `executePlan`; templated `buildData`; `compareBlocks`; protected read/start/check/build helpers; public state vectors `available_parts_`, `networking_failures_`, `output_buffer_`.

Control flow: The templated `buildData` inspects requested part types, groups by slice type, and delegates to standard, XOR, or EC builders implemented in the `.cc`.

State and persistence: Declares transient test execution state. No persistence.

Dependencies and integration: Depends on `common/read_plan.h` and `slice_traits`. Used by read-plan tests to avoid duplicating data generation and simulation logic.

Risks and test signals: Public mutable state is convenient but can leak between test assertions if reused without `executePlan` reset. Template behavior depends on each part's `getSliceType`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/plan_tester.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/serialization.h -->
# sources/distributed-fs/lizardfs/src/unittests/serialization.h

Purpose: Provides small test helpers for serialization/deserialization round trips.

Important APIs/types/functions: Generic serialization test templates/macros for comparing serialized and deserialized values; integration with `common/serialization`.

Control flow: Helpers serialize input values into a buffer, deserialize into output values, and assert equality or expected serialized shape depending on the helper used.

State and persistence: Test local buffers only. No persistence.

Dependencies and integration: Used by unit tests for serializable classes and protocol payloads. Depends on common serialization APIs and GTest-style equality.

Risks and test signals: Generic helpers assume equality operators and deterministic serialization. They are useful for positive tests but do not replace malformed-buffer testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/serialization.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/unittests.in -->
# sources/distributed-fs/lizardfs/src/unittests/unittests.in

Purpose: Template shell launcher for unit tests.

Important APIs/types/functions: Shell variables and configured paths; execution of the generated unittest binary from the build/install context.

Control flow: The script template is configured by CMake and runs the relevant unittest executable with forwarded arguments/environment.

State and persistence: No persistent state beyond process exit code.

Dependencies and integration: Used by the build/test harness to invoke compiled tests consistently.

Risks and test signals: Correctness depends on CMake substitutions and executable paths. The file is small and has no direct C++ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/unittests/unittests.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/uraft/CMakeLists.txt

Purpose: Build and install configuration for the `lizardfs-uraft` high-availability helper daemon and shell helper script.

Important APIs/types/functions: `configure_file(lizardfs-uraft-helper.in ...)`; `collect_sources(URAFT)`; executable `lizardfs-uraft`; link libraries `${Boost_LIBRARIES}`, `${RT_LIBRARY}`, `pthread`; install rules.

Control flow: CMake configures the helper script with install-time paths, collects sources plus `time_utils.cc`, builds the daemon, links dependencies, and installs the binary and helper.

State and persistence: Build/install state only.

Dependencies and integration: Integrates uRaft controller code with Boost, pthreads, and the installed LizardFS service management scripts.

Risks and test signals: Missing path substitutions can break the helper script. Link dependencies are platform-sensitive because of realtime and pthread libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/lizardfs-uraft-helper.in -->
# sources/distributed-fs/lizardfs/src/uraft/lizardfs-uraft-helper.in

Purpose: Configured Bash helper used by uRaft to query/promote/demote LizardFS masters and manage floating IP addresses.

Important APIs/types/functions: Functions `load_config`, `lizardfs_master`, `lizardfs_admin`, `get_metadata_version_from_file`, `lizardfs_promote`, `lizardfs_demote`, `lizardfs_quick_stop`, `lizardfs_metadata_version`, `lizardfs_isalive`, `lizardfs_assign_ip`, `lizardfs_drop_ip`, `lizardfs_dead`; command dispatch case.

Control flow: The script loads master and uraft configs, validates floating IP and admin password settings, probes metadata version through `lizardfs-admin` or `mfsmetarestore`, promotes by admin command or disk recovery path, demotes by dropping IP and restarting as shadow, and assigns/drops primary and optional secondary floating IPs.

State and persistence: Reads config files, metadata lock/path state, and metadata version from disk. Mutates service state by restarting `mfsmaster`, stopping/promoting/demoting via admin commands, and adding/removing IP addresses with `sudo ip`.

Dependencies and integration: Depends on installed `mfsmaster`, `lizardfs-admin`, `mfsmetarestore`, `logger`, `getent`, `awk`, `arping`, and system networking. It is called by the uRaft controller command hooks.

Risks and test signals: High operational risk: it manipulates master personality and floating IPs. Config loading uses shell sourcing of filtered config lines, so config content trust matters. Several commands require sudo/network privileges. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/lizardfs-uraft-helper.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/main.cc -->
# sources/distributed-fs/lizardfs/src/uraft/main.cc

Purpose: Main program for `lizardfs-uraft`, a Boost.Asio-based uRaft controller daemon for LizardFS high availability.

Important APIs/types/functions: `parseOptions`; `getSeed`; `daemonize`; `makePidFile`; `main`; `uRaftController::Options`; Boost.Program_options hidden config keys for node id, node addresses, election/heartbeat timing, local master, command timeouts, elector mode, and status port.

Control flow: `parseOptions` reads command-line options, opens and parses the config file, validates node id and node address list, and fills options/pidfile/daemon flags. `main` opens syslog, seeds randomness, optionally daemonizes with double fork and `/dev/null` stdio, creates Boost.Asio IO service and signal handlers, configures and initializes `uRaftController`, writes pidfile, and runs the event loop.

State and persistence: May write a pidfile. As a daemon it changes working directory, umask, stdio fds, and syslog state. Runtime cluster state is managed by `uRaftController`.

Dependencies and integration: Depends on `uraftcontroller.h`, Boost.Asio, Boost.Program_options, syslog, POSIX daemon APIs, and configured `ETC_PATH`. Integrates with the helper script through controller command options.

Risks and test signals: Config parsing accepts hidden options from config files and command line; missing node addresses or invalid ids are fatal. Daemonization closes stdio and writes pidfile after controller options are accepted. Signal handling requires Boost version >= 1.47 for async stop. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/main.cc -->
