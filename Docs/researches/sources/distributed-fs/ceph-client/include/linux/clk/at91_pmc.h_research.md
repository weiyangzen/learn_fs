# sources/distributed-fs/ceph-client/include/linux/clk/at91_pmc.h

Purpose: This is the AT91/SAMA Power Management Controller register-map header. It provides offsets, masks, status bits, write-protect keys, PLL fields, programmable-clock fields, USB/audio clock controls, and wake-up bits used by AT91 clock and PM drivers.

Important APIs/types/functions: It exports register offsets such as `AT91_PMC_SCER`, `AT91_PMC_SCDR`, `AT91_PMC_SCSR`, `AT91_CKGR_MOR`, `AT91_CKGR_PLLAR`, `AT91_CKGR_PLLBR`, `AT91_PMC_MCKR`, `AT91_PMC_PCKR(n)`, `AT91_PMC_SR`, `AT91_PMC_PROT`, `AT91_PMC_WPSR`, `AT91_PMC_PCR`, and audio PLL registers. Important masks include oscillator enable/select bits, PLL multiplier/divider fields, master-clock source/prescaler/divider fields, status bits such as `AT91_PMC_MCKRDY` and `AT91_PMC_LOCK*`, `AT91_PMC_KEY`, write-protect fields, and helper macros such as `AT91_PMC_MUL_GET`, `AT91_PMC3_MUL_GET`, `AT91_PMC_SMDDIV`, and `AT91_PMC_MCR_V2_ID`.

Control flow: There is no executable control flow in the header. Drivers use these definitions to sequence oscillator and PLL setup, wait on status bits, enable peripheral/generated clocks, configure programmable clocks, manage write protection, and handle wake events. Several offsets are SoC-version-specific or reused for different registers on different families.

State and persistence behavior: The state is entirely in PMC hardware registers. Register writes persist until reset, power-state loss, or later driver reprogramming. Some fields such as write-protect state and wake-up masks can affect subsequent register access and low-power behavior.

Dependencies and integration points: It includes `<linux/bits.h>` and integrates with AT91 clocksource, CCF, PM, USB, audio, watchdog/wakeup, and SoC initialization code that maps PMC registers.

Risks: Register offsets overlap by SoC generation, so using a SAM9X60/SAMA7G5 definition on older hardware can program the wrong register. Missing the `AT91_PMC_KEY` or write-protect key causes silent write failures. PLL and master-clock prescaler fields differ across families, and readiness/status bits must be polled before consumers use the clock.

Test signals: Boot tests on each AT91/SAMA family, PLL lock and master-clock ready polling, peripheral clock enable/disable tests, suspend/resume wake-source validation, write-protect violation checks, and measured USB/audio/generated clock frequencies are useful signals.
