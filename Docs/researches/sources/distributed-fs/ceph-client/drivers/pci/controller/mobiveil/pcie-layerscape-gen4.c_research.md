## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/pcie-layerscape-gen4.c

Purpose: NXP Layerscape Gen4 PCIe host driver layered on the Mobiveil host library. It provides Layerscape-specific PF register access, link-up detection, interrupt enablement, and PAB reset recovery.

Important APIs, types, and functions: `struct ls_g4_pcie` embeds `struct mobiveil_pcie`, delayed reset work, and IRQ. `ls_g4_pcie_link_up()` checks PF LTSSM L0. `ls_g4_pcie_enable_interrupt()` clears and enables PAB reset, INTx, MSI, uncorrectable, PM redirect, and event collector interrupts. `ls_g4_pcie_isr()` reads Mobiveil misc status, disables interrupts and schedules delayed work on PAB reset, clears status, and returns handled. `ls_g4_pcie_reinit_hw()` waits for `PF_INT_STAT_PABRST` and no PAB activity, toggles PF debug write-enable/reset bits, calls `mobiveil_host_init(..., true)`, and waits for link. `ls_g4_pcie_probe()` allocates host bridge private data, validates `msi-parent`, initializes ops, and calls `mobiveil_pcie_host_probe()`.

Control flow: platform probe delegates most host setup to the Mobiveil library, then enables interrupts. PAB reset interrupts are handled asynchronously by `ls_g4_pcie_reset()` which clears bridge bus reset and attempts hardware reinit.

State and persistence: volatile state includes PF debug/reset bits, Mobiveil PAB misc interrupt masks/status, delayed work, host bridge private state, and window/MSI state reprogrammed by `mobiveil_host_init()`. No persistent state.

Dependencies and integration points: Mobiveil common/host code, platform IRQ named `"intr"`, OF `msi-parent`, host bridge allocation, and compatible `fsl,lx2160a-pcie`.

Risks: Reset recovery returns early on success before re-enabling interrupts; interrupt state relies on earlier or hardware behavior and deserves scrutiny. `mobiveil_host_init(reinit=true)` skips bus-number setup but reprograms windows. The delayed work is not explicitly canceled in a remove path because the driver is built in.

Test signals: Layerscape Gen4 enumeration, MSI parent validation, PAB reset interrupt generation and recovery, link re-training after reset, INTx/MSI delivery through Mobiveil core, and timeout logs for PAB activity or link training failures.
