<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfsXX.sh -->
# sources/distributed-fs/lizardfs/tests/tools/lizardfsXX.sh

Purpose: provides LizardFS test harness coverage for lizardfsXX.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `install_lizardfsXX`, `test_lizardfsXX_executables`, `lizardfsXX_chunkserver_daemon`, `lizardfsXX_master_daemon`, `lizardfsXX`, `assert_lizardfsXX_services_count_equals`, and `assert_no_lizardfsXX_services_active` encapsulate legacy-version setup and invocation.

Control flow: The script proceeds through these visible steps: `rm -rf "$LIZARDFSXX_DIR"`; `mkdir -p "$LIZARDFSXX_DIR"`; `mkdir -p ${TEMP_DIR}/apt/apt.conf.d`; `mkdir -p ${TEMP_DIR}/apt/var/lib/apt/partial`; `mkdir -p ${TEMP_DIR}/apt/var/cache/apt/archives/partial`; `mkdir -p ${TEMP_DIR}/apt/var/lib/dpkg`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: `apt-get`, `dnf`, `wget`, `dpkg-deb`, `rpm2cpio`, `fakeroot`, environment/config variables such as `LIZARDFSXX_TAG`, `APT_CONFIG`, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: hard assertions, probe/admin porcelain output, row/count checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/lizardfsXX.sh -->
