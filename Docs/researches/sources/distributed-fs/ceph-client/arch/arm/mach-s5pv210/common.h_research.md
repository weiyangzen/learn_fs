<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/common.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/common.h

### Purpose
Declares common S5PV210 machine and PM entry points.

### Important APIs, Types, And Functions
`s5pv210_cpu_resume()` is the low-level resume symbol. `s5pv210_pm_init()` is declared when PM is enabled and stubbed otherwise.

### Control Flow
No direct flow. DT late init calls `s5pv210_pm_init()`, and PM code writes the physical resume symbol address before suspend.

### State, Persistence, And Dependencies
State lives in the implementation files and hardware registers. Depends on `CONFIG_PM`.

### Integration Points
Used by `s5pv210.c`, `pm.c`, and `sleep.S`.

### Risks
The PM stub means non-PM builds silently skip suspend setup. Resume symbol linkage must match the assembly implementation.

### Test Signals
Builds across PM configs and suspend/resume validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-s5pv210/common.h -->
