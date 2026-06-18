<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk.c

### Purpose
`early_printk.c` registers a minimal boot console that writes characters through the platform `prom_putchar()` hook.

### Important APIs, Types, And Functions
It defines `early_console_write()`, static console `early_console_prom`, and initializer `setup_early_printk()`.

### Control Flow
The write callback emits carriage return before newline, then sends each character to `prom_putchar()`. Setup returns if an early console already exists; otherwise it assigns `early_console` and registers the boot console.

### State, Persistence, And Dependencies
State is the global `early_console` pointer and console registration. Dependencies include `prom_putchar()` from platform or 8250 early code, console core, and MIPS setup globals.

### Integration Points
Early boot printk uses this before full console drivers bind. `early_printk_8250.c` can provide the `prom_putchar()` backend.

### Risks
If `prom_putchar()` blocks or is unconfigured, early output can disappear or stall. This console should be boot-only and not confused with the final console.

### Test Signals
Boot with early printk, verify newline translation, duplicate setup avoidance, printbuffer replay, and handoff to normal console drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/early_printk.c -->
