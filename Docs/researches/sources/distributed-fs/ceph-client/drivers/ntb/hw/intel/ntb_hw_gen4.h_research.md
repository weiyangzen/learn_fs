# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen4.h

Purpose: Defines Intel Gen4 through Gen6 NTB register offsets, topology masks, resource counts, link/LTR control bits, revision helpers, and exported Gen4 APIs.

Important APIs, types, and functions: Constants cover ICX revision range, Gen4 BAR-size config offsets, MMIO NTB control, xlat/limit/index, interrupt status/masks/vectors, SPADs, doorbells, LTR registers, link control/status, PPD0/PPD1, slot status, topology masks for ICX and SPR-like devices, DB/SPAD counts, snoop/nosnoop control bits, link-down and force-detect bits, LTR values, and Gen6 PPD0 offset. Prototypes declare `ndev_ntb4_debugfs_read()`, `gen4_init_dev()`, and `intel_ntb4_ops`. Inline helpers `pdev_is_ICX()` and `pdev_is_SPR()` classify Gen4 revisions.

Control flow: The header itself has no flow; its revision helpers and constants drive Gen4 init, link enable/disable, MW setup, and debugfs in `ntb_hw_gen4.c`.

State and persistence behavior: Hardware state addressed here persists in Gen4+ MMIO/config registers. Runtime state is held in shared `intel_ntb_dev`, including the Gen4-only `dev_up` field declared in `ntb_hw_intel.h`.

Dependencies and integration points: Includes `ntb_hw_intel.h` and is included by the main Intel file and Gen4 implementation. It bridges PCI ID generation helpers from `ntb_hw_intel.h` to revision-specific ICX/SPR behavior.

Risks and edge cases: The header has duplicate declarations for `ndev_ntb4_debugfs_read()`. `NTB_CTL_E2I_BAR45_NOSNOO` appears to be missing the final `P` in the macro name, which can trip future users even though current code does not use that macro. Revision-based `pdev_is_SPR()` treats any Gen4 revision above ICX max as SPR-like, so future Gen4 revisions inherit SPR topology parsing unless split out.

Test signals: Compile coverage, Gen4 revision matrix tests, static checks for unused/misspelled macros, and hardware readback of link/LTR/xlat/vector offsets validate this header.
