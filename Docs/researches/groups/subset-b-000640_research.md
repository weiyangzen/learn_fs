# subset-b-000640 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/atomic.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/atomic.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/atomic.h` defines ARM-specific atomic
integer and, when enabled, atomic64 operations using LDREX/STREX loops on ARMv6+ or IRQ masking on
older uniprocessor builds. It is part of the ARM kernel-architecture compatibility layer imported in
the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver,
and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `arch_atomic_read`, `arch_atomic_set`, `ATOMIC_OP`, `ATOMIC_OP_RETURN`, `ATOMIC_FETCH_OP`,
`arch_atomic_add_return_relaxed`, `arch_atomic_sub_return_relaxed`, `arch_atomic_fetch_add_relaxed`,
`arch_atomic_fetch_sub_relaxed`, `arch_atomic_fetch_and_relaxed`,
`arch_atomic_fetch_andnot_relaxed`, `arch_atomic_fetch_or_relaxed`, `arch_atomic_fetch_xor_relaxed`,
`arch_atomic_cmpxchg_relaxed`, `arch_atomic_fetch_add_unless`, `arch_atomic_add_return`,
`arch_atomic_sub_return`, `arch_atomic_fetch_add`, and 26 more; functions/prototypes: `prefetchw`,
`smp_mb`, `raw_local_irq_save`, `raw_local_irq_restore`. The file is 514 lines / 12897 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are normally used
from early boot, interrupt entry, or low-level driver paths where callers must already understand
local interrupt state. Most behavior is selected through preprocessor branches, so the actual
compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/compiler.h`, `linux/prefetch.h`, `linux/types.h`, `linux/irqflags.h`, `asm/barrier.h`,
`asm/cmpxchg.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Barrier correctness depends on ARM memory-model
semantics and the generic Linux ordering APIs. Interrupt-related declarations integrate with generic
irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `atomic.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce; callers must preserve interrupt-state assumptions and avoid using low-level
helpers from preemptible or wrong-context paths; heavy preprocessor selection creates configuration-
specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and irqchip paths;
ensure all include users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/auxvec.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/auxvec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/auxvec.h` provides the ARM auxiliary-vector
architecture slot count used when constructing userspace process auxv entries. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
no public C API beyond the include guard and architecture constant payload. The file is 1 lines / 29
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `uapi/asm/auxvec.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `auxvec.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bL_switcher.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/bL_switcher.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/bL_switcher.h` declares the big.LITTLE
switcher API used to pair logical CPUs, trace switch events, and coordinate cluster migration
support. It is part of the ARM kernel-architecture compatibility layer imported in the Ceph client
source tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and board-
support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_BL_SWITCHER_H`, `BL_NOTIFY_PRE_ENABLE`, `BL_NOTIFY_POST_ENABLE`,
`BL_NOTIFY_PRE_DISABLE`, `BL_NOTIFY_POST_DISABLE`; functions/prototypes: `bL_switch_request_cb`,
`bL_switcher_register_notifier`, `bL_switcher_unregister_notifier`, `bL_switcher_get_enabled`,
`bL_switcher_put_enabled`, `bL_switcher_trace_trigger`, `bL_switcher_get_logical_index`. The file is
74 lines / 2186 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/compiler.h`, `linux/types.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `bL_switcher.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bL_switcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/barrier.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/barrier.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/barrier.h` implements ARM memory-barrier,
DMA-barrier, SMP-barrier, read/write-once, and speculative execution ordering helpers. It is part of
the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its
direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than
Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `nop`, `sev`, `wfe`, `wfi`, `isb`, `dsb`, `dmb`, `CSDB`, `csdb`, `__arm_heavy_mb`, `mb`,
`rmb`, `wmb`, `dma_rmb`, `dma_wmb`, `__smp_mb`, `__smp_rmb`, `__smp_wmb`, and 1 more;
functions/prototypes: `arm_heavy_mb`. The file is 103 lines / 2910 bytes, and the exported surface
is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence.

