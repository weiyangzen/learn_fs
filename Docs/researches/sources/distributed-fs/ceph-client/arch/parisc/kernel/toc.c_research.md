<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/toc.c

### Purpose
`toc.c` handles PA-RISC Transfer of Control events by converting firmware PIM data into `pt_regs`, printing diagnostics, optionally entering KGDB, and rebooting.

### Important APIs, Types, And Functions
It defines `toc_lock`, per-cpu `toc_stack`, `toc20_to_pt_regs()`, `toc11_to_pt_regs()`, `toc_intr()`, and early init `setup_toc()`.

### Control Flow
The assembly handler enters `toc_intr()` with a per-CPU stack-backed `pt_regs`. C code verifies the stack, fetches TOC PIM data through PDC depending on CPU generation, fills `pt_regs`, enters KGDB if configured, serializes `show_regs()` output, parks nonzero CPUs, waits for other CPUs to print, and restarts with reason `TOC`. Setup writes the physical TOC handler address and checksum into PAGE0.

### State, Persistence, And Dependencies
Persistent state includes PAGE0 TOC vector fields, handler checksum, per-CPU TOC stacks, and the output serialization lock. Dependencies include PDC PIM calls, KGDB, `show_regs()`, machine restart, and TOC assembly symbols.

### Integration Points
Installed as an early firmware-visible TOC vector; used for crash/debug transfer events.

### Risks
TOC runs in exceptional conditions with limited stack assumptions. The checksum and physical vector fields must match firmware rules. Secondary CPUs intentionally spin forever after printing.

### Test Signals
Firmware TOC injection, KGDB over TOC, multi-CPU backtrace serialization, PAGE0 vector checksum validation, and restart after monarch delay are the useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc.c -->
