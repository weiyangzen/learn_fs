# sources/distributed-fs/ceph-client/drivers/mailbox/riscv-sbi-mpxy-mbox.c

Purpose: implements the RISC-V SBI Message Proxy mailbox controller. It discovers SBI MPXY channels, exposes RPMI-compatible channels to Linux mailbox clients, manages per-CPU SBI shared memory, and optionally wires channel notifications through platform MSIs.

Important APIs/types/functions: SBI attribute structures model standard MPXY, MSI, RPMI, channel-id, and notification data. `struct mpxy_local` is per-CPU shared memory state. `struct mpxy_mbox_channel` and `struct mpxy_mbox` hold discovered channel metadata, notification buffers, MSI mappings, and the mailbox controller. Helpers wrap SBI calls for channel IDs, attributes, message send, notifications, and shared-memory setup.

Control flow: probe checks SBI version and MPXY extension, gets shared-memory size, registers a CPU hotplug state to set per-CPU shared memory, discovers channels, reads standard and RPMI attributes, allocates notification buffers, computes max transfer sizes, configures MSI indexes for notification-capable channels, initializes platform MSI IRQs if needed, and registers a firmware-xlate mailbox controller. Send handles RPMI get/set attribute and request/response message types by issuing SBI calls through this CPU's shared memory. `peek_data` drains notification events and converts RPMI events into mailbox RX callbacks. Startup enables per-channel MSI and event state; shutdown disables them.

State and persistence: per-CPU shared memory remains active across CPU power-down by design. Channel attributes cache firmware state and track MSI/event enablement and `started`.

Dependencies and integration: depends on SBI MPXY extension, RPMI mailbox message ABI, CPU hotplug, RISC-V IMSIC/platform MSI domains, OF or ACPI match, and generic mailbox fwnode xlate.

Risks: shared-memory operations are CPU-local and guarded with `get_cpu`; misuse outside that pattern can corrupt SBI buffers. Notification parsing bounds are delicate. MSI domain availability can defer probe.

Test signals: SBI error mapping, channel discovery with multiple pages of IDs, RPMI send-with/without-response, notification draining by MSI and polling, CPU hotplug shared-memory setup, and OF/ACPI xlate.
