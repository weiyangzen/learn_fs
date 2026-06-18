# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteMethod.java

## Purpose
`RemoteMethod` describes a protocol method and parameter template for router fan-out calls to remote NameNodes. It lets callers combine static parameters with per-location dynamic parameters resolved from `RemoteLocationContext`.

## Important APIs, Types, And Functions
- Constructors support no-arg methods, `ClientProtocol` methods, and arbitrary protocol classes.
- `getMethod` resolves the reflected Java method using stored protocol, method name, and parameter types.
- `getParams(RemoteLocationContext)` converts the parameter template into actual invocation parameters for a specific location.
- `getProtocol`, `getTypes`, `getMethodName`, and `toString` expose metadata.
- Special handling rebuilds `CacheDirectiveInfo` with a destination path when the dynamic parameter type is `CacheDirectiveInfo`.

## Control Flow
The typed constructor validates that parameter count matches type count. `getMethod` uses `Class.getDeclaredMethod` and converts reflection/security failures to `IOException`. `getParams` returns an empty array for no-arg calls; otherwise it copies static values and replaces `RemoteParam` placeholders with per-context values.

## State And Persistence
`RemoteMethod` is immutable after construction except that parameter objects themselves may be mutable references. It stores no persistent state.

## Dependencies And Integration Points
It depends on Java reflection, `ClientProtocol`, `CacheDirectiveInfo`, `Path`, `RemoteParam`, and `RemoteLocationContext`. `RouterRpcClient`, `Quota`, `RouterCacheAdmin`, admin destination validation, and fairness tests use it as the common invocation description.

## Risks And Edge Cases
`getTypes` assumes `types` is non-null; callers should avoid it for no-arg methods. Reflection catches method signature mismatches only at runtime. The cache directive special case assumes destination path replacement while preserving other directive fields. Dynamic parameters return null if called without context, which can break protocol invocations unless callers only use context-free calls for static parameters.

## Test Signals
Remote method behavior is exercised indirectly by extensive router RPC tests, cache admin tests, quota tests, and fairness handler tests such as `TestRouterHandlersFairness` and `TestRouterRefreshFairnessPolicyController`. Signature regressions surface when reflected methods are invoked through `RouterRpcClient`.
