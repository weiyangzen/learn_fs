# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsTrash.java

Purpose: tests trash behavior for `ViewFileSystem`, including shell trash integration and localized trash placement inside mount points.

Important APIs and types: `ViewFileSystemTestSetup`, `TestTrash.trashShell`, `Trash.moveToAppropriateTrash`, `Trash`, `ConfigUtil.addLink`, `CONFIG_VIEWFS_TRASH_FORCE_INSIDE_MOUNT_POINT`, `FS_TRASH_INTERVAL_KEY`, `ContractTestUtils`, and `TestTrash.TestLFS`.

Control flow: setup creates a local target filesystem using `TestTrash.TestLFS`, configures a viewfs mount table, sets default FS to viewfs, and registers the same local implementation so home directory behavior is deterministic. `testTrash` delegates to Hadoop's shared trash shell test. `testLocalizedTrashInMoveToAppropriateTrash` first verifies default trash goes to target FS trash based on resolved path, then enables localized trash and verifies the file appears under `viewfs:/data/.Trash/<user>/Current`.

State and persistence: creates local files and trash directories and removes target test root plus `.Trash/Current` in teardown.

Dependencies and integration: connects viewfs path resolution with common `Trash` APIs and config flags.

Risks and test signals: regressions include trash paths built from unresolved viewfs paths when target trash is expected, localized trash ignored, or incorrect local home directory due to the filesystem implementation setting.
