# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cgi_validate_html.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for cgi validate html in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cgi validate html` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 4 minutes`
- `CHUNKSERVERS=3`
- `DISK_PER_CHUNKSERVER=3`
- `CGI_SERVER="YES"`
- `MOUNTS=3`
- `USE_RAMDISK="YES"`
- `CHUNKSERVER_LABELS="0,1:de|2:us"`
- `MASTER_CUSTOM_GOALS="11`
- `MOUNT_0_EXTRA_CONFIG="mfscachemode=NEVER,mfsreportreservedperiod=1,mfsdirentrycacheto=0"`
- `MOUNT_1_EXTRA_CONFIG="mfsmeta"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota,ignoregid"`
- `MFSEXPORTS_META_EXTRA_OPTIONS="nonrootmeta"`
- `MOUNT_2_EXTRA_EXPORTS="mingoal=1,maxgoal=10,maxtrashtime=2w"`
- `MESSAGE="Validating`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsreportreservedperiod`
- `mfsdirentrycacheto`
- `mfsmeta`
- `setup_local_empty_lizardfs`
- `mfs`
- `mfsmaster`
- `metadata_generate_all`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_program_installed wget tidy`
- `assert_less_than '20' "$(find "$cgi_pages/empty" -name "mfs.cgi*" | wc -l)"`
- `assert_less_than '20' "$(find "$cgi_pages/full" -name "mfs.cgi*" | wc -l)"`
- `expect_empty "$(grep -Inri -A 20 'Traceback' "$cgi_pages" || true)"`
- `MESSAGE="Validating $file" assert_empty "$(tidy -q -errors $file 2>&1)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 70 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for cgi validate html. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
