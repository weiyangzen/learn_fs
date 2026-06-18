# Research Report: subset-b-000759

Grouped research for PA-RISC kernel cache/TLB assembly, PCI/DMA glue, firmware status paths, PDT memory-error handling, and legacy performance-counter support. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pacache.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/pacache.S

Purpose: implements the low-level PA-RISC cache, TLB, page clear/copy, temporary-alias, and space-register-hashing routines used by the architecture memory-management layer. It is hot-path assembly with separate 32-bit and 64-bit loops, PA 1.x/2.0 alternatives, and QEMU-specific TLB behavior.

Important entry points are `flush_tlb_all_local`, `flush_instruction_cache_local`, `flush_data_cache_local`, `clear_page_asm`, `copy_page_asm`, `copy_user_page_asm`, `clear_user_page_asm`, page/range flush and purge routines for data and instruction caches, `flush_kernel_icache_page`, and `disable_sr_hashing_asm`. These routines depend on `cache_info`, `dcache_stride`, `icache_stride`, `TMPALIAS_MAP_START`, PA-RISC space registers, PSW bits, and alternative patching conditions such as no split TLB/cache and running under QEMU.

Control flow is almost entirely hardware sequencing: disable interrupts or switch to real mode where needed, walk cache/TLB geometry using base/stride/count/loop fields, issue `pitlbe`, `pdtlbe`, `fdce`, `fice`, `fdc`, `pdc`, or `fic`, then synchronize and restore state. User-page helpers create temporary local aliases by deriving virtual addresses from physical page numbers and relying on DTLB miss handlers to install translations. `disable_sr_hashing_asm` selects diagnostic-register sequences for PCXS, PCXL, and PA2.0 CPUs.

State and persistence are CPU-local: TLB contents, cache lines, diagnostic bits, temporary translations, and PSW/space-register state. Integration points include cacheflush/tlbflush C wrappers, page allocator helpers, module exports in `parisc_ksyms.c`, runtime text patching in `patch.c`, and DMA sync paths in `pci-dma.c`.

Risks include extremely timing- and register-sensitive real-mode transitions, stale aliases if purge/flush ordering changes, architecture-specific diagnostic words, and assumptions about maximum alias boundary and PA-RISC miss handlers. Test signals are boot stability on PA-RISC hardware and QEMU, successful page clear/copy tests, module loading, instruction-cache coherency after text patching, DMA coherency, and absence of TLB/cache corruption under SMP and strict RWX configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pacache.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/parisc_ksyms.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/parisc_ksyms.c

Purpose: declares PA-RISC architecture symbols that loadable modules need but that are implemented by compiler helpers, assembly routines, or low-level kernel code rather than ordinary exported C APIs.

Important exports include `memset`, atomic exchange and compare-exchange helpers (`__xchg8`, `__xchg32`, optional `__xchg64`, `__cmpxchg_u8/u16/u32/u64`), SMP `__atomic_hash`, user-memory `lclear_user`, 32-bit `$global$`, PA-RISC millicode arithmetic helpers such as `$$divI`, `$$divU`, `$$remI`, `$$remU`, `$$mulI`, specialized divide variants, libgcc 64-bit shift/multiply/compare helpers, 64-bit divide/mod helpers, `__canonicalize_funcptr_for_compare`, 32-bit `$$dyncall`, optional `_mcount`, and `clear_page_asm`/`copy_page_asm` from `pacache.S`.

Control flow is compile-time only: preprocessor guards expose symbols according to `CONFIG_SMP`, `CONFIG_64BIT`, and `CONFIG_FUNCTION_TRACER`. There is no runtime behavior beyond module loader symbol resolution.

State and persistence are in the kernel module symbol table. The file is an integration point between PA-RISC ABI requirements, GCC/libgcc emitted helper calls, hand-written assembly, ftrace, and external modules. It depends on declarations from `linux/atomic.h`, `linux/libgcc.h`, `linux/uaccess.h`, and architecture I/O headers to match actual definitions elsewhere.

