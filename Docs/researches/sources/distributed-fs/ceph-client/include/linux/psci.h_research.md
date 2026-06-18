# sources/distributed-fs/ceph-client/include/linux/psci.h

Purpose: declares the ARM PSCI firmware interface used for CPU power management, suspend, hotplug, OS-initiated mode, and firmware discovery through device tree or ACPI.

Important APIs and types: power-state type constants distinguish standby and power-down. Functions include `psci_tos_resident_on()`, `psci_cpu_suspend_enter()`, `psci_power_state_is_valid()`, `psci_set_osi_mode()`, and `psci_has_osi_support()`. `struct psci_operations` holds firmware call callbacks for version, CPU suspend/off/on, migrate, affinity info, and migrate info type. `struct psci_0_1_function_ids` stores legacy function IDs. Init hooks cover DT and ACPI, with ACPI HVC discovery helpers.

Control flow: platform init discovers PSCI via DT or ACPI, fills `psci_ops`, then CPU hotplug/idle/suspend paths call those operations to transition cores or query affinity. OSI mode can be enabled when firmware supports OS-initiated coordination.

State and persistence: global `psci_ops` and discovered function IDs are runtime firmware interface state. CPU power state is hardware/firmware state, not persisted by this header.

Dependencies and integration points: depends on ARM SMCCC, init ordering, CPU idle/hotplug/suspend code, ACPI, DT, and secure firmware. It bridges generic kernel power management to platform firmware.

Risks and test signals: risks include invalid power-state encodings, wrong conduit selection, ACPI/DT discovery mismatch, firmware returning unexpected errors, and OSI mode coordination bugs. Test CPU on/off, suspend states, ACPI and DT boot paths, HVC/SMC conduits, and invalid state rejection.
