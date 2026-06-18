# Group Research: subset-b-010014

This grouped report preserves one source-tree-aligned research section per assigned source file.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2EncryptionCapabilities.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2EncryptionCapabilities.java

## Purpose
Represents the SMB 3 encryption capabilities negotiate context. It serializes a non-empty ordered list of SMB3EncryptionCipher ids and parses the server's advertised cipher list back into enum values.

## Important APIs / Types / Functions
Defines class `SMB2EncryptionCapabilities` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2EncryptionCapabilities`, `writeContext`, `readContext`, `getCipherList`. Important fields include `cipherList`. Source size: 69 lines.

## Control Flow
Control flow is linear binary encoding: constructors select the negotiate context type, writeContext validates required fields and writes protocol-sized values, and readContext consumes counts or strings from SMBBuffer in wire order.

## State and Persistence
State fields observed: cipherList. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.mssmb2.SMB3EncryptionCipher, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer. JDK/JCE dependencies: java.util.ArrayList, java.util.List.

## Risks and Edge Cases
unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2EncryptionCapabilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContext.java

## Purpose
Provides the common header, factory, read, and write mechanics for SMB2 negotiate contexts. Subclasses contribute the variable data body while this base class handles context type, data length, reserved bytes, and 8-byte alignment skip on reads.

## Important APIs / Types / Functions
Defines class `SMB2NegotiateContext` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2NegotiateContext`, `write`, `writeContext`, `writeContextHeader`, `factory`, `read`, `readContext`, `readContextHeader`, `getNegotiateContextType`. Important fields include `negotiateContextType`. Source size: 114 lines.

## Control Flow
Control flow is serializer/parser oriented: write builds a temporary body, prefixes the context header, then appends body bytes; factory reads the context type and dispatches to the specific subclass; read consumes the data length, lets the subclass parse the body, then skips padding when more context bytes remain.

## State and Persistence
State fields observed: negotiateContextType. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer, com.hierynomus.smbj.common.SMBRuntimeException.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures; some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContextType.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContextType.java

## Purpose
Enumerates SMB2 negotiate context type wire values used by the negotiate context factory and serializers.

## Important APIs / Types / Functions
Defines enum `SMB2NegotiateContextType` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2NegotiateContextType`, `getValue`. Important fields include `value`. Source size: 38 lines.

## Control Flow
Control flow is serializer/parser oriented: write builds a temporary body, prefixes the context header, then appends body bytes; factory reads the context type and dispatches to the specific subclass; read consumes the data length, lets the subclass parse the body, then skips padding when more context bytes remain.

## State and Persistence
State fields observed: value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NegotiateContextType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NetNameNegotiateContextId.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NetNameNegotiateContextId.java

## Purpose
Models the SMB2 netname negotiate context with a UTF-16 null-terminated server name payload.

## Important APIs / Types / Functions
Defines class `SMB2NetNameNegotiateContextId` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2NetNameNegotiateContextId`, `writeContext`, `readContext`, `getNetName`. Important fields include `netName`. Source size: 52 lines.

## Control Flow
Control flow is linear binary encoding: constructors select the negotiate context type, writeContext validates required fields and writes protocol-sized values, and readContext consumes counts or strings from SMBBuffer in wire order.

## State and Persistence
State fields observed: netName. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2NetNameNegotiateContextId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2PreauthIntegrityCapabilities.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2PreauthIntegrityCapabilities.java

## Purpose
Models the SMB 3.1.1 preauthentication integrity capabilities context, including hash algorithm ids and the negotiate salt.

## Important APIs / Types / Functions
Defines class `SMB2PreauthIntegrityCapabilities` in package `com.hierynomus.mssmb2.messages.negotiate`. Important methods/functions include `SMB2PreauthIntegrityCapabilities`, `writeContext`, `readContext`, `getSalt`, `getHashAlgorithms`. Important fields include `DEFAULT_SALT_LENGTH`, `hashAlgorithms`, `salt`. Source size: 87 lines.

## Control Flow
Control flow is linear binary encoding: constructors select the negotiate context type, writeContext validates required fields and writes protocol-sized values, and readContext consumes counts or strings from SMBBuffer in wire order.

## State and Persistence
State fields observed: DEFAULT_SALT_LENGTH, hashAlgorithms, salt. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.mssmb2.SMB3HashAlgorithm, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smb.SMBBuffer. JDK/JCE dependencies: java.util.ArrayList, java.util.List.

## Risks and Edge Cases
unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures.

## Test Signals
Round-trip SMB2 negotiate-context fixtures with counts, unknown ids, alignment padding, and empty-field validation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/negotiate/SMB2PreauthIntegrityCapabilities.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/submodule/SMB2LockElement.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/submodule/SMB2LockElement.java

## Purpose
Carries one SMB2 lock range and validates that the supplied lock flag set is one of the protocol-permitted combinations.

## Important APIs / Types / Functions
Defines class `SMB2LockElement` in package `com.hierynomus.mssmb2.messages.submodule`. Important methods/functions include `SMB2LockElement`, `getOffset`, `getLength`, `getLockFlags`, `toString`. Important fields include `VALID_FLAG_COMBINATIONS`, `offset`, `length`, `lockFlags`. Source size: 66 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: VALID_FLAG_COMBINATIONS, offset, length, lockFlags. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.mssmb2.SMB2LockFlag. JDK/JCE dependencies: java.util.Arrays, java.util.EnumSet, java.util.List, java.util.Set.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/mssmb2/messages/submodule/SMB2LockElement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmConfig.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmConfig.java

## Purpose
Holds NTLM client configuration such as Windows version, workstation name, MIC/integrity preference, version omission behavior, and the 32-byte machine id used by single-host AV pairs.

## Important APIs / Types / Functions
Defines class `NtlmConfig` in package `com.hierynomus.ntlm`. Important methods/functions include `defaultConfig`, `builder`, `NtlmConfig`, `getWindowsVersion`, `getWorkstationName`, `isIntegrityEnabled`, `isOmitVersion`, `getMachineID`, `Builder`, `withWindowsVersion`, `withWorkstationName`, `withIntegrity`. Important fields include `windowsVersion`, `workstationName`, `integrity`, `omitVersion`, `machineID`, `config`. Source size: 128 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: windowsVersion, workstationName, integrity, omitVersion, machineID, config. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.WindowsVersion, com.hierynomus.ntlm.messages.WindowsVersion.NtlmRevisionCurrent, com.hierynomus.ntlm.messages.WindowsVersion.ProductMajorVersion, com.hierynomus.ntlm.messages.WindowsVersion.ProductMinorVersion. JDK/JCE dependencies: java.security.SecureRandom, java.util.Random.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; authentication behavior depends on nonce/machine-id randomness and should use SecureRandom in production.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmException.java

## Purpose
Runtime exception used to rethrow NTLM cryptographic or protocol failures without checked exception plumbing.

## Important APIs / Types / Functions
Defines class `NtlmException` in package `com.hierynomus.ntlm`. Important methods/functions include `NtlmException`. Source size: 37 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/NtlmException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvId.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvId.java

## Purpose
Enumerates NTLM target-info AV pair identifiers and their wire values.

