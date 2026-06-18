# sources/distributed-fs/ceph-client/drivers/net/ethernet/sunplus/spl2sw_register.h

Purpose: Defines Sunplus L2 switch MMIO register offsets used by the driver.

Important APIs/constants: Covers interrupt status/mask, flow-control thresholds, address table search/write registers, PVID/VLAN membership, port ability/status/control, CPU control, global control/reset/LED/watchdog, PHY control, forced MAC mode, CPU TX trigger, and descriptor base/current-pointer registers for CPU port instances.

Control flow and state: This file is declarative. Its offsets are the address contract for all `readl()`/`writel()` operations in descriptor, MAC, MDIO, PHY, interrupt, and driver code. Hardware state persists in these registers until reset or reprogramming.

Dependencies and integration points: Used with `comm->l2sw_reg_base` from `devm_platform_ioremap_resource()`. Bit positions come from `spl2sw_define.h`, so offset and bitfield headers must remain in sync with the SP7021 hardware manual.

Risks and test signals: A wrong offset corrupts unrelated switch state. Several CPU port 1 descriptor offsets are defined but current code primarily programs CPU port 0. Test register programming with hardware trace/debugfs where available, probe reset defaults, descriptor base addresses, MDIO transactions, and interrupt ack/mask behavior.
