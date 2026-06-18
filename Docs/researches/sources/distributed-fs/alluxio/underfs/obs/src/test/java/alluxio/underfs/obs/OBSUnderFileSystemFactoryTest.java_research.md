# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSUnderFileSystemFactoryTest.java

## Purpose
This is a registry smoke test for the OBS UFS module.

## Important APIs, Types, And Functions
The single `factory` test calls `UnderFileSystemFactoryRegistry.find("obs://bucket/key", Configuration.global())` and asserts a non-null factory.

## Control Flow
The test relies on service loader metadata for the module being present on the test classpath. It does not instantiate a UFS or exercise credentials.

## State And Persistence
No persistent state is used. The registry and global configuration are read only.

## Dependencies And Integration Points
It exercises Alluxio's UFS factory registry integration and the OBS module service-provider packaging.

## Risks
This catches packaging/registration regressions but not creation behavior, credential validation, or path rejection.

## Test Signals
Passing means the OBS module can advertise support for `obs://` URIs when included in the runtime.
