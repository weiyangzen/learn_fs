# subset-b-000719 Research

Grouped source research for subset B work item `subset-b-000719`. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/hwtest.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/hwtest.c

## Purpose

implements early m68k RAM probing helpers that safely test physical memory ranges before the normal
page allocator trusts them

## Important APIs, Types, and Functions

Source read size: 96 lines, 2645 bytes. Includes: `linux/module.h`, `asm/hwtest.h`. Defined
functions: `hwreg_present`, `hwreg_write`. Declared functions: `local_irq_save`. Exported symbols:
`hwreg_present`, `hwreg_write`.

## Control Flow and Behavior

the routines write and verify test patterns while using exception-protected probing so board setup
can reject missing or aliased RAM without crashing the kernel

## State and Persistence

persistent effects are limited to the discovered usable memory map fed into m68k boot memory setup;
the probe deliberately restores or overwrites test locations during early boot

## Dependencies and Integration Points

depends on m68k exception handling, setup memory descriptors, low-level physical addressing, and
early boot ordering before paging and memblock are finalized

## Risks and Test Signals

unsafe probing can corrupt firmware data or fault recursively; booting on machines with sparse,
mirrored, or partially populated RAM is the strongest test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/hwtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/init.c

## Purpose

provides the generic m68k memory initialization path for non-MMU or common-MMU builds, including
zone limits, node setup, paging initialization, initmem release, and final memory accounting

## Important APIs, Types, and Functions

Source read size: 118 lines, 2546 bytes. Includes: `linux/module.h`, `linux/signal.h`,
`linux/sched.h`, `linux/mm.h`, `linux/swap.h`, `linux/kernel.h`, `linux/string.h`, `linux/types.h`,
`linux/init.h`, `linux/memblock.h`, `linux/gfp.h`, `asm/setup.h`; plus 9 more. Defined functions:
`Copyright`, `m68k_setup_node`, `paging_init`, `free_initmem`, `init_pointer_tables`, `mem_init`.
Key macros/defines: `VECTORS`.

## Control Flow and Behavior

arch_zone_limits_init(), m68k_setup_node(), paging_init(), free_initmem(), init_pointer_tables(),
and mem_init() transition from boot memory descriptors to managed pages and initialize vector/page-
table areas as required by the selected CPU/MMU model

## State and Persistence

persistent state includes max_zone_pfns, pg_data_t node ranges, reserved vector pages, freed init
sections, totalram_pages, memblock reservations, and architecture page-table metadata

## Dependencies and Integration Points

integrates with memblock, sparse/contiguous memory models, m68k bootinfo, machdep hooks, TLB/page-
table setup, Atari ST-RAM handling, and generic mm initialization

## Risks and Test Signals

zone boundary or reservation errors can expose ROM, vectors, or page tables to the allocator; boot
logs, memblock debug, free_initmem accounting, and m68k defconfig boots are key signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/kmap.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/kmap.c

## Purpose

implements m68k highmem, temporary kernel mapping, and cache-color aware kmap support for MMU
systems

## Important APIs, Types, and Functions

Source read size: 400 lines, 8713 bytes. Includes: `linux/module.h`, `linux/mm.h`, `linux/kernel.h`,
`linux/string.h`, `linux/types.h`, `linux/slab.h`, `linux/vmalloc.h`, `asm/setup.h`, `asm/page.h`,
`asm/io.h`, `asm/tlbflush.h`. Defined functions: `Copyright`, `free_io_area`, `__free_io_area`,
`ioremap`, `kernel_set_cachemode`. Declared functions: `get_vm_area`, `printk`, `pmd_clear`,
`flush_tlb_all`, `kfree`, `__free_io_area`, `return`. Key macros/defines: `IO_SIZE`. Types visible
in this file: `vm_struct`. Exported symbols: `__ioremap`, `iounmap`, `kernel_set_cachemode`.

## Control Flow and Behavior

functions allocate virtual kmap slots, install/remove PTEs, flush caches/TLBs, and bridge highmem
pages into kernel address space for copy, clear, or I/O paths

## State and Persistence

runtime state is the fixmap/kmap PTE area, per-page virtual mapping state, cache flush side effects,
and any global locks protecting shared kmap slots

## Dependencies and Integration Points

depends on highmem, fixmap, page tables, cacheflush, TLB flush APIs, and generic kmap interfaces
used by filesystems, networking, and block I/O

## Risks and Test Signals

aliasing and stale-cache bugs are the major risks; highmem stress, kmap_local nesting, page copy
tests, and DMA/I/O workloads on 68030/040/060 systems are useful signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/kmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/mcfmmu.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/mcfmmu.c

## Purpose

implements ColdFire MMU paging, TLB-miss handling, boot memory allocation, and MMU context
management

## Important APIs, Types, and Functions

Source read size: 270 lines, 7264 bytes. Includes: `linux/kernel.h`, `linux/types.h`, `linux/mm.h`,
`linux/init.h`, `linux/string.h`, `linux/memblock.h`, `asm/setup.h`, `asm/page.h`,
`asm/mmu_context.h`, `asm/mcf_pgalloc.h`, `asm/tlbflush.h`, `asm/pgalloc.h`. Defined functions:
`paging_init`, `cf_tlb_miss`, `cf_bootmem_alloc`, `cf_mmu_context_init`, `turn`. Declared functions:
`local_irq_save`, `set_pte`, `memblock_add_node`. Key macros/defines: `KMAPAREA(x)`. Types visible
in this file: `mm_struct`.

## Control Flow and Behavior

paging_init() creates the kernel mapping, cf_tlb_miss() decodes fault extensions and fills DTLB/ITLB
entries, cf_bootmem_alloc() reserves early tables, cf_mmu_context_init() initializes ASID context
state, and steal_context() recycles exhausted contexts

## State and Persistence

persistent state includes context_mm[], next_mmu_context, page-table roots, TLB entries, bootmem
allocations, and per-mm context identifiers

## Dependencies and Integration Points

integrates with ColdFire exception vectors, asm/mmu_context.h, mcf page-table allocation, memblock,
TLB flushing, and generic fault handling

## Risks and Test Signals

fault extension decoding, context stealing, and TLB permissions are correctness-critical; ColdFire
MMU boot, page-fault stress, fork/exec churn, and vmalloc/ioremap tests are the main signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/mcfmmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/memory.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/memory.c

## Purpose

provides m68k cache maintenance exports for physical address ranges, especially 68040/060 cache-line
clear and push operations

## Important APIs, Types, and Functions

Source read size: 192 lines, 5121 bytes. Includes: `linux/module.h`, `linux/mm.h`, `linux/kernel.h`,
`linux/string.h`, `linux/types.h`, `linux/init.h`, `linux/pagemap.h`, `linux/gfp.h`, `asm/setup.h`,
`asm/page.h`, `asm/traps.h`, `asm/machdep.h`. Defined functions: `Copyright`, `cleari040`,
`push040`, `pushcl040`, `cache_clear`, `cache_push`. Declared functions: `volatile`,
`local_irq_save`, `pushcl040`, `clear040`, `push040`, `cache_clear`. Exported symbols:
`cache_clear`, `cache_push`.

## Control Flow and Behavior

cache_clear() and cache_push() choose CPU-specific operations and iterate over physical ranges using
inline assembly helpers for data/instruction cache lines

## State and Persistence

state changes are hardware cache contents and dirty-line writeback status; no durable software state
is kept

## Dependencies and Integration Points

depends on CPU type flags, cache line size assumptions, traps/machdep setup, and callers that need
coherent instruction, DMA, or aliasing behavior

## Risks and Test Signals

wrong line rounding or CPU selection leaves stale instructions or lost DMA data; module loading,
executable mmap, DMA drivers, and cacheflush selftests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/motorola.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/motorola.c

## Purpose

implements Motorola 68030/040/060 MMU page-table allocation, kernel mapping construction,
cacheability protection tables, and paging_init() for classic MMU m68k systems

## Important APIs, Types, and Functions

Source read size: 512 lines, 12988 bytes. Includes: `linux/module.h`, `linux/signal.h`,
`linux/sched.h`, `linux/mm.h`, `linux/swap.h`, `linux/kernel.h`, `linux/string.h`, `linux/types.h`,
`linux/init.h`, `linux/memblock.h`, `linux/gfp.h`, `asm/setup.h`; plus 7 more. Defined functions:
`nocache_page`, `cache_page`, `on`, `mmu_page_dtor`, `init_pointer_table`, `free_pointer_table`,
`kernel_page_table`, `kernel_ptr_table`, `map_node`, `paging_init`. Declared functions: `Copyright`,
`PD_MARKBITS`, `pagetable_pte_ctor`, `mmu_page_ctor`, `list_move_tail`, `panic`, `list_del`,
`list_move`, `clear_page`, `printk`, `memblock_add_node`, `module_fixup`, `m68k_setup_node`,
`flush_tlb_all`. Key macros/defines: `PD_PTABLE(ptdesc)`, `PD_PTDESC(ptable)`, `PD_MARKBITS(dp)`,
`ptable_size(type)`, `ptable_mask(type)`, `PAGE_NONE_C`, `PAGE_SHARED_C`, `PAGE_COPY_C`,
`PAGE_READONLY_C`. Types visible in this file: `ptdesc`, `ptable_desc`. External symbols
referenced/declared: `m68k_init_mapped_size`, `availmem`. Exported symbols: `mm_cachebits`.

## Control Flow and Behavior

init_pointer_table(), get_pointer_table(), free_pointer_table(), kernel_page_table(),
kernel_ptr_table(), map_node(), and paging_init() build and manage multi-level pointer tables and
page protections

## State and Persistence

persistent state includes kernel_pg_dir, pointer-table descriptors, ptdesc mark bits, mm_cachebits,
pgprot tables, memblock reservations, and installed MMU descriptors

## Dependencies and Integration Points

integrates with pgalloc, memblock, Atari ST-RAM, m68k sections, machdep setup, page protection
constants, and generic Linux page-table APIs

## Risks and Test Signals

pointer-table reference accounting, cacheability bits, and early mapping boundaries are fragile;
multi-platform m68k boots, vmalloc/ioremap, fork/exit page-table churn, and page protection tests
are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/motorola.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/sun3kmap.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/sun3kmap.c

## Purpose

implements Sun-3 ioremap/kmap-style mappings using the Sun-3 segment/PMEG MMU model

## Important APIs, Types, and Functions

Source read size: 159 lines, 3399 bytes. Includes: `linux/module.h`, `linux/types.h`,
`linux/kernel.h`, `linux/mm.h`, `linux/vmalloc.h`, `asm/page.h`, `asm/io.h`, `asm/sun3mmu.h`,
`../sun3/sun3.h`. Defined functions: `do_page_mapin`, `do_pmeg_mapin`, `iounmap`, `sun3_map_test`.
Declared functions: `Copyright`, `sun3_put_pte`, `do_page_mapin`, `sun3_ioremap`, `__volatile__`.
Types visible in this file: `vm_struct`. External symbols referenced/declared: `mmu_emu_map_pmeg`.
Exported symbols: `sun3_ioremap`, `__ioremap`, `iounmap`, `sun3_map_test`.

## Control Flow and Behavior

sun3_ioremap(), __ioremap(), iounmap(), and sun3_map_test() allocate virtual space, map pages or
PMEGs, and validate mapped bus addresses through safe byte access

## State and Persistence

persistent state is the installed Sun-3 MMU mapping entries and virtual allocation metadata for
device mappings

## Dependencies and Integration Points

depends on sun3mmu helpers, vmalloc, asm/io, Sun-3 PMEG management, and drivers that call ioremap
for on-board or VME devices

## Risks and Test Signals

PMEG exhaustion, wrong cache mode, or failed unmap cleanup breaks device access; Sun-3 boot with
SCSI/Ethernet/framebuffer drivers and ioremap fault tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/sun3kmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/sun3mmu.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mm/sun3mmu.c

