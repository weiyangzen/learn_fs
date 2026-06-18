## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arch_timer.h

### Purpose
Defines ARM64 architectural timer register accessors, stable counter reads, erratum workaround indirection, and event stream feature publication.

### Important APIs, Types, And Functions
Defines `enum arch_timer_erratum_match_type`, `struct arch_timer_erratum_workaround`, per-CPU `timer_unstable_counter_workaround`, `arch_timer_read_cntpct_el0`, `arch_timer_read_cntvct_el0`, `arch_timer_reg_write_cp15`, `arch_timer_reg_read_cp15`, `arch_timer_get_cntfrq`, `arch_timer_get_cntkctl`, `arch_timer_set_cntkctl`, `__arch_counter_get_cntpct`, `__arch_counter_get_cntvct`, stable variants, and event-stream helpers.

### Control Flow
Counter reads use alternatives to select ECV self-synchronizing registers when available, otherwise `isb; mrs`. Stable read macros route through per-CPU erratum handlers when configured. Timer register read/write helpers compile-time select physical or virtual timer registers and insert `isb()` after control writes.

### State, Persistence, And Dependencies
State lives in architectural timer registers, per-CPU workaround pointers, compat hwcap bits, and CPU feature flags. Dependencies include barriers, hwcap, sysreg, jump labels/percpu types, and generic clocksource timer definitions.

### Integration Points
Used by the ARM arch timer clocksource/clockevent driver, VDSO timekeeping decisions, compat HWCAP exposure, and erratum workaround framework.

### Risks
Timer reads require strict ordering; wrong ECV alternative or erratum handler selection can make time go backward. Register accessors must match physical/virtual timer paths. Event stream feature exposure affects userspace ABI.

### Test Signals
Run clocksource watchdog, high-resolution timer, suspend/resume, CPU hotplug, VDSO time tests, ECV-capable hardware tests, erratum workaround platform tests, and compat HWCAP validation.
