## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteUtils.java

Purpose: small helper class centralizing client-side validation for bulk delete path collections.

Important APIs and types: `validateBulkDeletePaths(Collection<Path>, int, Path)` checks non-null collection, page-size upper bound, absolute paths, and parent containment. `validatePathIsUnderParent(Path, Path)` walks ancestors until the base path is found.

Control flow: validation uses `requireNonNull` and Hadoop `Preconditions.checkArgument`; per-path checks are applied with `forEach`.

State and persistence behavior: stateless utility, no persistence.

Dependencies and integration points: used by `BulkDelete` implementations or callers before submitting batches.

Risks: base path null is not explicitly checked; containment relies on `Path.equals` and does not canonicalize schemes, authorities, dot segments, symlinks, or case. It permits deleting the base path itself.

Test signals: cover null collection, page overflow, relative paths, exact base path, nested descendants, sibling paths with similar prefixes, qualified vs unqualified paths, and null base path behavior.
