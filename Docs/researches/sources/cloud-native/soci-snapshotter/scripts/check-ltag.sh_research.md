# sources/cloud-native/soci-snapshotter/scripts/check-ltag.sh

Purpose: checks that repository files have required license headers.

Important APIs/types/functions: runs `ltag -t .headers -check -v` from the project root and prints guidance to run `scripts/add-ltag.sh` on failure.

Control flow: compute root, pushd, run ltag check, popd.

State and persistence: read-only validation.

Dependencies/integration points: requires GOPATH-installed `ltag` and `.headers`.

Risks: ltag's file selection controls what is checked; missing tool yields check failure.

Test signals: CI guard for license-header compliance.
