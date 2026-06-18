<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/soft-reboot.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/soft-reboot.sh

Purpose: destructive multi-phase test for systemd soft reboot behavior with and without OSTree `prepare-soft-reboot`.

Important APIs/functions: `assert_soft_reboot_count()`, `assert_status_jq()`, `ostree admin prepare-soft-reboot`, `--reset`, `--reboot`, `systemctl soft-reboot`, `systemctl reboot`, staged deploys, and rpm-ostree kernel-state changes.

Control flow/state: verifies `/sysroot` read-only on each boot, remounts writable for test commits, first tests bare `systemctl soft-reboot` without `/run/nextroot`, then stages `soft-reboot-test`, prepares soft reboot and checks status text/JSON plus `/run/nextroot`. Later phases verify booted commit/content, soft reboot into rollback, reset idempotence, staged-versus-soft-reboot interactions, default soft reboot via mounted nextroot, and rejection when initramfs or kargs change kernel state.

Dependencies/integration: requires systemd soft reboot support, autopkgtest soft-reboot helpers, rpm-ostree, jq, writable sysroot, and booted OSTree host.

Risks/test signals: very stateful and sensitive to host systemd behavior. Signals include `SoftRebootsCount`, mountpoints `/var` and `/boot`, deployment JSON flags, content files, `/run/ostree/nextroot-booted`, and expected `different kernel state` errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/soft-reboot.sh -->
