## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-mobiveil.c

Purpose: Common Mobiveil CSR, address translation window, and link polling helpers used by Mobiveil host-mode drivers.

Important APIs, types, and functions: `mobiveil_pcie_sel_page()` and `mobiveil_pcie_comp_addr()` implement the controller's paged CSR address scheme for offsets at or above `PAGED_ADDR_BNDRY`. `mobiveil_csr_read()` and `mobiveil_csr_write()` wrap size-checked MMIO access and report bad alignment/size. `mobiveil_pcie_link_up()` calls platform `ops->link_up` when present or checks common `LTSSM_STATUS`. `program_ob_windows()` and `program_ib_windows()` program APIO/PPIO address translation windows, extended high registers, type, size mask, AXI/PEX bases, and counters. `mobiveil_bringup_link()` polls link-up using retry constants.

Control flow: shared host init and platform reset recovery call these helpers to program windows and poll link. CSR access selects the register page on every access before touching the composed address.

State and persistence: state is volatile CSR page-select bits, translation window registers, `ob_wins_configured`/`ib_wins_configured` counters in `struct mobiveil_pcie`, and LTSSM status. No persistent state.

Dependencies and integration points: `struct mobiveil_pcie` and register definitions from `pcie-mobiveil.h`, platform device for logging, Linux MMIO and delay APIs, and optional platform-specific PAB ops.

Risks: Page selection is mutable shared hardware state; callers rely on PCI or higher-level serialization. Window overflow only logs and returns void, so host setup can continue with incomplete mappings. Size programming assumes power-of-two sizes because it writes `~(size - 1)`. Misaligned CSR accesses return a PCI BIOS error internally but the read wrapper still returns zero.

Test signals: direct and paged CSR offsets, byte/word/dword access alignment, outbound/inbound window register values for 32/64-bit addresses, max-window overflow logs, platform override link-up, common LTSSM polling timeout, and enumeration with IO/MEM ranges.
