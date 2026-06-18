# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestDirectoryMarkerListing.java

Purpose: semantic integration tests ensuring retained S3 directory markers are not mistaken for empty directories when listing, globbing, creating, deleting, or renaming. It is intentionally backport-friendly and does not use newer metric-cost helpers.

Important APIs/types/functions: `ITestDirectoryMarkerListing` extends `AbstractS3ATestBase`; `createConfiguration()` disables create-performance flags. `setup()` obtains an AWS SDK `S3Client`, computes S3 keys from `S3AFileSystem.pathToKey`, uses `fs.mkdirs`, `touch`, and direct `putObject` to create a marker directory, a peer object, and a real file below the marker. Helpers `head`, `head404`, `exec`, `toList`, `assertContainsExactlyStatusOfPaths`, and `assertRenamed` wrap assertions.

Control flow: tests first verify raw marker/file existence, then exercise `listStatus`, `listFiles`, `globStatus`, and `listLocatedStatus`; create APIs must reject no-overwrite attempts; nonrecursive delete must fail while recursive delete removes marker and child; rename tests validate base-directory moves, file moves into marker directories, explicit destination path moves, and failed empty-dir-over-marker rename.

State and persistence: real bucket objects are created through both S3A and low-level SDK calls. Teardown deletes exact marker, marker-with-slash, peer, and child keys before superclass cleanup to avoid audit failures from surplus markers.

Dependencies/integration: AWS SDK S3 model, S3A path/key conversion, audit spans for raw calls, exception translation, filesystem listing/glob/rename/delete semantics.

Risks: direct SDK setup bypasses normal S3A invariants; object ordering differs between objects and common prefixes; parameterized path characters require glob escaping.

Test signals: exact `FileStatus` path sets, expected `FileAlreadyExistsException` and `PathIsNotEmptyDirectoryException`, HEAD/404 checks, and post-rename/delete namespace checks.
