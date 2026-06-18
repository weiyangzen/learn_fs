# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/resources/NamenodeAddressParam.java

## Purpose

`NamenodeAddressParam.java` defines the WebHDFS string parameter for a NameNode RPC address, named `namenoderpcaddress`. The source was read as a complete 49-line file for this report.

## Important APIs, Types, and Functions

The class extends `StringParam`. Constants are `NAME = "namenoderpcaddress"` and `DEFAULT = ""`. It owns a `StringParam.Domain` with no regex constraint. Constructors accept either a raw string or a `NameNode`, and `getName()` returns the parameter name.

## Control Flow

The string constructor normalizes null and empty-string defaults to a null value; otherwise it parses the supplied string through the domain. The `NameNode` constructor stores `namenode.getTokenServiceName()`, binding the parameter to the NameNode's advertised token/RPC service. There is no further behavior beyond base `StringParam` conversion.

## State and Persistence Behavior

Instances are immutable parameter objects after construction and do not persist data. They carry a single request/query parameter value used by WebHDFS delegation and redirect flows.

## Dependencies and Integration Points

The class depends on `StringParam` and `org.apache.hadoop.hdfs.server.namenode.NameNode`. It integrates with WebHDFS resource parameter injection and token-service/Namenode address propagation for clients that need to address the correct NameNode RPC endpoint.

## Risks and Edge Cases

The domain does not validate address syntax, so malformed values are accepted until a downstream consumer attempts to use them. Empty string becomes null, which must remain consistent with URL generation and request parsing. The `NameNode` constructor assumes a non-null NameNode with a usable token service name.

## Test Signals

Tests should cover null, empty, and non-empty values; generated parameters from a mock or test NameNode; and WebHDFS URL/query round-trips that include HA or non-default RPC addresses.
