<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-driver.sh -->
## sources/cloud-native/ostree/buildutil/tap-driver.sh

### Purpose
This automake TAP driver executes a test command, parses TAP output, writes per-test logs and `.trs` metadata, and prints decorated summary lines.

### APIs, Types, and Control Flow
Shell option parsing requires `--test-name`, `--log-file`, `--trs-file`, then passes the command output and final exit status into an embedded awk program. The awk parser tracks planned tests, result numbers, TODO/SKIP directives, bailout, comments, expected failures, colorization, merge behavior, and exit status. It reports PASS/FAIL/XFAIL/XPASS/SKIP/ERROR, determines whether recheck or global log copy is needed, and writes automake metadata fields to the `.trs` file.

### State, Dependencies, and Integration
It writes the log file via fd 3 and `.trs` metadata. It uses `AM_TAP_AWK` or awk and is invoked by `glib-tap.mk` as the automake `LOG_DRIVER`.

### Risks and Test Signals
The parser is old but nuanced; small changes can break automake semantics around late plans, unplanned tests, expected failures, and exit-status handling. Test signal is correct `make check` reporting, especially for skipped tests, failing TAP, bailout, and recheck behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-driver.sh -->
