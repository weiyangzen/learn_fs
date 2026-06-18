# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_1.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `custom goals rebalancing case 1` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "6 minutes"`
- `CHUNKSERVERS=5`
- `USE_LOOP_DISKS=YES`
- `CHUNKSERVER_LABELS="0,1,2:ssd|3,4:hdd"`
- `MASTER_CUSTOM_GOALS="1`
- `CHUNKSERVER_EXTRA_CONFIG="PERFORM_FSYNC`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`
- `lizardfs_rebalancing_status`

Assertions and expectations include:
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 90 || \$2 > 110'" "2 minutes"`
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 70 || \$2 > 90'" "3 minutes"`
- `assert_awk_finds_no '$2 < 70 || $2 > 90' "$(lizardfs_rebalancing_status)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 33 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
