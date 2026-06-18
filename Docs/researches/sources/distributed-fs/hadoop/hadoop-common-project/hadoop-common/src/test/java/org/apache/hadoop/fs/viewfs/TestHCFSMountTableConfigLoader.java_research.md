# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestHCFSMountTableConfigLoader.java

Purpose: Tests `HCFSMountTableConfigLoader`, which loads viewfs mount-table XML configuration files from Hadoop-compatible filesystem paths.

Important APIs/types/functions: `MountTableConfigLoader`, `HCFSMountTableConfigLoader.load`, `ViewFsTestSetup.addMountLinksToFile`, `Constants.CONFIG_VIEWFS_PREFIX`, `CONFIG_VIEWFS_LINK`, `FsConstants.FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, `LocalFileSystem`, and JUnit lifecycle `BeforeAll/BeforeEach/AfterAll`.

Control flow: `init` creates a local filesystem test root. `setUp` creates a fresh configuration, maps overloaded `file` scheme implementation to `LocalFileSystem`, and creates `table.1.xml` and `table.2.xml`. The multiple-file test writes mount links only to the newer version file and loads the directory, expecting `/src1` and `/src2` config keys to map to `/tar1` and `/tar2`. Invalid-format tests create files with bad version naming, optionally containing mount links, then load the directory and assert no config keys are set. One test expects `FileNotFoundException` for a non-existent explicit file URI. Another writes links to the old-version file and loads that explicit file successfully. `tearDown` removes the test root after all tests.

State/persistence: Creates local XML files under a test root and mutates a fresh `Configuration` per test. Static file references are recreated in setup.

Dependencies/integration: Integrates mount-table loader version selection/parsing with local FS, viewfs config key conventions, and helper code that writes XML mount links.

Risks: Version file ordering and invalid filename parsing are central compatibility points. The method name `testLoadWithMountFile` actually checks a non-existent file, while `testLoadWithNonExistentMountFile` loads an existing old-version file, so names are confusing.

Test signals: Config keys present with expected target values for valid files, null config values for invalid filenames, and `FileNotFoundException` for missing explicit mount file.
