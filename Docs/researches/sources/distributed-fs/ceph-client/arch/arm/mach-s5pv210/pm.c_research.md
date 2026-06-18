<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/pm.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/pm.c

### Purpose
Implements S5PV210 suspend-to-RAM support for DT-based systems.

### Important APIs, Types, And Functions
Defines local `struct sleep_save`, `s3c_pm_do_save()`, `s3c_pm_do_restore_core()`, `s5pv210_read_eint_wakeup_mask()`, `s5pv210_cpu_suspend()`, `s5pv210_pm_prepare()`, `s5pv210_suspend_enter()`, suspend ops, syscore resume ops, and `s5pv210_pm_init()`.

### Control Flow
Late machine init registers syscore resume and suspend ops. Suspend enter reads EINT wake mask, rejects sleep if all internal and external wake sources are masked, saves UARTs, writes wake masks, writes `s5pv210_cpu_resume` to `S5P_INFORM0`, configures sleep oscillator and WFI sleep mode, disables SYSCON interrupts, saves core registers, flushes caches, and calls `cpu_suspend()`. On resume it restores UARTs, logs wake status, checks PM debug state, and syscore restore replays saved core registers.

### State, Persistence, And Dependencies
State includes `s5pv210_irqwake_intmask`, saved core register values, suspend ops registration, and system controller power registers. Dependencies include Samsung PM debug/UART helpers, ARM suspend/cacheflush, S5PV210 clock/power register definitions, and resume assembly.

### Integration Points
`s5pv210.c` calls `s5pv210_pm_init()` from DT late init. Pinctrl manages the external interrupt wake mask before this code reads it.

### Risks
The internal wake mask is currently a static all-masked value with a TODO for VIC wake support. If both internal and EINT masks are all ones, suspend is aborted. Wrong `INFORM0` or WFI configuration prevents resume.

### Test Signals
DT boot with `mem` suspend, EINT wake through pinctrl, UART restoration, wake-stat logging, and PM debug checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/pm.c -->
