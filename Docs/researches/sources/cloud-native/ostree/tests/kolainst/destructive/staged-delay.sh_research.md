<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-delay.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/staged-delay.sh

Purpose: verifies delayed `ostree-finalize-staged.service` shutdown still sees `/boot/loader/entries`.

Important APIs/functions: writes a systemd drop-in adding an `ExecStop` shell command, runs `rpm-ostree kargs`, and checks previous boot logs.

Control flow/state: first phase creates `/etc/systemd/system/ostree-finalize-staged.service.d/delay.conf`, reloads systemd, stages a karg change, and reboots. Second phase reads previous boot journal for the success message and service success/deactivation, then checks the karg in `/proc/cmdline`.

Dependencies/integration: requires systemd, rpm-ostree, journalctl, jq, and reboot harness.

Risks/test signals: depends on systemd version-specific success wording. Signals are custom log line, service success pattern, and cmdline karg.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-delay.sh -->
