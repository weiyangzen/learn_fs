# sources/cloud-native/ostree/tests/test-admin-deploy-none.sh

Purpose: runs shared admin deploy tests with `sysroot.bootloader none` and then verifies BLS snippet generation despite an incidental grub2 directory.

Important APIs/functions: `setup_os_repository "archive" "sysroot.bootloader none"`, `admin-test.sh`, `pull-local`, `ostree admin deploy`, and file assertions for BLS, kernel, hmac, and initramfs.

Control flow: delegates the large deployment matrix to `admin-test.sh`, resets the sysroot, creates a fake `boot/grub2/grub.cfg`, deploys with bootloader `none`, and asserts OSTree updates BLS snippets and boot assets rather than invoking grub2 behavior.

State/persistence: writes bootloader config snippets and boot asset directories in a bootloader-none sysroot.

Integration/risk/test signals: protects a workaround for systems where grub2 files exist but OSTree bootloader management is disabled. Risks are inherited shared-suite breadth and exact output message matching.