Risks are mostly ABI and link-time risks: removing an export can break out-of-tree or modular in-tree drivers, mismatching a helper prototype can corrupt call ABI, and 32-bit special symbols with `$` names are unusual enough to be easy to mishandle in tooling. Test signals are successful PA-RISC `modpost`, module insertion, ftrace-enabled builds, 32-bit and 64-bit allmodconfig-style builds, and lack of unresolved-symbol failures for modules using atomic, page, arithmetic, or function-pointer helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/parisc_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/patch.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/patch.c

Purpose: provides PA-RISC runtime text patching for kernel and module code, including strict RWX environments where direct writes to text mappings are not allowed.

Important types and functions are `struct patch`, `patch_lock`, `patch_map`, `patch_unmap`, `__patch_text_multiple`, `__patch_text`, `patch_text_stop_machine`, `patch_text`, and `patch_text_multiple`. The public wrappers run through `stop_machine_cpuslocked`; the double-underscore variants perform the actual patching and are marked `__kprobes` so they can be used safely around probing infrastructure.

Control flow first flushes dcache and icache aliases for the target range and flushes the kernel TLB range. `patch_map` decides whether the target is module or core kernel text and whether strict module/kernel RWX requires a writable fixmap alias. It maps the backing page into `FIX_TEXT_POKE0`, acquires `patch_lock` with IRQ save, and returns the writable address. `__patch_text_multiple` copies 32-bit instructions, remapping if the sequence crosses a page boundary, then flushes the modified alias range and TLB before unmapping and releasing the lock.

State is transient: fixmap slot contents, IRQ flags, cache/TLB state, and patched text bytes. Persistent behavior is the modified instruction stream. Dependencies include `core_kernel_text`, `vmalloc_to_page`, `virt_to_page`, fixmap APIs, cache/TLB flush assembly from `pacache.S`, and generic `stop_machine`.

Risks include partial patching if callers pass lengths not divisible by four, stale instruction cache if flush order changes, page-boundary remap mistakes, deadlock if called outside the expected CPU-locking context, and strict RWX differences between modules and core text. Test signals include alternatives/livepatch/ftrace/kprobe text modifications, SMP stop-machine stress, strict kernel/module RWX builds, and execution of newly patched instructions without illegal-instruction or stale-code behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pci-dma.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/pci-dma.c

Purpose: implements dynamic DMA allocation and cache synchronization for PA-RISC 1.1 PCXL/PCXL2 systems that lack an I/O TLB or DMA address translation hardware. It creates uncached kernel aliases backed by ordinary pages so coherent DMA buffers can be handed to devices.

Important state includes `pcxl_dma_start`, `pcxl_res_map`, `pcxl_res_hint`, `pcxl_res_size`, `pcxl_used_bytes`, `pcxl_used_pages`, `pcxl_res_lock`, and optional `/proc/bus/gsc/pcxl_dma` reporting. Important functions are page-table builders `map_pte_uncached`, `map_pmd_uncached`, `map_uncached_pages`, teardown helpers `unmap_uncached_*`, bitmap allocators `pcxl_alloc_range` and `pcxl_free_range`, `pcxl_dma_init`, `arch_dma_alloc`, `arch_dma_free`, `arch_sync_dma_for_device`, and `arch_sync_dma_for_cpu`.

Control flow at init only activates if `pcxl_dma_start` is set. It sizes the resource bitmap from `PCXL_DMA_MAP_SIZE`, allocates and clears it, and creates procfs diagnostics. Allocation verifies CPU type, rounds to page order, reserves a virtual alias range in a bitmap under spinlock, allocates zeroed physical pages, flushes their kernel mapping, maps the alias with `PAGE_KERNEL_UNC`, and returns the uncached virtual address while the DMA handle remains the physical address. Free reverses the mapping and bitmap state. Sync-to-device flushes dirty cache lines; sync-from-device purges cache lines so CPU reads see device writes.

