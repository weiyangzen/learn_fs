# sources/distributed-fs/alluxio/underfs/obs/src/main/java/alluxio/underfs/obs/OBSUnderFileSystemFactory.java

## Purpose
`OBSUnderFileSystemFactory` is the service-provider factory that lets Alluxio create Huawei OBS under file systems for `obs://` URIs.

## Important APIs, Types, And Functions
The class implements `UnderFileSystemFactory`. `create(String, UnderFileSystemConfiguration)` validates the path, checks required OBS credential properties, and delegates to `OBSUnderFileSystem.createInstance`. `supportsPath(String)` accepts only paths with `Constants.HEADER_OBS`. `checkOBSCredentials` requires `OBS_ACCESS_KEY`, `OBS_SECRET_KEY`, `OBS_ENDPOINT`, and `OBS_BUCKET_TYPE`.

## Control Flow
Creation is fail-fast: null paths are rejected, missing credentials produce an `IOException` wrapped through Guava `Throwables.propagate`, and factory construction errors from the concrete UFS are propagated the same way.

## State And Persistence
The factory has no mutable state. It only reads the supplied configuration and returns a new UFS instance.

## Dependencies And Integration Points
It integrates with Alluxio's UFS registry through the factory interface and depends on `AlluxioURI`, `PropertyKey`, and `OBSUnderFileSystem`.

## Risks
The credential check is stricter than simple path support, so registry discovery can succeed while actual creation fails. Exception wrapping uses older Guava propagation style, which can obscure checked failure types.

## Test Signals
`OBSUnderFileSystemFactoryTest` verifies registry discovery for `obs://` paths. Credential-negative and creation-error cases are not directly covered in this subset.
