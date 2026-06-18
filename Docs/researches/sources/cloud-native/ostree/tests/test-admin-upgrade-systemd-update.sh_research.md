# sources/cloud-native/ostree/tests/test-admin-upgrade-systemd-update.sh

Purpose: verifies `.updated` stamp files used by systemd-update-style flows are removed from new deployments and shared var during upgrade.

Important APIs/functions: `setup_os_repository "archive-z2"`, `remote add`, `pull`, `admin deploy`, `os_repository_new_commit`, `admin upgrade`, `touch -r`, and file existence assertions.

Control flow: deploys once, confirms no `.updated` stamps, creates stamps in deployment `/etc` and stateroot `/var`, creates a new commit, upgrades, and checks the new deployment and shared var lack stamps while the previous deployment's `/etc/.updated` remains.

State/persistence: writes deployment-local etc stamps and stateroot var stamps. Dependencies include archive-z2 setup and upgrade behavior.

Integration/risk/test signals: protects cleanup of update markers across deployment boundaries. Risk is mtime/source directory assumptions. Two TAP cases cover deploy and stamp removal.
