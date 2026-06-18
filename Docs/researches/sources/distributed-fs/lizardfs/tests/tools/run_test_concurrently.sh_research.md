<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/run_test_concurrently.sh -->
# sources/distributed-fs/lizardfs/tests/tools/run_test_concurrently.sh

Purpose: provides LizardFS test harness coverage for run_test_concurrently.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: uses `lizardfs {-j, directory, export}`; drives configuration through `NODES_COUNT`, `NODE_NUMBER`, `ARG_NAME`, `KEY`, `VALUE`, `WORKSPACE`, `TEST_SUITE`, `EXCLUDE_TESTS`, `RUN_UNITTESTS`, `VALGRIND`, ....

Control flow: The script proceeds through these visible steps: `make -C build/lizardfs -j$(nproc) install`; `mkdir -m 777 -p $TEST_OUTPUT_DIR`; `rm -rf "${TEST_OUTPUT_DIR:?}"/* || true`; `rm -rf /mnt/ramdisk/* || true`; `--lizardfs_tests_path "${LIZARDFS_TESTS_PATH}" \`.

State and persistence behavior: State and persistence under test include the temporary LizardFS installation, generated files, daemon runtime state, and assertion outputs; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `python3`, `valgrind`, environment/config variables such as `NODES_COUNT`, `NODE_NUMBER`, `ARG_NAME`, `KEY`, `VALUE`, `WORKSPACE`, LizardFS CLI/test helpers.

Risks and test signals: Risks: daemon kill/stop paths can leave stale state if readiness checks are wrong. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/run_test_concurrently.sh -->
