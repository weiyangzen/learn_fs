# Research: subset-b-000626

Grouped research for Alpha architecture kernel files in the Ceph-client source snapshot. Each section preserves the source path and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_titan.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/core_titan.c

**Purpose:** Implements TITAN core-logic support for Alpha systems: PCI configuration access, PCI hose setup, DMA/IOMMU window programming, TLB invalidation, reboot-time restoration of firmware PCI windows, I/O address mapping, machine-vector exported map helpers, and TITAN AGP support. It is selected through TITAN system machine vectors and is a major integration point between Alpha platform setup, Linux PCI, Alpha I/O primitives, and the AGP backend.

**Important APIs/types/functions:** Public or cross-file entry points include `titan_pci_ops`, `titan_pci_tbi()`, `titan_init_arch()`, `titan_kill_arch()`, `titan_ioportmap()`, `titan_ioremap()`, `titan_iounmap()`, `titan_is_mmio()`, `titan_agp_ops`, and `titan_agp_info()`. Important local helpers are `mk_conf_addr()`, `titan_read_config()`, `titan_write_config()`, `titan_init_one_pachip_port()`, `titan_init_pachips()`, `titan_query_agp()`, and the AGP aperture setup/bind/unbind/translate helpers. State includes `saved_config[4]` for firmware PCI window restore and `titan_pchip1_present` for multi-PChip detection.

**Control flow:** `titan_init_arch()` sets `boot_cpuid`, expands global I/O and memory resources, sets the 1 GiB direct DMA map at 2 GiB, initializes each discovered PA chip port as a PCI controller, and discovers the VGA hose. Each port gets resource objects, dense user mapping bases, config-space base, ISA and PCI scatter-gather arenas, direct-map window registers, monster-window enablement, optional AGP last-write initialization, and a PCI TLB flush. PCI config reads/writes compute a type-1-style config address from bus/devfn/register and use Alpha byte/word helpers plus barriers. `titan_ioremap()` chooses between direct-mapped TITAN memory, scatter-gather remapping through arena PTEs and vmalloc, VGA legacy mapping, or failure. AGP setup reserves an aperture inside the PCI SG arena and later binds AGP pages through the Alpha IOMMU.

**State and persistence behavior:** The file mutates hardware CSRs, global PCI controller lists, resource trees, direct DMA mapping globals, IOMMU arena state, and `alpha_agp_info` aperture metadata. It preserves firmware window state in `saved_config[]` and restores it in `titan_kill_arch()` so SRM can see expected PCI translations after reboot. No filesystem persistence is used.

**Dependencies and integration points:** Depends on `<asm/core_titan.h>` register layouts and address macros, Alpha PCI/IOMMU helpers from `pci_impl.h`, `memblock`, `vmalloc`, VGA hose discovery, and AGP backend types. Machine vectors use these functions through `machvec_impl.h` macros and system files such as `sys_titan.c`.

**Risks:** High-risk areas are hardware register ordering, `saved_config[]` ordering versus hose indexes, DMA window overlap, SG PTE validity checks, vmalloc cleanup in `titan_iounmap()`, assumptions about PChip presence, and AGP aperture reservation failures. The config path comments say concurrent config access is not safe; a future caller introducing parallel config cycles could expose this. `titan_is_mmio()` relies on address-bit conventions that must match map helpers.

**Test signals:** Boot a TITAN/Privateer kernel or emulator-equivalent far enough to enumerate all hoses, run PCI config read/write probes, DMA through ISA and PCI SG windows, exercise `ioremap()` for direct, SG, and VGA-like ranges, unload/use AGP if enabled, and reboot through SRM to verify PCI windows were restored. Kernel build coverage should include `CONFIG_ALPHA_TITAN`, `CONFIG_ALPHA_GENERIC`, AGP, VGA hose, and module symbol export variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_titan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_tsunami.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/core_tsunami.c

**Purpose:** Provides common TSUNAMI/TYPHOON core-logic services for Alpha machines: PCI config access, PChip discovery, hose/resource/IOMMU setup, direct and SG DMA window programming, simple I/O mapping, reboot restore of SRM PChip windows, and basic machine-check clearing. It is the core backend for DP264/ES40-class machine vectors.

**Important APIs/types/functions:** Exposes `tsunami_pci_ops`, `tsunami_pci_tbi()`, `tsunami_ioportmap()`, `tsunami_ioremap()`, `tsunami_init_arch()`, `tsunami_kill_arch()`, and `tsunami_machine_check()`. Local helpers include `mk_conf_addr()`, `tsunami_read_config()`, `tsunami_write_config()`, `tsunami_init_one_pchip()`, `tsunami_probe_read()`/`tsunami_probe_write()` when NXM probing is configured, `tsunami_kill_one_pchip()`, and the PCI error clear helpers. `saved_config[2]` records SRM PChip windows.

**Control flow:** Machine-vector initialization enters `tsunami_init_arch()`, optionally installs interrupt entry handling for NXM probe machine checks, expands `ioport_resource.end`, initializes PChip 0 and conditionally PChip 1 based on CChip CSC bit 14, then locates the VGA hose. Each PChip initialization probes for existence, allocates a `pci_controller`, registers I/O and MEM resources, saves SRM windows, creates an 8 MiB ISA SG arena and a size-for-memory PCI SG arena, configures window 0 as ISA SG, window 1 as PCI SG, window 2 as a 2 GiB direct map at 2 GiB, disables window 3, enables the monster window, and flushes the PCI TLB. Config access mirrors TITAN by composing a config-space address and doing byte/word/dword reads or writes with barriers.

**State and persistence behavior:** Runtime state consists of PChip CSRs, Linux resource trees, PCI controller list entries, direct DMA map globals, IOMMU arenas, and `saved_config[]`. `tsunami_kill_arch()` restores SRM window programming for every present PChip during reboot. Machine-check handling clears PChip `perror` state and releases the PAL logout frame; it does not persist data.

**Dependencies and integration points:** Depends on `<asm/core_tsunami.h>`, `pci_impl.h`, Alpha memory-barrier and machine-check state helpers, VGA fixups, and system vector files such as `sys_dp264.c`. PCI scanning later consumes the controllers through `common_init_pci()` in `pci.c`.

**Risks:** Register ordering is fragile; the source explicitly notes “magic” back-to-back memory barriers. Window sizing depends on `size_for_memory()`, and old Acer/ES40 devices require specific `align_entry` behavior. NXM probe code is configuration-dependent and must not leave expected machine-check flags set. The file assumes simple dense mapping and lacks TITAN-style SG `ioremap()` fallback.

**Test signals:** Build with `CONFIG_ALPHA_TSUNAMI` and relevant DP264/ES40 system vectors; boot on TSUNAMI/TYPHOON hardware or a faithful simulator; check two-PChip and one-PChip variants, PCI bus enumeration, DMA over ISA/PCI windows, SRM reboot path, and machine-check logging/clearing on injected PCI errors. Regression tests should watch for hangs around config-space writes and PChip error clear paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_tsunami.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_wildfire.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/core_wildfire.c

**Purpose:** Implements Wildfire platform core-logic discovery and PCI support. Wildfire systems are multi-QBB machines, so this file probes hardware topology, builds QBB/PCA/hose masks and maps, initializes PCI controllers per detected hose, programs DMA windows, handles PCI config cycles, flushes PCI TLBs, and provides the Wildfire machine-check handoff.

**Important APIs/types/functions:** Exported or machine-vector functions include `wildfire_init_arch()`, `wildfire_machine_check()`, `wildfire_kill_arch()`, `wildfire_pci_tbi()`, and `wildfire_pci_ops`. Global topology state includes `wildfire_hard_qbb_map[]`, `wildfire_soft_qbb_map[]`, `wildfire_hard_qbb_mask`, `wildfire_soft_qbb_mask`, `wildfire_gp_mask`, `wildfire_hs_mask`, `wildfire_iop_mask`, `wildfire_ior_mask`, `wildfire_pca_mask`, `wildfire_cpu_mask`, and `wildfire_mem_mask`. Key helpers are `wildfire_hardware_probe()`, `wildfire_init_qbb()`, `wildfire_init_pca()`, `wildfire_init_hose()`, `mk_conf_addr()`, `wildfire_read_config()`, and `wildfire_write_config()`.

