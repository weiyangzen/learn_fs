# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestClusterTopology.java

## Purpose
Tests core `NetworkTopology` behavior: available-node counts with exclusions/scopes, random selection distribution, excluded-scope selection, path normalization, and topology-distance weights.

## Important APIs, Types, And Functions
Defines `NodeElement implements Node`. Uses `NetworkTopology.getInstance()`, `add()`, `remove()`, `countNumOfAvailableNodes()`, `chooseRandom()`, `NodeBase.normalize()`, `getWeight()`, and `getWeightUsingNetworkLocation()`.

## Control Flow
Tests build small synthetic topologies with rack paths, add nodes, and query counts or random choices. Random distribution is checked with a chi-square test across three runs. Excluded tests select from a scope while excluding subscopes or nodes. Weight tests compare same node, same rack, different rack, and different pod levels.

## State And Persistence Behavior
Each test creates a new topology instance from configuration. Nodes hold mutable parent/location/level assigned by topology insertion.

## Dependencies And Integration Points
Depends on Hadoop network topology classes, Apache Commons Math `ChiSquareTest`, and tuple helpers.

## Risks
Random distribution tests can be probabilistic; the test tolerates up to two rejected chi-square runs out of three. Assertions accidentally use `assertSame("node3", node.getName())`, relying on string interning rather than value equality.

## Test Signals
Signals include correct available counts under root/rack/negative scopes, random coverage of all eligible nodes, null when exclusions remove all candidates, normalization of trailing slashes, and expected weights 0/2/4/6 by topology distance.
