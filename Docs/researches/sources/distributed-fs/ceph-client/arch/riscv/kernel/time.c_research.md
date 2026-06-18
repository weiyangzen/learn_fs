<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/time.c

Purpose: Initializes RISC-V timekeeping from firmware-provided timer frequency.

Important APIs/types/functions: Exports `riscv_timebase` and implements `time_init()`.

Control flow: During boot, `time_init()` reads the `timebase-frequency` from DT/ACPI helpers, stores it in `riscv_timebase`, registers the clocksource, and initializes the timer.

State and persistence: `riscv_timebase` becomes the persistent frequency used by timers and hwprobe.

Dependencies and integration points: Used by clocksource/timer init, SBI timer programming, and `sys_hwprobe.c` time CSR frequency reporting.

Risks: Wrong timebase causes broken scheduler ticks, timers, and userspace time calculations.

Test signals: Boot-time timer frequency logs, clocksource registration, timer interrupt operation, and hwprobe `TIME_CSR_FREQ` consistency.

Source read size: 51 lines, 1213 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/time.c -->
