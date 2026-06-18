# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_files_by_inode_permissions.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `files by inode permissions` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `FILE_SIZE="$size"`
- `INODE_PATH="${info[mount0]}/.lizardfs_file_by_inode"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_file_by_inode`
- `file-validate`
- `dd`

Assertions and expectations include:
- `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`
- `assert_success file-validate "$INODE_PATH/3"`
- `assert_failure dd if=/dev/random of="$INODE_PATH/3" bs=1 count=1`
- `assert_failure file-validate "$INODE_PATH/4"`
- `assert_failure dd if=/dev/random of="$INODE_PATH/5" bs=1 count=1`
- `assert_failure file-validate "$INODE_PATH/5"`
- `assert_success file-validate "$INODE_PATH/6"`
- `assert_success dd if=/dev/random of="$INODE_PATH/6" bs=1 count=1`
- `assert_success printf "#/bin/bash\necho 'Hello!\n' > /dev/null" > "$INODE_PATH/7"`
- `assert_success "$INODE_PATH/7"`
- `assert_failure ls $INODE_PATH`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 37 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
