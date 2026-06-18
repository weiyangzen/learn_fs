<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xattr.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xattr.sh

Purpose: checks extended attribute create/list/read/remove behavior on files, symlinks, and directories.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs_master_daemon`, `attr`, `expect_equals`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `assert_program_installed attr`; `setup_local_empty_lizardfs info`; `mkdir dir`; `name3="$(base64 -w 0 /dev/urandom | head -c 250)" # attr can't set >250B name (but doc says 256B)`; `expect_success attr -qs "$name1" -V "$value1" .`; `expect_success attr -qs "$name2" -V "$value2" file`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, extended attributes, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `attr`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: randomized paths need deterministic validation to avoid irreproducible failures. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_xattr.sh -->
