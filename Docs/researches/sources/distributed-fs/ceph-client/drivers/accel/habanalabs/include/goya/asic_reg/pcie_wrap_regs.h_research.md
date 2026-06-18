# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/pcie_wrap_regs.h

Purpose: maps the Goya PCIe wrapper block. It exposes 142 addresses for PHY reset, outstanding transaction control, indirect AXI write/read channels, miscellaneous PCIe metadata, response/status registers, LBW/HBW protection and cache override controls, queue initialization, split interrupts, user attribute registers, drain controls, and AXI error reporting.

Important APIs/types/functions: this is a macro-only header. Important groups include `mmPCIE_WRAP_IND_AW*`, `mmPCIE_WRAP_IND_W*`, `mmPCIE_WRAP_IND_AR*`, `mmPCIE_WRAP_IND_R*`, `mmPCIE_WRAP_AXI_PROT_OVR`, `mmPCIE_WRAP_LBW_PROT_OVR`, `mmPCIE_WRAP_DRAIN_CFG`, and `mmPCIE_WRAP_AXI_INTR`.

Control flow: indirect access code writes address, attributes, data, and valid bits into the wrapper channel registers, then polls response/valid registers. Reset and shutdown paths use drain/timeout/outstanding transaction registers before changing PCIe state. Security setup programs protection and user override registers.

State and persistence: wrapper configuration is hardware state. Protection, cache, lock, ARUSER/AWUSER, outstanding, and drain settings persist until reset or explicit rewrite and can affect all PCIe-originated transactions.

Dependencies and integration: included by `goya_regs.h`. Goya/Gaudi driver code references equivalent macros for HBW flush registers and LBW protection overrides, while security code computes protection-bit words from wrapper register addresses.

Risks: indirect-channel programming is order-sensitive; asserting valid before address/data fields are ready can issue malformed AXI transactions. Protection override bits are security-sensitive. Drain configuration must avoid racing with in-flight DMA or doorbell traffic.

Test signals: PCIe reset/remove stress, DMA drain tests, AXI error interrupt paths, security/protection register audits, and indirect read/write loopback tests are the strongest signals.
