# sources/cloud-native/ostree/tests-unit-container/run.sh

Purpose: simple container unit-test runner for scripts named `test-*` in the same directory.

Important APIs/functions: shell loop over `${dn}/test-*`, executes each case, prints "Running" and "ok" lines, counts cases, and exits 0 under `set -euo pipefail`.

Control flow: any failing test aborts the runner due to `set -e`. Successful tests increment `n` and final output reports the count.

State/persistence: no persistent state beyond whatever individual tests create.

Dependencies/integration: bash and executable test scripts in `tests-unit-container`. It is intended for the `privunit`/podman workflow mentioned by test comments.

Risks: glob order is shell/filesystem sorted and includes any executable or non-executable matching `test-*`; if a matching file is not executable, the runner fails. No TAP plan is emitted.

Test signals: this is itself a test harness; its output gives count and per-case pass markers.
