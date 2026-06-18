<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_atomicity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_atomicity.sh

Purpose: checks XOR truncate operations are atomic and leave either old or new valid contents.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `find_all_chunks`, `file-generate`, `file-validate`, `truncate`, `dd`, `assert_success`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`, `MESSAGE`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `FILE_SIZE=200K file-generate "$source"`; `lizardfs setgoal xor$level "$file"`; `truncate -s ${i}K "${info[mount$((2 + i % 3))]}/$file"`; `MESSAGE="Testing xor level $level" assert_success file-validate "$file"`; `find_all_chunks -name "*xor_1_of*" | xargs rm -vf`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; XOR/EC tests risk false positives if part placement or reconstruction is not independently checked; randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, soft expectation accumulation, content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xor_truncate_atomicity.sh -->
