# sources/distributed-fs/ceph-client/arch/powerpc/platforms/52xx/mpc52xx_gpt.c

## Purpose
`mpc52xx_gpt.c` is the driver for MPC5200 General Purpose Timers as GPIO controllers, cascaded IRQ controllers, timer APIs, and optionally GPT0 watchdog.

## Important APIs, Types, and Functions
The driver registers as `mpc52xx-gpt` at `subsys_initcall`. `mpc52xx_gpt_probe()` maps registers, records bus frequency, sets up GPIO and IRQ domains from DT properties, adds the timer to a global list, and configures watchdog capability. Exported APIs include `mpc52xx_gpt_from_irq()`, `mpc52xx_gpt_start_timer()`, `mpc52xx_gpt_stop_timer()`, and `mpc52xx_gpt_timer_period()`. Watchdog support registers `/dev/watchdog` when `CONFIG_MPC5200_WDT` is enabled.

## Control Flow, State, and Persistence
Each GPT has `mpc52xx_gpt_priv` with register mapping, raw spinlock, irq domain, bus frequency, GPIO chip, and watchdog mode bits. A global list is protected by `mpc52xx_gpt_list_mutex`. Watchdog mode blocks normal timer operations while active.

## Dependencies and Integration Points
It integrates platform devices from OF, gpiolib, irq domains, misc watchdog ABI, IPB bus-frequency helpers, and DT properties `gpio-controller`, `interrupt-controller`, `fsl,has-wdt`, and `fsl,wdt-on-boot`.

## Risks and Test Signals
Risks include multiplexing one hardware pin as GPIO and IRQ, watchdog `NOWAYOUT` semantics, period calculation limits, no remove path, and DT-encoded IRQ flags. Test signals are GPIO get/set/direction, edge IRQ delivery, timer period accuracy, watchdog open/ioctl/release behavior, GPT0 busy rejection, and early availability before dependent drivers.
