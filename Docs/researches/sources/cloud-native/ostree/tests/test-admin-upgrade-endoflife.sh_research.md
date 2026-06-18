# sources/cloud-native/ostree/tests/test-admin-upgrade-endoflife.sh

Purpose: verifies upgrade handling of commits marked end-of-life with a rebase target.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `admin deploy`, `os_repository_new_commit`, `ostree commit --add-metadata-string ostree.endoflife*`, `admin upgrade --pull-only`, and `--deploy-only`.

Control flow: deploys the runtime branch, creates a new branch, commits an empty EOL marker on the original branch with `ostree.endoflife` and `ostree.endoflife-rebase`, runs split upgrade, and checks the deployment moved to the new branch with expected boot checksum, content iteration, and origin.

State/persistence: writes branch refs, EOL metadata, origin files, and deployment directories. Dependencies include metadata-aware upgrade logic.

Integration/risk/test signals: protects product EOL rebasing semantics. Risks are exact origin content and boot checksum coupling. TAP ok lines cover initial deploy, new branch creation, and redirect update.
