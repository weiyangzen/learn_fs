<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/labeler.yml -->
## sources/cloud-native/ostree/.github/labeler.yml

### Purpose
This file maps changed paths to GitHub PR labels for area triage.

### APIs, Types, and Control Flow
It declares `area/prepare-root` for `src/switchroot/**` and `src/boot`, and `area/rust-bindings` for `rust-bindings/**`. The GitHub labeler action consumes these glob mappings in the labeler workflow.

### State, Dependencies, and Integration
There is no repository runtime state. Integration is with `.github/workflows/labeler.yml` and the `actions/labeler` action running under `pull_request_target`.

### Risks and Test Signals
`pull_request_target` requires careful action configuration because it runs with target-repo permissions; this file is data-only but controls labeling. Missing globs cause under-labeling, not build failure. Test signal is correct labels on PRs touching those paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/labeler.yml -->
