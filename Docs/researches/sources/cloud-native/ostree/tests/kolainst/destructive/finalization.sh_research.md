<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/finalization.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/finalization.sh

Purpose: tests staged deployment finalization locking, unlocking, and boot-time finalization behavior.

Important APIs/functions: uses `ostree admin deploy --lock-finalization`, `ostree admin lock-finalization --unlock`, `ostree admin status`, journal checks, and `rpm-ostree status --json`.

Control flow/state: first boot disables GPG verification and zincati, creates `staged-deploy`, deploys with finalization locked, and reboots. Second boot verifies it did not boot the new commit and logs say `Not finalizing`, then redeploys locked, unlocks, and reboots. Third boot verifies the new commit booted and previous finalize logs include `Bootloader updated`.

Dependencies/integration: requires writable sysroot, systemd, rpm-ostree, journalctl, jq, and autopkgtest reboot.

Risks/test signals: destructive staged state can persist on failure. Strong signals are finalization locked status text, booted checksum comparisons, and finalize journal messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/finalization.sh -->
