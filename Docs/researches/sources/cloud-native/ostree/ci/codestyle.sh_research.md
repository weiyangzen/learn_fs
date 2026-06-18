<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/ci/codestyle.sh -->
## sources/cloud-native/ostree/ci/codestyle.sh

### Purpose
This script performs source-structure style checks that do not require building OSTree.

### APIs, Types, and Control Flow
It optionally runs `cargo fmt --check` for every discovered `Cargo.toml` when cargo is installed. It then runs grep-based static analysis for prohibited patterns, currently `glnx_fd_close`, excluding the script itself.

### State, Dependencies, and Integration
It reads the git working tree and may invoke cargo. It integrates with local developer checks and CI style jobs.

### Risks and Test Signals
The `find -iname Cargo.toml` loop can include nested crates and assumes each manifest can be formatted independently. Grep-based checks are simple but can flag comments or examples. Test signal is a clean style check with actionable failure messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/ci/codestyle.sh -->
