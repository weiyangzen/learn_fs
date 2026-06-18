<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_sockets_leak_check.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_sockets_leak_check.sh

Purpose: checks daemon socket descriptor counts across operations to catch socket leaks.

Important APIs, functions, and commands: defines `get_used_socket_count`; uses `setup_local_empty_lizardfs`, `dd`; drives configuration through `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `USE_RAMDISK`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `DISK_PER_CHUNKSERVER`, `USE_RAMDISK`.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_sockets_leak_check.sh -->
