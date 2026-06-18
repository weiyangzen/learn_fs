# sources/distributed-fs/ceph-client/include/pcmcia/cisreg.h

## Purpose

`cisreg.h` defines offsets and bit masks for PCMCIA/CardBus configuration, status, pin replacement, socket/copy, extended status, function status, and zoomed-video indirect registers.

## Important APIs, types, and functions

Register offset macros include `CISREG_COR`, `CISREG_CCSR`, `CISREG_PRR`, `CISREG_SCR`, `CISREG_ESR`, IO base/size registers, CardBus function registers, and indirect register addresses. Bit masks include `COR_*`, `CCSR_*`, `PRR_*`, `SCR_*`, `ESR_*`, `CBFN_*`, `FEMR_*`, and `ICTRL0_*`.

## Control flow

PCMCIA core and drivers use these constants when reading or writing card configuration registers relative to `ConfigBase`. Control flows typically select a configuration option, enable a function/IRQ, acknowledge status, inspect ready/write-protect/battery events, or program indirect video registers.

## State and persistence behavior

The header owns no software state. It names hardware/card register bits whose values persist in the card until reset, power transition, or explicit write.

## Dependencies and integration points

It is standalone and integrates with PCMCIA CIS/configuration code, CardBus function status handling, power management, and legacy device drivers.

## Risks and test signals

Risks include writing wrong offsets for multifunction cards, confusing event and status bits, failing to clear/ack interrupts, and unsafe register writes during power transitions. Tests should cover configuration register programming, interrupt enable/ack, ready/write-protect event handling, CardBus function status, and suspend/resume reset behavior.
