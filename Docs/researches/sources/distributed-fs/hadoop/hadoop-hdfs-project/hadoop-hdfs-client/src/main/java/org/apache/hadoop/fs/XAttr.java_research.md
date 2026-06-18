# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/XAttr.java

Purpose: private model of a POSIX-style extended attribute with namespace, name, and optional byte-array value.

Important APIs and types: `NameSpace` enum defines `USER`, `TRUSTED`, `SECURITY`, `SYSTEM`, and `RAW`. `Builder` sets namespace, name, and value, then builds an immutable `XAttr` reference object. Getters expose the fields; `equals()`, `hashCode()`, `equalsIgnoreValue()`, and `toString()` support comparison and diagnostics.

Control flow and state: builder defaults namespace to `USER`. Constructed fields are final, but the byte-array `value` is stored and returned directly.

Dependencies and integration: used by HDFS xattr APIs and protocol conversion code. FindBugs suppression explicitly accepts representation exposure for `XAttr` and `XAttr.Builder`.

Risks and test signals: mutability of the exposed byte array means `XAttr` is not deeply immutable. Equality includes byte-array content; `equalsIgnoreValue()` allows namespace/name matching for operations that do not care about current value.