**Control flow:** `wildfire_init_arch()` expands the global I/O range, probes hardware through fast QSD/QSA/GP/IOP/NE/FE registers, initializes all discovered QBBs, and sets a direct PCI DMA map from 1 GiB to 3 GiB. The probe establishes hard-to-soft QBB mappings, detects HS/GP presence, CPU/memory populations, IOP/IOR masks, and PCA existence by checking IOP hose init and NE/FE identity registers. For each existing PCA, both hoses are initialized with `pci_controller` resources, two direct DMA windows, an ISA SG window at 8 MiB, and a 128 MiB PCI SG window at 3 GiB. TLB invalidation is a read from `pci_flush_tlb`.

**State and persistence behavior:** The file owns in-memory hardware topology masks/maps and mutates Wildfire PCI window CSRs and Linux PCI/resource state. It does not save/restore SRM state like TITAN/TSUNAMI and `wildfire_kill_arch()` is empty. Debug configuration printing is enabled by `DEBUG_DUMP_CONFIG`, so boot may emit probed topology.

**Dependencies and integration points:** Depends on `<asm/core_wildfire.h>` register structures and existence macros, Alpha PCI/IOMMU helpers, system vector setup in `sys_wildfire.c`, and generic PCI scanning in `pci.c`. IRQ and machine-check routing are largely elsewhere, but this file calls `process_mcheck_info()` after minimal synchronization.

**Risks:** Topology discovery is hardware-specific and uses magic identity masks; bad decoding can skip hoses or expose nonexistent ones. Window 3 has a FIXME about scaling, and no reboot restore exists. Machine-check handling contains a FIXME for clearing PCI errors. Config access inherits the non-concurrent assumptions from similar Alpha core logic files.

**Test signals:** Wildfire boot logs should show correct hard/soft QBB maps, resource masks, and PCI hose count. Validate PCI enumeration across all detected hoses, DMA through direct and SG windows, correct `pci_controller->index` encoding `(qbb << 3) + hose`, and graceful behavior on absent PCAs/QBBs. Injected PCI errors should demonstrate current reporting limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/core_wildfire.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/entry.S

**Purpose:** Defines Alpha kernel exception, interrupt, syscall, context-switch, fork, signal-return, FPU save/restore, and special syscall assembly entry points. It is the ABI-critical bridge between PALcode frames, Linux `pt_regs`, scheduler/work-pending logic, tracing/seccomp/audit, and C handlers.

**Important APIs/types/functions:** Main symbols include `entInt`, `entArith`, `entMM`, `entIF`, `entUna`, `entDbg`, `entSys`, `ret_from_sys_call`, `work_pending`, `do_switch_stack`, `undo_switch_stack`, `__save_fpu`, `alpha_switch_to`, `ret_from_fork`, `ret_from_kernel_thread`, `alpha_fork`, `alpha_vfork`, `alpha_clone`, `alpha_clone3`, `sys_sigreturn`, `sys_rt_sigreturn`, and `alpha_syscall_zero`. Critical macros are `SAVE_ALL`, `RESTORE_ALL`, `DO_SWITCH_STACK`, `UNDO_SWITCH_STACK`, CFI frame helpers, and `SYSCALL_SKIP_RETURN_RESTART_GATE`.

**Control flow:** PALcode vectors branch to entry labels, which save registers into the Alpha `pt_regs` layout, set up `current` by masking the stack pointer, and call C handlers such as `do_entInt`, `do_page_fault`, `do_entIF`, or `do_entUnaUser`. `entSys` saves the syscall number in both a mutable shadow (`regs->r1`) and restart copy (`regs->r2`), checks syscall trace/audit/seccomp flags, dispatches through `sys_call_table`, and stores Alpha ABI return state in `r0` plus `a3` (`r19`) error flag. The traced path calls `syscall_trace_enter`/`leave`, handles `nr == -1` skip-dispatch, and uses `SYSCALL_SKIP_RETURN_RESTART_GATE` to prevent invalid `-1` success and restrict syscall restart to `ERESTART*` codes. Return-to-user raises IPL while sampling work flags, calls `do_work_pending` for signals/notify, and restores FPU state when thread status requests it.

**State and persistence behavior:** Mutates kernel stack frames, thread-info flags/status, saved HAE cache/register, FP register slots, syscall shadow/original registers, and PAL context through `PAL_swpctx`/`PAL_rti`. No persistent storage is involved; correctness is entirely runtime architectural state.

**Dependencies and integration points:** Depends on generated offsets, PAL constants, `alpha_mv`, `sys_call_table`, thread-info flags, C handlers in traps/irq/signal/ptrace/process code, and Alpha syscall ABI conventions. CFI directives integrate with unwinding/debugging.

**Risks:** Very high risk because register offsets, restart gating, `a3` error semantics, FPU lazy-save state, and IPL transitions are ABI and correctness critical. Recent seccomp/ptrace skip handling must avoid returning `r0 == -1, a3 == 0` and must not restart skipped successful syscalls. Stack layout changes require matching `asm-offsets`.

**Test signals:** Build and boot with syscall tracing, audit, seccomp, signal delivery, `fork`/`clone`/`clone3`, FPU-heavy context switches, unaligned-access traps, page faults, and interrupt returns. Targeted tests should cover syscall `-1` injection, `ERESTART*` restart paths, `force_successful_syscall_return()`, `sigreturn`, kernel threads, and debug unwinding through CFI frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_common.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_common.c

**Purpose:** Supplies shared Alpha machine-check and console data-log utilities: raw logout-frame dumping, timestamp printing, subpacket parsing, annotation, handler registration, and previous-boot console data-log draining from HWRPB per-CPU structures.

**Important APIs/types/functions:** Exposes `err_print_prefix`, `mchk_dump_mem()`, `mchk_dump_logout_frame()`, `el_print_timestamp()`, `el_process_subpackets()`, `el_process_subpacket()`, `el_annotate_subpacket()`, `cdl_check_console_data_log()`, `cdl_register_subpacket_annotation()`, and `cdl_register_subpacket_handler()`. Internal state is `subpacket_handler_list` and `subpacket_annotation_list`, both singly linked lists registered by EV7/TITAN/Marvel handlers.

**Control flow:** Machine-check handlers or boot-time console-log checks pass an `el_subpacket` to `el_process_subpacket()`. Header subpackets are decoded by class/type to determine event name, frame length, packet count, and timestamp, then child subpackets are iterated. Non-header packets are routed through the registered class handler list. Annotation lookup matches class/type/revision and prints per-word labels while dumping memory. `cdl_check_console_data_log()` walks HWRPB processor slots, processes any `console_data_log_pa` pointer through identity mapping, then clears the pointer so firmware can discard it on restart.

**State and persistence behavior:** The only durable-ish behavior is clearing `pcpu->console_data_log_pa` in HWRPB after logging previous-boot errors. Handler/annotation lists are initialized during boot and then read during error handling. `err_print_prefix` is temporarily changed by platform handlers to alter severity.

**Dependencies and integration points:** Uses `<asm/hwrpb.h>`, `<asm/err_common.h>`, machine-check frame structures, and registration declarations in `err_impl.h`. `err_ev7.c`, `err_titan.c`, and `err_marvel.c` plug into this registry.

**Risks:** Subpacket parsing trusts firmware-provided lengths and packet counts; corrupt logs can lead to confusing output or early aborts. Registration duplicate detection does not check the final existing list element before appending, so duplicate last entries are a subtle risk. Global `err_print_prefix` is not concurrency-safe across simultaneous machine checks.

**Test signals:** Validate by booting with synthetic or firmware-supplied console data logs, registering EV7/TITAN handlers, and checking that known header/subpacket classes are printed and unknown classes abort cleanly. Static review should verify every handler returns the next subpacket pointer correctly and annotations terminate with NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev6.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev6.c

**Purpose:** Decodes and reports EV6 processor machine-check logout frames. It identifies Ibox, Mbox/Dcache, and Cbox/cache/memory error syndromes, decides whether an error is known/reportable, dumps additional frame data for non-dismissed events, and releases the PAL logout frame.

