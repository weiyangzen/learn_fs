# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/spt.c

Purpose: provides Sunrise Point PMC data for Skylake/Kaby Lake-era platforms and a special init path to redirect Coffee Lake-like systems to Cannon Lake PCH mapping when the SPT PMC PCI ID is absent.

Important APIs/types/functions: `spt_pll_map`, `spt_mphy_map`, `spt_pfear_map`, `ext_spt_pfear_map`, and `spt_ltr_show_map` feed `spt_reg_map`. `spt_core_init()` checks for `SPT_PMC_PCI_DEVICE_ID` with `pci_dev_present()` and chooses either SPT generic init or CNP generic init. `spt_pmc_dev` exports the platform descriptor.

Control flow: CPU match in `core.c` selects `spt_pmc_dev`; custom init detects whether actual PCH is SPT. If not, it calls `generic_core_init()` with `cnp_pmc_dev` to handle Coffee Lake cases where CPU ID resembles Kaby Lake but PCH registers are CNP-compatible.

State and persistence: all maps and PCI ID table are static. Runtime MMIO state is managed by `core.c`. SPT exposes MPHY/PLL paths that use PMC XRAM message registers in `core.c`.

Dependencies and integration points: depends on `core.h`, PCI device matching, and `cnp_pmc_dev`. Debugfs consumers include PPFEAR, LTR, MPHY power gating, PLL status, and package C-state.

Risks: fallback detection hinges on presence of one PCI ID; unusual firmware hiding could select the wrong regmap. MPHY/PLL debugfs reads depend on `PMC_READ_DISABLE` being clear; otherwise users get access-denied output. SPT LTR ordering affects manual `ltr_ignore` indices.

Test signals: on SPT hardware, `pll_status` and `mphy_core_lanes_power_gating_status` should exist if read is allowed. Coffee Lake-like systems should select CNP behavior. Build/link ensures `cnp_pmc_dev` reference resolves.
