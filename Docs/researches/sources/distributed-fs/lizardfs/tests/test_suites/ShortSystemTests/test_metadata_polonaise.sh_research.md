<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_polonaise.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_polonaise.sh

Purpose: compares metadata exposed by lizardfs-polonaise-server with native metadata printing to catch conversion or serving mismatches.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `lizardfs-polonaise-server`, `metadata_print`, `metadata_get_all_generators`, `metadata_validate_files`, `assert_eventually`, `lizardfs {dirinfo}`; drives configuration through `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MESSAGE`, `DISABLE_PRINTING_XATTRS`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `lizardfs-polonaise-server --master-host=localhost \`; `--master-port=${info[matocl]} \`; `mkdir -p "$mnt"`; `MESSAGE="Client is not available" assert_eventually 'lizardfs dirinfo "$mnt"'`; `for generator in $(metadata_get_all_generators | egrep -v "acl|xattr|trash"); do`.

State and persistence behavior: State and persistence under test include metadata files/changelogs, chunk files and replica/part placement, quota counters and limits, trash and undel metadata, extended attributes, ACL records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, environment/config variables such as `CHUNKSERVERS`, `MOUNTS`, `USE_RAMDISK`, `MFSEXPORTS_EXTRA_OPTIONS`, `MESSAGE`, `DISABLE_PRINTING_XATTRS`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; quota accounting risks off-by-one and soft/hard-limit drift; metadata tests risk comparing volatile fields unless output is normalized. Test signals: hard assertions, metadata diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_metadata_polonaise.sh -->
