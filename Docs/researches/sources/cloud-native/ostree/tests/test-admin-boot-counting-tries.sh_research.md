# sources/cloud-native/ostree/tests/test-admin-boot-counting-tries.sh

Purpose: verifies sysroot configuration `sysroot.boot-counting-tries` is honored in generated bootloader entry names.

Important APIs/functions: sources `libtest.sh`, calls `setup_os_repository "archive" "syslinux"`, uses `ostree config set/get`, `pull-local`, `rev-parse`, and `ostree admin deploy`.

Control flow: initializes a syslinux sysroot, sets boot-counting tries to `3`, confirms the config value, pulls the runtime ref, deploys it, and asserts the only BLS entry is named `ostree-1+3.conf`.

State/persistence: mutates `sysroot/ostree/repo/config`, imports commit objects, and writes `sysroot/boot/loader/entries`. Dependencies are the admin test harness and syslinux boot setup.

Integration/risk/test signals: protects boot-counting naming consumed by bootloaders/systemd-bless-boot flows. Risk is exact file-name assumptions when boot counting format changes. TAP uses two `tap_ok` calls and `tap_end`.
