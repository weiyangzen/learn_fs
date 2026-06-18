# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmstb_nand.c

Purpose: generic Broadcom STB platform glue for the shared brcmnand controller. It binds the generic `brcm,brcmnand` compatible and delegates behavior to the core without SoC-specific hooks.

Important APIs/types/functions: `brcmstb_nand_probe` calls `brcmnand_probe(pdev, NULL)`. The platform driver uses `brcmnand_remove`, `brcmnand_pm_ops`, and OF match `brcm,brcmnand`.

Control flow: direct pass-through probe. With no `brcmnand_soc`, the core uses normal MMIO access and standard controller-ready IRQ handling.

State and persistence: no glue-specific runtime state; all persistent state is in the core and platform resources.

Dependencies/integration: shared brcmnand core and OF platform matching. Link order keeps more specific glue before this generic driver.

Risks/test signals: overmatching platforms that need specific hooks and registration-order conflicts. Test generic STB probe, standard IRQ completion, MMIO access, MTD registration, suspend/resume, and specific-driver precedence.