## Purpose

initializes and manipulates the Sun-3 MMU context, segment, and page-map state for the 68020 Sun-3
port

## Important APIs, Types, and Functions

Source read size: 100 lines, 2836 bytes. Includes: `linux/signal.h`, `linux/sched.h`, `linux/mm.h`,
`linux/swap.h`, `linux/kernel.h`, `linux/string.h`, `linux/types.h`, `linux/init.h`,
`linux/memblock.h`, `asm/setup.h`, `linux/uaccess.h`, `asm/page.h`; plus 3 more. Defined functions:
`paging_init`. Declared functions: `pgd_val`, `mmu_emu_init`. External symbols referenced/declared:
`num_pages`.

## Control Flow and Behavior

the file exposes low-level page-map operations and startup initialization that program contexts,
segments, PMEG entries, and cache/MMU control registers

## State and Persistence

persistent state lives in Sun-3 hardware MMU maps, context tables, and boot-time mapping globals

## Dependencies and Integration Points

integrates with sun3kmap.c, sun3/mmu_emu.c, Sun-3 boot setup, page fault handling, and device DVMA
mapping

## Risks and Test Signals

context/segment aliasing can corrupt arbitrary address spaces; Sun-3 boot, user process switching,
page faults, and DVMA tests are key validation signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mm/sun3mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme147/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/mvme147/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/mvme147`, the m68k
platform area that configures the Motorola MVME147 VME board: machine model reporting, RTC, IRQ,
console, reset, and board-specific machdep hooks

## Important APIs, Types, and Functions

Source read size: 6 lines, 120 bytes. Build selections: `obj-y -> config.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme147/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme147/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mvme147/config.c

## Purpose

configures the Motorola MVME147 VME board: machine model reporting, RTC, IRQ, console, reset, and
board-specific machdep hooks

## Important APIs, Types, and Functions

Source read size: 210 lines, 4741 bytes. Includes: `linux/types.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/tty.h`, `linux/clocksource.h`, `linux/console.h`, `linux/linkage.h`, `linux/init.h`,
`linux/major.h`, `linux/interrupt.h`, `linux/platform_device.h`, `linux/rtc/m48t59.h`; plus 10 more.
Defined functions: `mvme147_parse_bootinfo`, `mvme147_reset`, `mvme147_get_model`,
`mvme147_init_IRQ`, `config_mvme147`, `mvme147_platform_init`, `mvme147_timer_int`,
`mvme147_sched_init`, `mvme147_read_clk`, `scc_delay`, `scc_write`, `mvme147_scc_write`. Declared
functions: `Copyright`, `platform_device_register_resndata`, `mvme147_read_clk`, `local_irq_save`,
`pr_err`, `__volatile__`, `scc_delay`. Key macros/defines: `PCC_TIMER_CLOCK_FREQ`,
`PCC_TIMER_CYCLES`, `PCC_TIMER_PRELOAD`. External symbols referenced/declared: `mvme147_reset`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme147/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme147/mvme147.h -->
# sources/distributed-fs/ceph-client/arch/m68k/mvme147/mvme147.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/mvme147` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 6 lines, 158 bytes. Declared functions: `mvme147_scc_write`. Types visible in this
file: `console`.

## Control Flow and Behavior

the header provides board or subsystem function prototypes, forward declarations, and include guards
consumed by adjacent C files

## State and Persistence

state is compile-time only, though the declared functions usually manipulate machine interrupt,
timer, PROM, or MMU state

## Dependencies and Integration Points

integrates local machine files with arch/m68k setup, machdep callbacks, and low-level assembly entry
points

## Risks and Test Signals

prototype drift causes build failures or wrong calling conventions; the platform defconfig build is
the first signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme147/mvme147.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme16x/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/mvme16x/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/mvme16x`, the m68k
platform area that configures Motorola MVME162/166/167 VME boards: model detection, memory/console
setup, RTC, interrupts, reset, and VME/board peripherals

## Important APIs, Types, and Functions

Source read size: 6 lines, 120 bytes. Build selections: `obj-y -> config.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme16x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme16x/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/mvme16x/config.c

## Purpose

configures Motorola MVME162/166/167 VME boards: model detection, memory/console setup, RTC,
interrupts, reset, and VME/board peripherals

## Important APIs, Types, and Functions

Source read size: 444 lines, 11108 bytes. Includes: `linux/types.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/seq_file.h`, `linux/tty.h`, `linux/clocksource.h`, `linux/console.h`, `linux/linkage.h`,
`linux/init.h`, `linux/major.h`, `linux/interrupt.h`, `linux/module.h`; plus 12 more. Defined
functions: `mvme16x_parse_bootinfo`, `mvme16x_reset`, `mvme16x_get_model`,
`mvme16x_get_hardware_list`, `mvme16x_init_IRQ`, `mvme16x_cons_write`, `config_mvme16x`,
`mvme16x_platform_init`, `mvme16x_abort_int`, `mvme16x_timer_int`, `mvme16x_sched_init`,
`mvme16x_read_clk`. Declared functions: `Copyright`, `sprintf`, `seq_printf`, `in_8`, `pr_info`,
`platform_device_register_resndata`, `mvme16x_read_clk`, `local_irq_save`. Key macros/defines:
`PCC2CHIP`, `PCCSCCMICR`, `PCCSCCTICR`, `PCCSCCRICR`, `PCCTPIACKR`, `CD2401_ADDR`, `CyGFRCR`,
`CyCCR`, `CyCLR_CHAN`, `CyINIT_CHAN`, `CyCHIP_RESET`, `CyENB_XMTR`, `CyDIS_XMTR`, `CyENB_RCVR`,
`CyDIS_RCVR`, `CyCAR`, `CyIER`, `CyMdmCh`, `CyRxExc`, `CyRxData`, `CyTxMpty`, `CyTxRdy`, `CyLICR`,
`CyRISR`; plus 71 more. External symbols referenced/declared: `mvme_bdid`, `mvme16x_sched_init`,
`mvme16x_reset`. Exported symbols: `mvme16x_config`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme16x/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme16x/mvme16x.h -->
# sources/distributed-fs/ceph-client/arch/m68k/mvme16x/mvme16x.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/mvme16x` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 6 lines, 155 bytes. Declared functions: `mvme16x_cons_write`. Types visible in
this file: `console`.

## Control Flow and Behavior

the header provides board or subsystem function prototypes, forward declarations, and include guards
consumed by adjacent C files

## State and Persistence

state is compile-time only, though the declared functions usually manipulate machine interrupt,
timer, PROM, or MMU state

## Dependencies and Integration Points

integrates local machine files with arch/m68k setup, machdep callbacks, and low-level assembly entry
points

## Risks and Test Signals

prototype drift causes build failures or wrong calling conventions; the platform defconfig build is
the first signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/mvme16x/mvme16x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/q40/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/q40`, the m68k
platform area that configures the Q40/Q60 machine family: boot model reporting,
keyboard/IDE/RTC/sound/timer hooks, interrupts, reset, and platform devices

## Important APIs, Types, and Functions

Source read size: 6 lines, 126 bytes. Build selections: `obj-y -> config.o q40ints.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/q40/config.c

## Purpose

configures the Q40/Q60 machine family: boot model reporting, keyboard/IDE/RTC/sound/timer hooks,
interrupts, reset, and platform devices

## Important APIs, Types, and Functions

Source read size: 296 lines, 6549 bytes. Includes: `linux/errno.h`, `linux/types.h`,
`linux/kernel.h`, `linux/mm.h`, `linux/console.h`, `linux/linkage.h`, `linux/init.h`,
`linux/major.h`, `linux/serial_reg.h`, `linux/rtc.h`, `linux/bcd.h`, `linux/platform_device.h`; plus
9 more. Defined functions: `q40_mem_console_write`, `q40_debug_setup`, `q40_heartbeat`, `q40_reset`,
`q40_halt`, `q40_get_model`, `q40_disable_irqs`, `config_q40`, `q40_parse_bootinfo`, `q40_hwclk`,
`q40_get_rtc_pll`, `q40_set_rtc_pll`, `q40_platform_init`. Declared functions: `Copyright`,
`register_console`, `outb`, `platform_device_register_simple`. Key macros/defines:
`Q40_RTC_PLL_MASK`, `Q40_RTC_PLL_SIGN`, `PCIDE_BASE1`, `PCIDE_BASE2`, `PCIDE_CTL`. External symbols
referenced/declared: `ql_ticks`, `q40_mem_cptr`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/q40.h -->
# sources/distributed-fs/ceph-client/arch/m68k/q40/q40.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/q40` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 6 lines, 168 bytes. Declared functions: `q40_init_IRQ`.

## Control Flow and Behavior

the header provides board or subsystem function prototypes, forward declarations, and include guards
consumed by adjacent C files

## State and Persistence

state is compile-time only, though the declared functions usually manipulate machine interrupt,
timer, PROM, or MMU state

## Dependencies and Integration Points

integrates local machine files with arch/m68k setup, machdep callbacks, and low-level assembly entry
points

## Risks and Test Signals

prototype drift causes build failures or wrong calling conventions; the platform defconfig build is
the first signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/q40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/q40ints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/q40/q40ints.c

## Purpose

implements Q40 interrupt controller setup, IRQ masking/unmasking, timer interrupt handling, and
legacy sound tick programming

## Important APIs, Types, and Functions

Source read size: 334 lines, 8121 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/errno.h`, `linux/interrupt.h`, `linux/irq.h`, `asm/machdep.h`, `asm/ptrace.h`, `asm/traps.h`,
`asm/q40_master.h`, `asm/q40ints.h`, `q40.h`. Defined functions: `q40_irq_startup`,
`q40_irq_shutdown`, `q40_init_IRQ`, `q40_mksound`, `q40_timer_int`, `q40_sched_init`,
`q40_irq_handler`, `q40_irq_enable`, `q40_irq_disable`. Declared functions: `Copyright`, `pr_warn`,
`m68k_irq_startup_irq`, `local_irq_save`, `floppy_hardint`, `do_IRQ`, `disable_irq`, `enable_irq`,
`master_outb`. Key macros/defines: `SVOL`, `IRQ_INPROGRESS`, `DEBUG_Q40INT`. Types visible in this
file: `IRQ_TABLE`.

## Control Flow and Behavior

q40_init_IRQ() installs irq_chip handlers, q40_irq_startup()/shutdown()/enable()/disable()
manipulate hardware masks, q40_timer_int() drives the scheduler tick, q40_sched_init() requests the
timer IRQ, and q40_irq_handler() demultiplexes pending sources

## State and Persistence

persistent state includes disabled/active IRQ mask bits, timer programming, IRQ chip state, and in-
progress IRQ bookkeeping

## Dependencies and Integration Points

integrates with asm/q40_master.h, asm/q40ints.h, generic irq_chip/handle_irq_event, machdep
interrupt entry, and timer/sound hooks from q40/config.c

## Risks and Test Signals

lost mask updates or bad demux ordering produce stuck IRQs or timer stalls; boot IRQ logs,
keyboard/network/disk interrupts, timer tick accounting, and sound tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/q40/q40ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/sun3`, the m68k
platform area that supports classic Sun-3 machines, including PROM access, IDPROM parsing, Intersil
RTC, LEDs, DVMA, interrupts, and segmented MMU support

## Important APIs, Types, and Functions

