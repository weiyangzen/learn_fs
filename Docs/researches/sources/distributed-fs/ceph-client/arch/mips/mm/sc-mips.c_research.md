<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-mips.c -->
## sources/distributed-fs/ceph-client/arch/mips/mm/sc-mips.c

### Purpose
`sc-mips.c` provides generic MIPS32/MIPS64 L2 cache detection and bcache operations for platforms using standard Config2 or CM3 L2 configuration registers.

### Important APIs, Types, And Functions
`mips_sc_wback_inv()` and `mips_sc_inv()` implement DMA cache maintenance. Prefetch control helpers use CM GCR L2 prefetch registers. `mips_sc_is_activated()`, `mips_sc_probe_cm3()`, and `mips_sc_probe()` populate `current_cpu_data.scache`. `mips_sc_init()` enables prefetch and installs `mips_sc_ops`.

### Control Flow
Probe first marks secondary cache not present, then uses CM3 L2 configuration when available or older Config1/Config2 fields otherwise. It rejects unsupported ISA or inactive/bypassed cache states, applies Ingenic XBurst corrections, fills sets/ways/line size/way size, clears the not-present flag, enables prefetch, and registers bcache operations.

### State, Persistence, And Dependencies
Persistent state is stored in `current_cpu_data.scache`, `current_cpu_data.options`, CM prefetch control registers, and the global `bcops` pointer. Dependencies include MIPS CM accessors, CP0 Config registers, cache op helpers, and machine type identifiers.

### Integration Points
The file feeds DMA cache maintenance, optional debugfs prefetch control, and CPU cache descriptors consumed by other architecture code. It is the generic L2 path for many MIPS cores.

### Risks
Config2 bit 12 is implementation-defined but interpreted as an L2 bypass bit for selected CPUs. Incorrect set/way/line decoding breaks cache flushing. Prefetch enable is gated on CM2.5+ and present prefetch units but still changes hardware performance behavior globally.

### Test Signals
Boot on representative CPUs covering Config2, CM3, QEMU generic, BMIPS, and XBurst overrides; validate reported cache geometry, DMA correctness, and debugfs prefetch enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/mm/sc-mips.c -->
