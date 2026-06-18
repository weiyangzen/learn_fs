# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_acl_permissions.sh

## Purpose
This shell scenario exercises ACL and permission semantics, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `acl permissions` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '4 minutes'`
- `MESSAGE="Testing`
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `LZFS_MOUNT_COMMAND=mfsmount3`
- `MFSEXPORTS_EXTRA_OPTIONS=nomasterpermcheck,ignoregid`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `setfacl`
- `getfacl`
- `mfsmount3`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfstest`
- `lizardfstest_`
- `lizardfstest_1`
- `lizardfstest_2`
- `lizardfstest_0`
- `make`

Assertions and expectations include:
- `assert_program_installed setfacl getfacl python3`
- `MESSAGE="Testing ACL support in $TEMP_DIR/" assert_success setfacl -m group:fuse:rw "$TEMP_DIR/f"`
- `expect_equals "$(ls $lizdir)" "$(ls $tmpdir)"`
- `expect_equals "$expected_perm" "$actual_perm"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 77 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ACL and permission semantics, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
