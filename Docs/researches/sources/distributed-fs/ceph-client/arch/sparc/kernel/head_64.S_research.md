# sources/distributed-fs/ceph-client/arch/sparc/kernel/head_64.S

## Purpose
`head_64.S` is the sparc64 boot entry and assembly aggregation point. It maps the kernel at `KERNBASE`, detects sun4u/sun4v CPU families, applies CPU-specific patching, initializes trap/TSB layout, and includes the core sparc64 low-level assembly files.

## Important APIs, Types, and Functions
Global entry labels are `_start`, `start`, `_stext`, `stext`, `setup_trap_table`, and `setup_tba`. Global state includes boot header fields, PROM strings and caches, `prom_root_node`, `is_sun4v`, `sun4v_chip_type`, `prom_tba`, `tlb_type`, `swapper_tsb`, and `swapper_4m_tsb`.

## Control Flow and State
Boot clears address masking, uses PROM CIF calls to find root/chosen nodes, gets the MMU ihandle, translates the current PC mapping, maps the full kernel at `KERNBASE`, detects sun4v and CPU compatible strings, configures Cheetah/Spitfire/Niagara/M7-specific registers, selects and records `tlb_type`, runs copy/clear/page/cache/TLB patchers, initializes stack/current/per-cpu base, clears BSS, calls `prom_init()`, then `start_early_boot()`. `setup_trap_table()` asks firmware to install Linux's trap table, configures sun4v fault-info scratchpad, sets kernel primary context, disables PROM tick/STICK interrupts, initializes IRQ work state, and restores interrupt state.

## Persistence and Dependencies
Persistent state includes PROM metadata, physical boot mapping records, chip type, TLB type, TSB memory, trap table address, and boot header fields. The file includes `etrap_64.S`, `rtrap_64.S`, `fpu_traps.S`, `ivec.S`, `hvcalls.S`, TLB miss code, syscall tables, and CPU error handlers.

## Integration Points, Risks, and Test Signals
Integration spans bootloaders, OpenPROM, hypervisor, trap table, TSB/TLB code, IRQ init, CPU-specific optimized routines, and early C boot. Risks include PROM call-frame mistakes, KERNBASE mapping size/alignment errors, chip misclassification, wrong patch selection, and trap table placement constraints. Test signals are successful boot on sun4u/sun4v variants, correct `tlb_type`/chip logs, working trap-table handoff, stable TLB refill behavior, and no PROM timer interrupts after setup.
