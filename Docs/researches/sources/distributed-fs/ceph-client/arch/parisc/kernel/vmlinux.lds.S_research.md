<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vmlinux.lds.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vmlinux.lds.S

### Purpose
`vmlinux.lds.S` defines the PA-RISC kernel image link layout, including init sections, text/data/BSS, GP/linkage tables, unwind tables, alignment constraints, and discarded sections.

### Important APIs, Types, And Functions
It sets output format/architecture, entry `parisc_kernel_start`, `jiffies` aliasing, `BSS_FIRST_SECTIONS`, long-call keep/discard macros, `_text/_stext/_etext`, `_sdata/_edata/_end`, `__start___unwind`, `__stop___unwind`, and 64-bit `.opd/.plt/.dlt` placement with `__gp`.

### Control Flow
The linker starts at `KERNEL_BINARY_TEXT_START`, emits init text/data/percpu/alternatives, aligns to huge pages, emits main text and RO data, places GP-sensitive linkage tables before RO data on 64-bit, emits `.PARISC.unwind`, writable data, lock-aligned data, BSS with page tables first, debug/modinfo/ELF details, notes, and architecture-specific discards.

### State, Persistence, And Dependencies
All kernel section addresses and linker-provided symbols persist in the final image. Dependencies include generic `vmlinux.lds.h`, PA-RISC cache/page/thread constants, unwind code, boot code, and binutils behavior.

### Integration Points
Consumed by boot, unwind initialization, alternatives, percpu setup, BSS/page-table assumptions, and module/debug metadata.

### Risks
`swapper_pg_dir` must remain first in BSS. `__gp` must stay below architectural limits. Section alignment impacts hugepage mapping, cache behavior, and early boot reachability.

### Test Signals
Link both 32-bit and 64-bit kernels, inspect section addresses, verify unwind symbols, boot with alternatives/percpu/BSS, and check no unwanted dynamic sections in static 64-bit images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vmlinux.lds.S -->