**Important APIs/types/functions:** Exposes `ev6_register_error_handlers()`, `ev6_process_logout_frame()`, and `ev6_machine_check()`. Key parsers are `ev6_parse_ibox()`, `ev6_parse_mbox()`, and `ev6_parse_cbox()`. It consumes `struct el_common_EV6_mcheck` from `<asm/err_ev6.h>` and disposition constants from the common error headers.

**Control flow:** `ev6_machine_check()` synchronizes the processor with `mb()` and `draina()`, first parses the frame with `print == 0`, and suppresses output only if disposition is dismissible. Otherwise it raises `err_print_prefix` to critical, prints correctable/uncorrectable vector context, reprocesses with printing enabled, dumps registers through `dik_show_regs()`, restores the prefix, then calls `wrmces(0x7)` to release the frame. `ev6_process_logout_frame()` ORs parser dispositions and, when printing, emits extra core registers and dumps the whole logout frame unless the disposition is dismissible.

**State and persistence behavior:** No persistent state. It reads a PAL logout frame pointed to by `la_ptr`, temporarily changes `err_print_prefix`, and clears machine-check state with `wrmces`.

**Dependencies and integration points:** Called by generic Alpha interrupt handling through `alpha_mv.machine_check` or delegated from TITAN/Privateer for processor-frame cases. Depends on `err_common.c` dump helpers, `get_irq_regs()`, SMP CPU id, and EV6 frame field definitions.

**Risks:** Parser status is built with bitwise OR over disposition values, so disposition constant design must make combinations meaningful. Print decoding is gated by compile-time verbose options for some surrounding handlers, and unknown errors fall back to full dumps. Incorrect bit definitions would misclassify hardware errors or suppress important logs.

**Test signals:** Use known EV6 logout-frame samples for Icache parity, Dcache tag/ECC, and Cbox memory/Bcache errors. Verify correctable versus uncorrectable vectors, no output for intentionally dismissible cases if any are added, register dump presence on reportable errors, and `wrmces` release. Compile with and without verbose machine-check support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev7.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev7.c

**Purpose:** Implements EV7 PAL logout-frame subpacket collection, generic EV7 machine-check reporting, and registration of annotation/handler tables for EV7 processor, ZBOX, RBOX, and IO PAL subpackets.

**Important APIs/types/functions:** Exposes `ev7_collect_logout_frame_subpackets()`, `ev7_machine_check()`, `ev7_pal_subpacket_handler`, and `ev7_register_error_handlers()`. Local data includes annotation arrays for EV7 processor, ZBOX, RBOX, and IO subpacket fields. `ev7_process_pal_subpacket()` is the registered class handler for `EL_CLASS__PAL`.

**Control flow:** `ev7_collect_logout_frame_subpackets()` verifies the outer `EL_CLASS__HEADER/LOGOUT_FRAME`, steps to the PAL logout-frame subpacket, saves the logout data pointer, and iterates the declared PAL subpacket count. It stores typed pointers for processor, RBOX, ZBOX, IO, and environmental subpackets in `struct ev7_lf_subpackets`, returning NULL on unexpected class/type. `ev7_machine_check()` synchronizes, prints a CPU correctable/uncorrectable message, delegates packet printing to `el_process_subpacket()`, then releases the frame. `ev7_process_pal_subpacket()` handles nested PAL logout frames by printing LPID/RBOX/timestamp/exc address and recursively processing contained subpackets; other PAL packets are annotated generically.

**State and persistence behavior:** No persistent state beyond registering annotation and handler list entries in `err_common.c`. It reads PAL logout memory and clears PAL machine-check state with `wrmces`.

**Dependencies and integration points:** Provides the base EV7 parser used directly by `err_marvel.c` and by EV7-capable machine vectors. Depends on `<asm/err_ev7.h>` layout definitions, common subpacket registries, timestamp and annotation helpers, SMP CPU id, and PAL vector constants.

**Risks:** The collector assumes well-formed length fields and one expected PAL logout subpacket structure. Unknown PAL subpacket types cause collection failure even if some useful data was already found. Environmental array indexing depends on `ev7_lf_env_index()` matching the contiguous type range.

**Test signals:** Feed synthetic EV7 subpacket sequences with each recognized class/type, malformed outer headers, non-PAL nested packets, unknown PAL types, and all environmental subpacket types. Boot Marvel/EV7 configurations should show registered annotations and sane fallback annotation output for non-logout PAL subpackets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_ev7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_impl.h -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_impl.h

**Purpose:** Private implementation header for Alpha machine-check/error handlers. It defines subpacket annotation and handler registry types, bitfield helper macros, and cross-file prototypes connecting common, EV6, EV7, Marvel, TITAN, and Privateer error handling code.

**Important APIs/types/functions:** Defines `struct el_subpacket_annotation`, `SUBPACKET_ANNOTATION()`, `struct el_subpacket_handler`, `SUBPACKET_HANDLER_INIT()`, `EXTRACT()`, and `GEN_MASK()`. Declares shared functions such as `mchk_dump_mem()`, `mchk_dump_logout_frame()`, `el_process_subpacket()`, `cdl_register_subpacket_annotation()`, EV7 collector/handlers, EV6 processing, Marvel handlers, and TITAN/Privateer handlers.

**Control flow:** This header has no runtime control flow, but its types determine the registry flow in `err_common.c`: class handlers return the next `el_subpacket`, annotations provide per-word labels, and platform files register arrays during init. `EXTRACT()` and `GEN_MASK()` are used throughout platform decoders to convert raw CSR fields to display and validity masks.

**State and persistence behavior:** No storage is allocated here. It exposes the global `err_print_prefix` and registration interfaces that mutate state in `err_common.c`.

**Dependencies and integration points:** Includes `<asm/mce.h>` for machine-check structures and disposition constants. It is included by all researched `err_*.c` files and is intentionally private to `arch/alpha/kernel`.

**Risks:** Macro naming conventions require each field to provide `__S` and `__M` symbols; mismatches fail at compile time or decode the wrong bits if constants are wrong. Registry struct layouts are shared across files, so changes must be coordinated. Because prototypes are conditional only by compile selection elsewhere, stale declarations can hide missing object coverage until link.

**Test signals:** Compile all Alpha machine-check configurations using EV6, EV7/Marvel, TITAN, and Privateer paths. Static checks should confirm every registered handler matches the expected `struct el_subpacket *(*)(struct el_subpacket *)` signature and every annotation array is NULL-terminated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_marvel.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_marvel.c

**Purpose:** Provides Marvel EV7 system-event and system-error handling, especially IO7/PCI-X error discovery, decoding, acknowledgment, and reporting. It supplements generic EV7 PAL parsing with Marvel-specific environmental and IO ASIC interpretation and fallback collection when PAL did not supply the correct IO subpacket.

**Important APIs/types/functions:** Exposes `marvel_machine_check()` and `marvel_register_error_handlers()`. Key helpers include `marvel_process_680_frame()`, `marvel_process_logout_frame()`, `marvel_process_io_error()`, `marvel_find_io7_with_error()`, and verbose decoders for PO7 and POx error summary, uncorrectable/correctable symptoms, TLB errors, split completions, transaction summaries, and up-hose garbage symptoms.

**Control flow:** `marvel_machine_check()` synchronizes, selects a processor for system event, system uncorrectable, or system correctable vectors, collects EV7 logout subpackets, supplies a scratch IO subpacket if PAL omitted one, initializes the IO PID, evaluates the frame silently, then either dismisses, reports decoded details, or dumps annotated subpackets. `marvel_process_logout_frame()` handles RBOX IO-error indications and dismisses expected PCI-X bridge config-probe machine checks matching a specific EV7 C_STAT/C_ADDR pattern. `marvel_process_io_error()` verifies or finds the IO7 with a valid error. `marvel_find_io7_with_error()` walks `marvel_next_io7()`, snapshots IO7/port CSRs into the PAL IO subpacket, acknowledges port TLB/error summary registers, acknowledges PO7 errors, and updates `io_pid`.

