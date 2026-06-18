# Research: subset-b-010021

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AceHeader.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AceHeader.cs

## Purpose
Models the four-byte MS-DTYP ACE_HEADER prefix used before every access-control entry.

## Important APIs, Types, And Functions
Declarations: `public class AceHeader`. Constants: `public const int Length = 4;`. Important fields include `public AceType AceType`, `public AceFlags AceFlags`, `public ushort AceSize`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it reads AceType, AceFlags, and AceSize from the buffer and writes them back in little-endian form.

## Control Flow
Values are consumed by the security descriptor parser and ACE/ACL serializers. There is no branching beyond reading fixed-width fields and preserving bit flags.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AceHeader.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceFlags.cs

## Purpose
Defines ACE inheritance and audit flag bits for security descriptor ACE headers.

## Important APIs, Types, And Functions
Declarations: `public enum AceFlags : byte`. Enum values include `{`, `OBJECT_INHERIT_ACE = 0x01`, `CONTAINER_INHERIT_ACE = 0x02`, `NO_PROPAGATE_INHERIT_ACE = 0x04`, `INHERIT_ONLY_ACE = 0x08`, `INHERITED_ACE = 0x10`, `SUCCESSFUL_ACCESS_ACE_FLAG = 0x40`, `FAILED_ACCESS_ACE_FLAG = 0x80`. Specific behavior: it is a byte-sized [Flags] enum consumed by AceHeader and ACE serializers.

## Control Flow
Values are consumed by the security descriptor parser and ACE/ACL serializers. There is no branching beyond reading fixed-width fields and preserving bit flags.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceType.cs

## Purpose
Enumerates MS-DTYP ACE type identifiers for access allowed/denied, audit/alarm, object, callback, mandatory-label, resource-attribute, and scoped-policy ACEs.

## Important APIs, Types, And Functions
Declarations: `public enum AceType : byte`. Enum values include `{`, `ACCESS_ALLOWED_ACE_TYPE = 0x00`, `ACCESS_DENIED_ACE_TYPE = 0x01`, `SYSTEM_AUDIT_ACE_TYPE = 0x02`, `SYSTEM_ALARM_ACE_TYPE = 0x03`, `ACCESS_ALLOWED_COMPOUND_ACE_TYPE = 0x04`, `ACCESS_ALLOWED_OBJECT_ACE_TYPE = 0x05`, `ACCESS_DENIED_OBJECT_ACE_TYPE = 0x06`, `SYSTEM_AUDIT_OBJECT_ACE_TYPE = 0x07`, `SYSTEM_ALARM_OBJECT_ACE_TYPE = 0x08`, `ACCESS_ALLOWED_CALLBACK_ACE_TYPE = 0x09`, `ACCESS_DENIED_CALLBACK_ACE_TYPE = 0x0A`, `ACCESS_ALLOWED_CALLBACK_OBJECT_ACE_TYPE = 0x0B`, `ACCESS_DENIED_CALLBACK_OBJECT_ACE_TYPE = 0x0C`. Specific behavior: it is used by ACE.GetAce and AceHeader to choose or label concrete ACE records.

## Control Flow
Values are consumed by the security descriptor parser and ACE/ACL serializers. There is no branching beyond reading fixed-width fields and preserving bit flags.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/Enums/AceType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACL.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACL.cs

## Purpose
Represents a self-contained access control list as a List<ACE> with ACL revision, reserved fields, computed size, and ACE count.

## Important APIs, Types, And Functions
Declarations: `public class ACL : List<ACE>`. Constants: `public const int FixedLength = 8;`. Important fields include `public byte AclRevision`, `public byte Sbz1`, `public ushort Sbz2`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it parses ACEs sequentially with ACE.GetAce and serializes list length/count before each ACE.

## Control Flow
Construction reads ACL revision/reserved/size/count, advances past the fixed header, then loops `AceCount` times using each ACE header size to locate the next ACE. Writing emits computed total length and count before delegating serialization to each ACE.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACL.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/Enums/SecurityDescriptorControl.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/Enums/SecurityDescriptorControl.cs

## Purpose
Defines SECURITY_DESCRIPTOR_CONTROL bit flags such as DACL/SACL presence, inheritance state, protection, RM control, and self-relative layout.

## Important APIs, Types, And Functions
Declarations: `public enum SecurityDescriptorControl : ushort`. Enum values include `{`, `OwnerDefaulted = 0x0001`, `GroupDefaulted = 0x0002`, `DaclPresent = 0x0004`, `DaclDefaulted = 0x0008`, `SaclPresent = 0x0010`, `SaclDefaulted = 0x0020`, `DaclUntrusted = 0x0040`, `ServerSecurity = 0x0080`, `DaclAutoInheritedReq = 0x0100`, `SaclAutoInheritedReq = 0x0200`, `DaclAutoInherited = 0x0400`, `SaclAutoInherited = 0x0800`, `DaclProtected = 0x1000`. Specific behavior: it is stored on SecurityDescriptor and ORed with SelfRelative when writing.

## Control Flow
Values are consumed by the security descriptor parser and ACE/ACL serializers. There is no branching beyond reading fixed-width fields and preserving bit flags.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/Enums/SecurityDescriptorControl.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SID.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SID.cs

## Purpose
Represents a packet-format Windows SID with revision, six-byte identifier authority, and little-endian subauthority list.

## Important APIs, Types, And Functions
Declarations: `public class SID`. Constants: `public const int FixedLength = 8;`. Important fields include `public static readonly byte[] WORLD_SID_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 }`, `public static readonly byte[] LOCAL_SID_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x02 }`, `public static readonly byte[] CREATOR_SID_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x02 }`, `public static readonly byte[] SECURITY_NT_AUTHORITY = new byte[] { 0x00, 0x00, 0x00, 0x00, 0x00, 0x05 }`, `public byte Revision`, `public byte[] IdentifierAuthority`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it provides Everyone and LocalSystem helpers and fixed/computed length serialization.

## Control Flow
Construction reads revision, subauthority count, six authority bytes, then loops over little-endian subauthorities. Writing mirrors that sequence and derives the count from the list length.

## State And Persistence
State is limited to public value fields and computed lengths; there is no persistence beyond byte serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects. IdentifierAuthority must be exactly six bytes and large subauthority counts can overflow byte count semantics if callers mutate the list unexpectedly.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SID.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SecurityDescriptor.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SecurityDescriptor.cs

## Purpose
Models a self-relative SECURITY_DESCRIPTOR containing optional owner SID, group SID, SACL, and DACL sections.

## Important APIs, Types, And Functions
Declarations: `public class SecurityDescriptor`. Constants: `public const int FixedLength = 20;`. Important fields include `public byte Revision`, `public byte Sbz1`, `public SecurityDescriptorControl Control`, `public SID OwnerSid`, `public SID GroupSid`, `public ACL Sacl`, `public ACL Dacl`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it parses header offsets, materializes optional nested SID/ACL objects, and writes a compact self-relative descriptor.

## Control Flow
Construction reads the fixed descriptor header, then follows non-zero owner/group/SACL/DACL offsets into nested SID or ACL objects. Writing first computes all self-relative offsets from the fixed header, writes the header with `SelfRelative` set, then emits optional sections in owner, group, SACL, DACL order. No external state is consulted.

