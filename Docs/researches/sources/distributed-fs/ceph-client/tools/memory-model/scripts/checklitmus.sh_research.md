# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checklitmus.sh

Purpose: Runs and judges one specified LKMM litmus test by invoking `runlitmus.sh` followed by `judgelitmus.sh`.

Important APIs/types/functions: Positional argument `$1` is the litmus file path. Calls `scripts/runlitmus.sh $1` and `scripts/judgelitmus.sh $1`.

Control flow: Sequential shell execution; because there is no `set -e`, the script's exit status is that of `judgelitmus.sh`, not necessarily `runlitmus.sh` if the run command fails but judge still runs.

State and persistence: Downstream scripts write `.out` files and judge output according to LKMM environment variables.

Dependencies/integration: Must be run from `tools/memory-model` with environment prepared by caller/parseargs. Depends on runlitmus and judgelitmus scripts.

Risks: `$1` is unquoted, so paths with spaces break. Run failure is not explicitly checked before judging. Only accepts one positional file despite shell passing possible extras to neither command.

Test signals: Run with valid test, missing test, runlitmus failure, judgelitmus mismatch, and file path quoting edge cases.
