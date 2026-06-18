<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespaceVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespaceVisitor.java

## Purpose

`NamespaceVisitor` is the traversal interface for HDFS namespace trees. It provides default hooks for inode kinds, recursive reference/directory traversal, child/snapshot iteration, and pre/post callbacks around sub-elements.

## Important APIs and types

- Nested `INodeVisitor` default no-op visitor.
- Default methods: `visitFile`, `visitSymlink`, `visitReference`, `visitReferenceRecursively`, `visitDirectory`, `visitDirectoryRecursively`, `visitSnapshottable`, `visitSubs`.
- Static adapters `getChildren` and `getSnapshots` return iterable `Element`s.
- Nested `Element` holds snapshot id and inode.

## Control flow

Concrete `INode.accept` implementations call into the visitor. The default recursive directory flow visits the directory, visits current/snapshot children, and for current-state directories additionally visits snapshottable feature and snapshot roots. Reference recursion visits the reference node, then the referred inode between `preVisitReferred` and `postVisitReferred`.

## State and persistence behavior

The interface has no state. Traversal state is carried by concrete visitors and `Element` values. It does not persist or mutate namespace data by itself.

## Dependencies and integration points

Used by namespace diagnostics and validation visitors. It depends on inode types and snapshot feature/diff classes.

## Risks and edge cases

`visitSubs` names the boolean `isList` but passes it as `isLast`; behavior is correct but the local name is confusing. Snapshot iteration filters only diffs marked snapshot root. Concurrent namespace mutation during traversal is not addressed here and must be controlled by callers.

## Test signals

Visitor tests should exercise all inode kinds, recursive and non-recursive reference behavior, snapshot root traversal, empty child lists, and pre/post hook pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/visitor/NamespaceVisitor.java -->