**State and persistence behavior:** It mutates IO7 hardware error CSRs to clear/acknowledge errors, fills scratch or PAL-provided subpacket memory, and temporarily changes `err_print_prefix`. No persistent filesystem state exists. The handler releases PAL logout frames with `wrmces`.

**Dependencies and integration points:** Depends on EV7 subpacket collection from `err_ev7.c`, IO7 topology/CSR accessors from `<asm/core_marvel.h>`, common error registries, and system vectors for Marvel. Verbose decoding depends on `CONFIG_VERBOSE_MCHECK`.

**Risks:** Error handling occurs during machine-check context; walking IO7 topology and acknowledging CSRs must be carefully ordered. Some useful diagnostics are compiled out without verbose machine-check support. The fallback IO7 search overwrites an IO subpacket with `0x55` first, so consumers must not rely on untouched PAL contents after fallback. Dismissal of config-probe errors is intentionally narrow but could hide real errors if the signature overlaps.

**Test signals:** Exercise Marvel system event, system correctable, and system uncorrectable vectors; inject IO7 PO7 and per-port POx valid errors; verify correct IO7 discovery when PAL reports no or wrong IO subpacket; check CSR acknowledgment order; validate the PCI-X config-probe dismissal path; and compare verbose versus non-verbose build output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_marvel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_titan.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/err_titan.c

**Purpose:** Implements TITAN and Privateer machine-check decoding. It parses CChip non-existent-memory indications, PChip SERROR/PERROR/AGPERROR fields, converts some machine-check-reported interrupts back into normal interrupts, registers Regatta-family console-data-log annotations, and delegates EV6 processor frames where appropriate.

**Important APIs/types/functions:** Exposes `titan_process_logout_frame()`, `titan_machine_check()`, `titan_register_error_handlers()`, `privateer_process_logout_frame()`, and `privateer_machine_check()`. Important helpers are `titan_parse_c_misc()`, `titan_parse_p_serror()`, `titan_parse_p_perror()`, `titan_parse_p_agperror()`, `titan_parse_p_chip()`, `el_process_regatta_subpacket()`, and `privateer_process_680_frame()`.

**Control flow:** `titan_machine_check()` synchronizes, delegates non-system vectors to `ev6_machine_check()`, parses TITAN system logout data silently, reports unless the frame is dismissible, optionally prints verbose decoded details and registers, then derives a TITAN interrupt mask from `c_dirx` and dispatches pending interrupt-like machine checks through `titan_dispatch_irqs()`. PERROR parsing specifically marks legacy VGA/BIOS or low I/O master-abort patterns as dismissible to tolerate video BIOS probing. `titan_register_error_handlers()` registers Regatta/TITAN annotations and handler then calls `ev6_register_error_handlers()`. Privateer processing selects EV6, TITAN, environmental, or unknown handling based on machine-check code; Privateer system events always report then dispatch pending 680/hotplug-like interrupts.

**State and persistence behavior:** Reads PAL logout frames and TITAN system-data areas, temporarily changes `err_print_prefix`, may dispatch IRQs, and clears machine-check state with `wrmces`. Registration mutates the common subpacket registry. No persistent storage is used.

**Dependencies and integration points:** Depends on `<asm/core_titan.h>`, `<asm/err_ev6.h>`, common error utilities, IRQ register access, `titan_dispatch_irqs()` from TITAN system code, and EV6 processing. Used by TITAN/Privateer machine vectors and console data-log replay.

**Risks:** Dismissal heuristics around PCI master aborts must be precise. Verbose decode blocks mean some detail only exists with `CONFIG_VERBOSE_MCHECK`. Converting machine-check bits back into interrupts couples error handling with IRQ routing. The Regatta handler calls `privateer_process_logout_frame()` on embedded frame data, so frame layout assumptions are critical.

**Test signals:** Use TITAN logout-frame samples for CChip NXM, PChip ECC, PCI parity/abort, SG PTE, and AGP errors. Verify expected dismissals for VGA/BIOS probing, interrupt dispatch from `c_dirx`, Privateer environmental vector behavior, Regatta subpacket annotation output, and fallback to EV6 on processor machine checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/err_titan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/es1888.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/es1888.c

**Purpose:** Contains a tiny platform initialization sequence for an onboard ES1888 sound chip, which is Sound Blaster 16 compatible. It programs the audio controller base address, extended mode, IRQ, and DMA channel through legacy ISA I/O ports.

**Important APIs/types/functions:** Exposes `es1888_init()` as an `__init` function declared through `proto.h`. It uses `inb()`/`outb()` from Alpha I/O wrappers. No custom data structures are defined.

**Control flow:** Initialization performs a fixed series of reads from ports `0x229`, `0x22b`, and `0x220` to unlock or select the base address, then resets the DSP/control interface at `0x226`, waits for status bit 7 at `0x22e`, enables extended mode with command `0xc6`, writes interrupt control selector `0xb1` followed by IRQ value `0x14` for IRQ 5, writes DMA control selector `0xb2`, then sets DMA channel value `0x18`. Busy-wait loops poll command-port bit 7 before subsequent writes.

**State and persistence behavior:** Mutates only ES1888 hardware registers through ISA port I/O. There is no kernel state except whatever the device later exposes to sound drivers, and no persistent storage.

**Dependencies and integration points:** Called by platform setup code such as DP264 variants when onboard audio needs early enablement. Depends on legacy port access working and the surrounding platform providing the expected chip at the hard-coded ports.

**Risks:** Hard-coded port and IRQ/DMA settings can conflict with firmware, another ISA device, or a platform variant without ES1888. Busy loops have no timeout, so absent or wedged hardware can hang boot. There is no resource reservation or detection in this function.

**Test signals:** On supported hardware, confirm boot does not hang, chip base is `0x220`, IRQ 5 and DMA 1 are visible to later sound probing, and no ISA resource conflicts appear. On unsupported configurations, ensure callers gate the function by platform identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/es1888.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/gct.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/gct.c

**Purpose:** Implements recursive search over Alpha Generic Configuration Tree version 6 nodes. It validates node magic, compares node type/subtype against a caller-provided search table, invokes matching callouts, and traverses sibling and child links.

**Important APIs/types/functions:** Exposes `gct6_find_nodes(gct6_node *node, gct6_search_struct *search)`. It uses `gct6_node`, `gct6_search_struct`, `GCT_NODE_MAGIC`, and `GCT_NODE_PTR()` from `<asm/gct.h>`.

**Control flow:** The function first verifies `node->magic`; if invalid it logs an error and returns `-EINVAL`. It then walks the search array until a zero type/subtype sentinel, calling `wanted->callout(node)` for each matching type/subtype. It recurses to `node->next` first, then to `node->child`, ORing return statuses.

**State and persistence behavior:** No owned state. It reads firmware-provided GCT memory and calls external callbacks that may mutate platform setup state. The traversal result is an aggregate status, not a stored cursor.

**Dependencies and integration points:** Used by platform discovery code that parses HWRPB/GCT firmware tables. Depends on valid firmware offsets that `GCT_NODE_PTR()` can translate into kernel addresses.

**Risks:** Recursive traversal trusts firmware tree structure; cycles or corrupt offsets could recurse indefinitely or fault. ORing negative statuses can obscure exact error codes. Callouts have no return channel, so callback failures cannot be propagated unless they mutate external state.

**Test signals:** Feed small synthetic GCT trees with valid siblings/children, multiple matching entries, sentinel termination, invalid magic, and absent callouts. Firmware-boot validation should check expected platform nodes are discovered exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/gct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/head.S

**Purpose:** Provides the earliest Alpha kernel entry code after the bootloader has loaded the kernel and switched to OSF/1 PALcode. It sets up the global pointer, initial task/thread pointer, stack pointer, starts the C kernel, and defines small PAL console service helpers.

**Important APIs/types/functions:** Defines `_stext`, `__start`, optional `__smp_callin`, `cserve_ena`, `cserve_dis`, and `halt`. It uses PAL operations `PAL_halt`, `PAL_rduniq`, `PAL_swpctx`, and `PAL_cserve`.