Source read size: 8 lines, 211 bytes. Build selections: `obj-y -> sun3ints.o sun3dvma.o idprom.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/config.c

## Purpose

sets Sun-3 machdep callbacks, model strings, memory/device setup, and reboot/interrupt/time hooks
during platform configuration

## Important APIs, Types, and Functions

Source read size: 221 lines, 5450 bytes. Includes: `linux/types.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/seq_file.h`, `linux/tty.h`, `linux/console.h`, `linux/init.h`, `linux/memblock.h`,
`linux/platform_device.h`, `linux/linkage.h`, `asm/oplib.h`, `asm/setup.h`; plus 14 more. Defined
functions: `sun3_get_hardware_list`, `sun3_init`, `sun3_reboot`, `sun3_halt`, `sun3_bootmem_alloc`,
`config_sun3`, `sun3_sched_init`, `sun3_platform_init`. Declared functions: `sun3_sched_init`,
`prom_init`, `m68k_setup_node`, `pr_info`, `sun3_enable_irq`, `platform_device_register_simple`.
External symbols referenced/declared: `availmem`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/dvma.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/dvma.c

## Purpose

initializes low-level Sun-3 DVMA page mappings from kernel addresses into bus-visible virtual space

## Important APIs, Types, and Functions

Source read size: 68 lines, 1290 bytes. Includes: `linux/init.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/memblock.h`, `linux/list.h`, `asm/page.h`, `asm/sun3mmu.h`, `asm/dvma.h`. Defined functions:
`dvma_page`, `dvma_map_iommu`, `sun3_dvma_init`. Declared functions: `sun3_put_pte`, `return`,
`dvma_page`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/dvma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/idprom.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/idprom.c

## Purpose

reads and validates the Sun IDPROM, including Ethernet address, machine type, serial, and checksum
fields

## Important APIs, Types, and Functions

Source read size: 134 lines, 4464 bytes. Includes: `linux/module.h`, `linux/kernel.h`,
`linux/types.h`, `linux/init.h`, `linux/string.h`, `asm/oplib.h`, `asm/idprom.h`, `asm/machines.h`,
`sun3.h`. Defined functions: `display_system_type`, `sun3_get_model`, `calc_idprom_cksum`,
`idprom_init`. Declared functions: `Copyright`, `prom_getproperty`, `prom_printf`, `strcpy`,
`display_system_type`. Types visible in this file: `idprom`. Exported symbols: `idprom`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/idprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/intersil.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/intersil.c

## Purpose

implements access to the Sun-3 Intersil RTC for hardware clock read/write operations

## Important APIs, Types, and Functions

Source read size: 70 lines, 1708 bytes. Includes: `linux/kernel.h`, `linux/rtc.h`, `asm/errno.h`,
`asm/intersil.h`, `asm/machdep.h`, `sun3.h`. Defined functions: `sun3_hwclk`. Declared functions:
`local_irq_save`, `local_irq_restore`. Key macros/defines: `STOP_VAL`, `START_VAL`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/intersil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/leds.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/leds.c

## Purpose

updates Sun-3 diagnostic LED hardware through the platform LED register

## Important APIs, Types, and Functions

Source read size: 16 lines, 273 bytes. Includes: `asm/contregs.h`, `asm/sun3mmu.h`, `asm/io.h`,
`sun3.h`. Defined functions: `sun3_leds`. Declared functions: `GET_DFC`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/mmu_emu.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/mmu_emu.c

## Purpose

emulates enough Sun-3 MMU behavior in software to support Linux page-table semantics on hardware
with a segmented PMEG MMU

## Important APIs, Types, and Functions

Source read size: 427 lines, 11915 bytes. Includes: `linux/init.h`, `linux/mman.h`, `linux/mm.h`,
`linux/kernel.h`, `linux/ptrace.h`, `linux/delay.h`, `linux/memblock.h`, `linux/bitops.h`,
`linux/module.h`, `linux/sched/mm.h`, `linux/string_choices.h`, `asm/setup.h`; plus 8 more. Defined
functions: `print_pte`, `print_pte_vaddr`, `mmu_emu_init`, `clear_context`, `get_free_context`,
`mmu_emu_map_pmeg`, `mmu_emu_handle_fault`. Declared functions: `pr_cont`, `memset`, `pr_info`,
`dvma_init`, `sun3_put_context`, `sun3_put_segmap`, `clear_context`, `sun3_put_pte`,
`str_read_write`, `mmu_emu_map_pmeg`, `pte_val`. Key macros/defines: `DEBUG_PROM_MAPS`,
`CONTEXTS_NUM`, `SEGMAPS_PER_CONTEXT_NUM`, `PAGES_PER_SEGMENT`, `PMEGS_NUM`, `PMEG_MASK`. Exported
symbols: `m68k_vmalloc_end`.

## Control Flow and Behavior

mmu_emu_init() builds software tables, mmu_emu_map_pmeg() assigns PMEGs to virtual segments,
mmu_emu_handle_fault() resolves faults by loading page map entries, and diagnostic helpers print
page-table state

## State and Persistence

persistent state includes PMEG allocation tables, context/segment mappings, software page-table
mirrors, and fault-time replacement metadata

## Dependencies and Integration Points

integrates with sun3mmu low-level map writes, Sun-3 fault handlers, sun3kmap/ioremap, and generic
m68k page-table state

## Risks and Test Signals

replacement policy, kernel/user context separation, and fault reentrancy are risky; Sun-3 multi-
process memory pressure, mmap/page-fault stress, and PMEG exhaustion tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/mmu_emu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/sun3/prom`, the
m68k platform area that supports classic Sun-3 machines, including PROM access, IDPROM parsing,
Intersil RTC, LEDs, DVMA, interrupts, and segmented MMU support

## Important APIs, Types, and Functions

Source read size: 7 lines, 206 bytes. Build selections: `obj-y -> init.o console.o printf.o misc.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/console.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/console.c

## Purpose

implements Sun-3 PROM console input/output wrappers used before the normal tty console is available

## Important APIs, Types, and Functions

Source read size: 170 lines, 4014 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/sched.h`, `asm/openprom.h`, `asm/oplib.h`, `linux/string.h`. Defined functions: `Copyright`,
`prom_nbputchar`, `prom_getchar`, `prom_putchar`, `prom_query_input_device`,
`prom_query_output_device`. Declared functions: `local_irq_save`. Types visible in this file:
`prom_input_device`, `prom_output_device`.

## Control Flow and Behavior

PROM console routines translate kernel console calls into ROM vector operations for putchar,
getchar, nonblocking polling, and console write loops

## State and Persistence

persistent state is minimal; behavior depends on PROM vector state and early console registration

## Dependencies and Integration Points

integrates with asm/openprom.h, oplib, early printk, boot diagnostics, and Sun-3 PROM initialization

## Risks and Test Signals

PROM calling convention mistakes hang early boot; serial/framebuffer PROM console boot logs are the
key signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/console.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/init.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/init.c

## Purpose

initializes Sun-3 PROM access structures and captures firmware entry points for later boot services

## Important APIs, Types, and Functions

Source read size: 36 lines, 821 bytes. Includes: `linux/kernel.h`, `linux/init.h`, `asm/openprom.h`,
`asm/oplib.h`. Defined functions: `prom_init`. Types visible in this file: `linux_romvec`,
`linux_nodeops`, `prom_major_version`.

## Control Flow and Behavior

prom_init() style logic records ROM vectors, initializes console/service hooks, and makes PROM calls
available to platform setup

## State and Persistence

persistent state is the global PROM vector table pointer and derived oplib state

## Dependencies and Integration Points

integrates with Sun-3 head code, openprom/oplib headers, early console, reboot, and IDPROM access

## Risks and Test Signals

wrong vector addresses break every firmware call; early boot console and reboot/halt tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/misc.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/misc.c

## Purpose

implements miscellaneous Sun-3 PROM services such as reboot, halt, command-line retrieval, IDPROM
copy, and firmware revision queries

## Important APIs, Types, and Functions

Source read size: 95 lines, 1839 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/sched.h`, `asm/sun3-head.h`, `asm/idprom.h`, `asm/openprom.h`, `asm/oplib.h`, `asm/movs.h`.
Defined functions: `Copyright`, `prom_cmdline`, `prom_halt`, `prom_get_idprom`, `prom_version`,
`prom_getrev`, `prom_getprev`. Declared functions: `void`, `GET_CONTROL_BYTE`.

## Control Flow and Behavior

functions call PROM vector slots directly and provide small wrappers used by platform setup and
machine restart paths

## State and Persistence

persistent state is external PROM state plus copied IDPROM/command-line data returned to callers

## Dependencies and Integration Points

integrates with asm/openprom.h, asm/oplib.h, IDPROM parsing, and machdep reset/halt callbacks

## Risks and Test Signals

bad PROM entry selection can hang the machine; reboot/halt and IDPROM validation are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/printf.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/printf.c

## Purpose

provides a small prom_printf() formatter for Sun-3 early firmware diagnostics

## Important APIs, Types, and Functions

Source read size: 55 lines, 975 bytes. Includes: `linux/kernel.h`, `asm/openprom.h`, `asm/oplib.h`.
Defined functions: `prom_printf`. Declared functions: `va_start`, `pr_info`. External symbols
referenced/declared: `kgdb_initialized`.

## Control Flow and Behavior

the function formats into a temporary buffer and writes through PROM console output while normal
printk may be unavailable

## State and Persistence

no durable state is kept beyond emitted firmware console output

## Dependencies and Integration Points

integrates with PROM console wrappers and early Sun-3 boot/debug code

## Risks and Test Signals

format buffer sizing and PROM output availability are the risks; early boot diagnostics are the
signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/printf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3.h -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/sun3` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 22 lines, 483 bytes. Includes: `linux/linkage.h`. Declared functions: `sun3_init`.
Types visible in this file: `rtc_time`.

## Control Flow and Behavior

the header provides board or subsystem function prototypes, forward declarations, and include guards
consumed by adjacent C files

## State and Persistence

state is compile-time only, though the declared functions usually manipulate machine interrupt,
timer, PROM, or MMU state

## Dependencies and Integration Points

integrates local machine files with arch/m68k setup, machdep callbacks, and low-level assembly entry
points

## Risks and Test Signals

prototype drift causes build failures or wrong calling conventions; the platform defconfig build is
the first signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3dvma.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3dvma.c

## Purpose

implements the higher-level Sun-3 DVMA allocator and mapping layer used by bus-mastering devices

## Important APIs, Types, and Functions

Source read size: 359 lines, 6735 bytes. Includes: `linux/memblock.h`, `linux/init.h`,
`linux/module.h`, `linux/kernel.h`, `linux/gfp.h`, `linux/mm.h`, `linux/list.h`, `asm/page.h`,
`asm/dvma.h`. Defined functions: `print_use`, `print_holes`, `refill`, `list_for_each`, `get_baddr`,
`free_baddr`, `dvma_init`, `dvma_map_align`, `dvma_unmap`, `dvma_free`. Declared functions:
`pr_info`, `list_move`, `pr_crit`, `INIT_LIST_HEAD`, `pr_debug`, `free_baddr`, `free_pages`,
`dvma_unmap`. Key macros/defines: `dvma_index(baddr)`, `dvma_entry_use(baddr)`. Types visible in
this file: `hole`, `list_head`. Exported symbols: `dvma_map_align`, `dvma_unmap`,
`dvma_malloc_align`, `dvma_free`.

## Control Flow and Behavior

the code allocates DVMA virtual ranges, maps kernel pages into DVMA bus-visible space, tracks active
mappings, and tears them down for device drivers

## State and Persistence

persistent state includes DVMA region metadata, mapping lists, page-map entries, and allocated
bootmem/vmalloc backing areas

## Dependencies and Integration Points

integrates with asm/dvma.h, Sun-3 MMU page map routines, SCSI/Ethernet drivers, and generic DMA
expectations for cache-coherent device access

## Risks and Test Signals

leaked DVMA slots, wrong bus addresses, or missing cache maintenance break I/O; disk/network
transfers under memory pressure are the primary signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3dvma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3ints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3ints.c

## Purpose

initializes and dispatches Sun-3 interrupt sources through m68k interrupt entry and generic IRQ
handling

## Important APIs, Types, and Functions

