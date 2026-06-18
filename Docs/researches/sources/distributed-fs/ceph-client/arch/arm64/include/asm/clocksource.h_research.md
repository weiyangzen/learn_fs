## sources/distributed-fs/ceph-client/arch/arm64/include/asm/clocksource.h

Purpose: routes arm64 clocksource definitions to the vDSO-facing clocksource header.

Important APIs/types/functions: includes `<asm/vdso/clocksource.h>` and defines no local API.

Control flow: compile-time include only.

State and persistence: no state in this header.

Dependencies and integration: used by timekeeping and vDSO build paths to share clocksource definitions.

Risks: include path breakage affects vDSO time reads and kernel timekeeping builds. Test signals are vDSO selftests, clocksource boot logs, and timekeeping regression tests.
