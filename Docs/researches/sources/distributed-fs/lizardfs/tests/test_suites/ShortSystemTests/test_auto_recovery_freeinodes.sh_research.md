# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_freeinodes.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery freeinodes` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=1`
- `MOUNTS=1`
- `USE_RAMDISK="YES"`
- `MOUNT_0_EXTRA_CONFIG="mfscachemode=NEVER,mfsattrcacheto=0,mfsreportreservedperiod=1"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MASTER_EXTRA_CONFIG="$master_cfg"`
- `AUTO_SHADOW_MASTER="NO"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsattrcacheto`
- `mfsreportreservedperiod`
- `setup_local_empty_lizardfs`
- `mfs`
- `metadata_file`
- `metadata_version`
- `metadata_get_version`
- `lizardfs`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `metadata_print`

Assertions and expectations include:
- `assert_eventually '[[ $(grep RELEASE "$changelog_file" | wc -l) == 100 ]]'`
- `assert_equals "$metadata_version" "$(metadata_get_version "$metadata_file")"`
- `assert_success lizardfs_master_daemon start`
- `assert_less_than "$metadata_version" "$new_metadata_version"`
- `assert_awk_finds_no '/CREATE.*:20$/' "$(cat "$changelog_file")"`
- `assert_awk_finds    '/CREATE.*:20$/' "$(cat "$changelog_file")" # Make sure that inode 20 was reused`
- `assert_equals "$new_metadata_version" "$(metadata_get_version "$metadata_file")"`
- `assert_no_diff "$metadata" "$(metadata_print "${info[mount0]}")"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 55 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