**Control flow:** `__start` computes/loads the GP with `ldgp`, loads `init_thread_union` into `$8` as the initial current thread pointer, sets `$30` to the top of that 16 KiB stack minus `pt_regs`, calls `start_kernel`, and halts if it returns. With SMP, `__smp_callin` loads GP, reads the target PCBB from the PAL unique value, swaps context into the target idle task, derives `current` from the stack pointer, calls `smp_callin`, then halts. `cserve_ena` and `cserve_dis` invoke SRM PAL console service calls 52/53 for interrupt enable/disable.

**State and persistence behavior:** Initializes only CPU architectural registers and PAL context. It does not write persistent state. `halt` is a simple PAL halt hook useful for debugging.

**Dependencies and integration points:** Depends on linker placement of `__HEAD`, `init_thread_union`, generated `SIZEOF_PT_REGS`, PAL constants, and C entry points `start_kernel()`/`smp_callin()`. `irq_srm.c` uses `cserve_ena/dis`.

**Risks:** Stack and current setup must match thread size and `pt_regs` layout. SMP call-in assumes SRM loaded the correct HWPCB and unique value. Any relocation/GP issue here prevents boot before diagnostics are available.

**Test signals:** Boot an Alpha kernel from SRM or emulator and verify transition to `start_kernel`, SMP secondary call-in, SRM interrupt masking on PC164-like systems, and clean PAL halt on failure. Build-time tests should catch offset mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/io.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/io.c

**Purpose:** Provides out-of-line Alpha I/O accessors and exported I/O memory helpers. It wraps platform-specific `__IO_PREFIX` operations with required memory barriers, implements port I/O helpers, raw and ordered MMIO helpers, repeated string I/O, `memcpy_fromio()`, `memcpy_toio()`, I/O memset, VGA screen copy/move helpers, and `ioport_map()`.

**Important APIs/types/functions:** Exports `ioread8/16/32/64`, `iowrite8/16/32/64`, `inb/inw/inl`, `outb/outw/outl`, `__raw_read*`, `__raw_write*`, `read*`, `write*`, `read*_relaxed`, `ioread*_rep`, `iowrite*_rep`, `ins*`, `outs*`, `memcpy_fromio()`, `memcpy_toio()`, `_memset_c_io()`, `scr_memcpyw()`, `scr_memmovew()`, `ioport_map()`, and `ioport_unmap()`.

**Control flow:** All generic accessors delegate through `IO_CONCAT(__IO_PREFIX, ...)`, where compile/machine-vector setup supplies the backend. Ordered reads use barriers before and after; ordered writes use a leading barrier; relaxed reads still use a barrier to order against each other. Repeated I/O functions coalesce aligned byte/word transfers where possible and handle unaligned 32-bit buffers with packed temporary structs. Copy/memset functions widen transfers when source/destination I/O and memory addresses are co-aligned, then finish tails bytewise. VGA helpers choose raw I/O, `memcpy_fromio()`, `memcpy_toio()`, or normal `memcpy()` based on `__is_ioaddr()`.

**State and persistence behavior:** No persistent state. The functions mutate device-visible I/O memory/ports and enforce ordering through Alpha memory barriers. `ioport_unmap()` is a no-op because mapped port tokens are direct machine-vector translations.

**Dependencies and integration points:** Depends on `<asm/io.h>` inline backends and machine-vector-selected `__IO_PREFIX`. Drivers and subsystems use this exported ABI for all Alpha I/O, including PCI sysfs legacy reads/writes and ISA helper code.

**Risks:** Ordering is architecture-critical; removing barriers can break drivers. The `ioread64()` implementation stores into `unsigned int ret` before returning `u64`, which is a suspicious truncation risk if the backend returns true 64-bit values. Repeated access alignment assumptions and packed struct use must match Alpha unaligned-access behavior.

**Test signals:** Build drivers that use every exported width and repeated I/O path; run MMIO ordering tests, IDE/PIO transfer tests, framebuffer/VGA console operations, unaligned buffer tests, and module symbol resolution. Static analysis should flag the `ioread64()` local type mismatch for review.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq.c

**Purpose:** Contains Alpha generic IRQ accounting, affinity selection, `/proc/interrupts` architecture rows, bad-IRQ reporting, and the common `handle_irq()` bridge into the generic IRQ subsystem.

**Important APIs/types/functions:** Exposes `irq_err_count`, per-CPU `irq_pmi_count`, `ack_bad_irq()`, SMP-only `irq_select_affinity()`, `arch_show_interrupts()`, and `handle_irq()`. It consumes `irq_to_desc()`, `generic_handle_irq_desc()`, `irq_enter()`, and `irq_exit()`.

**Control flow:** Controller-specific device interrupt handlers call `handle_irq(irq)`. It validates the descriptor and range, rate-limits invalid IRQ messages by `MAX_ILLEGAL_IRQS`, enters IRQ context, invokes the generic descriptor handler, and exits IRQ context. `arch_show_interrupts()` prints IPI counts on SMP, performance monitoring interrupt counts, and error count. SMP affinity selection round-robins over possible CPUs allowed by `irq_default_affinity`, unless the chip lacks `irq_set_affinity` or user affinity was recorded.

**State and persistence behavior:** Maintains runtime counters and optional per-IRQ user-affinity flags. No persistent storage. Invalid IRQs increment `irq_err_count`.

**Dependencies and integration points:** Called by `irq_alpha.c` and controller files (`irq_i8259.c`, `irq_pyxis.c`, `irq_srm.c`, platform system files). Integrates with Linux generic IRQ descriptors and procfs interrupt display.

**Risks:** The invalid IRQ condition combines descriptor/range checks in a way that only logs up to a cap; out-of-range values after the cap silently return. Affinity code assumes valid IRQ index for `irq_user_affinity[]`. `generic_handle_irq_desc()` expects the descriptor to be initialized by platform init.

**Test signals:** Trigger valid and invalid IRQs, inspect `/proc/interrupts`, verify `irq_err_count`, exercise SMP affinity-capable chips, and confirm nested IRQ enter/exit accounting under device interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_alpha.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_alpha.c

**Purpose:** Implements the Alpha PAL interrupt entry C dispatcher and machine-check support glue. It routes interrupt types to IPI, RTC, machine-check, device, and performance handlers, initializes architecture IRQ handling, resets ISA DMA, reports generic machine-check info, and installs the RTC IRQ.

**Important APIs/types/functions:** Exposes optional `__min_ipl`, `perf_irq`, `do_entInt()`, `common_init_isa_dma()`, `init_IRQ()`, `process_mcheck_info()`, and `init_rtc_irq()`. It uses `alpha_mv.machine_check`, `alpha_mv.device_interrupt`, and `alpha_mv.init_irq` from the machine vector.

**Control flow:** Assembly `entInt` calls `do_entInt(type, vector, la_ptr, regs)`. The dispatcher disables local interrupts, switches on PAL interrupt type, and calls `handle_ipi()`, `handle_irq(RTC_IRQ)`, `alpha_mv.machine_check()`, `alpha_mv.device_interrupt()`, or `perf_irq()`, with `set_irq_regs()` around handlers that need current register context. `init_IRQ()` writes the interrupt entry vector through `wrent()` before invoking platform IRQ init. `process_mcheck_info()` suppresses expected machine checks used by probing, otherwise prints vector/PC/code, decodes common PAL reason codes, dumps registers, and optionally dumps logout memory.

**State and persistence behavior:** Mutates per-CPU expected/taken machine-check flags, global `perf_irq`, ISA DMA controllers, IRQ register context, and PAL interrupt entry state. No persistent data.

**Dependencies and integration points:** Entry assembly, machine vectors, SMP IPI handlers, Alpha PAL operations, DMA register constants, `rtc_timer_interrupt`, and generic IRQ functions all meet here.

**Risks:** Interrupts intentionally remain disabled until PAL return because some PALcode has RTI/IPL issues. Expected machine-check state is delicate for probing paths. A module can override `perf_irq`, so it must preserve interrupt-context constraints. Incorrect vector type routing can turn machine checks into device IRQs or vice versa.

