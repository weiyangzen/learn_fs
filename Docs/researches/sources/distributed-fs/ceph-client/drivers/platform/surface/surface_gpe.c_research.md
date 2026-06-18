# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_gpe.c

Purpose: Creates a small DMI-driven platform device that enables lid wakeup on Intel-based Microsoft Surface systems whose ACPI lid wake path depends on a specific GPE number.

Important APIs and types: `dmi_lid_device_table` maps Surface models/SKUs to software-node `gpe` properties. `struct surface_lid_device` stores the selected GPE. `surface_lid_enable_wakeup()` wraps `acpi_set_gpe_wake_mask()`. Probe calls `acpi_mark_gpe_for_wake()`, `acpi_enable_gpe()`, and disables the wake mask until suspend.

Control flow: Module init finds the first DMI match, registers the `surface_gpe` platform driver, creates a software fwnode containing the GPE property, allocates a matching platform device, and adds it. Probe reads the property, allocates state, marks/enables the GPE, and leaves wake disabled while running. Suspend enables the GPE wake mask; resume disables it. Exit unregisters the platform device and driver and removes the software node.

State and persistence: Runtime state is just the GPE number in devres-managed memory plus the global platform-device pointer. The ACPI wake mark and enabled GPE are firmware/kernel ACPI state and are restored in remove by disabling wake and the GPE.

Dependencies and integration points: Uses ACPI GPE APIs, DMI matching, platform-device creation, and software fwnodes. The module alias is broad for Surface systems and the DMI table narrows actual binding.

Risks: GPE numbers are hard-coded from DSDT inspection, so firmware revisions or new SKUs can need table updates. A wrong GPE can break lid wake or enable unrelated wake sources. Failure after `acpi_enable_gpe()` is cleaned only on the final wake-disable error path, so new error paths must preserve cleanup.

Test signals: DMI autoload on listed Surface models; successful probe logs; `/proc/acpi/wakeup` or ACPI debug showing correct wake mask changes; lid-open wake from suspend; no wake enable on unsupported Surface/AMD variants; module unload disabling the GPE.
