<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_write_during_scan.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_write_during_scan.sh

Purpose: performs reads and writes while chunk scanning is slowed to catch races between scan state and client I/O.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_chunkserver_daemon`, `lizardfs_wait_for_all_ready_chunkservers`, `file-generate`, `file-validate`, `lizardfs {setgoal}`; drives configuration through `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`, `LD_PRELOAD`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir goal3`; `lizardfs setgoal 2 goal3`; `FILE_SIZE=1K file-generate goal3/test_${file}`; `lizardfs_chunkserver_daemon 0 stop`; `lizardfs_chunkserver_daemon 1 stop`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `USE_RAMDISK`, `MOUNTS`, `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `MOUNT_EXTRA_CONFIG`, `FILE_SIZE`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_write_during_scan.sh -->
