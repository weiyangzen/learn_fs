# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/regs-timers.h

Purpose: MMP/PXA timer register and bit definitions.

Important APIs/types/functions: Defines timer register offsets and control/status bit masks used by `time.c`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates with the MMP clocksource/clockevent implementation.

Risks: Wrong offsets or bit definitions break scheduler ticks and delay calibration.

Test signals: Timer interrupt and clocksource tests on MMP/PXA platforms.