## Important APIs / Types / Functions
Defines enum `AvId` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvId`, `getValue`. Important fields include `value`. Source size: 43 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPair.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPair.java

## Purpose
Abstract base for typed NTLM target-info AV pairs with common id/value storage and read/write contracts.

## Important APIs / Types / Functions
Defines class `AvPair` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPair`, `read`, `getValue`, `toString`. Important fields include `avId`, `value`. Source size: 54 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
State fields observed: avId, value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPair.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairChannelBindings.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairChannelBindings.java

## Purpose
Typed AV pair for MsvAvChannelBindings carrying raw channel-binding bytes.

## Important APIs / Types / Functions
Defines class `AvPairChannelBindings` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairChannelBindings`, `write`, `read`. Source size: 44 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairChannelBindings.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairEnd.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairEnd.java

## Purpose
Sentinel AV pair for MsvAvEOL with zero-length value.

## Important APIs / Types / Functions
Defines class `AvPairEnd` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairEnd`, `write`, `read`. Source size: 38 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairEnd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFactory.java

## Purpose
Dispatches NTLM target-info AV pair parsing by reading the AvId field and constructing the matching AvPair subtype.

## Important APIs / Types / Functions
Defines class `AvPairFactory` in package `com.hierynomus.ntlm.av`. Important methods/functions include `read`. Source size: 54 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException, com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFlags.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFlags.java

## Purpose
Typed AV pair for MsvAvFlags carrying a 32-bit flag value.

## Important APIs / Types / Functions
Defines class `AvPairFlags` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairFlags`, `write`, `read`. Source size: 44 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairFlags.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairSingleHost.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairSingleHost.java

## Purpose
Typed AV pair for MsvAvSingleHost carrying custom data and the configured 32-byte machine id.

## Important APIs / Types / Functions
Defines class `AvPairSingleHost` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairSingleHost`, `read`, `write`. Important fields include `machineID`. Source size: 51 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
State fields observed: machineID. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairSingleHost.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairString.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairString.java

## Purpose
Typed AV pair for UTF-16LE string-valued target-info fields such as NetBIOS and DNS names.

## Important APIs / Types / Functions
Defines class `AvPairString` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairString`, `read`, `write`. Source size: 45 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairString.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairTimestamp.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairTimestamp.java

## Purpose
Typed AV pair for MsvAvTimestamp using the shared MS-DTYP FileTime helpers.

## Important APIs / Types / Functions
Defines class `AvPairTimestamp` in package `com.hierynomus.ntlm.av`. Important methods/functions include `AvPairTimestamp`, `write`, `read`. Source size: 42 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.msdtyp.FileTime, com.hierynomus.msdtyp.MsDataTypes, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Buffer.BufferException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/av/AvPairTimestamp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/ComputedNtlmV2Response.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/ComputedNtlmV2Response.java

## Purpose
Simple result carrier for the NTLMv2 NT response, LM response, and session base key computed from a challenge.

## Important APIs / Types / Functions
Defines class `ComputedNtlmV2Response` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `ComputedNtlmV2Response`, `getNtResponse`, `getLmResponse`, `getSessionBaseKey`. Important fields include `ntResponse`, `lmResponse`, `sessionBaseKey`. Source size: 40 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: ntResponse, lmResponse, sessionBaseKey. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/ComputedNtlmV2Response.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmFunctions.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmFunctions.java

## Purpose
Central NTLM helper library for Unicode/OEM encoding, MD4/MD5/HMACT64 hashing, RC4 encryption, and DES key setup.

## Important APIs / Types / Functions
Defines class `NtlmFunctions` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `NtlmFunctions`, `unicode`, `oem`, `md4`, `hmac_md5`, `md5`, `rc4k`, `setupKey`, `getDESCipher`. Important fields include `UNICODE`. Source size: 168 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: UNICODE. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Cipher.CryptMode.ENCRYPT, com.hierynomus.ntlm.NtlmException, com.hierynomus.protocol.commons.Charsets, com.hierynomus.security.Cipher, com.hierynomus.security.Mac, com.hierynomus.security.MessageDigest, ... . JDK/JCE dependencies: java.nio.charset.Charset.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmFunctions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV1Functions.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV1Functions.java

## Purpose
Implements NTLMv1 one-way functions for NT and LAN Manager password hashes.

## Important APIs / Types / Functions
Defines class `NtlmV1Functions` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `NtlmV1Functions`, `NTOWFv1`, `LMOWFv1`. Important fields include `securityProvider`. Source size: 84 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: securityProvider. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.NtlmException, com.hierynomus.security.Cipher, com.hierynomus.security.SecurityException, com.hierynomus.security.SecurityProvider. JDK/JCE dependencies: java.io.UnsupportedEncodingException, java.util.Arrays, java.util.Random.

## Risks and Edge Cases
authentication behavior depends on nonce/machine-id randomness and should use SecureRandom in production; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV1Functions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV2Functions.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV2Functions.java

## Purpose
Implements NTLMv2 response-key, LMv2 response, NT proof string, NT response blob, session base key, and KXKEY derivation.

## Important APIs / Types / Functions
Defines class `NtlmV2Functions` in package `com.hierynomus.ntlm.functions`. Important methods/functions include `NtlmV2Functions`, `computeResponse`, `NTOWFv2`, `LMOWFv2`, `getLmV2Response`, `getNtV2Response`, `getSessionBaseKey`, `ntResponseTemp`, `ntProofStr`, `kxKey`. Important fields include `random`, `securityProvider`. Source size: 214 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: random, securityProvider. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.NtlmChallenge, com.hierynomus.ntlm.messages.TargetInfo, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Endian, com.hierynomus.security.SecurityProvider. JDK/JCE dependencies: java.util.Random. External dependencies: org.bouncycastle.util.Arrays.

## Risks and Edge Cases
authentication behavior depends on nonce/machine-id randomness and should use SecureRandom in production; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/functions/NtlmV2Functions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmAuthenticate.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmAuthenticate.java

## Purpose
Serializes NTLM AUTHENTICATE_MESSAGE fields, offsets, optional version, optional MIC, and payload byte arrays.

## Important APIs / Types / Functions
Defines class `NtlmAuthenticate` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmAuthenticate`, `getBaseMessageSize`, `write`, `setMic`, `getVersion`, `toString`. Important fields include `lmResponse`, `ntResponse`, `userName`, `domainName`, `workstation`, `encryptedRandomSessionKey`, `mic`. Source size: 139 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: lmResponse, ntResponse, userName, domainName, workstation, encryptedRandomSessionKey, mic. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.functions.NtlmFunctions, com.hierynomus.protocol.commons.ByteArrayUtils, com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Endian, ... . JDK/JCE dependencies: java.util.Set.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmAuthenticate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmChallenge.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmChallenge.java

## Purpose
Parses NTLM CHALLENGE_MESSAGE fields including target name, negotiate flags, server challenge, optional version, and target-info AV pairs.