Dependencies include generic DMA direct/map-ops contracts, PA-RISC cache/TLB purge helpers, kernel page-table allocation, physical/virtual translation, procfs, and boot CPU type data. Integration points are device DMA APIs and drivers running on older GSC/PCI PA-RISC machines.

Risks include panic on resource exhaustion or requests over 32 pages, bitmap accounting bugs, missing allocation failure checks after `__get_free_pages`, stale cache lines causing DMA corruption, and PCXL-only behavior returning `NULL` for other CPUs so generic DMA must handle fallback. Test signals are DMA buffer allocation/free on PCXL hardware, procfs resource accounting, driver I/O correctness for all DMA directions, and stress tests for allocation exhaustion and cache coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pci-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pci.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/pci.c

Purpose: supplies PA-RISC PCI BIOS glue, legacy I/O port accessors, resource alignment, device enablement, bridge initialization, and HBA registration.

Important globals are `pci_port`, `pci_bios`, `pci_hba_count`, and `parisc_pci_hba`. The exported port functions are generated by `PCI_PORT_IN` and `PCI_PORT_OUT` into `inb/inw/inl` and `outb/outw/outl`; they route encoded PCI port addresses to the right host-bus adapter and optionally delegate bus 0 accesses to EISA helpers. Important PCI hooks are `pcibios_init`, `pcibios_fixup_bus`, `pcibios_set_master`, `pcibios_init_bridge`, `pcibios_align_resource`, `pcibios_enable_device`, and `pcibios_register_hba`.

Control flow starts at `subsys_initcall(pcibios_init)`, which delegates firmware/controller-specific setup through `pci_bios->init` and sets `pci_cache_line_size`. Bus scanning calls `pcibios_fixup_bus`; driver enable paths call `pcibios_enable_device` to enable resources, SERR, and parity. `pcibios_set_master` ensures cache-line size and latency timer are reasonable unless firmware or a driver already set latency. Bridge initialization sets secondary latency and bridge control bits for parity, SERR, and master-abort reporting. HBA registration assigns up to 32 HBA slots used by port I/O.

State is mostly boot-time persistent: HBA array entries, HBA numbers, global firmware operation tables, and PCI config-space settings. Dependencies include PA-RISC `asm/io.h`, `asm/superio.h`, EISA support, generic PCI core, and platform-specific `pci_bios_ops`/`pci_port_ops` providers.

Risks include out-of-range encoded port HBAs indexing `parisc_pci_hba`, global single-operation-table assumptions, firmware method absence, resource alignment constraints that differ from generic PCI expectations, and hardware error-reporting bits affecting marginal devices. Test signals are successful PCI enumeration, working port I/O and EISA coexistence, correct bridge config, driver `pci_enable_device()` behavior, and resource assignment logs on PA-RISC systems with multiple HBAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_chassis.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_chassis.c

Purpose: integrates PA-RISC firmware chassis-code reporting with boot, panic, reboot, warning, and optional LCD/LED status paths.

Important state and functions include boot parameter `pdcchassis=`, `pdc_chassis_enabled`, panic and reboot notifier blocks, `parisc_pdc_chassis_init`, `pdc_chassis_send_status`, optional `pdc_chassis_warn_show`, and `pdc_chassis_create_procfs`. The firmware-facing calls are `pdc_pat_chassis_send_log`, `pdc_chassis_disp`, and `pdc_chassis_warn`.

Control flow during boot registers panic and reboot notifiers when `CONFIG_PDC_CHASSIS` is enabled and the boot parameter has not disabled support. `pdc_chassis_send_status` maps generic direct messages such as boot start, boot complete, shutdown, panic, LPMC, and HPMC to either 64-bit PDC PAT message/state pairs or 32-bit legacy chassis display codes. After a successful status update it refreshes LCD text when LCD/LED support is enabled. With chassis warnings enabled, init probes firmware warning support and creates `/proc/chassis`; reads decode component, battery, and temperature warning bits.

State persists mostly in firmware-visible chassis logs, front-panel display/LED state, registered notifier chains, and procfs. Dependencies include PDC/PDC_PAT firmware APIs, panic and reboot notifier infrastructure, processor/PAT detection, procfs seq files, and LCD/LED integration.

