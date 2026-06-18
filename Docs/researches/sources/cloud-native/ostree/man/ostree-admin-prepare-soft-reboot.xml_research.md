# sources/cloud-native/ostree/man/ostree-admin-prepare-soft-reboot.xml

Purpose: documents `ostree admin prepare-soft-reboot`, which prepares or clears a deployment target for systemd soft reboot.

Important APIs/types: required deployment `INDEX` except reset mode; options `--reboot` and `--reset`; see-also `systemd-soft-reboot.service(8)`.

Control flow: validates the target index is not the currently booted deployment, mounts `/run/nextroot`, may clear staged deployments when needed, optionally initiates soft reboot, or clears pending soft reboot state with `--reset`.

State and persistence: writes transient runtime mount/nextroot state and may clear staged deployment state.

Dependencies and integration: depends on `open_tree` support indicated by configure soft-reboot checks, systemd soft reboot, deployment indexing, and staged deployment state.

Risks and test signals: risks include kernel/initramfs mismatch, active staged deployment interactions, and stale `/run/nextroot`. Signals are systemd soft-reboot tests and reset/reboot option coverage.
