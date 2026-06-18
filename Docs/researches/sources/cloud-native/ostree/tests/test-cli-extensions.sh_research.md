# sources/cloud-native/ostree/tests/test-cli-extensions.sh

Purpose: validates OSTree CLI extension command discovery and unknown-command error behavior.

Important APIs/functions: uses `${CMD_PREFIX} ostree env`, `${CMD_PREFIX} ostree nosuchcommand`, `assert_file_has_content`, and `assert_not_reached`.

Control flow: runs the `env` extension and checks it receives/prints a custom test flag, then runs a nonexistent command and expects a clean `Unknown command 'nosuchcommand'` error instead of invoking an absent extension.

State/persistence: writes `out.txt` and `err.txt` only. Dependencies include the test environment's local extension path and `libtest.sh` assertions.

Integration/risk/test signals: protects command dispatch between built-in commands and `ostree-*` extension binaries. Risks are environment path setup and exact error wording. Two TAP ok messages cover extension and unknown command.
