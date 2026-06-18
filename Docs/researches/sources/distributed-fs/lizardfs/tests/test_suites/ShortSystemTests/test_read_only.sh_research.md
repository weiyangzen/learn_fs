<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_only.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_only.sh

Purpose: checks read-only mount behavior across file, directory, xattr, attr, rename, unlink, truncate, and metadata-modifying operations.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_metalogger_daemon`, `file-generate`, `file-validate`, `truncate`, `dd`, `attr`, `setfattr`, `setfacl`, `metadata_print`, `metadata_generate_all`, `metadata_validate_files`, ...; drives configuration through `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_1_EXTRA_EXPORTS`, `MFSEXPORTS_EXTRA_OPTIONS`, `FILE_SIZE`.

Control flow: The script proceeds through these visible steps: `assert_program_installed attr`; `setup_local_empty_lizardfs info`; `lizardfs_metalogger_daemon start`; `metadata_generate_all`; `FILE_SIZE=16M file-generate rw_file`; `expect_success setfacl -m mask::r rw_file`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, `setfattr`, `setfacl`, environment/config variables such as `MOUNTS`, `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_1_EXTRA_EXPORTS`, `MFSEXPORTS_EXTRA_OPTIONS`, `FILE_SIZE`.

Risks and test signals: Risks: quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, soft expectation accumulation, content validation, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_read_only.sh -->
