<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend_asm.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/power/suspend_asm.S

### Purpose
`suspend_asm.S` is the low-level Loongson-3 sleep/wakeup routine used for ACPI S3 suspend.

### Important APIs, Types, And Functions
Macros are `SETUP_SLEEP` and `SETUP_WAKEUP`. Symbols are `loongarch_suspend_enter` and global inner label `loongarch_wakeup_start`.

### Control Flow
The entry saves key registers on the stack, stores the saved stack pointer in `acpi_saved_sp`, flushes all caches, passes wakeup PC and SP to firmware through `a0/a1`, and calls the firmware suspend routine at `loongarch_suspend_addr`. Wakeup sets DMW windows, jumps to virtual addressing, enables paging via CRMD, reloads the saved stack pointer, restores registers, and returns.

### State, Persistence, And Dependencies
State includes stack-saved registers, `acpi_saved_sp`, firmware-provided sleep/wakeup context, DMW configuration, and CRMD paging state. Dependencies include cache flushing, address-space setup macros, LoongArch CSRs, and `loongarch_suspend_addr` from `suspend.c`.

### Integration Points
Called by `loongarch_acpi_suspend()`. Firmware calls back to `loongarch_wakeup_start` after resume.

### Risks
Firmware ABI assumptions are strict: argument registers, wakeup physical/virtual transition, and stack preservation must match platform firmware. Cache flushes before sleep are important for firmware visibility.

### Test Signals
ACPI S3 cycles on Loongson-3 hardware, firmware wake path tracing, cache coherency checks after resume, and objdump review of wakeup code alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/power/suspend_asm.S -->
