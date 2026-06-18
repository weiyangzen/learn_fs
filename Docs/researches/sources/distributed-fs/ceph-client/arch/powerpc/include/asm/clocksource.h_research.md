# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/clocksource.h

Purpose: routes the architecture clocksource include path to the PowerPC VDSO clocksource definitions.

Important APIs/types/functions: includes `<asm/vdso/clocksource.h>` under the PowerPC clocksource include guard.

Control flow: no runtime logic in this wrapper. Timekeeping and VDSO code consume the included definitions.

State and persistence: no state is stored here. Clocksource state lives in the timekeeping core and PowerPC VDSO data.

Dependencies and integration points: integrates generic clocksource include users with PowerPC VDSO clocksource support.

Risks: if the VDSO clocksource header changes path or API, this wrapper must stay aligned or architecture timekeeping builds will fail.

Test signals: PowerPC timekeeping builds, VDSO clock_gettime tests, and boot-time clocksource registration checks.
