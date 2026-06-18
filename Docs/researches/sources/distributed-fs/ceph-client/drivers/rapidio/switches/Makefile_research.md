# sources/distributed-fs/ceph-client/drivers/rapidio/switches/Makefile

## Purpose
Maps RapidIO switch Kconfig symbols to their driver objects.

## Important APIs, types, and functions
`obj-$(CONFIG_RAPIDIO_CPS_XX) += idtcps.o`, `obj-$(CONFIG_RAPIDIO_CPS_GEN2) += idt_gen2.o`, and `obj-$(CONFIG_RAPIDIO_RXS_GEN3) += idt_gen3.o`.

## Control flow
No runtime flow. Kbuild includes objects based on `.config`.

## State and persistence
No runtime state; build output depends on configuration.

## Dependencies and integration
Integrates directly with `switches/Kconfig` and the RapidIO core symbols used by each object.

## Risks
Misaligned symbol names would silently omit a driver; current names match Kconfig.

## Test signals
Kernel build with each switch option toggled and module alias/probe availability for the selected object.
