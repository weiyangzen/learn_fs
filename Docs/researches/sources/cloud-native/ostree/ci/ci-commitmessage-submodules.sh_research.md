<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-commitmessage-submodules.sh -->
## sources/cloud-native/ostree/ci/ci-commitmessage-submodules.sh

### Purpose
This CI gate ensures commits that change submodule pointers explicitly say which submodule was updated.

### APIs, Types, and Control Flow
It sources `libbuild.sh`, accepts an optional head commit, creates a guarded tempdir, ensures git exists, copies the repository to avoid recloning submodules, iterates commits in `origin/main..HEAD`, rejects non-empty merge commits, records changed files and commit logs, checks out each commit, initializes submodules, and for each changed submodule requires the commit message to contain `Update submodule: <path>` unless the author is Dependabot.

### State, Dependencies, and Integration
It uses temp copies, git logs/diffs/checkouts, and submodule metadata. It integrates with the `codestyle` GitHub Actions job and Dependabot submodule updates.

### Risks and Test Signals
It assumes `origin/main` exists and that copying the repo preserves enough metadata. The grep for author is simple and tied to Dependabot log formatting. Test signal is CI failure on accidental submodule pointer changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/ci-commitmessage-submodules.sh -->
