# sources/cloud-native/ostree/tests/test-admin-deploy-2.sh

Purpose: regression suite for deployment cleanup and boot object lifecycle after repeated upgrades and deploys.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `remote add`, `admin upgrade`, `os_repository_new_commit`, and filesystem assertions against `/boot/ostree`.

Control flow: deploys an initial runtime with kernel arguments, creates new commits, upgrades twice to rotate old deployments, verifies boot checksums and deployment directories, and checks that boot assets for no-longer-referenced deployments are collected while active ones remain.

State/persistence: writes sysroot deployments, bootloader entries, boot object directories, remote config, and test commits. It relies on exported `rev` and `bootcsum` from `libtest.sh`.

Integration/risk/test signals: validates admin deployment garbage collection across update generations. Risks include boot checksum coupling and assumptions about deployment index rotation. Eight TAP plan entries report command and layout success.