## Important APIs / Types / Functions
Defines class `NtlmChallenge` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `read`, `readTargetInfo`, `readTargetName`, `readVersion`, `readTargetNameFields`, `readTargetInfoFields`, `getTargetName`, `getServerChallenge`, `getNegotiateFlags`, `getTargetInfo`, `getVersion`, `toString`. Important fields include `logger`, `targetNameLen`, `targetNameBufferOffset`, `negotiateFlags`, `serverChallenge`, `version`, `targetInfoLen`, `targetInfoBufferOffset`, `targetName`, `targetInfo`. Source size: 129 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: logger, targetNameLen, targetNameBufferOffset, negotiateFlags, serverChallenge, version, targetInfoLen, targetInfoBufferOffset, targetName, targetInfo. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.ByteArrayUtils, com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer. JDK/JCE dependencies: java.util.EnumSet. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmChallenge.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmMessage.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmMessage.java

## Purpose
Base class for NTLM messages that normalizes caller-provided flags with mandatory NTLM and Unicode defaults.

## Important APIs / Types / Functions
Defines class `NtlmMessage` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmMessage`. Important fields include `DEFAULT_FLAGS`, `negotiateFlags`, `version`. Source size: 36 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: DEFAULT_FLAGS, negotiateFlags, version. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.NtlmNegotiateFlag.*. JDK/JCE dependencies: java.util.EnumSet, java.util.Set.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmMessage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiate.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiate.java

## Purpose
Serializes NTLM NEGOTIATE_MESSAGE including flags, optional OEM domain/workstation fields, and optional version bytes.

## Important APIs / Types / Functions
Defines class `NtlmNegotiate` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmNegotiate`, `write`, `toString`. Important fields include `domain`, `workstation`, `omitVersion`. Source size: 98 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: domain, workstation, omitVersion. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.messages.Utils.EMPTY, com.hierynomus.ntlm.messages.Utils.writeOffsettedByteArrayFields, com.hierynomus.ntlm.functions.NtlmFunctions, com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.ntlm.messages.NtlmNegotiateFlag.*. JDK/JCE dependencies: java.util.Set.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiateFlag.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiateFlag.java

## Purpose
Source file in package com.hierynomus.ntlm.messages defining enum NtlmNegotiateFlag for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines enum `NtlmNegotiateFlag` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `NtlmNegotiateFlag`, `getValue`. Important fields include `value`. Source size: 60 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: value. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmNegotiateFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmPacket.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmPacket.java

## Purpose
Source file in package com.hierynomus.ntlm.messages defining class NtlmPacket for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `NtlmPacket` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `write`, `read`. Source size: 32 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/NtlmPacket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/TargetInfo.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/TargetInfo.java

## Purpose
Mutable collection of NTLM AV pairs with read-until-EOL parsing, write-with-EOL serialization, copy, get, put, and existence helpers.

## Important APIs / Types / Functions
Defines class `TargetInfo` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `TargetInfo`, `readFrom`, `writeTo`, `copy`, `getAvPair`, `putAvPair`, `hasAvPair`, `toString`. Important fields include `logger`, `targetInfo`. Source size: 99 lines.

## Control Flow
Control flow follows NTLM AV pair framing: readers consume AvId/AvLen/value tuples, factories dispatch by AvId, TargetInfo loops until MsvAvEOL, and writers emit each pair followed by the end sentinel.

## State and Persistence
State fields observed: logger, targetInfo. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.ntlm.av.AvId, com.hierynomus.ntlm.av.AvPair, com.hierynomus.ntlm.av.AvPairEnd, com.hierynomus.ntlm.av.AvPairFactory, com.hierynomus.protocol.commons.buffer.Buffer. JDK/JCE dependencies: java.util.ArrayList, java.util.List. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/TargetInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/Utils.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/Utils.java

## Purpose
Source file in package com.hierynomus.ntlm.messages defining class Utils for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `Utils` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `Utils`, `writeOffsettedByteArrayFields`, `ensureNotNull`. Important fields include `EMPTY`. Source size: 46 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: EMPTY. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.ntlm.functions.NtlmFunctions.unicode.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/WindowsVersion.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/WindowsVersion.java

## Purpose
Represents the NTLM VERSION structure and nested enums for product major, minor, build, and revision values.

## Important APIs / Types / Functions
Defines class `WindowsVersion` in package `com.hierynomus.ntlm.messages`. Important methods/functions include `ProductMajorVersion`, `getValue`, `ProductMinorVersion`, `NtlmRevisionCurrent`, `WindowsVersion`, `readFrom`, `writeTo`, `toString`, `equals`, `hashCode`, `getNtlmRevision`. Important fields include `value`, `value`, `value`, `majorVersion`, `minorVersion`, `productBuild`, `ntlmRevision`. Source size: 130 lines.

## Control Flow
Control flow is NTLM message construction or parsing: security-buffer length/offset records are written first, payloads follow at computed offsets, and challenge parsing repositions the Buffer read cursor to offset-described target name and target-info payloads.

## State and Persistence
State fields observed: value, value, value, majorVersion, minorVersion, productBuild, ntlmRevision. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.EnumWithValue, com.hierynomus.protocol.commons.buffer.Buffer. JDK/JCE dependencies: java.util.Objects.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; unknown enum values must be handled deliberately to avoid null propagation or unexpected runtime failures; mutable byte arrays can be modified by callers after construction.

## Test Signals
Use MS-NLMP known-answer vectors for negotiate/challenge/authenticate bytes and NTLMv1/v2 hashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/ntlm/messages/WindowsVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/Packet.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/Packet.java

## Purpose
Source file in package com.hierynomus.protocol defining interface Packet for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines interface `Packet` in package `com.hierynomus.protocol`. Source size: 25 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/Packet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/PacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/PacketData.java

## Purpose
Source file in package com.hierynomus.protocol defining interface PacketData for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines interface `PacketData` in package `com.hierynomus.protocol`. Source size: 26 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/PacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/ByteArrayUtils.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/ByteArrayUtils.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class ByteArrayUtils for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `ByteArrayUtils` in package `com.hierynomus.protocol.commons`. Important methods/functions include `equals`, `printHex`, `toHex`, `parseHex`, `parseHexDigit`. Source size: 143 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/ByteArrayUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Charsets.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Charsets.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class Charsets for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `Charsets` in package `com.hierynomus.protocol.commons`. Important methods/functions include `Charsets`. Important fields include `UTF_8`, `UTF_16BE`, `UTF_16LE`, `UTF_16`, `US_ASCII`. Source size: 32 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: UTF_8, UTF_16BE, UTF_16LE, UTF_16, US_ASCII. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.nio.charset.Charset.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Charsets.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/EnumWithValue.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/EnumWithValue.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining interface EnumWithValue for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines interface `EnumWithValue` in package `com.hierynomus.protocol.commons`. Important methods/functions include `toLong`, `toEnumSet`, `isSet`, `valueOf`, `ensureNotNull`. Source size: 79 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.Collection, java.util.EnumSet, java.util.Set.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/EnumWithValue.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Factory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Factory.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining interface Factory for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines interface `Factory` in package `com.hierynomus.protocol.commons`. Important methods/functions include `create`, `get`, `getNames`. Source size: 105 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.LinkedList, java.util.List.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Factory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/IOUtils.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/IOUtils.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class IOUtils for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `IOUtils` in package `com.hierynomus.protocol.commons`. Important methods/functions include `closeQuietly`, `closeSilently`. Important fields include `logger`. Source size: 48 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: logger. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/IOUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Objects.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Objects.java

