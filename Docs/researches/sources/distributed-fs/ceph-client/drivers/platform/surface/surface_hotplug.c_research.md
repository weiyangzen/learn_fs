# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_hotplug.c

Purpose: Provides out-of-band hot-plug signaling for Surface Book dGPU/base hardware, especially when the PCIe device is in D3cold and cannot generate normal PCIe hot-plug events.

Important APIs and types: ACPI GPIO mappings expose base presence, device power, and device presence interrupt/status GPIOs. `_DSM` GUID `5515a847-ed55-4b27-8352-cd320e10360a` accepts per-IRQ notifications. `struct shps_device` stores per-IRQ mutexes, GPIO descriptors, and Linux IRQ numbers. Key functions are `shps_setup_irq()`, `shps_handle_irq()`, and `shps_dsm_notify_irq()`.

Control flow: Probe filters out ACPI `MSHW0153` instances that have no GPIOs, adds driver GPIO mappings, allocates state, initializes IRQ slots, and conditionally sets up each IRQ only if the corresponding DSM function exists. Each threaded IRQ identifies its type, reads the status GPIO, calls the DSM function with that value, and lets ACPI emit device-check notifications for downstream PCIe hotplug. Probe also sends initial DSM notifications for present IRQs to synchronize firmware state.

State and persistence: The driver keeps no persistent policy; it mirrors current GPIO states into ACPI via DSM calls. IRQ registrations and GPIO descriptors are devm-managed; remove disables active IRQs and destroys locks.

Dependencies and integration points: Integrates ACPI, GPIO descriptor mapping, IRQ threading, and platform-driver matching on `MSHW0153`. It is indirectly coupled to ACPI firmware and PCIe hotplug handling that consumes the resulting ACPI notifications.

Risks: DSM function numbering and `enum shps_irq_type` order must remain synchronized. GPIO mapping indexes are firmware-contract sensitive. `surface_hotplug_remove()` is called on partial probe failures, so initialization order of mutexes/IRQ sentinel values matters. Missing DSM functions are valid on Surface Book 3 and must not be treated as fatal.

Test signals: Probe on Surface Book 2/3; IRQ setup count matching DSM availability; attach/detach or dGPU power transitions causing DSM debug logs and PCIe hotplug rescans; no binding on Surface Laptop 3 `MSHW0153`; clean module unload with IRQs disabled.
