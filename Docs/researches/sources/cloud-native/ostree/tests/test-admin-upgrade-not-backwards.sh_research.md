# sources/cloud-native/ostree/tests/test-admin-upgrade-not-backwards.sh

Purpose: ensures admin upgrade refuses chronologically older commits unless downgrades are explicitly allowed.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `admin deploy`, `admin upgrade`, `admin upgrade --allow-downgrade`, timestamped `ostree commit`, and object-path helpers.

Control flow: deploys a ref, performs a normal upgrade, creates a new upstream commit with an old timestamp and new content, attempts upgrade and expects a chronological error without importing the new file object, then reruns with `--allow-downgrade` and expects success.

State/persistence: mutates upstream repo history and sysroot repo objects; checks absence/presence of content object paths. Dependencies include timestamp comparison logic.

Integration/risk/test signals: protects downgrade safety during upgrades. Risks are time metadata and exact error text. TAP reports refusal and allowed downgrade.
