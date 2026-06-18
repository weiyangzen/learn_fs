# Group Research: subset-b-010022

Work item `subset-b-010022` covers 129 SMBLibrary SMB1 command, transaction, enum, and helper C# source files. Each section below is marker-delimited for reconciliation and split into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMBAndXCommand.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMBAndXCommand.cs

- **Purpose:** Defines SMBAndXCommand for the SMB1 command packet layer. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1650 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMBAndXCommand`.
- **Important APIs/types/functions:** Types: class SMBAndXCommand : SMB1Command. Constructors: SMBAndXCommand. Constants/static metadata: none. Fields/properties: AndXCommand, AndXReserved, AndXOffset. Methods/overrides: GetBytes, WriteAndXOffset.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMBAndXCommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SMBAndXCommand.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXRequest.cs

- **Purpose:** SMB_COM_SESSION_SETUP_ANDX Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 123 lines, 6268 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SessionSetupAndXRequest`.
- **Important APIs/types/functions:** Types: class SessionSetupAndXRequest : SMBAndXCommand. Constructors: SessionSetupAndXRequest. Constants/static metadata: ParametersLength. Fields/properties: MaxBufferSize, MaxMpxCount, VcNumber, SessionKey, OEMPasswordLength, UnicodePasswordLength, Reserved, Capabilities, OEMPassword, UnicodePassword, AccountName, PrimaryDomain, NativeOS, NativeLanMan. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SESSION_SETUP_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SESSION_SETUP_ANDX to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXRequestExtended.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXRequestExtended.cs

- **Purpose:** SMB_COM_SESSION_SETUP_ANDX Extended Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 106 lines, 4792 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SessionSetupAndXRequestExtended`.
- **Important APIs/types/functions:** Types: class SessionSetupAndXRequestExtended : SMBAndXCommand. Constructors: SessionSetupAndXRequestExtended. Constants/static metadata: ParametersLength. Fields/properties: MaxBufferSize, MaxMpxCount, VcNumber, SessionKey, SecurityBlobLength, Reserved, Capabilities, SecurityBlob, NativeOS, NativeLanMan. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SESSION_SETUP_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SESSION_SETUP_ANDX to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXRequestExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXResponse.cs

- **Purpose:** SMB_COM_SESSION_SETUP_ANDX Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 91 lines, 3812 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SessionSetupAndXResponse`.
- **Important APIs/types/functions:** Types: class SessionSetupAndXResponse : SMBAndXCommand. Constructors: SessionSetupAndXResponse. Constants/static metadata: ParametersLength. Fields/properties: Action, NativeOS, NativeLanMan, PrimaryDomain. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SESSION_SETUP_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SESSION_SETUP_ANDX to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXResponseExtended.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXResponseExtended.cs

- **Purpose:** SMB_COM_SESSION_SETUP_ANDX Response, NT LAN Manager dialect, Extended Security response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 99 lines, 4171 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SessionSetupAndXResponseExtended`.
- **Important APIs/types/functions:** Types: class SessionSetupAndXResponseExtended : SMBAndXCommand. Constructors: SessionSetupAndXResponseExtended. Constants/static metadata: ParametersLength. Fields/properties: Action, SecurityBlobLength, SecurityBlob, NativeOS, NativeLanMan. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SESSION_SETUP_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SESSION_SETUP_ANDX to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SessionSetupAndXResponseExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformation2Request.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformation2Request.cs

- **Purpose:** SMB_COM_SET_INFORMATION2 Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 57 lines, 2291 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SetInformation2Request`.
- **Important APIs/types/functions:** Types: class SetInformation2Request : SMB1Command. Constructors: SetInformation2Request. Constants/static metadata: ParametersLength. Fields/properties: FID, CreationDateTime, LastAccessDateTime, LastWriteDateTime. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SET_INFORMATION2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMB1Helper. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SET_INFORMATION2 to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformation2Request.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformation2Response.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformation2Response.cs

- **Purpose:** SMB_COM_SET_INFORMATION2 Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 40 lines, 1058 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SetInformation2Response`.
- **Important APIs/types/functions:** Types: class SetInformation2Response : SMB1Command. Constructors: SetInformation2Response. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SET_INFORMATION2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SET_INFORMATION2 to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformation2Response.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformationRequest.cs

- **Purpose:** SMB_COM_SET_INFORMATION Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 80 lines, 2801 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SetInformationRequest`.
- **Important APIs/types/functions:** Types: class SetInformationRequest : SMB1Command. Constructors: SetInformationRequest. Constants/static metadata: ParametersLength, SupportedBufferFormat. Fields/properties: FileAttributes, LastWriteTime, Reserved, BufferFormat, FileName. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SET_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding. UTIME fields are converted between SMB seconds-since-1970 values and nullable DateTime values.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMB1Helper, UTimeHelper. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString, UTimeHelper.ReadNullableUTime, UTimeHelper.WriteUTime.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SET_INFORMATION to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException(Unsupported Buffer Format).
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformationResponse.cs

- **Purpose:** SMB_COM_SET_INFORMATION Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 40 lines, 1053 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SetInformationResponse`.
- **Important APIs/types/functions:** Types: class SetInformationResponse : SMB1Command. Constructors: SetInformationResponse. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_SET_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_SET_INFORMATION to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/SetInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2InterimResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2InterimResponse.cs

- **Purpose:** Parses and serializes the Transaction2InterimResponse wire response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 31 lines, 854 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2InterimResponse`.
- **Important APIs/types/functions:** Types: class Transaction2InterimResponse : TransactionInterimResponse. Constructors: Transaction2InterimResponse. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION2.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION2 to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2InterimResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Request.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Request.cs

- **Purpose:** SMB_COM_TRANSACTION2 Request The SMB_COM_TRANSACTION2 request format is similar to that of the SMB_COM_TRANSACTION request except for the Name field. The differences are in the subcommands supported, and in the purposes and usages of some. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 37 lines, 1183 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Request`.
- **Important APIs/types/functions:** Types: class Transaction2Request : TransactionRequest. Constructors: Transaction2Request. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION2.
- **Control flow:** It reuses the generic transaction request parse/serialize path and changes only the SMB command discriminator.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionRequest.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION2 to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Request.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Response.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Response.cs

- **Purpose:** SMB_COM_TRANSACTION2 Response The SMB_COM_TRANSACTION2 response format is identical to that of the SMB_COM_TRANSACTION response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 36 lines, 1027 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Response`.
- **Important APIs/types/functions:** Types: class Transaction2Response : TransactionResponse. Constructors: Transaction2Response. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION2.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionResponse.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION2 to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2Response.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2SecondaryRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2SecondaryRequest.cs

- **Purpose:** SMB_COM_TRANSACTION2_SECONDARY Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 81 lines, 3615 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SecondaryRequest`.
- **Important APIs/types/functions:** Types: class Transaction2SecondaryRequest : TransactionSecondaryRequest. Constructors: Transaction2SecondaryRequest. Constants/static metadata: none. Fields/properties: FID. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION2_SECONDARY.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Header. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION2_SECONDARY to the message layer.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/Transaction2SecondaryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionInterimResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionInterimResponse.cs

- **Purpose:** SMB_COM_TRANSACTION Interim Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 41 lines, 1094 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionInterimResponse`.
- **Important APIs/types/functions:** Types: class TransactionInterimResponse : SMB1Command. Constructors: TransactionInterimResponse. Constants/static metadata: ParametersLength. Fields/properties: none detected. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionInterimResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionRequest.cs

- **Purpose:** SMB_COM_TRANSACTION Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 173 lines, 7734 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionRequest`.
- **Important APIs/types/functions:** Types: class TransactionRequest : SMB1Command. Constructors: TransactionRequest. Constants/static metadata: FixedSMBParametersLength. Fields/properties: TotalParameterCount, TotalDataCount, MaxParameterCount, MaxDataCount, MaxSetupCount, Reserved1, Flags, Timeout, Reserved2, Reserved3, Setup, Name, TransParameters, TransData. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION.
- **Control flow:** Parsing reads total/count/offset fields from SMB_Parameters, then slices transaction parameters and data from absolute offsets in the containing SMB message. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMB1Header, SMB1Helper, TransactionRequest. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION to the message layer.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** Exception(Setup length must be a multiple of 2).
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionResponse.cs

- **Purpose:** SMB_COM_TRANSACTION Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 126 lines, 5960 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionResponse`.
- **Important APIs/types/functions:** Types: class TransactionResponse : SMB1Command. Constructors: TransactionResponse. Constants/static metadata: FixedSMBParametersLength. Fields/properties: TotalParameterCount, TotalDataCount, Reserved1, ParameterDisplacement, DataDisplacement, Reserved2, Setup, TransParameters, TransData. Methods/overrides: GetBytes, CalculateMessageSize. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION.
- **Control flow:** Serialization recalculates parameter/data counts, four-byte padding, and absolute offsets before delegating to the base SMB command frame writer. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMB1Header, TransactionResponse. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION to the message layer.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** ArgumentException(Invalid Trans_Data length).
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionSecondaryRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionSecondaryRequest.cs

- **Purpose:** SMB_COM_TRANSACTION_SECONDARY Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 92 lines, 4038 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionSecondaryRequest`.
- **Important APIs/types/functions:** Types: class TransactionSecondaryRequest : SMB1Command. Constructors: TransactionSecondaryRequest. Constants/static metadata: SMBParametersLength. Fields/properties: TotalParameterCount, TotalDataCount, ParameterCount, ParameterOffset, ParameterDisplacement, DataCount, DataOffset, DataDisplacement, TransParameters, TransData. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TRANSACTION_SECONDARY.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMB1Header. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TRANSACTION_SECONDARY to the message layer.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TransactionSecondaryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXRequest.cs

- **Purpose:** SMB_COM_TREE_CONNECT_ANDX Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 97 lines, 3742 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeConnectAndXRequest`.
- **Important APIs/types/functions:** Types: class TreeConnectAndXRequest : SMBAndXCommand. Constructors: TreeConnectAndXRequest. Constants/static metadata: ParametersLength. Fields/properties: Flags, Password, Path, Service. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TREE_CONNECT_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianReader.ReadUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString, ServiceNameHelper.GetServiceName, ServiceNameHelper.GetServiceString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TREE_CONNECT_ANDX to the message layer. Converts between service enum values and the OEM service strings exchanged by tree-connect packets.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXResponse.cs

