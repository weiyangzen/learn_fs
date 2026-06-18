# sources/distributed-fs/ceph-client/scripts/spdxcheck-test.sh

Purpose: `spdxcheck-test.sh` is a smoke test for the SPDX checker against text, binary, stdin, and full-tree inputs.

Important APIs, types, and functions: it loops over `Makefile` and `Documentation/images/logo.gif`, running `python3 scripts/spdxcheck.py $FILE` and stdin mode via `python3 scripts/spdxcheck.py - < $FILE`, then runs a complete tree check redirected to `/dev/null`.

Control flow: there is no `set -e`, so the effective failure behavior depends on the shell or caller. Commands run sequentially.

State and persistence: no persistent state; stdout from full tree scan is discarded.

Dependencies and integration points: depends on Python 3, `scripts/spdxcheck.py`, and the referenced files existing in a full kernel tree.

Risks: without `set -e`, a failed command may not stop the script when run directly in some contexts. Referenced paths must exist in the source tree variant.

Test signals: nonzero exit from any `spdxcheck.py` call should be captured by the invoking test harness. Add `set -e` if direct execution should fail fast.