**Test signals:** Boot and verify `wrent(entInt)`, RTC timer IRQ registration, device IRQ dispatch through current machine vector, machine-check probe suppression, real machine-check reporting, performance interrupt override modules, and ISA DMA reset behavior on legacy systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_alpha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_i8259.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_i8259.c

**Purpose:** Implements the legacy PC/AT 8259A PIC backend for Alpha systems, including mask/unmask/ack operations, initialization of IRQs 0-15, and ISA device interrupt dispatch through either PCI interrupt-ack cycles or direct PIC ISR polling.

**Important APIs/types/functions:** Exposes `i8259a_enable_irq()`, `i8259a_disable_irq()`, `i8259a_mask_and_ack_irq()`, `i8259a_irq_type`, `init_i8259a_irqs()`, `isa_device_interrupt()` when an `IACK_SC` address exists, and `isa_no_iack_sc_device_interrupt()` for polling mode. Internal state is `cached_irq_mask` and `i8259_irq_lock`.

**Control flow:** Init masks both PICs, installs `i8259a_irq_type` for IRQs 0-15, and reserves IRQ 2 as the cascade. Enable/disable update the cached mask under a spinlock and write the correct master/slave mask port. Mask-and-ack disables the IRQ then emits specific EOI commands, acknowledging slave first for IRQs >= 8. Device interrupt dispatch either reads the interrupt vector from the platform IACK sparse-cycle address and calls `handle_irq()`, or polls PIC ISR registers, masks out cascade/high bits, and handles all set bits.

**State and persistence behavior:** Maintains the runtime PIC mask cache and programs hardware PIC registers. No persistent state.

**Dependencies and integration points:** Used by many Alpha platform init paths as the ISA interrupt base. Depends on `outb/inb`, platform `IACK_SC` macros or machine-vector `iack_sc`, generic IRQ descriptors, and `no_action` for cascade reservation.

**Risks:** Mask bit semantics are inverted relative to some other controllers. Polling mode assumes simultaneous device IRQs are rare and relies on readable PIC command ports. Wrong `IACK_SC` mapping leads to bogus IRQ numbers. PIC operations must remain locked on SMP.

**Test signals:** Verify boot-time PIC masking, cascade registration, ISA IRQ delivery through both IACK and polling configurations, slave IRQ EOI ordering, and no spurious IRQ storms after mask/unmask cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_i8259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_impl.h -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_impl.h

**Purpose:** Private IRQ implementation header for Alpha kernel IRQ files and platform code. It declares common controller entry points, RTC IRQ number, ISA DMA initialization, i8259 chip functions, and `handle_irq()`.

**Important APIs/types/functions:** Defines `RTC_IRQ` as 8. Declares `isa_device_interrupt()`, `isa_no_iack_sc_device_interrupt()`, `srm_device_interrupt()`, `pyxis_device_interrupt()`, `init_srm_irqs()`, `init_pyxis_irqs()`, `init_rtc_irq()`, `common_init_isa_dma()`, `i8259a_enable_irq()`, `i8259a_disable_irq()`, `i8259a_mask_and_ack_irq()`, `i8259a_irq_type`, `init_i8259a_irqs()`, and `handle_irq()`.

**Control flow:** No runtime code; the declarations allow system-specific `sys_*.c` files and controller backends to wire machine vectors and IRQ chips together consistently.

**State and persistence behavior:** None. It exposes functions that mutate IRQ controller state elsewhere.

**Dependencies and integration points:** Includes generic interrupt, IRQ, and profile headers. Shared by `irq.c`, `irq_alpha.c`, `irq_i8259.c`, `irq_pyxis.c`, `irq_srm.c`, and many Alpha system platform files.

**Risks:** Any signature mismatch here breaks cross-file builds. `RTC_IRQ` is baked into Alpha timer interrupt handling and must match PAL vector assumptions. Because it is private, adding declarations here without corresponding build coverage can leave some platform configs broken.

**Test signals:** Compile all Alpha platform configurations, especially those using SRM-only, Pyxis, i8259, and custom system IRQ handlers. Confirm no duplicate or missing declarations as generic IRQ APIs evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_pyxis.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_pyxis.c

**Purpose:** Implements common PYXIS core-logic IRQ handling: a 32-bit enabled-mask controller for PCI interrupts above ISA, cascade to i8259, and initialization of level-triggered PYXIS IRQ descriptors.

**Important APIs/types/functions:** Exposes `pyxis_device_interrupt()` and `init_pyxis_irqs()`. Internal helpers/state are `cached_irq_mask`, `pyxis_update_irq_hw()`, `pyxis_enable_irq()`, `pyxis_disable_irq()`, `pyxis_mask_and_ack_irq()`, and `pyxis_irq_type`.

**Control flow:** Initialization disables all PYXIS interrupts, clears pending requests, performs an ISA interrupt-ack cycle, installs `pyxis_irq_type` for IRQs 16-47 except ignored ones, marks them level-triggered, and reserves IRQ 23 (`16 + 7`) as the ISA cascade. Device interrupt handling reads `PYXIS_INT_REQ`, filters with `cached_irq_mask`, and handles each set bit; bit 7 delegates to `isa_device_interrupt()`, all others call `handle_irq(16 + bit)`.

**State and persistence behavior:** Maintains a cached enabled mask and writes PYXIS INT_MASK/INT_REQ CSRs. No persistent state.

**Dependencies and integration points:** Depends on CIA/PYXIS core register macros, Alpha I/O barriers, i8259 cascade handling, and generic IRQ descriptors. Used by Pyxis-based system vectors.

**Risks:** Mask bit semantics are “1 means enabled,” unlike i8259. `init_pyxis_irqs()` tests `ignore_mask >> i` while iterating absolute IRQ numbers, so callers must pass an absolute-bit mask. Cascade handling assumes bit 7 is always ISA. Register write/readback ordering is required to force CSR effects.

**Test signals:** Boot a Pyxis platform, confirm IRQs 16-47 map and level flags are set, trigger ISA cascade and non-ISA PCI interrupts, test ignored IRQ mask behavior, and verify pending bits are cleared during init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_pyxis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_srm.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_srm.c

**Purpose:** Provides SRM PALcode-managed interrupt support for Alpha systems that let firmware handle interrupt masking. It defines an IRQ chip using `cserve_ena/dis`, initializes SRM IRQ descriptors, and converts SRM vectors to Linux IRQ numbers.

**Important APIs/types/functions:** Exposes `srm_irq_lock`, `init_srm_irqs()`, and `srm_device_interrupt()`. Internal helpers are `srm_enable_irq()`, `srm_disable_irq()`, and `srm_irq_type`.

**Control flow:** `init_srm_irqs(max, ignore_mask)` installs `srm_irq_type` for IRQs 16 through `max - 1`, skipping ignored IRQs below 64, and marks them level-triggered. The chip enable/disable callbacks serialize PAL console service calls with `srm_irq_lock` and pass `irq - 16` to `cserve_ena()` or `cserve_dis()`. Runtime dispatch computes `irq = (vector - 0x800) >> 4` and calls `handle_irq()`.

**State and persistence behavior:** No software mask cache; firmware/PAL owns mask state. The spinlock only serializes SMP access to PAL console service calls. No persistent data.

**Dependencies and integration points:** Depends on `cserve_ena/dis` from `head.S`, generic IRQ descriptors, and machine vectors that route device interrupts to `srm_device_interrupt()`.

**Risks:** Vector-to-IRQ arithmetic assumes SRM vector layout. PAL SMP safety is uncertain, hence the lock. Incorrect `max` or `ignore_mask` from platform code can expose firmware-reserved vectors. Firmware failures may not be visible to Linux.

**Test signals:** On SRM-managed systems, test enable/disable under SMP, device IRQ delivery from vectors, ignored-vector behavior, and level IRQ handling. Verify no concurrent PAL cserve calls occur under interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/irq_srm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/machvec_impl.h -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/machvec_impl.h

**Purpose:** Provides helper macros for instantiating Alpha machine vectors. It fills HAE/IACK defaults, MMU ASID limits, I/O operation tables, PCI operation hooks, and generic-versus-specific machine-vector placement/aliasing behavior.

