# sources/cloud-native/ostree/tests/test-admin-deploy-bootprefix.sh

Purpose: verifies `sysroot.bootprefix=true` causes generated BLS entries to prefix kernel and initrd paths with `/boot`.

Important APIs/functions: `setup_os_repository`, `ostree config set sysroot.bootprefix true`, `pull-local`, `ostree admin deploy`, and `assert_file_has_content_literal`.

Control flow: builds a syslinux admin test repository, pulls a runtime ref, enables bootprefix in repo config, deploys with a root karg, and inspects `ostree-1.conf` for `linux /boot/ostree/testos-` and `initrd /boot/ostree/testos-`.

State/persistence: changes repo config and writes bootloader snippets. Dependencies are bootloader layout from the admin harness.

Integration/risk/test signals: protects compatibility with bootloaders or layouts requiring `/boot`-prefixed paths. Risk is exact BLS text matching if formatting changes. TAP reports one `bootprefix` case.
