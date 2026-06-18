# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/HAZKInfo.proto

## Purpose

`HAZKInfo.proto` defines the protobuf payload stored or exchanged for NameNode high-availability ZooKeeper failover metadata. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java package `org.apache.hadoop.hdfs.server.namenode.ha.proto`, and outer class `HAZKInfoProtos`. It defines one message, `ActiveNodeInfo`, with required `nameserviceId`, `namenodeId`, `hostname`, `port`, and `zkfcPort`.

## Control Flow

There is no service or executable flow. HA failover code serializes `ActiveNodeInfo` when advertising the active NameNode and deserializes it when fencing, monitoring, or resolving the active node.

## State and Persistence Behavior

This schema represents HA coordination state, commonly backed by ZooKeeper znodes. All fields are required, so missing identity or address data makes the payload invalid to proto2 readers.

## Dependencies and Integration Points

It integrates with HDFS HA, ZooKeeper Failover Controller, and NameNode service discovery/fencing. Generated Java lives under the NameNode HA package rather than the general HDFS protocol package.

## Risks and Edge Cases

Changing field numbers, required fields, or package/outer class names risks breaking persistent ZooKeeper data and rolling upgrades. Hostname/port correctness is critical for fencing the right process. Multi-nameservice clusters depend on both nameservice and namenode IDs being preserved.

## Test Signals

Tests should cover serialization/deserialization of active node records, HA failover with multiple nameservices, stale znode handling, and compatibility with existing persisted active-node data.
