# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/time.c

Purpose: RiscPC legacy timer and clock event/source setup.

Important APIs/types/functions: provides timer initialization and interrupt handling around IOMD timer registers for the platform tick.

Control flow: init programs the hardware timer period, registers the interrupt handler, and hooks into ARM timekeeping. The handler acknowledges the timer interrupt and advances kernel time via the clockevent/timer tick path.

State and persistence: hardware timer count/control registers and registered IRQ handler form runtime state.

Dependencies and integration points: depends on IOMD, `mach/irqs.h`, legacy timer tick selected by Kconfig, and machine descriptor `init_time`.

Risks: incorrect tick rate or acknowledgement causes lost ticks or interrupt storms. Legacy timer code lacks DT clock discovery.

Test signals: stable jiffies, scheduler timer operation, timer IRQ rate, and boot under `LEGACY_TIMER_TICK`.
