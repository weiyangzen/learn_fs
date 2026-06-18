<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-deploy-selinux.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/itest-deploy-selinux.sh

Purpose: verifies `/etc` merge and boot artifact labeling during deployments on SELinux systems.

Important APIs/functions: deploys host commit with current kargs, compares `ls -Z` labels for selected `/etc` files/directories, creates a `test-label` commit with modified initramfs and `--selinux-policy`, deploys it, and validates `/boot/ostree` kernel/initramfs labels.

Control flow/state: creates and undeploys temporary deployments, uses `/ostree/repo/tmp` checkout, deletes/replaces boot assets, and removes `test-label` ref at the end.

Dependencies/integration: requires SELinux labels, writable sysroot, `ls -Z`, rpm-ostree/ostree, and boot layout.

Risks/test signals: skipped files are tolerated, but exact context expectations (`boot_t`) are Fedora/SELinux-policy dependent. Signals are matching labels and successful undeploy cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/itest-deploy-selinux.sh -->
