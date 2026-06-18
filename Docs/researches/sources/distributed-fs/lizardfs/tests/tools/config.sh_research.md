<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/config.sh -->
# sources/distributed-fs/lizardfs/tests/tools/config.sh

Purpose: provides LizardFS test harness coverage for config.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: defines `check_configuration`; uses `mfsmount`, `mfsmaster`, `mfschunkserver`; drives configuration through `TEMP_DIR`, `PATH`.

Control flow: The script proceeds through these visible steps: `elif [[ -f /etc/lizardfs_tests.conf ]]; then`; `echo "Using the default \"/etc/lizardfs_tests.conf\" tests configuration file"`; `. /etc/lizardfs_tests.conf`; `mkdir -p "$TEMP_DIR"`; `if ! touch "$TEMP_DIR/check_tmp_dir" || ! rm "$TEMP_DIR/check_tmp_dir"; then`; `$LIZARDFS_ROOT/sbin/{mfsmaster,mfschunkserver} \`.

State and persistence behavior: State and persistence under test include chunk files and replica/part placement, client mount/export state; all are created under the test runner workspace or through the mounted LizardFS instance and are expected to be cleaned by the harness.

Dependencies and integration points: Dependencies and integration points: environment/config variables such as `TEMP_DIR`, `PATH`, LizardFS CLI/test helpers.

Risks and test signals: Risks: main risks are missing prerequisites, daemon readiness races, and assertion coverage that checks counts without validating full contents. Test signals: content validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/config.sh -->