## Purpose
Source file in package com.hierynomus.protocol.commons defining class Objects for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `Objects` in package `com.hierynomus.protocol.commons`. Important methods/functions include `Objects`, `equals`, `hash`. Source size: 32 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.Arrays.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/Objects.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/backport/JavaVersion.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/backport/JavaVersion.java

## Purpose
Source file in package com.hierynomus.protocol.commons.backport defining class JavaVersion for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines class `JavaVersion` in package `com.hierynomus.protocol.commons.backport`. Important methods/functions include `isJava7OrEarlier`. Source size: 26 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/backport/JavaVersion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/backport/Jdk7HttpProxySocket.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/backport/Jdk7HttpProxySocket.java

## Purpose
Socket wrapper for Java 7 HTTP CONNECT proxy support before the JDK supplied native behavior.

## Important APIs / Types / Functions
Defines class `Jdk7HttpProxySocket` in package `com.hierynomus.protocol.commons.backport`. Important methods/functions include `Jdk7HttpProxySocket`, `connect`, `connectHttpProxy`, `checkAndFlushProxyResponse`. Important fields include `httpProxy`. Source size: 82 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: httpProxy. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets. JDK/JCE dependencies: java.io.IOException, java.io.InputStream, java.net.*.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction; network timeouts, proxy parsing, and close behavior need integration tests.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/backport/Jdk7HttpProxySocket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Buffer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Buffer.java

## Purpose
Generic mutable read/write byte buffer with endian-aware primitive, string, null-terminated string, skip, compact, and InputStream helpers.

## Important APIs / Types / Functions
Defines class `Buffer` in package `com.hierynomus.protocol.commons.buffer`. Important methods/functions include `BufferException`, `PlainBuffer`, `getNextPowerOf2`, `Buffer`, `array`, `available`, `clear`, `rpos`, `wpos`, `ensureAvailable`, `ensureCapacity`, `compact`. Important fields include `logger`, `DEFAULT_SIZE`, `MAX_SIZE`, `data`, `endianness`, `rpos`, `wpos`. Source size: 792 lines.

## Control Flow
Control flow is cursor based: read methods check availability and advance rpos, write methods ensure capacity and advance wpos, endian helpers implement primitive byte order, and string helpers select UTF-16/UTF-8 behavior from Charset names.

## State and Persistence
State fields observed: logger, DEFAULT_SIZE, MAX_SIZE, data, endianness, rpos, wpos. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.ByteArrayUtils. JDK/JCE dependencies: java.io.ByteArrayOutputStream, java.io.IOException, java.io.InputStream, java.nio.charset.Charset, java.nio.charset.UnsupportedCharsetException. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Exercise endian read/write values, boundary underflow, capacity growth, string encodings, null-terminated strings, and InputStream behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Buffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Endian.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Endian.java

## Purpose
Defines big-endian and little-endian primitive/string codecs used by Buffer and SMBBuffer.

## Important APIs / Types / Functions
Defines class `to` in package `com.hierynomus.protocol.commons.buffer`. Important methods/functions include `readNullTerminatedUtf16String`, `readUtf16String`, `writeNullTerminatedUtf16String`, `writeUInt16`, `readUInt16`, `writeUInt24`, `readUInt24`, `writeUInt32`, `readUInt32`, `writeUInt64`, `readUInt64`, `writeLong`. Important fields include `NULL_TERMINATOR`, `LE`, `BE`. Source size: 322 lines.

## Control Flow
Control flow is cursor based: read methods check availability and advance rpos, write methods ensure capacity and advance wpos, endian helpers implement primitive byte order, and string helpers select UTF-16/UTF-8 behavior from Charset names.

## State and Persistence
State fields observed: NULL_TERMINATOR, LE, BE. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets. JDK/JCE dependencies: java.io.ByteArrayOutputStream, java.nio.charset.Charset.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Exercise endian read/write values, boundary underflow, capacity growth, string encodings, null-terminated strings, and InputStream behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/buffer/Endian.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/AFuture.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/AFuture.java

## Purpose
Small concurrency utility in the protocol commons layer. AFuture adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines class `AFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `map`. Source size: 28 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.concurrent.Future.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/AFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/CancellableFuture.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/CancellableFuture.java

## Purpose
Future wrapper that coordinates cancellation with an external callback while delegating blocking get operations to a wrapped AFuture.

## Important APIs / Types / Functions
Defines class `CancellableFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `CancellableFuture`, `cancel`, `isCancelled`, `isDone`, `get`. Important fields include `wrappedFuture`, `callback`, `cancelled`, `lock`. Source size: 90 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: wrappedFuture, callback, cancelled, lock. Concurrency state is explicit and lives only in process memory. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.common.SMBRuntimeException. JDK/JCE dependencies: java.util.concurrent.ExecutionException, java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException, java.util.concurrent.atomic.AtomicBoolean, java.util.concurrent.locks.ReentrantReadWriteLock.

## Risks and Edge Cases
concurrency semantics need tests for timeout, cancellation, interruption, and double-close paths.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/CancellableFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/ExceptionWrapper.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/ExceptionWrapper.java

## Purpose
Small concurrency utility in the protocol commons layer. ExceptionWrapper adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines interface `ExceptionWrapper` in package `com.hierynomus.protocol.commons.concurrent`. Source size: 21 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/ExceptionWrapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/Futures.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/Futures.java

## Purpose
Small concurrency utility in the protocol commons layer. Futures adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines class `Futures` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `get`, `sequence`, `transform`. Source size: 58 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.concurrent.AFuture.Function. JDK/JCE dependencies: java.util.List, java.util.concurrent.ExecutionException, java.util.concurrent.Future, java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/Futures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/Promise.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/Promise.java

## Purpose
Lock/condition-backed promise used to deliver either a value or a wrapped error to waiting futures.

## Important APIs / Types / Functions
Defines class `Promise` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `Promise`, `deliver`, `deliverError`, `clear`, `retrieve`, `tryRetrieve`, `isDelivered`, `inError`, `isFulfilled`, `hasWaiters`, `lock`, `unlock`. Important fields include `logger`, `name`, `wrapper`, `lock`, `cond`, `val`, `pendingEx`. Source size: 259 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: logger, name, wrapper, lock, cond, val, pendingEx. Concurrency state is explicit and lives only in process memory. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException, java.util.concurrent.locks.Condition, java.util.concurrent.locks.ReentrantLock. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
concurrency semantics need tests for timeout, cancellation, interruption, and double-close paths.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/Promise.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/PromiseBackedFuture.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/PromiseBackedFuture.java

