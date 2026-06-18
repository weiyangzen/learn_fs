<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/ECTopologyVerifier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/ECTopologyVerifier.java

## Purpose

`ECTopologyVerifier` checks whether the current cluster topology can support enabled erasure-coding policies.

## Important APIs and types

Static entry points accept either a `DatanodeInfo[]` report plus policies or explicit rack/DataNode counts plus policies, returning `ECTopologyVerifierResult`. Helpers compute unique rack count, readable policy names, and minimum required DataNodes/racks.

## Control flow

For all policies, the verifier computes the maximum `dataUnits + parityUnits` as the required DataNode count. It computes rack requirement as `ceil(policyDN / parityUnits)` and takes the maximum across policies. Empty policy sets are treated as success. Verification fails first on insufficient DataNodes, then on insufficient racks, otherwise returns success with a readable policy list.

## State and persistence behavior

The class is stateless and final with a private constructor. It persists nothing.

## Dependencies and integration points

It integrates with `ErasureCodingPolicy`, `DatanodeInfo`, `ECTopologyVerifierResult`, and EC policy enablement/admin flows.

## Risks and edge cases

The rack calculation assumes rack-fault-tolerant placement expectations and may be conservative for custom policies. Rack counting trusts `DatanodeInfo.getNetworkLocation`, including null or default locations as map keys. Empty policies produce success rather than warning failure.

## Test signals

Tests should cover empty policies, multiple policies with different maxima, insufficient DataNodes, insufficient racks, duplicate rack locations, and readable error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/ECTopologyVerifier.java -->
