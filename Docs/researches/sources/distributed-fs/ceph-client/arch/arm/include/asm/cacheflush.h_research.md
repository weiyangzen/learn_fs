# sources/distributed-fs/ceph-client/arch/arm/include/asm/cacheflush.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cacheflush.h` declares and wraps ARM cache
maintenance operations for MMU changes, instruction/data coherency, user mappings, and DMA
visibility. It is part of the ARM kernel-architecture compatibility layer imported in the Ceph
client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and
board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASMARM_CACHEFLUSH_H`, `CACHE_COLOUR`, `PG_dcache_clean`, `__cpuc_flush_icache_all`,
`__cpuc_flush_kern_all`, `__cpuc_flush_kern_louis`, `__cpuc_flush_user_all`,
`__cpuc_flush_user_range`, `__cpuc_coherent_kern_range`, `__cpuc_coherent_user_range`,
`__cpuc_flush_dcache_area`, `dmac_flush_range`, `copy_from_user_page`, `__flush_icache_all_generic`,
`__flush_icache_all_v7_smp`, `__flush_icache_preferred`, `flush_cache_louis`, `flush_cache_all`, and
21 more; types: `cpu_cache_fns`, `mm_struct`, `page`; functions/prototypes:
`__cpuc_flush_icache_all`, `__cpuc_flush_kern_all`, `__cpuc_flush_kern_louis`,
`__cpuc_flush_user_all`, `__cpuc_flush_user_range`, `__cpuc_coherent_kern_range`,
`__cpuc_coherent_user_range`, `__cpuc_flush_dcache_area`, `dmac_flush_range`,
`__flush_icache_preferred`, `dsb`, `flush_cache_mm`, `flush_cache_range`, `flush_dcache_page`,
`flush_dcache_folio`, `__flush_anon_page`, `flush_cache_all`, `__cpuc_clean_dcache_area`, and 5
more. The file is 476 lines / 15507 bytes, and the exported surface is primarily an include-time
contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are normally used
from early boot, interrupt entry, or low-level driver paths where callers must already understand
local interrupt state. MMU and mapping helpers are reached from memory-management setup, page-table
transitions, highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.
Most behavior is selected through preprocessor branches, so the actual compiled path depends heavily
on `CONFIG_*`, CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `cpu_cache_fns`, `mm_struct`, `page`. External state or
implementation hooks include `cpu_cache`, `__cpuc_flush_icache_all`, `__cpuc_flush_kern_all`,
`__cpuc_flush_kern_louis`, `__cpuc_flush_user_all`, `__cpuc_flush_user_range`,
`__cpuc_coherent_kern_range`, `__cpuc_coherent_user_range`, and 4 more. DMA-visible state depends on
cache cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers.
There is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. Direct includes are `linux/mm.h`,
`asm/glue-cache.h`, `asm/shmparam.h`, `asm/cachetype.h`, `asm/outercache.h`. It integrates with
generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Barrier correctness depends on ARM memory-model semantics and the generic Linux
ordering APIs. Mapping helpers depend on page-table, vmalloc, highmem, or memory-type definitions
supplied elsewhere under `arch/arm`. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cacheflush.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce; callers must preserve interrupt-state assumptions and avoid using low-level
helpers from preemptible or wrong-context paths; incorrect address alignment, memory type, or cache
alias handling can corrupt data or make executable mappings incoherent; heavy preprocessor selection
creates configuration-specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and irqchip paths; run
MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