**Important APIs/types/functions:** Defines HAE address fallbacks for IRONGATE, MARVEL, POLARIS, TSUNAMI, TITAN, WILDFIRE and optional one-window chips; fake `JENSEN_IACK_SC`, `T2_IACK_SC`, and `WILDFIRE_IACK_SC`; token-pasting macros `CAT1/CAT`; `DO_DEFAULT_RTC`; `DO_EV5_MMU`, `DO_EV6_MMU`, `DO_EV7_MMU`; `IO_LITE()`, `IO()`, `DO_*_IO` macros; `__initmv`; and `ALIAS_MV()`.

**Control flow:** No runtime code. System-specific `sys_*.c` files use these macros to initialize `struct alpha_machine_vector` fields. In generic kernels, vectors live in init data so setup can copy the selected one into `alpha_mv`. In non-generic kernels, `ALIAS_MV()` emits an assembler alias from `alpha_mv` to the single compiled vector and exports it.

**State and persistence behavior:** Affects placement and symbol aliasing of machine-vector objects at compile/link time. Runtime state is the selected `alpha_mv`, owned elsewhere.

**Dependencies and integration points:** Central to every Alpha system vector file. It connects core logic I/O functions such as `titan_ioremap`, `tsunami_pci_ops`, and `wildfire_pci_tbi` to the generic `alpha_mv` dispatch used by I/O, PCI, IRQ, and setup code.

**Risks:** Macro expansion must match exact symbol naming conventions for each core logic. Fake IACK values exist only to satisfy initialization and can be dangerous if accidentally used. Generic/non-generic aliasing is toolchain-sensitive and uses inline assembly due to GCC alias limitations.

**Test signals:** Build generic and non-generic Alpha kernels for each supported machine vector, inspect `alpha_mv` symbol resolution, boot enough to exercise I/O calls through machine vectors, and verify selected vector init data is not freed before copy in generic kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/machvec_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/module.c

**Purpose:** Implements Alpha-specific kernel module section preparation and ELF64 relocation application. It sizes and allocates module GOT entries for `R_ALPHA_LITERAL`, records GOT offsets in relocation metadata, and applies Alpha relocation types at load time.

**Important APIs/types/functions:** Exposes `module_frob_arch_sections()` and `apply_relocate_add()`. Internal type `struct got_entry` tracks per-symbol/addend GOT allocation. Important relocation cases include `R_ALPHA_REFLONG`, `REFQUAD`, `GPREL32`, `LITERAL`, `GPDISP`, `BRSGP`, `BRADDR`, `SREL32`, `SREL64`, `GPRELHIGH`, `GPRELLOW`, and `GPREL16`.

**Control flow:** `module_frob_arch_sections()` locates `.symtab` and `.got`, allocates one `got_entry` chain head per symbol, resets `.got` to an 8-byte-aligned `SHT_NOBITS` area, scans all `SHT_RELA` sections, and for each `R_ALPHA_LITERAL` assigns/deduplicates a GOT slot by symbol plus addend. It stores the GOT offset in high bits of `r_info` for later use. `apply_relocate_add()` computes `got` and GP (`got + 0x8000`), iterates relocations for a target section, computes symbol value plus addend, patches the target instruction/data, writes GOT entries for literals, and reports overflow/unknown relocation errors.

**State and persistence behavior:** Mutates module ELF section headers before allocation, relocation records in memory, the module GOT, and loaded text/data. Temporary GOT chains are allocated and freed during section frobbing. No persistent state.

**Dependencies and integration points:** Hooks into the Linux module loader. Depends on Alpha ELF relocation definitions, module `arch.gotsecindex`, and the Alpha GP/GOT code model.

**Risks:** Co-opting high bits of `r_info` for GOT offsets depends on relocation type width assumptions. Overflow checks are critical for branch, GP-relative, and literal relocations. Misaligned `REFQUAD` handling intentionally writes as two 32-bit halves because `BUG()` can produce misalignment.

**Test signals:** Load modules containing literals with same/different addends, GP-relative data, long branches, local `BRSGP`, section-symbol relocations, and intentionally overflowing relocations. Confirm `.got` size/alignment, GP value, relocation patch bytes, and clear errors for unknown/overflow cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/osf_sys.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/osf_sys.c

**Purpose:** Implements Alpha OSF/1 compatibility syscalls and ABI quirks. It translates OSF directory, stat, statfs, mount, uname/domain/sysinfo, property-list, signal-stack, floating-point control, timeval32/time, rusage/wait, memory mapping, priority, dual-return UID/GID/PID/pipe, and HAE interfaces to Linux internals.

**Important APIs/types/functions:** Defines many `SYSCALL_DEFINE*` entry points: `osf_brk`, `osf_set_program_attributes`, `osf_getdirentries`, `osf_mmap`, stat/statfs variants, `osf_mount`, `osf_utsname`, `getpagesize`, `getdtablesize`, `osf_getdomainname`, `osf_proplist_syscall`, `osf_sigstack`, `osf_sysinfo`, `osf_getsysinfo`, `osf_setsysinfo`, `osf_gettimeofday`, `osf_settimeofday`, `osf_utimes`, `osf_select`, `osf_getrusage`, `osf_wait4`, `osf_usleep_thread`, `old_adjtimex`, `arch_get_unmapped_area`, `osf_getpriority`, `getxuid`, `getxgid`, `getxpid`, `alpha_pipe`, and `sethae`. ABI structs include `osf_dirent`, `osf_stat`, `osf_statfs`, `osf_statfs64`, `timeval32`, `itimerval32`, `rusage32`, and `timex32`.

**Control flow:** Most syscalls copy OSF-shaped user structures, call a native Linux helper (`iterate_dir`, `vfs_stat`, `user_statfs`, `do_mount`, `ktime_get_real_ts64`, `core_sys_select`, `kernel_wait4`, `do_adjtimex`, etc.), then translate results back to OSF layout. `osf_getsysinfo` and `osf_setsysinfo` access Alpha thread IEEE FP control/status and unaligned-access control bits. `arch_get_unmapped_area()` first tries the caller hint as a lower bound, then `TASK_UNMAPPED_BASE`, then low memory to satisfy OSF loader expectations. Dual-return syscalls write the second result to `current_pt_regs()->r20`.

**State and persistence behavior:** Mutates `current->mm` break/code fields, mount namespace state via `do_mount`, UTS/timekeeping via settimeofday, current thread IEEE/UAC state, alternate signal stack fields, process sleep state, and saved HAE in `pt_regs`. It persists only through normal kernel subsystem state changes requested by syscalls.

**Dependencies and integration points:** Depends on VFS, mount, timekeeping, scheduler, signal, FPU/FPCR, HWRPB, usercopy, Alpha syscall return ABI, and syscall table wiring. It also defines Alpha `arch_get_unmapped_area()` used by mm.

**Risks:** This is ABI compatibility code with many usercopy and 32-bit time truncation surfaces. OSF structures differ subtly from Linux; overflow, alignment, and partial-buffer behavior matter. Some interfaces are explicitly guessed or minimally implemented, such as property lists and mount translations. `osf_sigstack()` uses lossy stack-size assumptions.

**Test signals:** Run OSF/1 compatibility binaries or targeted syscall tests for directory offsets, large inode overflow, statfs buffer truncation, UFS/CDFS/procfs mount translations, domain/sysinfo strings, FP control get/set/raise exception, timeval32 conversion, select timeout non-copyback, wait4 rusage32, `arch_get_unmapped_area()` hint behavior, dual-return register values, and `sethae`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/osf_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.c

**Purpose:** Detects and configures National Semiconductor PC873xx Super I/O chips on Alpha platforms. It probes known config-port bases, identifies chip models, and enables selected parallel/IDE features.

**Important APIs/types/functions:** Exposes `pc873xx_probe()`, `pc873xx_get_base()`, `pc873xx_get_model()`, `pc873xx_enable_epp19()`, and `pc873xx_enable_ide()`. Internal helpers are `pc873xx_read()` and `pc873xx_write()`. State includes static `base` and `model`, probe ports `0x398` and `0x26e`, and model-name table.

