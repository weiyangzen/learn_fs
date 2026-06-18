# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestChRootedFileSystem.java

Purpose: Integration/unit tests for `ChRootedFileSystem`, the `FileSystem`-API chroot wrapper, verifying path translation, basic filesystem operations, working-directory handling, ACL/snapshot/storage-policy delegation, delete-on-exit handling, and viewfs child FS interactions.

Important APIs/types/functions: `ChRootedFileSystem`, `FileSystem`, `FileSystemTestHelper`, `FilterFileSystem`, `ViewFileSystem`, `ConfigUtil.addLink`, `ContentSummary`, ACL methods, snapshot methods, storage policy methods, `deleteOnExit`, `resolvePath`, static `getChildFileSystem`, and inner mock `MockFileSystem`.

Control flow: `setUp` creates a local target root and wraps it in `ChRootedFileSystem`; `tearDown` deletes it. Basic tests assert URI, home/working directory, and `makeQualified` behavior. Create/delete, mkdir/delete, rename, content summary, list, working directory, and resolve tests operate through the chrooted FS and verify corresponding target-root paths exist or disappear on the raw local FS. Mock-backed tests configure `mockfs://foo/a/b` and verify paths like `/c` translate to `/a/b/c` for delete, delete-on-exit, ACL operations, snapshots, and storage policies. `testListLocatedFileStatus` creates a viewfs mount to `mockfs://foo/user` and verifies delegation to `/user`.

State/persistence: Creates and deletes local test-root content. Some tests use Mockito-backed raw FS instances. `deleteOnExit` queues state internally until `close`.

Dependencies/integration: Integrates chroot path translation with Hadoop `FileSystem`, local FS, viewfs mount tables, ACLs, snapshots, storage policies, content summaries, and delete-on-exit machinery.

Risks: Local filesystem behavior may differ by platform, especially permissions and URI handling. Several tests rely on current `Path.makeQualified` behavior while comments note a questionable URI path-part interpretation. Mock tests verify delegation paths but not real backend behavior.

Test signals: Existence checks through both chroot and raw target, exact translated mock paths, expected file status paths, `FileNotFoundException` for missing resolve, content-summary quota defaults, and no exception on empty-path URI construction.
