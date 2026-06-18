# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_general.sh

## Purpose
This shell scenario exercises upgrade compatibility in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `lizardfs upgrade general` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 90 seconds`
- `CHUNKSERVERS=2`
- `USE_RAMDISK=YES`
- `MASTERSERVERS=2`
- `START_WITH_LEGACY_LIZARDFS=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_1_EXTRA_CONFIG="CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_TIME`
- `REPLICATION_TIMEOUT='30`
- `FILE_SIZE=12345678`
- `function generate_file {`

External commands and harness APIs used by the scenario:
- `mfsmount`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_admin_master`
- `lizardfsXX`
- `mfssetgoal`
- `file-generate`
- `file-validate`
- `lizardfs_master_n`
- `lizardfs_shadow_synchronized`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `mfsgetgoal`
- `lizardfsXX_chunkserver_daemon`

Assertions and expectations include:
- `assert_equals 1 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 2 $(lizardfs_admin_master list-chunkservers | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 1 $(lizardfs_admin_master list-mounts | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success lizardfsXX mfssetgoal 2 dir`
- `assert_success generate_file file0`
- `assert_success file-validate file0`
- `assert_eventually "lizardfs_shadow_synchronized 1"`
- `assert_equals 0 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success mkdir dir`
- `assert_equals "dir: $goal" "$(lizardfsXX mfssetgoal "$goal" dir || echo FAILED)"`
- `assert_equals "dir: $goal" "$(lizardfsXX mfsgetgoal dir || echo FAILED)"`
- `assert_equals "$expected" "$(lizardfsXX mfsgetgoal -r dir || echo FAILED)"`
- `assert_success generate_file file1`
- `assert_success file-validate file1`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 113 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
