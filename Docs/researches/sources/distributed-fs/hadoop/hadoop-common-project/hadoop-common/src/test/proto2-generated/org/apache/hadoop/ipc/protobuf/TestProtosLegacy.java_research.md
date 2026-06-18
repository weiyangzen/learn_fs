# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestProtosLegacy.java

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007410`: lines 1-7102, `Docs/researches/chunks/subset-b-007410_research.md`
- `subset-b-007411`: lines 7103-9894, `Docs/researches/chunks/subset-b-007411_research.md`

## Chunk Research

### subset-b-007410: lines 1-7102

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestProtosLegacy.java lines 1-7102

## Purpose

This chunk is the beginning and bulk of the generated Java binding for `src/test/proto/test_legacy.proto`, with outer class `org.apache.hadoop.ipc.protobuf.TestProtosLegacy`. It is test-only protobuf infrastructure for Hadoop IPC/RPC compatibility tests that need legacy proto2 generated message classes alongside the newer generated test protos.

The range covers generated message APIs for empty calls, echo calls, optional echo calls, sleep/slow-ping calls, arithmetic calls, and the request side of an exchange call. It also begins `ExchangeResponseProto`, but the chunk stops inside that class's parsing constructor before the full class, builders, descriptors, and file descriptor initialization are visible.

## Important APIs, Types, and Functions

- `TestProtosLegacy` is a final utility-style outer class with a private constructor and a no-op `registerAllExtensions(ExtensionRegistry)`. The source proto defines no extensions, so extension registration is intentionally empty.
- Every message has a paired `*OrBuilder` interface extending `com.google.protobuf.MessageOrBuilder`. These interfaces expose field presence and accessors for typed user code and generated service stubs.
- `EmptyRequestProto` and `EmptyResponseProto` have no declared fields. Their instances still preserve unknown fields, expose parse/build/default-instance methods, implement equality/hash using descriptors plus unknown fields, and serialize unknown fields.
- `EchoRequestProto` and `EchoResponseProto` each carry `required string message = 1`. They expose `hasMessage()`, `getMessage()`, `getMessageBytes()`, builder setters/clearers, required-field initialization checks, and UTF-8 lazy conversion between `String` and `ByteString`.
- `OptRequestProto` and `OptResponseProto` each carry `optional string message = 1`. They use the same string storage and bitfield presence pattern as the required echo messages, but `isInitialized()` always succeeds because the field is optional.
- `SleepRequestProto` carries `required int32 milliSeconds = 1`; `SleepResponseProto` is empty. The request builder requires `setMilliSeconds()` before `build()`, while the response behaves like the other empty messages.
- `SlowPingRequestProto` carries `required bool shouldSlow = 1`, using protobuf bool wire tag `8`, `hasShouldSlow()`, `getShouldSlow()`, and builder `setShouldSlow()` / `clearShouldSlow()`.
- `EchoRequestProto2` and `EchoResponseProto2` each carry `repeated string message = 1`. They store values in `LazyStringList`, expose list/count/index/bytes accessors, and builders provide `setMessage`, `addMessage`, `addAllMessage`, `clearMessage`, and `addMessageBytes`.
- `AddRequestProto` carries two required integers, `param1 = 1` and `param2 = 2`. Both fields must be present for `build()` to succeed. The builder tracks them with separate `bitField0_` bits.
- `AddRequestProto2` carries `repeated int32 params = 1`. The parser accepts both unpacked tag `8` values and packed tag `10` length-delimited values, while `writeTo()` emits each value as unpacked `int32`.
- `AddResponseProto` carries `required int32 result = 1` and has the same required-field builder and initialization behavior as the scalar request types.
- `ExchangeRequestProto` carries `repeated int32 values = 1`, with the same repeated-int parsing, builder mutability, equality, hash, and serialization model as `AddRequestProto2`.
- `ExchangeResponseProtoOrBuilder` and the start of `ExchangeResponseProto` appear at the chunk tail. The visible portion shows it has `repeated int32 values = 1`, default-instance/unknown-field plumbing, and the beginning of parsing for unpacked values.
- Each complete message in this range exposes `PARSER`, `parseFrom(...)`, `parseDelimitedFrom(...)`, `newBuilder()`, `toBuilder()`, `build()`, `buildPartial()`, `mergeFrom(...)`, `getDescriptor()`, and `internalGetFieldAccessorTable()`.

## Control Flow and Execution Model

Generated parsing constructors follow the same pattern: initialize default fields, allocate an `UnknownFieldSet.Builder`, repeatedly call `input.readTag()`, switch on known field tags, and delegate unrecognized tags to `parseUnknownField(...)`. Tag `0` exits the loop. `InvalidProtocolBufferException` is rethrown after attaching the unfinished message; `IOException` is wrapped in `InvalidProtocolBufferException`; `finally` freezes unknown fields and calls `makeExtensionsImmutable()`.

Scalar required/optional fields use `bitField0_` to track presence. For string fields, parsing stores raw `ByteString` and accessors lazily convert to `String`, caching the converted value only when the bytes are valid UTF-8. Integer and boolean fields are stored directly as primitives.

Repeated string parsing lazily replaces the default empty `LazyStringArrayList` with a mutable list on first field encounter, then wraps it in `UnmodifiableLazyStringList` at the end of parsing. Repeated integer parsing lazily replaces `Collections.emptyList()` with an `ArrayList`, accepts both unpacked and packed encodings, and wraps the list in `Collections.unmodifiableList()` after parsing.

Builders mirror that state machine. Mutable repeated fields are guarded by `ensureMessageIsMutable()`, `ensureParamsIsMutable()`, or `ensureValuesIsMutable()`. `buildPartial()` transfers builder field values to a message and freezes repeated lists when needed. `build()` additionally checks `isInitialized()` and throws the protobuf uninitialized-message exception when required fields are absent.

Serialization is deterministic for this generated code path: `writeTo()` emits present scalar fields in field-number order, iterates repeated fields, then writes unknown fields. `getSerializedSize()` computes and memoizes sizes, including unknown fields. Equality and hash code include declared present fields/lists plus unknown fields.

## State and Persistence Behavior

Message instances are immutable after construction except for internal memoization fields such as `memoizedIsInitialized`, `memoizedSerializedSize`, and `memoizedHashCode`. Builders are mutable and use bitfields to track presence and repeated-list mutability. Static `defaultInstance` objects are initialized per class and returned by `getDefaultInstance()` and builder `getDefaultInstanceForType()`.

There is no filesystem, network, or external persistence in this generated class. Persistence is protobuf wire serialization through `writeTo()`, `parseFrom(...)`, and delimited stream helpers. Unknown fields are intentionally preserved across parse/merge/serialize cycles, which matters for compatibility tests involving legacy or forward-compatible RPC messages.

The generated class also supports Java object serialization via `writeReplace()` inherited from `GeneratedMessage`, but the actual durable contract is the protobuf binary encoding. Repeated collections returned by built messages are immutable; builder list accessors return unmodifiable views while mutation goes through builder methods.

## Dependencies and Integration Points

This code depends on the legacy `com.google.protobuf` Java runtime APIs: `GeneratedMessage`, `MessageOrBuilder`, `Parser`, `AbstractParser`, `CodedInputStream`, `CodedOutputStream`, `ByteString`, `UnknownFieldSet`, `Descriptors`, `ExtensionRegistryLite`, `LazyStringArrayList`, `LazyStringList`, and `UnmodifiableLazyStringList`.

The schema source is `hadoop-common/src/test/proto/test_legacy.proto`, which sets `java_package = "org.apache.hadoop.ipc.protobuf"` and `java_outer_classname = "TestProtosLegacy"`. The Maven configuration includes `src/test/proto2-generated` as a test source root and excludes `TestProtosLegacy.java` from at least one source-checking path, consistent with it being checked-in generated code.

The main test integration is Hadoop IPC protobuf RPC testing. `TestProtoBufRpc` imports `TestProtosLegacy` directly and uses visible messages from this chunk for legacy RPC methods: `EmptyRequestProto`/`EmptyResponseProto`, `EchoRequestProto`/`EchoResponseProto`, and `SleepRequestProto`/`SleepResponseProto`. `TestRpcServiceProtosLegacy.java`, another generated test service binding, references these message defaults and types to build service descriptors, client stubs, and method dispatch.

The non-legacy `TestProtos` generated classes share similar message names and are used more broadly by `TestRPC`, `TestRpcBase`, and other IPC tests. This class exists to keep legacy proto2 output available without replacing the newer generated classes.

## Risks and Edge Cases

- This is generated code marked `DO NOT EDIT`. Manual edits risk diverging from `test_legacy.proto` and from the protobuf compiler/runtime version expected by the test build.
- Required proto2 fields are enforced only by `isInitialized()` / `build()`. `buildPartial()` can create incomplete messages, and parsers can return unfinished messages on exceptions. Tests that use partial messages can bypass normal required-field validation.
- Required string fields default to `""` internally but are not considered present until their bit is set. Code must use `hasMessage()` when absence and empty string differ.
- Optional string fields also default to `""`; `hasMessage()` is required to distinguish omitted values from an explicitly set empty value.
- Repeated integer parsers accept packed encodings even though `writeTo()` emits unpacked values. Compatibility tests should account for both wire forms when reading but should expect this generated class to write the unpacked proto2 form.
- String getters lazily cache UTF-8 conversion. Invalid UTF-8 bytes can still be accessed through `getMessageBytes()`; `getMessage()` returns a UTF-8 conversion but only caches it when `ByteString.isValidUtf8()` is true.
- Unknown fields participate in equality and hash code. Two messages with identical declared fields but different unknown fields compare unequal, which can surprise tests that only reason about declared schema fields.
- The chunk boundary cuts off `ExchangeResponseProto` mid-class. Research and merge reconciliation should combine this with the next chunk before drawing conclusions about the full response type, descriptor table, or file-level static initialization.

## Test Signals

Useful validation signals are the IPC tests that instantiate and send these messages through Hadoop's protobuf RPC stack, especially `TestProtoBufRpc` legacy service methods and generated `TestRpcServiceProtosLegacy` stubs. These exercise empty messages, required strings, required integer sleep values, and protobuf service dispatch using the legacy generated classes.

Focused protobuf-level checks for this chunk would cover:

- Empty request/response round trips preserving unknown fields.
- Required-field failures for `EchoRequestProto`, `EchoResponseProto`, `SleepRequestProto`, `SlowPingRequestProto`, `AddRequestProto`, and `AddResponseProto` when builders omit required fields.
- Optional string presence behavior for omitted, empty, and non-empty `OptRequestProto` / `OptResponseProto`.
- Repeated string list immutability after `build()` and builder mutability through add/set/clear methods.
- Repeated integer parsing from both unpacked and packed encodings for `AddRequestProto2` and `ExchangeRequestProto`.
- Equality/hash behavior when unknown fields differ.

## Chunk Boundary Notes

Lines 1-7102 include complete generated definitions through `ExchangeRequestProto` and only the beginning of `ExchangeResponseProto`. The file continues with the remainder of `ExchangeResponseProto`, auth/user/sleep2 messages, and the static descriptor/file-descriptor initialization. Those later pieces should be covered by their own chunk reports and merged later into the per-file research document.

### subset-b-007411: lines 7103-9894

# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto2-generated/org/apache/hadoop/ipc/protobuf/TestProtosLegacy.java lines 7103-9894

## Purpose

This chunk is the tail of the generated `TestProtosLegacy` Java class for `test_legacy.proto`. It belongs to Hadoop IPC test fixtures, not production filesystem code. The range completes `ExchangeResponseProto`, defines `AuthMethodResponseProto`, `UserResponseProto`, `SleepRequestProto2`, and `SleepResponseProto2`, then wires the static protobuf descriptors and field accessor tables for every message in the file.

The code is generated by the proto2 Java compiler against the older `com.google.protobuf.GeneratedMessage` API. Its practical purpose is to provide stable, legacy protobuf message classes used by Hadoop RPC protocol tests, especially tests that validate required-field behavior, repeated-field wire compatibility, SASL/auth metadata responses, user identity responses, and protocol evolution from the original sleep request/response messages to optional int64 timing fields.

## Important APIs, Types, and Functions

- `ExchangeResponseProto` is a generated message for `hadoop.common.ExchangeResponseProto` with one repeated `int32 values = 1` field. This chunk starts inside its parsing constructor, covering both unpacked tag `8` and packed tag `10` decoding, conversion to an unmodifiable list, descriptor lookup, parser singleton, public repeated-field readers, serialization, equality/hash behavior, parse helpers, and its nested `Builder`.
- `ExchangeResponseProto.Builder` exposes `getValuesList()`, `getValuesCount()`, `getValues(int)`, `setValues(int,int)`, `addValues(int)`, `addAllValues(Iterable<Integer>)`, and `clearValues()`. It uses `bitField0_` as a mutability marker and `ensureValuesIsMutable()` to copy the list before edits.
- `AuthMethodResponseProtoOrBuilder` and `AuthMethodResponseProto` model `required int32 code = 1` and `required string mechanismName = 2`. The public API includes `hasCode()`, `getCode()`, `hasMechanismName()`, `getMechanismName()`, and `getMechanismNameBytes()`.
- `AuthMethodResponseProto.Builder` enforces proto2 required-field initialization through `isInitialized()`, `build()`, and `newUninitializedMessageException(result)`. It provides `setCode()`, `clearCode()`, `setMechanismName(String)`, `clearMechanismName()`, and `setMechanismNameBytes(ByteString)`.
- `UserResponseProtoOrBuilder` and `UserResponseProto` model `required string user = 1`. They expose `hasUser()`, `getUser()`, and `getUserBytes()`, with the same lazy `String`/`ByteString` storage pattern as `AuthMethodResponseProto`.
- `UserResponseProto.Builder` provides `setUser(String)`, `clearUser()`, and `setUserBytes(ByteString)`, and treats missing `user` as uninitialized.
- `SleepRequestProto2OrBuilder` and `SleepRequestProto2` model `optional int64 sleep_time = 1`. They expose `hasSleepTime()` and `getSleepTime()`, and the builder exposes `setSleepTime(long)` and `clearSleepTime()`.
- `SleepResponseProto2OrBuilder` and `SleepResponseProto2` model `optional int64 receive_time = 1` and `optional int64 response_time = 2`. They expose `hasReceiveTime()`, `getReceiveTime()`, `hasResponseTime()`, and `getResponseTime()`, with builder setters and clearers for both fields.
- Every message in this range has a static `PARSER` implemented with `AbstractParser<T>`, parse overloads for `ByteString`, `byte[]`, `InputStream`, delimited `InputStream`, and `CodedInputStream`, plus overloads accepting `ExtensionRegistryLite`.
- Every message tracks `UnknownFieldSet unknownFields`, memoizes `isInitialized()` as a byte, memoizes serialized size, memoizes hash code, implements `writeTo(CodedOutputStream)`, and participates in Java serialization through `writeReplace()`.
- The final descriptor block declares `internal_static_hadoop_common_*_descriptor` and `internal_static_hadoop_common_*_fieldAccessorTable` members for all 20 generated message types in `test_legacy.proto`.
- The static initializer embeds the serialized file descriptor data for `test_legacy.proto`, calls `Descriptors.FileDescriptor.internalBuildGeneratedFileFrom(...)`, and assigns descriptor/message indices and field accessor names through `InternalDescriptorAssigner`.

## Control Flow

Parsing follows the standard generated proto2 loop. Each private message constructor initializes default fields, creates an `UnknownFieldSet.Builder`, then repeatedly calls `input.readTag()`. Known wire tags set bits in `bitField0_` and read values from the `CodedInputStream`; unknown tags are delegated to `parseUnknownField(...)`. Tag `0` or an unknown field that cannot be parsed terminates the loop. `InvalidProtocolBufferException` is rethrown with `setUnfinishedMessage(this)`, `IOException` is wrapped as `InvalidProtocolBufferException`, and `finally` stores unknown fields and calls `makeExtensionsImmutable()`.

`ExchangeResponseProto` has the most interesting parser path in this chunk. For tag `8`, it reads one unpacked `int32` value. For tag `10`, it reads a length-delimited packed repeated field, pushes a limit, reads `int32` values until `getBytesUntilLimit() == 0`, then pops the limit. If the list was mutated during parsing, it is frozen with `Collections.unmodifiableList(...)` before construction completes.

Building follows generated-message copy semantics. `newBuilder()` creates a nested `Builder`; callers set fields; `buildPartial()` creates the immutable message and copies the builder's bit field state; `build()` calls `isInitialized()` and throws when required fields are absent. Required messages in this chunk are `AuthMethodResponseProto` and `UserResponseProto`; optional/repeated messages always return initialized.

Serialization is field-presence driven. Required and optional scalar fields are written only when their corresponding `bitField0_` bit is set. `ExchangeResponseProto.writeTo()` writes each repeated `values_` element as an unpacked `int32`, even though the parser accepts both packed and unpacked encodings. Size computation mirrors this, adding per-element tag overhead for `values_` and using `computeInt64Size`, `computeInt32Size`, or `computeBytesSize` for scalar/string fields.

The descriptor initializer runs when `TestProtosLegacy` is loaded. It builds a `FileDescriptor` from the embedded `descriptorData`, then maps message indexes to generated descriptors in schema order: empty request/response, echo/opt/sleep/slow-ping messages, `Add*`, `Exchange*`, `AuthMethodResponseProto`, `UserResponseProto`, and the `Sleep*Proto2` messages. Field accessor tables are created with Java property names such as `Values`, `Code`, `MechanismName`, `User`, `SleepTime`, `ReceiveTime`, and `ResponseTime`.

## State and Persistence Behavior

All state here is in-memory protobuf message state. Message instances are immutable after construction except for lazy caching of string/byte representations, memoized initialization result, memoized serialized size, and memoized hash code. Builders are mutable and use `bitField0_` to track both field presence and, for repeated fields, whether a list has been copied to a mutable `ArrayList`.

The proto2 presence model is preserved. `AuthMethodResponseProto` defaults `code_` to `0` and `mechanismName_` to the empty string, but those defaults do not satisfy initialization unless the `has*` bits are set. `UserResponseProto` behaves the same for `user_`. `SleepRequestProto2` and `SleepResponseProto2` default int64 values to `0L`, but absent and explicitly-set-zero are distinguishable through `hasSleepTime()`, `hasReceiveTime()`, and `hasResponseTime()`.

String fields use `Object` slots that hold either a `String` or `ByteString`. `get*()` decodes from bytes with UTF-8 and may cache a `String` when the bytes are valid UTF-8. `get*Bytes()` converts a `String` to `ByteString` and stores it back. Builder `set*Bytes(...)` does not perform an explicit UTF-8 validity check in this generated vintage, so invalid byte payloads can be represented and later decoded through `toStringUtf8()`.

Unknown fields are preserved in `UnknownFieldSet`, included in serialization, equality, hash code, and merges. This matters for Hadoop compatibility tests because messages can round-trip fields from a newer schema even when this generated class does not understand them.

No filesystem or external persistence is performed by this chunk. Persistent behavior is indirect: these generated classes define the wire format emitted to Hadoop IPC test streams and the descriptor metadata used by protobuf reflection.

## Dependencies and Integration Points

The code depends on the protobuf Java runtime classes under `com.google.protobuf`: `GeneratedMessage`, `MessageOrBuilder`, `Parser`, `AbstractParser`, `CodedInputStream`, `CodedOutputStream`, `ByteString`, `UnknownFieldSet`, `InvalidProtocolBufferException`, `Descriptors`, `ExtensionRegistry`, and `ExtensionRegistryLite`. It also uses JDK collection and stream types such as `List`, `ArrayList`, `Collections`, `InputStream`, `IOException`, and `ObjectStreamException`.

Within Hadoop, this generated source lives under `hadoop-common/src/test/proto2-generated`, so consumers are test classes and generated RPC service stubs that import `org.apache.hadoop.ipc.protobuf.TestProtosLegacy`. The messages align with `hadoop.common` test protocol schemas used by IPC compatibility and RPC behavior tests. Relevant integration surfaces include:

- Exchange RPC tests, which can return a sequence of integer values through `ExchangeResponseProto`.
- Authentication-method tests, which can return an integer method code plus a SASL mechanism name through `AuthMethodResponseProto`.
- User identity tests, which can return the current or effective user through `UserResponseProto`.
- Sleep/timing tests, which can use `SleepRequestProto2` and `SleepResponseProto2` optional int64 fields to represent requested sleep duration and observed receive/response timestamps.
- Reflection or dynamic-message code that calls `TestProtosLegacy.getDescriptor()` and expects descriptor indexes and field accessor names to match `test_legacy.proto`.

The descriptor block integrates all message classes in the file, not just the classes whose bodies are in this range. The merge lane should therefore combine this research with earlier chunks for full coverage of `Empty*`, `Echo*`, `Opt*`, `SleepRequestProto`, `SleepResponseProto`, `SlowPingRequestProto`, `Add*`, and `ExchangeRequestProto`.

## Risks and Edge Cases

- This is generated code and should not be hand-edited. Behavioral changes should come from `test_legacy.proto` and the matching protoc/runtime version; manual edits risk desynchronizing class bodies, descriptors, and field accessor tables.
- The chunk begins in the middle of `ExchangeResponseProto`'s parsing constructor. The class/interface declaration and the first part of the constructor are outside this work item, so the merge stage needs the previous chunk for a complete class narrative.
- `ExchangeResponseProto` accepts packed and unpacked repeated int32 encodings while writing unpacked values. Tests relying on exact byte-for-byte packed output would fail, but parser compatibility is broader than serializer output.
- Required fields in `AuthMethodResponseProto` and `UserResponseProto` are a compatibility-sensitive proto2 behavior. `buildPartial()` can create incomplete messages, but `build()` and parser `parseFrom(...)` paths enforce initialization; tests must choose the correct construction path when intentionally testing malformed inputs.
- String fields can carry `ByteString` values. The generated `get*()` methods decode with `toStringUtf8()`, and the setters reject only null values. Inputs with invalid UTF-8 may not fail at builder time, which can matter in negative wire-format tests.
- `bitField0_` has different meanings depending on context: field presence for scalar/string messages and list mutability for repeated-field builders. A careless generated-code patch could break presence checks or accidentally expose mutable lists.
- `UnknownFieldSet` participates in equality and hash code. Two messages with identical known fields but different unknown fields are not equal, which can surprise tests that compare only visible schema values.
- The descriptor initializer relies on exact message ordering in `descriptorData`. Adding, removing, or reordering schema messages without regenerating the whole file would bind accessors to the wrong descriptors.
- `PARSER` fields are public mutable static fields in this old generated style, not `final`. Test code could technically replace them and corrupt parsing behavior process-wide.
- Memoized fields are not synchronized. This is normal for protobuf generated messages, but it assumes benign races for immutable message objects rather than externally synchronized cache writes.

## Test Signals

Useful validation should target the generated behavior through Hadoop IPC tests and small protobuf round-trip tests rather than editing this file directly:

- Build `AuthMethodResponseProto` with both required fields, serialize/parse it, and assert `hasCode()`, `getCode()`, `hasMechanismName()`, and `getMechanismName()` survive round-trip.
- Attempt `AuthMethodResponseProto.newBuilder().setCode(...).build()` and `UserResponseProto.newBuilder().build()` and assert they throw uninitialized-message exceptions.
- Use `buildPartial()` for incomplete required messages and assert `isInitialized()` returns false.
- Parse `ExchangeResponseProto` from both unpacked repeated int32 bytes and packed repeated int32 bytes, then assert the same `getValuesList()` content.
- Verify `ExchangeResponseProto.writeTo()` emits all repeated values and that `getSerializedSize()` is stable across repeated calls.
- Build `SleepRequestProto2` and `SleepResponseProto2` with no fields, explicit zero fields, and nonzero fields; assert the `has*()` predicates distinguish absent from set-zero.
- Add unknown fields through a newer/dynamic message or raw wire payload, parse with these legacy classes, reserialize, and assert unknown fields are preserved.
- Reflect through `TestProtosLegacy.getDescriptor()` and assert message indexes and field names for `ExchangeResponseProto`, `AuthMethodResponseProto`, `UserResponseProto`, `SleepRequestProto2`, and `SleepResponseProto2`.
- Exercise merge behavior: merging messages with unknown fields should preserve them, merging repeated `values` should append when the builder already has values, and merging optional scalar fields should set presence only when the source has presence.

## Chunk Boundary Notes

Lines 7103-9894 cover the generated tail of `TestProtosLegacy.java`. The first visible line is inside `ExchangeResponseProto`'s constructor, while the file closes at the outer class insertion point after descriptor initialization. The final per-file report should join this with earlier chunks for the complete generated schema surface and with the original `test_legacy.proto` if the reconciliation lane needs canonical schema intent.
