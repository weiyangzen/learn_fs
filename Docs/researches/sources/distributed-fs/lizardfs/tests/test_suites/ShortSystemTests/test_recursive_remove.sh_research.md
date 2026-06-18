<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_recursive_remove.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_recursive_remove.sh

Purpose: removes a large generated tree recursively and validates metadata/chunk cleanup and command completion.

Important APIs, functions, and commands: defines `dirgenerate`; uses `setup_local_empty_lizardfs`, `assert_eventually`, `lizardfs {rremove, setgoal, settrashtime}`; drives configuration through `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`, `CHUNKS_LOOP_MAX_CPU`, `OPERATIONS_DELAY_INIT`, `MASTER_CUSTOM_GOALS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir root${level}_${suffix}`; `mkdir test`; `lizardfs setgoal ec test`; `lizardfs settrashtime 0 test`; `lizardfs rremove test`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, trash and undel metadata, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `CHUNKSERVERS`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`, `MASTER_EXTRA_CONFIG`, `CHUNKS_LOOP_MIN_TIME`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load. Test signals: hard assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_recursive_remove.sh -->