- **Purpose:** SMB_COM_TREE_CONNECT_ANDX Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 75 lines, 2660 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeConnectAndXResponse`.
- **Important APIs/types/functions:** Types: class TreeConnectAndXResponse : SMBAndXCommand. Constructors: TreeConnectAndXResponse. Constants/static metadata: ParametersLength. Fields/properties: OptionalSupport, Service, NativeFileSystem. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TREE_CONNECT_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString, ServiceNameHelper.GetServiceName, ServiceNameHelper.GetServiceString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TREE_CONNECT_ANDX to the message layer. Converts between service enum values and the OEM service strings exchanged by tree-connect packets.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXResponseExtended.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXResponseExtended.cs

- **Purpose:** SMB_COM_TREE_CONNECT_ANDX Extended Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 83 lines, 3413 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeConnectAndXResponseExtended`.
- **Important APIs/types/functions:** Types: class TreeConnectAndXResponseExtended : SMBAndXCommand. Constructors: TreeConnectAndXResponseExtended. Constants/static metadata: ParametersLength. Fields/properties: OptionalSupport, MaximalShareAccessRights, GuestMaximalShareAccessRights, Service, NativeFileSystem. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_TREE_CONNECT_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Helper, AccessMask. Wire helpers observed: LittleEndianReader.ReadUInt16, LittleEndianReader.ReadUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString, ServiceNameHelper.GetServiceName, ServiceNameHelper.GetServiceString.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TREE_CONNECT_ANDX to the message layer. Converts between service enum values and the OEM service strings exchanged by tree-connect packets.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeConnectAndXResponseExtended.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectRequest.cs

- **Purpose:** SMB_COM_TREE_DISCONNECT Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 35 lines, 927 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeDisconnectRequest`.
- **Important APIs/types/functions:** Types: class TreeDisconnectRequest : SMB1Command. Constructors: TreeDisconnectRequest. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TREE_DISCONNECT.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TREE_DISCONNECT to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectResponse.cs

- **Purpose:** SMB_COM_TREE_DISCONNECT Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 35 lines, 939 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeDisconnectResponse`.
- **Important APIs/types/functions:** Types: class TreeDisconnectResponse : SMB1Command. Constructors: TreeDisconnectResponse. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: CommandName.SMB_COM_TREE_DISCONNECT.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_TREE_DISCONNECT to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/TreeDisconnectResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteAndXRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteAndXRequest.cs

- **Purpose:** SMB_COM_WRITE_ANDX Request SMB 1.0: The 2 reserved bytes at offset 18 become DataLengthHigh (used when the CAP_LARGE_WRITEX capability has been negotiated). It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 118 lines, 4664 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteAndXRequest`.
- **Important APIs/types/functions:** Types: class WriteAndXRequest : SMBAndXCommand. Constructors: WriteAndXRequest. Constants/static metadata: ParametersFixedLength. Fields/properties: FID, Offset, Timeout, WriteMode, Remaining, Data. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand, SMB1Header. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE_ANDX to the message layer.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Correctness depends on exact WordCount/setup length handling. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteAndXRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteAndXResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteAndXResponse.cs

- **Purpose:** SMB_COM_WRITE_ANDX Response SMB 1.0: The 2 reserved bytes at offset 8 become CountHigh (used when the CAP_LARGE_WRITEX capability has been negotiated). It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 63 lines, 2295 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteAndXResponse`.
- **Important APIs/types/functions:** Types: class WriteAndXResponse : SMBAndXCommand. Constructors: WriteAndXResponse. Constants/static metadata: ParametersLength. Fields/properties: Count, Available, Reserved. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE_ANDX.
- **Control flow:** AndX packets reserve the first four parameter bytes for next-command id, reserved byte, and absolute next-command offset. Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMBAndXCommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE_ANDX to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteAndXResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawFinalResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawFinalResponse.cs

- **Purpose:** SMB_COM_WRITE_RAW Final Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1352 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteRawFinalResponse`.
- **Important APIs/types/functions:** Types: class WriteRawFinalResponse : SMB1Command. Constructors: WriteRawFinalResponse. Constants/static metadata: ParametersLength. Fields/properties: Count. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE_COMPLETE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE_COMPLETE to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawFinalResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawInterimResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawInterimResponse.cs

- **Purpose:** SMB_COM_WRITE_RAW Interim Response. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1367 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteRawInterimResponse`.
- **Important APIs/types/functions:** Types: class WriteRawInterimResponse : SMB1Command. Constructors: WriteRawInterimResponse. Constants/static metadata: ParametersLength. Fields/properties: Available. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE_RAW.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE_RAW to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawInterimResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawRequest.cs

- **Purpose:** SMB_COM_WRITE_RAW Request. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 71 lines, 2510 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteRawRequest`.
- **Important APIs/types/functions:** Types: class WriteRawRequest : SMB1Command. Constructors: WriteRawRequest. Constants/static metadata: ParametersFixedLength. Fields/properties: FID, CountOfBytes, Reserved1, Offset, Timeout, WriteMode, Reserved2, OffsetHigh, Data. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE_RAW.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Some outbound methods intentionally stop with NotImplementedException, so this type currently supports inbound parsing more than full serialization.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE_RAW to the message layer.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Correctness depends on exact WordCount/setup length handling. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. NotImplementedException blocks full round-trip serialization for this type.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures, tests asserting unsupported serialization paths throw NotImplementedException.
- **Explicit failure paths:** NotImplementedException.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRawRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRequest.cs

- **Purpose:** SMB_COM_WRITE Request. This command is obsolete. Windows NT4 SP6 will send this command with empty data for some reason. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 83 lines, 3156 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteRequest`.
- **Important APIs/types/functions:** Types: class WriteRequest : SMB1Command. Constructors: WriteRequest. Constants/static metadata: ParametersLength, SupportedBufferFormat. Fields/properties: FID, CountOfBytesToWrite, WriteOffsetInBytes, EstimateOfRemainingBytesToBeWritten, BufferFormat, Data. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException(Unsupported Buffer Format), ArgumentException(Invalid Data length).
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteResponse.cs

- **Purpose:** SMB_COM_WRITE Response. This command is obsolete. Windows NT4 SP6 will send this command with empty data for some reason. It is part of the SMB1 command packet surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 44 lines, 1160 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteResponse`.
- **Important APIs/types/functions:** Types: class WriteResponse : SMB1Command. Constructors: WriteResponse. Constants/static metadata: ParametersLength. Fields/properties: CountOfBytesWritten. Methods/overrides: GetBytes. Protocol discriminator returns: CommandName.SMB_COM_WRITE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. The important transient buffers are SMBParameters and SMBData, which mirror SMB_Parameters and SMB_Data on the wire. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Command. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Instantiated through SMB1Command.ReadCommand based on SMB1Header.Command and the reply flag, then serialized by SMB1Message. Advertises CommandName.SMB_COM_WRITE to the message layer.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Commands/WriteResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/NamedPipeStatus.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/NamedPipeStatus.cs

- **Purpose:** SMB_NMPIPE_STATUS. It is part of the packed SMB1 enum/bitfield structure surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 97 lines, 3000 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ReadMode`.
- **Important APIs/types/functions:** Types: enum ReadMode : byte, enum NamedPipeType : byte, enum Endpoint : byte, enum NonBlocking : byte, struct NamedPipeStatus. Constructors: NamedPipeStatus. Constants/static metadata: Length. Fields/properties: ICount, ReadMode, NamedPipeType, Endpoint, NonBlocking. Methods/overrides: WriteBytes, ToUInt16, Read. Enum values: ByteMode=0x00, MessageMode=0x01, ByteModePipe=0x00, MessageModePipe=0x01, ClientSideEnd=0x00, ServerSideEnd=0x01, Block=0x00, DoNotBlock=0x01.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/NamedPipeStatus.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/OpenResults.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/OpenResults.cs

- **Purpose:** Defines OpenResults for the packed SMB1 enum/bitfield structure layer. It is part of the packed SMB1 enum/bitfield structure surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 52 lines, 1454 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpenResults`.
- **Important APIs/types/functions:** Types: struct OpenResults. Constructors: OpenResults. Constants/static metadata: Length. Fields/properties: OpenResult, OpLockGranted. Methods/overrides: WriteBytes, Read.
- **Control flow:** Constructors decode packed bytes or integers into fields; WriteBytes and conversion helpers repack those fields into the SMB wire layout.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/EnumStructures/OpenResults.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/CommandName.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/CommandName.cs

- **Purpose:** Defines protocol constants for CommandName. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 42 lines, 1413 bytes. Namespace `SMBLibrary.SMB1`. Primary type `CommandName`.
- **Important APIs/types/functions:** Types: enum CommandName : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_COM_CREATE_DIRECTORY=0x00, SMB_COM_DELETE_DIRECTORY=0x01, SMB_COM_CLOSE=0x04, SMB_COM_FLUSH=0x05, SMB_COM_DELETE=0x06, SMB_COM_RENAME=0x07, SMB_COM_QUERY_INFORMATION=0x08, SMB_COM_SET_INFORMATION=0x09, SMB_COM_READ=0x0A, SMB_COM_WRITE=0x0B, SMB_COM_CHECK_DIRECTORY=0x10, SMB_COM_WRITE_RAW=0x1D, SMB_COM_WRITE_COMPLETE=0x20, SMB_COM_SET_INFORMATION2=0x22, SMB_COM_LOCKING_ANDX=0x24, SMB_COM_TRANSACTION=0x25, SMB_COM_TRANSACTION_SECONDARY=0x26, SMB_COM_ECHO=0x2B, SMB_COM_OPEN_ANDX=0x2D, SMB_COM_READ_ANDX=0x2E, SMB_COM_WRITE_ANDX=0x2F, SMB_COM_TRANSACTION2=0x32, SMB_COM_TRANSACTION2_SECONDARY=0x33, SMB_COM_FIND_CLOSE2=0x34, SMB_COM_TREE_DISCONNECT=0x71, SMB_COM_NEGOTIATE=0x72, SMB_COM_SESSION_SETUP_ANDX=0x73, SMB_COM_LOGOFF_ANDX=0x74, SMB_COM_TREE_CONNECT_ANDX=0x75, SMB_COM_QUERY_INFORMATION_DISK=0x80, SMB_COM_NT_TRANSACT=0xA0, SMB_COM_NT_TRANSACT_SECONDARY=0xA1, SMB_COM_NT_CREATE_ANDX=0xA2, SMB_COM_NT_CANCEL=0xA4, SMB_COM_NO_ANDX_COMMAND=0xFF.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/CommandName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ExtendedFileAttributes.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ExtendedFileAttributes.cs

- **Purpose:** SMB_EXT_FILE_ATTR. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 36 lines, 1527 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ExtendedFileAttributes`.
- **Important APIs/types/functions:** Types: enum ExtendedFileAttributes : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: ReadOnly=0x00000001, Hidden=0x00000002, System=0x00000004, Directory=0x00000010, Archive=0x00000020, Normal=0x00000080, Temporary=0x00000100, Sparse=0x00000200, ReparsePoint=0x00000400, Compressed=0x00000800, Offline=0x00001000, NotIndexed=0x00002000, Encrypted=0x00004000, PosixSemantics=0x01000000, BackupSemantics=0x02000000, DeleteOnClose=0x04000000, SequentialScan=0x08000000, RandomAccess=0x10000000, NoBuffering=0x10000000, WriteThrough=0x80000000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ExtendedFileAttributes.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags.cs

