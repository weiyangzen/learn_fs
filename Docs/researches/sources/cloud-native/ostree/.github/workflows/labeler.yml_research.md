<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/labeler.yml -->
## sources/cloud-native/ostree/.github/workflows/labeler.yml

### Purpose
This workflow applies path-based labels to pull requests.

### APIs, Types, and Control Flow
It runs on `pull_request_target`, has one `triage` job on Ubuntu, grants `contents: read` and `pull-requests: write`, and invokes `actions/labeler@v4` using the repository labeler config.

### State, Dependencies, and Integration
The action updates PR labels through GitHub API state. It integrates with `.github/labeler.yml`.

### Risks and Test Signals
Because `pull_request_target` has elevated context, it should avoid checking out and running untrusted PR code; this workflow only runs an action, which is the expected safer shape. Test signal is expected labels appearing on PRs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/labeler.yml -->
