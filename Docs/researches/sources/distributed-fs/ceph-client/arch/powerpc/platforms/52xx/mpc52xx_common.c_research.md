# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_common.c

## Purpose
`mpc52xx_common.c` provides common MPC52xx services for device mapping, OF platform population, XLB arbitration, PSC clock divisors, watchdog restart, and AC97 GPIO reset.

## Important APIs, Types, and Functions
`mpc52xx_map_common_devices()` permanently maps watchdog GPT, CDM, simple GPIO, and wakeup GPIO. `mpc5200_setup_xlb_arbiter()` sets XLB priorities and applies original MPC5200 pipelining erratum handling. `mpc52xx_declare_of_platform_devices()` populates supported bus nodes. Exported `mpc52xx_set_psc_clkdiv()` programs PSC MCLK dividers. `mpc52xx_restart()` resets through GPT watchdog. Exported `mpc5200_psc_ac97_gpio_reset()` bit-bangs AC97 cold reset through GPIO.

## Control Flow, State, and Persistence
Global mappings `mpc52xx_wdt`, `mpc52xx_cdm`, `simple_gpio`, and `wkup_gpio` persist for restart and exported helper use. Spinlocks protect CDM and GPIO register updates.

## Dependencies and Integration Points
It depends on OF match tables, MPC52xx register structs, gpt `fsl,has-wdt` properties, platform bus population, and AC97/PSC clients.

## Risks and Test Signals
Risks include permanent mappings, missing watchdog preventing restart, PSC ID restrictions, bootloader-dependent XLB state, and temporary GPIO mux changes during AC97 reset. Test signals are restart, PSC audio clocking, AC97 cold reset on PSC1/PSC2, OF device registration, and erratum behavior on MPC5200 versus MPC5200B.
