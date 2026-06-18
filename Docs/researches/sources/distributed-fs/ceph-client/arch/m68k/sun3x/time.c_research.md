# sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.c

## Purpose

implements Sun-3x RTC/time initialization and hardware clock access using the platform timer/clock
chip

## Important APIs, Types, and Functions

Source read size: 103 lines, 2075 bytes. Includes: `linux/types.h`, `linux/kd.h`, `linux/init.h`,
`linux/sched.h`, `linux/kernel_stat.h`, `linux/interrupt.h`, `linux/rtc.h`, `linux/bcd.h`,
`asm/irq.h`, `asm/io.h`, `asm/machdep.h`, `asm/traps.h`; plus 3 more. Defined functions:
`sun3x_hwclk`, `sun3x_timer_tick`, `sun3x_sched_init`. Declared functions: `local_irq_save`,
`local_irq_restore`, `sun3_disable_interrupts`. Key macros/defines: `M_CONTROL`, `M_SEC`, `M_MIN`,
`M_HOUR`, `M_DAY`, `M_DATE`, `M_MONTH`, `M_YEAR`, `C_WRITE`, `C_READ`, `C_SIGN`, `C_CALIB`.

## Control Flow and Behavior

control flow is entered from platform setup, firmware service wrappers, or generic
timekeeping/machdep hooks

## State and Persistence

persistent state includes PROM vectors, installed machdep callbacks, RTC register values, and
DVMA/IOMMU state for data movers

## Dependencies and Integration Points

integrates with Sun-3x PROM firmware, m68k machine setup, generic timekeeping, reset paths, and
device drivers

## Risks and Test Signals

firmware ABI and clock register mistakes can block boot or skew time; Sun-3x boot, clock read/write,
PROM console, and DMA tests are signals