### State, Persistence, And Dependencies
External state or implementation hooks include `arm_heavy_mb`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. Direct includes are `asm-
generic/barrier.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Barrier correctness depends on ARM memory-model
semantics and the generic Linux ordering APIs. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `barrier.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; run DMA mapping, scatterlist, and noncoherent-device tests;
ensure all include users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bitops.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/bitops.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/bitops.h` provides ARM bit manipulation
primitives, including atomic bitops, non-atomic local bitops, find/ffz helpers, and little-endian
operation aliases. It is part of the ARM kernel-architecture compatibility layer imported in the
Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and
board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ATOMIC_BITOP`, `set_bit`, `clear_bit`, `change_bit`, `test_and_set_bit`,
`test_and_clear_bit`, `test_and_change_bit`, `find_first_zero_bit`, `find_next_zero_bit`,
`find_first_bit`, `find_next_bit`, `find_first_zero_bit_le`, `find_next_zero_bit_le`,
`find_next_bit_le`; functions/prototypes: `BIT_MASK`, `BIT_WORD`, `raw_local_irq_save`,
`raw_local_irq_restore`, `_set_bit`, `_clear_bit`, `_change_bit`, `_test_and_set_bit`,
`_test_and_clear_bit`, `_test_and_change_bit`, `_find_first_zero_bit_le`, `_find_first_bit_le`,
`_find_next_bit_le`, `_find_first_zero_bit_be`, `_find_first_bit_be`, `_find_next_bit_be`,
`_find_next_zero_bit_le`. The file is 278 lines / 7732 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
Ordering-sensitive helpers place barriers around the architectural operation so SMP, DMA, exception
return, or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are
normally used from early boot, interrupt entry, or low-level driver paths where callers must already
understand local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `_set_bit`, `_clear_bit`, `_change_bit`,
`_test_and_set_bit`, `_test_and_clear_bit`, `_test_and_change_bit`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `linux/compiler.h`, `linux/irqflags.h`,
`asm/barrier.h`, `asm-generic/bitops/non-atomic.h`, `asm-generic/bitops/__fls.h`, `asm-
generic/bitops/__ffs.h`, `asm-generic/bitops/fls.h`, `asm-generic/bitops/ffs.h`, `asm-
generic/bitops/builtin-__fls.h`, `asm-generic/bitops/builtin-__ffs.h`, and 9 more. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Barrier correctness depends on ARM memory-model semantics and the generic Linux
ordering APIs. Interrupt-related declarations integrate with generic irqchip, exception entry, and
per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `bitops.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
missing or misplaced barriers can create SMP, DMA, or device-ordering races that are hard to
reproduce; callers must preserve interrupt-state assumptions and avoid using low-level helpers from
preemptible or wrong-context paths.

### Test Signals
run SMP, lockdep, memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and
irqchip paths; ensure all include users still build with sparse/objtool-style diagnostics where
available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bitrev.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/bitrev.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/bitrev.h` uses ARM RBIT when available to
implement byte, halfword, and word bit reversal helpers. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `__asm__`. The file is 21 lines / 451 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `bitrev.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bitrev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bug.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/bug.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/bug.h` maps BUG/WARN traps onto undefined-
instruction encodings and exception-table metadata so ARM can recover diagnostic location data. It
is part of the ARM kernel-architecture compatibility layer imported in the Ceph client source tree,
so its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code
rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASMARM_BUG_H`, `BUG_INSTR_VALUE`, `BUG_INSTR`, `BUG`, `_BUG`, `__BUG`, `HAVE_ARCH_BUG`,
`FAULT_CODE_ALIGNMENT`, `FAULT_CODE_DEBUG`; types: `pt_regs`, `mm_struct`; functions/prototypes:
`die`, `show_pte`, `__show_regs`, `__show_regs_alloc_free`, `c_backtrace`. The file is 93 lines /
2620 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. MMU and mapping
helpers are reached from memory-management setup, page-table transitions, highmem/fixmap setup, or
device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `pt_regs`, `mm_struct`. External state or implementation
hooks include `c_backtrace`, `__show_regs`, `__show_regs_alloc_free`. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. Direct includes are `linux/linkage.h`,
`linux/types.h`, `asm/opcodes.h`, `asm-generic/bug.h`. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit. Mapping
helpers depend on page-table, vmalloc, highmem, or memory-type definitions supplied elsewhere under
`arch/arm`.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `bug.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; incorrect address alignment, memory type, or cache alias handling can corrupt
data or make executable mappings incoherent.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run MMU, highmem,
ioremap, kexec, and cache/TLB coherency tests; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bugs.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/bugs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/bugs.h` declares CPU bug checking entry
points for ARM boot and CPU bring-up. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `check_other_bugs`; functions/prototypes: `check_writebuffer_bugs`, `check_other_bugs`. The
file is 16 lines / 297 bytes, and the exported surface is primarily an include-time contract for
other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `check_writebuffer_bugs`, `check_other_bugs`. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `bugs.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/bugs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cache.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cache.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cache.h` defines ARM cache-line sizing
constants and L1 cache shift globals used by generic cache and DMA code. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `ARCH_SLAB_MINALIGN`,
`__read_mostly`; functions/prototypes: `cache_line_size`. The file is 35 lines / 896 bytes, and the
exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and
device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
run DMA mapping, scatterlist, and noncoherent-device tests; ensure all include users still build
with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cacheflush.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cacheflush.h

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cachetype.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cachetype.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cachetype.h` decodes the global cache type
value and exposes helpers for VIVT, VIPT, PIPT, Harvard, and aliasing cache properties. It is part
of the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its
direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than
Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `CACHEID_VIVT`, `CACHEID_VIPT_NONALIASING`, `CACHEID_VIPT_ALIASING`, `CACHEID_VIPT`,
`CACHEID_ASID_TAGGED`, `CACHEID_VIPT_I_ALIASING`, `CACHEID_PIPT`, `cache_is_vivt`, `cache_is_vipt`,
`cache_is_vipt_nonaliasing`, `cache_is_vipt_aliasing`, `icache_is_vivt_asid_tagged`,
`icache_is_vipt_aliasing`, `icache_is_pipt`, `cpu_dcache_is_aliasing`, `__CACHEID_ARCH_MIN`,
`__CACHEID_ALWAYS`, `__CACHEID_NEVER`, and 9 more; functions/prototypes: `writel`, `readl`,
`cacheid`. The file is 114 lines / 3096 bytes, and the exported surface is primarily an include-time
contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Register
definitions are passive until board, CPU, debug, or device drivers read/write the corresponding MMIO
or coprocessor state. Most behavior is selected through preprocessor branches, so the actual
compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
External state or implementation hooks include `cacheid`. Hardware state lives in CP15/CP14
registers or MMIO registers and persists independently of the header; the header only names access
patterns. There is no userspace filesystem persistence in this file; persistence is either kernel
memory, CPU register state, hardware register state, or generated ABI values. Direct includes are
`linux/io.h`, `asm/v7m.h`. It integrates with generic Linux ARM architecture code through include-
time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cachetype.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; register bit definitions are hardware-specific and can fault or misconfigure
hardware if used on the wrong CPU or SoC; heavy preprocessor selection creates configuration-
specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; validate on matching
hardware or emulation with register-level smoke tests; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/checksum.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/checksum.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/checksum.h` declares ARM networking
checksum helpers and provides fold/csum_add/csum_sub/csum_tcpudp_nofold inline operations. It is
part of the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so
its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather
than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_HAVE_ARCH_COPY_AND_CSUM_FROM_USER`, `_HAVE_ARCH_CSUM_AND_COPY`, `_HAVE_ARCH_IPV6_CSUM`;
functions/prototypes: `csum_partial`, `csum_partial_copy_nocheck`, `csum_partial_copy_from_user`,
`return`, `csum_fold`, `htonl`. The file is 166 lines / 4053 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/in6.h`, `linux/uaccess.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `checksum.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/clocksource.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/clocksource.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/clocksource.h` declares ARM clocksource
initialization glue for generic timekeeping. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_CLOCKSOURCE_H`. The file is 7 lines / 161 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/vdso/clocksource.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `clocksource.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cmpxchg.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cmpxchg.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cmpxchg.h` implements ARM cmpxchg/xchg
primitives, including exclusive-access loops, pre-ARMv6 IRQ-protected fallbacks, and size dispatch.
It is part of the ARM kernel-architecture compatibility layer imported in the Ceph client source
tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code
rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `swp_is_buggy`, `arch_xchg_relaxed`, `arch_xchg`, `arch_cmpxchg_local`,
`arch_cmpxchg64_local`, `arch_cmpxchg_relaxed`, `arch_cmpxchg64_relaxed`; functions/prototypes:
`__bad_xchg`, `prefetchw`, `raw_local_irq_save`, `raw_local_irq_restore`, `__bad_cmpxchg`,
`cmpxchg_emu_u8`, `__generic_cmpxchg_local`, `__cmpxchg`. The file is 285 lines / 6463 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are normally used
from early boot, interrupt entry, or low-level driver paths where callers must already understand
local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `__bad_xchg`, `__bad_cmpxchg`. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. Direct includes are `linux/irqflags.h`,
`linux/prefetch.h`, `asm/barrier.h`, `linux/cmpxchg-emu.h`, `asm-generic/cmpxchg-local.h`, `asm-
generic/cmpxchg.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Barrier correctness depends on ARM memory-model
semantics and the generic Linux ordering APIs. Interrupt-related declarations integrate with generic
irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cmpxchg.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce; callers must preserve interrupt-state assumptions and avoid using low-level
helpers from preemptible or wrong-context paths.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and irqchip paths;
ensure all include users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/compiler.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/compiler.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/compiler.h` defines compiler attributes for
ARM exception-table offset handling and unaligned packed structures. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `__asmeq`. The file is 29 lines / 978 bytes, and the exported surface is primarily an
include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `compiler.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cp15.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cp15.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cp15.h` wraps ARM CP15 system control
coprocessor reads and writes for barriers, control register manipulation, and thread/PID registers.
It is part of the ARM kernel-architecture compatibility layer imported in the Ceph client source
tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code
rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `CR_M`, `CR_A`, `CR_C`, `CR_W`, `CR_P`, `CR_D`, `CR_L`, `CR_B`, `CR_S`, `CR_R`, `CR_F`,
`CR_Z`, `CR_I`, `CR_V`, `CR_RR`, `CR_L4`, `CR_DT`, `CR_HA`, and 16 more; functions/prototypes:
`asm`, `isb`, `cr_alignment`. The file is 122 lines / 3302 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
External state or implementation hooks include `cr_alignment`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `asm/barrier.h`, `asm/vdso/cp15.h`. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Barrier correctness depends on ARM memory-model semantics and the
generic Linux ordering APIs.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cp15.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cp15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cpu.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cpu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cpu.h` defines the per-CPU architecture
descriptor used by CPU registration and topology exposure. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
types: `cpuinfo_arm`; functions/prototypes: `DECLARE_PER_CPU`. The file is 22 lines / 370 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `cpuinfo_arm`. There is no userspace filesystem persistence
in this file; persistence is either kernel memory, CPU register state, hardware register state, or
generated ABI values. Direct includes are `linux/percpu.h`, `linux/cpu.h`. It integrates with
generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cpu.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cpufeature.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cpufeature.h` provides ARM CPU feature
override types and helpers for late CPU feature masking. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `MAX_CPU_FEATURES`, `__hwcap_feature`, `__hwcap2_feature`, `cpu_feature`;
functions/prototypes: `BIT`. The file is 35 lines / 1291 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/log2.h`, `asm/hwcap.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cpufeature.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cpuidle.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cpuidle.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cpuidle.h` declares CPU-idle entry points
and device-tree initialization for ARM idle drivers. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__cpuidle_method_section`, `ARM_CPUIDLE_WFI_STATE_PWR`, `ARM_CPUIDLE_WFI_STATE`,
`CPUIDLE_METHOD_OF_DECLARE`, `arm_cpuidle_save_irq_context`, `arm_cpuidle_restore_irq_context`;
types: `cpuidle_driver`, `device_node`, `cpuidle_ops`, `of_cpuidle_method`,
`arm_cpuidle_irq_context`; functions/prototypes: `arm_cpuidle_suspend`, `arm_cpuidle_init`,
`arm_cpuidle_simple_enter`. The file is 58 lines / 1628 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `cpuidle_driver`, `device_node`, `cpuidle_ops`,
`of_cpuidle_method`, `arm_cpuidle_irq_context`. External state or implementation hooks include
`arm_cpuidle_simple_enter`, `arm_cpuidle_suspend`, `arm_cpuidle_init`. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. Direct includes are `asm/proc-fns.h`. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cpuidle.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cputype.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/cputype.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cputype.h` defines implementer/part IDs,
CPU architecture decoding, CPUID reads, cache ID reads, and helper predicates for ARM core
detection. It is part of the ARM kernel-architecture compatibility layer imported in the Ceph client
source tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and board-
support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `CPUID_ID`, `CPUID_CACHETYPE`, `CPUID_TCM`, `CPUID_TLBTYPE`, `CPUID_MPUIR`, `CPUID_MPIDR`,
`CPUID_REVIDR`, `CPUID_EXT_PFR0`, `CPUID_EXT_PFR1`, `CPUID_EXT_DFR0`, `CPUID_EXT_AFR0`,
`CPUID_EXT_MMFR0`, `CPUID_EXT_MMFR1`, `CPUID_EXT_MMFR2`, `CPUID_EXT_MMFR3`, `CPUID_EXT_ISAR0`,
`CPUID_EXT_ISAR1`, `CPUID_EXT_ISAR2`, and 57 more; types: `proc_info_list`; functions/prototypes:
`lookup_processor`, `readl`, `read_cpuid`, `read_cpuid_id`, `processor_id`. The file is 348 lines /
8886 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Register
definitions are passive until board, CPU, debug, or device drivers read/write the corresponding MMIO
or coprocessor state. Most behavior is selected through preprocessor branches, so the actual
compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `proc_info_list`. External state or implementation hooks
include `processor_id`. Hardware state lives in CP15/CP14 registers or MMIO registers and persists
independently of the header; the header only names access patterns. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `linux/stringify.h`, `linux/kernel.h`,
`asm/io.h`, `asm/v7m.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cputype.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; register bit definitions are hardware-specific and can fault or misconfigure
hardware if used on the wrong CPU or SoC; heavy preprocessor selection creates configuration-
specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; validate on matching
hardware or emulation with register-level smoke tests; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/cputype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/current.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/current.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/current.h` implements efficient current
task lookup through TPIDRPRW/TPIDRURO or stack masking depending on CPU and SMP configuration. It is
part of the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so
its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather
than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_CURRENT_H`, `current`; types: `task_struct`; functions/prototypes:
`__builtin_thread_pointer`, `asm`, `__current`. The file is 65 lines / 1844 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
Caller-visible state is represented by `task_struct`. External state or implementation hooks include
`__current`. There is no userspace filesystem persistence in this file; persistence is either kernel
memory, CPU register state, hardware register state, or generated ABI values. Direct includes are
`asm/insn.h`. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `current.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dcc.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/dcc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/dcc.h` provides debug communications
channel CP14 polling and byte I/O helpers. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `isb`. The file is 33 lines / 623 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/barrier.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Barrier correctness depends on ARM memory-model
semantics and the generic Linux ordering APIs.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dcc.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/delay.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/delay.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/delay.h` declares ARM delay-loop
calibration state and maps udelay/ndelay/mdelay to architecture-aware delay backends. It is part of
the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its
direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than
Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `MAX_UDELAY_MS`, `UDELAY_MULT`, `UDELAY_SHIFT`, `__delay`, `__udelay`, `__const_udelay`,
`udelay`, `ARCH_HAS_READ_CURRENT_TIMER`; types: `delay_timer`; functions/prototypes: `__bad_udelay`,
`__loop_delay`, `__loop_udelay`, `__loop_const_udelay`, `register_current_timer_delay`. The file is
100 lines / 2901 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `delay_timer`. External state or implementation hooks include
`__bad_udelay`, `__loop_delay`, `__loop_udelay`, `__loop_const_udelay`,
`register_current_timer_delay`. There is no userspace filesystem persistence in this file;
persistence is either kernel memory, CPU register state, hardware register state, or generated ABI
values. Direct includes are `asm/page.h`, `asm/param.h`. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `delay.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/device.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/device.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/device.h` adds ARM-specific per-device DMA
metadata and arch setup hooks. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASMARM_DEVICE_H`, `to_dma_iommu_mapping`; types: `dev_archdata`, `dma_iommu_mapping`,
`omap_device`, `pdev_archdata`. The file is 29 lines / 533 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `dev_archdata`, `dma_iommu_mapping`, `omap_device`,
`pdev_archdata`. DMA-visible state depends on cache cleanliness, bus mappings, and device/platform
data owned by the DMA mapping or driver layers. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit. Mapping helpers depend on page-table, vmalloc, highmem,
or memory-type definitions supplied elsewhere under `arch/arm`. DMA paths integrate with cache
maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `device.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/div64.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/div64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/div64.h` selects optimized ARM 64-bit
division helpers and generic div64 fallbacks. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__div64_32`, `do_div`, `__arch_xprod_64`; functions/prototypes: `asm`. The file is 118
lines / 2754 bytes, and the exported surface is primarily an include-time contract for other kernel
files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/types.h`, `asm/compiler.h`, `asm-generic/div64.h`. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `div64.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/div64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dma-iommu.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/dma-iommu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/dma-iommu.h` declares ARM DMA/IOMMU mapping
helpers for attaching devices, mapping scatterlists, and managing IOVA cookies. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `ASMARM_DMA_IOMMU_H`; types: `dma_iommu_mapping`, `iommu_domain`, `kref`;
functions/prototypes: `arm_iommu_create_mapping`, `arm_iommu_release_mapping`,
`arm_iommu_detach_device`. The file is 36 lines / 906 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `dma_iommu_mapping`, `iommu_domain`, `kref`. DMA-visible
state depends on cache cleanliness, bus mappings, and device/platform data owned by the DMA mapping
or driver layers. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/mm_types.h`, `linux/scatterlist.h`, `linux/kref.h`. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit. Mapping
helpers depend on page-table, vmalloc, highmem, or memory-type definitions supplied elsewhere under
`arch/arm`. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dma-iommu.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dma-iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dma.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/dma.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/dma.h` defines ISA-style DMA constants,
cache alignment requirements, DMA addressability checks, and old DMA-channel hooks. It is part of
the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its
direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than
Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `MAX_DMA_ADDRESS`, `ARCH_LOW_ADDRESS_LIMIT`, `DMA_MODE_MASK`, `DMA_MODE_READ`,
`DMA_MODE_WRITE`, `DMA_MODE_CASCADE`, `DMA_AUTOINIT`, `clear_dma_ff`, `set_dma_addr`, `NO_DMA`;
functions/prototypes: `raw_spin_lock_irqsave`, `raw_spin_unlock_irqrestore`, `set_dma_page`,
`request_dma`, `free_dma`, `enable_dma`, `disable_dma`, `dma_channel_active`, `set_dma_sg`,
`__set_dma_addr`, `set_dma_count`, `set_dma_mode`, `set_dma_speed`, `get_dma_residue`,
`arm_dma_zone_size`, `arm_dma_limit`, `dma_spin_lock`. The file is 149 lines / 4268 bytes, and the
exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `arm_dma_zone_size`, `arm_dma_limit`,
`dma_spin_lock`, `set_dma_page`, `request_dma`, `free_dma`, `enable_dma`, `disable_dma`, and 7 more.
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values.
Direct includes are `linux/spinlock.h`, `linux/scatterlist.h`, `mach/isa-dma.h`. It integrates with
generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Interrupt-related declarations integrate with generic irqchip, exception entry,
and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and
device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dma.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dmi.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/dmi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/dmi.h` adapts DMI support for ARM by
conditionally enabling SMBIOS availability. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `dmi_early_remap`, `dmi_early_unmap`, `dmi_remap`, `dmi_unmap`, `dmi_alloc`. The file is 15
lines / 378 bytes, and the exported surface is primarily an include-time contract for other kernel
files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/io.h`, `linux/slab.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dmi.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/domain.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/domain.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/domain.h` defines ARM domain access control
constants and inline helpers for switching DACR/domain state. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `DOMAIN_KERNEL`, `DOMAIN_USER`, `DOMAIN_IO`, `DOMAIN_VECTORS`, `DOMAIN_NOACCESS`,
`DOMAIN_CLIENT`, `DOMAIN_MANAGER`, `domain_mask`, `domain_val`, `DACR_INIT`, `__DACR_DEFAULT`,
`DACR_UACCESS_DISABLE`, `DACR_UACCESS_ENABLE`, `TUSER`, `TUSERCOND`; functions/prototypes:
`current_thread_info`, `isb`. The file is 141 lines / 3429 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/thread_info.h`, `asm/barrier.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit. Barrier correctness
depends on ARM memory-model semantics and the generic Linux ordering APIs.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `domain.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ecard.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/ecard.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/ecard.h` declares expansion-card data
structures and driver registration APIs for Acorn-style ARM ecard buses. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `MANU_ACORN`, `PROD_ACORN_SCSI`, `PROD_ACORN_ETHER1`, `PROD_ACORN_MFM`, `MANU_ANT2`,
`PROD_ANT_ETHER3`, `MANU_ATOMWIDE`, `PROD_ATOMWIDE_3PSERIAL`, `MANU_IRLAM_INSTRUMENTS`,
`MANU_IRLAM_INSTRUMENTS_ETHERN`, `MANU_OAK`, `PROD_OAK_SCSI`, `MANU_MORLEY`,
`PROD_MORLEY_SCSI_UNCACHED`, `MANU_CUMANA`, `PROD_CUMANA_SCSI_2`, `PROD_CUMANA_SCSI_1`, `MANU_ICS`,
and 40 more; types: `ecard_id`, `in_ecid`, `expansion_card`, `device`, `resource`, `in_chunk_dir`,
`ecard_driver`, `device_driver`, `ecard_t`, `loader_t`, `expansion_card_ops`; functions/prototypes:
`ecard_setirq`, `ecard_readchunk`, `ecard_request_resources`, `ecard_release_resources`,
`ecard_register_driver`, `ecard_remove_driver`, `ecard_bus_type`. The file is 219 lines / 6125
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `ecard_id`, `in_ecid`, `expansion_card`, `device`,
`resource`, `in_chunk_dir`, `ecard_driver`, `device_driver`, and 3 more. External state or
implementation hooks include `ecard_readchunk`, `ecard_request_resources`,
`ecard_release_resources`, `ecard_bus_type`. DMA-visible state depends on cache cleanliness, bus
mappings, and device/platform data owned by the DMA mapping or driver layers. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. It integrates with generic Linux ARM architecture
code through include-time contracts rather than a standalone translation unit. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ecard.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ecard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/edac.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/edac.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/edac.h` provides ARM EDAC hooks for memory
error reporting integration. It is part of the ARM kernel-architecture compatibility layer imported
in the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt,
driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_EDAC_H`. The file is 38 lines / 995 bytes, and the exported surface is primarily an
include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and
device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `edac.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run DMA mapping,
scatterlist, and noncoherent-device tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/edac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/efi.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/efi.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/efi.h` declares ARM EFI runtime mapping,
boot services, and memory map helpers. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `arch_efi_call_virt_setup`, `arch_efi_call_virt_teardown`, `arch_efi_call_virt`,
`ARCH_EFI_IRQ_FLAGS_MASK`, `arm_efi_init`, `MAX_UNCOMP_KERNEL_SIZE`, `EFI_PHYS_ALIGN`; types:
`efi_arm_entry_state`; functions/prototypes: `efi_init`, `arm_efi_init`, `efi_create_mapping`,
`efi_set_mapping_permissions`, `check_and_switch_context`, `efi_virtmap_load`, `efi_virtmap_unload`,
`__cpuc_flush_dcache_area`. The file is 94 lines / 2678 bytes, and the exported surface is primarily
an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. MMU and mapping helpers are reached from
memory-management setup, page-table transitions, highmem/fixmap setup, or device mapping code rather
than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `efi_arm_entry_state`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `asm/cacheflush.h`, `asm/cachetype.h`,
`asm/early_ioremap.h`, `asm/fixmap.h`, `asm/highmem.h`, `asm/mach/map.h`, `asm/mmu_context.h`,
`asm/ptrace.h`, `asm/uaccess.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. Mapping helpers depend on page-
table, vmalloc, highmem, or memory-type definitions supplied elsewhere under `arch/arm`. Interrupt-
related declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting
code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `efi.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; incorrect address alignment, memory type, or cache alias handling can
corrupt data or make executable mappings incoherent.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run MMU, highmem, ioremap, kexec, and
cache/TLB coherency tests; ensure all include users still build with sparse/objtool-style
diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/elf.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/elf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/elf.h` defines ARM ELF ABI constants,
register sets, hwcap export, core-dump state, and executable personality handling. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `ELF_NGREG`, `EF_ARM_EABI_MASK`, `EF_ARM_EABI_UNKNOWN`, `EF_ARM_EABI_VER1`,
`EF_ARM_EABI_VER2`, `EF_ARM_EABI_VER3`, `EF_ARM_EABI_VER4`, `EF_ARM_EABI_VER5`, `EF_ARM_BE8`,
`EF_ARM_LE8`, `EF_ARM_MAVERICK_FLOAT`, `EF_ARM_VFP_FLOAT`, `EF_ARM_SOFT_FLOAT`, `EF_ARM_OLD_ABI`,
`EF_ARM_NEW_ABI`, `EF_ARM_ALIGN8`, `EF_ARM_PIC`, `EF_ARM_MAPSYMSFIRST`, and 49 more; types:
`task_struct`, `elf32_hdr`, `linux_binprm`, `elf_greg_t`, `elf_fpregset_t`; functions/prototypes:
`elf_check_arch`, `arm_elf_read_implies_exec`, `elf_set_personality`, `arch_setup_additional_pages`.
The file is 155 lines / 4693 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it. Most behavior is selected through preprocessor branches, so
the actual compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board
configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `task_struct`, `elf32_hdr`, `linux_binprm`, `elf_greg_t`,
`elf_fpregset_t`. External state or implementation hooks include `elf_check_arch`,
`arm_elf_read_implies_exec`, `elf_set_personality`. There is no userspace filesystem persistence in
this file; persistence is either kernel memory, CPU register state, hardware register state, or
generated ABI values. Direct includes are `asm/auxvec.h`, `asm/hwcap.h`, `asm/ptrace.h`,
`asm/user.h`. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `elf.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/exception.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/exception.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/exception.h` marks exception entry/exit
functions with ARM-specific asmlinkage attributes. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__exception_irq_entry`. The file is 15 lines / 416 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/interrupt.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Interrupt-related declarations integrate with
generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `exception.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fiq.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/fiq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fiq.h` declares fast interrupt ownership,
handler installation, register save state, and enable/disable interfaces. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
types: `fiq_handler`; functions/prototypes: `claim_fiq`, `release_fiq`, `set_fiq_handler`,
`enable_fiq`, `disable_fiq`, `__set_fiq_regs`, `__get_fiq_regs`. The file is 57 lines / 1391 bytes,
and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `fiq_handler`. External state or implementation hooks include
`claim_fiq`, `release_fiq`, `set_fiq_handler`, `enable_fiq`, `disable_fiq`, `__set_fiq_regs`,
`__get_fiq_regs`. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/ptrace.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Interrupt-related declarations integrate with
generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fiq.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fiq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/firmware.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/firmware.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/firmware.h` defines firmware operation
tables for SoC reset, idle, suspend, SMP boot, and hotplug hooks. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `call_firmware_op`; types: `firmware_ops`; functions/prototypes: `BUG_ON`, `firmware_ops`.
The file is 79 lines / 1728 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `firmware_ops`. External state or implementation hooks
include `firmware_ops`. There is no userspace filesystem persistence in this file; persistence is
either kernel memory, CPU register state, hardware register state, or generated ABI values. Direct
includes are `linux/bug.h`. It integrates with generic Linux ARM architecture code through include-
time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `firmware.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fixmap.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/fixmap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fixmap.h` defines ARM fixed virtual address
slots for early ioremap, vectors, PCI I/O, text patching, and highmem mappings. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_FIXMAP_H`, `FIXADDR_START`, `FIXADDR_END`, `FIXADDR_TOP`, `NR_FIX_BTMAPS`,
`FIX_BTMAPS_SLOTS`, `TOTAL_FIX_BTMAPS`, `FIXMAP_PAGE_COMMON`, `FIXMAP_PAGE_NORMAL`,
`FIXMAP_PAGE_RO`, `FIXMAP_PAGE_IO`, `FIXMAP_PAGE_NOCACHE`, `__early_set_fixmap`; types:
`fixed_addresses`; functions/prototypes: `__set_fixmap`, `early_fixmap_init`. The file is 66 lines /
1881 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/pgtable.h`, `asm/kmap_size.h`, `asm-generic/fixmap.h`. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.
Mapping helpers depend on page-table, vmalloc, highmem, or memory-type definitions supplied
elsewhere under `arch/arm`.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fixmap.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; ensure all include users still
build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/floppy.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/floppy.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/floppy.h` provides ARM legacy floppy I/O,
DMA, and virtual DMA compatibility definitions. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `fd_outb`, `fd_inb`, `fd_request_irq`, `fd_free_irq`, `fd_disable_irq`, `fd_enable_irq`,
`fd_dma_setup`, `fd_request_dma`, `fd_free_dma`, `fd_disable_dma`, `DMA_FLOPPYDISK`, `FDC1`,
`FLOPPY0_TYPE`, `FLOPPY1_TYPE`, `N_FDC`, `N_DRIVE`, `EXTRA_FLOPPY_PARAMS`; functions/prototypes:
`set_dma_mode`, `__set_dma_addr`, `set_dma_count`, `enable_dma`, `swap`. The file is 81 lines / 2289
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `floppy.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fncpy.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/fncpy.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fncpy.h` provides helpers for copying
functions to executable memory while preserving PC-relative execution assumptions. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `FNCPY_ALIGN`, `fncpy`. The file is 82 lines / 2552 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/types.h`, `linux/string.h`, `asm/bug.h`, `asm/cacheflush.h`. It integrates with generic
Linux ARM architecture code through include-time contracts rather than a standalone translation
unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fncpy.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fncpy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fpstate.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/fpstate.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fpstate.h` defines floating-point/VFP
context structures saved in threads and signal frames. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `FP_HARD_SIZE`, `FP_SOFT_SIZE`, `IWMMXT_SIZE`, `FP_SIZE`; types: `vfp_hard_struct`,
`vfp_state`, `fp_hard_struct`, `fp_soft_struct`, `iwmmxt_struct`, `fp_state`. The file is 79 lines /
1377 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `vfp_hard_struct`, `vfp_state`, `fp_hard_struct`,
`fp_soft_struct`, `iwmmxt_struct`, `fp_state`. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fpstate.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fpstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fpu.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/fpu.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fpu.h` declares ARM FPU initialization and
context-preservation hooks. It is part of the ARM kernel-architecture compatibility layer imported
in the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt,
driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `kernel_fpu_available`, `kernel_fpu_begin`, `kernel_fpu_end`. The file is 15 lines / 309
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/neon.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fpu.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ftrace.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/ftrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/ftrace.h` declares ARM ftrace patching
types and graph tracing hooks. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_FTRACE`, `HAVE_FUNCTION_GRAPH_FP_TEST`, `ARCH_SUPPORTS_FTRACE_OPS`, `MCOUNT_ADDR`,
`MCOUNT_INSN_SIZE`, `ftrace_return_address`, `ARCH_HAS_SYSCALL_MATCH_SYM_NAME`; types:
`dyn_arch_ftrace`, `module`; functions/prototypes: `__gnu_mcount_nc`, `return_address`,
`strcasecmp`. The file is 84 lines / 2006 bytes, and the exported surface is primarily an include-
time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `dyn_arch_ftrace`, `module`. External state or implementation
hooks include `__gnu_mcount_nc`. There is no userspace filesystem persistence in this file;
persistence is either kernel memory, CPU register state, hardware register state, or generated ABI
values. It integrates with generic Linux ARM architecture code through include-time contracts rather
than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ftrace.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/futex.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/futex.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/futex.h` implements ARM futex atomic
operations through user-access assembly sequences and exception-table fixups. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_FUTEX_H`, `__futex_atomic_ex_table`, `__futex_atomic_op`; functions/prototypes:
`smp_mb`, `prefetchw`, `uaccess_save_and_enable`, `uaccess_restore`, `preempt_disable`,
`preempt_enable`, `__futex_atomic_op`. The file is 180 lines / 4357 bytes, and the exported surface
is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`, `linux/preempt.h`, `asm/domain.h`. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Barrier correctness depends on ARM memory-model semantics and the
generic Linux ordering APIs.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `futex.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-cache.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-cache.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-cache.h` selects cache maintenance
implementations according to CPU/cache configuration. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_GLUE_CACHE_H`, `MULTI_CACHE`, `_CACHE`, `__cpuc_flush_icache_all`,
`__cpuc_flush_kern_all`, `__cpuc_flush_kern_louis`, `__cpuc_flush_user_all`,
`__cpuc_flush_user_range`, `__cpuc_coherent_kern_range`, `__cpuc_coherent_user_range`,
`__cpuc_flush_dcache_area`, `dmac_flush_range`. The file is 151 lines / 2950 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values.
Direct includes are `asm/glue.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. DMA paths integrate with cache
maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `glue-cache.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
run DMA mapping, scatterlist, and noncoherent-device tests; ensure all include users still build
with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-df.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-df.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-df.h` selects data-abort handler
implementations according to CPU family configuration. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_GLUE_DF_H`, `MULTI_DABORT`, `CPU_DABORT_HANDLER`. The file is 99 lines / 2110 bytes,
and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/glue.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Mapping helpers depend on page-table, vmalloc,
highmem, or memory-type definitions supplied elsewhere under `arch/arm`.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `glue-df.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; ensure all include users still
build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-df.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-pf.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-pf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-pf.h` selects prefetch-abort handler
implementations according to CPU family configuration. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_GLUE_PF_H`, `MULTI_PABORT`, `CPU_PABORT_HANDLER`. The file is 54 lines / 1005 bytes,
and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/glue.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `glue-pf.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-proc.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-proc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-proc.h` selects processor helper
implementations for the configured ARM CPU families. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_GLUE_PROC_H`, `MULTI_CPU`, `CPU_NAME`, `cpu_proc_init`, `cpu_proc_fin`, `cpu_reset`,
`cpu_do_idle`, `cpu_dcache_clean_area`, `cpu_do_switch_mm`, `cpu_set_pte_ext`, `cpu_suspend_size`,
`cpu_do_suspend`, `cpu_do_resume`. The file is 261 lines / 4424 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/glue.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Mapping helpers depend on page-table, vmalloc,
highmem, or memory-type definitions supplied elsewhere under `arch/arm`.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `glue-proc.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; ensure all include users still
build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue-proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/glue.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/glue.h` provides token-pasting helpers used
by ARM glue headers to bind CPU/cache implementation symbols. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `____glue`, `__glue`. The file is 22 lines / 613 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `glue.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardirq.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardirq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardirq.h` connects ARM hardirq accounting
to generic irq_cpustat storage. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__ARCH_IRQ_EXIT_IRQS_DISABLED`, `ack_bad_irq`. The file is 12 lines / 246 bytes, and the
exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/irq.h`, `asm-generic/hardirq.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hardirq.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-aurora-l2.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-aurora-l2.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-aurora-l2.h` declares
Marvell Aurora L2 cache controller init, suspend, and broadcast maintenance hooks. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `AURORA_SYNC_REG`, `AURORA_RANGE_BASE_ADDR_REG`, `AURORA_FLUSH_PHY_ADDR_REG`,
`AURORA_INVAL_RANGE_REG`, `AURORA_CLEAN_RANGE_REG`, `AURORA_FLUSH_RANGE_REG`,
`AURORA_ACR_REPLACEMENT_OFFSET`, `AURORA_ACR_REPLACEMENT_MASK`, `AURORA_ACR_REPLACEMENT_TYPE_WAYRR`,
`AURORA_ACR_REPLACEMENT_TYPE_LFSR`, `AURORA_ACR_REPLACEMENT_TYPE_SEMIPLRU`, `AURORA_ACR_PARITY_EN`,
`AURORA_ACR_ECC_EN`, `AURORA_ACR_FORCE_WRITE_POLICY_OFFSET`, `AURORA_ACR_FORCE_WRITE_POLICY_MASK`,
`AURORA_ACR_FORCE_WRITE_POLICY_DIS`, `AURORA_ACR_FORCE_WRITE_BACK_POLICY`,
`AURORA_ACR_FORCE_WRITE_THRO_POLICY`, and 33 more. The file is 100 lines / 3451 bytes, and the
exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it. Most behavior is selected through preprocessor branches, so
the actual compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board
configuration.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache-aurora-l2.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-aurora-l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-b15-rac.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-b15-rac.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-b15-rac.h` declares Broadcom
Brahma-B15 RAC cache controller enable/disable and flush hooks. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
functions/prototypes: `b15_flush_kern_cache_all`. The file is 10 lines / 162 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache-b15-rac.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-b15-rac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-feroceon-l2.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-feroceon-l2.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-feroceon-l2.h` declares
Feroceon L2 cache initialization for Marvell ARM SoCs. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `feroceon_l2_init`, `feroceon_of_init`. The file is 9 lines / 251 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `feroceon_l2_init`, `feroceon_of_init`. There is no
userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache-feroceon-l2.h`.
In the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-feroceon-l2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-l2x0.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-l2x0.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-l2x0.h` defines
PL310/L2C-2x0 cache controller register offsets, bit fields, and platform init/PM APIs. It is part
of the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its
direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than
Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `L2X0_CACHE_ID`, `L2X0_CACHE_TYPE`, `L2X0_CTRL`, `L2X0_AUX_CTRL`, `L310_TAG_LATENCY_CTRL`,
`L310_DATA_LATENCY_CTRL`, `L2X0_EVENT_CNT_CTRL`, `L2X0_EVENT_CNT1_CFG`, `L2X0_EVENT_CNT0_CFG`,
`L2X0_EVENT_CNT1_VAL`, `L2X0_EVENT_CNT0_VAL`, `L2X0_INTR_MASK`, `L2X0_MASKED_INTR_STAT`,
`L2X0_RAW_INTR_STAT`, `L2X0_INTR_CLEAR`, `L2X0_CACHE_SYNC`, `L2X0_DUMMY_REG`, `L2X0_INV_LINE_PA`,
and 97 more; types: `l2x0_regs`; functions/prototypes: `l2x0_init`, `l2x0_of_init`,
`l2x0_pmu_register`, `l2x0_pmu_suspend`, `l2x0_pmu_resume`, `l2x0_saved_regs`. The file is 192 lines
/ 6377 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it. Most behavior is selected through preprocessor branches, so
the actual compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board
configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `l2x0_regs`. External state or implementation hooks include
`l2x0_init`, `l2x0_of_init`, `l2x0_saved_regs`. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. Direct includes are `linux/errno.h`, `linux/init.h`, `linux/types.h`. It integrates with
generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache-l2x0.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-l2x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-tauros2.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-tauros2.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-tauros2.h` declares Tauros2
L2 cache initialization and resume hooks. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `CACHE_TAUROS2_PREFETCH_ON`, `CACHE_TAUROS2_LINEFILL_BURST8`; functions/prototypes:
`tauros2_init`. The file is 11 lines / 295 bytes, and the exported surface is primarily an include-
time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `tauros2_init`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache-tauros2.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-tauros2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-uniphier.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-uniphier.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-uniphier.h` declares
Socionext UniPhier outer-cache initialization. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__CACHE_UNIPHIER_H`; functions/prototypes: `uniphier_cache_init`. The file is 21 lines /
411 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/errno.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cache-uniphier.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cache-uniphier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cp14.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cp14.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cp14.h` maps ARM CP14 debug and
trace registers to inline MRC/MCR accessor macros. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `dbg_read`, `dbg_write`, `etm_read`, `etm_write`, `MRC14`, `MCR14`, `RCP14_DBGDIDR`,
`RCP14_DBGDSCRint`, `RCP14_DBGDTRRXint`, `RCP14_DBGWFAR`, `RCP14_DBGVCR`, `RCP14_DBGECR`,
`RCP14_DBGDSCCR`, `RCP14_DBGDSMCR`, `RCP14_DBGDTRRXext`, `RCP14_DBGDSCRext`, `RCP14_DBGDTRTXext`,
`RCP14_DBGDRCR`, and 446 more. The file is 534 lines / 25160 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Register
definitions are passive until board, CPU, debug, or device drivers read/write the corresponding MMIO
or coprocessor state. Most behavior is selected through preprocessor branches, so the actual
compiled path depends heavily on `CONFIG_*`, CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
Hardware state lives in CP15/CP14 registers or MMIO registers and persists independently of the
header; the header only names access patterns. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. Direct includes are `linux/types.h`. It integrates with generic Linux ARM architecture
code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cp14.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; register bit definitions are hardware-specific and can fault or misconfigure
hardware if used on the wrong CPU or SoC; heavy preprocessor selection creates configuration-
specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; validate on matching
hardware or emulation with register-level smoke tests; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/cp14.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/dec21285.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/dec21285.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/dec21285.h` defines DEC 21285 host
bridge register layout, IRQ lines, timer, UART, and PCI window constants. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `DC21285_PCI_IACK`, `DC21285_ARMCSR_BASE`, `DC21285_PCI_TYPE_0_CONFIG`,
`DC21285_PCI_TYPE_1_CONFIG`, `DC21285_OUTBOUND_WRITE_FLUSH`, `DC21285_FLASH`, `DC21285_PCI_IO`,
`DC21285_PCI_MEM`, `DC21285_IO`, `BUS_OFFSET`, `CSR_PCICMD`, `CSR_CLASSREV`, `CSR_PCICACHELINESIZE`,
`CSR_PCICSRBASE`, `CSR_PCICSRIOBASE`, `CSR_PCISDRAMBASE`, `CSR_PCIROMBASE`, `CSR_MBOX0`, and 95
more. The file is 138 lines / 5222 bytes, and the exported surface is primarily an include-time
contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values.
Direct includes are `mach/hardware.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dec21285.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/dec21285.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ioc.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ioc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ioc.h` defines Acorn IOC register
layout, timers, IRQ/FIQ masks, and keyboard/serial hardware constants. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `ioc_readb`, `ioc_writeb`, `IOC_CONTROL`, `IOC_KARTTX`, `IOC_KARTRX`, `IOC_IRQSTATA`,
`IOC_IRQREQA`, `IOC_IRQCLRA`, `IOC_IRQMASKA`, `IOC_IRQSTATB`, `IOC_IRQREQB`, `IOC_IRQMASKB`,
`IOC_FIQSTAT`, `IOC_FIQREQ`, `IOC_FIQMASK`, `IOC_T0CNTL`, `IOC_T0LTCHL`, `IOC_T0CNTH`, and 21 more.
The file is 69 lines / 1549 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Interrupt-related declarations integrate with generic irqchip, exception entry,
and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ioc.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ioc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/iomd.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/iomd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/iomd.h` defines Acorn IOMD/IOMD2
register maps for timers, DMA, IRQs, video, sound, and keyboard hardware. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `iomd_readb`, `iomd_readl`, `iomd_writeb`, `iomd_writel`, `IOMD_CONTROL`, `IOMD_KARTTX`,
`IOMD_KARTRX`, `IOMD_KCTRL`, `IOMD_IRQSTATA`, `IOMD_IRQREQA`, `IOMD_IRQCLRA`, `IOMD_IRQMASKA`,
`IOMD_IRQSTATB`, `IOMD_IRQREQB`, `IOMD_IRQMASKB`, `IOMD_FIQSTAT`, `IOMD_FIQREQ`, `IOMD_FIQMASK`, and
91 more; functions/prototypes: `vram_half_sam`. The file is 182 lines / 4225 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
External state or implementation hooks include `vram_half_sam`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.
Interrupt-related declarations integrate with generic irqchip, exception entry, and per-CPU irq
accounting code. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and device model
code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `iomd.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/iomd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/locomo.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/locomo.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/locomo.h` declares Sharp LoCoMo
companion-chip registers, subdevice IDs, and driver helper APIs. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARCH_LOCOMO`, `locomo_writel`, `locomo_readl`, `LOCOMO_VER`, `LOCOMO_ST`,
`LOCOMO_C32K`, `LOCOMO_ICR`, `LOCOMO_MCSX0`, `LOCOMO_MCSX1`, `LOCOMO_MCSX2`, `LOCOMO_MCSX3`,
`LOCOMO_ASD`, `LOCOMO_HSD`, `LOCOMO_HSC`, `LOCOMO_TADC`, `LOCOMO_LTC`, `LOCOMO_LTINT`, `LOCOMO_DAC`,
and 99 more; types: `locomo_dev`, `device`, `locomo_driver`, `device_driver`,
`locomo_platform_data`; functions/prototypes: `locomolcd_power`, `locomo_driver_register`,
`locomo_driver_unregister`, `locomo_gpio_set_dir`, `locomo_gpio_read_level`,
`locomo_gpio_read_output`, `locomo_gpio_write`, `locomo_m62332_senddata`, `locomo_frontlight_set`.
The file is 217 lines / 7083 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `locomo_dev`, `device`, `locomo_driver`, `device_driver`,
`locomo_platform_data`. External state or implementation hooks include `locomolcd_power`. DMA-
visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the DMA
mapping or driver layers. There is no userspace filesystem persistence in this file; persistence is
either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `locomo.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/locomo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/memc.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/memc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/memc.h` defines Acorn MEMC
register offsets and page size constants. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `VDMA_ALIGNMENT`, `VDMA_XFERSIZE`, `VDMA_INIT`, `VDMA_START`, `VDMA_END`, `video_set_dma`;
functions/prototypes: `memc_write`. The file is 23 lines / 550 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `memc_write`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `memc.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
run DMA mapping, scatterlist, and noncoherent-device tests; ensure all include users still build
with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/memc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/sa1111.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/sa1111.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/sa1111.h` declares Intel/StrongARM
SA-1111 companion-chip subdevices, IRQs, platform data, and helper APIs. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARCH_SA1111`, `SA1111_SAC_DMA_MIN_XFER`, `SA1111_SKCR`, `SA1111_SMCR`, `SA1111_SKID`,
`SKCR_PLL_BYPASS`, `SKCR_RCLKEN`, `SKCR_SLEEP`, `SKCR_DOZE`, `SKCR_VCO_OFF`, `SKCR_SCANTSTEN`,
`SKCR_CLKTSTEN`, `SKCR_RDYEN`, `SKCR_SELAC`, `SKCR_OPPC`, `SKCR_PLLTSTEN`, `SKCR_USBIOTSTEN`,
`SKCR_OE_EN`, and 204 more; types: `sa1111_dev`, `device`, `resource`, `sa1111_driver`,
`device_driver`, `sa1111_platform_data`; functions/prototypes: `sa1111_enable_device`,
`sa1111_disable_device`, `sa1111_get_irq`, `sa1111_pll_clock`, `sa1111_select_audio_mode`,
`sa1111_set_audio_rate`, `sa1111_get_audio_rate`, `sa1111_check_dma_bug`, `sa1111_driver_register`,
`sa1111_driver_unregister`, `sa1111_bus_type`. The file is 442 lines / 12646 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `sa1111_dev`, `device`, `resource`, `sa1111_driver`,
`device_driver`, `sa1111_platform_data`. External state or implementation hooks include
`sa1111_bus_type`. DMA-visible state depends on cache cleanliness, bus mappings, and device/platform
data owned by the DMA mapping or driver layers. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit. Interrupt-related declarations integrate with generic
irqchip, exception entry, and per-CPU irq accounting code. DMA paths integrate with cache
maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `sa1111.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/sa1111.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/scoop.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/scoop.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/scoop.h` declares Sharp SCOOP
GPIO/controller register data and platform helper APIs. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `SCOOP_MCR`, `SCOOP_CDR`, `SCOOP_CSR`, `SCOOP_CPR`, `SCOOP_CCR`, `SCOOP_IRR`, `SCOOP_IRM`,
`SCOOP_IMR`, `SCOOP_ISR`, `SCOOP_GPCR`, `SCOOP_GPWR`, `SCOOP_GPRR`, `SCOOP_CPR_OUT`,
`SCOOP_CPR_SD_3V`, `SCOOP_CPR_CF_XV`, `SCOOP_CPR_CF_3V`, `SCOOP_GPCR_PA22`, `SCOOP_GPCR_PA21`, and
10 more; types: `scoop_config`, `scoop_pcmcia_dev`, `device`, `scoop_pcmcia_config`;
functions/prototypes: `reset_scoop`, `read_scoop_reg`, `write_scoop_reg`, `platform_scoop_config`.
The file is 67 lines / 1822 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `scoop_config`, `scoop_pcmcia_dev`, `device`,
`scoop_pcmcia_config`. External state or implementation hooks include `platform_scoop_config`. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.
Interrupt-related declarations integrate with generic irqchip, exception entry, and per-CPU irq
accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `scoop.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/scoop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ssp.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ssp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ssp.h` declares StrongARM SSP
register bits and SPI-like transfer helpers. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `SSP_H`; types: `ssp_state`; functions/prototypes: `ssp_write_word`, `ssp_read_word`,
`ssp_flush`, `ssp_enable`, `ssp_disable`, `ssp_save_state`, `ssp_restore_state`, `ssp_init`,
`ssp_exit`. The file is 25 lines / 480 bytes, and the exported surface is primarily an include-time
contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `ssp_state`. There is no userspace filesystem persistence in
this file; persistence is either kernel memory, CPU register state, hardware register state, or
generated ABI values. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ssp.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ssp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/highmem.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/highmem.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/highmem.h` defines ARM highmem kmap slots,
PKMAP sizing, and kmap flush helpers. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_HIGHMEM_H`, `PKMAP_BASE`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR`, `PKMAP_ADDR`,
`flush_cache_kmaps`, `ARCH_NEEDS_KMAP_HIGH_GET`, `arch_kmap_local_high_get`,
`arch_kmap_local_post_map`, `arch_kmap_local_pre_unmap`, `arch_kmap_local_post_unmap`;
functions/prototypes: `kmap_high_get`, `pkmap_page_table`. The file is 78 lines / 2397 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. MMU and mapping helpers are reached from
memory-management setup, page-table transitions, highmem/fixmap setup, or device mapping code rather
than from normal filesystem paths.

### State, Persistence, And Dependencies
External state or implementation hooks include `pkmap_page_table`, `kmap_high_get`. There is no
userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. Direct includes are `asm/cachetype.h`,
`asm/fixmap.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Mapping helpers depend on page-table, vmalloc,
highmem, or memory-type definitions supplied elsewhere under `arch/arm`. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `highmem.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; incorrect address alignment, memory type, or cache alias handling can
corrupt data or make executable mappings incoherent.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run MMU, highmem, ioremap, kexec, and
cache/TLB coherency tests; ensure all include users still build with sparse/objtool-style
diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb-3level.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb-3level.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb-3level.h` defines hugepage PTE
layout helpers for ARM LPAE/three-level page tables. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_HUGETLB_3LEVEL_H`, `__HAVE_ARCH_HUGE_PTEP_GET`. The file is 29 lines / 740 bytes,
and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Mapping helpers depend on page-table, vmalloc, highmem, or memory-type definitions
supplied elsewhere under `arch/arm`.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hugetlb-3level.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; ensure all include users still
build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb-3level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb.h` declares ARM hugetlb page setup
and hugepage PTE helpers. It is part of the ARM kernel-architecture compatibility layer imported in
the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver,
and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_HUGETLB_H`, `arch_clear_hugetlb_flags`; functions/prototypes: `clear_bit`. The
file is 24 lines / 543 bytes, and the exported surface is primarily an include-time contract for
other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/cacheflush.h`, `asm/page.h`, `asm/hugetlb-3level.h`, `asm-generic/hugetlb.h`. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hugetlb.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_breakpoint.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_breakpoint.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_breakpoint.h` defines ARM hardware
breakpoint/watchpoint control fields and debug architecture limits. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ARM_HW_BREAKPOINT_H`, `ARM_DEBUG_ARCH_RESERVED`, `ARM_DEBUG_ARCH_V6`,
`ARM_DEBUG_ARCH_V6_1`, `ARM_DEBUG_ARCH_V7_ECP14`, `ARM_DEBUG_ARCH_V7_MM`, `ARM_DEBUG_ARCH_V7_1`,
`ARM_DEBUG_ARCH_V8`, `ARM_DEBUG_ARCH_V8_1`, `ARM_DEBUG_ARCH_V8_2`, `ARM_DEBUG_ARCH_V8_4`,
`ARM_BREAKPOINT_EXECUTE`, `ARM_BREAKPOINT_LOAD`, `ARM_BREAKPOINT_STORE`, `ARM_FSR_ACCESS_MASK`,
`ARM_BREAKPOINT_PRIV`, `ARM_BREAKPOINT_USER`, `ARM_BREAKPOINT_LEN_1`, and 24 more; types:
`task_struct`, `arch_hw_breakpoint_ctrl`, `arch_hw_breakpoint`, `perf_event_attr`, `notifier_block`,
`perf_event`, `pmu`; functions/prototypes: `arch_check_bp_in_kernelspace`, `arch_get_debug_arch`,
`arch_get_max_wp_len`, `clear_ptrace_hw_breakpoint`, `arch_install_hw_breakpoint`,
`arch_uninstall_hw_breakpoint`, `hw_breakpoint_pmu_read`, `hw_breakpoint_slots`,
`arch_bp_generic_fields`, `hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`. The file is
146 lines / 3848 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Most behavior is
selected through preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`,
CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `task_struct`, `arch_hw_breakpoint_ctrl`,
`arch_hw_breakpoint`, `perf_event_attr`, `notifier_block`, `perf_event`, `pmu`. External state or
implementation hooks include `arch_bp_generic_fields`, `arch_check_bp_in_kernelspace`,
`hw_breakpoint_arch_parse`, `hw_breakpoint_exceptions_notify`, `arch_get_debug_arch`,
`arch_get_max_wp_len`, `clear_ptrace_hw_breakpoint`. There is no userspace filesystem persistence in
this file; persistence is either kernel memory, CPU register state, hardware register state, or
generated ABI values. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hw_breakpoint.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_irq.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_irq.h` declares ARM interrupt-controller
initialization and generic handle_arch_irq integration. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ARCH_ARM_HW_IRQ_H`, `ARCH_IRQ_INIT_FLAGS`; functions/prototypes: `pr_crit`,
`irq_err_count`. The file is 17 lines / 349 bytes, and the exported surface is primarily an include-
time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `irq_err_count`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. Interrupt-related declarations
integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hw_irq.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hwcap.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hwcap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hwcap.h` defines ARM ELF HWCAP and HWCAP2
feature bits exposed to userspace. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ELF_HWCAP`, `ELF_HWCAP2`; functions/prototypes: `elf_hwcap2`. The file is 16 lines / 378
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `elf_hwcap2`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `uapi/asm/hwcap.h`. It integrates with generic
Linux ARM architecture code through include-time contracts rather than a standalone translation
unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hwcap.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hypervisor.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/hypervisor.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hypervisor.h` declares ARM hypervisor
detection and setup hooks. It is part of the ARM kernel-architecture compatibility layer imported in
the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver,
and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_HYPERVISOR_H`; functions/prototypes: `kvm_init_hyp_services`,
`kvm_arm_hyp_service_available`. The file is 12 lines / 282 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/xen/hypervisor.h`. It integrates with generic Linux ARM architecture code through include-
time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `hypervisor.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/idmap.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/idmap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/idmap.h` declares identity-mapping setup
for MMU transition, suspend, and secondary CPU bring-up paths. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `__idmap`; functions/prototypes: `setup_mm_for_reboot`, `idmap_pgd`. The file is 15 lines /
359 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
External state or implementation hooks include `idmap_pgd`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. Direct includes are
`linux/compiler.h`, `linux/pgtable.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit. Mapping helpers depend on
page-table, vmalloc, highmem, or memory-type definitions supplied elsewhere under `arch/arm`. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `idmap.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/idmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/insn.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/insn.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/insn.h` defines ARM/Thumb instruction
encoding helpers used by patching, probes, and instruction decoders. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `LOAD_SYM_ARMV6`; functions/prototypes: `__arm_gen_branch`. The file is 47 lines / 1317
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/types.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `insn.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/io.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/io.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/io.h` defines ARM raw MMIO, port-I/O
emulation, ioremap, memcpy_to/fromio, barriers, and endian-aware accessor APIs. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `isa_virt_to_bus`, `isa_bus_to_virt`, `__raw_readw`, `__raw_writew`, `__raw_writeb`,
`__raw_writel`, `__raw_readb`, `__raw_readl`, `MT_DEVICE`, `MT_DEVICE_NONSHARED`,
`MT_DEVICE_CACHED`, `MT_DEVICE_WC`, `IOMEM`, `__iormb`, `__iowmb`, `PCI_IO_VIRT_BASE`, `PCI_IOBASE`,
`pci_remap_iospace`, and 51 more; types: `resource`, `pci_dev`; functions/prototypes:
`atomic_io_modify`, `atomic_io_modify_relaxed`, `__raw_writesb`, `__raw_writesw`, `__raw_writesl`,
`__raw_readsb`, `__raw_readsw`, `__raw_readsl`, `__arm_ioremap_pfn`, `__arm_ioremap_exec`,
`__arm_iomem_set_ro`, `__readwrite_bug`, `pci_ioremap_set_mem_type`, `pci_remap_iospace`,
`pci_remap_cfgspace`, `_memcpy_fromio`, `_memcpy_toio`, `_memset_io`, and 15 more. The file is 429
lines / 14159 bytes, and the exported surface is primarily an include-time contract for other kernel
files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence. MMU and mapping helpers are
reached from memory-management setup, page-table transitions, highmem/fixmap setup, or device
mapping code rather than from normal filesystem paths. Register definitions are passive until board,
CPU, debug, or device drivers read/write the corresponding MMIO or coprocessor state. Most behavior
is selected through preprocessor branches, so the actual compiled path depends heavily on
`CONFIG_*`, CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `resource`, `pci_dev`. External state or implementation hooks
include `atomic_io_modify`, `atomic_io_modify_relaxed`, `__arm_ioremap_caller`, `__arm_ioremap_pfn`,
`__arm_ioremap_exec`, `__readwrite_bug`, `_memcpy_fromio`, `_memcpy_toio`, and 10 more. Hardware
state lives in CP15/CP14 registers or MMIO registers and persists independently of the header; the
header only names access patterns. DMA-visible state depends on cache cleanliness, bus mappings, and
device/platform data owned by the DMA mapping or driver layers. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `linux/string.h`, `linux/types.h`,
`asm/byteorder.h`, `asm/page.h`, `asm-generic/pci_iomap.h`, `asm/barrier.h`, `mach/io.h`, `asm-
generic/io.h`. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit. Barrier correctness depends on ARM memory-model semantics
and the generic Linux ordering APIs. Mapping helpers depend on page-table, vmalloc, highmem, or
memory-type definitions supplied elsewhere under `arch/arm`. DMA paths integrate with cache
maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `io.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce; incorrect address alignment, memory type, or cache alias handling can corrupt
data or make executable mappings incoherent; register bit definitions are hardware-specific and can
fault or misconfigure hardware if used on the wrong CPU or SoC; heavy preprocessor selection creates
configuration-specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; run MMU, highmem, ioremap, kexec, and cache/TLB coherency
tests; run DMA mapping, scatterlist, and noncoherent-device tests; validate on matching hardware or
emulation with register-level smoke tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/irq.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/irq.h` defines ARM IRQ constants and
irqchip initialization hooks. It is part of the ARM kernel-architecture compatibility layer imported
in the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt,
driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `NR_IRQS_LEGACY`, `NR_IRQS`, `irq_canonicalize`, `NO_IRQ`, `arch_trigger_cpumask_backtrace`;
types: `irqaction`, `pt_regs`; functions/prototypes: `handle_IRQ`, `arch_trigger_cpumask_backtrace`.
The file is 47 lines / 808 bytes, and the exported surface is primarily an include-time contract for
other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `irqaction`, `pt_regs`. External state or implementation
hooks include `arch_trigger_cpumask_backtrace`. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. Direct includes are `mach/irqs.h`, `linux/cpumask.h`. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.
Interrupt-related declarations integrate with generic irqchip, exception entry, and per-CPU irq
accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `irq.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/irq_work.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/irq_work.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/irq_work.h` selects whether ARM supports
self-IPIs for generic irq_work. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `is_smp`. The file is 12 lines / 234 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Ordering-sensitive helpers place barriers around the architectural operation so SMP, DMA, exception
return, or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are
normally used from early boot, interrupt entry, or low-level driver paths where callers must already
understand local interrupt state.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/smp_plat.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Barrier correctness depends on ARM memory-model
semantics and the generic Linux ordering APIs. Interrupt-related declarations integrate with generic
irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `irq_work.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
missing or misplaced barriers can create SMP, DMA, or device-ordering races that are hard to
reproduce; callers must preserve interrupt-state assumptions and avoid using low-level helpers from
preemptible or wrong-context paths.

