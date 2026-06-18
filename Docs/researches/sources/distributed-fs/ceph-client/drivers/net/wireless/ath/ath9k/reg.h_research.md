# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg.h

## Purpose
`reg.h` is the central ath9k MAC/PCU hardware register map for non-USB ath9k devices. It contains register offsets, field masks, shifts, and helper address macros used by the HAL and core driver to program DMA, interrupts, TX/RX queues, beacon timers, sleep, counters, diagnostics, Bluetooth coexistence, WoW power-management bits, and PHY calibration control entry points that sit in MAC-visible register space.

## Important APIs, types, and constants
This header exports preprocessor constants rather than functions. Important groups include `AR_CR`, `AR_CFG`, `AR_IER`, `AR_ISR*`, and `AR_IMR*` for device control and interrupt status/masks; `AR_QTXDP`, `AR_QMISC`, `AR_DQCUMASK`, `AR_DLCL_IFS`, and related QCU/DCU macros for TX queue programming; `AR_RXDP`, `AR_HP_RXDP`, `AR_LP_RXDP`, `AR_RX_FILTER`, and multicast filter registers for RX control; `AR_TSF_*`, `AR_GEN_TIMERS`, `AR_TIMER_MODE`, beacon, quiet, sleep, and TSF registers for timekeeping; MIB/cycle/error counter addresses; key cache field definitions; PCU misc flags; Bluetooth coexistence weights and mode bits; and WoW/PM control fields such as `AR_PMCTRL_*` and `AR_WOW_BEACON_TIMO_MAX`.

## Control flow and integration
There is no executable control flow here. The macros are consumed by ath9k hardware routines through `REG_READ`, `REG_WRITE`, `REG_RMW_FIELD`, and bit operations from the ath9k HAL. The register families line up with higher-level files in this subset: `xmit.c` depends on TX queue/DCU/QCU behavior programmed through HAL helpers using these definitions, `wow.c` reaches PM/WoW routines that eventually touch the WoW and power-control fields, and `rng.c` uses PHY register definitions from companion PHY headers while following the same register-access convention.

## State and persistence behavior
The state represented by this file is volatile device state in PCI/SoC hardware registers. It controls persistent-in-hardware queue pointers, interrupt masks, timer state, TSF counters, sleep state, diagnostic overrides, and counters until reset, suspend, or explicit reprogramming. The header itself owns no software persistence.

## Dependencies
The macros assume ath9k hardware revision predicates and common register helpers are available from the surrounding HAL headers, especially `AR_SREV_*` selectors for revision-dependent offsets. Consumers must understand endian-neutral register values, field masks, and the distinction between read-clear interrupt registers and normal readable registers.

## Risks
The main risks are wrong offsets or masks causing silent hardware misprogramming, revision predicates selecting an invalid register layout, duplicate or aliased definitions hiding chip-specific differences, and callers using status/mask macros on the wrong register family. Interrupt and DMA definitions are particularly high risk because small mistakes can wedge TX/RX, lose interrupts, or leave DMA active during reset.

## Test signals
Useful signals include successful device probe/reset across supported revisions, stable TX/RX under interrupt load, correct queue setup and drain behavior, WoW suspend/resume tests, beacon/TSF timing tests, MIB counter sanity, and register-readback diagnostics where the HAL writes fields and verifies expected masked values.
