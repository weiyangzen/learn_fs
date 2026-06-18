# sources/distributed-fs/alluxio/underfs/ozone/src/main/java/alluxio/underfs/ozone/OzoneUnderFileSystem.java

## Purpose
`OzoneUnderFileSystem` adapts Apache Ozone through Alluxio's HDFS UFS implementation.

## Important APIs, Types, And Functions
It extends `HdfsUnderFileSystem`. `createInstance` builds Hadoop configuration with inherited `createConfiguration` and constructs the Ozone subclass. The constructor passes URI, Alluxio UFS conf, and Hadoop conf to the parent. `getUnderFSType` returns `ozone`.

## Control Flow
All filesystem operations are inherited from HDFS UFS. This class only supplies construction and type identity.

## State And Persistence
Runtime state is inherited from `HdfsUnderFileSystem`, including Hadoop filesystem handles and configuration. This subclass adds no fields.

## Dependencies And Integration Points
It depends on Ozone Hadoop filesystem wiring being available through the module POM and on HDFS UFS behavior for actual operations.

## Risks
Most correctness risk lies in URI support and Hadoop/Ozone configuration compatibility rather than local code. Because operations are inherited, Ozone-specific edge cases may not have specialized handling.

## Test Signals
No direct test is listed in this subset. Build and factory behavior are the primary signals.
