# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-boards/malta.h

Purpose: Malta board address and peripheral definitions for system controllers, GIC/CPC/GCMP, RTC, SMSC Super I/O, and jumper register access.

Important APIs/types/functions: Defines MSC interrupt-controller base addresses, `MALTA_GT_PORT_BASE`, `MALTA_BONITO_PORT_BASE`, and `MALTA_MSC_PORT_BASE`. Inline helpers `get_gt_port_base()` and `get_msc_port_base()` read controller windows. Defines `GCMP_BASE_ADDR`, `GIC_BASE_ADDR`, `CPC_BASE_ADDR`, `MSC01_BIU_REG_BASE`, `MSC01_SC_CFG_*`, RTC ports `0x70/0x71`, SMSC config registers and values, `SMSC_WRITE`, `MALTA_JMPRS_REG`, and `malta_dt_shim()`.

Control flow, state, and persistence: Inline port-base helpers read MMIO configuration to compute I/O port bases. Board state persists in system-controller registers, Super I/O config space, and jumper hardware.

Dependencies and integration: Includes GT64120, MSC01 PCI, and `ioremap`/`inl`/`outb` accessors indirectly. It integrates with Malta PCI, interrupt, RTC, device-tree shimming, and Super I/O initialization.

Risks and test signals: Controller-specific base selection is fragile across Malta revisions. Test with GT, Bonito, MSC, and SOC-it variants, PCI I/O enumeration, RTC access, GIC/CPC discovery, and Super I/O activation.
