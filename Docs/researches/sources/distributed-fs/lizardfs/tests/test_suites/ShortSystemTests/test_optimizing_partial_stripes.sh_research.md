<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_optimizing_partial_stripes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_optimizing_partial_stripes.sh

Purpose: checks partial-stripe optimization for XOR data by observing visible size changes and read behavior during delayed operations.

Important APIs, functions, and commands: uses `setup_local_empty_lizardfs`, `dd`, `expect_equals`, `assert_eventually_prints`, `expect_eventually_prints`, `lizardfs {setgoal}`; drives configuration through `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`.

Control flow: The script proceeds through these visible steps: `setup_local_empty_lizardfs info`; `mkdir "${info[mount0]}/dir"`; `lizardfs setgoal xor3 "${info[mount0]}/dir"`; `expect_eventually_prints "$stripe_size" 'stat -c %s "${info[mount1]}/dir/f1"' '4 seconds'`; `expect_eventually_prints "$file_size" 'stat -c %s "${info[mount1]}/dir/f1"' '7 seconds'`; `expect_equals 0 "$(stat -c %s "${info[mount1]}/dir/f2")"`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, active/pending file-lock records, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: the local LizardFS shell harness, `valgrind`, environment/config variables such as `CHUNKSERVERS`, `USE_RAMDISK`, `MOUNTS`, `MOUNT_EXTRA_CONFIG`.

Risks and test signals: Risks: timing-sensitive waits can hide slow convergence or produce flakes under load; fixed sleeps make the scenario sensitive to host speed; background jobs require reliable cleanup and freeze signaling; daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: hard assertions, soft expectation accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_optimizing_partial_stripes.sh -->
