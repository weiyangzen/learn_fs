# sources/cloud-native/soci-snapshotter/scripts/check-all.sh

Purpose: convenience wrapper to run standard repository checks.

Important APIs/types/functions: executes `check-dco.sh`, `check-flatc.sh`, `check-ltag.sh`, and `check-lint.sh` sequentially.

Control flow: fail-fast shell with `set -eux -o pipefail`; each script must succeed.

State and persistence: read-only checks except any called tool side effects; no direct state.

Dependencies/integration points: relies on sibling scripts and installed check tools.

Risks: assumes it is run from the scripts directory or a working directory where `./check-*.sh` resolves correctly; unlike many other scripts it does not compute its own directory.

Test signals: aggregate CI signal for DCO, generated flatbuffers, headers, and lint.
