<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/unlock-transient.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/unlock-transient.sh

Purpose: verifies `ostree admin unlock --transient` creates transient writable `/usr` overlay state that does not persist across reboot.

Important APIs/functions: computes deployment backing dir from rpm-ostree JSON, runs `ostree admin unlock --transient`, uses `unshare -m` to remount `/usr` writable, and checks backing upperdir.

Control flow/state: first phase confirms `/usr/share/writable-usr-test` absent, unlocks transiently, verifies outer namespace still cannot write, writes through an isolated namespace, verifies file exists via overlay and in the backing `usr-transient/upper`, then reboots. Second phase verifies the file did not persist, unlocks again, and rechecks absence.

Dependencies/integration: requires root, mount namespaces, rpm-ostree JSON, writable sysroot, and reboot harness.

Risks/test signals: path construction depends on deployment serial/checksum layout. Signals are write failures in outer namespace, file existence in backing upperdir, and absence after reboot.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/unlock-transient.sh -->
