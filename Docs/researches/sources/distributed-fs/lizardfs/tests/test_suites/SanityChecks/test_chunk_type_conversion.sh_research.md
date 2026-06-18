# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_type_conversion.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `chunk type conversion` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 60 seconds`
- `WAIT_FOR_REPLICATION=40`
- `NUMBER_OF_CHUNKSERVERS=4`
- `GOALS_TO_BE_TESTED="2`
- `VERIFY_FILE_CONTENT=NO`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 7 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_chunk_type_conversion.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
