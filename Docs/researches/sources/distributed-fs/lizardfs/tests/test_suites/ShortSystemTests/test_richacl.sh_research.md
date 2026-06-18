<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_richacl.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_richacl.sh

Purpose: checks richacl command support and ACL persistence through LizardFS where richacl tooling is available.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `richacl`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `richacl`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`, `CHUNKSERVER_EXTRA_CONFIG`, `READ_AHEAD_KB`, `MAX_READ_BEHIND_KB`.

Risks and test signals: Risks: lock tests risk stale owners or blocked helper processes. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_richacl.sh -->
