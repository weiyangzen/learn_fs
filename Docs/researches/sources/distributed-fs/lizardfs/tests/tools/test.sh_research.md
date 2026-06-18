<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test.sh -->
# sources/distributed-fs/lizardfs/tests/tools/test.sh

Purpose: provides LizardFS test harness coverage for test.sh, using the shell test harness and LizardFS command-line tools.

Important APIs, functions, and commands: `test_begin`, `test_end`, `test_fail`, `test_add_failure`, `test_freeze_result`, `test_frozen`, `parametrize_command`, `test_cleanup`, and `catch_error_` implement the shell test lifecycle, failure accumulation, cleanup, and error trapping.

Control flow: The script proceeds through these visible steps: `rm -f "$ERROR_DIR/syslog.log"`; `'user=$(stat -c "%U" "{}"); sudo -nu $user setfacl -b "{}" ; sudo -nu $user chmod 777 "{}"' \;`; `echo "TEMP_DIR variable empty, cowardly refusing to rm -rf /*"`; `if ! rm -rf "$TEMP_DIR"/* 2>/dev/null; then`; `rm -rf "$TEMP_DIR"/*`; `if ! rm -rf "$RAMDISK_DIR"/* 2>/dev/null; then`.

State and persistence behavior: State includes the failure counter, frozen-result marker, cleanup traps, test start/end timestamps, and global shell variables consumed by the framework.

Dependencies and integration points: Dependencies and integration points: `setfacl`, `tee`, environment/config variables such as `PS4`, LizardFS CLI/test helpers.

Risks and test signals: Risks: fixed sleeps make the scenario sensitive to host speed; daemon kill/stop paths can leave stale state if readiness checks are wrong; lock tests risk stale owners or blocked helper processes. Test signals: successful command completion and nonzero exit status on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/tools/test.sh -->
