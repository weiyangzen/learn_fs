# sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/ObsClientExt.java

## Purpose
`ObsClientExt` extends Huawei's `ObsClient` to inject additional OBS client properties after construction.

## Important APIs, Types, And Functions
The only API is the constructor accepting access key, secret key, endpoint, and a `Map<String,Object>` of OBS configuration values. It calls the parent `ObsClient` constructor and writes every map entry into the inherited `obsProperties`.

## Control Flow
Construction loops through configuration entries, stringifies non-null values, stores them in `obsProperties`, and logs each key/value at debug level.

## State And Persistence
State is persisted in the underlying client property bag for the lifetime of the OBS client. The class adds no separate fields.

## Dependencies And Integration Points
It depends on Huawei OBS SDK internals exposing `obsProperties`. It is used by the OBS UFS construction path to apply Alluxio-provided client settings that the base constructor does not take directly.

## Risks
Because it reaches into inherited mutable properties, compatibility depends on OBS SDK implementation details. Null values are passed to `setProperty` as null, which may be provider-sensitive. Debug logging can reveal configuration keys and values.

## Test Signals
No direct unit test appears in this subset. Coverage is indirect through OBS UFS construction and stream tests.
