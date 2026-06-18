# sources/distributed-fs/ceph-client/drivers/firmware/psci/psci.c

## Purpose
`psci.c` is the kernel's ARM PSCI firmware frontend. It discovers PSCI via device tree or ACPI, selects the SMCCC conduit (`SMC` or `HVC`), fills the global `psci_ops` dispatch table, and wires PSCI into CPU hotplug, CPU idle, system suspend, restart, poweroff, hibernation, SMCCC discovery, and KVM hypervisor-service discovery.

## Important APIs, Types, And Functions
- Global state: `struct psci_operations psci_ops`, `invoke_psci_fn`, `psci_conduit`, `resident_cpu`, `psci_cpu_suspend_feature`, `psci_system_reset2_supported`, and `psci_system_off2_hibernate_supported`.
- Discovery entry points: `psci_dt_init()` matches `arm,psci`, `arm,psci-0.2`, and `arm,psci-1.0`; `psci_acpi_init()` uses ACPI flags to choose HVC/SMC and then probes PSCI 0.2+.
- PSCI operation implementations: `psci_0_1_cpu_suspend/off/on/migrate`, `psci_0_2_cpu_suspend/off/on/migrate`, `psci_affinity_info()`, `psci_migrate_info_type()`, `psci_migrate_info_up_cpu()`.
- Integration APIs exported or visible to other firmware/power code: `psci_tos_resident_on()`, `get_psci_0_1_function_ids()`, `psci_set_osi_mode()`, `psci_has_osi_support()`, `psci_power_state_is_valid()`, and `psci_cpu_suspend_enter()`.
- System lifecycle hooks: `psci_sys_reset()`, `psci_sys_poweroff()`, optional `psci_sys_hibernate()`, and the `platform_suspend_ops` using `SYSTEM_SUSPEND`.
- Optional debug surface: debugfs file `psci` reports PSCI/SMCCC versions, optional function availability, OSI support, state-ID format, and Trusted OS residency.

## Control Flow
Initialization starts from DT or ACPI, calls `set_conduit()` to bind `invoke_psci_fn` to `arm_smccc_smc()` or `arm_smccc_hvc()`, then calls `psci_probe()` for PSCI 0.2+. `psci_probe()` reads `PSCI_VERSION`, rejects conflicting pre-0.2 firmware, installs standard v0.2 operation IDs, registers reset and poweroff handlers, checks Trusted OS migration residency, and for PSCI 1.0+ initializes SMCCC discovery, CPU suspend feature bits, system suspend, `SYSTEM_RESET2`, `SYSTEM_OFF2`, and KVM hypervisor service discovery. PSCI 0.1 uses DT-provided function IDs and only fills operations whose properties exist.

Runtime calls funnel through `invoke_psci_fn()` and then map PSCI negative status codes to Linux errno via `psci_to_linux_errno()`. CPU idle either invokes PSCI directly for retention states or uses `cpu_suspend()` and `psci_suspend_finisher()` for context-losing states. Restart chooses `SYSTEM_RESET2` for warm/soft reboot when supported and otherwise uses `SYSTEM_RESET`; poweroff always uses PSCI 0.2 `SYSTEM_OFF`.

## State And Persistence
State is kernel-resident and initialized early: the selected conduit, PSCI function table, feature bits, and Trusted OS resident logical CPU are retained for the lifetime of the boot. There is no persistent storage, but the driver can change firmware suspend mode with `SET_SUSPEND_MODE` and can enter firmware-controlled reset/off/suspend states. `pm_power_off` and restart notifier registration make PSCI the active lifecycle backend.

## Dependencies And Integration Points
The file depends on SMCCC call helpers, OF/ACPI discovery, CPU hotplug and idle infrastructure, suspend/hibernate infrastructure, restart notifiers, debugfs, and architecture resume symbols. It also seeds `arm_smccc_version_init()` for later SMCCC users and invokes `kvm_init_hyp_services()` when PSCI/SMCCC discovery is new enough.

## Risks
Incorrect conduit selection breaks every PSCI call. PSCI 0.1 depends on firmware-provided DT function IDs and can have partial operation coverage. CPU suspend state validation is keyed off firmware feature bits; mismatched state encodings can produce failed suspend or deeper-than-expected idle. The driver deliberately avoids powering off a CPU hosting a UP Trusted OS, so bad `MIGRATE_INFO_UP_CPU` data can affect hotplug behavior. Reset/poweroff calls do not return on successful firmware action, making failures hard to recover from.

## Test Signals
Boot logs should show PSCI and SMCCC versions and conduit-related probing. Debugfs `psci` should enumerate optional PSCI functions accurately. CPU hotplug, cpuidle, system suspend, hibernation, warm reboot, cold reboot, and poweroff are the main integration tests. `psci_checker.c` provides a late-init stress test when enabled.
