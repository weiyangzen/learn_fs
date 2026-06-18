# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_set_get_goal.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for set get goal in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `set get goal` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MASTER_CUSTOM_GOALS="8`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`

Assertions and expectations include:
- `assert_equals "directory: $new_goal" "$(lizardfs setgoal "$new_goal" directory || echo FAILED)"`
- `assert_equals "directory: $new_goal" "$(lizardfs getgoal directory || echo FAILED)"`
- `assert_success lizardfs setgoal $goal directory/file$goal`
- `assert_equals "directory/file$goal: $goal" "$(lizardfs getgoal directory/file$goal)"`
- `assert_success lizardfs setgoal 3 directory/file{2..3}`
- `expect_equals $'directory/file2: 3\ndirectory/file3: 3' "$(lizardfs getgoal directory/file{2..3})"`
- `assert_success lizardfs setgoal -r 3 directory`
- `expect_equals "directory/file2: 3" "$(lizardfs getgoal directory/file2)"`
- `expect_equals "directory/file3: 3" "$(lizardfs getgoal directory/file3)"`
- `expect_equals "directory/file5: 3" "$(lizardfs getgoal directory/file5)"`
- `expect_equals "directory/fileX: 3" "$(lizardfs getgoal directory/fileX)"`
- `expect_equals "directory/filexor2: 3" "$(lizardfs getgoal directory/filexor2)"`
- `expect_equals "directory/filexor5: 3" "$(lizardfs getgoal directory/filexor5)"`
- `expect_equals "directory/filexor7: 3" "$(lizardfs getgoal directory/filexor7)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 61 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for set get goal. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