Risks include firmware support variability, returning `-1` for unsupported messages or platform mode, making firmware calls in panic context, config-dependent behavior divergence between 32-bit and 64-bit kernels, and warning-bit interpretation across machine families. Test signals are boot logs enabling chassis support, visible front-panel state changes for boot and shutdown, panic/reboot notifier invocation, `/proc/chassis` contents on supported systems, and graceful "not supported" behavior on machines without the firmware option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_chassis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_cons.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_cons.c

Purpose: provides early console output through PA-RISC PDC/IODC firmware before a normal console driver is available, with optional KGDB polling input.

Important functions and state are `pdc_console_write`, optional `kgdb_pdc_read_char`, `kgdb_pdc_write_char`, `kgdb_pdc_io_ops`, `pdc_earlycon_setup`, and `EARLYCON_DECLARE(pdc, ...)`. It uses `PAGE0->mem_cons` and `PAGE0->mem_kbd` firmware console descriptors and the PDC helpers `pdc_iodc_print` and `pdc_iodc_getc`.

Control flow is simple but early-boot sensitive. Earlycon setup checks whether the firmware console is duplex; if so, it copies console output parameters into the keyboard/input descriptor so reads and writes use the same device. It installs `pdc_console_write` as the console write callback and marks the port as big-endian memory-mapped I/O. When KGDB is configured it registers `kgdb_pdc` read/write operations. Writes loop until `pdc_iodc_print` reports the full byte count has been emitted.

State is firmware console descriptor data in page zero, the early console object, optional KGDB I/O registration, and no persistent kernel buffers. Dependencies are early console infrastructure, serial core constants, KGDB, page-zero firmware data, and PDC IODC routines.

Risks include infinite write looping if firmware reports no progress, reliance on firmware calls before full kernel services exist, duplex descriptor assumptions, no-op KGDB writes because normal console already echoes output, and very slow firmware I/O changing boot timing. Test signals are early boot messages with `earlycon=pdc`, KGDB character polling on supported firmware, no crash before console handoff, and correct output on both serial and graphics/firmware console configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_cons.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pdt.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/pdt.c

Purpose: reads and monitors the PA-RISC firmware Page Deallocation Table, which records physical pages with correctable or uncorrectable memory errors, and prevents or reacts to use of those pages.

Important state includes `pdt_type`, `pdt_poll_interval`, `pdt_status`, and page-aligned `pdt_entry`. Important functions are `arch_report_meminfo`, `get_info_pat_new`, `get_info_pat_cell`, `report_mem_err`, `pdc_pdt_init`, `pdt_mainloop`, and `pdt_initcall`. Access modes cover no support, legacy PDC, newer PAT all-cell reporting, and older PAT cell-local reporting.

Control flow during early init probes PAT-new, PAT-cell, then legacy PDC interfaces. On success it logs table metadata, reads existing entries, reports DIMM location when available, warns if bad memory intersects the kernel image or initrd, reserves each bad page through `memblock_reserve`, and increments poisoned-page accounting. A late initcall starts `kpdtd`, which sleeps for five minutes normally or one minute after errors, polls firmware for new entries, reads only the required entries where possible, reports them, and invokes `memory_failure` for permanent or multi-bit errors or `soft_offline_page` for transient single-bit errors when memory-failure support is built.

State persists in firmware PDT contents, kernel status mirrors, memblock reservations, poisoned-page counters, and the kthread. Dependencies include PDC/PAT memory calls, `parisc_cell_num`, `memblock`, initrd bounds, memory-failure APIs, procfs `/proc/meminfo` reporting, and PA-RISC physical-address encoding.

Risks include PDT entry format differences between PAT and non-PAT systems, truncating to one page of entries, bad memory inside kernel/initrd areas where mitigation is limited, kthread failure on unexpected firmware errors, and ignored runtime errors without `CONFIG_MEMORY_FAILURE`. Test signals include boot logs with PDT type and entries, `/proc/meminfo` PDT counters, reserved bad pages in early memory maps, runtime memory-offline events, and firmware error injection or hardware logs matching kernel reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/pdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/perf.c

