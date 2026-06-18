<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux_test.go -->
# sources/cloud-native/moby/daemon/containerfs_linux_test.go

Purpose: unit coverage for safe creation of mount targets inside an `os.Root`.

Important APIs and flow: `TestCreateIfNotExists` opens a temporary directory as an `os.Root`, verifies directory creation is idempotent, verifies nested file creation creates parents and a file rather than a directory, and verifies repeated file creation succeeds.

State and persistence: writes only inside temporary test directories.

Dependencies and integration: targets `createIfNotExists` in `containerfs_linux.go`, using `gotest.tools` assertions and the Go `os.Root` API.

Risks and gaps: does not cover symlink escape attempts, bind mounting, recursive read-only behavior, mount namespace lifecycle, `RunInFS`, `GoInFS`, `Close`, or `Stat`.

Test signals: narrow but useful for idempotent mount-target preparation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerfs_linux_test.go -->
