<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/root-transient-ro.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/root-transient-ro.sh

Purpose: verifies `prepare-root.conf` `[root] transient-ro = true` keeps `/` read-only while allowing writable remounts only in isolated namespaces.

Important APIs/functions: modifies `/etc/ostree/prepare-root.conf`, runs `rpm-ostree initramfs-etc --track`, checks `test -w /`, uses `unshare -m` remount with `LIBMOUNT_FORCE_MOUNT2=always`, and reboots.

Control flow/state: first phase masks zincati, copies and edits prepare-root config, tracks it into initramfs, and reboots. Second phase checks `/` is not writable in the main namespace, creates `/new-dir-in-root` through a mount namespace remount, and verifies main namespace remains read-only.

Dependencies/integration: requires rpm-ostree initramfs-etc, OSTree prepare-root, mount namespaces, and autopkgtest reboot.

Risks/test signals: modifies root/initramfs configuration and may affect later boots. Signals are write tests before/after isolated remount and presence of the new directory.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/root-transient-ro.sh -->
