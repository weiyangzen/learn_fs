# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/package-info.java


Purpose: This package descriptor declares `org.apache.hadoop.portmap` as Hadoop's ONC RPC port mapper implementation package.

Important APIs and types: It attaches Hadoop classification annotations, marking the package `InterfaceAudience.Private` and `InterfaceStability.Evolving`. There are no executable APIs.

Control flow and state: There is no runtime control flow or mutable state. The file provides package metadata consumed by documentation and annotation-aware tooling.

Dependencies and integration: It imports Hadoop classification annotations and applies them at package scope. The package is used by Hadoop's ONC RPC/NFS-adjacent services for program-to-port registration and lookup.

Risks and test signals: The main risk is classification drift if public consumers start depending on private evolving classes. Tests are not needed for this descriptor beyond compile/package checks.
