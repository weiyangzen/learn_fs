# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHarFileSystem.java

Purpose: validates core `HarFileSystem` behavior that does not require a full archive fixture: URI rejection, checksum nullability, block-location offset normalization, and method-override coverage against `FileSystem`.

Important APIs/types/functions: `HarFileSystem`, `FileSystem`, `BlockLocation`, `HarFileSystem.fixBlockLocations`, `Path.getFileSystem`, `getFileChecksum`, and the reflection-only `MustNotImplement` interface listing methods HAR should inherit rather than override.

Control flow/state/persistence: `testHarUri` creates invalid `har://` paths and expects `IOException` during filesystem resolution. `testFileChecksum` constructs a HAR path and asserts checksum is null. `testFixBlockLocations` mutates `BlockLocation` arrays in place across eight range-overlap scenarios plus a MAPREDUCE-1752 regression. `testInheritedMethodsImplemented` iterates declared `FileSystem` methods, skips static/private/final methods, and uses reflection to require HAR to override only methods not in the allowlist.

Dependencies/integration points: tightly couples HAR to the evolving `FileSystem` API, including append, ACL, XAttr, snapshot, storage policy, open-file builders, multipart upload, trash, and bulk delete signatures. Reflection makes this a maintenance gate whenever `FileSystem` adds methods.

Risks/test signals: highest-risk signal is API drift: new `FileSystem` methods must be classified as HAR-specific overrides or inherited defaults. Block-location tests catch off-by-one and partial-overlap errors in archived-file reads. URI tests protect HAR authority parsing.
