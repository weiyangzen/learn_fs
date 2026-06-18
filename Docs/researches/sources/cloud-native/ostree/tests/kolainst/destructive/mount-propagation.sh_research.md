<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/mount-propagation.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/mount-propagation.sh

Purpose: verifies mounts under `/var` and `/sysroot` propagate correctly into separate mount namespaces and do not leak into deployment var paths.

Important APIs/functions: `get_mount()` uses `nsenter` and `findmnt --json`; `assert_has_mount()`, `assert_not_has_mount()`, and `test_mounts()` inspect root and child namespaces. The script creates tmpfs mounts manually and via `/etc/fstab`.

Control flow/state: first phase creates `/var/foo` and `/sysroot/bar`, starts an `unshare -m` process, mounts tmpfs, tests propagation, writes fstab entries and a `test-mounts.service` ordered after `ostree-remount`, then reboots. Second phase verifies service timing from journal and repeats mount assertions in its namespace.

Dependencies/integration: requires root, mount namespaces, systemd ordering, jq, findmnt, journalctl, and writable sysroot.

Risks/test signals: timing and namespace-sensitive. Strong signals are namespace inequality, mount presence/absence, and monotonic journal ordering around remount and mount units.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/mount-propagation.sh -->
