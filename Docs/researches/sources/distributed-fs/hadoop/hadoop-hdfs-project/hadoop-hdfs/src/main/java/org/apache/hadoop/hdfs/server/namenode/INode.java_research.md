# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INode.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INode.java

Purpose: `INode` is the abstract base for the NameNode namespace tree. It models common file, directory, symlink, and reference behavior: identity, parent linkage, snapshot-aware metadata, path construction, type casting, subtree cleanup, content summary, quota accounting, block reclamation bookkeeping, and visitor dispatch.

Important APIs and types: abstract metadata APIs include id, permission status, user/group/mode setters, ACL/XAttr feature access, modification/access time, storage policy, `recordModification`, `cleanSubtree`, `destroyAndCollectBlocks`, `computeContentSummary`, and `computeQuotaUsage`. Type predicates/casts cover file, directory, symlink, and reference. Static path helpers validate and split absolute paths. Nested `QuotaDelta`, `ReclaimContext`, and `BlocksMapUpdateInfo` carry quota deltas, deletion context, blocks to delete, replication updates, removed inodes, and removed under-construction leases. `Feature` is a marker for inode feature attachments.

Control flow: snapshot-aware mutators call `recordModification(latestSnapshotId)` before changing current metadata. State membership helpers walk parents, references, and snapshot children to decide current/latest-snapshot presence. Path reconstruction walks parents twice, first for size and then for byte copy. Content summary and quota entry points seed storage policy context, delegate to subclass traversal, then convert counters to public `ContentSummary`. Deletion paths call subclass cleanup, while `BlocksMapUpdateInfo.addDeleteBlock` marks blocks deleted and recursively collects copy-on-truncate blocks.

State and persistence behavior: each inode holds a parent pointer that can be either an `INodeDirectory` or `INodeReference`. Subclasses persist most fields in fsimage/edit logs; this base class defines how snapshot copies and current state are distinguished. Reclaim and quota contexts are transient operation state used to later update block maps, leases, and quota caches.

Dependencies and integration points: it sits at the center of NameNode code, integrating with `INodeDirectory`, `INodeFile`, `INodeSymlink`, `INodeReference`, snapshot classes, block management, storage policies, quota/content summary classes, `FSDirectory`, visitor APIs, ACL/XAttr features, and edit-log operation cleanup.

Risks: equality and hashing are id-only, so id uniqueness is critical. Parent/reference handling is subtle around rename plus snapshots; quota updates may need propagation along old and new paths. Many safety checks are assertions or preconditions whose misuse can corrupt namespace accounting. Recursive cleanup/content summary can be expensive and must coordinate with lock-yielding contexts in callers/subclasses.

Test signals: tests should cover snapshot-aware metadata mutation, current/latest-snapshot membership, reference parent resolution, path component generation, quota/content summary conversion, block deletion including truncate blocks, reclaim context copy semantics, id-based equality, invalid path assertions, and visitor unsupported/default behavior.
