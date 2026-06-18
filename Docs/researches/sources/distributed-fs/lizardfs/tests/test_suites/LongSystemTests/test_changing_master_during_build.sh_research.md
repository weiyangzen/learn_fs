# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_changing_master_during_build.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for changing master during build in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `changing master during build` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '40 minutes'`
- `MASTERSERVERS=$metaservers_nr`
- `CHUNKSERVERS=2`
- `CHUNKSERVER_EXTRA_CONFIG="MASTER_RECONNECTION_DELAY`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="MAGIC_AUTO_FILE_REPAIR`
- `MINIMUM_PARALLEL_JOBS=5`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `master_kill_loop() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `git`
- `cmake`
- `lizardfs_master_n`
- `lizardfs_shadow_synchronized`
- `lizardfs_stop_master_without_saving_metadata`
- `lizardfs_make_conf_for_shadow`
- `lizardfs_make_conf_for_master`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `make`

Assertions and expectations include:
- `assert_program_installed git`
- `assert_program_installed cmake`
- `assert_eventually "lizardfs_shadow_synchronized $shadow_id"`
- `assert_eventually "lizardfs_shadow_synchronized $new_master_id"`
- `assert_eventually "lizardfs_shadow_synchronized $prev_master_id"`
- `assert_success git clone https://github.com/lizardfs/lizardfs.git`
- `assert_success cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../install`
- `assert_success make -j${PARALLEL_JOBS} install`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 63 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for changing master during build. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