Purpose: implements the legacy PA-RISC `/dev/perf` misc driver for PCX-U and PCX-W family CPU performance counters. It selects internal counter images, writes RDR and Runway diagnostic registers directly, starts/stops counters, and returns four counter values through ioctl.

Important state includes `perf_processor_interface`, `perf_enabled`, `perf_lock`, `cpu_device`, RDR-number lists for W and U chips, RDR description tables, write-control bitmask arrays, and image arrays from `perf_images.h`. Important file operations and helpers are `perf_open`, `perf_release`, `perf_read`, `perf_write`, `perf_ioctl`, `perf_config`, `perf_start_counters`, `perf_stop_counters`, `perf_rdr_get_entry`, `perf_rdr_read_ubuf`, `perf_rdr_clear`, `perf_write_image`, and `perf_rdr_write`. Assembly integration is through `perf_rdr_shift_in/out_U/W` and `perf_intrigue_enable/disable_perf_counters`.

Control flow at device init identifies supported CPU types, chooses ONYX or CUDA interface and Piranha bitmasks where needed, registers a misc device named by `PA_PERF_DEV`, patches images if that disabled block is ever restored, and binds to CPU 0's PA-RISC device. Open enforces single active owner. A write requires `perfmon_capable`, accepts one 32-bit image selector containing interface and test id, validates it, stops counters, writes the selected internal image, and restarts counters. `PA_PERF_OFF` stops counters, decodes RDR counter/sticky bits differently for ONYX and CUDA, clears them, and copies four 32-bit results to user space.

State persists in CPU performance hardware, selected image programming, misc-device registration, and single-open flag. Dependencies include CPU type detection, capability checks, user-copy helpers, Runway MMIO, `perf_images.h`, and the highly specific assembly routines in `perf_asm.S`.

Risks include direct diagnostic-register programming that can hang CPUs if images or ordering are wrong, SMP limitation to CPU 0, no `iounmap` after `ioremap`, debug `printk` noise in hot operations, fragile counter bit extraction, and single-open state that resets on close without stopping counters. Test signals are misc-device registration on supported CPUs, `PA_PERF_VERSION`, successful image selection writes, stable counter deltas from `PA_PERF_ON/OFF`, permission denial without perfmon capability, and no machine checks while programming RDR/Runway registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_asm.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_asm.S

Purpose: provides the low-level PA-RISC assembly primitives used by `perf.c` to enable/disable performance counters and shift data into or out of remote diagnose registers on PCX-U and PCX-W style CPUs.

Important entry points are `perf_intrigue_enable_perf_counters`, `perf_intrigue_disable_perf_counters`, `perf_rdr_shift_in_W`, `perf_rdr_shift_out_W`, `perf_rdr_shift_in_U`, and `perf_rdr_shift_out_U`. Macros encode privileged diagnostic instructions: `MTDIAG_1`, `MTDIAG_2`, `MFDIAG_1`, `MFDIAG_2`, `STDIAG`, `SFDIAG`, plus the `DR2_SLOW_RET` bit required by errata/ERS before shifting remote diagnose registers.

Control flow for counter enable/disable temporarily sets the performance-coprocessor bit in `ccr`, issues `pmenb` or `pmdis`, synchronizes, then restores the coprocessor bit with required nops. RDR shift routines set `DR2_SLOW_RET`, branch through a table of fixed eight-instruction sequences based on RDR number, use `SFDIAG`/`MFDIAG` to read through staging register 28 or `MTDIAG`/`STDIAG` to write through staging register 25, and restore DR2 on return. Several short RDRs are shifted back after reads to preserve machine state; unsupported holes branch directly to the return path.

State is entirely CPU diagnostic register and performance-counter hardware state. It depends on the PA-RISC calling convention, privileged diagnostic opcodes encoded as words, cacheline-aligned sequence layout, and `perf.c` passing valid RDR numbers and widths from its tables.