- **Purpose:** Defines protocol constants for HeaderFlags. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 14 lines, 376 bytes. Namespace `SMBLibrary.SMB1`. Primary type `HeaderFlags`.
- **Important APIs/types/functions:** Types: enum HeaderFlags : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: LockAndRead=0x01, CaseInsensitive=0x08, CanonicalizedPaths=0x10, Oplock=0x20, Reply=0x80.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags2.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags2.cs

- **Purpose:** Indicates that the client or server supports extended security. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 25 lines, 944 bytes. Namespace `SMBLibrary.SMB1`. Primary type `HeaderFlags2`.
- **Important APIs/types/functions:** Types: enum HeaderFlags2 : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: LongNamesAllowed=0x0001, ExtendedAttributes=0x0002, SecuritySignature=0x0004, CompressedData=0x0008, SecuritySignatureRequired=0x0010, LongNameUsed=0x0040, ReparsePath=0x400, ExtendedSecurity=0x0800, DFS=0x1000, ReadIfExecute=0x2000, NTStatusCode=0x4000, Unicode=0x8000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/HeaderFlags2.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Locking/LockType.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Locking/LockType.cs

- **Purpose:** Request to cancel all outstanding lock requests for the specified FID and PID. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 24 lines, 669 bytes. Namespace `SMBLibrary.SMB1`. Primary type `LockType`.
- **Important APIs/types/functions:** Types: enum LockType : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: READ_WRITE_LOCK=0x00, SHARED_LOCK=0x01, OPLOCK_RELEASE=0x02, CHANGE_LOCKTYPE=0x04, CANCEL_LOCK=0x08, LARGE_FILES=0x10.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Locking/LockType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/FileStatusFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/FileStatusFlags.cs

- **Purpose:** Defines protocol constants for FileStatusFlags. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 12 lines, 193 bytes. Namespace `SMBLibrary.SMB1`. Primary type `FileStatusFlags`.
- **Important APIs/types/functions:** Types: enum FileStatusFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NO_EAS=0x01, NO_SUBSTREAMS=0x02, NO_REPARSETAG=0x04.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/FileStatusFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/NTCreateFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/NTCreateFlags.cs

- **Purpose:** If set, the client requests an exclusive OpLock. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 20 lines, 554 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTCreateFlags`.
- **Important APIs/types/functions:** Types: enum NTCreateFlags : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NT_CREATE_REQUEST_OPLOCK=0x00000002, NT_CREATE_REQUEST_OPBATCH=0x00000004, NT_CREATE_OPEN_TARGET_DIR=0x00000008, NT_CREATE_REQUEST_EXTENDED_RESPONSE=0x00000010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/NTCreateFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/OpLockLevel.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/OpLockLevel.cs

- **Purpose:** Defines protocol constants for OpLockLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 220 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpLockLevel`.
- **Important APIs/types/functions:** Types: enum OpLockLevel : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NoOpLockGranted=0x00, ExclusiveOpLockGranted=0x01, BatchOpLockGranted=0x02, Level2OpLockGranted=0x03.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/OpLockLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/SecurityFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/SecurityFlags.cs

- **Purpose:** Defines protocol constants for SecurityFlags. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 10 lines, 184 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SecurityFlags`.
- **Important APIs/types/functions:** Types: enum SecurityFlags : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_SECURITY_CONTEXT_TRACKING=0x01, SMB_SECURITY_EFFECTIVE_ONLY=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/NTCreate/SecurityFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/Capabilities.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/Capabilities.cs

- **Purpose:** The server supports extended security for authentication. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 31 lines, 1272 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Capabilities`.
- **Important APIs/types/functions:** Types: enum Capabilities : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: RawMode=0x00000001, MPXMode=0x00000002, Unicode=0x00000004, LargeFiles=0x00000008, NTSMB=0x00000010, RpcRemoteApi=0x00000020, NTStatusCode=0x00000040, Level2Oplocks=0x00000080, LockAndRead=0x00000100, NTFind=0x00000200, DFS=0x00001000, InfoLevelPassthrough=0x00002000, LargeRead=0x00004000, LargeWrite=0x00008000, LightWeightIO=0x00010000, Unix=0x00800000, DynamicReauthentication=0x20000000, ExtendedSecurity=0x80000000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/Capabilities.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/SecurityMode.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/SecurityMode.cs

- **Purpose:** If clear, the server supports only Share Level access control. If set, the server supports only User Level access control. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 23 lines, 881 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SecurityMode`.
- **Important APIs/types/functions:** Types: enum SecurityMode : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: UserSecurityMode=0x01, EncryptPasswords=0x02, SecuritySignaturesEnabled=0x04, SecuritySignaturesRequired=0x08.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Negotiate/SecurityMode.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/AccessRights.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/AccessRights.cs

- **Purpose:** Defines protocol constants for AccessRights. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 10 lines, 193 bytes. Namespace `SMBLibrary.SMB1`. Primary type `AccessRights`.
- **Important APIs/types/functions:** Types: enum AccessRights : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_DA_ACCESS_READ=0x00, SMB_DA_ACCESS_WRITE=0x01, SMB_DA_ACCESS_READ_WRITE=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/AccessRights.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenFlags.cs

- **Purpose:** If this bit is set, the client requests that the file attribute data in the response be populated. All fields after the FID in the response are also populated. If this bit is not set, all fields after the FID in the response are zero. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 31 lines, 925 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpenFlags`.
- **Important APIs/types/functions:** Types: enum OpenFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: REQ_ATTRIB=0x0001, REQ_OPLOCK=0x0002, REQ_OPLOCK_BATCH=0x0004, SMB_OPEN_EXTENDED_RESPONSE=0x0010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenResult.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenResult.cs

- **Purpose:** Defines protocol constants for OpenResult. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 225 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OpenResult`.
- **Important APIs/types/functions:** Types: enum OpenResult : byte. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: Reserved=0x00, FileExistedAndWasOpened=0x01, NotExistedAndWasCreated=0x02, FileExistedAndWasTruncated=0x03.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Open/OpenResult.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ResourceType.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ResourceType.cs

- **Purpose:** OpenAndX Response: Valid. OpenAndX Extended Response: Invalid (SMB 1.0). NTCreateAndX Response: Valid. NTCreateAndX Extended Response: Invalid (SMB 1.0). Transact2Open2: Was never valid. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 28 lines, 810 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ResourceType`.
- **Important APIs/types/functions:** Types: enum ResourceType : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: FileTypeDisk=0x0000, FileTypeByteModePipe=0x0001, FileTypeMessageModePipe=0x0002, FileTypePrinter=0x0003, FileTypeCommDevice=0x0004, FileTypeUnknown=0xFFFF.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/ResourceType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SMBFileAttributes.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SMBFileAttributes.cs

- **Purpose:** SMB_FILE_ATTRIBUTES. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 24 lines, 889 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMBFileAttributes`.
- **Important APIs/types/functions:** Types: enum SMBFileAttributes : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: Normal=0x0000, ReadOnly=0x0001, Hidden=0x0002, System=0x0004, Volume=0x0008, Directory=0x0010, Archive=0x0020, SearchReadOnly=0x0100, SearchHidden=0x0200, SearchSystem=0x0400, SearchDirectory=0x1000, SearchArchive=0x2000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SMBFileAttributes.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SessionSetup/SessionSetupAction.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SessionSetup/SessionSetupAction.cs

- **Purpose:** Defines protocol constants for SessionSetupAction. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 216 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SessionSetupAction`.
- **Important APIs/types/functions:** Types: enum SessionSetupAction : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SetupGuest=0x01, UseLanmanKey=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/SessionSetup/SessionSetupAction.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Transaction/TransactionFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Transaction/TransactionFlags.cs

- **Purpose:** Defines protocol constants for TransactionFlags. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 174 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionFlags`.
- **Important APIs/types/functions:** Types: enum TransactionFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DISCONNECT_TID=0x0001, NO_RESPONSE=0x0002.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Transaction/TransactionFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/OptionalSupportFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/OptionalSupportFlags.cs

- **Purpose:** The server supports the use of SMB_FILE_ATTRIBUTES exclusive search attributes in client requests. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 22 lines, 694 bytes. Namespace `SMBLibrary.SMB1`. Primary type `OptionalSupportFlags`.
- **Important APIs/types/functions:** Types: enum OptionalSupportFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_SUPPORT_SEARCH_BITS=0x0001, SMB_SHARE_IS_IN_DFS=0x0002, SMB_CSC_CACHE_MANUAL_REINT=0x0000, SMB_CSC_CACHE_AUTO_REINT=0x0004, SMB_CSC_CACHE_VDO=0x0008, SMB_CSC_NO_CACHING=0x000C, SMB_UNIQUE_FILE_NAME=0x0010, SMB_EXTENDED_SIGNATURES=0x0020.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/OptionalSupportFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/ServiceName.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/ServiceName.cs

- **Purpose:** Valid only for request. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 16 lines, 265 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ServiceName`.
- **Important APIs/types/functions:** Types: enum ServiceName. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DiskShare, PrinterShare, NamedPipe, SerialCommunicationsDevice, AnyType.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/ServiceName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/TreeConnectFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/TreeConnectFlags.cs

