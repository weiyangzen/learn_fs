# sources/distributed-fs/ceph-client/arch/m68k/bvme6000/config.c

Purpose: BVME4000/BVME6000 board setup, timer clocksource, reset, abort interrupt, and machine hardware clock support.

Important APIs are `bvme6000_parse_bootinfo()`, `config_bvme6000()`, `bvme6000_sched_init()`, `bvme6000_hwclk()`, and `bvme6000_reset()`. Bootinfo parsing recognizes `BI_VME_TYPE`. Board configuration infers `vme_brdtype` from CPU when absent, installs machdep hooks, configures PIT ports, reports system-controller state, and disables snooping for Ethernet/VME accesses.

Timer flow programs DP8570A RTC timer 1 in mode 2 with an 8 MHz clock, requests `BVME_IRQ_RTC`, registers a continuous clocksource, and requests `BVME_IRQ_ABORT`. `bvme6000_timer_int()` acknowledges RTC interrupts, advances `clk_total`, resets `clk_offset`, and calls `legacy_timer_tick(1)`. `bvme6000_read_clk()` repeatedly latches timer state until T1 interrupt/output readings are stable, avoiding rollover/chip fault windows.

State includes PIT/RTC hardware registers, `clk_total`, `clk_offset`, board type, config register state, and vector entries restored by abort handling. `bvme6000_reset()` enables watchdog through PIT port C and spins.

Dependencies include BVME hardware headers, VME bootinfo, generic clocksource/IRQ/machdep APIs, BCD helpers, and vector table symbols.

Risks and test signals: timer read has explicit invalid-read avoidance; changing it can break monotonic time. Abort handler copies vectors from BVMBug ROM addresses and is hardware-specific. Test timer tick/clocksource monotonicity, RTC read/write, abort button behavior, reset watchdog, and board type detection.
