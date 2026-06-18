# sources/cloud-native/soci-snapshotter/scripts/add-ltag.sh

Purpose: applies license headers to project files using `ltag`.

Important APIs/types/functions: shell script computes its directory, project root, then runs `$(go env GOPATH)/bin/ltag -v -t .headers` from the root.

Control flow: `set -eux -o pipefail`, pushd root, execute ltag, popd.

State and persistence: mutates files in the repository by adding/updating license headers.

Dependencies/integration points: requires Go environment and `ltag` installed by `install-check-tools.sh`; uses `.headers` template.

Risks: broad file mutation if `.headers` or ltag matching changes. It assumes GOPATH bin contains ltag.

Test signals: paired with `check-ltag.sh`, which fails if headers are missing.