### Test Signals
run SMP, lockdep, memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and
irqchip paths; ensure all include users still build with sparse/objtool-style diagnostics where
available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/irqflags.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/irqflags.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/irqflags.h` implements local IRQ flag
save/restore and enable/disable using CPSR or CPS instructions. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `IRQMASK_REG_NAME_R`, `IRQMASK_REG_NAME_W`, `IRQMASK_I_BIT`, `arch_local_irq_save`,
`arch_local_irq_enable`, `arch_local_irq_disable`, `local_fiq_enable`, `local_fiq_disable`,
`local_abt_enable`, `local_abt_disable`, `arch_local_save_flags`, `arch_local_irq_restore`,
`arch_irqs_disabled_flags`. The file is 187 lines / 3969 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. IRQ/FIQ helpers
are normally used from early boot, interrupt entry, or low-level driver paths where callers must
already understand local interrupt state.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/ptrace.h`, `asm-generic/irqflags.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `irqflags.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; callers must preserve interrupt-state assumptions and avoid using low-level
helpers from preemptible or wrong-context paths.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; exercise boot,
interrupt entry/exit, and irqchip paths; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/jump_label.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/jump_label.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/jump_label.h` defines ARM static-key/jump-
label patch records and branch generation constraints. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_JUMP_LABEL_H`, `JUMP_LABEL_NOP_SIZE`, `ARCH_STATIC_BRANCH_ASM`; types:
`jump_entry`, `jump_label_t`. The file is 53 lines / 1151 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `jump_entry`, `jump_label_t`. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. Direct includes are `linux/types.h`,
`asm/unified.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `jump_label.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan.h` declares KASAN shadow setup and
init hooks for ARM. It is part of the ARM kernel-architecture compatibility layer imported in the
Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and
board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `KASAN_SHADOW_SCALE_SHIFT`; functions/prototypes: `kasan_early_init`, `kasan_init`. The file
is 33 lines / 708 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `kasan_init`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. Direct includes are `asm/kasan_def.h`. It integrates with generic
Linux ARM architecture code through include-time contracts rather than a standalone translation
unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kasan.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan_def.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan_def.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan_def.h` defines ARM KASAN shadow
address layout and scale constants. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `KASAN_SHADOW_SCALE_SHIFT`, `KASAN_SHADOW_OFFSET`, `KASAN_SHADOW_END`, `KASAN_SHADOW_START`.
The file is 81 lines / 2726 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kasan_def.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kasan_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec-internal.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec-internal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec-internal.h` declares ARM internal
kexec relocation and soft-restart helpers. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ARM_KEXEC_INTERNAL_H`; types: `kexec_relocate_data`. The file is 12 lines / 272 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `kexec_relocate_data`. There is no userspace filesystem
persistence in this file; persistence is either kernel memory, CPU register state, hardware register
state, or generated ABI values. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kexec-internal.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec.h` defines ARM kexec architecture
limits, machine_kexec hooks, and crash relocation state. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ARM_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`,
`KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `KEXEC_ARM_ATAGS_OFFSET`,
`KEXEC_ARM_ZIMAGE_OFFSET`, `ARCH_HAS_KIMAGE_ARCH`, `phys_to_boot_phys`, `boot_phys_to_phys`,
`page_to_boot_pfn`, `boot_pfn_to_page`; types: `kimage_arch`, `pt_regs`; functions/prototypes:
`memcpy`, `phys_to_idmap`, `idmap_to_phys`, `page_to_pfn`, `pfn_to_page`. The file is 83 lines /
2207 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
Caller-visible state is represented by `kimage_arch`, `pt_regs`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kexec.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run DMA mapping,
scatterlist, and noncoherent-device tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kfence.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kfence.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kfence.h` defines ARM KFENCE pool
mapping/protection hooks. It is part of the ARM kernel-architecture compatibility layer imported in
the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver,
and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `PFN_DOWN`, `pte_alloc_one_kernel`, `set_pte_ext`, `pmd_populate_kernel`,
`flush_tlb_kernel_range`, `is_kfence_address`, `pmd_off_k`, `set_memory_valid`. The file is 53 lines
/ 1058 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/kfence.h`, `asm/pgalloc.h`, `asm/set_memory.h`. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit. Mapping
helpers depend on page-table, vmalloc, highmem, or memory-type definitions supplied elsewhere under
`arch/arm`.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kfence.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; ensure all include users still
build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kgdb.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kgdb.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kgdb.h` defines ARM KGDB breakpoint
encoding, register layout, and trap integration. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__ARM_KGDB_H__`, `BREAK_INSTR_SIZE`, `GDB_BREAKINST`, `KGDB_BREAKINST`,
`KGDB_COMPILED_BREAK`, `CACHE_FLUSH_IS_SAFE`, `_GP_REGS`, `_FP_REGS`, `_EXTRA_REGS`, `GDB_MAX_REGS`,
`DBG_MAX_REG_NUM`, `KGDB_MAX_NO_CPUS`, `BUFMAX`, `NUMREGBYTES`, `NUMCRITREGBYTES`, `_R0`, `_R1`,
`_R2`, and 15 more; functions/prototypes: `asm`, `kgdb_handle_bus_error`, `kgdb_fault_expected`. The
file is 107 lines / 2783 bytes, and the exported surface is primarily an include-time contract for
other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Most behavior is
selected through preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`,
CPU architecture level, and board configuration.

