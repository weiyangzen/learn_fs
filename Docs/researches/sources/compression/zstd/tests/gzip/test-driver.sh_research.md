<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/gzip/test-driver.sh -->
## sources/compression/zstd/tests/gzip/test-driver.sh

Purpose: Automake-compatible test driver that runs one test script, captures its log, writes `.trs` metadata, and maps exit statuses into PASS/FAIL/SKIP/ERROR/XFAIL/XPASS outcomes.

Important APIs and functions: Supports `--test-name`, `--log-file`, `--trs-file`, `--expect-failure`, `--color-tests`, and `--enable-hard-errors`. Internal helpers are `usage_error` and `print_usage`; the main body parses options, installs signal traps, runs the test command, classifies status, writes the log and `.trs`, and exits with the tweaked status.

Control flow: Mandatory options are validated first. The selected test command is executed with stdout/stderr redirected to the log file. Exit status `99` can be downgraded to failure if hard errors are disabled. Result classification follows Automake conventions: `0` is PASS unless expected failure, `77` is SKIP, `99` is ERROR, other statuses are FAIL unless expected failure.

State and persistence: Writes the requested log file and `.trs` file. On signals 1, 2, 13, or 15 it removes those files and exits with the signal-derived status.

Dependencies and integration points: Used by `gzip/Makefile` pattern targets. Downstream automation reads `.trs` keys `:test-result:`, `:global-test-result:`, `:recheck:`, and `:copy-in-global-log:`.

Risks: `set -u` makes missing variables fatal, which is useful but can make option parsing brittle. Color codes include literal escape sequences. The driver does not append the test command itself to metadata, only the result.

Test signals: Console receives a single colored or plain `PASS: name`-style line. The log ends with result and exit status, and `.trs` contains matching metadata.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/gzip/test-driver.sh -->