- **Purpose:** If set and SMB_Header.TID is valid, the tree connect specified by the TID in the SMB header of the request SHOULD be disconnected when the server sends the response. If this tree disconnect fails, then the error SHOULD be ignored If set. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 27 lines, 1050 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TreeConnectFlags`.
- **Important APIs/types/functions:** Types: enum TreeConnectFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DisconnectTID=0x0001, ExtendedSignatures=0x0004, ExtendedResponse=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/TreeConnect/TreeConnectFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Write/WriteMode.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Write/WriteMode.cs

- **Purpose:** Defines protocol constants for WriteMode. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 13 lines, 231 bytes. Namespace `SMBLibrary.SMB1`. Primary type `WriteMode`.
- **Important APIs/types/functions:** Types: enum WriteMode : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: WritethroughMode=0x0001, ReadBytesAvailable=0x0002, RAW_MODE=0x0004, MSG_START=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Enums/Write/WriteMode.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/Enums/NTTransactSubcommandName.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/Enums/NTTransactSubcommandName.cs

- **Purpose:** This is the Function field in SMB_COM_NT_TRANSACT request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 18 lines, 533 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactSubcommandName`.
- **Important APIs/types/functions:** Types: enum NTTransactSubcommandName : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: NT_TRANSACT_CREATE=0x0001, NT_TRANSACT_IOCTL=0x0002, NT_TRANSACT_SET_SECURITY_DESC=0x0003, NT_TRANSACT_NOTIFY_CHANGE=0x0004, NT_TRANSACT_QUERY_SECURITY_DESC=0x0006, NT_TRANSACT_QUERY_QUOTA=0x0007, NT_TRANSACT_SET_QUOTA=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/Enums/NTTransactSubcommandName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactCreateRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactCreateRequest.cs

- **Purpose:** NT_TRANSACT_CREATE Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 90 lines, 3941 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactCreateRequest`.
- **Important APIs/types/functions:** Types: class NTTransactCreateRequest : NTTransactSubcommand. Constructors: NTTransactCreateRequest. Constants/static metadata: ParametersFixedLength. Fields/properties: Flags, RootDirectoryFID, DesiredAccess, AllocationSize, ExtFileAttributes, ShareAccess, CreateDisposition, CreateOptions, ImpersonationLevel, SecurityFlags, Name, SecurityDescriptor, ExtendedAttributes. Methods/overrides: GetParameters, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_CREATE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. Some outbound methods intentionally stop with NotImplementedException, so this type currently supports inbound parsing more than full serialization.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, NTTransactSubcommand, FileFullEAInformation, SecurityDescriptor, AccessMask. Wire helpers observed: ByteReader.ReadByte, LittleEndianReader.ReadUInt32, SMB1Helper.ReadFixedLengthString.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. NotImplementedException blocks full round-trip serialization for this type. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** Unicode and OEM string alignment fixtures, tests asserting unsupported serialization paths throw NotImplementedException.
- **Explicit failure paths:** NotImplementedException.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactCreateRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLRequest.cs

- **Purpose:** NT_TRANSACT_IOCTL Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 66 lines, 1957 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactIOCTLRequest`.
- **Important APIs/types/functions:** Types: class NTTransactIOCTLRequest : NTTransactSubcommand. Constructors: NTTransactIOCTLRequest. Constants/static metadata: SetupLength. Fields/properties: FunctionCode, FID, IsFsctl, IsFlags, Data. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_IOCTL.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLResponse.cs

- **Purpose:** NT_TRANSACT_IOCTL Response. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 57 lines, 1550 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactIOCTLResponse`.
- **Important APIs/types/functions:** Types: class NTTransactIOCTLResponse : NTTransactSubcommand. Constructors: NTTransactIOCTLResponse. Constants/static metadata: ParametersLength, SetupLength. Fields/properties: TransactionDataSize, Data. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_IOCTL.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactIOCTLResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeRequest.cs

- **Purpose:** NT_TRANSACT_NOTIFY_CHANGE Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1830 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactNotifyChangeRequest`.
- **Important APIs/types/functions:** Types: class NTTransactNotifyChangeRequest : NTTransactSubcommand. Constructors: NTTransactNotifyChangeRequest. Constants/static metadata: SetupLength. Fields/properties: CompletionFilter, FID, WatchTree, Reserved. Methods/overrides: GetSetup. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_NOTIFY_CHANGE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeResponse.cs

- **Purpose:** NT_TRANSACT_NOTIFY_CHANGE Response. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 53 lines, 1591 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactNotifyChangeResponse`.
- **Important APIs/types/functions:** Types: class NTTransactNotifyChangeResponse : NTTransactSubcommand. Constructors: NTTransactNotifyChangeResponse. Constants/static metadata: none. Fields/properties: FileNotifyInformationBytes. Methods/overrides: GetParameters, GetFileNotifyInformation, SetFileNotifyInformation. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_NOTIFY_CHANGE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactNotifyChangeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorRequest.cs

- **Purpose:** NT_TRANSACT_QUERY_SECURITY_DESC Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 53 lines, 1803 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactQuerySecurityDescriptorRequest`.
- **Important APIs/types/functions:** Types: class NTTransactQuerySecurityDescriptorRequest : NTTransactSubcommand. Constructors: NTTransactQuerySecurityDescriptorRequest. Constants/static metadata: ParametersLength. Fields/properties: FID, Reserved, SecurityInfoFields. Methods/overrides: GetParameters. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_QUERY_SECURITY_DESC.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorResponse.cs

- **Purpose:** NT_TRANSACT_QUERY_SECURITY_DESC Response. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 66 lines, 1996 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactQuerySecurityDescriptorResponse`.
- **Important APIs/types/functions:** Types: class NTTransactQuerySecurityDescriptorResponse : NTTransactSubcommand. Constructors: NTTransactQuerySecurityDescriptorResponse. Constants/static metadata: ParametersLength. Fields/properties: LengthNeeded, SecurityDescriptor. Methods/overrides: GetParameters, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_QUERY_SECURITY_DESC.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand, SecurityDescriptor. Wire helpers observed: LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactQuerySecurityDescriptorResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSetSecurityDescriptorRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSetSecurityDescriptorRequest.cs

- **Purpose:** NT_TRANSACT_SET_SECURITY_DESC Request. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 61 lines, 2045 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactSetSecurityDescriptorRequest`.
- **Important APIs/types/functions:** Types: class NTTransactSetSecurityDescriptorRequest : NTTransactSubcommand. Constructors: NTTransactSetSecurityDescriptorRequest. Constants/static metadata: ParametersLength. Fields/properties: FID, Reserved, SecurityInformation, SecurityDescriptor. Methods/overrides: GetParameters, GetData. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_SET_SECURITY_DESC.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand, SecurityDescriptor. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSetSecurityDescriptorRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSetSecurityDescriptorResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSetSecurityDescriptorResponse.cs

- **Purpose:** NT_TRANSACT_SET_SECURITY_DESC Response. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 32 lines, 924 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactSetSecurityDescriptorResponse`.
- **Important APIs/types/functions:** Types: class NTTransactSetSecurityDescriptorResponse : NTTransactSubcommand. Constructors: NTTransactSetSecurityDescriptorResponse. Constants/static metadata: ParametersLength. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: NTTransactSubcommandName.NT_TRANSACT_SET_SECURITY_DESC.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSetSecurityDescriptorResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSubcommand.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSubcommand.cs

- **Purpose:** Defines NTTransactSubcommand for the NT transaction subcommand layer. It is part of the NT transaction subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 58 lines, 2005 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NTTransactSubcommand`.
- **Important APIs/types/functions:** Types: class NTTransactSubcommand. Constructors: NTTransactSubcommand. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetSetup, GetParameters, GetData, GetSubcommandRequest. Dispatch cases: NTTransactSubcommandName.NT_TRANSACT_CREATE, NTTransactSubcommandName.NT_TRANSACT_IOCTL, NTTransactSubcommandName.NT_TRANSACT_SET_SECURITY_DESC, NTTransactSubcommandName.NT_TRANSACT_NOTIFY_CHANGE, NTTransactSubcommandName.NT_TRANSACT_QUERY_SECURITY_DESC.
- **Control flow:** A static dispatcher validates setup length or subcommand id and instantiates the concrete request parser, otherwise raising InvalidDataException. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: NTTransactSubcommand.
- **Integration points:** Used inside SMB_COM_NT_TRANSACT payloads and selected by NTTransactSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/NTTransactSubcommands/NTTransactSubcommand.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Cryptography.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Cryptography.cs

- **Purpose:** Calculates SMB1 message signatures over signing keys, optional challenge responses, and padded message bytes. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 29 lines, 1124 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Cryptography`.
- **Important APIs/types/functions:** Types: class SMB1Cryptography. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: CalculateSignature.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** Cryptographic state is local to the signature calculation and the returned ulong signature.
- **Dependencies:** Usings: System.Security.Cryptography, Utilities. Local dependencies and referenced protocol types: none. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt64.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first.
- **Test signals:** known SMB1 signing test vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Cryptography.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Header.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Header.cs

- **Purpose:** SMB_FLAGS2_EXTENDED_SECURITY. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 140 lines, 4672 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Header`.
- **Important APIs/types/functions:** Types: class SMB1Header. Constructors: SMB1Header. Constants/static metadata: Length, ProtocolSignature. Fields/properties: Protocol, Command, Status, Flags, Flags2, SecurityFeatures, TID, UID, MID, PID, ReplyFlag, ExtendedSecurityFlag, UnicodeFlag. Methods/overrides: WriteBytes, GetBytes, IsValidSMB1Header.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Header signing state is represented by the SecurityFeatures field but persistence is left to the surrounding SMB session. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Header, NTStatus. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianConverter.ToUInt64, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, LittleEndianWriter.WriteUInt64.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Most parsers trust advertised wire offsets and lengths; malformed packets can surface as range/format exceptions unless callers validate packet size first. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Header.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Helper.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Helper.cs

