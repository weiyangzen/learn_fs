<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me-regs.h -->
# sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me-regs.h

Purpose: defines PCI device IDs, PCI firmware-status offsets, MEI memory-mapped register offsets, and bit masks for the classic Intel ME/HECI hardware backend.

Important APIs and constants: device IDs cover legacy ICH/ICH10, PCH generations, server chipsets, Atom/embedded variants, GSC/GSCFI/CSC-style devices, and newer named platforms. Firmware-status offsets include `PCI_CFG_HFS_1` through `PCI_CFG_HFS_6` and SKU/PM/PXP masks. Register offsets include `H_CB_WW`, `H_CSR`, `ME_CB_RW`, `ME_CSR_HA`, `H_HPG_CSR`, `H_D0I3C`, and GSC extended operation memory registers. Bit masks describe host and ME circular-buffer depth/pointers, ready/reset/interrupt bits, PG isolation, D0i3, and TRC status.

Control flow: no executable code. `hw-me.c` uses these constants to read/write hardware, compute buffer slots, control interrupts, perform resets, negotiate power gating, read FW status, and configure platform quirks.

State and persistence: no in-memory state. Values map persistent hardware registers exposed by PCI config space or MMIO.

Dependencies and integration: included by `hw-me.c` and likely PCI ID tables outside this subset. The SPDX dual license allows reuse in GPL/BSD-compatible contexts for register definitions.

Risks: incorrect offsets or masks can corrupt hardware communication, mis-detect firmware SKU, break D0i3/PG handling, or falsely enable unsupported platforms. Device ID additions must match platform configuration selection in the ME PCI driver and `mei_cfg_idx`.

Test signals: probe success on each platform ID, correct sysfs `fw_status` output, interrupt delivery through `H_CSR`/`ME_CSR_HA`, runtime PM D0i3 transitions, TRC tracepoint register reads, and PXP/GSC boot-type detection on GSC devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/misc/mei/hw-me-regs.h -->
