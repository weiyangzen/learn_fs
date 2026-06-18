# sources/cloud-native/nydus/tests/bats/install_bats.sh

Purpose: installs BATS from source when it is not already present.

Important APIs/types/functions: shell script with `set -e`; runs `which bats && exit`, defines `BATS_REPO=https://github.com/bats-core/bats-core.git` and `LOCAL_DIR=/tmp/bats`, clones the repository, runs `./install.sh /usr`, and removes the temporary directory.

Control flow: if `bats` exists on PATH the script exits successfully. Otherwise it recreates `/tmp/bats`, clones bats-core, installs into `/usr`, returns to the previous directory, and cleans up.

State and persistence: modifies `/usr` by installing BATS and deletes `/tmp/bats`. It has no project-local state.

Dependencies and integration points: used by `tests/bats/Makefile` before running BATS suites. Requires network access, git, shell, and permissions to install under `/usr`.

Risks: `git clone ... || true` can hide clone failures; the subsequent `cd bats-core` will fail under `set -e`, but the original failure reason may be obscured. Unquoted variables are safe for current constants but fragile. Installing to `/usr` requires root privileges and mutates the host.

Test signals: supports integration tests but is not tested itself. Failures here prevent the BATS CI target from running.
