# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NodeBase.java

Purpose: base mutable implementation of `Node` that stores a node name, normalized network location, tree parent, and tree level. It also provides path utility functions used by topology code.

Important APIs/types/functions: constructors from full path or name/location, `normalize`, `getPath`, `getPathComponents`, `locationToDepth`, getters/setters, `equals`, `hashCode`, and `toString`.

Control flow: constructors call `normalize` and split paths on the last slash. `normalize` rejects null and relative locations, collapses duplicate slashes, strips a trailing slash, and maps empty input to root. Equality and hash code are path based.

State and persistence: in-memory fields `name`, `location`, `level`, and `parent`; no persistence. `name` must not contain `/`; null names become empty strings.

Dependencies and integration: used by `NetworkTopology`, `InnerNodeImpl`, block placement helpers, and tests as the canonical path formatter/normalizer.

Risks: `setNetworkLocation` does not normalize, so callers can bypass constructor invariants. `getPathComponents` uses Java `split("/")`, so leading slash creates an initial empty component; distance code depends on that behavior. Mutating location/name after insertion changes equality and hash code.

Test signals: topology tests validate normalization, path identity, and level/depth behavior through higher-level APIs.