### State, Persistence, And Dependencies
External state or implementation hooks include `kgdb_handle_bus_error`, `kgdb_fault_expected`. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. Direct includes are
`linux/ptrace.h`, `asm/opcodes.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kgdb.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kprobes.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/kprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kprobes.h` declares ARM kprobe instruction
slots, per-probe architecture data, and breakpoint helpers. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ARM_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot`,
`kretprobe_blacklist_size`, `arch_specific_insn`, `MAX_OPTIMIZED_LENGTH`, `MAX_OPTINSN_SIZE`,
`RELATIVEJUMP_SIZE`, `MAX_COPIED_INSN`; types: `kprobe`, `prev_kprobe`, `kprobe_ctlblk`,
`arch_optimized_insn`, `kprobe_opcode_t`; functions/prototypes: `arch_remove_kprobe`,
`kprobe_fault_handler`. The file is 78 lines / 2150 bytes, and the exported surface is primarily an
include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `kprobe`, `prev_kprobe`, `kprobe_ctlblk`,
`arch_optimized_insn`, `kprobe_opcode_t`. There is no userspace filesystem persistence in this file;
persistence is either kernel memory, CPU register state, hardware register state, or generated ABI
values. Direct includes are `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`,
`linux/notifier.h`, `asm/probes.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kprobes.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/krait-l2-accessors.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/krait-l2-accessors.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/krait-l2-accessors.h` declares Qualcomm
Krait L2 accessor helpers. It is part of the ARM kernel-architecture compatibility layer imported in
the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt, driver,
and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `krait_set_l2_indirect_reg`, `krait_get_l2_indirect_reg`. The file is 9 lines
/ 231 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `krait_set_l2_indirect_reg`,
`krait_get_l2_indirect_reg`. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `krait-l2-accessors.h`.
In the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/krait-l2-accessors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/linkage.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/linkage.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/linkage.h` adds ARM assembler linkage
annotations such as ENDPROC and alignment conventions. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__ALIGN`, `__ALIGN_STR`, `ENDPROC`. The file is 12 lines / 216 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `linkage.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/arch.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/arch.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/arch.h` defines the ARM machine
descriptor and MACHINE_START/MACHINE_END macros used by board files. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `smp_ops`, `smp_init_ops`, `for_each_machine_desc`, `MACHINE_START`, `MACHINE_END`,
`DT_MACHINE_START`; types: `tag`, `pt_regs`, `smp_operations`, `machine_desc`, `reboot_mode`;
functions/prototypes: `bool`, `machine_desc`. The file is 95 lines / 2653 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
Ordering-sensitive helpers place barriers around the architectural operation so SMP, DMA, exception
return, or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are
normally used from early boot, interrupt entry, or low-level driver paths where callers must already
understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `tag`, `pt_regs`, `smp_operations`, `machine_desc`. External
state or implementation hooks include `machine_desc`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. Direct includes are
`linux/types.h`, `linux/reboot.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. Barrier correctness depends on ARM
memory-model semantics and the generic Linux ordering APIs. Interrupt-related declarations integrate
with generic irqchip, exception entry, and per-CPU irq accounting code. DMA paths integrate with
cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `arch.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
missing or misplaced barriers can create SMP, DMA, or device-ordering races that are hard to
reproduce; callers must preserve interrupt-state assumptions and avoid using low-level helpers from
preemptible or wrong-context paths.

### Test Signals
run SMP, lockdep, memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and
irqchip paths; run DMA mapping, scatterlist, and noncoherent-device tests; ensure all include users
still build with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/dma.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/dma.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/dma.h` defines legacy ARM machine DMA
channel structures and controller hooks. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
types: `dma_struct`, `dma_ops`, `scatterlist`, `dma_t`; functions/prototypes: `isa_dma_add`. The
file is 46 lines / 1367 bytes, and the exported surface is primarily an include-time contract for
other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `dma_struct`, `dma_ops`, `scatterlist`, `dma_t`. External
state or implementation hooks include `isa_dma_add`. DMA-visible state depends on cache cleanliness,
bus mappings, and device/platform data owned by the DMA mapping or driver layers. There is no
userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dma.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
run DMA mapping, scatterlist, and noncoherent-device tests; ensure all include users still build
with sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/flash.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/flash.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/flash.h` declares machine flash
partition and set-VPP callbacks. It is part of the ARM kernel-architecture compatibility layer
imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASMARM_MACH_FLASH_H`; types: `mtd_partition`, `mtd_info`, `flash_platform_data`. The file
is 36 lines / 1029 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `mtd_partition`, `mtd_info`, `flash_platform_data`. There is
no userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. It integrates with generic Linux ARM
architecture code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `flash.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/flash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/irq.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/irq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/irq.h` declares machine interrupt
initialization hooks and chained IRQ helpers. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `do_bad_IRQ`; types: `seq_file`; functions/prototypes: `init_FIQ`, `show_fiq_list`. The file
is 30 lines / 587 bytes, and the exported surface is primarily an include-time contract for other
kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `seq_file`. External state or implementation hooks include
`init_FIQ`, `show_fiq_list`. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values.
Direct includes are `linux/irq.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. Interrupt-related declarations
integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `irq.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/map.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/map.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/map.h` defines static MMIO mapping
descriptors and iotable initialization APIs. It is part of the ARM kernel-architecture compatibility
layer imported in the Ceph client source tree, so its direct consumers are kernel architecture, MM,
interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `iotable_init`, `vm_reserve_area_early`; types: `map_desc`, `mem_type`;
functions/prototypes: `iotable_init`, `debug_ll_addr`, `debug_ll_io_init`, `get_mem_type`,
`vm_reserve_area_early`, `create_mapping_late`, `ioremap_page`. The file is 65 lines / 1479 bytes,
and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
MMU and mapping helpers are reached from memory-management setup, page-table transitions,
highmem/fixmap setup, or device mapping code rather than from normal filesystem paths.

### State, Persistence, And Dependencies
Caller-visible state is represented by `map_desc`, `mem_type`. External state or implementation
hooks include `iotable_init`, `vm_reserve_area_early`, `create_mapping_late`, `debug_ll_addr`,
`debug_ll_io_init`, `get_mem_type`, `ioremap_page`. DMA-visible state depends on cache cleanliness,
bus mappings, and device/platform data owned by the DMA mapping or driver layers. There is no
userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. Direct includes are `asm/io.h`. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Mapping helpers depend on page-table, vmalloc, highmem, or memory-type
definitions supplied elsewhere under `arch/arm`. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `map.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
incorrect address alignment, memory type, or cache alias handling can corrupt data or make
executable mappings incoherent.