## State And Persistence
State is an in-memory descriptor graph of optional owner/group SIDs and SACL/DACL ACLs plus control bits. Serialization is self-contained and does not persist outside the returned byte array.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, plus adjacent `ACE`, `ACL`, `SID`, `AceType`, `AceFlags`, and `SecurityDescriptorControl` types. It integrates with SMB/NT file-store security information parsing and any file system code that transports Windows security descriptors.

## Risks
Bounds and validity checks are minimal, so malformed offsets, ACE sizes, SID subauthority counts, or ACL counts can surface as reader exceptions or inconsistent nested objects. Only self-relative layout is written; callers expecting absolute descriptors must not reuse this serializer blindly.

## Test Signals
Useful signals are byte-for-byte round trips for descriptors with owner, group, DACL, SACL, empty ACLs, multiple ACE sizes, Everyone/LocalSystem SIDs, all control flag combinations, and malformed offset/count fixtures that fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/SecurityDescriptor.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NBTConnectionReceiveBuffer.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NBTConnectionReceiveBuffer.cs

## Purpose
Buffers TCP NetBIOS session bytes until a complete session packet is available.

## Important APIs, Types, And Functions
Declarations: `public class NBTConnectionReceiveBuffer : IDisposable`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it uses a rented or allocated byte array, cached packet length, compaction, and SessionPacket factory dispatch.

## Control Flow
Callers receive into `Buffer` at `WriteOffset`, report bytes with `SetNumberOfBytesReceived`, poll `HasCompletePacket`, then dequeue either a parsed `SessionPacket` or raw packet bytes. Dequeue removes consumed bytes and compacts leftovers when a partial following packet remains.

## State And Persistence
Mutable state is the rented backing buffer, read offset, byte count, and cached packet length. It is explicitly not thread-safe. `Dispose` returns the rented buffer on modern target frameworks. There is no durable persistence; state only spans a TCP receive loop.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately. The buffer is not thread-safe and cached `m_packetLength` assumes callers always call `HasCompletePacket` before dequeueing.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NBTConnectionReceiveBuffer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/EnumStructures/NameFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/EnumStructures/NameFlags.cs

## Purpose
Packs NetBIOS name-service owner node type and group/workgroup bit into the two-byte name flags field.

## Important APIs, Types, And Functions
Declarations: `public enum OwnerNodeType : byte`; `public struct NameFlags`. Constants: `public const int Length = 2;`. Important fields include `public OwnerNodeType NodeType`, `public bool WorkGroup`. Enum values include `{`, `BNode = 0x00`, `PNode = 0x01`, `MNode = 0x10`. Specific behavior: it implements explicit conversions to and from ushort for resource-record data.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/EnumStructures/NameFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NameRecordType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NameRecordType.cs