- **Purpose:** SMB_DATE. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 187 lines, 6222 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Helper`.
- **Important APIs/types/functions:** Types: class SMB1Helper. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: ReadNullableFileTime, ReadSMBDate, WriteSMBDate, ReadSMBTime, WriteSMBTime, ReadSMBDateTime, WriteSMBDateTime, ReadNullableSMBDateTime, ReadSMBString, WriteSMBString, ReadFixedLengthString, WriteFixedLengthString.
- **Control flow:** String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Helper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Message.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Message.cs

- **Purpose:** Each message has a single header and either a single command or multiple batched (AndX) commands. Multiple command requests or responses can be sent in a single message. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 106 lines, 3807 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SMB1Message`.
- **Important APIs/types/functions:** Types: class SMB1Message. Constructors: SMB1Message. Constants/static metadata: none. Fields/properties: Header, Commands. Methods/overrides: GetBytes, GetSMB1Message.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: SMB1Command, SMBAndXCommand, SMB1Header. Wire helpers observed: ByteWriter.WriteBytes, ByteWriter.WriteByte.
- **Integration points:** Advertises its SMB command discriminator to the message layer.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, invalid setup or command values raising InvalidDataException.
- **Explicit failure paths:** ArgumentException(Invalid command sequence), InvalidDataException(Invalid SMB header signature).
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/SMB1Message.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/ServiceNameHelper.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/ServiceNameHelper.cs

- **Purpose:** Provides shared SMB1 conversion helpers used by command and subcommand serializers. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 50 lines, 1585 bytes. Namespace `SMBLibrary.SMB1`. Primary type `ServiceNameHelper`.
- **Important APIs/types/functions:** Types: class ServiceNameHelper. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetServiceString, GetServiceName. Protocol discriminator returns: ServiceName.DiskShare, ServiceName.PrinterShare, ServiceName.NamedPipe, ServiceName.SerialCommunicationsDevice, ServiceName.AnyType. Dispatch cases: ServiceName.DiskShare, ServiceName.PrinterShare, ServiceName.NamedPipe, ServiceName.SerialCommunicationsDevice.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Converts between service enum values and the OEM service strings exchanged by tree-connect packets.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/ServiceNameHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/AccessModeOptions.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/AccessModeOptions.cs

- **Purpose:** Write-through mode. If this flag is set, then no read ahead or write behind is allowed on this file or device. When the response is returned, data is expected to be on the disk or device. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 97 lines, 3010 bytes. Namespace `SMBLibrary.SMB1`. Primary type `AccessMode`.
- **Important APIs/types/functions:** Types: enum AccessMode : byte, enum SharingMode : byte, enum ReferenceLocality : byte, enum CachedMode : byte, enum WriteThroughMode : byte, struct AccessModeOptions. Constructors: AccessModeOptions. Constants/static metadata: Length. Fields/properties: AccessMode, SharingMode, ReferenceLocality, CachedMode, WriteThroughMode. Methods/overrides: WriteBytes, Read. Enum values: Read=0x00, Write=0x01, ReadWrite=0x02, Execute=0x03, Compatibility=0x00, DenyReadWriteExecute=0x01, DenyWrite=0x02, DenyReadExecute=0x03, DenyNothing=0x04, Unknown=0x00, Sequential=0x01, Random=0x02, RandomWithLocality=0x03, CachingAllowed=0x00, DoNotCacheFile=0x01, Disabled=0x00, WriteThrough=0x01.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/AccessModeOptions.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/ActionTaken.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/ActionTaken.cs

- **Purpose:** Defines protocol constants for LockStatus. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 34 lines, 1029 bytes. Namespace `SMBLibrary.SMB1`. Primary type `LockStatus`.
- **Important APIs/types/functions:** Types: enum LockStatus : byte, struct ActionTaken. Constructors: ActionTaken. Constants/static metadata: none. Fields/properties: OpenResult, LockStatus. Methods/overrides: WriteBytes. Enum values: NoOpLockWasRequestedOrGranted=0x00, OpLockWasRequestedAndGranted=0x01.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/ActionTaken.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/OpenMode.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/OpenMode.cs

- **Purpose:** Defines protocol constants for CreateFile. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 57 lines, 1586 bytes. Namespace `SMBLibrary.SMB1`. Primary type `CreateFile`.
- **Important APIs/types/functions:** Types: enum CreateFile : byte, enum FileExistsOpts : byte, struct OpenMode. Constructors: OpenMode. Constants/static metadata: Length. Fields/properties: FileExistsOpts, CreateFile. Methods/overrides: WriteBytes, Read. Enum values: ReturnErrorIfNotExist=0x00, CreateIfNotExist=0x01, ReturnError=0x00, Append=0x01, TruncateToZero=0x02.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality, numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/EnumStructures/OpenMode.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/FindFlags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/FindFlags.cs

- **Purpose:** Defines protocol constants for FindFlags. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 14 lines, 329 bytes. Namespace `SMBLibrary.SMB1`. Primary type `FindFlags`.
- **Important APIs/types/functions:** Types: enum FindFlags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_FIND_CLOSE_AFTER_REQUEST=0x0001, SMB_FIND_CLOSE_AT_EOS=0x0002, SMB_FIND_RETURN_RESUME_KEYS=0x0004, SMB_FIND_CONTINUE_FROM_LAST=0x0008, SMB_FIND_WITH_BACKUP_INTENT=0x0010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/FindFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Open2Flags.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Open2Flags.cs

- **Purpose:** Return additional information in the response; populate the CreationTime, FileDataSize, AccessMode, ResourceType, and NMPipeStatus fields in the response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 30 lines, 794 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Open2Flags`.
- **Important APIs/types/functions:** Types: enum Open2Flags : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: REQ_ATTRIB=0x0001, REQ_OPLOCK=0x0002, REQ_OPBATCH=0x0004, REQ_EASIZE=0x0008.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Open2Flags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/SearchStorageType.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/SearchStorageType.cs

- **Purpose:** Defines protocol constants for SearchStorageType. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 9 lines, 160 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SearchStorageType`.
- **Important APIs/types/functions:** Types: enum SearchStorageType : uint. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: FILE_DIRECTORY_FILE=0x01, FILE_NON_DIRECTORY_FILE=0x40.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/SearchStorageType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Transaction2SubcommandName.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Transaction2SubcommandName.cs

- **Purpose:** Defines protocol constants for Transaction2SubcommandName. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 18 lines, 560 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SubcommandName`.
- **Important APIs/types/functions:** Types: enum Transaction2SubcommandName : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: TRANS2_OPEN2=0x0000, TRANS2_FIND_FIRST2=0x0001, TRANS2_FIND_NEXT2=0x0002, TRANS2_QUERY_FS_INFORMATION=0x0003, TRANS2_SET_FS_INFORMATION=0x0004, TRANS2_QUERY_PATH_INFORMATION=0x0005, TRANS2_SET_PATH_INFORMATION=0x006, TRANS2_QUERY_FILE_INFORMATION=0x0007, TRANS2_SET_FILE_INFORMATION=0x0008, TRANS2_CREATE_DIRECTORY=0x000D, TRANS2_GET_DFS_REFERRAL=0x0010.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Enums/Transaction2SubcommandName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryRequest.cs

- **Purpose:** TRANS2_CREATE_DIRECTORY Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 63 lines, 2110 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2CreateDirectoryRequest`.
- **Important APIs/types/functions:** Types: class Transaction2CreateDirectoryRequest : Transaction2Subcommand. Constructors: Transaction2CreateDirectoryRequest. Constants/static metadata: none. Fields/properties: Reserved, DirectoryName, ExtendedAttributeList. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_CREATE_DIRECTORY.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, Transaction2Subcommand, FullExtendedAttributeList. Wire helpers observed: LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryResponse.cs

- **Purpose:** TRANS2_CREATE_DIRECTORY Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 48 lines, 1430 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2CreateDirectoryResponse`.
- **Important APIs/types/functions:** Types: class Transaction2CreateDirectoryResponse : Transaction2Subcommand. Constructors: Transaction2CreateDirectoryResponse. Constants/static metadata: ParametersLength. Fields/properties: EaErrorOffset. Methods/overrides: GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_CREATE_DIRECTORY.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2CreateDirectoryResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindFirst2Request.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindFirst2Request.cs

- **Purpose:** TRANS2_FIND_FIRST2 Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 135 lines, 4542 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2FindFirst2Request`.
- **Important APIs/types/functions:** Types: class Transaction2FindFirst2Request : Transaction2Subcommand. Constructors: Transaction2FindFirst2Request. Constants/static metadata: none. Fields/properties: SearchAttributes, SearchCount, Flags, InformationLevel, SearchStorageType, FileName, GetExtendedAttributeList, CloseAfterRequest, CloseAtEndOfSearch. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_FIND_FIRST2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindFirst2Request.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindFirst2Response.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindFirst2Response.cs

- **Purpose:** TRANS2_FIND_FIRST2 Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 79 lines, 2914 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2FindFirst2Response`.
- **Important APIs/types/functions:** Types: class Transaction2FindFirst2Response : Transaction2Subcommand. Constructors: Transaction2FindFirst2Response. Constants/static metadata: ParametersLength. Fields/properties: SID, SearchCount, EndOfSearch, EaErrorOffset, LastNameOffset, FindInformationListBytes. Methods/overrides: GetParameters, GetData, GetFindInformationList, SetFindInformationList. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_FIND_FIRST2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand, FindInformationList. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindFirst2Response.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindNext2Request.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindNext2Request.cs

- **Purpose:** TRANS2_FIND_NEXT2 Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 97 lines, 3437 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2FindNext2Request`.
- **Important APIs/types/functions:** Types: class Transaction2FindNext2Request : Transaction2Subcommand. Constructors: Transaction2FindNext2Request. Constants/static metadata: none. Fields/properties: SID, SearchCount, InformationLevel, ResumeKey, Flags, FileName, GetExtendedAttributeList. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_FIND_NEXT2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindNext2Request.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindNext2Response.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindNext2Response.cs

