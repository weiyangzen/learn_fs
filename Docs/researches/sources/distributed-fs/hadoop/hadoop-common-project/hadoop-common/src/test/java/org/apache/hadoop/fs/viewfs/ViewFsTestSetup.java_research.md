# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/ViewFsTestSetup.java

Purpose: shared setup and mount-link serialization helper for `ViewFs`/`FileContext` tests and overload-scheme central mount-table tests.

Important APIs and types: `FileContext`, `FileContextTestHelper`, `FsConstants.VIEWFS_URI`, `ConfigUtil`, `ViewFileSystemOverloadScheme.ChildFsGetter`, `FSDataOutputStream`, `Constants.CONFIG_VIEWFS_*`, `Shell.WINDOWS`, and `Path`.

Control flow: `setupForViewFsLocalFs` prepares a local target root, links first components for test dir, home dir, and working dir, opens `FileContext` for `viewfs:///`, and sets the working directory. `tearDownForViewFsLocalFs` deletes the target test root. `setUpHomeDir` and `linkUpFirstComponents` mirror the `FileSystem` setup helper. `addMountLinksToFile` writes Hadoop XML properties to a given mount table config file and supports normal links, fallback, merge slash, and NFly links. `addMountLinksToConf` writes equivalent links directly to `Configuration`.

State and persistence: writes temporary mount-table XML when requested and mutates local test directories.

Dependencies and integration: important bridge between in-memory mount config and central mount-table files used by overload scheme tests.

Risks and test signals: serialization bugs can make file-backed and config-backed mount tables diverge; NFly source parsing is strict; wrong scheme selection in `ChildFsGetter` can write config to the wrong filesystem.