Source read size: 100 lines, 2142 bytes. Includes: `linux/types.h`, `linux/kernel.h`,
`linux/sched.h`, `linux/kernel_stat.h`, `linux/interrupt.h`, `asm/intersil.h`, `asm/oplib.h`,
`asm/sun3ints.h`, `asm/irq_regs.h`, `linux/seq_file.h`, `sun3.h`. Defined functions:
`sun3_disable_interrupts`, `sun3_enable_interrupts`, `sun3_enable_irq`, `sun3_disable_irq`,
`sun3_int7`, `sun3_int5`, `sun3_vec255`, `sun3_init_IRQ`. Declared functions: `sun3_leds`,
`local_irq_save`, `m68k_setup_user_interrupt`.

## Control Flow and Behavior

control flow is driven by platform initialization, machdep callbacks, interrupt entry, or driver
DMA/clock requests depending on the file

## State and Persistence

persistent state is hardware register state, installed callbacks, cached IDPROM/RTC data, or
MMU/DVMA mappings as appropriate

## Dependencies and Integration Points

integrates with asm/machdep.h, Sun-3 PROM/oplib, sun3.h prototypes, m68k traps, generic
IRQ/timekeeping, and device drivers

## Risks and Test Signals

hardware register ordering and firmware assumptions are the main risks; Sun-3 defconfig boot, PROM
diagnostics, clock, IRQ, and device I/O tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3/sun3ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3x/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/sun3x`, the m68k
platform area that supports Sun-3x machines, including PROM vectors, DVMA/IOMMU setup, RTC/time
handling, model reporting, and reset paths

## Important APIs, Types, and Functions

Source read size: 6 lines, 139 bytes. Build selections: `obj-y -> config.o time.o dvma.o prom.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3x/config.c

## Purpose

sets Sun-3x machine callbacks and model/reset behavior for the 68030 Sun platform variant

## Important APIs, Types, and Functions

Source read size: 76 lines, 1435 bytes. Includes: `linux/types.h`, `linux/mm.h`, `linux/seq_file.h`,
`linux/console.h`, `linux/init.h`, `asm/machdep.h`, `asm/irq.h`, `asm/sun3xprom.h`,
`asm/sun3ints.h`, `asm/setup.h`, `asm/oplib.h`, `asm/config.h`; plus 2 more. Defined functions:
`sun3_leds`, `sun3x_get_hardware_list`, `config_sun3x`. Declared functions: `sun3x_prom_init`.

## Control Flow and Behavior

control flow is entered from platform setup, firmware service wrappers, or generic
timekeeping/machdep hooks

## State and Persistence

persistent state includes PROM vectors, installed machdep callbacks, RTC register values, and
DVMA/IOMMU state for data movers

## Dependencies and Integration Points

integrates with Sun-3x PROM firmware, m68k machine setup, generic timekeeping, reset paths, and
device drivers

## Risks and Test Signals

firmware ABI and clock register mistakes can block boot or skew time; Sun-3x boot, clock read/write,
PROM console, and DMA tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/dvma.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3x/dvma.c

## Purpose

implements Sun-3x DVMA allocation and IOMMU mapping for the 68030-based Sun-3x platform

## Important APIs, Types, and Functions

Source read size: 200 lines, 4670 bytes. Includes: `linux/kernel.h`, `linux/init.h`,
`linux/bitops.h`, `linux/mm.h`, `linux/memblock.h`, `linux/vmalloc.h`, `asm/sun3x.h`, `asm/dvma.h`,
`asm/io.h`, `asm/page.h`, `asm/tlbflush.h`. Defined functions: `dvma_print`, `dvma_map_cpu`,
`dvma_map_iommu`, `dvma_unmap_iommu`. Declared functions: `pr_info`, `pr_debug`, `flush_tlb_all`,
`dvma_entry_set`, `dvma_print`. Key macros/defines: `IOMMU_ADDR_MASK`, `IOMMU_CACHE_INHIBIT`,
`IOMMU_FULL_BLOCK`, `IOMMU_MODIFIED`, `IOMMU_USED`, `IOMMU_WRITE_PROTECT`, `IOMMU_DT_MASK`,
`IOMMU_DT_INVALID`, `IOMMU_DT_VALID`, `IOMMU_DT_BAD`, `dvma_entry_paddr(index)`,
`dvma_entry_vaddr(index,paddr)`, `dvma_entry_set(index,addr)`, `dvma_entry_clr(index)`,
`dvma_entry_hash(addr)`.

## Control Flow and Behavior

dvma_map_align(), dvma_unmap(), dvma_malloc_align(), dvma_free(), and initialization paths manage
DVMA address space and page-table/IOMMU entries

## State and Persistence

persistent state includes the DVMA allocator, IOMMU page tables, virtual mapping ranges, and driver-
visible bus addresses

## Dependencies and Integration Points

integrates with Sun-3x PROM/MMU setup, asm/dvma.h, SBus/VME-style drivers, and generic DMA mapping
assumptions

## Risks and Test Signals

alignment and IOMMU PTE bugs cause device data corruption; SCSI/network DMA, allocation/free churn,
and boot with multiple DVMA users are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/dvma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/prom.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3x/prom.c

## Purpose

wraps Sun-3x PROM calls for device tree-like firmware queries, console operations, reboot/halt, and
memory/device discovery

## Important APIs, Types, and Functions

Source read size: 164 lines, 3668 bytes. Includes: `linux/types.h`, `linux/kernel.h`, `linux/tty.h`,
`linux/console.h`, `linux/init.h`, `linux/mm.h`, `linux/string.h`, `asm/page.h`, `asm/setup.h`,
`asm/traps.h`, `asm/sun3xprom.h`, `asm/idprom.h`; plus 3 more. Defined functions: `sun3x_halt`,
`sun3x_reboot`, `sun3x_prom_write`, `sun3x_prom_init`, `sun3x_debug_setup`, `prom_getintdefault`,
`prom_getbool`, `prom_printf`, `prom_halt`, `prom_get_idprom`. Declared functions: `volatile`,
`idprom_init`, `pr_warn`, `register_console`. Types visible in this file: `linux_romvec`.

## Control Flow and Behavior

control flow is entered from platform setup, firmware service wrappers, or generic
timekeeping/machdep hooks

## State and Persistence

persistent state includes PROM vectors, installed machdep callbacks, RTC register values, and
DVMA/IOMMU state for data movers

## Dependencies and Integration Points

integrates with Sun-3x PROM firmware, m68k machine setup, generic timekeeping, reset paths, and
device drivers

## Risks and Test Signals

firmware ABI and clock register mistakes can block boot or skew time; Sun-3x boot, clock read/write,
PROM console, and DMA tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.c -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.c

## Purpose

implements Sun-3x RTC/time initialization and hardware clock access using the platform timer/clock
chip

## Important APIs, Types, and Functions

Source read size: 103 lines, 2075 bytes. Includes: `linux/types.h`, `linux/kd.h`, `linux/init.h`,
`linux/sched.h`, `linux/kernel_stat.h`, `linux/interrupt.h`, `linux/rtc.h`, `linux/bcd.h`,
`asm/irq.h`, `asm/io.h`, `asm/machdep.h`, `asm/traps.h`; plus 3 more. Defined functions:
`sun3x_hwclk`, `sun3x_timer_tick`, `sun3x_sched_init`. Declared functions: `local_irq_save`,
`local_irq_restore`, `sun3_disable_interrupts`. Key macros/defines: `M_CONTROL`, `M_SEC`, `M_MIN`,
`M_HOUR`, `M_DAY`, `M_DATE`, `M_MONTH`, `M_YEAR`, `C_WRITE`, `C_READ`, `C_SIGN`, `C_CALIB`.

## Control Flow and Behavior

control flow is entered from platform setup, firmware service wrappers, or generic
timekeeping/machdep hooks

## State and Persistence

persistent state includes PROM vectors, installed machdep callbacks, RTC register values, and
DVMA/IOMMU state for data movers

## Dependencies and Integration Points

integrates with Sun-3x PROM firmware, m68k machine setup, generic timekeeping, reset paths, and
device drivers

## Risks and Test Signals

firmware ABI and clock register mistakes can block boot or skew time; Sun-3x boot, clock read/write,
PROM console, and DMA tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.h -->
# sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.h

## Purpose

declares local interfaces for `sources/distributed-fs/ceph-client/arch/m68k/sun3x` so nearby m68k
machine or MMU files can share prototypes without exposing them globally

## Important APIs, Types, and Functions

Source read size: 19 lines, 433 bytes. Declared functions: `sun3x_hwclk`. Key macros/defines:
`SUN3X_TIME_H`. Types visible in this file: `mostek_dt`. External symbols referenced/declared:
`sun3x_hwclk`.

## Control Flow and Behavior

the header provides board or subsystem function prototypes, forward declarations, and include guards
consumed by adjacent C files

## State and Persistence

state is compile-time only, though the declared functions usually manipulate machine interrupt,
timer, PROM, or MMU state

## Dependencies and Integration Points

integrates local machine files with arch/m68k setup, machdep callbacks, and low-level assembly entry
points

## Risks and Test Signals

prototype drift causes build failures or wrong calling conventions; the platform defconfig build is
the first signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/sun3x/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/tools/amiga`, the
m68k platform area that supports an m68k machine-specific platform area

## Important APIs, Types, and Functions

Source read size: 12 lines, 161 bytes.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/dmesg.c -->
# sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/dmesg.c

## Purpose

implements an Amiga diagnostic dmesg extractor that scans chip memory for saved kernel message
records

## Important APIs, Types, and Functions

Source read size: 69 lines, 1656 bytes. Includes: `stdio.h`, `stdlib.h`, `unistd.h`. Defined
functions: `main`. Declared functions: `return`. Key macros/defines: `CHIPMEM_START`, `CHIPMEM_END`,
`SAVEKMSG_MAGIC1`, `SAVEKMSG_MAGIC2`. Types visible in this file: `savekmsg`.

## Control Flow and Behavior

main() parses an optional memory limit, scans for SAVE/KMSG magic, validates lengths, and prints the
saved kernel log payload

## State and Persistence

persistent state is only process-local scan buffers and stdout output; it does not modify the memory
image

## Dependencies and Integration Points

depends on Amiga saved-kmsg layout constants, stdio/unistd, and host access to a memory dump or
mapped chip memory

## Risks and Test Signals

bad bounds checks can read outside the supplied image; tests should cover missing magic, truncated
records, and valid saved logs
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/tools/amiga/dmesg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/Makefile -->
# sources/distributed-fs/ceph-client/arch/m68k/virt/Makefile

## Purpose

selects the object files built for `sources/distributed-fs/ceph-client/arch/m68k/virt`, the m68k
platform area that supports the m68k virtual platform used by emulators, including bootinfo parsing,
Goldfish timer, platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 6 lines, 135 bytes. Build selections: `obj-y -> config.o ints.o platform.o`.

## Control Flow and Behavior

Kbuild object variables include the platform's configuration, interrupt, PROM, DVMA, or helper
objects when the corresponding CONFIG symbol is enabled

## State and Persistence

there is no runtime state; the persistent effect is linked object coverage in vmlinux

## Dependencies and Integration Points

integrates with arch/m68k top-level Makefile/Kconfig.machine and the machine's machdep hook
implementation

## Risks and Test Signals

missing objects produce unresolved hooks or silently absent platform support; platform defconfig
builds are the main test signal
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/config.c -->
# sources/distributed-fs/ceph-client/arch/m68k/virt/config.c

## Purpose

supports the m68k virtual platform used by emulators, including bootinfo parsing, Goldfish timer,
platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 92 lines, 2146 bytes. Includes: `linux/reboot.h`, `linux/serial_core.h`,
`clocksource/timer-goldfish.h`, `asm/bootinfo.h`, `asm/bootinfo-virt.h`, `asm/byteorder.h`,
`asm/machdep.h`, `asm/virt.h`, `asm/config.h`. Defined functions: `virt_get_model`, `virt_reset`,
`virt_parse_bootinfo`, `virt_sched_init`, `config_virt`. Declared functions: `snprintf`. Types
visible in this file: `virt_booter_data`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/ints.c -->
# sources/distributed-fs/ceph-client/arch/m68k/virt/ints.c

## Purpose

supports the m68k virtual platform used by emulators, including bootinfo parsing, Goldfish timer,
platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 154 lines, 3698 bytes. Includes: `linux/delay.h`, `linux/interrupt.h`,
`linux/irq.h`, `linux/kernel.h`, `linux/sched.h`, `linux/sched/debug.h`, `linux/types.h`,
`linux/ioport.h`, `asm/hwtest.h`, `asm/irq.h`, `asm/irq_regs.h`, `asm/processor.h`; plus 1 more.
Defined functions: `gfpic_read`, `gfpic_write`, `virt_irq_enable`, `virt_irq_disable`,
`virt_irq_startup`, `virt_nmi_handler`, `goldfish_pic_irq`, `virt_init_IRQ`. Declared functions:
`ioread32be`, `iowrite32be`, `m68k_setup_irq_controller`, `DEFINE_RES_MEM_NAMED`, `pr_err`,
`irq_set_chained_handler`. Key macros/defines: `GFPIC_REG_IRQ_PENDING`, `GFPIC_REG_IRQ_DISABLE_ALL`,
`GFPIC_REG_IRQ_DISABLE`, `GFPIC_REG_IRQ_ENABLE`, `GF_PIC(irq)`, `GF_IRQ(irq)`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/ints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/platform.c -->
# sources/distributed-fs/ceph-client/arch/m68k/virt/platform.c

## Purpose

supports the m68k virtual platform used by emulators, including bootinfo parsing, Goldfish timer,
platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 94 lines, 2365 bytes. Includes: `linux/platform_device.h`, `linux/interrupt.h`,
`linux/memblock.h`, `asm/virt.h`, `asm/irq.h`. Defined functions: `virt_virtio_init`,
`virt_platform_init`. Declared functions: `platform_device_register_simple`, `ARRAY_SIZE`,
`platform_device_unregister`. Key macros/defines: `VIRTIO_BUS_NB`. Types visible in this file:
`platform_device`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/virt/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/Kbuild -->
# sources/distributed-fs/ceph-client/arch/microblaze/Kbuild

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze`

