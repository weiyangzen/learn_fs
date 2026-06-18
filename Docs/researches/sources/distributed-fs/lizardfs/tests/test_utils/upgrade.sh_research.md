<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/upgrade.sh -->
# sources/distributed-fs/lizardfs/tests/test_utils/upgrade.sh

Purpose: shared upgrade-test helpers for stopping legacy services, switching to current daemons, generating deterministic files, validating fixtures, and manipulating chunkserver ranges.

Important APIs, functions, and commands: defines `generate_file`, `validate_file`; uses `lizardfs_admin_master`, `lizardfs_chunkserver_daemon`, `lizardfs_master_n`, `lizardfs_wait_for_all_ready_chunkservers`, `lizardfs_mount_unmount`, `lizardfs_mount_start`, `file-generate`, `file-validate`, `lizardfsXX_chunkserver_daemon`, `lizardfsXX_master_daemon`, `assert_success`, `assert_equals`; drives configuration through `SEED`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `function stop_lizardfsXX_chunkservers_from_to {`; `lizardfsXX_chunkserver_daemon $i stop`; `assert_equals 1 $mas_n # so far, we always have only 1 legacy master`; `assert_success lizardfs_mount_unmount $i`; `assert_success lizardfsXX_chunkserver_daemon $i stop`; `assert_success lizardfsXX_master_daemon stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `SEED`, `FILE_SIZE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: upgrade tests depend on external package availability and version-specific behavior. Test signals: hard assertions, content validation, probe/admin porcelain output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_utils/upgrade.sh -->
