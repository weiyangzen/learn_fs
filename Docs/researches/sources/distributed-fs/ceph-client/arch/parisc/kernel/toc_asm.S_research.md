<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc_asm.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/toc_asm.S

### Purpose
`toc_asm.S` is the low-level firmware TOC handler that saves enough CPU state and switches to virtual kernel execution before calling `toc_intr()`.

### Important APIs, Types, And Functions
It exports `toc_handler`, `toc_handler_csum`, and `toc_handler_size`, and imports `toc_intr` and per-cpu `toc_stack`.

### Control Flow
The handler selects the per-CPU TOC stack on SMP, lays out and clears a `pt_regs`, saves FP registers, installs `swapper_pg_dir` into control registers, clears upper space registers, converts stack and argument pointers to virtual addresses, enables kernel virtual mapping, loads GP, and branches to `toc_intr()`.

### State, Persistence, And Dependencies
The handler's code bytes and checksum are consumed by firmware through PAGE0 fields set in `toc.c`. It depends on task CPU offsets, per-cpu offsets, page-table symbols, `virt_map`, and PA-RISC calling convention.

### Integration Points
Directly paired with `toc.c`; firmware enters this code on TOC.

### Risks
The checksum word is included in the firmware checksum span. Per-CPU stack selection depends on `cr30` still identifying the current task. Register save omissions limit what C can report.

### Test Signals
TOC injection on UP and SMP, FP register visibility in dumps, checksum acceptance by firmware, and successful transition from physical to virtual mode validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/toc_asm.S -->