## Purpose
Defines protocol constants for `NameRecordType` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum NameRecordType : ushort`. Enum values include `{`, `NB = 0x0020`, `NBStat = 0x0021`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NameRecordType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NameServiceOperation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NameServiceOperation.cs

## Purpose
Defines protocol constants for `NameServiceOperation` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum NameServiceOperation : byte`. Enum values include `{`, `QueryRequest = 0x00`, `RegistrationRequest = 0x05`, `ReleaseRequest = 0x06`, `WackRequest = 0x07`, `RefreshRequest = 0x08`, `QueryResponse = 0x10`, `RegistrationResponse = 0x15`, `ReleaseResponse = 0x16`, `WackResponse = 0x17`, `RefreshResponse = 0x18`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NameServiceOperation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NetBiosSuffix.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NetBiosSuffix.cs

## Purpose
Defines protocol constants for `NetBiosSuffix` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum NetBiosSuffix : byte`. Enum values include `{`, `WorkstationService = 0x00`, `MessengerService = 0x03`, `DomainMasterBrowser = 0x1B`, `MasterBrowser = 0x1D`, `BrowserServiceElections = 0x1E`, `FileServerService = 0x20`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/NetBiosSuffix.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/OperationFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/OperationFlags.cs

## Purpose
Defines protocol constants for `OperationFlags` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum OperationFlags : byte`. Enum values include `{`, `Broadcast = 0x01`, `RecursionAvailable = 0x08`, `RecursionDesired = 0x10`, `Truncated = 0x20`, `AuthoritativeAnswer = 0x40`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/OperationFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/QuestionClass.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/QuestionClass.cs

## Purpose
Defines protocol constants for `QuestionClass` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum QuestionClass : ushort`. Enum values include `{`, `In = 0x0001`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/QuestionClass.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/ResourceRecordClass.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/ResourceRecordClass.cs

## Purpose
Defines protocol constants for `ResourceRecordClass` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum ResourceRecordClass : ushort`. Enum values include `{`, `In = 0x0001`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Enums/ResourceRecordClass.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameQueryRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameQueryRequest.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `NameQueryRequest`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class NameQueryRequest`. Important fields include `public NameServicePacketHeader Header`, `public QuestionSection Question`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameQueryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameRegistrationRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameRegistrationRequest.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `NameRegistrationRequest`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class NameRegistrationRequest`. Constants: `public const int DataLength = 6;`. Important fields include `public NameServicePacketHeader Header`, `public QuestionSection Question`, `public ResourceRecord Resource`, `public NameFlags NameFlags`, `public byte[] Address`. Serialization surface: `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameRegistrationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameServicePacketHeader.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameServicePacketHeader.cs

## Purpose
Represents the 12-byte RFC 1002 name-service header with transaction id, opcode, flags/result code, and section counts.

## Important APIs, Types, And Functions
Declarations: `public class NameServicePacketHeader`. Constants: `public const int Length = 12;`. Important fields include `public ushort TransactionID`, `public NameServiceOperation OpCode`, `public OperationFlags Flags`, `public byte ResultCode`, `public ushort QDCount`, `public ushort ANCount`, `public ushort NSCount`, `public ushort ARCount`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it packs opcode/flags/result into the second header word and writes all fields big-endian.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NameServicePacketHeader.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NodeStatusRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NodeStatusRequest.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `NodeStatusRequest`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class NodeStatusRequest`. Important fields include `public NameServicePacketHeader Header`, `public QuestionSection Question`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NodeStatusRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NodeStatusResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NodeStatusResponse.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `NodeStatusResponse`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class NodeStatusResponse`. Important fields include `public NameServicePacketHeader Header`, `public ResourceRecord Resource`, `public NodeStatistics Statistics`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/NodeStatusResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/PositiveNameQueryResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/PositiveNameQueryResponse.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `PositiveNameQueryResponse`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class PositiveNameQueryResponse`. Constants: `public const int EntryLength = 6;`. Important fields include `public NameServicePacketHeader Header`, `public ResourceRecord Resource`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/PositiveNameQueryResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/NodeStatistics.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/NodeStatistics.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `NodeStatistics`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class NodeStatistics`. Constants: `public const int Length = 46;`. Important fields include `public byte[] UnitID`, `public byte Jumpers`, `public byte TestResult`, `public ushort VersionNumber`, `public ushort PeriodOfStatistics`, `public ushort NumberOfCRCs`, `public ushort NumberOfAlignmentErrors`, `public ushort NumberOfCollisions`, `public ushort NumberOfSendAborts`, `public uint NumberOfGoodSends`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/NodeStatistics.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/QuestionSection.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/QuestionSection.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `QuestionSection`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class QuestionSection`. Important fields include `public string Name`, `public NameRecordType Type`, `public QuestionClass Class`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/QuestionSection.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/ResourceRecord.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/ResourceRecord.cs

## Purpose
Represents a NetBIOS name-service packet or packet substructure for `ResourceRecord`, preserving RFC 1002 field layout.

## Important APIs, Types, And Functions
Declarations: `public class ResourceRecord`. Important fields include `public string Name`, `public NameRecordType Type`, `public ResourceRecordClass Class`, `public uint TTL`, `public byte[] Data`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Name-service packet constructors parse the header, question/resource sections, and resource data in RFC order. `GetBytes` methods populate derived resource data first, then write header and sections to a memory stream using big-endian network fields and NetBIOS name encoding or name pointers where applicable.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `NetBiosUtils`, name-service enums, `NameFlags`, `QuestionSection`, `ResourceRecord`, and `NodeStatistics`. It integrates with NetBIOS name query, registration, and node-status client/server flows.

## Risks
Name compression support is write-only for explicit pointers; `DecodeName` rejects label lengths above 63 and does not follow compressed pointers, so compressed incoming names may fail. Resource data lengths and counts are trusted when parsing, making truncated or hostile packets dependent on lower-level bounds exceptions.

## Test Signals
Useful signals are RFC 1001/1002 sample name encodings, query/registration/node-status round trips, group and unique name flags, multiple address records, node-statistics length checks, pointer-written resource records, and truncated packet rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NameServicePackets/Structures/ResourceRecord.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NetBiosUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NetBiosUtils.cs

## Purpose
Implements Microsoft NetBIOS name shaping plus RFC 1001/1002 first-level and second-level name encoding/decoding.

## Important APIs, Types, And Functions
Declarations: `public class NetBiosUtils`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it also writes compressed name pointers for name-service resource records.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/NetBiosUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/Enums/SessionPacketTypeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/Enums/SessionPacketTypeName.cs

## Purpose
Defines protocol constants for `SessionPacketTypeName` used by adjacent NetBIOS or RPC packet serializers.

## Important APIs, Types, And Functions
Declarations: `public enum SessionPacketTypeName : byte`. Enum values include `{`, `SessionMessage = 0x00`, `SessionRequest = 0x81`, `PositiveSessionResponse = 0x82`, `NegativeSessionResponse = 0x83`, `RetargetSessionResponse = 0x84`, `SessionKeepAlive = 0x85`.

## Control Flow
Control flow is local parse/write logic over byte buffers with no asynchronous behavior.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on local protocol helpers and utility readers/writers.

## Risks
The type is low-level wire-format code with limited validation and should be covered by round-trip and malformed-input tests.

## Test Signals
Useful signals are byte fixture and round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/Enums/SessionPacketTypeName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/NegativeSessionResponsePacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/NegativeSessionResponsePacket.cs

## Purpose
Defines `NegativeSessionResponsePacket` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class NegativeSessionResponsePacket : SessionPacket`. Important fields include `public byte ErrorCode`. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/NegativeSessionResponsePacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/PositiveSessionResponsePacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/PositiveSessionResponsePacket.cs

## Purpose
Defines `PositiveSessionResponsePacket` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class PositiveSessionResponsePacket : SessionPacket`. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/PositiveSessionResponsePacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionKeepAlivePacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionKeepAlivePacket.cs

## Purpose
Defines `SessionKeepAlivePacket` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class SessionKeepAlivePacket : SessionPacket`. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionKeepAlivePacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionMessagePacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionMessagePacket.cs

## Purpose
Defines `SessionMessagePacket` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class SessionMessagePacket : SessionPacket`. Serialization surface: buffer constructors/read methods.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionMessagePacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionPacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionPacket.cs

## Purpose
Base class and factory for RFC 1002 NetBIOS session packets and Direct TCP transport packet framing.

## Important APIs, Types, And Functions
Declarations: `public abstract class SessionPacket`. Constants: `public const int HeaderLength = 4;`; `public const int MaxSessionPacketLength = 131075;`; `public const int MaxDirectTcpPacketLength = 16777215;`. Important fields include `public SessionPacketTypeName Type`, `public byte[] Trailer`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it parses the 4-byte type/length header, supports 17-bit NBT and 24-bit Direct TCP lengths, and dispatches by SessionPacketTypeName.

## Control Flow
The base constructor reads the session type and trailer length, the factory switches on type to instantiate concrete packet classes, and `GetBytes` rewrites the four-byte header from the current trailer length.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionPacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionRequestPacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionRequestPacket.cs

## Purpose
Defines `SessionRequestPacket` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class SessionRequestPacket : SessionPacket`. Important fields include `public string CalledName`, `public string CallingName`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately. Trailer-relative offsets must start at zero; offset reuse bugs would misparse trailer fields.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionRequestPacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionRetargetResponsePacket.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionRetargetResponsePacket.cs

## Purpose
Defines `SessionRetargetResponsePacket` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class SessionRetargetResponsePacket : SessionPacket`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
Concrete session packet classes set their `Type`, optionally decode the trailer into typed fields, rebuild `Trailer` in `GetBytes`, then delegate header writing to `SessionPacket`.

## State And Persistence
State is the packet fields or encoded name data for one NetBIOS packet. Network registration, cache, and session state are managed by callers; these classes only preserve fields needed for serialization.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SessionPacketTypeName`, concrete session packet classes, `NetBiosUtils`, `System.IO`, and optionally `ArrayPool<byte>`. It integrates with SMB over NetBIOS/TCP and Direct TCP receive/send framing.

## Risks
Session packet lengths are trusted after the four-byte header; callers must ensure the receive buffer is large enough for Direct TCP lengths or increase it deliberately. Trailer-relative offsets must start at zero; offset reuse bugs would misparse trailer fields.

## Test Signals
Useful signals are fragmented TCP receive tests, multiple packets in one buffer, partial following-packet compaction, keep-alive/positive/negative/request/retarget/message factory dispatch, Direct TCP large-length framing, and Dispose/ArrayPool behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NetBios/SessionPackets/SessionRetargetResponsePacket.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/EnumStructures/DataRepresentationFormat.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/EnumStructures/DataRepresentationFormat.cs

## Purpose
Models the DCE/RPC packed data representation label for character set, byte order, and floating-point representation.

## Important APIs, Types, And Functions
Declarations: `public enum CharacterFormat : byte`; `public enum ByteOrder : byte`; `public enum FloatingPointRepresentation : byte`; `public struct DataRepresentationFormat`. Important fields include `public CharacterFormat CharacterFormat`, `public ByteOrder ByteOrder`, `public FloatingPointRepresentation FloatingPointRepresentation`. Enum values include `{`, `ASCII = 0x00`, `EBCDIC = 0x01`, `{`, `BigEndian = 0x00`, `LittleEndian = 0x01`, `{`, `IEEE = 0x00`, `VAX = 0x01`, `Cray = 0x02`, `IBM = 0x03`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it packs character format in the low nibble and byte order in the high nibble of the first byte.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/EnumStructures/DataRepresentationFormat.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/FaultStatus.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/FaultStatus.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `FaultStatus` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public enum FaultStatus : uint`. Enum values include `{`, `OpRangeError = 0x1C010002`, `UnknownInterface = 0x1C010003`, `RPCVersionMismatch = 0x1C000008`, `ProtocolError = 0x1C01000B`.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/FaultStatus.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/NegotiationResult.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/NegotiationResult.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `NegotiationResult` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public enum NegotiationResult : ushort`. Enum values include `{`, `Acceptance`, `UserRejection`, `ProviderRejection`, `NegotiateAck`.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/NegotiationResult.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/PacketFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/PacketFlags.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `PacketFlags` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public enum PacketFlags : byte`. Enum values include `{`, `FirstFragment = 0x01`, `LastFragment = 0x02`, `PendingCancel = 0x04`, `ConcurrntMultiplexing = 0x10`, `DidNotExecute = 0x20`, `Maybe = 0x40`, `ObjectUUID = 0x80`.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/PacketFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/PacketTypeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/PacketTypeName.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `PacketTypeName` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public enum PacketTypeName : byte`. Enum values include `{`, `Request = 0x00`, `Response = 0x02`, `Fault = 0x03`, `Bind = 0x0B`, `BindAck = 0x0C`, `BindNak = 0x0D`, `AlterContext = 0x0E`, `AlterContextResponse = 0x0F`, `Shutdown = 0x11`, `COCancel = 0x12`, `Orphaned = 0x13`.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/PacketTypeName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/RejectionReason.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/RejectionReason.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `RejectionReason` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public enum RejectionReason : ushort`. Enum values include `{`, `NotSpecified`, `AbstractSyntaxNotSupported`, `ProposedTransferSyntaxesNotSupported`, `LocalLimitExceeded`.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Enums/RejectionReason.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/INDRStructure.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/INDRStructure.cs

## Purpose
Defines the minimal Read/Write contract for NDR-serializable structures.

## Important APIs, Types, And Functions
Declarations: `public interface INDRStructure`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it is implemented by NDRUnicodeString and generic conformant arrays.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/INDRStructure.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRConformantArray.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRConformantArray.cs

## Purpose
Implements a one-dimensional NDR conformant array of INDRStructure elements.

## Important APIs, Types, And Functions
Declarations: `public class NDRConformantArray`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it reads/writes max_count followed by each element inside BeginStructure/EndStructure deferral scope.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRConformantArray.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRParser.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRParser.cs

## Purpose
Reads little-endian NDR primitives, strings, structures, top-level full pointers, and embedded deferred referents.

## Important APIs, Types, And Functions
Declarations: `public class NDRParser`. Serialization surface: buffer constructors/read methods. Specific behavior: it tracks offset alignment, structure nesting depth, deferred structures, and referent id reuse.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is transient parser/writer offset or stream position, structure nesting depth, deferred referent list, and referent-id map. It persists only for one NDR stub encode/decode operation.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRParser.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRTypeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRTypeName.cs

## Purpose
Names supported NDR primitive/constructed helper types.

## Important APIs, Types, And Functions
Declarations: `public enum NDRTypeName`. Enum values include `{`, `UnicodeString`. Specific behavior: it currently contains UnicodeString as the only type marker.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRTypeName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRUnicodeString.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRUnicodeString.cs

## Purpose
Serializes and parses NDR conformant-varying UTF-16 strings with optional null termination.

## Important APIs, Types, And Functions
Declarations: `public class NDRUnicodeString : INDRStructure`. Important fields include `public string Value`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it reads max_count, offset, actual_count, then aligned 16-bit characters; writes the same sequence.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRUnicodeString.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRWriter.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRWriter.cs

## Purpose
Writes little-endian NDR primitives, strings, structures, full pointers, and deferred embedded referents.

## Important APIs, Types, And Functions
Declarations: `public class NDRWriter`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it tracks stream alignment, nested deferral, referent ids, and exposes GetBytes for produced stub data.

## Control Flow
NDR read/write flow is explicit and alignment-sensitive: structures call `BeginStructure`, read or write primitive fields through aligned parser/writer methods, register embedded pointer referents for deferred processing, and flush deferred structures when the outermost structure ends.

## State And Persistence
State is transient parser/writer offset or stream position, structure nesting depth, deferred referent list, and referent-id map. It persists only for one NDR stub encode/decode operation.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `MemoryStream`, `INDRStructure`, and NDR helper classes. It integrates with RPC request/response stub payload encoding used by higher SMBLibrary RPC clients.

## Risks
NDR alignment and deferred referent ordering are subtle; missing Begin/EndStructure calls or shared referent reuse can change wire layout. Parser methods trust declared counts, so malformed max_count/actual_count values can drive excessive reads or allocations in caller-owned structures.

## Test Signals
Useful signals are NDR round trips for Unicode strings with and without null terminators, conformant arrays, null and non-null top-level pointers, embedded deferred pointers, duplicate referent ids, and primitive alignment at odd offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/NDR/NDRWriter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindAckPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindAckPDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `BindAckPDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class BindAckPDU : RPCPDU`. Constants: `public const int BindAckFieldsFixedLength = 8;`. Important fields include `public ushort MaxTransmitFragmentSize`, `public ushort MaxReceiveFragmentSize`, `public uint AssociationGroupID`, `public ResultList ResultList`, `public byte[] AuthVerifier`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindAckPDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindNakPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindNakPDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `BindNakPDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class BindNakPDU : RPCPDU`. Constants: `public const int BindNakFieldsFixedLength = 2;`. Important fields include `public RejectionReason RejectReason`, `public VersionsSupported Versions`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindNakPDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindPDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `BindPDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class BindPDU : RPCPDU`. Constants: `public const int BindFieldsFixedLength = 8;`. Important fields include `public ushort MaxTransmitFragmentSize`, `public ushort MaxReceiveFragmentSize`, `public uint AssociationGroupID`, `public ContextList ContextList`, `public byte[] AuthVerifier`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/BindPDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/FaultPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/FaultPDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `FaultPDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class FaultPDU : RPCPDU`. Constants: `public const int FaultFieldsLength = 16;`. Important fields include `public uint AllocationHint`, `public ushort ContextID`, `public byte CancelCount`, `public byte Reserved`, `public FaultStatus Status`, `public uint Reserved2`, `public byte[] Data`, `public byte[] AuthVerifier`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/FaultPDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RPCPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RPCPDU.cs

## Purpose
Base class and factory for connection-oriented DCE/RPC PDUs.

## Important APIs, Types, And Functions
Declarations: `public abstract class RPCPDU`. Constants: `public const int CommonFieldsLength = 16;`. Important fields include `public byte VersionMajor`, `public byte VersionMinor`, `public PacketFlags Flags`, `public DataRepresentationFormat DataRepresentation`, `public ushort AuthLength`, `public uint CallID`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it parses common header fields, writes fragment/auth lengths, and dispatches concrete PDU types.

## Control Flow
Common parsing reads version, packet type, flags, data representation, fragment length, auth length, and call id. Static dispatch examines packet type and returns bind, bind-ack, bind-nak, request, response, or fault subclasses. Common writing updates fragment/auth lengths before subclass body serialization.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RPCPDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RequestPDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RequestPDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `RequestPDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class RequestPDU : RPCPDU`. Constants: `public const int RequestFieldsFixedLength = 8;`. Important fields include `public uint AllocationHint`, `public ushort ContextID`, `public ushort OpNum`, `public Guid ObjectGuid`, `public byte[] Data`, `public byte[] AuthVerifier`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/RequestPDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/ResponsePDU.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/ResponsePDU.cs

## Purpose
Represents the connection-oriented DCE/RPC `ResponsePDU` PDU variant, including common header fields plus variant-specific body data.

## Important APIs, Types, And Functions
Declarations: `public class ResponsePDU : RPCPDU`. Constants: `public const int ResponseFieldsLength = 8;`. Important fields include `public uint AllocationHint`, `public ushort ContextID`, `public byte CancelCount`, `public byte Reserved`, `public byte[] Data`, `public byte[] AuthVerifier`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The constructor parses common RPC fields first, advances to the variant body, reads fixed fields and variable payloads, and leaves authentication bytes in `AuthVerifier` when present. `GetBytes` sets `AuthLength`, allocates `Length`, writes common fields, then emits variant fields and payloads.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, RPC enums, `DataRepresentationFormat`, bind/result/context structures, syntax ids, and NDR payload producers/consumers. It integrates with connection-oriented MS-RPCE over SMB named pipes or TCP transports.

## Risks
Fragment length, auth length, and body offset math are trusted; malformed PDUs can produce negative or out-of-range data lengths if not prevalidated. Only little-endian NDR/common-field use is implemented in practice; unusual data representations are recorded but not generally used to switch reader endianness.

## Test Signals
Useful signals are bind/bind-ack/bind-nak/request/response/fault byte fixtures, first/last fragment flags, auth verifier lengths, context/result lists, object UUID request variants, fault status values, and rejection/versions-supported payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/PDU/ResponsePDU.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/RPCHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/RPCHelper.cs

## Purpose
Provides helpers for DCE/RPC port_any_t string structures.

## Important APIs, Types, And Functions
Declarations: `public class RPCHelper`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods. Specific behavior: it reads and writes little-endian length-prefixed null-terminated ANSI port addresses.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/RPCHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ContextElement.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ContextElement.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `ContextElement` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public class ContextElement`. Important fields include `public ushort ContextID`, `public byte Reserved`, `public SyntaxID AbstractSyntax`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ContextElement.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ContextList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ContextList.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `ContextList` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public class ContextList : List<ContextElement>`. Important fields include `public byte Reserved1`, `public ushort Reserved2`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ContextList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ResultElement.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ResultElement.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `ResultElement` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public struct ResultElement`. Constants: `public const int Length = 24;`. Important fields include `public NegotiationResult Result`, `public RejectionReason Reason`, `public SyntaxID TransferSyntax`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ResultElement.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ResultList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ResultList.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `ResultList` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public class ResultList : List<ResultElement>`. Important fields include `public byte Reserved`, `public ushort Reserved2`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/ResultList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/SyntaxID.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/SyntaxID.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `SyntaxID` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public struct SyntaxID`. Constants: `public const int Length = 20;`. Important fields include `public Guid InterfaceUUID`, `public uint InterfaceVersion`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/SyntaxID.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/Version.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/Version.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `Version` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public struct Version`. Constants: `public const int Length = 2;`. Important fields include `public byte Major`, `public byte Minor`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/Version.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/VersionsSupported.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/VersionsSupported.cs

## Purpose
Represents a DCE/RPC helper structure or enum named `VersionsSupported` used by bind negotiation, result lists, syntax ids, or fault handling.

## Important APIs, Types, And Functions
Declarations: `public class VersionsSupported`. Serialization surface: buffer constructors/read methods, `WriteBytes`/writer methods.

## Control Flow
Parsing and writing are fixed-layout DCE/RPC helpers. Lists read a leading count then loop over fixed or computed-length elements; writers derive the count from the current collection and advance offsets after each nested structure.

## State And Persistence
State is an in-memory representation of one RPC value, PDU, or helper list. Persistent protocol state such as association groups, context ids, and call ids is carried by fields but managed by higher layers.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers plus adjacent RPC enums and structures. It integrates with bind negotiation, bind rejection, syntax matching, version reporting, and endpoint port handling.

## Risks
List counts are byte-sized and trusted; oversized or truncated context/result lists rely on reader exceptions. Equality/hash behavior on syntax ids should remain stable because they may be used as dictionary keys or negotiation comparisons.

## Test Signals
Useful signals are fixed-length round trips, count-derived list lengths, syntax id equality/hash checks, negotiate-ack/result codes, fault/rejection enum mapping, and port address null-termination length accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/RPC/Structures/VersionsSupported.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CheckDirectoryRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CheckDirectoryRequest.cs

## Purpose
SMB_COM_CHECK_DIRECTORY request for validating a directory path encoded as an SMB_STRING data field.

## Important APIs, Types, And Functions
Declarations: `public class CheckDirectoryRequest : SMB1Command`. Constants: `public const byte SupportedBufferFormat = 0x04;`. Important fields include `public byte BufferFormat`, `public string DirectoryName`. `CommandName` returns `SMB_COM_CHECK_DIRECTORY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CheckDirectoryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CheckDirectoryResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CheckDirectoryResponse.cs

## Purpose
Empty SMB_COM_CHECK_DIRECTORY success response payload.

## Important APIs, Types, And Functions
Declarations: `public class CheckDirectoryResponse : SMB1Command`. `CommandName` returns `SMB_COM_CHECK_DIRECTORY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CheckDirectoryResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CloseRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CloseRequest.cs

## Purpose
SMB_COM_CLOSE request carrying FID and optional last-modified UTime.

## Important APIs, Types, And Functions
Declarations: `public class CloseRequest : SMB1Command`. Constants: `public const int ParametersLength = 6;`. Important fields include `public ushort FID`, `public DateTime? LastTimeModified`. `CommandName` returns `SMB_COM_CLOSE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CloseRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CloseResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CloseResponse.cs

## Purpose
Empty SMB_COM_CLOSE response payload.

## Important APIs, Types, And Functions
Declarations: `public class CloseResponse : SMB1Command`. `CommandName` returns `SMB_COM_CLOSE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CloseResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CreateDirectoryRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CreateDirectoryRequest.cs

## Purpose
SMB_COM_CREATE_DIRECTORY request carrying a directory name SMB_STRING.

## Important APIs, Types, And Functions
Declarations: `public class CreateDirectoryRequest : SMB1Command`. Constants: `public const byte SupportedBufferFormat = 0x04;`. Important fields include `public byte BufferFormat`, `public string DirectoryName`. `CommandName` returns `SMB_COM_CREATE_DIRECTORY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CreateDirectoryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CreateDirectoryResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CreateDirectoryResponse.cs

## Purpose
Empty SMB_COM_CREATE_DIRECTORY response payload.

## Important APIs, Types, And Functions
Declarations: `public class CreateDirectoryResponse : SMB1Command`. `CommandName` returns `SMB_COM_CREATE_DIRECTORY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/CreateDirectoryResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteDirectoryRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteDirectoryRequest.cs

## Purpose
SMB_COM_DELETE_DIRECTORY request carrying a directory name SMB_STRING.

## Important APIs, Types, And Functions
Declarations: `public class DeleteDirectoryRequest : SMB1Command`. Constants: `public const int SupportedBufferFormat = 0x04;`. Important fields include `public byte BufferFormat`, `public string DirectoryName`. `CommandName` returns `SMB_COM_DELETE_DIRECTORY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteDirectoryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteDirectoryResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteDirectoryResponse.cs

## Purpose
Empty SMB_COM_DELETE_DIRECTORY response payload.

## Important APIs, Types, And Functions
Declarations: `public class DeleteDirectoryResponse : SMB1Command`. `CommandName` returns `SMB_COM_DELETE_DIRECTORY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteDirectoryResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteRequest.cs

## Purpose
SMB_COM_DELETE request carrying search attributes and a file name SMB_STRING.

## Important APIs, Types, And Functions
Declarations: `public class DeleteRequest : SMB1Command`. Constants: `public const int SupportedBufferFormat = 0x04;`; `public const int ParametersLength = 2;`. Important fields include `public SMBFileAttributes SearchAttributes`, `public byte BufferFormat`, `public string FileName`. `CommandName` returns `SMB_COM_DELETE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteResponse.cs

## Purpose
Empty SMB_COM_DELETE response payload.

## Important APIs, Types, And Functions
Declarations: `public class DeleteResponse : SMB1Command`. `CommandName` returns `SMB_COM_DELETE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/DeleteResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/EchoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/EchoRequest.cs

## Purpose
SMB_COM_ECHO request carrying EchoCount and arbitrary echo data in SMBData.

## Important APIs, Types, And Functions
Declarations: `public class EchoRequest : SMB1Command`. Constants: `public const int ParametersLength = 2;`. Important fields include `public ushort EchoCount`. `CommandName` returns `SMB_COM_ECHO`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/EchoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/EchoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/EchoResponse.cs

## Purpose
SMB_COM_ECHO response carrying SequenceNumber and echoed data.

## Important APIs, Types, And Functions
Declarations: `public class EchoResponse : SMB1Command`. Constants: `public const int ParametersLength = 2;`. Important fields include `public ushort SequenceNumber`. `CommandName` returns `SMB_COM_ECHO`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/EchoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ErrorResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ErrorResponse.cs

## Purpose
Generic command-shaped response object used when an SMB header carries an error status and no command-specific payload is parsed.

## Important APIs, Types, And Functions
Declarations: `public class ErrorResponse : SMB1Command`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ErrorResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FindClose2Request.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FindClose2Request.cs

## Purpose
SMB_COM_FIND_CLOSE2 request closing a search handle.

## Important APIs, Types, And Functions
Declarations: `public class FindClose2Request : SMB1Command`. Constants: `public const int ParameterCount = 2;`. Important fields include `public ushort SearchHandle`. `CommandName` returns `SMB_COM_FIND_CLOSE2`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FindClose2Request.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FindClose2Response.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FindClose2Response.cs

## Purpose
Empty SMB_COM_FIND_CLOSE2 response payload.

## Important APIs, Types, And Functions
Declarations: `public class FindClose2Response : SMB1Command`. `CommandName` returns `SMB_COM_FIND_CLOSE2`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FindClose2Response.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FlushRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FlushRequest.cs

## Purpose
SMB_COM_FLUSH request carrying the FID to flush.

## Important APIs, Types, And Functions
Declarations: `public class FlushRequest : SMB1Command`. Constants: `public const int ParametersLength = 2;`. Important fields include `public ushort FID`. `CommandName` returns `SMB_COM_FLUSH`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FlushRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FlushResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FlushResponse.cs

## Purpose
Empty SMB_COM_FLUSH response payload.

## Important APIs, Types, And Functions
Declarations: `public class FlushResponse : SMB1Command`. `CommandName` returns `SMB_COM_FLUSH`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/FlushResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXRequest.cs

## Purpose
Defines `LockingRange` for SMBLibrary protocol serialization.

## Important APIs, Types, And Functions
Declarations: `public class LockingRange`; `public class LockingAndXRequest : SMBAndXCommand`. Constants: `public const int Length32 = 10;`; `public const int Length64 = 20;`; `public const int ParametersLength = 12;`. Important fields include `public ushort PID`, `public ulong ByteOffset`, `public ulong LengthInBytes`, `public ushort FID`, `public LockType TypeOfLock`, `public byte NewOpLockLevel`, `public uint Timeout`. `CommandName` returns `SMB_COM_LOCKING_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXResponse.cs

## Purpose
SMB_COM_LOCKING_ANDX response carrying only the AndX header fields.

## Important APIs, Types, And Functions
Declarations: `public class LockingAndXResponse : SMBAndXCommand`. Constants: `public const int ParametersLength = 4;`. `CommandName` returns `SMB_COM_LOCKING_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LockingAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LogoffAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LogoffAndXRequest.cs

## Purpose
SMB_COM_LOGOFF_ANDX request carrying only the AndX header fields.

## Important APIs, Types, And Functions
Declarations: `public class LogoffAndXRequest : SMBAndXCommand`. Constants: `public const int ParametersLength = 4;`. `CommandName` returns `SMB_COM_LOGOFF_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LogoffAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LogoffAndXResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LogoffAndXResponse.cs

## Purpose
SMB_COM_LOGOFF_ANDX response carrying only the AndX header fields.

## Important APIs, Types, And Functions
Declarations: `public class LogoffAndXResponse : SMBAndXCommand`. Constants: `public const int ParametersLength = 4;`. `CommandName` returns `SMB_COM_LOGOFF_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/LogoffAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCancelRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCancelRequest.cs

## Purpose
SMB_COM_NT_CANCEL request used to cancel an outstanding command with no body fields.

## Important APIs, Types, And Functions
Declarations: `public class NTCancelRequest : SMB1Command`. `CommandName` returns `SMB_COM_NT_CANCEL`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCancelRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXRequest.cs

## Purpose
SMB_COM_NT_CREATE_ANDX request for opening or creating files with NT access masks, create disposition/options, impersonation, security flags, and path.

## Important APIs, Types, And Functions
Declarations: `public class NTCreateAndXRequest : SMBAndXCommand`. Constants: `public const int ParametersLength = 48;`. Important fields include `public byte Reserved`, `public NTCreateFlags Flags`, `public uint RootDirectoryFID`, `public AccessMask DesiredAccess`, `public long AllocationSize`, `public ExtendedFileAttributes ExtFileAttributes`, `public ShareAccess ShareAccess`, `public CreateDisposition CreateDisposition`, `public CreateOptions CreateOptions`, `public ImpersonationLevel ImpersonationLevel`. `CommandName` returns `SMB_COM_NT_CREATE_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXResponse.cs

## Purpose
Standard SMB_COM_NT_CREATE_ANDX response with FID, oplock level, timestamps, attributes, allocation/eof sizes, resource type, pipe status, and directory flag.

## Important APIs, Types, And Functions
Declarations: `public class NTCreateAndXResponse : SMBAndXCommand`. Constants: `public const int ParametersLength = 68;`. Important fields include `public OpLockLevel OpLockLevel`, `public ushort FID`, `public CreateDisposition CreateDisposition`, `public DateTime? CreateTime`, `public DateTime? LastAccessTime`, `public DateTime? LastWriteTime`, `public DateTime? LastChangeTime`, `public ExtendedFileAttributes ExtFileAttributes`, `public long AllocationSize`, `public long EndOfFile`. `CommandName` returns `SMB_COM_NT_CREATE_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXResponseExtended.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXResponseExtended.cs

## Purpose
Extended NT_CREATE_ANDX response variant adding volume GUID, file id, and maximal access fields while preserving the Windows declared WordCount quirk.

## Important APIs, Types, And Functions
Declarations: `public class NTCreateAndXResponseExtended : SMBAndXCommand`. Constants: `public const int ParametersLength = 100;`; `public const int DeclaredParametersLength = 84;`. Important fields include `public OpLockLevel OpLockLevel`, `public ushort FID`, `public CreateDisposition CreateDisposition`, `public DateTime? CreateTime`, `public DateTime? LastAccessTime`, `public DateTime? LastWriteTime`, `public DateTime? LastChangeTime`, `public ExtendedFileAttributes ExtFileAttributes`, `public long AllocationSize`, `public long EndOfFile`. `CommandName` returns `SMB_COM_NT_CREATE_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTCreateAndXResponseExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactInterimResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactInterimResponse.cs

## Purpose
Zero-parameter interim response for multi-part SMB_COM_NT_TRANSACT processing.

## Important APIs, Types, And Functions
Declarations: `public class NTTransactInterimResponse : SMB1Command`. Constants: `public const int ParametersLength = 0;`. `CommandName` returns `SMB_COM_NT_TRANSACT`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Transaction parameter/data displacement and alignment bugs can corrupt multi-part transaction reconstruction.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactInterimResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactRequest.cs

## Purpose
Primary SMB_COM_NT_TRANSACT request with setup words and aligned transaction parameter/data blocks.

## Important APIs, Types, And Functions
Declarations: `public class NTTransactRequest : SMB1Command`. Constants: `public const int FixedSMBParametersLength = 38;`. Important fields include `public byte MaxSetupCount`, `public ushort Reserved1`, `public uint TotalParameterCount`, `public uint TotalDataCount`, `public uint MaxParameterCount`, `public uint MaxDataCount`, `public NTTransactSubcommandName Function`, `public byte[] Setup`, `public byte[] TransParameters`, `public byte[] TransData`. `CommandName` returns `SMB_COM_NT_TRANSACT`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Transaction parameter/data displacement and alignment bugs can corrupt multi-part transaction reconstruction.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactResponse.cs

## Purpose
SMB_COM_NT_TRANSACT response with total counts, displacements, setup, and aligned parameter/data blocks.

## Important APIs, Types, And Functions
Declarations: `public class NTTransactResponse : SMB1Command`. Constants: `public const int FixedSMBParametersLength = 36;`. Important fields include `public byte[] Reserved1`, `public uint TotalParameterCount`, `public uint TotalDataCount`, `public uint ParameterDisplacement`, `public uint DataDisplacement`, `public byte[] Setup`, `public byte[] TransParameters`, `public byte[] TransData`. `CommandName` returns `SMB_COM_NT_TRANSACT`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Transaction parameter/data displacement and alignment bugs can corrupt multi-part transaction reconstruction.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactSecondaryRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactSecondaryRequest.cs

## Purpose
Secondary SMB_COM_NT_TRANSACT request carrying later fragments and displacements for parameter/data blocks.

## Important APIs, Types, And Functions
Declarations: `public class NTTransactSecondaryRequest : SMB1Command`. Constants: `public const int SMBParametersLength = 36;`. Important fields include `public byte[] Reserved1`, `public uint TotalParameterCount`, `public uint TotalDataCount`, `public uint ParameterDisplacement`, `public uint DataDisplacement`, `public byte Reserved2`, `public byte[] TransParameters`, `public byte[] TransData`. `CommandName` returns `SMB_COM_NT_TRANSACT_SECONDARY`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Transaction parameter/data displacement and alignment bugs can corrupt multi-part transaction reconstruction.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NTTransactSecondaryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateRequest.cs

## Purpose
SMB_COM_NEGOTIATE request listing dialect strings in buffer-format-delimited data.

## Important APIs, Types, And Functions
Declarations: `public class NegotiateRequest : SMB1Command`. Constants: `public const int SupportedBufferFormat = 0x02;`. `CommandName` returns `SMB_COM_NEGOTIATE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponse.cs

## Purpose
Classic negotiate response with dialect index, security mode, limits, capabilities, server time, challenge, and optional domain/server strings.

## Important APIs, Types, And Functions
Declarations: `public class NegotiateResponse : SMB1Command`. Constants: `public const int ParametersLength = 34;`. Important fields include `public ushort DialectIndex`, `public SecurityMode SecurityMode`, `public ushort MaxMpxCount`, `public ushort MaxNumberVcs`, `public uint MaxBufferSize`, `public uint MaxRawSize`, `public uint SessionKey`, `public Capabilities Capabilities`, `public DateTime SystemTime`, `public short ServerTimeZone`. `CommandName` returns `SMB_COM_NEGOTIATE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponseExtended.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponseExtended.cs

## Purpose
Extended-security negotiate response with server GUID and security blob instead of challenge/domain strings.

## Important APIs, Types, And Functions
Declarations: `public class NegotiateResponseExtended : SMB1Command`. Constants: `public const int ParametersLength = 34;`. Important fields include `public ushort DialectIndex`, `public SecurityMode SecurityMode`, `public ushort MaxMpxCount`, `public ushort MaxNumberVcs`, `public uint MaxBufferSize`, `public uint MaxRawSize`, `public uint SessionKey`, `public Capabilities Capabilities`, `public DateTime SystemTime`, `public short ServerTimeZone`. `CommandName` returns `SMB_COM_NEGOTIATE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponseExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponseNotSupported.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponseNotSupported.cs

## Purpose
Negotiate response variant reporting dialects not supported with dialect index 0xFFFF.

## Important APIs, Types, And Functions
Declarations: `public class NegotiateResponseNotSupported : SMB1Command`. Constants: `public const int ParametersLength = 2;`; `public const ushort DialectsNotSupported = 0xFFFF;`. `CommandName` returns `SMB_COM_NEGOTIATE`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/NegotiateResponseNotSupported.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXRequest.cs

## Purpose
SMB_COM_OPEN_ANDX request for opening a path with flags, access mode, attributes, open mode, allocation size, and timeout.

## Important APIs, Types, And Functions
Declarations: `public class OpenAndXRequest : SMBAndXCommand`. Constants: `public const int ParametersLength = 30;`. Important fields include `public OpenFlags Flags`, `public AccessModeOptions AccessMode`, `public SMBFileAttributes SearchAttrs`, `public SMBFileAttributes FileAttrs`, `public DateTime? CreationTime`, `public OpenMode OpenMode`, `public uint AllocationSize`, `public uint Timeout`, `public uint Reserved`. `CommandName` returns `SMB_COM_OPEN_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXResponse.cs

## Purpose
SMB_COM_OPEN_ANDX response with FID, file attributes, UTime last-write, size, granted access, resource/pipe status, open result, and reserved bytes.

## Important APIs, Types, And Functions
Declarations: `public class OpenAndXResponse : SMBAndXCommand`. Constants: `public const int ParametersLength = 30;`. Important fields include `public ushort FID`, `public SMBFileAttributes FileAttrs`, `public DateTime? LastWriteTime`, `public uint FileDataSize`, `public AccessRights AccessRights`, `public ResourceType ResourceType`, `public NamedPipeStatus NMPipeStatus`, `public OpenResults OpenResults`, `public byte[] Reserved`. `CommandName` returns `SMB_COM_OPEN_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXResponseExtended.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXResponseExtended.cs

## Purpose
Extended OpenAndX response adding server FID and maximal access fields.

## Important APIs, Types, And Functions
Declarations: `public class OpenAndXResponseExtended : SMBAndXCommand`. Constants: `public const int ParametersLength = 38;`. Important fields include `public ushort FID`, `public SMBFileAttributes FileAttrs`, `public DateTime? LastWriteTime`, `public uint FileDataSize`, `public AccessRights AccessRights`, `public ResourceType ResourceType`, `public NamedPipeStatus NMPipeStatus`, `public OpenResults OpenResults`, `public uint ServerFID`, `public ushort Reserved`. `CommandName` returns `SMB_COM_OPEN_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/OpenAndXResponseExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationDiskRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationDiskRequest.cs

## Purpose
SMB_COM_QUERY_INFORMATION_DISK request with no command-specific payload.

## Important APIs, Types, And Functions
Declarations: `public class QueryInformationDiskRequest : SMB1Command`. `CommandName` returns `SMB_COM_QUERY_INFORMATION_DISK`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationDiskRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationDiskResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationDiskResponse.cs

## Purpose
SMB_COM_QUERY_INFORMATION_DISK response with total/free units, blocks per unit, block size, and reserved word.

## Important APIs, Types, And Functions
Declarations: `public class QueryInformationDiskResponse : SMB1Command`. Constants: `public const int ParameterLength = 10;`. Important fields include `public ushort TotalUnits`, `public ushort BlocksPerUnit`, `public ushort BlockSize`, `public ushort FreeUnits`, `public ushort Reserved`. `CommandName` returns `SMB_COM_QUERY_INFORMATION_DISK`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationDiskResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationRequest.cs

## Purpose
Deprecated SMB_COM_QUERY_INFORMATION request carrying a file name SMB_STRING.

## Important APIs, Types, And Functions
Declarations: `public class QueryInformationRequest : SMB1Command`. Constants: `public const byte SupportedBufferFormat = 0x04;`. Important fields include `public byte BufferFormat`, `public string FileName`. `CommandName` returns `SMB_COM_QUERY_INFORMATION`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationResponse.cs

## Purpose
Deprecated query-information response carrying file attributes, UTime last-write, file size, and reserved bytes.

## Important APIs, Types, And Functions
Declarations: `public class QueryInformationResponse : SMB1Command`. Constants: `public const int ParameterLength = 20;`. Important fields include `public SMBFileAttributes FileAttributes`, `public DateTime? LastWriteTime`, `public uint FileSize`, `public byte[] Reserved`. `CommandName` returns `SMB_COM_QUERY_INFORMATION`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/QueryInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadAndXRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadAndXRequest.cs

## Purpose
SMB_COM_READ_ANDX request with FID, 32/64-bit offset, min/max counts, remaining count, and large-read MaxCountHigh handling.

## Important APIs, Types, And Functions
Declarations: `public class ReadAndXRequest : SMBAndXCommand`. Constants: `public const int ParametersFixedLength = 20;`. Important fields include `public ushort FID`, `public ulong Offset`, `public ushort MinCountOfBytesToReturn`, `public uint Timeout_or_MaxCountHigh`, `public ushort Remaining`. `CommandName` returns `SMB_COM_READ_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadAndXResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadAndXResponse.cs

## Purpose
SMB_COM_READ_ANDX response with data offset/length, optional unicode padding, high data length, reserved bytes, and read data.

## Important APIs, Types, And Functions
Declarations: `public class ReadAndXResponse : SMBAndXCommand`. Constants: `public const int ParametersLength = 24;`. Important fields include `public ushort Available`, `public ushort DataCompactionMode`, `public ushort Reserved1`, `public byte[] Reserved2`, `public byte[] Data`. `CommandName` returns `SMB_COM_READ_ANDX`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Extended variants share command names and are selected by length/WordCount, making regression tests for both classic and extended forms important.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadRequest.cs

## Purpose
Legacy SMB_COM_READ request with FID, byte count, 32-bit offset, and estimated remaining count.

## Important APIs, Types, And Functions
Declarations: `public class ReadRequest : SMB1Command`. Constants: `public const int ParametersLength = 10;`. Important fields include `public ushort FID`, `public ushort CountOfBytesToRead`, `public uint ReadOffsetInBytes`, `public ushort EstimateOfRemainingBytesToBeRead`. `CommandName` returns `SMB_COM_READ`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadResponse.cs

## Purpose
Legacy SMB_COM_READ response with returned count, buffer format/count pair, reserved bytes, and read bytes.

## Important APIs, Types, And Functions
Declarations: `public class ReadResponse : SMB1Command`. Constants: `public const int ParametersLength = 10;`; `public const int SupportedBufferFormat = 0x01;`. Important fields include `public ushort CountOfBytesReturned`, `public byte[] Reserved`, `public byte BufferFormat`, `public byte[] Bytes`. `CommandName` returns `SMB_COM_READ`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/ReadResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/RenameRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/RenameRequest.cs

## Purpose
SMB_COM_RENAME request with search attributes and old/new SMB_STRING names, including Unicode alignment before the second name.

## Important APIs, Types, And Functions
Declarations: `public class RenameRequest : SMB1Command`. Constants: `public const int SupportedBufferFormat = 0x04;`; `public const int ParametersLength = 2;`. Important fields include `public SMBFileAttributes SearchAttributes`, `public byte BufferFormat1`, `public byte BufferFormat2`. `CommandName` returns `SMB_COM_RENAME`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/RenameRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/RenameResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/RenameResponse.cs

## Purpose
Empty SMB_COM_RENAME response payload.

## Important APIs, Types, And Functions
Declarations: `public class RenameResponse : SMB1Command`. `CommandName` returns `SMB_COM_RENAME`, which is used by `SMB1Command` dispatch and SMB header command matching. Serialization surface: buffer constructors/read methods.

## Control Flow
The parse constructor delegates SMB parameter/data framing to `SMB1Command` or `SMBAndXCommand`, then reads command-specific fields from `SMBParameters` and `SMBData`. `GetBytes` rebuilds those arrays from public fields, applies SMB string Unicode alignment where required, and delegates final framing to the base class.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate.

## Test Signals
Useful signals are command-specific byte fixtures, parse/serialize round trips in Unicode and OEM modes where applicable, empty success response bodies, command-name dispatch, WordCount/ByteCount verification, timestamp conversion, and malformed short-buffer tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/RenameResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMB1Command.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMB1Command.cs

## Purpose
Abstract base and parser dispatch for SMB1 command payloads.

## Important APIs, Types, And Functions
Declarations: `public abstract class SMB1Command`. Serialization surface: buffer constructors/read methods, `GetBytes`, `WriteBytes`/writer methods. Specific behavior: it owns WordCount/SMBParameters/ByteCount/SMBData framing, request/response factories, and known WordCount quirks.

## Control Flow
The base constructor reads WordCount, SMBParameters, ByteCount, and SMBData. `GetBytes` validates an even parameter length, computes WordCount and ByteCount, handles the NT_CREATE_ANDX extended declared WordCount exception, and writes the framed command body. Static request/response dispatch switches on `CommandName` and WordCount to choose concrete command classes or `ErrorResponse`.

## State And Persistence
State lives in public command fields plus protected `SMBParameters` and `SMBData` byte arrays inherited from `SMB1Command`. Instances represent one decoded or to-be-encoded SMB message body; they do not own file handles, network sockets, or durable server state.

## Dependencies And Integration Points
Depends on `Utilities.ByteReader`/`ByteWriter` and endian-specific converter/writer helpers, `SMB1Helper`, `SMB1Header`, command enums, file/access/time helper enums, AndX base framing, and transaction/create/open/read helper types. It integrates with SMB1 packet parsing and command construction in client and server code.

## Risks
SMB1 wire layout is offset-heavy. Unicode padding, ByteCount, WordCount, AndX offsets, transaction parameter/data offsets, and large-read/create variants must remain byte-accurate. Dispatch falls back to `ErrorResponse` for unrecognized WordCount variants, so adding new command variants requires updating both request and response factories.

## Test Signals
Useful signals are request/response factory tests for every supported command, classic versus extended WordCount variants, error-status fallback, even parameter length validation, and NT_CREATE_ANDX declared WordCount handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMB1Command.cs -->
