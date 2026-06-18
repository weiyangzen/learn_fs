# sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystemFactory.java

## Purpose
This factory exposes Apache Ozone as an Alluxio UFS while reusing HDFS factory behavior.

## Important APIs, Types, And Functions
It extends `HdfsUnderFileSystemFactory`. `create` delegates to `OzoneUnderFileSystem.createInstance`, `supportsPath(String)` accepts `o3fs://`, `ofs://`, and `o3fs:` paths, `supportsPath(String, UnderFileSystemConfiguration)` adds availability checks through `UnderFileSystemUtils.isHdfsUnderFSSupported`, and `getVersion` returns `OzoneUfsConstants.UFS_OZONE_VERSION`.

## Control Flow
Path support first checks scheme/prefix. Configuration-aware support then ensures the Hadoop/Ozone filesystem can be loaded for that path.

## State And Persistence
The factory has no mutable state.

## Dependencies And Integration Points
It integrates with Alluxio UFS registry, HDFS UFS factory logic, generated Ozone constants, and Ozone Hadoop filesystem classes.

## Risks
Scheme support is broader than simple URI prefixes and includes `o3fs:`. Runtime support can differ from path support if dependencies or Hadoop profiles are missing.

## Test Signals
No direct test is present in this subset. Build-time dependency/profile validation and generic UFS registry tests elsewhere would be expected signals.
