# sources/distributed-fs/ceph-client/drivers/platform/x86/pmc_atom.c

Purpose: This is the Intel Atom SoC Power Management Controller support code for Bay Trail and Cherry Trail. It maps PMC registers, exports `pmc_atom_read()`, registers debugfs status files, configures PMC wake bits, optionally provides `pm_power_off`, registers PMC platform clocks, and hooks s2idle diagnostics.

Important APIs, types, and functions: `struct pmc_dev` holds the global PMC MMIO mapping, register map, debugfs directory, and init flag. `struct pmc_reg_map` and `struct pmc_bit_map` define status/disable/pss bit names for Bay Trail and Cherry Trail. `pmc_atom_read()` is the exported read helper. `pmc_power_off()` writes ACPI PM1 control S5 bits. `pmc_dbgfs_register()` creates `dev_state`, `pss_state`, and `sleep_state`. `pmc_s2idle_check()` reports devices/clocks blocking low-power idle.

Control flow: `pmc_atom_init()` scans all PCI devices for VLV/CHT PMC IDs instead of binding a PCI driver, because another driver owns the multifunction device. `pmc_setup_dev()` reads ACPI/PMC base addresses from PCI config, maps PMC MMIO, installs poweroff if possible, writes `PMC_S0IX_WAKE_EN`, creates debugfs, registers `clk-pmc-atom` platform data with DMI critical-clock quirks, registers s2idle checks, and marks the singleton initialized.

State and persistence: State is a singleton `pmc_device` plus `acpi_base_addr` and `pmc_clk_is_critical`. Register writes change platform wake and clock behavior. Debugfs output and s2idle checks are live views of PMC registers. There is no module exit path shown because initialization is by `device_initcall`.

Dependencies and integration points: Dependencies include PCI, ACPI, debugfs, suspend/LPS0 hooks, DMI, the `clk-pmc-atom` platform clock driver, and Siemens DMI parsing helpers. It interacts with `pm_power_off` and can affect system shutdown behavior.

Risks and edge cases: The singleton assumes one PMC. It returns the clock-registration error even after successfully mapping and initializing the PMC, so a clock failure can make init report failure despite partial side effects. There is no explicit unmap/debugfs cleanup in this initcall-style driver. DMI critical-clock logic mutates global `pmc_clk_is_critical`, including Siemens-specific negative cases. Incorrect false-positive masks could over-report s2idle blockers.

Test signals: Validate debugfs files on Bay Trail and Cherry Trail, `pmc_atom_read()` before/after init, poweroff path with nonzero ACPI base, clock registration and critical-clock DMI quirks, and s2idle diagnostics on systems with known D0 blockers. PCI scan should verify only supported device IDs initialize the driver.
