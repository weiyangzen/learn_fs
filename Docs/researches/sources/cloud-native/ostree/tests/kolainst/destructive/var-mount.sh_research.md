<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/var-mount.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/var-mount.sh

Purpose: regression test for explicit `/var` bind mount from deployment var path through `/etc/fstab`.

Important APIs/functions: uses `ostree admin status` to infer stateroot, appends an fstab bind mount, and verifies `var.mount`.

Control flow/state: first phase writes `/var/somenewfile`, appends `/sysroot/ostree/deploy/<stateroot>/var /var none bind 0 0` to `/etc/fstab`, and reboots. Second phase checks `systemctl status var.mount` and that the file remains in `/var`.

Dependencies/integration: requires reboot harness, systemd fstab generator, and OSTree deployment layout.

Risks/test signals: mutates `/etc/fstab` and assumes status parsing of the booted line. Signals are active `var.mount` and preserved file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/var-mount.sh -->