## Important APIs, Types, and Functions

Source read size: 8 lines, 153 bytes. Build selections: `obj-y -> kernel/`, `obj-y -> mm/`, `obj-y
-> boot/dts/`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/Kconfig -->
# sources/distributed-fs/ceph-client/arch/microblaze/Kconfig

## Purpose

declares the MicroBlaze architecture configuration surface, CPU feature dependencies, platform
choices, endian mode, MMU, cache, PCI, and generic kernel capability selections

## Important APIs, Types, and Functions

Source read size: 218 lines, 5809 bytes. Kconfig symbols: `MICROBLAZE`, `CPU_BIG_ENDIAN`,
`CPU_LITTLE_ENDIAN`, `ARCH_HAS_ILOG2_U32`, `ARCH_HAS_ILOG2_U64`, `GENERIC_HWEIGHT`,
`GENERIC_CALIBRATE_DELAY`, `GENERIC_CSUM`, `STACKTRACE_SUPPORT`, `LOCKDEP_SUPPORT`, `MMU`,
`CMDLINE_BOOL`, `CMDLINE`, `CMDLINE_FORCE`, `NR_CPUS`, `ADVANCED_OPTIONS`, `HIGHMEM`,
`LOWMEM_SIZE_BOOL`, `LOWMEM_SIZE`, `MANUAL_RESET_VECTOR`, `KERNEL_START_BOOL`, `KERNEL_START`,
`TASK_SIZE_BOOL`, `TASK_SIZE`; plus 1 more.

## Control Flow and Behavior

config entries select architecture feature symbols and source other MicroBlaze Kconfig fragments so
Kbuild can choose matching objects and compiler flags

## State and Persistence

persistent state is the generated .config/autoconf.h that shapes every compiled MicroBlaze object

## Dependencies and Integration Points

integrates with init/Kconfig, generic MM/IRQ/time/ftrace/perf options, platform Kconfig, and the
MicroBlaze Makefile

## Risks and Test Signals

bad dependencies produce unbootable or uncompilable kernels for a soft CPU configuration;
mmu_defconfig, randconfig, and QEMU/FPGA boots are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze`

## Important APIs, Types, and Functions

Source read size: 93 lines, 3495 bytes. Build selections: `libs-y -> arch/microblaze/lib/`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/boot/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/boot`

## Important APIs, Types, and Functions

Source read size: 35 lines, 890 bytes.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/boot/dts`

## Important APIs, Types, and Functions

Source read size: 20 lines, 355 bytes. Build selections: `dtb-y -> system.dtb`, `obj-y ->
linked_dtb.o`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/linked_dtb.S -->
# sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/linked_dtb.S

## Purpose

embeds a linked device tree blob into a dedicated assembly section for MicroBlaze boot images

## Important APIs, Types, and Functions

Source read size: 2 lines, 70 bytes.

## Control Flow and Behavior

the assembler source includes the generated DTB binary so early boot can find platform description
data without external firmware handoff

## State and Persistence

persistent state is the linked .dtb image inside the kernel binary

## Dependencies and Integration Points

integrates with boot/dts Makefile rules, vmlinux linking, and early device-tree unflattening

## Risks and Test Signals

section naming or missing DTB input prevents early platform discovery; dtbs and boot image builds
are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/linked_dtb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/Kbuild

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/include/asm`

## Important APIs, Types, and Functions

Source read size: 11 lines, 279 bytes. Build selections: `generated-y -> syscall_table.h`,
`generic-y -> cmpxchg.h`, `generic-y -> extable.h`, `generic-y -> kvm_para.h`, `generic-y ->
mcs_spinlock.h`, `generic-y -> parport.h`, `generic-y -> syscalls.h`, `generic-y -> tlb.h`,
`generic-y -> user.h`, `generic-y -> text-patching.h`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/asm-compat.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/asm-compat.h

## Purpose

normalizes constants and assembly syntax between C and assembler users

## Important APIs, Types, and Functions

Source read size: 18 lines, 519 bytes. Includes: `asm/types.h`. Key macros/defines:
`_ASM_MICROBLAZE_ASM_COMPAT_H`, `stringify_in_c(...)`, `ASM_CONST(x)`, `__stringify_in_c(...)`,
`__ASM_CONST(x)`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/asm-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/asm-offsets.h

## Purpose

includes generated assembler offsets for low-level MicroBlaze assembly

## Important APIs, Types, and Functions

Source read size: 1 lines, 35 bytes. Includes: `generated/asm-offsets.h`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/barrier.h

## Purpose

defines MicroBlaze memory barriers around the mbar instruction and generic fallbacks

## Important APIs, Types, and Functions

Source read size: 13 lines, 313 bytes. Includes: `asm-generic/barrier.h`. Key macros/defines:
`_ASM_MICROBLAZE_BARRIER_H`, `mb()`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cache.h

## Purpose

defines L1 cache alignment, DMA minimum alignment, and slab alignment constants

## Important APIs, Types, and Functions

