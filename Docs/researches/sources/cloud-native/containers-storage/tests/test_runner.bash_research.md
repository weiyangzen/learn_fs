# sources/cloud-native/containers-storage/tests/test_runner.bash

Purpose: thin execution wrapper for `containers-storage` Bats tests.

Important APIs and control flow: it enables `set -e`, changes to the directory containing the script using `readlink -f`, sources `helpers.bash`, defines `execute` to echo and run a command, defaults `TESTS` to all tests when no arguments are supplied, and runs `time bats --tap $TESTS`.

State and persistence: no persistence beyond the helper-supplied `TESTDIR` lifecycle. It inherits driver and storage options from the environment.

Dependencies and integration: depends on Bash, GNU `readlink -f`, `time`, and `bats`. It is called directly by `test_drivers.bash` and can also be invoked manually with test path arguments.

Risks: `execute` uses `eval`, so caller-provided test names are shell-interpreted. This is acceptable for trusted test harness use but unsafe for arbitrary input. `$TESTS` is unquoted to permit multiple tests, trading off pathname safety.

Test signals: returns the Bats process status and emits TAP output; failures propagate due to `set -e`.