### Test Signals
run MMU, highmem, ioremap, kexec, and cache/TLB coherency tests; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/pci.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/pci.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/pci.h` declares ARM machine PCI host-
controller setup, scan, swizzle, and mapping hooks. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
types: `pci_sys_data`, `pci_ops`, `pci_bus`, `pci_host_bridge`, `device`, `hw_pci`, `list_head`,
`resource`; functions/prototypes: `u8`, `pci_common_init_dev`, `pci_map_io_early`,
`iop3xx_pci_setup`, `iop3xx_pci_preinit`, `iop3xx_pci_preinit_cond`, `dc21285_setup`,
`dc21285_preinit`, `dc21285_postinit`, `iop3xx_ops`, `dc21285_ops`. The file is 86 lines / 2164
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `pci_sys_data`, `pci_ops`, `pci_bus`, `pci_host_bridge`,
`device`, `hw_pci`, `list_head`, `resource`. External state or implementation hooks include
`pci_map_io_early`, `iop3xx_ops`, `iop3xx_pci_setup`, `iop3xx_pci_preinit`,
`iop3xx_pci_preinit_cond`, `dc21285_ops`, `dc21285_setup`, `dc21285_preinit`, and 1 more. There is
no userspace filesystem persistence in this file; persistence is either kernel memory, CPU register
state, hardware register state, or generated ABI values. Direct includes are `linux/ioport.h`. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `pci.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/sharpsl_param.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/sharpsl_param.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/sharpsl_param.h` declares Sharp SL
boot-parameter layout shared with board initialization. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
types: `sharpsl_param_info`; functions/prototypes: `__attribute__`, `sharpsl_save_param`,
`sharpsl_param`. The file is 33 lines / 689 bytes, and the exported surface is primarily an include-
time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
Caller-visible state is represented by `sharpsl_param_info`. External state or implementation hooks
include `sharpsl_param`, `sharpsl_save_param`. There is no userspace filesystem persistence in this
file; persistence is either kernel memory, CPU register state, hardware register state, or generated
ABI values. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `sharpsl_param.h`. In
the distributed filesystem tree this matters indirectly: the Ceph client can only rely on
networking, page cache, DMA, fault handling, and scheduler primitives if these architecture hooks
compile and behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/sharpsl_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/time.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/time.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/time.h` declares legacy machine timer
descriptors and init hooks. It is part of the ARM kernel-architecture compatibility layer imported
in the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt,
driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
functions/prototypes: `register_persistent_clock`. The file is 13 lines / 332 bytes, and the
exported surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
External state or implementation hooks include `register_persistent_clock`. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. It integrates with generic Linux ARM architecture
code through include-time contracts rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `time.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mach/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mc146818rtc.h -->
## sources/distributed-fs/ceph-client/arch/arm/include/asm/mc146818rtc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/mc146818rtc.h` maps legacy CMOS RTC
accessors for ARM platforms that provide MC146818-compatible hardware. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `_ASM_MC146818RTC_H`, `RTC_IRQ`, `RTC_PORT`, `RTC_ALWAYS_BCD`, `CMOS_READ`, `CMOS_WRITE`.
The file is 31 lines / 720 bytes, and the exported surface is primarily an include-time contract for
other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/io.h`, `linux/kernel.h`. It integrates with generic Linux ARM architecture code through
include-time contracts rather than a standalone translation unit. Interrupt-related declarations
integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `mc146818rtc.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mc146818rtc.h -->
