# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/StoreImplementationUtils.java

## Purpose
Utilities for stream capability probing in filesystem store implementations.

## Important APIs, Types, and Functions
isProbeForSyncable(), hasCapability(OutputStream,String), hasCapability(InputStream,String), package-private objectHasCapability().

## Control Flow
isProbeForSyncable compares against HSYNC/HFLUSH ignoring case. hasCapability delegates only if the object implements StreamCapabilities.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Used by FSData streams and store code to answer hsync/hflush and other capability probes.

## Risks and Test Signals
Risks are null capability handling and case behavior. Tests should cover StreamCapabilities and plain streams, hsync/hflush probes, and unsupported capabilities.