- **Purpose:** TRANS2_FIND_NEXT2 Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 76 lines, 2735 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2FindNext2Response`.
- **Important APIs/types/functions:** Types: class Transaction2FindNext2Response : Transaction2Subcommand. Constructors: Transaction2FindNext2Response. Constants/static metadata: ParametersLength. Fields/properties: SearchCount, EndOfSearch, EaErrorOffset, LastNameOffset, FindInformationListBytes. Methods/overrides: GetParameters, GetData, GetFindInformationList, SetFindInformationList. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_FIND_NEXT2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand, FindInformationList. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2FindNext2Response.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralRequest.cs

- **Purpose:** TRANS2_GET_DFS_REFERRAL Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1365 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2GetDfsReferralRequest`.
- **Important APIs/types/functions:** Types: class Transaction2GetDfsReferralRequest : Transaction2Subcommand. Constructors: Transaction2GetDfsReferralRequest. Constants/static metadata: none. Fields/properties: ReferralRequest. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_GET_DFS_REFERRAL.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: SMBLibrary.DFS, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralResponse.cs

- **Purpose:** TRANS2_GET_DFS_REFERRAL Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 42 lines, 1249 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2GetDfsReferralResponse`.
- **Important APIs/types/functions:** Types: class Transaction2GetDfsReferralResponse : Transaction2Subcommand. Constructors: Transaction2GetDfsReferralResponse. Constants/static metadata: ParametersLength. Fields/properties: ReferralResponse. Methods/overrides: GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_GET_DFS_REFERRAL.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: SMBLibrary.DFS. Local dependencies and referenced protocol types: Transaction2Subcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2GetDfsReferralResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Request.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Request.cs

- **Purpose:** TRANS2_OPEN2 Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 95 lines, 3491 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Open2Request`.
- **Important APIs/types/functions:** Types: class Transaction2Open2Request : Transaction2Subcommand. Constructors: Transaction2Open2Request. Constants/static metadata: none. Fields/properties: Flags, AccessMode, Reserved1, FileAttributes, CreationTime, OpenMode, AllocationSize, Reserved, FileName, ExtendedAttributeList. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_OPEN2.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding. UTIME fields are converted between SMB seconds-since-1970 values and nullable DateTime values.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, UTimeHelper, Transaction2Subcommand, FullExtendedAttributeList. Wire helpers observed: ByteReader.ReadBytes, ByteReader.ReadByte, LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, ByteWriter.WriteBytes, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString, UTimeHelper.ReadNullableUTime, UTimeHelper.WriteUTime.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields. Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Request.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Response.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Response.cs

- **Purpose:** TRANS2_OPEN2 Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 77 lines, 3258 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Open2Response`.
- **Important APIs/types/functions:** Types: class Transaction2Open2Response : Transaction2Subcommand. Constructors: Transaction2Open2Response. Constants/static metadata: ParametersLength. Fields/properties: FID, FileAttributes, CreationTime, FileDataSize, AccessMode, ResourceType, NMPipeStatus, ActionTaken, Reserved, ExtendedAttributeErrorOffset, ExtendedAttributeLength. Methods/overrides: GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_OPEN2.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. UTIME fields are converted between SMB seconds-since-1970 values and nullable DateTime values.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: UTimeHelper, Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, UTimeHelper.ReadNullableUTime, UTimeHelper.WriteUTime.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Open2Response.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationRequest.cs

- **Purpose:** TRANS2_QUERY_FS_INFORMATION Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 85 lines, 2476 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryFSInformationRequest`.
- **Important APIs/types/functions:** Types: class Transaction2QueryFSInformationRequest : Transaction2Subcommand. Constructors: Transaction2QueryFSInformationRequest. Constants/static metadata: SMB_INFO_PASSTHROUGH, ParametersLength. Fields/properties: InformationLevel, IsPassthroughInformationLevel, QueryFSInformationLevel, FileSystemInformationClass. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_FS_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationResponse.cs

- **Purpose:** TRANS2_QUERY_FS_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 70 lines, 2330 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryFSInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2QueryFSInformationResponse : Transaction2Subcommand. Constructors: Transaction2QueryFSInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: InformationBytes. Methods/overrides: GetData, GetQueryFSInformation, SetQueryFSInformation, GetFileSystemInformation, SetFileSystemInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_FS_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFSInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFileInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFileInformationRequest.cs

- **Purpose:** TRANS2_QUERY_FILE_INFORMATION Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 107 lines, 3448 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryFileInformationRequest`.
- **Important APIs/types/functions:** Types: class Transaction2QueryFileInformationRequest : Transaction2Subcommand. Constructors: Transaction2QueryFileInformationRequest. Constants/static metadata: SMB_INFO_PASSTHROUGH, ParametersLength. Fields/properties: FID, InformationLevel, GetExtendedAttributeList, IsPassthroughInformationLevel, QueryInformationLevel, FileInformationClass. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_FILE_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand, FullExtendedAttributeList. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFileInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFileInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFileInformationResponse.cs

- **Purpose:** TRANS2_QUERY_FILE_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 78 lines, 2618 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryFileInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2QueryFileInformationResponse : Transaction2Subcommand. Constructors: Transaction2QueryFileInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: EaErrorOffset, InformationBytes. Methods/overrides: GetParameters, GetData, GetQueryInformation, SetQueryInformation, GetFileInformation, SetFileInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_FILE_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryFileInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationRequest.cs

- **Purpose:** TRANS2_QUERY_PATH_INFORMATION Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 119 lines, 3898 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryPathInformationRequest`.
- **Important APIs/types/functions:** Types: class Transaction2QueryPathInformationRequest : Transaction2Subcommand. Constructors: Transaction2QueryPathInformationRequest. Constants/static metadata: SMB_INFO_PASSTHROUGH, ParametersFixedLength. Fields/properties: InformationLevel, Reserved, FileName, GetExtendedAttributeList, IsPassthroughInformationLevel, QueryInformationLevel, FileInformationClass. Methods/overrides: GetSetup, GetParameters, GetData. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_PATH_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: SMB1Helper, Transaction2Subcommand, FullExtendedAttributeList. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationResponse.cs

- **Purpose:** TRANS2_QUERY_PATH_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 78 lines, 2604 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2QueryPathInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2QueryPathInformationResponse : Transaction2Subcommand. Constructors: Transaction2QueryPathInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: EaErrorOffset, InformationBytes. Methods/overrides: GetParameters, GetData, GetQueryInformation, SetQueryInformation, GetFileInformation, SetFileInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_QUERY_PATH_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2QueryPathInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFSInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFSInformationRequest.cs

- **Purpose:** TRANS2_SET_FS_INFORMATION Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 93 lines, 2947 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SetFSInformationRequest`.
- **Important APIs/types/functions:** Types: class Transaction2SetFSInformationRequest : Transaction2Subcommand. Constructors: Transaction2SetFSInformationRequest. Constants/static metadata: SMB_INFO_PASSTHROUGH, ParametersLength. Fields/properties: FID, InformationLevel, InformationBytes, IsPassthroughInformationLevel, FileSystemInformationClass. Methods/overrides: GetSetup, GetParameters, GetData, SetFileSystemInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_SET_FS_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFSInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFSInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFSInformationResponse.cs

- **Purpose:** TRANS2_SET_FS_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 32 lines, 920 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SetFSInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2SetFSInformationResponse : Transaction2Subcommand. Constructors: Transaction2SetFSInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_SET_FS_INFORMATION.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFSInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFileInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFileInformationRequest.cs

- **Purpose:** TRANS2_SET_FILE_INFORMATION Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 114 lines, 3510 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SetFileInformationRequest`.
- **Important APIs/types/functions:** Types: class Transaction2SetFileInformationRequest : Transaction2Subcommand. Constructors: Transaction2SetFileInformationRequest. Constants/static metadata: SMB_INFO_PASSTHROUGH, ParametersLength. Fields/properties: FID, InformationLevel, Reserved, InformationBytes, IsPassthroughInformationLevel, SetInformationLevel, FileInformationClass. Methods/overrides: GetSetup, GetParameters, GetData, SetInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_SET_FILE_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFileInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFileInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFileInformationResponse.cs

- **Purpose:** TRANS2_SET_FILE_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1528 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SetFileInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2SetFileInformationResponse : Transaction2Subcommand. Constructors: Transaction2SetFileInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: EaErrorOffset. Methods/overrides: GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_SET_FILE_INFORMATION.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetFileInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetPathInformationRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetPathInformationRequest.cs

- **Purpose:** TRANS2_SET_PATH_INFORMATION Request. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 124 lines, 3790 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SetPathInformationRequest`.
- **Important APIs/types/functions:** Types: class Transaction2SetPathInformationRequest : Transaction2Subcommand. Constructors: Transaction2SetPathInformationRequest. Constants/static metadata: SMB_INFO_PASSTHROUGH, ParametersFixedLength. Fields/properties: InformationLevel, Reserved, FileName, InformationBytes, IsPassthroughInformationLevel, SetInformationLevel, FileInformationClass. Methods/overrides: GetSetup, GetParameters, GetData, SetInformation. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_SET_PATH_INFORMATION.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, Utilities. Local dependencies and referenced protocol types: SMB1Helper, Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt16, LittleEndianWriter.WriteUInt32, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality, Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetPathInformationRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetPathInformationResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetPathInformationResponse.cs

- **Purpose:** TRANS2_SET_PATH_INFORMATION Response. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 48 lines, 1529 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2SetPathInformationResponse`.
- **Important APIs/types/functions:** Types: class Transaction2SetPathInformationResponse : Transaction2Subcommand. Constructors: Transaction2SetPathInformationResponse. Constants/static metadata: ParametersLength. Fields/properties: EaErrorOffset. Methods/overrides: GetParameters. Protocol discriminator returns: Transaction2SubcommandName.TRANS2_SET_PATH_INFORMATION.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2SetPathInformationResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Subcommand.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Subcommand.cs

