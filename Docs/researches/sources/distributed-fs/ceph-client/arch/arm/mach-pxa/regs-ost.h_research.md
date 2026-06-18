<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-ost.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-ost.h

Purpose: OS timer and watchdog register definitions for PXA.

Important definitions: physical resource `OST_PHYS/OST_LEN`, match registers `OSMR0-4`, counters `OSCR/OSCR4`, `OMCR4`, status `OSSR`, watchdog enable `OWER`, interrupt enable `OIER`, match status bits, watchdog match enable, and interrupt-enable bits.

Control flow and integration: reset code uses channel 3 as watchdog reset source; `devices.c` exposes the timer range to `sa1100_wdt`; timer code uses these registers through clocksource support.

State and persistence: timer counters and watchdog registers are hardware state.

Dependencies: includes `pxa-regs.h` for `io_p2v`.

Risks and test signals: watchdog reset path loops after arming OSMR3, so wrong timer rate or register mapping can hang. Test watchdog device probe, hard restart, and OS timer interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-ost.h -->
