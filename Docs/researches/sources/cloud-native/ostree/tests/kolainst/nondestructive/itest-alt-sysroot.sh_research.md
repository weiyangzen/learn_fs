<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-alt-sysroot.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-alt-sysroot.sh

Purpose: verifies `ostree admin status --sysroot` rejects a sysroot whose `/boot` is vfat.

Important APIs/functions: re-execs itself in a private mount namespace if needed, creates a 512M vfat loop image, runs `ostree admin init-fs -E 1 sysroot`, mounts image at `sysroot/boot`, and expects status failure.

Control flow/state: all state is in a tempdir under `/var/tmp`; cleanup trap removes tempdir, and the script manually unmounts `sysroot/boot` before fatal paths.

Dependencies/integration: requires root, loop mounting, `mkfs.vfat`, OSTree admin commands, and `libinsttest.sh`.

Risks/test signals: missing vfat tooling or loop capability will fail setup. Main signal is error text `/boot cannot currently be a vfat filesystem`.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-alt-sysroot.sh -->