## Purpose
Small concurrency utility in the protocol commons layer. PromiseBackedFuture adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines class `PromiseBackedFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `PromiseBackedFuture`, `cancel`, `isCancelled`, `isDone`, `get`. Important fields include `promise`. Source size: 62 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: promise. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.concurrent.ExecutionException, java.util.concurrent.TimeUnit.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/PromiseBackedFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/SequencedFuture.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/SequencedFuture.java

## Purpose
Small concurrency utility in the protocol commons layer. SequencedFuture adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines class `SequencedFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `SequencedFuture`, `isCancelled`, `cancel`, `isDone`, `get`. Important fields include `futures`. Source size: 81 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: futures. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.ArrayList, java.util.List, java.util.concurrent.ExecutionException, java.util.concurrent.Future, java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/SequencedFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/TransformedFuture.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/TransformedFuture.java

## Purpose
Small concurrency utility in the protocol commons layer. TransformedFuture adapts Java Future/lock patterns into the project AFuture, promise, sequencing, transformation, or exception-wrapping model.

## Important APIs / Types / Functions
Defines class `TransformedFuture` in package `com.hierynomus.protocol.commons.concurrent`. Important methods/functions include `TransformedFuture`, `cancel`, `isCancelled`, `isDone`, `get`. Important fields include `wrapped`, `function`. Source size: 56 lines.

## Control Flow
Control flow centers on Future or Promise state transitions. Callers deliver values or errors, wait with optional timeouts, sequence or transform wrapped futures, and cancellation wrappers invoke external callbacks while delegating result retrieval.

## State and Persistence
State fields observed: wrapped, function. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.concurrent.ExecutionException, java.util.concurrent.Future, java.util.concurrent.TimeUnit, java.util.concurrent.TimeoutException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Cover success, timeout, wrapped error, interrupted wait, cancellation callback, and transformed/sequenced future ordering.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/concurrent/TransformedFuture.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/socket/ProxySocketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/socket/ProxySocketFactory.java

## Purpose
SocketFactory implementation that creates sockets through an optional Proxy and applies a configurable connect timeout.

## Important APIs / Types / Functions
Defines class `ProxySocketFactory` in package `com.hierynomus.protocol.commons.socket`. Important methods/functions include `ProxySocketFactory`, `createSocket`, `getHttpProxy`. Important fields include `logger`, `DEFAULT_CONNECT_TIMEOUT`, `proxy`, `connectTimeout`. Source size: 94 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: logger, DEFAULT_CONNECT_TIMEOUT, proxy, connectTimeout. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: javax.net.SocketFactory, java.io.IOException, java.net.InetAddress, java.net.InetSocketAddress, java.net.Proxy, java.net.Socket. External dependencies: org.slf4j.Logger, org.slf4j.LoggerFactory.

## Risks and Edge Cases
network timeouts, proxy parsing, and close behavior need integration tests.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/commons/socket/ProxySocketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/package-info.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/package-info.java

## Purpose
Source file in package com.hierynomus.protocol defining package x for the SMBJ user-network filesystem source tree.

## Important APIs / Types / Functions
Defines package `x` in package `com.hierynomus.protocol`. Source size: 21 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketFactory.java

## Purpose
Generic transport-layer contract or holder for packet IO. PacketFactory helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines interface `PacketFactory` in package `com.hierynomus.protocol.transport`. Important methods/functions include `read`. Source size: 40 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.PacketData, com.hierynomus.protocol.commons.buffer.Buffer. JDK/JCE dependencies: java.io.IOException.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketHandlers.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketHandlers.java

## Purpose
Generic transport-layer contract or holder for packet IO. PacketHandlers helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines class `PacketHandlers` in package `com.hierynomus.protocol.transport`. Important methods/functions include `PacketHandlers`, `getSerializer`, `getReceiver`, `getPacketFactory`. Important fields include `serializer`, `receiver`, `packetFactory`. Source size: 49 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: serializer, receiver, packetFactory. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.PacketData.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketHandlers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketReceiver.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketReceiver.java

## Purpose
Generic transport-layer contract or holder for packet IO. PacketReceiver helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines interface `PacketReceiver` in package `com.hierynomus.protocol.transport`. Source size: 24 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.PacketData.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketReceiver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketSerializer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketSerializer.java

## Purpose
Generic transport-layer contract or holder for packet IO. PacketSerializer helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines interface `PacketSerializer` in package `com.hierynomus.protocol.transport`. Source size: 29 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/PacketSerializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportException.java

## Purpose
Generic transport-layer contract or holder for packet IO. TransportException helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines class `TransportException` in package `com.hierynomus.protocol.transport`. Important methods/functions include `wrap`, `TransportException`. Important fields include `Wrapper`. Source size: 45 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: Wrapper. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.concurrent.ExceptionWrapper. JDK/JCE dependencies: java.io.IOException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportLayer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportLayer.java

## Purpose
Generic transport-layer contract or holder for packet IO. TransportLayer helps connect protocol-neutral Packet/PacketData objects to serializers, receivers, factories, and connection implementations.

## Important APIs / Types / Functions
Defines interface `TransportLayer` in package `com.hierynomus.protocol.transport`. Source size: 50 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet. JDK/JCE dependencies: java.io.IOException, java.net.InetSocketAddress.

## Risks and Edge Cases
network timeouts, proxy parsing, and close behavior need integration tests.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/protocol/transport/TransportLayer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/AEADBlockCipher.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/AEADBlockCipher.java

## Purpose
Security abstraction type. AEADBlockCipher defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines interface `AEADBlockCipher` in package `com.hierynomus.security`. Source size: 32 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: javax.crypto.spec.GCMParameterSpec.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/AEADBlockCipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/Cipher.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/Cipher.java

## Purpose
Security abstraction type. Cipher defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines interface `Cipher` in package `com.hierynomus.security`. Source size: 28 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/Cipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/DerivationFunction.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/DerivationFunction.java

## Purpose
Security abstraction type. DerivationFunction defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines interface `DerivationFunction` in package `com.hierynomus.security`. Source size: 25 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.jce.derivationfunction.DerivationParameters.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/DerivationFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/Mac.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/Mac.java

## Purpose
Security abstraction type. Mac defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines interface `Mac` in package `com.hierynomus.security`. Source size: 30 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/Mac.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/MessageDigest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/MessageDigest.java

## Purpose
Security abstraction type. MessageDigest defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines interface `MessageDigest` in package `com.hierynomus.security`. Source size: 30 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/MessageDigest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityException.java

## Purpose
Security abstraction type. SecurityException defines the project-facing contract used by NTLM and SMB cryptographic code without binding callers to JCE or Bouncy Castle.

## Important APIs / Types / Functions
Defines class `SecurityException` in package `com.hierynomus.security`. Important methods/functions include `SecurityException`. Source size: 27 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityProvider.java

## Purpose
Abstraction boundary for digest, MAC, cipher, AEAD cipher, and derivation-function implementations.

## Important APIs / Types / Functions
Defines interface `SecurityProvider` in package `com.hierynomus.security`. Source size: 40 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/SecurityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCAEADCipherFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCAEADCipherFactory.java

## Purpose
Bouncy Castle direct AEAD factory for AES/CCM/NoPadding and AES/GCM/NoPadding wrapped in the project AEADBlockCipher interface.

