# sources/distributed-fs/ceph-client/arch/m68k/hp300/time.h

Purpose: declares the HP300 scheduler/timer initialization entry point for other HP300 machine code.

Important APIs/types/functions: declares `extern void hp300_sched_init(void);`.

Control flow: no executable logic.

State and persistence: no state.

Dependencies/integration: included by `config.c` to assign `mach_sched_init` and by `time.c` for local consistency.

Risks: if the declaration diverges from `time.c`, the machine callback assignment can break at compile or link time.

Test signals: build coverage that includes both `config.c` and `time.c`, and link resolution for `hp300_sched_init`.
