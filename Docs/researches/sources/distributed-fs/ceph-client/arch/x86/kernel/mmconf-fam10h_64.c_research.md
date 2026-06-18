# sources/distributed-fs/ceph-client/arch/x86/kernel/mmconf-fam10h_64.c

Purpose: Detects and enables PCI MMCONFIG space on AMD Family 10h systems, especially platforms whose firmware leaves MMCONFIG disabled or needs a safe high-MMIO base selected.

Important APIs/types/functions: exposes `fam10h_check_enable_mmcfg()` and `check_enable_amd_mmconf_dmi()`. Internal state is `fam10h_pci_mmconf_base`. Important helpers are `get_fam10h_pci_mmconf_base()`, `cmp_range()`, and DMI callback `set_check_enable_amd_mmconf()`.

Control flow: DMI can set `PCI_CHECK_ENABLE_AMD_MMCONF` for affected systems. The check function reads `MSR_FAM10H_MMIO_CONF_BASE`; if already enabled and trustworthy, it records or validates the base. Otherwise it probes hostbridge PCI IDs, reads top-of-memory and high-MMIO window registers, chooses a base above TOM2 while avoiding reserved HT ranges near `0xfd-0xff << 32`, searches around existing high-MMIO ranges for a valid window, then programs the MSR for one 256-bus segment.

State and persistence: chosen base persists in `fam10h_pci_mmconf_base` for the running kernel and is written to the CPU MSR. The PCI probe flag may be cleared if no valid base can be found.

Dependencies and integration points: depends on early PCI config access, AMD MSRs, ACPI PCI state, DMI matching, PCI MMCONFIG architecture init, PCI probe flags, high-MMIO resource interpretation, and sort/range helpers.

Risks: base selection must not collide with RAM, HyperTransport reserved ranges, or existing high-MMIO windows. Trust policy differs when ACPI is enabled versus disabled. Programming inconsistent bases across CPUs would break PCI config access, so the first discovered base is reused.

Test signals: test on AMD Family 10h systems with MMCONFIG enabled, disabled, ACPI off, and DMI-triggered Sun systems. Verify programmed MSR base, 256-bus range, no overlap with high-MMIO windows, and successful extended PCI config reads after enablement.