## Important APIs / Types / Functions
Defines class `BCAEADCipherFactory` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCAEADBlockCipher`, `createParams`, `init`, `updateAAD`, `update`, `doFinal`, `reset`. Important fields include `lookup`, `wrappedCipher`. Source size: 128 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, wrappedCipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.AEADBlockCipher, com.hierynomus.security.Cipher.CryptMode, com.hierynomus.security.SecurityException. JDK/JCE dependencies: java.util.HashMap, java.util.Map, javax.crypto.spec.GCMParameterSpec. External dependencies: org.bouncycastle.crypto.CipherParameters, org.bouncycastle.crypto.InvalidCipherTextException, org.bouncycastle.crypto.engines.AESEngine, org.bouncycastle.crypto.modes.CCMBlockCipher, org.bouncycastle.crypto.modes.GCMBlockCipher, org.bouncycastle.crypto.params.AEADParameters, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCAEADCipherFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCCipherFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCCipherFactory.java

## Purpose
Bouncy Castle direct cipher factory for DES/ECB/NoPadding and RC4 wrapped behind the project Cipher interface.

## Important APIs / Types / Functions
Defines class `BCCipherFactory` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCBlockCipher`, `createParams`, `BCStreamCipher`, `init`, `update`, `doFinal`, `reset`. Important fields include `lookup`, `wrappedCipher`, `streamCipher`. Source size: 136 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, wrappedCipher, streamCipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.Cipher, com.hierynomus.security.SecurityException. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.BufferedBlockCipher, org.bouncycastle.crypto.CipherParameters, org.bouncycastle.crypto.InvalidCipherTextException, org.bouncycastle.crypto.StreamCipher, org.bouncycastle.crypto.engines.DESEngine, org.bouncycastle.crypto.engines.RC4Engine, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCCipherFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCDerivationFunctionFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCDerivationFunctionFactory.java

## Purpose
Bouncy Castle direct counter-mode KDF factory for KDF/Counter/HMACSHA256.

## Important APIs / Types / Functions
Defines class `BCDerivationFunctionFactory` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCDerivationFunction`, `createParams`, `init`, `generateBytes`. Important fields include `lookup`, `function`. Source size: 79 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, function. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.DerivationFunction, com.hierynomus.security.jce.derivationfunction.CounterDerivationParameters, com.hierynomus.security.jce.derivationfunction.DerivationParameters. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.digests.SHA256Digest, org.bouncycastle.crypto.generators.KDFCounterBytesGenerator, org.bouncycastle.crypto.macs.HMac, org.bouncycastle.crypto.params.KDFCounterParameters.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCDerivationFunctionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMac.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMac.java

## Purpose
Direct Bouncy Castle security adapter. BCMac maps project-level algorithm names to Bouncy Castle digest, MAC, cipher, AEAD, or KDF implementations.

## Important APIs / Types / Functions
Defines class `BCMac` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCMac`, `getMacFactory`, `init`, `update`, `doFinal`, `reset`. Important fields include `lookup`, `mac`. Source size: 100 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, mac. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.Mac. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.digests.MD5Digest, org.bouncycastle.crypto.digests.SHA256Digest, org.bouncycastle.crypto.engines.AESEngine, org.bouncycastle.crypto.macs.CMac, org.bouncycastle.crypto.macs.HMac, org.bouncycastle.crypto.params.KeyParameter.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMac.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMessageDigest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMessageDigest.java

## Purpose
Direct Bouncy Castle security adapter. BCMessageDigest maps project-level algorithm names to Bouncy Castle digest, MAC, cipher, AEAD, or KDF implementations.

## Important APIs / Types / Functions
Defines class `BCMessageDigest` in package `com.hierynomus.security.bc`. Important methods/functions include `create`, `BCMessageDigest`, `getDigest`, `update`, `digest`, `reset`, `getDigestLength`. Important fields include `lookup`, `digest`. Source size: 105 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup, digest. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.MessageDigest. JDK/JCE dependencies: java.util.HashMap, java.util.Map. External dependencies: org.bouncycastle.crypto.Digest, org.bouncycastle.crypto.digests.MD4Digest, org.bouncycastle.crypto.digests.MD5Digest, org.bouncycastle.crypto.digests.SHA256Digest, org.bouncycastle.crypto.digests.SHA512Digest.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCMessageDigest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCSecurityProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCSecurityProvider.java

## Purpose
SecurityProvider implementation backed by direct Bouncy Castle primitives and the local HMACT64 adapter.

## Important APIs / Types / Functions
Defines class `BCSecurityProvider` in package `com.hierynomus.security.bc`. Important methods/functions include `getDigest`, `getMac`, `getCipher`, `getAEADBlockCipher`, `getDerivationFunction`. Source size: 61 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.AEADBlockCipher, com.hierynomus.security.Cipher, com.hierynomus.security.DerivationFunction, com.hierynomus.security.Mac, com.hierynomus.security.MessageDigest, com.hierynomus.security.SecurityProvider, ... . JDK/JCE dependencies: java.util.Objects.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/bc/BCSecurityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceAEADCipher.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceAEADCipher.java

## Purpose
JCE-backed security adapter. JceAEADCipher wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceAEADCipher` in package `com.hierynomus.security.jce`. Important methods/functions include `JceAEADCipher`, `init`, `updateAAD`, `update`, `doFinal`, `reset`. Important fields include `cipher`. Source size: 87 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: cipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.AEADBlockCipher, com.hierynomus.security.Cipher.CryptMode, com.hierynomus.security.SecurityException. JDK/JCE dependencies: java.security.InvalidAlgorithmParameterException, java.security.InvalidKeyException, java.security.NoSuchAlgorithmException, java.security.NoSuchProviderException, java.security.Provider, javax.crypto.BadPaddingException, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceAEADCipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceCipher.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceCipher.java

## Purpose
JCE-backed security adapter. JceCipher wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceCipher` in package `com.hierynomus.security.jce`. Important methods/functions include `JceCipher`, `init`, `update`, `doFinal`, `reset`. Important fields include `cipher`. Source size: 83 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: cipher. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Cipher, com.hierynomus.security.SecurityException. JDK/JCE dependencies: javax.crypto.BadPaddingException, javax.crypto.IllegalBlockSizeException, javax.crypto.NoSuchPaddingException, javax.crypto.ShortBufferException, javax.crypto.spec.SecretKeySpec, java.security.InvalidKeyException, ... .

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceCipher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunction.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunction.java

## Purpose
JCE-backed security adapter. JceDerivationFunction wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceDerivationFunction` in package `com.hierynomus.security.jce`. Important methods/functions include `init`, `generateBytes`. Source size: 33 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.DerivationFunction, com.hierynomus.security.SecurityException, com.hierynomus.security.jce.derivationfunction.DerivationParameters.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage; mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunction.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunctionFactory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunctionFactory.java

## Purpose
JCE-backed security adapter. JceDerivationFunctionFactory wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceDerivationFunctionFactory` in package `com.hierynomus.security.jce`. Important methods/functions include `create`. Important fields include `lookup`. Source size: 53 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: lookup. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Factory, com.hierynomus.security.DerivationFunction, com.hierynomus.security.jce.derivationfunction.KDFCounterHMacSHA256. JDK/JCE dependencies: java.security.NoSuchAlgorithmException, java.util.HashMap, java.util.Map.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceDerivationFunctionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMac.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMac.java

