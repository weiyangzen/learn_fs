<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_nfs4_acl.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_nfs4_acl.sh

Purpose: verifies NFSv4 ACL storage and retrieval on files/directories/symlinks through the LizardFS mount.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `file-generate`, `nfs4_setfacl`, `nfs4_getfacl`, `assert_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `assert_program_installed nfs4_setfacl`; `assert_program_installed nfs4_getfacl`; `setup_local_empty_lizardfs info`; `mkdir -p dir1/dir2`; `FILE_SIZE=1234567 file-generate file1`; `FILE_SIZE=2345678 file-generate dir1/file2`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `nfs4_setfacl`, `nfs4_getfacl`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `FILE_SIZE`.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_nfs4_acl.sh -->