Source read size: 26 lines, 648 bytes. Includes: `asm/registers.h`. Key macros/defines:
`_ASM_MICROBLAZE_CACHE_H`, `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `SMP_CACHE_BYTES`,
`ARCH_DMA_MINALIGN`, `ARCH_SLAB_MINALIGN`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cacheflush.h

## Purpose

declares cache controller operations and cache/TLB-facing flush helpers for pages, folios, and user
text updates

## Important APIs, Types, and Functions

Source read size: 103 lines, 3427 bytes. Includes: `linux/mm.h`, `linux/io.h`, `asm-
generic/cacheflush.h`. Defined functions: `flush_dcache_folio`, `copy_to_user_page`. Declared
functions: `microblaze_cache_init`, `flush_dcache_range`, `invalidate_icache_range`. Key
macros/defines: `_ASM_MICROBLAZE_CACHEFLUSH_H`, `enable_icache()`, `disable_icache()`,
`flush_icache()`, `flush_icache_range(start, end)`, `invalidate_icache()`,
`invalidate_icache_range(start, end)`, `enable_dcache()`, `disable_dcache()`, `invalidate_dcache()`,
`invalidate_dcache_range(start, end)`, `flush_dcache()`, `flush_dcache_range(start, end)`,
`ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_dcache_page(page)`, `flush_dcache_folio`,
`flush_cache_page(vma, vmaddr, pfn)`, `copy_to_user_page`. Types visible in this file: `scache`,
`page`. External symbols referenced/declared: `mbc`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/checksum.h

## Purpose

declares or selects IP checksum helpers for networking

## Important APIs, Types, and Functions

Source read size: 36 lines, 806 bytes. Includes: `asm-generic/checksum.h`. Defined functions:
`Copyright`. Key macros/defines: `_ASM_MICROBLAZE_CHECKSUM_H`, `csum_tcpudp_nofold`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cpuinfo.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cpuinfo.h

## Purpose

defines CPU feature data structures, PVR-derived fields, and CPU information publication helpers

## Important APIs, Types, and Functions

Source read size: 105 lines, 2043 bytes. Includes: `linux/of.h`. Defined functions: `fcpu`. Declared
functions: `setup_cpuinfo`, `of_property_read_u32`. Key macros/defines: `_ASM_MICROBLAZE_CPUINFO_H`.
Types visible in this file: `cpu_ver_key`, `family_string_key`, `cpuinfo`. External symbols
referenced/declared: `cpu_ver_lookup`, `family_string_lookup`, `cpuinfo`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/cpuinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/current.h

## Purpose

implements current task lookup from the MicroBlaze stack/thread pointer model

## Important APIs, Types, and Functions

Source read size: 26 lines, 716 bytes. Declared functions: `Copyright`. Key macros/defines:
`_ASM_MICROBLAZE_CURRENT_H`, `CURRENT_TASK`, `get_current()`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/delay.h

## Purpose

defines busy-wait delay loops and calibration hooks

## Important APIs, Types, and Functions

Source read size: 85 lines, 2138 bytes. Includes: `linux/param.h`. Defined functions: `Copyright`,
`__udelay`. Declared functions: `volatile`, `__bad_udelay`, `__udelay`. Key macros/defines:
`_ASM_MICROBLAZE_DELAY_H`, `__MAX_UDELAY`, `__MAX_NDELAY`, `udelay(n)`, `ndelay(n)`, `muldiv(a, b,
c)`. External symbols referenced/declared: `loops_per_jiffy`, `__bad_udelay`, `__bad_ndelay`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/dma.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/dma.h

## Purpose

declares architecture DMA address limits and generic DMA interfaces

## Important APIs, Types, and Functions

Source read size: 12 lines, 330 bytes. Key macros/defines: `_ASM_MICROBLAZE_DMA_H`,
`MAX_DMA_ADDRESS`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/elf.h

## Purpose

defines kernel-side ELF process, core-dump, register, and loader behavior

## Important APIs, Types, and Functions

Source read size: 27 lines, 602 bytes. Includes: `uapi/asm/elf.h`. Key macros/defines:
`_ASM_MICROBLAZE_ELF_H`, `SET_PERSONALITY(ex)`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/entry.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/entry.h

## Purpose

declares low-level exception/syscall entry helpers and thread flag work masks

## Important APIs, Types, and Functions

Source read size: 34 lines, 1020 bytes. Includes: `asm/percpu.h`, `asm/ptrace.h`, `linux/linkage.h`.
Declared functions: `Copyright`. Key macros/defines: `_ASM_MICROBLAZE_ENTRY_H`, `PER_CPU(var)`.
External symbols referenced/declared: `do_notify_resume`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/entry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/exceptions.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/exceptions.h

## Purpose

declares exception handlers and hardware exception enable/disable helpers

## Important APIs, Types, and Functions

Source read size: 69 lines, 1930 bytes. Declared functions: `Copyright`. Key macros/defines:
`_ASM_MICROBLAZE_EXCEPTIONS_H`, `HWEX_MSR_BIT`, `__enable_hw_exceptions()`,
`__disable_hw_exceptions()`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/exceptions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/fixmap.h

## Purpose

defines fixed virtual mapping slots used during early ioremap and highmem/fixmap operations

## Important APIs, Types, and Functions

Source read size: 66 lines, 1876 bytes. Includes: `linux/kernel.h`, `asm/page.h`, `linux/threads.h`,
`asm/kmap_size.h`, `asm-generic/fixmap.h`. Declared functions: `__set_fixmap`. Key macros/defines:
`_ASM_FIXMAP_H`, `FIXADDR_TOP`, `__FIXADDR_SIZE`, `FIXADDR_START`, `FIXMAP_PAGE_NOCACHE`. Types
visible in this file: `fixed_addresses`. External symbols referenced/declared: `__set_fixmap`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/flat.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/flat.h

## Purpose

implements FLAT binary relocation access helpers for no-MMU style binary support

## Important APIs, Types, and Functions

Source read size: 81 lines, 1984 bytes. Includes: `linux/unaligned.h`. Defined functions:
`Copyright`, `flat_put_addr_at_rp`. Declared functions: `put_unaligned`. Key macros/defines:
`_ASM_MICROBLAZE_FLAT_H`, `flat_get_relocate_addr(rel)`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/flat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ftrace.h

## Purpose

defines MicroBlaze ftrace call-site sizing and graph tracing hooks

## Important APIs, Types, and Functions

Source read size: 28 lines, 719 bytes. Defined functions: `ftrace_call_adjust`. Declared functions:
`_mcount`. Key macros/defines: `_ASM_MICROBLAZE_FTRACE`, `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`. Types
visible in this file: `dyn_arch_ftrace`. External symbols referenced/declared: `_mcount`,
`ftrace_call_graph`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/futex.h

## Purpose

implements futex atomic operations on user memory with exception recovery

## Important APIs, Types, and Functions

Source read size: 99 lines, 2179 bytes. Includes: `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`.
Defined functions: `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`. Declared
functions: `__volatile__`, `__futex_atomic_op`. Key macros/defines: `_ASM_MICROBLAZE_FUTEX_H`,
`__futex_atomic_op(insn, ret, oldval, uaddr, oparg)`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/hash.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/hash.h

## Purpose

selects hash helpers and generic hashing integration

## Important APIs, Types, and Functions

Source read size: 82 lines, 2429 bytes. Defined functions: `__hash_32`. Key macros/defines:
`_ASM_HASH_H`, `HAVE_ARCH__HASH_32`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/highmem.h

## Purpose

defines highmem kmap bounds and helper declarations

## Important APIs, Types, and Functions

Source read size: 61 lines, 1800 bytes. Includes: `linux/init.h`, `linux/interrupt.h`,
`linux/uaccess.h`, `asm/fixmap.h`. Defined functions: `memory`. Key macros/defines:
`_ASM_HIGHMEM_H`, `PKMAP_ORDER`, `LAST_PKMAP`, `PKMAP_BASE`, `LAST_PKMAP_MASK`, `PKMAP_NR(virt)`,
`PKMAP_ADDR(nr)`, `flush_cache_kmaps()`, `arch_kmap_local_post_map(vaddr, pteval)`,
`arch_kmap_local_post_unmap(vaddr)`. External symbols referenced/declared: `pkmap_page_table`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/io.h

## Purpose

defines MMIO, raw I/O accessors, ioremap policy, and port-I/O compatibility hooks

## Important APIs, Types, and Functions

Source read size: 60 lines, 1643 bytes. Includes: `asm/byteorder.h`, `asm/page.h`, `linux/types.h`,
`linux/mm.h`, `asm-generic/io.h`. Declared functions: `pci_iounmap`. Key macros/defines:
`_ASM_MICROBLAZE_IO_H`, `_IO_BASE`, `_ISA_MEM_BASE`, `pci_iounmap`, `PCI_IOBASE`, `IO_SPACE_LIMIT`,
`out_be32(a, v)`, `out_be16(a, v)`, `in_be32(a)`, `in_be16(a)`, `writel_be(v, a)`, `readl_be(a)`,
`out_le32(a, v)`, `out_le16(a, v)`, `in_le32(a)`, `in_le16(a)`, `out_8(a, v)`, `in_8(a)`. Types
visible in this file: `pci_dev`. External symbols referenced/declared: `pci_iounmap`, `isa_io_base`,
`isa_mem_base`, `iounmap`, `ioremap`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irq.h

## Purpose

declares irq numbering and architecture IRQ initialization hooks

## Important APIs, Types, and Functions

Source read size: 14 lines, 274 bytes. Includes: `asm-generic/irq.h`. Declared functions:
`Copyright`. Key macros/defines: `_ASM_MICROBLAZE_IRQ_H`. Types visible in this file: `pt_regs`.
External symbols referenced/declared: `do_IRQ`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irqflags.h

## Purpose

implements interrupt flag save/restore, enable, disable, and MSR bit manipulation

## Important APIs, Types, and Functions

Source read size: 119 lines, 2529 bytes. Includes: `linux/types.h`, `asm/registers.h`. Defined
functions: `Copyright`, `arch_local_irq_disable`, `arch_local_irq_enable`, `arch_local_irq_save`,
`arch_local_save_flags`, `arch_local_irq_restore`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`.
Declared functions: `volatile`, `arch_irqs_disabled_flags`. Key macros/defines:
`_ASM_MICROBLAZE_IRQFLAGS_H`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/kgdb.h

## Purpose

defines KGDB breakpoint and register integration details

## Important APIs, Types, and Functions

Source read size: 32 lines, 741 bytes. Defined functions: `arch_kgdb_breakpoint`. Declared
functions: `__volatile__`, `microblaze_kgdb_break`. Key macros/defines: `__MICROBLAZE_KGDB_H__`,
`CACHE_FLUSH_IS_SAFE`, `BUFMAX`, `NUMREGBYTES`, `BREAK_INSTR_SIZE`. Types visible in this file:
`pt_regs`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu.h

## Purpose

defines the MicroBlaze MMU context, TLB, and page-table support data

## Important APIs, Types, and Functions

Source read size: 119 lines, 4052 bytes. Declared functions: `_tlbie`. Key macros/defines:
`_ASM_MICROBLAZE_MMU_H`, `PP_RWXX`, `PP_RWRX`, `PP_RWRW`, `PP_RXRX`, `MICROBLAZE_TLB_SIZE`,
`MICROBLAZE_TLB_SKIP`, `MICROBLAZE_LMB_TLB_ID`, `TLB_LO`, `TLB_HI`, `TLB_DATA`, `TLB_TAG`,
`TLB_EPN_MASK`, `TLB_PAGESZ_MASK`, `TLB_PAGESZ(x)`, `PAGESZ_1K`, `PAGESZ_4K`, `PAGESZ_16K`,
`PAGESZ_64K`, `PAGESZ_256K`, `PAGESZ_1M`, `PAGESZ_4M`, `PAGESZ_16M`, `TLB_VALID`; plus 11 more.
Types visible in this file: `mm_context_t`. External symbols referenced/declared: `_tlbie`,
`_tlbia`, `tlb_skip`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu_context.h

## Purpose

selects the MMU context implementation header

## Important APIs, Types, and Functions

Source read size: 2 lines, 72 bytes. Includes: `asm/mmu_context_mm.h`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu_context_mm.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu_context_mm.h

## Purpose

implements MMU context lifecycle, activation, ASID/TLB behavior, and lazy TLB hooks

## Important APIs, Types, and Functions

Source read size: 140 lines, 3893 bytes. Includes: `linux/atomic.h`, `linux/mm_types.h`,
`linux/sched.h`, `asm/bitops.h`, `asm/mmu.h`, `asm-generic/mm_hooks.h`, `asm-generic/mmu_context.h`.
Defined functions: `get_mmu_context`, `destroy_context`, `switch_mm`, `activate_mm`. Declared
functions: `Copyright`, `clear_bit`, `mmu_context_init`. Key macros/defines:
`_ASM_MICROBLAZE_MMU_CONTEXT_H`, `CTX_TO_VSID(ctx, va)`, `NO_CONTEXT`, `LAST_CONTEXT`,
`FIRST_CONTEXT`, `init_new_context(tsk, mm)`, `destroy_context`, `activate_mm`. Types visible in
this file: `task_struct`, `mm_struct`. External symbols referenced/declared: `set_context`,
`context_map`, `next_mmu_context`, `nr_free_contexts`, `context_mm`, `steal_context`,
`mmu_context_init`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/mmu_context_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/module.h

## Purpose

defines MicroBlaze relocation constants used by loadable module relocation

## Important APIs, Types, and Functions

Source read size: 28 lines, 704 bytes. Includes: `asm-generic/module.h`. Key macros/defines:
`_ASM_MICROBLAZE_MODULE_H`, `R_MICROBLAZE_NONE`, `R_MICROBLAZE_32`, `R_MICROBLAZE_32_PCREL`,
`R_MICROBLAZE_64_PCREL`, `R_MICROBLAZE_32_PCREL_LO`, `R_MICROBLAZE_64`, `R_MICROBLAZE_32_LO`,
`R_MICROBLAZE_SRO32`, `R_MICROBLAZE_SRW32`, `R_MICROBLAZE_64_NONE`, `R_MICROBLAZE_32_SYM_OP_SYM`,
`R_MICROBLAZE_NUM`. Types visible in this file: `counter`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/page.h

## Purpose

defines page table scalar types, virt/phys conversion, pfn helpers, and kernel address layout

## Important APIs, Types, and Functions

Source read size: 141 lines, 3715 bytes. Includes: `linux/pfn.h`, `asm/setup.h`, `asm/asm-compat.h`,
`linux/const.h`, `vdso/page.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`. Defined
functions: `virt_to_pfn`. Declared functions: `page_is_ram`, `phys_to_pfn`, `__va`. Key
macros/defines: `_ASM_MICROBLAZE_PAGE_H`, `LOAD_OFFSET`, `PTE_SHIFT`, `PAGE_OFFSET`, `PTE_FMT`,
`copy_page(to, from)`, `clear_page(pgaddr)`, `copy_user_page(vto, vfrom, vaddr, topg)`,
`pte_val(x)`, `pgprot_val(x)`, `pgd_val(x)`, `__pte(x)`, `__pgd(x)`, `__pgprot(x)`,
`phys_to_pfn(phys)`, `pfn_to_phys(pfn)`, `virt_to_page(kaddr)`, `page_to_virt(page)`,
`ARCH_PFN_OFFSET`, `__virt_to_phys(addr)`, `__phys_to_virt(addr)`, `tophys(rd, rs)`, `tovirt(rd,
rs)`, `__pa(x)`; plus 3 more. Types visible in this file: `pte_basic_t`, `pgtable_t`, `pte`,
`pgprot`, `pgd`. External symbols referenced/declared: `max_low_pfn`, `min_low_pfn`, `max_pfn`,
`memory_start`, `memory_size`, `lowmem_size`, `kernel_tlb`, `page_is_ram`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci-bridge.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci-bridge.h

## Purpose

declares PCI controller structures and I/O port detection helpers

## Important APIs, Types, and Functions

Source read size: 49 lines, 1040 bytes. Includes: `linux/pci.h`, `linux/list.h`, `linux/ioport.h`.
Defined functions: `pcibios_vaddr_is_ioport`, `isa_vaddr_is_ioport`. Declared functions:
`pcibios_vaddr_is_ioport`. Key macros/defines: `_ASM_MICROBLAZE_PCI_BRIDGE_H`. Types visible in this
file: `device_node`, `pci_controller`, `pci_bus`, `list_head`, `resource`. External symbols
referenced/declared: `hose_list`, `pcibios_vaddr_is_ioport`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci.h

## Purpose

defines PCI DMA, resource, and pcibios policy hooks