- **Purpose:** Defines Transaction2Subcommand for the Transaction2 subcommand layer. It is part of the Transaction2 subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 74 lines, 3373 bytes. Namespace `SMBLibrary.SMB1`. Primary type `Transaction2Subcommand`.
- **Important APIs/types/functions:** Types: class Transaction2Subcommand. Constructors: Transaction2Subcommand. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetSetup, GetParameters, GetData, GetSubcommandRequest. Dispatch cases: Transaction2SubcommandName.TRANS2_OPEN2, Transaction2SubcommandName.TRANS2_FIND_FIRST2, Transaction2SubcommandName.TRANS2_FIND_NEXT2, Transaction2SubcommandName.TRANS2_QUERY_FS_INFORMATION, Transaction2SubcommandName.TRANS2_SET_FS_INFORMATION, Transaction2SubcommandName.TRANS2_QUERY_PATH_INFORMATION, Transaction2SubcommandName.TRANS2_SET_PATH_INFORMATION, Transaction2SubcommandName.TRANS2_QUERY_FILE_INFORMATION, Transaction2SubcommandName.TRANS2_SET_FILE_INFORMATION, Transaction2SubcommandName.TRANS2_CREATE_DIRECTORY, Transaction2SubcommandName.TRANS2_GET_DFS_REFERRAL.
- **Control flow:** A static dispatcher validates setup length or subcommand id and instantiates the concrete request parser, otherwise raising InvalidDataException. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: Transaction2Subcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION2 requests/responses; setup bytes carry Transaction2SubcommandName and the enclosing Transaction2Request/Response carries the byte arrays.
- **Risks:** Correctness depends on exact WordCount/setup length handling. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/Transaction2Subcommands/Transaction2Subcommand.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/NamedPipeState.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/NamedPipeState.cs

- **Purpose:** Defines protocol constants for NamedPipeState. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 11 lines, 223 bytes. Namespace `SMBLibrary.SMB1`. Primary type `NamedPipeState`.
- **Important APIs/types/functions:** Types: enum NamedPipeState : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: DisconnectedByServer=0x0001, Listening=0x0002, ConnectionToServerOK=0x0003, ServerEndClosed=0x0004.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/NamedPipeState.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/PipeState.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/PipeState.cs

- **Purpose:** If set, the named pipe is operating in message mode. If not set, the named pipe is operating in byte mode. In message mode, the system treats the bytes read or written in each I/O operation to the pipe as a message unit. The system MUST. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 25 lines, 1295 bytes. Namespace `SMBLibrary.SMB1`. Primary type `PipeState`.
- **Important APIs/types/functions:** Types: enum PipeState : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: ReadMode=0x0100, Nonblocking=0x8000.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Flag enum drift can silently change negotiated capabilities or access semantics.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/PipeState.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/TransactionSubcommandName.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/TransactionSubcommandName.cs

- **Purpose:** The 0x0001 subcommand code is interpreted as TRANS_MAILSLOT_WRITE if the operation is being performed on a mailslot. The same code is interpreted as a TRANS_SET_NMPIPE_STATE (section 2.2.5.1) if the operation is performed on a named pipe. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 27 lines, 953 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionSubcommandName`.
- **Important APIs/types/functions:** Types: enum TransactionSubcommandName : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: TRANS_MAILSLOT_WRITE=0x0001, TRANS_SET_NMPIPE_STATE=0x0001, TRANS_RAW_READ_NMPIPE=0x0011, TRANS_QUERY_NMPIPE_STATE=0x0021, TRANS_QUERY_NMPIPE_INFO=0x0022, TRANS_PEEK_NMPIPE=0x0023, TRANS_TRANSACT_NMPIPE=0x0026, TRANS_RAW_WRITE_NMPIPE=0x0031, TRANS_READ_NMPIPE=0x0036, TRANS_WRITE_NMPIPE=0x0037, TRANS_WAIT_NMPIPE=0x0053, TRANS_CALL_NMPIPE=0x0054.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: none.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/Enums/TransactionSubcommandName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionCallNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionCallNamedPipeRequest.cs

- **Purpose:** TRANS_CALL_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1549 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionCallNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionCallNamedPipeRequest : TransactionSubcommand. Constructors: TransactionCallNamedPipeRequest. Constants/static metadata: none. Fields/properties: Priority, WriteData. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_CALL_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionCallNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionCallNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionCallNamedPipeResponse.cs

- **Purpose:** TRANS_CALL_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 44 lines, 1182 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionCallNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionCallNamedPipeResponse : TransactionSubcommand. Constructors: TransactionCallNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: ReadData. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_CALL_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionCallNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeRequest.cs

- **Purpose:** TRANS_PEEK_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1334 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionPeekNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionPeekNamedPipeRequest : TransactionSubcommand. Constructors: TransactionPeekNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_PEEK_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeResponse.cs

- **Purpose:** TRANS_PEEK_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 61 lines, 2005 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionPeekNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionPeekNamedPipeResponse : TransactionSubcommand. Constructors: TransactionPeekNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: ReadDataAvailable, MessageBytesLength, NamedPipeState, ReadData. Methods/overrides: GetParameters, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_PEEK_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionPeekNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoRequest.cs

- **Purpose:** TRANS_QUERY_NMPIPE_INFO Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1644 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeInfoRequest`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeInfoRequest : TransactionSubcommand. Constructors: TransactionQueryNamedPipeInfoRequest. Constants/static metadata: none. Fields/properties: FID, Level. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_INFO.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoResponse.cs

- **Purpose:** TRANS_QUERY_NMPIPE_INFO Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 71 lines, 2611 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeInfoResponse`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeInfoResponse : TransactionSubcommand. Constructors: TransactionQueryNamedPipeInfoResponse. Constants/static metadata: ParametersLength. Fields/properties: OutputBufferSize, InputBufferSize, MaximumInstances, CurrentInstances, PipeNameLength, PipeName. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_INFO.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command. String fields branch on the negotiated Unicode flag and include protocol-specific null terminators or alignment padding.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: SMB1Helper, TransactionSubcommand. Wire helpers observed: ByteReader.ReadByte, LittleEndianConverter.ToUInt16, ByteWriter.WriteByte, LittleEndianWriter.WriteUInt16, SMB1Helper.ReadSMBString, SMB1Helper.WriteSMBString.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeInfoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateRequest.cs

- **Purpose:** TRANS_QUERY_NMPIPE_STATE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 44 lines, 1247 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeStateRequest`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeStateRequest : TransactionSubcommand. Constructors: TransactionQueryNamedPipeStateRequest. Constants/static metadata: none. Fields/properties: FID. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_STATE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateResponse.cs

- **Purpose:** TRANS_QUERY_NMPIPE_STATE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 52 lines, 1500 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionQueryNamedPipeStateResponse`.
- **Important APIs/types/functions:** Types: class TransactionQueryNamedPipeStateResponse : TransactionSubcommand. Constructors: TransactionQueryNamedPipeStateResponse. Constants/static metadata: ParametersLength. Fields/properties: NMPipeStatus. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_QUERY_NMPIPE_STATE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionQueryNamedPipeStateResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawReadNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawReadNamedPipeRequest.cs

- **Purpose:** TRANS_RAW_READ_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 48 lines, 1334 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionRawReadNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionRawReadNamedPipeRequest : TransactionSubcommand. Constructors: TransactionRawReadNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_RAW_READ_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawReadNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawReadNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawReadNamedPipeResponse.cs

- **Purpose:** TRANS_RAW_READ_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1211 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionRawReadNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionRawReadNamedPipeResponse : TransactionSubcommand. Constructors: TransactionRawReadNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: BytesRead. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_RAW_READ_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawReadNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeRequest.cs

- **Purpose:** TRANS_RAW_WRITE_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1556 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionRawWriteNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionRawWriteNamedPipeRequest : TransactionSubcommand. Constructors: TransactionRawWriteNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID, WriteData. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_RAW_WRITE_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeResponse.cs

- **Purpose:** TRANS_RAW_WRITE_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1302 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionRawWriteNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionRawWriteNamedPipeResponse : TransactionSubcommand. Constructors: TransactionRawWriteNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: BytesWritten. Methods/overrides: GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_RAW_WRITE_NMPIPE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionRawWriteNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeRequest.cs

- **Purpose:** TRANS_READ_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1333 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionReadNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionReadNamedPipeRequest : TransactionSubcommand. Constructors: TransactionReadNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_READ_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeResponse.cs

- **Purpose:** TRANS_READ_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1190 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionReadNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionReadNamedPipeResponse : TransactionSubcommand. Constructors: TransactionReadNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: ReadData. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_READ_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionReadNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSetNamedPipeStateRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSetNamedPipeStateRequest.cs

- **Purpose:** TRANS_SET_NMPIPE_STATE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1655 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionSetNamedPipeStateRequest`.
- **Important APIs/types/functions:** Types: class TransactionSetNamedPipeStateRequest : TransactionSubcommand. Constructors: TransactionSetNamedPipeStateRequest. Constants/static metadata: none. Fields/properties: FID, PipeState. Methods/overrides: GetSetup, GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_SET_NMPIPE_STATE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSetNamedPipeStateRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSetNamedPipeStateResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSetNamedPipeStateResponse.cs

