<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/suspend.c

### Purpose
`suspend.c` implements common LoongArch ACPI suspend/resume state handling around the assembly sleep entry.

### Important APIs, Types, And Functions
It defines `loongarch_suspend_addr`, `struct saved_registers`, static `saved_regs`, and functions `loongarch_common_suspend()`, `loongarch_common_resume()`, and `loongarch_acpi_suspend()`.

### Control Flow
Suspend saves counters, user/kernel PGD CSRs, page-walk controls, exception config, extended-unit enable, per-CPU base, and the firmware suspend address. `loongarch_acpi_suspend()` enables wake sources, saves common state, calls `loongarch_suspend_enter()`, then restores common state. Resume syncs counters, flushes TLBs, reinstalls exception vector CSRs, restores page-table/page-walk CSRs, exception config, EUEN, and per-CPU base.

### State, Persistence, And Dependencies
State survives S3 in static saved registers and firmware-managed CPU state. Dependencies include ACPI wake setup, LoongArch CSRs, exception vector symbols `eentry`/`tlbrentry`, TLB flushes, timer counter sync, and assembly in `suspend_asm.S`.

### Integration Points
Generic suspend path calls `loongarch_acpi_suspend()`. `platform.c` provides `loongson_sysconf.suspend_addr`. `tlb.c` originally installed the exception vectors restored here.

### Risks
Missing CSR restoration can break page walking, exceptions, or percpu addressing after resume. Wake setup and firmware entry must be valid before assembly enters sleep.

### Test Signals
ACPI S3 suspend/resume cycles, timer continuity checks, page-fault/TLB stress after resume, CPU hotplug after resume, and wake-source validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend.c -->