Risks are high because these routines run privileged CPU-specific sequences with exact instruction ordering, branch-table sizing, and staging-register side effects. Wrong widths or RDR tables can leave diagnostic registers shifted, and unsupported CPUs can fault or hang. Test signals are limited to supported PA-RISC hardware: enabling/disabling counters, reading and writing all RDRs used by the image lists, repeated `PA_PERF_ON/OFF`, and absence of machine checks or corrupted PDC/diagnostic state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_event.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_event.c

Purpose: implements PA-RISC kernel callchain collection for the generic Linux perf event subsystem.

The single exported behavior is `perf_callchain_kernel(struct perf_callchain_entry_ctx *entry, struct pt_regs *regs)`. It uses `struct unwind_frame_info`, `unwind_frame_init_task`, `unwind_once`, `__kernel_text_address`, and `perf_callchain_store`.

Control flow initializes an unwind cursor for `current` and repeatedly unwinds one frame. The loop exits when unwinding fails or returns a zero instruction pointer. For each frame it first verifies that the instruction pointer is a kernel text address, then stores it into the perf callchain buffer. If the address is not kernel text or the perf buffer refuses another entry, the function returns immediately. The `regs` argument is not used; this implementation starts from the current task unwind state rather than explicitly seeding from the sampled register frame.

State is transient and per-sample: unwind cursor contents and entries appended to the perf callchain context. Dependencies are the PA-RISC unwinder, generic perf callchain storage, current task context, and kernel text address validation.

Risks include callchains beginning from the wrong point if ignoring `regs` is inappropriate for interrupt/NMI sampling contexts, truncated stacks when unwinder metadata is missing, early termination on non-kernel text addresses, and architecture unwinder bugs surfacing as missing perf samples. Test signals are `perf record -g` kernel callchains on PA-RISC, unwinder self-tests if available, verifying no user-space addresses appear in kernel callchains, and sane stack traces under interrupt and syscall sampling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_images.h -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_images.h

Purpose: stores the internal performance-counter programming images used by the legacy PA-RISC `/dev/perf` driver, replacing user-supplied raw images with kernel-owned constants to reduce the chance of programming invalid CPU diagnostic state.

Important definitions are `PCXU_IMAGE_SIZE`, `PCXW_IMAGE_SIZE`, the `onyx_images` and `cuda_images` two-dimensional `uint32_t` arrays, and image-count macros such as `MAX_ONYX_IMAGES` and `MAX_CUDA_IMAGES`. The images correspond to named event sets documented in comments, including CPI, bus utilization, TLB miss variants, branch prediction/taken/not-taken behavior, instruction/data misses, local stalls, Runway transactions, shared-library CPI, floating-point instructions, cache miss reporting, branch reports, call-return stack behavior, and icache reporting. The arrays are marked `__ro_after_init`.

Control flow is data-driven through `perf.c`: user space writes a 32-bit selector with interface and image id; `perf_write` validates the id against these arrays and calls `perf_config`; `perf_write_image` then streams the selected image across RDRs and Runway debug/status registers using RDR tables and write-control bitmasks. The disabled `perf_patch_images` block in `perf.c` documents that some TLB-oriented images were intended to receive IVA/miss-handler addresses if image formats changed.

State persists as read-only kernel data after init and as hardware programming once copied into CPU registers. Dependencies include exact PCX-U/Onyx and PCX-W/Cuda image formats, RDR widths/order in `perf.c`, and Runway register programming conventions.

Risks are dominated by opaque magic constants from HP-UX-era tooling: any edit can silently program the wrong diagnostic paths or hang the CPU. Array dimensions must match the driver-selected image sizes, comments must stay aligned with image ordering, and `__ro_after_init` prevents later mutation except for currently disabled patching. Test signals are compile-time array sizing, successful selection of every image id on matching hardware, plausible counter semantics for each image, and no CPU faults when images are repeatedly downloaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/perf_images.h -->
