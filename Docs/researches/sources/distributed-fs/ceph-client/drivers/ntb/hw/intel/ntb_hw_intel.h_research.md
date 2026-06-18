# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_intel.h

Purpose: Defines shared Intel NTB device IDs, common NTB control/link macros, unsafe-access flags, BAR masks, common register descriptor structs, the central `intel_ntb_dev` runtime state, and PCI generation classifier helpers.

Important APIs, types, and functions: Device ID macros cover Gen1 JSF/SNB/IVT/HSX/BDX primary/secondary/B2B IDs, Gen3 SKX, Gen4 ICX, Gen5 GNR, and Gen6 DMR. `NTB_CTL_*` and `NTB_LNK_STA_*` abstract common control and link status bits. `struct intel_ntb_reg`, `intel_ntb_alt_reg`, and `intel_ntb_xlat_reg` describe generation-specific register layouts consumed by common code. `struct intel_b2b_addr` stores B2B BAR translation defaults. `struct intel_ntb_vec` and `struct intel_ntb_dev` hold IRQ and per-device state. Inline helpers classify PCI devices by generation.

Control flow: No direct flow, but all Intel C files use `intel_ntb_dev` and classifier helpers to choose generation init paths and NTB ops.

State and persistence behavior: `intel_ntb_dev` is the central in-memory state for the Intel driver: NTB core handle, B2B placement, BAR split flag, cached NTB control/link state, resource counts, DB masks, IRQ vector arrays, register layout pointers, self/peer MMIO mappings, peer physical address, heartbeat timestamp/work, errata/unsafe flags, debugfs state, and Gen4 `dev_up`.

Dependencies and integration points: Includes Linux NTB, PCI, and non-atomic lo/hi 64-bit I/O support. It is shared by gen1/gen3/gen4 headers and implementations. The PCI classifier helpers integrate with the main probe logic and debugfs dispatch.

Risks and edge cases: The generation classifier helpers are hardcoded switch/if lists, so new PCI IDs must be added both here and in the PCI ID table. `intel_ntb_reg` uses a flexible `mw_bar[]` member and is instantiated with static trailing initializers; any access depends on correct `mw_count`. `db_size` sometimes represents register stride/size imperfectly for newer hardware, so users should rely on generation DB helpers.

Test signals: Full Intel driver build, probe dispatch for every PCI ID, classifier unit-style checks if available, and debugfs/register sanity tests across generations validate this shared contract.
