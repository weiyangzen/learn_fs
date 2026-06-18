<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/auto-prune.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/auto-prune.sh

Purpose: destructive boot filesystem ENOSPC regression test for OSTree early bootcsum auto-pruning.

Important APIs/functions: local helpers track steps, journal cursors, journal grep/non-grep, bootcsum directory counts, and bootfs space consumption/restoration. It creates modified kernel commits `modkernel1/2/3`.

Control flow/state: may replace `/boot` with a loopback ext4 image large enough for the scenario, fills `/boot` with a big file, stages/rebases deployments, runs `ostree admin finalize-staged` with and without `OSTREE_SYSROOT_OPTS=no-early-prune`, and validates bootloader hash changes. Later phases test ext4 reserved space estimation and many-small-DTB block accounting.

Dependencies/integration: requires root, writable sysroot/repo, rpm-ostree, ext4 semantics, journalctl, loop mounts, and host kernel/initramfs paths.

Risks/test signals: highly destructive to `/boot` and assumes FCOS ext4. Strong signals are ENOSPC failures without auto-prune, journal messages about two-step bootloader updates, and expected bootcsum directory counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/auto-prune.sh -->
