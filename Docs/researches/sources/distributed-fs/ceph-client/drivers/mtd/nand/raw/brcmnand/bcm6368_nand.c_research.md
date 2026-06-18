# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcm6368_nand.c

Purpose: BCM6368 MIPS DSL platform glue for the shared Broadcom NAND controller. It supplies platform-specific controller-ready interrupt acknowledge and enable operations.

Important APIs/types/functions: `struct bcm6368_nand_soc` embeds `struct brcmnand_soc` and stores interrupt MMIO base. `bcm6368_nand_intc_ack` checks and acknowledges `BCM6368_CTRL_READY`; `bcm6368_nand_intc_set` toggles the ready interrupt enable. `bcm6368_nand_probe` maps `nand-int-base`, installs hooks, clears/acks interrupts, and delegates to `brcmnand_probe`.

Control flow: probe allocates glue state, maps the named resource, assigns `ctlrdy_ack`/`ctlrdy_set_enabled`, disables and acknowledges all interrupts, then lets the core handle NAND setup. Remove and PM are shared core functions.

State and persistence: only the interrupt base mapping and hook table persist in the glue. Interrupt enable/status bits persist in the hardware register block.

Dependencies/integration: OF compatible `brcm,nand-bcm6368`, platform resource `nand-int-base`, and exported brcmnand core APIs.

Risks/test signals: status/enable bitfield mistakes, acknowledge semantics, missing resource, and interrupt storms. Test probe, controller-ready IRQ completion, suspend/resume interrupt re-enable, fallback polling, and MTD read/write/erase.
