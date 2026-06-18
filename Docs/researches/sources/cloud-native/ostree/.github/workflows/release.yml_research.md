<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/release.yml -->
## sources/cloud-native/ostree/.github/workflows/release.yml

### Purpose
This workflow sanity-checks release commits that modify `configure.ac`.

### APIs, Types, and Control Flow
It runs for PRs to `main` when `configure.ac` changes, but the job only proceeds when the PR label is `kind/release` or the title starts with `Release`. It checks out the PR head with recursive submodules and full history, runs `ci/ci-release-build.sh` at `HEAD`, then checks out `HEAD^` and runs the same sanity check.

### State, Dependencies, and Integration
It depends on git history being available and on the release-check script parsing `configure.ac`, commit messages, and symbol files. It mutates only the working checkout.

### Risks and Test Signals
The `github.event.label.name` expression may only be populated for labeled events, while the workflow trigger is plain `pull_request`; title matching is the fallback. The test signal is the script accepting both release and previous commit states, catching accidental `is_release_build` mismatches.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/release.yml -->
