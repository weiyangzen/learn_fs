## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/DirectoryListingStartAfterNotFoundException.java

Purpose: `DirectoryListingStartAfterNotFoundException` is an HDFS-limited stable exception thrown when a paged directory listing cannot find the requested `startAfter` marker.

Important APIs and types: it extends `IOException`, declares `serialVersionUID = 1L`, and provides default and message constructors.

Control flow, state, and persistence: the class has no custom control flow or mutable state. Its serialized form follows normal `IOException` behavior plus the declared serial id.

Dependencies and integration: directory listing implementations can throw this to distinguish missing pagination anchors from generic listing failures. Callers can catch it separately to retry from a different marker, surface a precise error, or handle object-store consistency behaviors.

Risks and test signals: risk is low but compatibility matters because exception type is part of HDFS listing contracts. Tests should assert constructors, message preservation, catchability as `IOException`, and correct use in listing paths where `startAfter` is absent.