- **Purpose:** TRANS_SET_NMPIPE_STATE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 29 lines, 846 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionSetNamedPipeStateResponse`.
- **Important APIs/types/functions:** Types: class TransactionSetNamedPipeStateResponse : TransactionSubcommand. Constructors: none. Constants/static metadata: ParametersLength. Fields/properties: none detected. Methods/overrides: none detected. Protocol discriminator returns: TransactionSubcommandName.TRANS_SET_NMPIPE_STATE.
- **Control flow:** Control flow is direct helper invocation from neighboring SMB1 packet readers and writers.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSetNamedPipeStateResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSubcommand.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSubcommand.cs

- **Purpose:** Defines TransactionSubcommand for the classic transaction named-pipe subcommand layer. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 74 lines, 3129 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionSubcommand`.
- **Important APIs/types/functions:** Types: class TransactionSubcommand. Constructors: TransactionSubcommand. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: GetSetup, GetParameters, GetData, GetSubcommandRequest. Dispatch cases: TransactionSubcommandName.TRANS_SET_NMPIPE_STATE, TransactionSubcommandName.TRANS_RAW_READ_NMPIPE, TransactionSubcommandName.TRANS_QUERY_NMPIPE_STATE, TransactionSubcommandName.TRANS_QUERY_NMPIPE_INFO, TransactionSubcommandName.TRANS_PEEK_NMPIPE, TransactionSubcommandName.TRANS_TRANSACT_NMPIPE, TransactionSubcommandName.TRANS_RAW_WRITE_NMPIPE, TransactionSubcommandName.TRANS_READ_NMPIPE, TransactionSubcommandName.TRANS_WRITE_NMPIPE, TransactionSubcommandName.TRANS_WAIT_NMPIPE, TransactionSubcommandName.TRANS_CALL_NMPIPE.
- **Control flow:** A static dispatcher validates setup length or subcommand id and instantiates the concrete request parser, otherwise raising InvalidDataException. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed.
- **Dependencies:** Usings: System, System.Collections.Generic, System.IO, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Correctness depends on exact WordCount/setup length handling. Unicode alignment and null-termination rules are easy regression points. Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** invalid setup or command values raising InvalidDataException, Unicode and OEM string alignment fixtures.
- **Explicit failure paths:** InvalidDataException.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionSubcommand.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeRequest.cs

- **Purpose:** TRANS_TRANSACT_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 55 lines, 1553 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionTransactNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionTransactNamedPipeRequest : TransactionSubcommand. Constructors: TransactionTransactNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID, WriteData. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_TRANSACT_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeResponse.cs

- **Purpose:** TRANS_TRANSACT_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 45 lines, 1210 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionTransactNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionTransactNamedPipeResponse : TransactionSubcommand. Constructors: TransactionTransactNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: ReadData. Methods/overrides: GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_TRANSACT_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionTransactNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWaitNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWaitNamedPipeRequest.cs

- **Purpose:** TRANS_WAIT_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 47 lines, 1349 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionWaitNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionWaitNamedPipeRequest : TransactionSubcommand. Constructors: TransactionWaitNamedPipeRequest. Constants/static metadata: none. Fields/properties: Priority. Methods/overrides: GetSetup. Protocol discriminator returns: TransactionSubcommandName.TRANS_WAIT_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWaitNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWriteNamedPipeRequest.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWriteNamedPipeRequest.cs

- **Purpose:** TRANS_WRITE_NMPIPE Request. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 56 lines, 1538 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionWriteNamedPipeRequest`.
- **Important APIs/types/functions:** Types: class TransactionWriteNamedPipeRequest : TransactionSubcommand. Constructors: TransactionWriteNamedPipeRequest. Constants/static metadata: none. Fields/properties: FID, WriteData. Methods/overrides: GetSetup, GetData. Protocol discriminator returns: TransactionSubcommandName.TRANS_WRITE_NMPIPE.
- **Control flow:** Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** No durable state is stored; values are passed through method parameters and return values.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16, LittleEndianWriter.WriteUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Unicode alignment and null-termination rules are easy regression points.
- **Test signals:** Unicode and OEM string alignment fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWriteNamedPipeRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWriteNamedPipeResponse.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWriteNamedPipeResponse.cs

- **Purpose:** TRANS_WRITE_NMPIPE Response. It is part of the classic transaction named-pipe subcommand surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 44 lines, 1276 bytes. Namespace `SMBLibrary.SMB1`. Primary type `TransactionWriteNamedPipeResponse`.
- **Important APIs/types/functions:** Types: class TransactionWriteNamedPipeResponse : TransactionSubcommand. Constructors: TransactionWriteNamedPipeResponse. Constants/static metadata: ParametersLength. Fields/properties: BytesWritten. Methods/overrides: GetParameters. Protocol discriminator returns: TransactionSubcommandName.TRANS_WRITE_NMPIPE.
- **Control flow:** Outbound control flow builds SMBParameters and SMBData from public fields, then calls the base serializer to add WordCount and ByteCount. Subcommand serialization is split into setup, parameter, and data byte arrays consumed by the enclosing transaction command.
- **State and persistence behavior:** State is held in public protocol fields until serialized; no durable storage or process-wide mutation is performed. Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: TransactionSubcommand. Wire helpers observed: LittleEndianConverter.ToUInt16.
- **Integration points:** Used inside SMB_COM_TRANSACTION named-pipe transactions and selected by TransactionSubcommand.GetSubcommandRequest.
- **Risks:** Large payloads must fit SMB1 16-bit count/offset fields unless explicitly split or handled with high-length fields.
- **Test signals:** round-trip parse/serialize byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/TransactionSubcommands/TransactionWriteNamedPipeResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/UTimeHelper.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/UTimeHelper.cs

- **Purpose:** UTime - The number of seconds since Jan 1, 1970, 00:00:00. It is part of the SMB1 protocol helper surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 82 lines, 2604 bytes. Namespace `SMBLibrary.SMB1`. Primary type `UTimeHelper`.
- **Important APIs/types/functions:** Types: class UTimeHelper. Constructors: none. Constants/static metadata: MinUTimeValue. Fields/properties: none detected. Methods/overrides: ReadUTime, ReadNullableUTime, WriteUTime.
- **Control flow:** UTIME fields are converted between SMB seconds-since-1970 values and nullable DateTime values.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: System, System.Collections.Generic, System.Text, Utilities. Local dependencies and referenced protocol types: UTimeHelper. Wire helpers observed: LittleEndianConverter.ToUInt32, LittleEndianWriter.WriteUInt32.
- **Integration points:** Consumed by neighboring SMBLibrary SMB1 code through the `SMBLibrary.SMB1` namespace.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** caller-level packet tests that consume this helper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1/UTimeHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/FindInformationLevel.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/FindInformationLevel.cs

- **Purpose:** Defines protocol constants for FindInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 16 lines, 618 bytes. Namespace `SMBLibrary.SMB1`. Primary type `FindInformationLevel`.
- **Important APIs/types/functions:** Types: enum FindInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_STANDARD=0x0001, SMB_INFO_QUERY_EA_SIZE=0x0002, SMB_INFO_QUERY_EAS_FROM_LIST=0x0003, SMB_FIND_FILE_DIRECTORY_INFO=0x0101, SMB_FIND_FILE_FULL_DIRECTORY_INFO=0x0102, SMB_FIND_FILE_NAMES_INFO=0x0103, SMB_FIND_FILE_BOTH_DIRECTORY_INFO=0x0104, SMB_FIND_FILE_ID_FULL_DIRECTORY_INFO=0x0105, SMB_FIND_FILE_ID_BOTH_DIRECTORY_INFO=0x0106.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/FindInformationLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryFSInformationLevel.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryFSInformationLevel.cs

- **Purpose:** Defines protocol constants for QueryFSInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 13 lines, 377 bytes. Namespace `SMBLibrary.SMB1`. Primary type `QueryFSInformationLevel`.
- **Important APIs/types/functions:** Types: enum QueryFSInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_ALLOCATION=0x0001, SMB_INFO_VOLUME=0x0002, SMB_QUERY_FS_VOLUME_INFO=0x0102, SMB_QUERY_FS_SIZE_INFO=0x0103, SMB_QUERY_FS_DEVICE_INFO=0x0104, SMB_QUERY_FS_ATTRIBUTE_INFO=0x0105.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryFSInformationLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryInformationLevel.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryInformationLevel.cs

- **Purpose:** Defines protocol constants for QueryInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 20 lines, 749 bytes. Namespace `SMBLibrary.SMB1`. Primary type `QueryInformationLevel`.
- **Important APIs/types/functions:** Types: enum QueryInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_STANDARD=0x0001, SMB_INFO_QUERY_EA_SIZE=0x0002, SMB_INFO_QUERY_EAS_FROM_LIST=0x0003, SMB_INFO_QUERY_ALL_EAS=0x0004, SMB_INFO_IS_NAME_VALID=0x0006, SMB_QUERY_FILE_BASIC_INFO=0x0101, SMB_QUERY_FILE_STANDARD_INFO=0x0102, SMB_QUERY_FILE_EA_INFO=0x0103, SMB_QUERY_FILE_NAME_INFO=0x0104, SMB_QUERY_FILE_ALL_INFO=0x0107, SMB_QUERY_FILE_ALT_NAME_INFO=0x0108, SMB_QUERY_FILE_STREAM_INFO=0x0109, SMB_QUERY_FILE_COMPRESSION_INFO=0x010B.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/QueryInformationLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/SetInformationLevel.cs -->
# Research: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/SetInformationLevel.cs

- **Purpose:** Defines protocol constants for SetInformationLevel. It is part of the SMB1 protocol enum surface under `SMBLibrary.SMB1`.
- **Source facts:** Read in full: 13 lines, 395 bytes. Namespace `SMBLibrary.SMB1`. Primary type `SetInformationLevel`.
- **Important APIs/types/functions:** Types: enum SetInformationLevel : ushort. Constructors: none. Constants/static metadata: none. Fields/properties: none detected. Methods/overrides: none detected. Enum values: SMB_INFO_STANDARD=0x0001, SMB_INFO_SET_EAS=0x0002, SMB_SET_FILE_BASIC_INFO=0x0101, SMB_SET_FILE_DISPOSITION_INFO=0x0102, SMB_SET_FILE_ALLOCATION_INFO=0x0103, SMB_SET_FILE_END_OF_FILE_INFO=0x0104.
- **Control flow:** There is no runtime branching; callers cast raw protocol values to this enum and combine flags where the enum has a Flags attribute.
- **State and persistence behavior:** Constants are static protocol metadata and do not change at runtime.
- **Dependencies:** Usings: none. Local dependencies and referenced protocol types: none.
- **Integration points:** Shared with SMB1FileStore helpers and TRANS2 query/set/find command payloads to select information-level structures.
- **Risks:** Primary risk is integration drift with SMB1 protocol constants and neighboring serializers.
- **Test signals:** numeric-value assertions against MS-SMB constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Enums/SetInformationLevel.cs -->
