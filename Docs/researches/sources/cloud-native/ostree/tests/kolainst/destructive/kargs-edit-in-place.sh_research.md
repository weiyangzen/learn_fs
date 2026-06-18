<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/kargs-edit-in-place.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/kargs-edit-in-place.sh

Purpose: verifies `ostree admin kargs edit-in-place --append-if-missing` changes bootloader entries and survives reboot.

Important APIs/functions: uses `rpm-ostree kargs --append`, `ostree admin kargs edit-in-place`, loader entry content assertions, and autopkgtest reboot.

Control flow/state: first phase stages/appends a dummy karg through rpm-ostree, edits the loader entry in place with `testarg`, asserts the loader entry contains it, and reboots. Second phase checks both kargs in `/proc/cmdline`.

Dependencies/integration: requires sudo/root, bootloader entries under `/boot/loader/entries`, rpm-ostree, and reboot harness.

Risks/test signals: destructive to kernel args and boot entries. Signals are loader-entry text before reboot and `/proc/cmdline` after reboot.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/kargs-edit-in-place.sh -->
