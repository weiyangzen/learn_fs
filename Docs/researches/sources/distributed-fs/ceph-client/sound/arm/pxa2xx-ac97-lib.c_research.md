# sources/distributed-fs/ceph-client/sound/arm/pxa2xx-ac97-lib.c

## Purpose
This file is an exported helper library for Intel/Marvell PXA AC97 controller access. It provides serialized AC97 register read/write, CPU-family-specific warm/cold reset sequences, IRQ-assisted completion waits, hardware probe/remove, PM clock handling, and modem status accessors.

## Important APIs, Types, And Functions
Exported APIs include `pxa2xx_ac97_read()`, `pxa2xx_ac97_write()`, `pxa2xx_ac97_try_warm_reset()`, `pxa2xx_ac97_try_cold_reset()`, `pxa2xx_ac97_finish_reset()`, PM helpers, `pxa2xx_ac97_hw_probe()`, `pxa2xx_ac97_hw_remove()`, `pxa2xx_ac97_read_modr()`, and `pxa2xx_ac97_read_misr()`. Static reset helpers are selected by `cpu_is_pxa25x()`, `cpu_is_pxa27x()`, or `cpu_is_pxa3xx()`. `pxa2xx_ac97_irq()` records GSR bits and wakes waiters.

## Control Flow
Probe maps MMIO, discovers or assigns reset GPIO, prepares PXA27x reset workarounds and optional `AC97CONFCLK`, enables `AC97CLK`, obtains IRQ, and requests the AC97 IRQ. Read/write take `car_mutex`, choose primary/secondary audio or modem register space, clear completion bits, issue MMIO access, and wait for SDONE/CDONE through a wait queue with timeout fallback. Reset functions perform family-specific register/GPIO/clock sequences and poll for primary or secondary codec ready. Remove shuts down AC-link, frees IRQ, releases clocks, and clears globals.

## State And Persistence
Global static state includes serialized controller access (`car_mutex`), completion wait queue, latched `gsr_bits`, AC97 clocks, reset GPIO state, and `ac97_reg_base`. This library assumes one active PXA AC97 controller instance.

## Dependencies And Integration Points
It depends on platform devices, clocks, GPIO descriptors, PXA CPU detection/configuration helpers, AC97 register definitions from `pxa2xx-ac97-regs.h`, and exported ALSA/PXA library headers. Other ALSA/ASoC PXA drivers call these exported functions to implement AC97 bus operations.

## Risks And Test Signals
Global state makes multi-controller use unsafe. PXA27x and PXA3xx hardware errata drive unusual timeout and reset behavior; regression tests should exercise all CPU-family reset paths where possible. `pxa2xx_ac97_read()` rejects `slot > 0`, while write does not perform the same check, so caller discipline matters. Test signals include successful codec-ready polling, read/write completion or timeout reporting, IRQ wakeups, correct clock cleanup on probe failures, and no stale `gsr_bits` after repeated accesses.