## Important APIs, Types, and Functions

Source read size: 44 lines, 1025 bytes. Includes: `linux/types.h`, `linux/slab.h`, `linux/string.h`,
`linux/dma-mapping.h`, `linux/pci.h`, `linux/scatterlist.h`, `asm/io.h`, `asm/pci-bridge.h`. Defined
functions: `xilinx_pci_init`. Declared functions: `numbers`. Key macros/defines:
`__ASM_MICROBLAZE_PCI_H`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `pcibios_assign_all_busses()`,
`HAVE_PCI_MMAP`, `ARCH_GENERIC_PCI_MMAP_RESOURCE`. Types visible in this file: `file`. External
symbols referenced/declared: `pci_domain_nr`, `pci_proc_domain`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgalloc.h

## Purpose

implements page-table page allocation and freeing helpers

## Important APIs, Types, and Functions

Source read size: 36 lines, 950 bytes. Includes: `linux/kernel.h`, `linux/highmem.h`,
`linux/pgtable.h`, `asm/setup.h`, `asm/io.h`, `asm/page.h`, `asm/cache.h`, `asm-generic/pgalloc.h`.
Declared functions: `Copyright`. Key macros/defines: `_ASM_MICROBLAZE_PGALLOC_H`,
`__HAVE_ARCH_PTE_ALLOC_ONE_KERNEL`, `pgd_alloc(mm)`, `__pte_free_tlb(tlb, pte, addr)`,
`pmd_populate(mm, pmd, pte)`, `pmd_populate_kernel(mm, pmd, pte)`. External symbols
referenced/declared: `__bad_pte`, `pte_alloc_one_kernel`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgtable.h

## Purpose

defines MicroBlaze page-table layout, PTE bits, protection values, and PTE/PMD/PGD accessors

## Important APIs, Types, and Functions

Source read size: 437 lines, 14059 bytes. Includes: `asm/setup.h`, `asm-generic/pgtable-nopmd.h`,
`linux/sched.h`, `linux/threads.h`, `asm/processor.h`, `asm/mmu.h`, `asm/page.h`. Defined functions:
`pte_present`, `pte_write`, `pte_exec`, `pte_dirty`, `pte_young`, `pte_uncache`, `pte_cache`,
`mk_pte_phys`, `pte_modify`, `The`, `set_pte`, `ptep_test_and_clear_young`,
`ptep_test_and_clear_dirty`, `ptep_get_and_clear`, `ptep_mkdirty`, `pmd_page_vaddr`,
`pte_swp_exclusive`, `pte_swp_mkexclusive`, `pte_swp_clear_exclusive`. Declared functions:
`Copyright`, `raw_local_irq_save`, `__pte`, `iopa`. Key macros/defines: `_ASM_MICROBLAZE_PGTABLE_H`,
`VMALLOC_START`, `VMALLOC_END`, `_PAGE_CACHE_CTL`, `pgprot_noncached(prot)`,
`pgprot_noncached_wc(prot)`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `PTRS_PER_PTE`,
`PTRS_PER_PMD`, `PTRS_PER_PGD`, `USER_PTRS_PER_PGD`, `USER_PGD_PTRS`, `KERNEL_PGD_PTRS`,
`pte_ERROR(e)`, `pgd_ERROR(e)`, `_PAGE_GUARDED`, `_PAGE_PRESENT`, `_PAGE_NO_CACHE`,
`_PAGE_WRITETHRU`, `_PAGE_USER`, `_PAGE_RW`, `_PAGE_DIRTY`; plus 48 more. Types visible in this
file: `vm_area_struct`. External symbols referenced/declared: `mem_init_done`, `va_to_phys`,
`va_to_pte`, `swapper_pg_dir`, `iopa`, `ioremap_base`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/processor.h

## Purpose

defines thread_struct, start-thread behavior, CPU idle hooks, and process state helpers

## Important APIs, Types, and Functions

Source read size: 92 lines, 2584 bytes. Includes: `asm/ptrace.h`, `asm/setup.h`, `asm/registers.h`,
`asm/entry.h`, `asm/current.h`. Declared functions: `Copyright`, `__get_wchan`. Key macros/defines:
`_ASM_MICROBLAZE_PROCESSOR_H`, `cpu_relax()`, `task_pt_regs(tsk)`, `TASK_SIZE`,
`TASK_UNMAPPED_BASE`, `THREAD_KSP`, `INIT_THREAD`, `KERNEL_STACK_SIZE`, `task_tos(task)`,
`task_regs(task)`, `task_pt_regs_plus_args(tsk)`, `task_sp(task)`, `task_pc(task)`,
`KSTK_EIP(task)`, `KSTK_ESP(task)`, `STACK_TOP`, `STACK_TOP_MAX`. Types visible in this file:
`thread_struct`, `pt_regs`. External symbols referenced/declared: `cpuinfo_op`, `ret_from_fork`,
`ret_from_kernel_thread`, `of_debugfs_root`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ptrace.h

## Purpose

defines kernel pt_regs helpers and register accessors

## Important APIs, Types, and Functions

Source read size: 24 lines, 593 bytes. Includes: `uapi/asm/ptrace.h`. Defined functions:
`Copyright`. Key macros/defines: `_ASM_MICROBLAZE_PTRACE_H`, `kernel_mode(regs)`, `user_mode(regs)`,
`instruction_pointer(regs)`, `profile_pc(regs)`, `user_stack_pointer(regs)`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pvr.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pvr.h

## Purpose

defines Processor Version Register structures, feature bit masks, and PVR access helpers

## Important APIs, Types, and Functions

Source read size: 224 lines, 8791 bytes. Declared functions: `cpu_has_pvr`. Key macros/defines:
`_ASM_MICROBLAZE_PVR_H`, `PVR_MSR_BIT`, `PVR0_PVR_FULL_MASK`, `PVR0_USE_BARREL_MASK`,
`PVR0_USE_DIV_MASK`, `PVR0_USE_HW_MUL_MASK`, `PVR0_USE_FPU_MASK`, `PVR0_USE_EXC_MASK`,
`PVR0_USE_ICACHE_MASK`, `PVR0_USE_DCACHE_MASK`, `PVR0_USE_MMU`, `PVR0_USE_BTC`, `PVR0_ENDI`,
`PVR0_VERSION_MASK`, `PVR0_USER1_MASK`, `PVR1_USER2_MASK`, `PVR2_D_OPB_MASK`, `PVR2_D_LMB_MASK`,
`PVR2_I_OPB_MASK`, `PVR2_I_LMB_MASK`, `PVR2_INTERRUPT_IS_EDGE_MASK`, `PVR2_EDGE_IS_POSITIVE_MASK`,
`PVR2_D_PLB_MASK`, `PVR2_I_PLB_MASK`; plus 111 more. Types visible in this file: `pvr_s`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/pvr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/registers.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/registers.h

## Purpose

names MicroBlaze special-purpose registers and MSR bit definitions

## Important APIs, Types, and Functions

Source read size: 45 lines, 1508 bytes. Key macros/defines: `_ASM_MICROBLAZE_REGISTERS_H`, `MSR_BE`,
`MSR_IE`, `MSR_C`, `MSR_BIP`, `MSR_FSL`, `MSR_ICE`, `MSR_DZ`, `MSR_DCE`, `MSR_EE`, `MSR_EIP`,
`MSR_CC`, `FSR_IO`, `FSR_DZ`, `FSR_OF`, `FSR_UF`, `FSR_DO`, `MSR_UM`, `MSR_UMS`, `MSR_VM`,
`MSR_VMS`, `MSR_KERNEL`, `MSR_KERNEL_VMS`, `ESR_DIZ`; plus 1 more.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/seccomp.h

## Purpose

selects MicroBlaze seccomp syscall metadata

## Important APIs, Types, and Functions

Source read size: 11 lines, 256 bytes. Includes: `linux/unistd.h`, `asm-generic/seccomp.h`. Key
macros/defines: `_ASM_MICROBLAZE_SECCOMP_H`, `__NR_seccomp_sigreturn`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/sections.h

## Purpose

declares architecture section symbols

## Important APIs, Types, and Functions

Source read size: 20 lines, 503 bytes. Includes: `asm-generic/sections.h`. Key macros/defines:
`_ASM_MICROBLAZE_SECTIONS_H`. External symbols referenced/declared: `_ssbss`, `__ivt_start`,
`_fdt_start`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/setup.h

## Purpose

declares early machine setup, reset, halt, poweroff, and MMU reset hooks

## Important APIs, Types, and Functions

Source read size: 29 lines, 721 bytes. Includes: `uapi/asm/setup.h`. Declared functions:
`Copyright`. Key macros/defines: `_ASM_MICROBLAZE_SETUP_H`. External symbols referenced/declared:
`cmd_line`, `klimit`, `mmu_reset`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/string.h

## Purpose

declares architecture-optimized memset, memcpy, and memmove

## Important APIs, Types, and Functions

Source read size: 23 lines, 532 bytes. Declared functions: `Copyright`. Key macros/defines:
`_ASM_MICROBLAZE_STRING_H`, `__HAVE_ARCH_MEMSET`, `__HAVE_ARCH_MEMCPY`, `__HAVE_ARCH_MEMMOVE`.
External symbols referenced/declared: `memset`, `memcpy`, `memmove`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/switch_to.h

## Purpose

declares the assembly context switch entry and wraps switch_to

## Important APIs, Types, and Functions

Source read size: 21 lines, 493 bytes. Declared functions: `Copyright`, `task_thread_info`. Key
macros/defines: `_ASM_MICROBLAZE_SWITCH_TO_H`, `switch_to(prev, next, last)`. Types visible in this
file: `task_struct`, `thread_info`. External symbols referenced/declared: `_switch_to`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/syscall.h

## Purpose

defines syscall number, argument, return-value, and rollback accessors

## Important APIs, Types, and Functions

Source read size: 86 lines, 1902 bytes. Includes: `uapi/linux/audit.h`, `linux/kernel.h`,
`linux/sched.h`, `asm/ptrace.h`. Defined functions: `syscall_get_nr`, `syscall_set_nr`,
`syscall_rollback`, `syscall_get_error`, `syscall_get_return_value`, `syscall_set_return_value`,
`microblaze_get_syscall_arg`, `syscall_get_arguments`, `syscall_get_arch`. Declared functions:
`BUG`, `do_syscall_trace_enter`. Key macros/defines: `__ASM_MICROBLAZE_SYSCALL_H`. Types visible in
this file: `pt_regs`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/thread_info.h

## Purpose

defines thread_info layout, flags, stack size, and current-thread helpers

## Important APIs, Types, and Functions

Source read size: 143 lines, 3844 bytes. Includes: `linux/types.h`, `asm/processor.h`. Declared
functions: `asm`. Key macros/defines: `_ASM_MICROBLAZE_THREAD_INFO_H`, `THREAD_SHIFT`,
`THREAD_SIZE`, `THREAD_SIZE_ORDER`, `INIT_THREAD_INFO(tsk)`, `TIF_SYSCALL_TRACE`,
`TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_SINGLESTEP`, `TIF_NOTIFY_SIGNAL`,
`TIF_MEMDIE`, `TIF_SYSCALL_AUDIT`, `TIF_SECCOMP`, `TIF_POLLING_NRFLAG`, `_TIF_SYSCALL_TRACE`,
`_TIF_NOTIFY_RESUME`, `_TIF_SIGPENDING`, `_TIF_NEED_RESCHED`, `_TIF_SINGLESTEP`,
`_TIF_NOTIFY_SIGNAL`, `_TIF_POLLING_NRFLAG`, `_TIF_SYSCALL_AUDIT`, `_TIF_SECCOMP`; plus 4 more.
Types visible in this file: `cpu_context`, `thread_info`, `task_struct`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/timex.h

## Purpose

defines MicroBlaze clock tick type and timebase constants

## Important APIs, Types, and Functions