**Control flow:** `pc873xx_probe()` iterates probe bases, reserves two I/O ports with `request_region()`, reads `REG_SID`, matches bit patterns to PC87332/PC87306/PC87334/PC87303, and releases the region if no match. Feature functions read the configured base register, print an informational message, and write updated control bits: `pc873xx_enable_epp19()` sets PCR mode bits to EPP v1.9, while `pc873xx_enable_ide()` sets bit `0x40` in FER. Writes disable local interrupts and write the data byte twice as required by the chip.

**State and persistence behavior:** Stores detected base/model in static variables and mutates Super I/O configuration registers. The requested I/O region remains held after successful probe. No filesystem persistence.

**Dependencies and integration points:** Uses constants from `pc873xx.h`, Alpha port I/O, Linux I/O resource reservation, and platform setup code that calls probe/enable functions.

**Risks:** Probe only recognizes a subset of possible models and returns `1` or `-1` rather than normal `0/-errno`. `pc873xx_get_model()` assumes `model` is valid and should not be called before successful probe. Feature writes assume the selected chip has compatible registers.

**Test signals:** On target boards, confirm probe base, model string, retained I/O resource, EPP mode configuration, and IDE interrupt enablement. Negative tests should cover both probe ports unavailable or unknown SID values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.h -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.h

**Purpose:** Private header for PC873xx Super I/O support. It defines configuration-register indexes, model identifiers, and function prototypes used by platform setup code and `pc873xx.c`.

**Important APIs/types/functions:** Register constants include `REG_FER`, `REG_FAR`, `REG_PTR`, `REG_FCR`, `REG_PCR`, `REG_KRR`, `REG_PMC`, `REG_TUP`, `REG_SID`, `REG_ASC`, and `REG_IRC`. Model constants are `PC87303`, `PC87306`, `PC87312`, `PC87332`, and `PC87334`. Prototypes cover `pc873xx_probe()`, `pc873xx_get_base()`, `pc873xx_get_model()`, `pc873xx_enable_epp19()`, and `pc873xx_enable_ide()`.

**Control flow:** None; it is declarative.

**State and persistence behavior:** None. Constants describe hardware register addressing used by `pc873xx.c`.

**Dependencies and integration points:** Included by the PC873xx implementation and any Alpha platform file that needs Super I/O probing or feature enables.

**Risks:** Register constants must match the National PC873xx configuration protocol. Exposing `pc873xx_get_model()` without an `__init` prototype annotation in callers could cause section mismatch warnings if used incorrectly. Model `PC87312` exists but probe code in this subset does not identify it.

**Test signals:** Build platform files that include this header; verify constants against the chip datasheet and ensure every prototype has a matching implementation and expected init section usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pc873xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci-sysfs.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci-sysfs.c

**Purpose:** Implements Alpha-specific PCI sysfs resource and legacy bus mmap/read/write support. Alpha has sparse and dense PCI address spaces, so this file exposes `resourceN_sparse`, `resourceN_dense`, or adjusted legacy names/sizes and maps them through the proper hose base.

**Important APIs/types/functions:** Exposes `pci_remove_resource_files()`, `pci_create_resource_files()`, `pci_mmap_legacy_page_range()`, `pci_adjust_legacy_attr()`, `pci_legacy_read()`, and `pci_legacy_write()`. Local helpers include `hose_mmap_page_range()`, `__pci_mmap_fits()`, `pci_mmap_resource()`, sparse/dense mmap wrappers, `sparse_mem_mmap_fits()`, `pci_create_one_attr()`, `pci_create_attr()`, `__legacy_mmap_fits()`, and `has_sparse()`.

**Control flow:** Resource creation iterates standard BARs, skips empty resources, determines whether sparse and/or dense files are needed based on hose bases and sparse address fit, allocates `bin_attribute` structures plus embedded names, and creates sysfs mmap files. The mmap path validates the requested VMA fits the BAR, translates resource to bus address, adjusts `vm_pgoff` for sparse scaling, adds the hose base, and calls `io_remap_pfn_range()`. Legacy mmap adjusts file names/sizes for sparse spaces and maps bus legacy I/O or memory. Legacy read/write add the hose I/O base then call `inb/inw/inl` or `outb/outw/outl` with alignment checks.

**State and persistence behavior:** Creates/removes sysfs binary attributes attached to `struct pci_dev`; mutates VMA offsets during mmap; performs legacy I/O port reads/writes. No persistent data beyond sysfs lifetime.

**Dependencies and integration points:** Integrates with generic PCI sysfs hooks, Alpha `struct pci_controller` bases, `pcibios_resource_to_bus()`, `iomem_is_exclusive()`, and Alpha I/O accessors.

**Risks:** Sparse mappings multiply sizes by 32 and shift offsets, so fit calculations must match hardware encoding. Resource allocation uses `GFP_ATOMIC`; failures must remove partial files. `pci_legacy_write()` appears to call `outb(port, val)`/`outw(port, val)`/`outl(port, val)` even though Alpha wrappers take `(value, port)`, which is a likely argument-order bug worth review.

**Test signals:** On sparse and dense Alpha hoses, inspect sysfs resource file names/sizes, mmap each BAR within and beyond range, test exclusive iomem rejection, legacy mmap/read/write alignment errors, and verify byte/word/dword legacy writes actually write the intended value to the intended port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci.c -->
# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci.c

**Purpose:** Provides common Alpha PCI infrastructure: hose list management, PCI quirks, resource alignment, subsystem PCI initialization, optional SRM config save/restore, bus fixups, latency fixes, console resource claiming, root-bus scanning over multiple PCI controllers, allocation helpers, `pciconfig_iobase` syscall, and exported ISA bridge / `pci_iounmap()`.

**Important APIs/types/functions:** Exposes `pci_io_names`, `pci_mem_names`, `pci_hae0_name`, `hose_head`, `hose_tail`, `pci_isa_hose`, `pcibios_align_resource()`, `pcibios_fixup_bus()`, `pcibios_set_master()`, `pcibios_claim_one_bus()`, `common_init_pci()`, `alloc_pci_controller()`, `alloc_resource()`, `pciconfig_iobase()`, `pci_iounmap()`, and `isa_bridge`. Quirks include `quirk_isa_bridge()`, `quirk_cypress()`, and `pcibios_fixup_final()`.

**Control flow:** Core-logic files allocate and populate `pci_controller` hoses before `pcibios_init()` calls `alpha_mv.init_pci()`. `common_init_pci()` iterates hoses, clips memory-resource ends to avoid direct/SG DMA windows, builds host-bridge windows with offsets, sets machine-vector PCI ops/swizzle/map callbacks, scans each root bus, tracks domain info when bus numbers would overflow, claims firmware/console resources, assigns unassigned resources, and adds devices. Bus fixups optionally read bridge bases in probe-only mode and save SRM state per device. Resource alignment enforces per-hose minima and avoids sparse-memory alias octants. `pciconfig_iobase()` returns hose or sparse/dense base information by hose index or PCI bus/devfn.

**State and persistence behavior:** Maintains global hose list, `pci_isa_hose`, optional SRM saved-config linked list, `isa_bridge`, PCI resources, and host bridge/bus state. It can restore SRM PCI config during reboot when `ALPHA_RESTORE_SRM_SETUP` is enabled. No filesystem persistence.

**Dependencies and integration points:** Central integration point for all Alpha core logic files, machine vectors, Linux PCI core, memblock allocation, IOMMU arena globals, syscall table, and reboot code that may call `pci_restore_srm_config()`.

**Risks:** Multi-hose resource offsets and bus-number domain fallback are subtle. Cypress quirk modifies direct/SG DMA windows to avoid BIOS ROM aliases. `pciconfig_iobase()` assumes domain 0 for device lookup. `alloc_pci_controller()` relies on memblock zeroing/initialization assumptions after allocation; callers must fill all fields before scan.

**Test signals:** Boot representative one-hose and multi-hose Alpha systems, verify PCI enumeration/resource assignment, probe-only SRM behavior, Cypress IDE/bridge quirks, ISA bridge DMA mask, bus mastering latency timer writes, `pciconfig_iobase()` outputs, domain info when bus numbers wrap, and reboot SRM config restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/pci.c -->
