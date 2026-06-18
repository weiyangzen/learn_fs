# sources/cloud-native/ostree/tests/test-admin-deploy-grub2.sh

Purpose: runs the shared admin deployment suite with a grub2 bootloader configuration and ostree-grub-generator enabled.

Important APIs/functions: sources `libtest.sh`, calls `setup_os_repository "archive" "grub2 ostree-grub-generator"`, sets `extra_admin_tests=0`, and sources `admin-test.sh`.

Control flow: this wrapper delegates almost all behavior to `admin-test.sh`, which performs init-fs, deploy, status, rollback, undeploy, `/etc` merge, and bootloader validation checks.

State/persistence: creates a sysroot with grub2 config and all deployment artifacts exercised by the shared suite. Dependencies include grub2 fixture support and `bootloader-entries-crosscheck.py`.

Integration/risk/test signals: proves the generic admin suite works for grub2-specific bootloader integration. Risks are inherited from `admin-test.sh` plus grub2 file layout drift. TAP plan comes from the shared suite.