Source read size: 13 lines, 266 bytes. Includes: `asm-generic/timex.h`. Key macros/defines:
`_ASM_MICROBLAZE_TIMEX_H`, `CLOCK_TICK_RATE`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/tlbflush.h

## Purpose

declares local/global TLB flush helpers

## Important APIs, Types, and Functions

Source read size: 53 lines, 1687 bytes. Includes: `linux/sched.h`, `linux/threads.h`,
`asm/processor.h`, `asm/mmu.h`, `asm/page.h`. Defined functions: `local_flush_tlb_all`,
`local_flush_tlb_mm`, `local_flush_tlb_page`, `local_flush_tlb_range`, `flush_tlb_pgtables`.
Declared functions: `Copyright`. Key macros/defines: `_ASM_MICROBLAZE_TLBFLUSH_H`, `__tlbia()`,
`__tlbie(x)`, `flush_tlb_kernel_range(start, end)`, `update_mmu_cache_range(vmf, vma, addr, ptep,
nr)`, `update_mmu_cache(vma, addr, pte)`, `flush_tlb_all`, `flush_tlb_mm`, `flush_tlb_page`,
`flush_tlb_range`. External symbols referenced/declared: `_tlbie`, `_tlbia`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/uaccess.h

## Purpose

implements user memory access validation, copy, clear, get_user, put_user, and exception-table
wrappers

## Important APIs, Types, and Functions

Source read size: 269 lines, 7126 bytes. Includes: `linux/kernel.h`, `asm/mmu.h`, `asm/page.h`,
`linux/pgtable.h`, `asm/extable.h`, `linux/string.h`, `asm-generic/access_ok.h`. Defined functions:
`__clear_user`, `clear_user`, `raw_copy_from_user`, `raw_copy_to_user`. Declared functions:
`Copyright`, `__volatile__`, `__clear_user`, `__user_bad`, `typeof`, `__get_user_asm`,
`__put_user_asm`, `__copy_tofrom_user`, `strncpy_from_user`. Key macros/defines:
`_ASM_MICROBLAZE_UACCESS_H`, `__FIXUP_SECTION`, `__EX_TABLE_SECTION`, `__get_user_asm(insn,
__gu_ptr, __gu_val, __gu_err)`, `get_user(x, ptr)`, `__get_user(x, ptr)`, `__put_user_asm(insn,
__gu_ptr, __gu_val, __gu_err)`, `__put_user_asm_8(__gu_ptr, __gu_val, __gu_err)`, `put_user(x,
ptr)`, `__put_user_check(x, ptr, size)`, `__put_user(x, ptr)`, `INLINE_COPY_FROM_USER`,
`INLINE_COPY_TO_USER`. External symbols referenced/declared: `__copy_tofrom_user`, `__user_bad`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unistd.h

## Purpose

connects MicroBlaze syscall numbering to generic generated syscall headers

## Important APIs, Types, and Functions

Source read size: 38 lines, 1053 bytes. Includes: `uapi/asm/unistd.h`. Key macros/defines:
`_ASM_MICROBLAZE_UNISTD_H`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_ALARM`,
`__ARCH_WANT_SYS_GETHOSTNAME`, `__ARCH_WANT_SYS_PAUSE`, `__ARCH_WANT_SYS_SIGNAL`,
`__ARCH_WANT_SYS_TIME32`, `__ARCH_WANT_SYS_UTIME32`, `__ARCH_WANT_SYS_WAITPID`,
`__ARCH_WANT_SYS_SOCKETCALL`, `__ARCH_WANT_SYS_FADVISE64`, `__ARCH_WANT_SYS_GETPGRP`,
`__ARCH_WANT_SYS_NICE`, `__ARCH_WANT_SYS_OLDUMOUNT`, `__ARCH_WANT_SYS_SIGPENDING`,
`__ARCH_WANT_SYS_SIGPROCMASK`, `__ARCH_WANT_SYS_CLONE`, `__ARCH_WANT_SYS_VFORK`,
`__ARCH_WANT_SYS_FORK`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unwind.h

## Purpose

declares stack unwinding data and helpers

## Important APIs, Types, and Functions

Source read size: 27 lines, 611 bytes. Declared functions: `microblaze_unwind`. Key macros/defines:
`__MICROBLAZE_UNWIND_H`. Types visible in this file: `stack_trace`, `trap_handler_info`. External
symbols referenced/declared: `microblaze_trap_handlers`, `_hw_exception_handler`,
`ex_handler_unhandled`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/vmalloc.h

## Purpose

defines architecture vmalloc mapping policy

## Important APIs, Types, and Functions

Source read size: 4 lines, 108 bytes. Key macros/defines: `_ASM_MICROBLAZE_VMALLOC_H`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/xilinx_mb_manager.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/xilinx_mb_manager.h

## Purpose

declares Xilinx MicroBlaze management platform hooks

## Important APIs, Types, and Functions

Source read size: 29 lines, 861 bytes. Includes: `linux/of_address.h`. Declared functions:
`Copyright`. Key macros/defines: `_XILINX_MB_MANAGER_H`, `XMB_INJECT_ERR_OFFSET`.

## Control Flow and Behavior

the header provides macros, inline functions, type definitions, or declarations that are expanded
into core MicroBlaze kernel, MM, entry, scheduler, IRQ, tracing, or driver code

## State and Persistence

state is generally compile-time definitions; inline helpers may manipulate MSR bits, TLB entries,
page tables, CPU registers, user memory, or task/thread state at runtime

## Dependencies and Integration Points

integrates with asm-generic fallbacks, MicroBlaze low-level assembly, generic
MM/scheduler/IRQ/syscall/cache subsystems, and device-tree platform code

## Risks and Test Signals

because these headers sit on architecture-wide interfaces, small changes can break boot or ABI
assumptions; allmodconfig builds plus targeted MM, uaccess, futex, signal, and tracing tests are
signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/asm/xilinx_mb_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/Kbuild

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/include/uapi/asm`

## Important APIs, Types, and Functions

Source read size: 3 lines, 86 bytes. Build selections: `generated-y -> unistd_32.h`, `generic-y ->
ucontext.h`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/auxvec.h

## Purpose

declares MicroBlaze auxiliary vector constants for userspace process startup

## Important APIs, Types, and Functions

Source read size: 2 lines, 64 bytes.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/byteorder.h

## Purpose

selects little-endian or big-endian exported byteorder helpers based on kernel configuration

## Important APIs, Types, and Functions

Source read size: 11 lines, 298 bytes. Includes: `linux/byteorder/little_endian.h`,
`linux/byteorder/big_endian.h`. Key macros/defines: `_ASM_MICROBLAZE_BYTEORDER_H`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/elf.h

## Purpose

defines user-visible ELF machine constants, relocation numbers, and register/core-dump layouts

## Important APIs, Types, and Functions

Source read size: 123 lines, 3331 bytes. Includes: `linux/elf-em.h`, `asm/ptrace.h`,
`asm/byteorder.h`. Declared functions: `Copyright`. Key macros/defines:
`_UAPI_ASM_MICROBLAZE_ELF_H`, `EM_MICROBLAZE_OLD`, `ELF_ARCH`, `elf_check_arch(x)`, `ELF_CLASS`,
`ELF_GREG_T`, `ELF_NGREG`, `ELF_GREGSET_T`, `ELF_FPREGSET_T`, `ELF_NFPREG`, `ELF_ET_DYN_BASE`,
`ELF_DATA`, `ELF_EXEC_PAGESIZE`, `ELF_CORE_COPY_REGS(_dest, _regs)`, `ELF_HWCAP`, `ELF_PLATFORM`,
`ELF_PLAT_INIT(_r, _f)`. Types visible in this file: `elf_greg_t`, `elf_fpreg_t`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/posix_types.h

## Purpose

selects exported POSIX type definitions for MicroBlaze

## Important APIs, Types, and Functions

Source read size: 10 lines, 302 bytes. Includes: `asm-generic/posix_types.h`. Key macros/defines:
`_ASM_MICROBLAZE_POSIX_TYPES_H`, `__kernel_mode_t`. Types visible in this file: `__kernel_mode_t`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/ptrace.h

## Purpose

defines user-visible pt_regs/register structures and ptrace constants

## Important APIs, Types, and Functions

Source read size: 73 lines, 1827 bytes. Key macros/defines: `_UAPI_ASM_MICROBLAZE_PTRACE_H`,
`PT_GPR(n)`, `PT_PC`, `PT_MSR`, `PT_EAR`, `PT_ESR`, `PT_FSR`, `PT_KERNEL_MODE`. Types visible in
this file: `pt_regs`, `microblaze_reg_t`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/setup.h

## Purpose

defines exported setup constants such as command-line sizing

## Important APIs, Types, and Functions

Source read size: 17 lines, 532 bytes. Key macros/defines: `_UAPI_ASM_MICROBLAZE_SETUP_H`,
`COMMAND_LINE_SIZE`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/sigcontext.h

## Purpose

defines the user-visible signal context saved in signal frames

## Important APIs, Types, and Functions

Source read size: 21 lines, 537 bytes. Includes: `asm/ptrace.h`. Key macros/defines:
`_ASM_MICROBLAZE_SIGCONTEXT_H`. Types visible in this file: `sigcontext`, `pt_regs`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/unistd.h

## Purpose

selects generic syscall numbering and architecture syscall count exports

## Important APIs, Types, and Functions

Source read size: 16 lines, 495 bytes. Includes: `asm/unistd_32.h`. Key macros/defines:
`_UAPI_ASM_MICROBLAZE_UNISTD_H`.

## Control Flow and Behavior

the file is consumed by headers_install and userspace libc/tooling, so constants and structures must
remain ABI-compatible

## State and Persistence

there is no mutable kernel runtime state, but compiled userspace and trace/debug tools persist the
ABI definitions

## Dependencies and Integration Points

integrates with asm-generic UAPI headers, ELF loaders, signal delivery, ptrace, seccomp, libc, and
perf/debuggers depending on the declarations

## Risks and Test Signals

renumbering or changing struct layout breaks existing binaries; headers_install, libc build, ptrace,
signal, and syscall tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/kernel`

## Important APIs, Types, and Functions

Source read size: 29 lines, 687 bytes. Build selections: `obj-y -> head.o dma.o exceptions.o \`,
`obj-y -> cpu/`, `obj-y -> misc.o`, `obj-y -> entry.o`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/asm-offsets.c

## Purpose

generates assembler-visible offsets for MicroBlaze task, thread, pt_regs, CPU, and irq structures

## Important APIs, Types, and Functions

Source read size: 132 lines, 5299 bytes. Includes: `linux/init.h`, `linux/stddef.h`,
`linux/sched.h`, `linux/kernel_stat.h`, `linux/ptrace.h`, `linux/hardirq.h`, `linux/thread_info.h`,
`linux/kbuild.h`, `asm/cpuinfo.h`. Defined functions: `Copyright`. Declared functions: `DEFINE`. Key
macros/defines: `COMPILE_OFFSETS`.

## Control Flow and Behavior

main() emits DEFINE/OFFSET values through linux/kbuild.h so entry.S, exception handlers, and context
switch assembly can address C structures correctly

## State and Persistence

there is no runtime state; persistent output is generated asm-offsets.h in the build tree

## Dependencies and Integration Points

integrates with Kbuild generated headers, low-level entry/exception/context-switch assembly, and CPU
info structures

## Risks and Test Signals

layout drift causes subtle register save/restore corruption; the generated offsets build step, boot,
syscall, interrupt, and signal tests are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/Makefile -->
# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/kernel/cpu`

## Important APIs, Types, and Functions

Source read size: 13 lines, 311 bytes. Build selections: `ccflags-y -> -DCPU_MAJOR=$(CPU_MAJOR)
-DCPU_MINOR=$(CPU_MINOR) \`, `obj-y -> cache.o cpuinfo.o cpuinfo-pvr-full.o cpuinfo-static.o mb.o
pvr.o`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/Makefile -->
