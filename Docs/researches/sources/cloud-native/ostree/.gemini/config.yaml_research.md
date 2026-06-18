<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.gemini/config.yaml -->
## sources/cloud-native/ostree/.gemini/config.yaml

### Purpose
This config enables Gemini code review behavior for pull requests while suppressing noisy summaries.

### APIs, Types, and Control Flow
The YAML sets `have_fun: true`, enables `code_review`, uses a medium severity threshold, allows unlimited comments with `max_review_comments: -1`, and configures pull-request-opened behavior so `help` and `summary` are disabled but `code_review` is true.

### State, Dependencies, and Integration
There is no runtime state. The file integrates only with the Gemini review service and has an empty `ignore_patterns` list, so all files are reviewable unless the service applies its own defaults.

### Risks and Test Signals
The main risk is review-noise configuration drift: unlimited comments can be heavy on large PRs even with summary disabled. Test signal is external service behavior on PR open, not repository tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.gemini/config.yaml -->
