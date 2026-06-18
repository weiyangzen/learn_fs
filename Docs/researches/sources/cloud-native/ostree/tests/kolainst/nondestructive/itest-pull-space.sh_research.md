<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull-space.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull-space.sh

Purpose: tests `min-free-space-percent` and `min-free-space-size` enforcement for object pulls and static-delta application.

Important APIs/functions: creates a 20MiB ext4 loopback filesystem, initializes bare-user repos with `fsync=false`, sets repo config free-space thresholds, runs `pull-local`, `pull-local --commit-metadata-only`, `static-delta generate --empty`, and `static-delta apply-offline`.

Control flow/state: first expects pull failure from default percent threshold, then size threshold failure and success, then verifies metadata-only writes can bypass low content free-space. It creates two repos and a 2MB file delta, fails applying with 14MB minimum, then lowers to 1MB and succeeds.

Dependencies/integration: requires loop devices, ext4 mkfs, host `/ostree/repo`, and static-delta support.

Risks/test signals: exact free-space values are tied to filesystem overhead. Signals are expected error strings `min-free-space-percent`/`min-free-space-size` and success after threshold reduction.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull-space.sh -->
