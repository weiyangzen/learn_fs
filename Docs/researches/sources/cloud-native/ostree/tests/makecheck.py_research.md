<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/makecheck.py -->
## sources/cloud-native/ostree/tests/makecheck.py

Purpose: convenience wrapper around `make check` that extracts failed test output from `test-suite.log`.

Important APIs/functions: `run_make_check()` runs `make check -j 6` plus CLI args; `is_header()` detects Automake section headers; `print_truncated()` prints first line and last 20 lines; `get_failed_test_output()` parses failure/error sections; `analyze` mode parses a supplied log.

Control flow/state: on normal run, exits 0 if make succeeds; on failure, parses `test-suite.log`, optionally moves it to `$ARTIFACTS/test-suite.log`, and exits 1.

Dependencies/integration: requires GNU make, Automake-style `test-suite.log`, Python 3, and optional artifacts directory.

Risks/test signals: parser assumes previous line before `========` is `KEY: value`; malformed logs can break splitting. Signal is concise failed test tail output in CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/makecheck.py -->
