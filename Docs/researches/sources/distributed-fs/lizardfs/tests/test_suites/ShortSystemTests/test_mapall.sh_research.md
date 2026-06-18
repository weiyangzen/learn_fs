<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mapall.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mapall.sh

Purpose: checks export-side mapall UID/GID remapping across normal and mapall mounts, including metadata-generator output and noowner exceptions.

Important APIs, functions, and commands: defines `stat_ug`; uses `setup_local_empty_lizardfs`, `metadata_get_all_generators`, `expect_equals`, `lizardfs {geteattr}`; drives configuration through `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_EXPORTS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `expect_equals 'lizardfstest:lizardfstest' $(stat_ug "$normal/normal")`; `expect_equals 'lizardfstest_6:lizardfstest_4' $(stat_ug "$normal/mapall")`; `expect_equals 'root:root' $(stat_ug "$mapall/normal")`; `expect_equals 'lizardfstest:lizardfstest' $(stat_ug "$mapall/mapall")`; `rm "$normal/normal"`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `MOUNT_1_EXTRA_EXPORTS`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_mapall.sh -->
