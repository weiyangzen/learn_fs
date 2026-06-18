# sources/distributed-fs/ceph-client/drivers/pcmcia/sa1100_generic.h

Purpose: Declares machine-specific SA-1100 PCMCIA initialization entry points used by the generic SA-11x0 platform driver.

Important APIs and types: Includes common SoC and SA11xx base definitions, then declares `pcmcia_*_init(struct device *)` functions for many legacy SA-1100 boards, including H3600 and Collie-relevant names.

Control flow: No logic executes here. `sa1100_generic.c` conditionally references a subset of these declarations based on Kconfig symbols.

State and persistence: No state is stored. The declared functions create or register common SoC socket state in their implementations.

Dependencies and integration points: Ties legacy board files to the generic SA11x0 PCMCIA platform driver and `sa11xx_drv_pcmcia_probe()`.

Risks: Declarations include many legacy boards not necessarily built in this tree; Kconfig must ensure only available implementations are referenced. Signature mismatch would break compile-time integration.

Test signals: Compile coverage for enabled SA1100 machine configs and successful dispatch from legacy probe into the matching board init routine.
