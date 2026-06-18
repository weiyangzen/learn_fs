<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/boot-automount.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/boot-automount.sh

Purpose: verifies staged deployment finalization keeps `/boot` mounted when `/boot` is managed by a short-idle systemd automount.

Important APIs/functions: uses `AUTOPKGTEST_REBOOT_MARK` phases, `systemctl`, `ostree admin deploy --stage`, `rpmostree_query_json`, and journal monotonic timestamps.

Control flow/state: phase 1 installs/enables `boot.automount`, unmounts `/boot`, starts the automount, stages a deployment with a dummy karg, checks finalize and hold services are active and `/boot` remains mounted after timeout, then reboots. Phase 2 verifies staged deployment finalized, karg is on `/proc/cmdline`, services succeeded, and hold service stopped before boot unmounting.

Dependencies/integration: requires root, systemd automounts, rpm-ostree/OSTree, journalctl, jq, and autopkgtest reboot.

Risks/test signals: timing-sensitive around automount idle timeout and journal ordering. Signals are service states, absence of staged marker, cmdline karg, and ordered timestamps.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/boot-automount.sh -->
