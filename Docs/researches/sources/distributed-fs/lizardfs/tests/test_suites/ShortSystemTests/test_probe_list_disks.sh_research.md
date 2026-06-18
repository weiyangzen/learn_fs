<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_disks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_disks.sh

Purpose: checks list-disks porcelain output for multiple chunkservers and disks, including labels and disk health fields.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `expect_equals`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir dir_$goal`; `lizardfs setgoal $goal dir_$goal`; `FILE_SIZE=60M file-generate dir_$goal/file`; `expect_equals 12 $(wc -l <<< "$disks")`; `cs_data="$(grep ":${info[chunkserver${i}_port]} " <<< "$disks")"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MASTER_EXTRA_CONFIG`, `OPERATIONS_DELAY_INIT`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`.

Risks and test signals: Risks: XOR/EC tests risk false positives if part placement or reconstruction is not independently checked. Test signals: soft expectation accumulation, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_probe_list_disks.sh -->
