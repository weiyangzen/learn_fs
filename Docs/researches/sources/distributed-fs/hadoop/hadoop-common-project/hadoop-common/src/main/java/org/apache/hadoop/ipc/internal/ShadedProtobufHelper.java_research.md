<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/ShadedProtobufHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/ShadedProtobufHelper.java

## Purpose
`ShadedProtobufHelper` centralizes helper code for Hadoop's shaded protobuf RPC implementation, especially exception conversion, ByteString reuse, token/proto conversion, and concise protobuf IPC calls.

## Important APIs, Types, And Functions
- `getRemoteException(ServiceException se)` returns the wrapped `IOException` cause or a new `IOException` wrapping the service exception.
- `getFixedByteString(Text)` and `getFixedByteString(String)` cache ByteStrings for fixed small string sets.
- `getByteString(byte[])` returns `ByteString.EMPTY` for empty arrays or copies non-empty arrays.
- `tokenFromProto(TokenProto)` builds a Hadoop `Token` from proto identifier/password/kind/service.
- `protoFromToken(Token<?>)` builds a `TokenProto` using cached fixed fields for kind and service.
- `ipc(IpcCall<T>)` executes a lambda and translates shaded protobuf `ServiceException` into `IOException`.
- `IpcCall<T>` is a functional interface for calls throwing `ServiceException`.

## Control Flow
The helper has only static methods. The cache methods look up by the provided key and populate `FIXED_BYTESTRING_CACHE` on miss. Text keys are copied into a new `Text` object so later mutation of the input `Text` cannot corrupt the cache key. `ipc` wraps protobuf stub calls and normalizes exception handling for translators.

## State And Persistence
The only state is a process-wide `ConcurrentHashMap<Object, ByteString>` with no expiration. Token conversions allocate new token/proto objects and do not persist data.

## Dependencies And Integration Points
Used by shaded protobuf client-side translators in Hadoop IPC. Depends on shaded `ByteString`, `ServiceException`, Hadoop `Text`, security `Token`, and `TokenProto`.

## Risks And Edge Cases
The fixed ByteString cache is intentionally unbounded; callers must restrict it to small fixed string domains. Mixed `String` and `Text` keys coexist as different key types. `getRemoteException` preserves only `IOException` causes; non-IO causes become a wrapper `IOException`.

## Test Signals
Tests should verify exception conversion with null, IO, and non-IO causes; Text mutation after caching; empty byte-array singleton behavior; token round-trips; and translator lambdas converting `ServiceException` to `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/internal/ShadedProtobufHelper.java -->