## Purpose
JCE-backed security adapter. JceMac wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceMac` in package `com.hierynomus.security.jce`. Important methods/functions include `JceMac`, `init`, `update`, `doFinal`, `reset`. Important fields include `algorithm`, `mac`. Source size: 79 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: algorithm, mac. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Mac, com.hierynomus.security.SecurityException. JDK/JCE dependencies: javax.crypto.spec.SecretKeySpec, java.security.InvalidKeyException, java.security.NoSuchAlgorithmException, java.security.NoSuchProviderException, java.security.Provider.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMac.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMessageDigest.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMessageDigest.java

## Purpose
JCE-backed security adapter. JceMessageDigest wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `JceMessageDigest` in package `com.hierynomus.security.jce`. Important methods/functions include `JceMessageDigest`, `update`, `digest`, `reset`, `getDigestLength`. Important fields include `md`. Source size: 79 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: md. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.MessageDigest, com.hierynomus.security.SecurityException, com.hierynomus.security.jce.messagedigest.MD4. JDK/JCE dependencies: java.security.NoSuchAlgorithmException, java.security.NoSuchProviderException, java.security.Provider.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceMessageDigest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceSecurityProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceSecurityProvider.java

## Purpose
SecurityProvider implementation backed by the configured JCE provider, provider name, or platform default.

## Important APIs / Types / Functions
Defines class `JceSecurityProvider` in package `com.hierynomus.security.jce`. Important methods/functions include `JceSecurityProvider`, `getDigest`, `getMac`, `getCipher`, `getAEADBlockCipher`, `getDerivationFunction`. Important fields include `jceProvider`, `providerName`. Source size: 71 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: jceProvider, providerName. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.*, com.hierynomus.security.SecurityException, com.hierynomus.security.mac.HmacT64. JDK/JCE dependencies: java.security.Provider, java.util.Objects.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/JceSecurityProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/CounterDerivationParameters.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/CounterDerivationParameters.java

## Purpose
JCE-backed security adapter. CounterDerivationParameters wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines class `CounterDerivationParameters` in package `com.hierynomus.security.jce.derivationfunction`. Important methods/functions include `CounterDerivationParameters`, `getSeed`, `getFixedCounterSuffix`, `getCounterLength`. Important fields include `seed`, `fixedCounterSuffix`, `counterLength`. Source size: 53 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: seed, fixedCounterSuffix, counterLength. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.util.Arrays.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/CounterDerivationParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/DerivationParameters.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/DerivationParameters.java

## Purpose
JCE-backed security adapter. DerivationParameters wraps platform crypto APIs behind the project interfaces while normalizing provider selection and exception types.

## Important APIs / Types / Functions
Defines interface `DerivationParameters` in package `com.hierynomus.security.jce.derivationfunction`. Source size: 19 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/DerivationParameters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256.java

## Purpose
JCE implementation of counter-mode HMAC-SHA256 derivation used by SMB signing/encryption key derivation flows.

## Important APIs / Types / Functions
Defines class `KDFCounterHMacSHA256` in package `com.hierynomus.security.jce.derivationfunction`. Important methods/functions include `KDFCounterHMacSHA256`, `init`, `generateBytes`. Important fields include `mac`, `fixedSuffix`, `maxLength`. Source size: 80 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: mac, fixedSuffix, maxLength. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.SecurityException, com.hierynomus.security.jce.JceDerivationFunction. JDK/JCE dependencies: java.security.InvalidKeyException, java.security.NoSuchAlgorithmException, javax.crypto.Mac, javax.crypto.spec.SecretKeySpec.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/derivationfunction/KDFCounterHMacSHA256.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/messagedigest/MD4.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/messagedigest/MD4.java

## Purpose
Pure Java MD4 MessageDigest fallback used when the active JCE provider does not supply MD4.

## Important APIs / Types / Functions
Defines class `MD4` in package `com.hierynomus.security.jce.messagedigest`. Important methods/functions include `MD4`, `engineGetDigestLength`, `engineUpdate`, `engineDigest`, `engineReset`, `pad`, `process`. Important fields include `BYTE_DIGEST_LENGTH`, `BYTE_BLOCK_LENGTH`, `A`, `B`, `C`, `D`, `a`, `b`, `c`, `d`, `msgLength`, `buffer`. Source size: 314 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: BYTE_DIGEST_LENGTH, BYTE_BLOCK_LENGTH, A, B, C, D, a, b, c, d, msgLength, buffer. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.security.DigestException, java.security.MessageDigest.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction; legacy NTLM primitives are cryptographically weak but protocol-required for compatibility.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/jce/messagedigest/MD4.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/mac/HmacT64.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/mac/HmacT64.java

## Purpose
Implements the NTLM-specific HMACT64 variant, a modified HMAC-MD5 that truncates long keys rather than hashing them.

## Important APIs / Types / Functions
Defines class `HmacT64` in package `com.hierynomus.security.mac`. Important methods/functions include `HmacT64`, `init`, `doFinal`, `update`, `reset`. Important fields include `BLOCK_LENGTH`, `IPAD`, `OPAD`, `md5`, `ipad`, `opad`. Source size: 112 lines.

## Control Flow
Control flow maps an algorithm name to a concrete primitive, initializes it with caller-provided key or derivation parameters, streams update bytes, finalizes output, and wraps provider exceptions in the project SecurityException when required.

## State and Persistence
State fields observed: BLOCK_LENGTH, IPAD, OPAD, md5, ipad, opad. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.security.Mac, com.hierynomus.security.MessageDigest, com.hierynomus.security.SecurityException.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compare outputs with published digest/MAC/KDF/cipher vectors and run provider parity checks between JCE and Bouncy Castle paths.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/security/mac/HmacT64.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/Packets.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/Packets.java

## Purpose
Extracts serialized SMB packet bytes from a packet's SMBBuffer using header start and message end positions while preserving the original read cursor.

## Important APIs / Types / Functions
Defines class `Packets` in package `com.hierynomus.smb`. Important methods/functions include `getPacketBytes`. Source size: 43 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.smbj.common.SMBRuntimeException.

## Risks and Edge Cases
offset and cursor math should be fuzzed for malformed or truncated packets; mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/Packets.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBBuffer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBBuffer.java

## Purpose
SMB-specific little-endian Buffer specialization with reserved-byte writers and UTF-16 string length helpers.

## Important APIs / Types / Functions
Defines class `SMBBuffer` in package `com.hierynomus.smb`. Important methods/functions include `SMBBuffer`, `putReserved`, `putReserved1`, `putReserved2`, `putReserved4`, `putString`, `putStringLengthUInt16`. Important fields include `RESERVED_2`, `RESERVED_4`. Source size: 101 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: RESERVED_2, RESERVED_4. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.Charsets, com.hierynomus.protocol.commons.buffer.Buffer, com.hierynomus.protocol.commons.buffer.Endian. JDK/JCE dependencies: java.util.Arrays.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBHeader.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBHeader.java

## Purpose
SMB packet infrastructure type. SMBHeader connects the generic protocol buffer/packet contracts to SMB-specific headers, packet data, and little-endian wire buffers.

## Important APIs / Types / Functions
Defines interface `SMBHeader` in package `com.hierynomus.smb`. Source size: 28 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacket.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacket.java

## Purpose
SMB packet infrastructure type. SMBPacket connects the generic protocol buffer/packet contracts to SMB-specific headers, packet data, and little-endian wire buffers.

## Important APIs / Types / Functions
Defines class `SMBPacket` in package `com.hierynomus.smb`. Important methods/functions include `SMBPacket`, `getHeader`, `read`, `getBuffer`. Important fields include `header`, `buffer`. Source size: 43 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: header, buffer. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.Packet, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
some API surface intentionally throws unsupported/TODO behavior and callers need explicit coverage.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacket.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacketData.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacketData.java

## Purpose
Partial SMB packet data holder that reads a header from a backing SMBBuffer before a concrete packet is selected.

## Important APIs / Types / Functions
Defines class `SMBPacketData` in package `com.hierynomus.smb`. Important methods/functions include `SMBPacketData`, `readHeader`, `getHeader`, `getDataBuffer`. Important fields include `header`, `dataBuffer`. Source size: 58 lines.

## Control Flow
Control flow is simple delegation through the package's interface or data holder contract.

## State and Persistence
State fields observed: header, dataBuffer. Several byte-array values are kept in memory and should be treated as mutable caller-owned data unless explicitly cloned. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.protocol.PacketData, com.hierynomus.protocol.commons.buffer.Buffer.

## Risks and Edge Cases
mutable byte arrays can be modified by callers after construction.

## Test Signals
Compile-time contract tests and focused unit tests around public methods are the primary signal.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smb/SMBPacketData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/FileTimes.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/FileTimes.java

## Purpose
Small conversion helper from SMB/MS-DTYP FileTime to java.nio.file.attribute.FileTime.

## Important APIs / Types / Functions
Defines class `FileTimes` in package `com.hierynomus.smbfs`. Important methods/functions include `FileTimes`, `fromSmb`. Source size: 27 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.nio.file.attribute.FileTime.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/FileTimes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/InvalidShareException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/InvalidShareException.java

## Purpose
Runtime exception used by the SMB filesystem provider when a URI names an invalid share.

## Important APIs / Types / Functions
Defines class `InvalidShareException` in package `com.hierynomus.smbfs`. Important methods/functions include `InvalidShareException`. Source size: 25 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Dependencies are limited to same-package language constructs and no explicit imports.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/InvalidShareException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSource.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSource.java

## Purpose
Internal abstraction for opening named DiskShare instances and closing the holder that owns related network resources.

## Important APIs / Types / Functions
Defines interface `ShareSource` in package `com.hierynomus.smbfs`. Important methods/functions include `open`. Source size: 31 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
No durable instance state is defined; behavior is stateless or contract-only. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.share.DiskShare. JDK/JCE dependencies: java.io.Closeable, java.io.IOException.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSource.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSourceImpl.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSourceImpl.java

## Purpose
Opens SMB connections, authenticates sessions, connects disk shares, and closes share/session/connection holders for the NIO filesystem layer.

## Important APIs / Types / Functions
Defines class `ShareSourceImpl` in package `com.hierynomus.smbfs`. Important methods/functions include `ShareSourceImpl`, `open`, `close`, `HolderImpl`, `share`. Important fields include `client`, `host`, `port`, `context`, `closed`, `share`. Source size: 82 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: client, host, port, context, closed, share. Concurrency state is explicit and lives only in process memory. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.SMBClient, com.hierynomus.smbj.auth.AuthenticationContext, com.hierynomus.smbj.connection.Connection, com.hierynomus.smbj.session.Session, com.hierynomus.smbj.share.DiskShare. JDK/JCE dependencies: java.io.IOException.

## Risks and Edge Cases
network timeouts, proxy parsing, and close behavior need integration tests.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ShareSourceImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbDirectoryStream.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbDirectoryStream.java

## Purpose
DirectoryStream implementation over a precomputed path list, enforcing one iterator and a closed state.

## Important APIs / Types / Functions
Defines class `SmbDirectoryStream` in package `com.hierynomus.smbfs`. Important methods/functions include `SmbDirectoryStream`, `iterator`, `close`. Important fields include `list`, `closed`, `iteratorTaken`. Source size: 51 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: list, closed, iteratorTaken. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
JDK/JCE dependencies: java.io.IOException, java.nio.file.DirectoryStream, java.nio.file.Path, java.util.Iterator, java.util.List.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbDirectoryStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileAttributes.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileAttributes.java

## Purpose
Adapts SMB FileAllInformation into Java BasicFileAttributes time, type, and size values.

## Important APIs / Types / Functions
Defines class `SmbFileAttributes` in package `com.hierynomus.smbfs`. Important methods/functions include `SmbFileAttributes`, `lastModifiedTime`, `lastAccessTime`, `creationTime`, `isRegularFile`, `isDirectory`, `isSymbolicLink`, `isOther`, `size`, `fileKey`. Important fields include `fileInformation`. Source size: 78 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: fileInformation. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.msfscc.fileinformation.FileAllInformation, com.hierynomus.smbfs.FileTimes.fromSmb. JDK/JCE dependencies: java.nio.file.attribute.BasicFileAttributes, java.nio.file.attribute.FileTime.

## Risks and Edge Cases
main risk is contract drift with callers because this is shared protocol infrastructure.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileAttributes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileChannel.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileChannel.java

## Purpose
SeekableByteChannel adapter over an SMBJ File with locked position tracking, read/write/truncate, and idempotent close.

## Important APIs / Types / Functions
Defines class `SmbFileChannel` in package `com.hierynomus.smbfs`. Important methods/functions include `SmbFileChannel`, `read`, `write`, `position`, `size`, `truncate`, `isOpen`, `close`. Important fields include `lock`, `holder`, `file`, `position`, `closed`. Source size: 121 lines.

## Control Flow
Control flow adapts Java NIO calls onto SMBJ objects: shares are opened from SMBClient connections, file attributes are read from FileAllInformation, streams expose list iteration, and channels guard shared position updates with a lock.

## State and Persistence
State fields observed: lock, holder, file, position, closed. Concurrency state is explicit and lives only in process memory. Network/file resources are external integration state and require close-path coverage. The file itself does not persist configuration to disk; persistence is limited to serialized protocol bytes or remote SMB side effects.

## Dependencies and Integration Points
Project dependencies: com.hierynomus.smbj.share.File. JDK/JCE dependencies: java.io.IOException, java.nio.ByteBuffer, java.nio.channels.SeekableByteChannel, java.util.concurrent.atomic.AtomicBoolean, java.util.concurrent.locks.ReentrantLock.

## Risks and Edge Cases
concurrency semantics need tests for timeout, cancellation, interruption, and double-close paths.

## Test Signals
Use mocked SMBJ DiskShare/File/Connection objects for close and position behavior plus integration tests against a disposable SMB share.

<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileChannel.java -->
