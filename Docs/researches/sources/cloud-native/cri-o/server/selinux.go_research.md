# sources/cloud-native/cri-o/server/selinux.go

Purpose: derives alternate SELinux process labels for KVM-isolated and init/systemd-style containers.

Important APIs and functions: `KVMLabel`, `InitLabel`, and `swapSELinuxLabel`.

Control flow: empty input label returns empty output for SELinux-disabled environments. Otherwise it obtains a reference KVM or init container label, releases it, parses both contexts, replaces the destination `type` with the reference label's `type`, and returns the modified context.

State and persistence: no filesystem mutation; interacts with SELinux label allocation/release state through the SELinux library.

Dependencies and integration: used by sandbox/container spec setup when runtime type requires KVM or init labels.

Risks: errors parsing either SELinux context abort label generation. Only the `type` field is swapped; other context fields remain from the original container label.

Test signals: no direct tests in this subset.
