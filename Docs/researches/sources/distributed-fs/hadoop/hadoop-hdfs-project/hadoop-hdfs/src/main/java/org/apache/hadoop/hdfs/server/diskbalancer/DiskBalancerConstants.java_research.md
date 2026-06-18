# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/DiskBalancerConstants.java

## Purpose

`DiskBalancerConstants` holds shared constants for HDFS disk balancer plan handling and per-volume settings.

## Important APIs, Control Flow, and State

The class defines `DISKBALANCER_BANDWIDTH`, `DISKBALANCER_VOLUME_NAME`, `DISKBALANCER_MIN_VERSION`, and `DISKBALANCER_MAX_VERSION`. The private constructor prevents instantiation. There is no runtime control flow or mutable state.

The version constants define the accepted plan-file version range, currently only version 1. The string constants are used as stable keys for disk-balancer attributes/configuration.

## Dependencies, Integration, Risks, and Tests

Dependencies are only Hadoop classification annotations. Integration points are disk balancer planning, command, and DataNode RPC validation code that relies on version and key names.

Risks include version constants drifting from parser/RPC support and string-key changes breaking compatibility. Tests should cover plan-version validation and any code that reads/writes these key names.
