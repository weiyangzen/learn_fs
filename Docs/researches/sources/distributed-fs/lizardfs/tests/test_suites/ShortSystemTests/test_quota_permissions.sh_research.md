<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_permissions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_permissions.sh

Purpose: checks that quota modification permissions follow export/admin rules and user identity expectations.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs {repquota, setquota}`; drives configuration through `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_failure lizardfs setquota -g $gid 0 0 3 6 . # fail, permissions missing`; `expect_failure lizardfs repquota -a . # fail, permissions missing`; `expect_failure lizardfs repquota -g $gid1 . # fail, permissions missing`; `expect_failure lizardfs repquota -u $uid1 . # fail, permissions missing`; `expect_success lizardfs repquota -g $gid . # OK`.

State and persistence behavior: State and persistence under test include quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_quota_permissions.sh -->
