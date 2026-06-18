# sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_tar_archives.sh

## Purpose
This shell scenario exercises ContinuousTests scenario coverage for tar archives in the LizardFS bash test harness. The script is part of `ContinuousTests` and focuses on `tar archives` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 240 minutes  # Must be high when the 30G file is validated`
- `MESSAGE="Verifying`
- `FILE_SIZE=$size`
- `verify_archive() {`

External commands and harness APIs used by the scenario:
- `tar`
- `file-validate`
- `lizardfs`
- `file-generate`

Assertions and expectations include:
- `assert_success mkdir work/verify`
- `assert_success tar -xf "$archive" -C work/verify`
- `assert_less_than 4 $(echo "$files" | wc -l)`
- `assert_success file-validate "$file"`
- `assert_success rm -rf work/verify`
- `assert_success rm -rf work/*`
- `assert_success mkdir -p "work/$path"`
- `FILE_SIZE=$size assert_success file-generate "$filename"`
- `assert_success touch "$archive"  # Create if not exists`
- `assert_success lizardfs makesnapshot "$archive" work/tmp.tar`
- `assert_success tar -f work/tmp.tar --append --seek -v -C work "$path"`
- `assert_success mv -v work/tmp.tar "$archive"`
- `assert_success mv -v "$archive.$((i))" "$archive.$((i+1))"`
- `assert_success mv -v "$archive" "$archive.1"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 69 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ContinuousTests scenario coverage for tar archives. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
