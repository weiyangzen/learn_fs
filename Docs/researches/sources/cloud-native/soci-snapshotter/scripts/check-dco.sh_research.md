# sources/cloud-native/soci-snapshotter/scripts/check-dco.sh

Purpose: validates Developer Certificate of Origin signatures for recent commits.

Important APIs/types/functions: runs `git-validation -run DCO -range HEAD~20..HEAD`.

Control flow: fail-fast shell invokes GOPATH-installed `git-validation`.

State and persistence: read-only over git history.

Dependencies/integration points: requires `git-validation` installed by `install-check-tools.sh`.

Risks: only checks last 20 commits and includes comments about known historical exceptions. Shallow clones with less history may fail.

Test signals: CI signal for signed-off-by compliance in recent history.
