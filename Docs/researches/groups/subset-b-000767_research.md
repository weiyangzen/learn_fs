# Research Report: subset-b-000767

Grouped source-tree-aligned research for PowerPC architecture headers in `sources/distributed-fs/ceph-client`. Each file section preserves the source path for deterministic reconciliation into the mapped per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_gtm.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_gtm.h

Purpose: Declares the Freescale General-purpose Timer Module 16-bit timer interface used by platform timer clients that need ownership, programming, stopping, and acknowledgement of GTM channels.

Important APIs, types, and functions: `struct gtm_timer` carries the IRQ number, parent `struct gtm`, allocation state, and `__iomem` register pointers for control, mode, prescale, counter, reference, and event registers. Exported APIs are `gtm_get_timer16()`, `gtm_get_specific_timer16()`, `gtm_put_timer16()`, `gtm_set_timer16()`, `gtm_set_exact_timer16()`, `gtm_stop_timer16()`, and `gtm_ack_timer16()`.

Control flow: Callers acquire an available timer, configure a relative or exact 16-bit timeout with optional reload, service the IRQ by acknowledging event bits, stop the timer when no longer needed, and release ownership with `gtm_put_timer16()`.

State and persistence: State is volatile hardware/MMIO state plus the in-memory `requested` ownership bit. There is no persistent storage; all programming is lost across reset or driver teardown.

Dependencies and integration points: Depends on Linux integer types and Freescale GTM implementation code that owns the opaque `struct gtm`. It integrates with interrupt handlers, board code, and SoC timer users that know a GTM instance or can use any available timer.

Risks: Ownership must be balanced or timers can leak. Register pointers are raw MMIO, so endian access, event acknowledgement masks, and reload calculations are hardware-sensitive. The microsecond API can overflow or quantize against a 16-bit counter.

Test signals: Exercise generic and specific timer allocation, release-after-stop, one-shot and reload programming, exact 16-bit boundary values, event acknowledgement, IRQ firing, and concurrent allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_gtm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_hcalls.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_hcalls.h

Purpose: Provides inline wrappers for Freescale/ePAPR vendor hypercalls used to control partitions, DMA isolation, virtual MPIC MSI routing, error queues, nap state, device claims, and system reset.

Important APIs, types, and functions: Defines `FH_*` hcall numbers, `FH_HCALL_TOKEN()`, partition status constants, VCPU state constants, and `struct fh_sg_list`. Wrappers include `fh_send_nmi()`, device-tree property get/set, partition restart/status/start/stop/memcpy/stop_dma, `fh_dma_enable()`, `fh_dma_disable()`, `fh_vmpic_get_msir()`, `fh_system_reset()`, `fh_err_get_info()`, `fh_get_core_state()`, `fh_enter_nap()`, `fh_exit_nap()`, and `fh_claim_device()`.

Control flow: Each inline wrapper marshals arguments into registers, uses the ePAPR `ev_hcall*` helpers, then decodes return registers into output pointers. `CONFIG_PHYS_64BIT` changes physical-address argument packing for dtprops and memcpy scatter-gather entries.

State and persistence: No state is stored in the header. Hypercalls mutate hypervisor-owned partition/device/DMA/core state and copy results back through caller-provided buffers.

Dependencies and integration points: Depends on `asm/epapr_hcalls.h`, `asm/byteorder.h`, Linux errno/types, and Freescale hypervisor ABI. It integrates with board management, partition lifecycle code, error handling, DMA setup, and virtual interrupt controller paths.

Risks: ABI register ordering is brittle, especially where 64-bit physical addresses are split. Buffer length limits for dtprops and error queues must match hypervisor expectations. Some wrappers accept output pointers directly and assume callers provide valid storage. Hypercall failures are returned as Freescale status values, not normal Linux errno in all cases.

Test signals: Hypervisor ABI tests should cover 32-bit and `CONFIG_PHYS_64BIT` builds, property buffers at max length, partition state transitions, DMA enable/disable idempotence, scatter-gather memcpy packing, long/error returns, and output register decoding for MSIR and core-state calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_hcalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_lbc.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_lbc.h

Purpose: Defines register layouts, bitfields, controller state, and helper APIs for the Freescale Local Bus Controller and its UPM/FCM/GPCM operating modes.

Important APIs, types, and functions: `struct fsl_lbc_bank` models bank base/option registers, `struct fsl_lbc_regs` mirrors BR/OR, MAR/MAMR/MBMR/MCMR, event, bus, clock, and FCM registers, `struct fsl_upm` describes an assigned UPM machine, and `struct fsl_lbc_ctrl` stores the device, lock, IRQ, mapped registers, bank count, and suspend shadows. Helpers include `fsl_lbc_addr()`, `fsl_lbc_find()`, `fsl_upm_find()`, `fsl_upm_start_pattern()`, `fsl_upm_end_pattern()`, `fsl_upm_run_pattern()`, and global `fsl_lbc_ctrl_dev`.

Control flow: Drivers locate a bank/UPM by physical base, lock the controller, program machine mode registers or FCM sequences, start UPM patterns by writing `MxMR_OP_RP`, access attached devices, end patterns by returning to normal operation, and service/clear LTESR events.

State and persistence: Runtime state is MMIO register content plus controller lock/IRQ/bookkeeping. Suspend support snapshots bank and controller registers for restore. No disk persistence exists.

Dependencies and integration points: Depends on MMIO helpers, device model, spinlocks, and Freescale NAND/UPM/localbus consumers. It bridges board device-tree mappings to low-level local bus registers.

Risks: Bitfield definitions directly encode hardware ABI. Incorrect bank matching or endian MMIO access can corrupt memory windows. UPM pattern mode is global to the machine and must be serialized. Event masks distinguish NAND-specific and full-controller faults; clearing the wrong bits can lose diagnostics.

Test signals: Validate BR/OR decoding, UPM start/end under lock, FCM NAND command sequences, LTESR interrupt handling, suspend/resume register restore, and address lookup for all configured localbus banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_lbc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pamu_stash.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pamu_stash.h

Purpose: Exposes Freescale PAMU cache-stash configuration for IOMMU domains.

Important APIs, types, and functions: `enum pamu_stash_target` names L1, L2, and L3 stash targets. `fsl_pamu_configure_l1_stash(struct iommu_domain *domain, u32 cpu)` programs L1 stashing for a domain relative to a CPU.

Control flow: IOMMU or device setup code selects a target CPU/domain and calls the helper before DMA traffic that should be stashed near that CPU.

State and persistence: The header stores no state. Configuration persists only in PAMU/IOMMU hardware tables until changed or reset.

Dependencies and integration points: Depends on the generic `iommu_domain` abstraction and Freescale PAMU backend code. It is a small interface between DMA isolation and cache-locality policy.

Risks: CPU-to-cache mapping must be valid for the SoC. Stashing on the wrong CPU can hurt performance or violate assumptions in driver affinity code. Builds without PAMU support need the implementation to be correctly gated elsewhere.

Test signals: Test domain setup on valid and invalid CPU IDs, DMA traffic locality/performance counters, multi-CPU affinity changes, and compile coverage with PAMU/IOMMU options enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pamu_stash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pm.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pm.h

Purpose: Declares Freescale/QorIQ power-management modes and operation callbacks used by RCPM and platform sleep/deep-sleep code.

Important APIs, types, and functions: Defines e500 phase values, platform sleep levels, `FSL_PM_SLEEP`, `FSL_PM_DEEP_SLEEP`, `struct fsl_pm_ops`, global `qoriq_pm_ops`, and `fsl_rcpm_init()`. Operations cover IRQ mask/unmask, CPU enter/exit state, CPU up/die hooks, platform sleep entry, timebase freeze, IP-block power retention, and supported mode discovery.

Control flow: Platform initialization calls `fsl_rcpm_init()`, installs `qoriq_pm_ops`, and later CPU idle/hotplug/suspend paths invoke callbacks around state transitions and device power-retention decisions.

State and persistence: The header defines callback state only. Actual state is held by platform PM drivers and hardware registers; sleep settings persist only while the hardware remains powered/configured.

Dependencies and integration points: Integrates MPIC interrupt masking, CPU hotplug, suspend, timebase handling, and QorIQ RCPM support.

Risks: Callback ordering is critical: masking interrupts, freezing timebase, and powering IP blocks at the wrong point can break wakeup or time accounting. A null or partially populated `qoriq_pm_ops` must be handled by callers.

Test signals: Suspend and deep-sleep entry/exit, CPU hotplug through `cpu_die`/`cpu_up_prepare`, wake interrupt masking, timebase continuity, and mode discovery on boards with different RCPM revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fsl_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ftrace.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ftrace.h

Purpose: Supplies PowerPC-specific ftrace constants, register accessors, syscall-name matching, graph tracing hooks, per-CPU ftrace enable state, and trampoline metadata.

Important APIs, types, and functions: Defines `MCOUNT_ADDR`, `MCOUNT_INSN_SIZE`, `FTRACE_MCOUNT_MAX_OFFSET`, `struct dyn_arch_ftrace`, `arch_ftrace_get_regs()`, `arch_ftrace_fill_perf_regs()`, ftrace register getters/setters, `ftrace_graph_func()`, `arch_syscall_match_sym_name()`, `this_cpu_*_ftrace()` helpers, trampoline symbols, `ftrace_free_init_tramp()`, `ftrace_call_adjust()`, and direct-call support through `arch_ftrace_set_direct_caller()`.

Control flow: Dynamic ftrace patches call sites or patchable entries, initializes NOPs, optionally routes through out-of-line stubs, snapshots register state for callbacks/perf, and uses per-CPU PACA state to gate tracing on PPC64.

State and persistence: Runtime state includes per-callsite metadata, optional out-of-line stub pointers, PACA `ftrace_enabled`, and trampoline text ranges. It is kernel-memory state only.

Dependencies and integration points: Depends on ftrace core, `linux/ftrace_regs.h`, module metadata, PACA on PPC64, and PowerPC text patching/trampoline code.

Risks: Call-site offsets and ABI register fields must match compiler output. Syscall symbol matching has PowerPC-specific prefixes. Direct-call and graph paths modify return IP/link fields, so bad register handling can corrupt returns. Init trampoline lifetime must match module/core patching.

Test signals: Build/function tracing with `CONFIG_FUNCTION_TRACER`, dynamic ftrace with args/regs/direct calls, syscall tracing for `ppc_`, `ppc32_`, and `ppc64_` names, graph tracing, module tracepoints, and per-CPU enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/futex.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/futex.h

Purpose: Implements PowerPC futex atomic operations and compare-exchange in user memory using load-reserve/store-conditional sequences with exception-table recovery.

Important APIs, types, and functions: `__futex_atomic_op()` emits the atomic inline assembly for set/add/or/andn/xor operations. `arch_futex_atomic_op_inuser()` dispatches `FUTEX_OP_*` operations and returns the old value. `futex_atomic_cmpxchg_inatomic()` performs atomic compare-exchange on a user pointer.

Control flow: Callers enter with pagefaults disabled by the futex core. The assembly attempts user access, performs the atomic update with `lwarx/stwcx.`, retries on reservation failure, and uses exception fixups to return `-EFAULT`. Successful operations report the old user value.

State and persistence: The only state changed is the user futex word. No kernel state is persisted by the header.

Dependencies and integration points: Depends on Linux futex core, `uaccess`, PowerPC synchronization primitives, errno, and exception tables. It is part of the arch futex contract used by locking primitives in userspace.

Risks: Memory ordering and exception fixups are correctness-critical. Operation decoding must match generic futex op encodings. Misaligned or unmapped user addresses must fail without corrupting state. Reservation loops can spin under contention.

Test signals: Futex atomic op tests for all supported ops, compare-exchange success/failure, invalid user pointers, high contention, 32-bit and 64-bit builds, and memory-ordering litmus tests around wake/wait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/grackle.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/grackle.h

Purpose: Declares setup support for the Apple/Motorola Grackle PCI host bridge on PowerPC platforms.

Important APIs, types, and functions: Exposes `setup_grackle(struct pci_controller *hose)` when building the kernel and includes the PCI bridge controller type.

Control flow: Platform PCI setup code detects a Grackle host bridge, initializes the `pci_controller`, then calls `setup_grackle()` for bridge-specific configuration.

State and persistence: No state is stored in the header. Bridge configuration is applied to PCI/host-bridge registers by implementation code.

Dependencies and integration points: Depends on `asm/pci-bridge.h` and old PowerMac/CHRP PCI initialization paths.

Risks: The header is tiny but architecture-specific. Wrong bridge setup can affect all PCI config and I/O windows under the host bridge.

Test signals: Boot PCI enumeration on Grackle-based machines or emulators, config-space reads/writes, legacy I/O window setup, and build coverage for old PowerPC platform options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/grackle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/guest-state-buffer.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/guest-state-buffer.h

Purpose: Defines the PowerPC KVM/PAPR nested-virtualization guest-state buffer ABI: guest-state IDs, serialized element format, buffers, bitmaps, parsers, and message helpers for H_GUEST state hypercalls.

Important APIs, types, and functions: Defines `KVMPPC_GSID_*` IDs for guestwide, hostwide, meta, register, vector, and interrupt state; element class/type/flag enums; serialized `struct kvmppc_gs_header` and `struct kvmppc_gs_elem`; buffer, bitmap, parser, message, partition-table, process-table, and buffer-info structures. Key APIs include `kvmppc_gsid_size()`, `kvmppc_gsid_flags()`, `kvmppc_gsid_mask()`, `kvmppc_gsb_new/free/put/send/recv()`, `__kvmppc_gse_put()`, `kvmppc_gse_parse()`, typed put/get helpers, bitmap operations, parser lookup, and message send/receive wrappers.

Control flow: Callers create a buffer, include GSIDs in a message bitmap, serialize requested state into big-endian elements, invoke send or receive hypercalls, parse returned elements into a lookup table, and refresh caller-owned data through message ops.

State and persistence: `struct kvmppc_gs_buff` tracks capacity, used length, guest ID, VCPU ID, and header pointer. Bitmap/parser/message state is transient kernel memory. Hypervisor-owned guest state changes persist outside the buffer.

Dependencies and integration points: Depends on `hvcall.h`, `plpar_wrappers`, bitmap APIs, GFP allocation, PowerPC vector layout offsets, and KVM Book3S HV nested guest management.

Risks: Serialized sizes and endianness are ABI-sensitive. `kvmppc_gse_get_vector128()` warns on bad length but still continues after assigning zero, so malformed buffers need careful parser validation. GSID masks silently clear unsupported bits. Iteration trusts element counts and remaining length checks; off-by-one errors can drop or overrun elements.

Test signals: Round-trip every GSID class, malformed element lengths, full and empty bitmaps, vector layouts with and without VSX, buffer capacity exhaustion, H_GUEST send/receive failures, and parser duplicate/unknown GSID behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/guest-state-buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hardirq.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hardirq.h

Purpose: Defines PowerPC hardirq accounting layout and stack/interrupt entry helpers required by the generic IRQ subsystem.

Important APIs, types, and functions: `irq_cpustat_t` embeds `__softirq_pending` and optional `timer_irqs_event`. `ack_bad_irq()` is declared for unexpected IRQs. `ARCH_WANTS_NMI_IRQSTAT` advertises architecture NMI irqstat needs.

Control flow: Low-level interrupt entry increments/uses per-CPU irq stats, generic hardirq code reads pending softirq state, and unexpected vectors call `ack_bad_irq()`.

State and persistence: Per-CPU irq statistics are volatile runtime state. No persistence beyond kernel memory.

Dependencies and integration points: Depends on generic hardirq definitions and PowerPC low-level interrupt code. It integrates with softirq scheduling and debug/accounting code.

Risks: Layout must match generic expectations. Optional event accounting is config-sensitive, and bad IRQ handling must avoid recursive interrupt failure.

Test signals: Interrupt storm handling, bad IRQ reporting, softirq pending propagation, timer IRQ event accounting under `CONFIG_PPC_WATCHDOG`, and SMP per-CPU stat isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/head-64.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/head-64.h

Purpose: Defines 64-bit PowerPC early exception/prolog constants, PACA slot layout, and assembly helper macros used by low-level head/exception code.

Important APIs, types, and functions: Provides `PACA_SLOT_*` offsets, `PACA_SIZE`, exception vector helper constants, `TRAMP_REAL_BEGIN`, `TRAMP_VIRT_BEGIN`, and assembly macros for fixed-size exception branches, trap vectors, KVM test bits, and label placement.

Control flow: Assembly files include these definitions to lay out early real-mode trampolines, exception vectors, and PACA references before C runtime is available.

State and persistence: No C state is stored. The constants define boot-time and exception-time memory layout that remains ABI-like for assembly.

Dependencies and integration points: Integrates with `head_64.S`, exception vector code, PACA definitions, KVM interrupt paths, and linker layout.

Risks: Any offset or vector-size mismatch can break boot or exception dispatch. Macros are sensitive to instruction size, alignment, and whether code executes in real or virtual mode.

Test signals: PPC64 boot on hash/radix platforms, exception vector entry for system reset/machine check/interrupts, KVM-enabled builds, and objdump checks for expected vector placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/head-64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/heathrow.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/heathrow.h

Purpose: Defines register offsets and bit masks for the Apple Heathrow/Paddington I/O controller used on older PowerMac systems.

Important APIs, types, and functions: Constants cover feature control registers, media bay, floppy, SCC, SCSI, IDE, sound, Ethernet, PCI, and power-management bits. No functions or structs are declared.

Control flow: Platform and driver code uses these masks to set/clear controller feature bits during device enable, reset, suspend, and wake handling.

State and persistence: State is held in hardware feature-control registers. This header only names bit positions.

Dependencies and integration points: Integrates with old PowerMac feature drivers, MacIO/PMU paths, and platform power management.

Risks: Many bit names represent board-specific wiring. Incorrect masks can disable clocks, reset devices, or break wake behavior. There is no type safety around raw register access.

Test signals: Boot and suspend/resume on Heathrow/Paddington machines, device enable for IDE/SCSI/SCC/sound/Ethernet, media bay switching, and register readback after feature toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/heathrow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/highmem.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/highmem.h

Purpose: Provides PowerPC highmem declarations and kmap support glue for 32-bit systems with memory beyond the permanent kernel mapping.

Important APIs, types, and functions: Defines `PKMAP_BASE`, `LAST_PKMAP`, `LAST_PKMAP_MASK`, `PKMAP_NR()`, `PKMAP_ADDR()`, declares `kmap_prot`, `kmap_pte`, and includes generic highmem helpers. It also declares `flush_cache_kmaps()` behavior.

Control flow: Highmem pages are temporarily mapped through pkmap slots. Generic kmap code uses the architecture constants and page-table pointer to establish mappings and flush caches as needed.

State and persistence: pkmap page tables and mapping counters are runtime-only kernel state.

Dependencies and integration points: Depends on page-table, cache flush, and generic highmem infrastructure. It is relevant mainly for 32-bit PowerPC highmem builds.

Risks: Incorrect slot arithmetic or cache flushing can corrupt highmem data. Highmem code is config-sensitive and must not leak into PPC64 assumptions.

Test signals: 32-bit highmem boot, kmap/kunmap stress, pkmap wraparound, cache-coherency tests, and build coverage with and without `CONFIG_HIGHMEM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hmi.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hmi.h

Purpose: Declares Hypervisor Maintenance Interrupt event types and entry points for handling HMI conditions on PowerPC systems.

Important APIs, types, and functions: Defines event type constants for malformed event data, release, malfunction alert, processor recovery done, unknown events, and `struct pt_regs`-based handler declarations such as `hmi_exception_realmode` through interrupt macros elsewhere.

Control flow: Real-mode or early exception code receives an HMI, decodes event data, and dispatches to C handlers that can log, recover, or escalate.

State and persistence: No state is stored in the header. HMI state is in CPU/hypervisor event buffers and handler-side logs.

Dependencies and integration points: Integrates OPAL/pSeries HMI paths, machine-check style recovery, and low-level interrupt declarations.

Risks: HMI handling often runs with restricted context. Bad event decoding or unsafe calls from real mode can worsen platform failures.

Test signals: Injected HMI events for known and unknown types, malformed payload handling, real-mode entry coverage, recovery-done reporting, and builds across OPAL/pSeries configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hugetlb.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hugetlb.h

Purpose: Provides PowerPC huge-page helpers used by generic hugetlb code for page-table setup, PTE conversion, flush decisions, and hugepage range handling.

Important APIs, types, and functions: Declares or defines helpers such as huge PTE accessors, `arch_make_huge_pte()`, `huge_ptep_*` operations, `hugetlb_free_pgd_range()`, and architecture predicates around hugepage support. Behavior is split by radix/hash and config options.

Control flow: Generic hugetlb code calls these helpers when creating, changing, clearing, or flushing huge mappings. PowerPC-specific code handles hugepage PTE encoding and MMU model details.

State and persistence: The header manipulates page-table state; mappings persist until unmapped. No independent state is stored in the header.

Dependencies and integration points: Depends on PowerPC MMU/page-table headers and generic hugetlb infrastructure. It integrates memory management, TLB flush, and page fault paths.

Risks: Huge PTE encoding differs across MMU variants. Wrong flush or range-free behavior can leave stale translations. Config stubs must match generic API expectations.

Test signals: hugetlbfs mmap/fault/unmap, migration and protection changes, hash and radix builds, 4K/64K base page sizes, gigantic pages, and TLB invalidation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcall.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcall.h

Purpose: Defines the pSeries/PAPR hypervisor call ABI: return codes, flags, opcode numbers, capability bits, hcall wrapper prototypes, and data structures for memory, performance, and nested guest state.

Important APIs, types, and functions: Provides `HVSC`, `H_SUCCESS` and extensive error/long-busy codes, `H_IS_LONG_BUSY()`, page/TCE/VPA/RPTI/guest capability flags, all major `H_*` opcodes through `MAX_HCALL_OPCODE`, `plpar_hcall_norets()`, raw/notrace variants, `plpar_hcall()`, `plpar_hcall9()`, tracepoint hooks, `h_get_mpp()`, `h_get_mpp_x()`, `get_longbusy_msecs()`, `struct hv_guest_state`, and GPCI request structs.

Control flow: Callers select an opcode/flags, invoke a `plpar_hcall*` wrapper, inspect the PAPR return code, optionally retry on long-busy codes using the provided delay hint, and decode retbuf/data structures.

State and persistence: The header holds no state. Hcalls mutate hypervisor-owned partition, memory, interrupt, VIO, KVM guest, and platform state. Tracepoint static-key state is external.

Dependencies and integration points: Integrates pSeries platform code, KVM Book3S HV, VIO, IOMMU/TCE, memory hotplug, secure VM, persistent keys, SCM, XIVE, and performance counter paths.

Risks: Opcode/flag constants are firmware ABI. Return-code sign conventions mix positive busy hints and negative errors. Raw calls are used in real mode and must avoid tracing/statistics. `hv_guest_state_size()` must stay version-compatible as fields are appended.

Test signals: Hcall wrapper ABI tests, long-busy retry handling, tracepoint entry/exit, nested guest state versions 1 and 2, GPCI buffer sizing, and platform firmware tests for representative opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvconsole.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvconsole.h

Purpose: Declares low-level pSeries LPAR hypervisor console get/put helpers for virtual terminal devices.

Important APIs, types, and functions: Defines `MAX_VIO_PUT_CHARS` and `SIZE_VIO_GET_CHARS` as 16-byte firmware transfer limits. Exposes `hvc_get_chars()`, `hvc_put_chars()`, and `hvc_vio_init_early()`.

Control flow: Console drivers call get/put wrappers with a vterm number and buffer. Early boot can initialize HVC VIO before the full device model is available.

State and persistence: No state in the header. Console state lives in hvc/vio driver structures and firmware terminal queues.

Dependencies and integration points: Integrates with hvc console, pSeries VIO firmware, and early console setup.

Risks: Firmware transfer size is capped at 16 bytes, so callers must handle short I/O. Early initialization runs before normal allocation/device discovery.

Test signals: Early console output, runtime HVC read/write, transfer sizes above and below 16 bytes, vterm absence, and boot with console as primary device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvconsole.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcserver.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcserver.h

Purpose: Declares PPC64 hypervisor virtual-console server partner discovery and connection management interfaces.

Important APIs, types, and functions: `HVCS_CLC_LENGTH` sets the converged location code length. `struct hvcs_partner_info` records list linkage, partner unit address, partition ID, and location code. APIs include `hvcs_get_partner_info()`, `hvcs_free_partner_info()`, `hvcs_register_connection()`, and `hvcs_free_connection()`.

Control flow: Server code requests partner info into a list, registers a connection to a partner partition/unit address, later frees the connection and list data.

State and persistence: Partner lists are caller-owned kernel memory. Active connection state is managed by firmware and the hvcs driver.

Dependencies and integration points: Depends on Linux lists and pSeries VIO/hvcs firmware calls.

Risks: Location-code lengths and caller-provided `pi_buff` storage must match firmware output. Connection registration/freeing must be balanced to avoid stale virtual terminal routes.

Test signals: Partner enumeration with multiple entries, long location codes, connection register/free cycles, firmware errors, and list cleanup after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcserver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvsi.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvsi.h

Purpose: Defines the Hypervisor Virtual Serial Interface packet format and library state used by hvc/tty serial console implementations.

Important APIs, types, and functions: Defines packet header types, control/query verbs, modem-control masks, `HVSI_MAX_OUTGOING_DATA`, `HVSI_VERSION`, packet structs (`hvsi_header`, `hvsi_data`, `hvsi_control`, `hvsi_query`, `hvsi_query_response`), `struct hvsi_priv`, and hvsilib open/close/read/write/establish/get/put APIs.

Control flow: The library buffers incoming bytes, parses packet headers and lengths, sends data/control/query packets through supplied `get_chars`/`put_chars` callbacks, negotiates protocol establishment, and exposes modem-control updates to tty code.

State and persistence: `struct hvsi_priv` stores input buffer cursor/length, sequence number, open/established/console flags, modem-control state, tty pointer, callbacks, and terminal number. It is runtime tty state only.

Dependencies and integration points: Integrates hvc console structures, tty state, pSeries hypervisor terminal I/O, and endian packet fields.

Risks: Packet lengths are small and must be validated against the 255-byte input buffer. Sequence numbers and establishment state affect protocol correctness. Modem-control masks are sparse.

Test signals: Protocol establishment, data packets at maximum payload, split/partial input packets, control/query responses, DTR changes, close protocol, and console versus normal tty open paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_breakpoint.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_breakpoint.h

Purpose: Defines PowerPC hardware breakpoint/watchpoint architecture state and helper contracts for perf and ptrace watchpoints.

Important APIs, types, and functions: `struct arch_hw_breakpoint` records address, type, requested and hardware length, flags, and perf single-step state. Defines read/write/translate/user/kernel/hypervisor/extraneous type bits, disabled flag, DABR/DAWR length limits, `HW_BREAKPOINT_SIZE`, `nr_wp_slots()`, `wp_check_constraints()`, and `wp_get_instr_detail()`.

Control flow: Breakpoint setup validates address/type/length against DABR/DAWR constraints, programs one or two watchpoint slots depending on CPU features, and exception handling decodes the faulting instruction/effective address for constraint checks.

State and persistence: Per-task/perf breakpoint state is stored outside the header. Hardware DAWR/DABR registers hold volatile watchpoint state.

Dependencies and integration points: Depends on CPU feature detection, instruction decoding, perf hardware breakpoint core, ptrace/debug exception paths, and PowerPC Book3S/8xx differences.

Risks: Slot count changes with `CPU_FTR_DAWR1`. Length granularity differs for DABR/DAWR and 8xx. Mis-decoding instructions can cause false positives or missed watchpoints.

Test signals: Read/write watchpoints, user/kernel privilege filters, DAWR1-capable CPUs, DABR fallback, 8xx granularity, perf single-step reinstall, and extraneous IRQ handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_irq.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_irq.h

Purpose: Implements PowerPC local interrupt masking primitives, soft-mask state, lazy interrupt replay checks, PMI handling, and idle IRQ preparation declarations.

Important APIs, types, and functions: Defines `PACA_IRQ_*` pending bits, soft mask states, hard enable/disable helpers, `irq_soft_mask_*()` operations, `arch_local_irq_*()` operations, PMI pending helpers, PMU save/restore macros, `hard_irq_disable()`, `lazy_irq_pending()`, `should_hard_irq_enable()`, `do_hard_irq_enable()`, `arch_irq_disabled_regs()`, idle prep APIs, and `mtmsr_isync_irqsafe()`.

Control flow: Code manipulates soft mask bits in PACA/regs, disables or enables hardware EE/RI bits as required, queues pending events for lazy replay, treats PMI specially where necessary, and prepares idle paths to avoid losing pending interrupts.

State and persistence: Runtime state lives in PACA fields, MSR bits, pt_regs snapshots, and pending interrupt bits. No persistent storage exists.

Dependencies and integration points: Depends on PACA, MSR accessors, tracing, lockdep IRQ state, PMU code, idle code, and low-level exception entry/exit.

Risks: Hardware and software masks can diverge. Enabling hard IRQs in unsafe contexts risks reentrancy. PMI handling is config-sensitive. Lazy pending bits must be replayed in the right order.

Test signals: IRQ enable/disable nesting, soft-mask transitions through exception entry/exit, PMU interrupt save/restore, idle entry with pending IRQs, lockdep IRQ tracing, and SMP stress with doorbell/decrementer/external interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hydra.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hydra.h

Purpose: Defines register offsets and bit masks for the Apple Hydra Mac I/O controller used by legacy PowerPC systems.

Important APIs, types, and functions: Constants describe feature-control, interrupt, DMA, SCC, SCSI, Ethernet, and power-management bits. The header does not expose functions.

Control flow: Platform feature code uses these constants to toggle clocks/resets, route interrupts, and enable controller subdevices.

State and persistence: State is held in Hydra hardware registers only.

Dependencies and integration points: Integrates with old PowerMac platform, MacIO-style device setup, and low-level feature control code.

Risks: The definitions are board-specific and lack type checking. Wrong masks can disable essential devices or misroute interrupts on old machines.

Test signals: Boot on Hydra-based hardware/emulators, SCC/SCSI/Ethernet initialization, interrupt routing, suspend/resume register restore, and device reset sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hydra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/i8259.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/i8259.h

Purpose: Declares legacy 8259 PIC initialization for PowerPC systems that include an ISA-compatible interrupt controller.

Important APIs, types, and functions: Exposes `i8259_init(struct device_node *node, unsigned long intack_addr)` and includes IRQ definitions.

Control flow: Platform setup discovers the PIC node and interrupt-acknowledge address, then initializes the 8259 cascade and legacy IRQ range.

State and persistence: PIC mask/vector state is hardware runtime state managed by the implementation.

Dependencies and integration points: Depends on device-tree nodes and generic IRQ subsystem. It integrates legacy ISA interrupts into PowerPC IRQ domains.

Risks: Wrong acknowledge address or device-tree wiring can break all legacy IRQs. Legacy PIC code must coexist with MPIC/XIVE/IPIC controllers.

Test signals: ISA IRQ delivery for IRQ0-15, cascade interrupt through the parent controller, mask/unmask behavior, spurious IRQ handling, and boot without an 8259 node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/i8259.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ibmebus.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ibmebus.h

Purpose: Declares IBM eBus device/driver structures and registration helpers for pSeries virtual platform buses.

Important APIs, types, and functions: `struct ibmebus_dev` wraps `struct device`, an OF node, and bus resource metadata. `struct ibmebus_driver` includes name, OF match table, probe/remove/shutdown callbacks, and embedded `device_driver`. Helpers convert device/driver types and register/unregister drivers.

Control flow: Drivers register an `ibmebus_driver`, the bus matches OF nodes against `id_table`, invokes probe with an `ibmebus_dev`, and later calls remove/shutdown.

State and persistence: Device/driver state is normal Linux device-model runtime state. No persistent storage.

Dependencies and integration points: Depends on OF device tree and Linux device model. It integrates IBM platform bus devices with module driver binding.

Risks: OF match tables and resource metadata must accurately describe platform devices. Driver callbacks must handle hotplug/removal if supported.

Test signals: Driver registration/unregistration, OF matching, probe/remove/shutdown ordering, module unload, and resource exposure for representative eBus devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ibmebus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/icswx.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/icswx.h

Purpose: Defines the PowerPC ICSWX coprocessor interface, request-block layout, status bits, and inline instruction wrappers.

Important APIs, types, and functions: Declares request/status flags, `struct coprocessor_request_block`, `struct coprocessor_status_block`, `struct vas_window`, and inline `icswx()`-style assembly helpers that execute the instruction and return condition/status information.

Control flow: Accelerator/VAS users prepare a request block and status block, issue the ICSWX instruction against a window/context, then inspect status/error bits for completion or fault handling.

State and persistence: Request and status blocks are caller-owned memory. Accelerator/window state is maintained by hardware and VAS/coproc subsystems.

Dependencies and integration points: Integrates with VAS/NX/coprocessor drivers, PowerPC inline assembly, and endian/alignment-sensitive hardware block formats.

Risks: Request block alignment and reserved fields must match hardware. Inline assembly clobbers and condition handling are ABI-sensitive. Fault/status interpretation must distinguish retryable and fatal accelerator errors.

Test signals: Successful ICSWX submission, invalid window/context faults, status-block error decoding, alignment failures, concurrent submissions, and accelerator reset/error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/icswx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/idle.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/idle.h

Purpose: Declares PowerPC CPU idle state, stop/winkle helpers, thread-sibling coordination, and idle wake/replay interfaces.

Important APIs, types, and functions: Provides idle state flags and prototypes for entering low-power states, saving/restoring SPRs, stop API helpers, `pnv_*` idle functions, and CPU/thread state tracking used by platform idle code.

Control flow: CPU idle paths select a platform state, prepare IRQ state, save required registers, enter nap/sleep/winkle/stop, resume through low-level wake code, restore state, and replay pending interrupts.

State and persistence: Runtime state includes per-CPU idle flags, saved SPRs, sibling thread state, and platform stop state. It is volatile across boot/runtime only.

Dependencies and integration points: Integrates cpuidle, OPAL/PowerNV, pSeries/QorIQ idle support, interrupt masking, timebase handling, and SMP CPU hotplug.

Risks: Idle entry interacts tightly with interrupt masking and firmware. Losing SPR state or missing a pending interrupt can hang a CPU. Deep states may affect sibling threads.

Test signals: cpuidle state residency, wake from decrementer/external interrupts, stop/winkle state save/restore, sibling-thread coordination, CPU hotplug from idle states, and suspend/resume stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/idle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/imc-pmu.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/imc-pmu.h

Purpose: Defines In-Memory Collection PMU structures and constants for PowerNV/PowerPC performance monitoring units backed by OPAL IMC metadata.

Important APIs, types, and functions: Describes IMC domain/type constants, event and counter metadata structures, memory block descriptors, per-PMU data, and helper prototypes for IMC PMU registration and event handling.

Control flow: Platform code discovers IMC catalog data, builds PMU instances and event tables, maps counter memory, registers perf PMUs, and perf event operations read/update counters.

State and persistence: Runtime state includes mapped IMC memory, PMU/event descriptors, active event state, and per-CPU/chip metadata. It is not persistent across reboot.

Dependencies and integration points: Depends on perf PMU core, OPAL IMC catalog/memory interfaces, CPU/chip topology, and PowerNV platform code.

Risks: Catalog parsing and counter offsets are firmware ABI-sensitive. Counter memory may be per-core/chip/thread and needs correct affinity. Hotplug and memory mapping lifetime must be synchronized with perf events.

Test signals: IMC catalog discovery, perf list/stat for core/chip/thread PMUs, CPU hotplug, counter wraparound, invalid event IDs, and firmware absence/failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/imc-pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/immap_cpm2.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/immap_cpm2.h

Purpose: Defines the CPM2 internal memory map for classic embedded PowerPC SoCs, including SIU, interrupt controller, timers, DMA, FCC/SCC/SMC, USB, and dual-port RAM regions.

Important APIs, types, and functions: Provides many packed register-map structs, `cpm2_map_t` for the full IMMR layout, PISCR bit definitions, `im_dprambase`, and global mapped pointer `cpm2_immr`.

Control flow: CPM2 platform and driver code maps the IMMR, casts it to `cpm2_map_t`, then accesses sub-block registers for communication controllers, timers, DMA, and interrupt/pin configuration.

State and persistence: State is hardware MMIO register content and dual-port RAM. `cpm2_immr` is a runtime mapping pointer.

Dependencies and integration points: Integrates CPM2 serial, Ethernet, USB, DMA, interrupt, and board setup drivers. It depends on exact SoC register layout and `__iomem` access discipline.

Risks: This is a large hardware ABI map; padding/reserved fields must remain exact. Direct struct MMIO access is fragile across endian, alignment, and compiler packing assumptions. Wrong offsets can affect unrelated peripherals.

Test signals: CPM2 board boot, serial/FCC/SCC/SMC operation, timer interrupts, DMA transfers, USB if present, dual-port RAM allocation, and compile-time offset checks against datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/immap_cpm2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/inst.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/inst.h

Purpose: Provides an architecture-neutral wrapper type and helpers for PowerPC instructions, including support for prefixed 64-bit instructions on newer CPUs.

Important APIs, types, and functions: Defines `get_user_instr()`, `__get_user_instr()`, `ppc_inst_t` accessors, `ppc_inst()`, `ppc_inst_prefix()`, `ppc_inst_val()`, `ppc_inst_suffix()`, `ppc_inst_read()`, `ppc_inst_prefixed()`, `ppc_inst_swab()`, `ppc_inst_equal()`, `ppc_inst_len()`, `ppc_inst_next()`, `ppc_inst_as_ulong()`, `ppc_inst_write()`, and nofault copy helpers.

Control flow: Instruction decoders and patchers read a word, detect whether it is prefixed, fetch/write the suffix when needed, compare or byte-swap the logical instruction, and advance pointers by 4 or 8 bytes.

State and persistence: No state is stored. Helpers read/write kernel or user instruction memory.

Dependencies and integration points: Used by kprobes, ftrace, BPF, instruction emulation, patching, and fault-safe code reads. Depends on uaccess and nofault copy helpers.

Risks: Prefixed instruction length handling is critical for patching and stepping. User instruction fetch must be endian-correct and fault-safe. Treating prefixed instructions as single words can corrupt decoding.

Test signals: Decode normal and prefixed instructions, nofault copies across faults, pointer advancement, byte-swap equality, text patching of prefixed instructions, and 32-bit/non-prefixed build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/interrupt.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/interrupt.h

Purpose: Centralizes PowerPC interrupt vector numbers, exception entry/exit preparation, NMI handling, and declaration/definition macros for C interrupt handlers.

Important APIs, types, and functions: Defines `INTERRUPT_*` vector offsets, soft-mask assertions, restart-table search prototypes, `interrupt_enter_prepare()`, `interrupt_exit_prepare()`, async and NMI prepare/exit helpers, `struct interrupt_nmi_state`, handler attributes, `DECLARE_*` and `DEFINE_*` handler macros, many exception handler declarations, syscall/interrupt exit helpers, and replay functions.

Control flow: Low-level assembly calls generated C wrappers. Wrappers run enter preparation, invoke the typed handler, run exit preparation, and mark functions not probeable. NMI paths save/restore ftrace and irq state separately.

State and persistence: Uses pt_regs, soft-mask state, interrupt restart tables, tracing/lockdep state, and temporary NMI state. No persistent storage exists.

Dependencies and integration points: Integrates low-level exception vectors, tracing, lockdep, KCSAN/KASAN attributes, syscall exit, soft interrupt replay, page fault, machine check, HMI, and IRQ handlers.

Risks: Entry/exit ordering is delicate: IRQ state, tracing, RCU, and restart table handling must match context. Handler macros encode ABI and probe restrictions. Reentrancy around NMI and masked interrupts is high risk.

Test signals: Exception entry for all declared handlers, syscall exit restart paths, soft-mask assertion coverage, NMI/ftrace disable behavior, machine check/HMI paths, and lockdep/RCU tracing under interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io-defs.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io-defs.h

Purpose: Provides the macro include-list used by `io.h` to declare and define PCI/ISA port I/O accessors consistently.

Important APIs, types, and functions: Expands `DEF_PCI_AC_RET` or `DEF_PCI_AC_NORET` for `inb/inw/inl`, `outb/outw/outl`, string input operations, and string output operations.

Control flow: `io.h` includes this file twice with different macro definitions: once to build the `ppc_pci_io` hook structure and again to generate inline wrappers that call hooks or default implementations.

State and persistence: No state. It participates in compile-time code generation.

Dependencies and integration points: Tightly coupled to `asm/io.h` and optional indirect PIO hooks.

Risks: Because it is intentionally multiple-included, include guards would break it. Argument tuple order must match both hook declarations and default `__do_*` functions.

Test signals: Compile with and without `CONFIG_PPC_INDIRECT_PIO`, verify all accessors are declared once, and exercise hook override paths for port I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io.h

Purpose: Implements PowerPC MMIO, port I/O, endian-specific accessors, ioremap declarations, raw real-mode accessors, generic iomap glue, and address translation helpers.

Important APIs, types, and functions: Defines IO base variables, low-level `in_*`/`out_*` MMIO accessors with barriers, raw real-mode `__raw_rm_*` operations, PIO recovery on PPC32, EEH-aware `read*` wrappers, string I/O, `ppc_pci_io` hook structure via `io-defs.h`, `ioremap*`, `iounmap`, `ioport_map`, `iosync`, iobarriers, `virt_to_phys()`, `phys_to_virt()`, `virt_to_bus()`/`bus_to_virt()` on PPC32, and bit set/clear helpers.

Control flow: Drivers map resources with `ioremap`, use Linux read/write accessors, which route through EEH or raw MMIO and optionally through indirect PIO hooks. Reads use sync/twi/isync sequences; writes use sync and mark MMIO write buffers pending.

State and persistence: Runtime state includes global IO base variables, ISA bridge state, indirect PIO hook function pointers, and MMIO mappings. Hardware register state persists as device state.

Dependencies and integration points: Integrates PCI/ISA, EEH, generic iomap, page table mapping, delay/barrier primitives, and architecture-specific assembly constraints.

Risks: Barrier semantics and endian conversion are correctness-critical. PPC32 recovery fixups for bad PIO accesses are fragile. `virt_to_phys()` warns under debug virtual for invalid addresses and must not be used for DMA bus mappings. Indirect PIO hooks must mirror default semantics.

Test signals: MMIO read/write endian tests, EEH injected failures, PPC32 bad-port recovery, indirect PIO hook coverage, ioremap variants, string I/O, real-mode raw access in hypervisor context, and barrier ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io_event_irq.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io_event_irq.h

Purpose: Defines pSeries I/O event interrupt payload format and notifier entry point for platform event-log I/O notifications.

Important APIs, types, and functions: Defines event type, subtype, and scope constants; `PSERIES_IOEI_RPC_MAX_LEN`; `struct pseries_io_event`; and global `pseries_ioei_notifier_list`.

Control flow: Firmware/platform code decodes an I/O event section, populates `struct pseries_io_event`, then notifies registered listeners through the atomic notifier chain.

State and persistence: Event structs are transient. The notifier list is runtime kernel state.

Dependencies and integration points: Depends on Linux notifier APIs and pSeries platform event logging. It integrates PCI/PHB, service processor, node online/offline, and device rebalance notifications.

Risks: RPC data length must not exceed the fixed 216-byte buffer. Atomic notifier callbacks must be safe in the context used by the event IRQ path.

Test signals: Inject event types/subtypes, maximum RPC length, multiple notifier registrations, callback failure ordering, and node/PHB rebalance notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io_event_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/iommu.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/iommu.h

Purpose: Declares PowerPC IOMMU/TCE table structures, table/group operations, DMA mapping helpers, VFIO-style TCE exchange APIs, and early platform initialization hooks.

Important APIs, types, and functions: Defines IOMMU page macros, DMA window property names, `iommu_table_ops`, `iommu_pool`, `iommu_table`, `iommu_table_group_ops`, `iommu_table_group`, table reference/init/clear/reserve helpers, group registration/device attach, TCE exchange/kill/check/flush/direction helpers, DMA map/unmap/coherent APIs, early pSeries/DART/PASEMI init, and `dma_iommu_ops`.

Control flow: Platform setup creates tables/groups, devices attach to a group, DMA mapping allocates TCE ranges from pools, writes TCEs through table ops, flushes as needed, and unmap/free returns ranges. VFIO/userspace paths exchange TCEs after parameter checks.

State and persistence: `iommu_table` stores page shift, offset, size, pools, locks, reference count, userspace ownership, and ops. Groups link tables to devices. State is runtime memory plus hardware TCE tables.

Dependencies and integration points: Integrates DMA API, PCI/pSeries/DART platform code, VFIO/IOMMU userspace mappings, device-tree DMA windows, and memory hotplug/restore.

Risks: TCE address/permission checks protect DMA isolation. Pool allocation must be synchronized. Userspace-owned entries need careful RO/permission handling. Early boot init order affects all DMA.

Test signals: DMA map/unmap/coherent allocation, scatter-gather boundaries, TCE userspace exchange failures, table refcounting, group attach/detach, IOMMU off/force-on modes, and suspend restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ipic.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ipic.h

Purpose: Declares the Freescale IPIC interrupt controller register offsets, initialization flags, priority groups, MCP IRQ IDs, and setup/status APIs.

Important APIs, types, and functions: Defines spread-mode and MCP flags, IPIC register offsets, `enum ipic_prio_grp`, `enum ipic_mcp_irq`, `ipic_set_default_priority()`, `ipic_get_mcp_status()`, `ipic_clear_mcp_status()`, `ipic_init()`, and `ipic_get_irq()`.

Control flow: Platform code initializes IPIC from a device-tree node with flags, sets default priority, uses `ipic_get_irq()` as the interrupt dispatch source, and reads/clears MCP status for critical events.

State and persistence: Controller state is in IPIC hardware registers and implementation-owned `struct ipic`.

Dependencies and integration points: Depends on Linux IRQ core and OF node discovery. It integrates embedded Freescale interrupt routing with generic IRQ handling.

Risks: Priority/register offsets are hardware ABI. Incorrect spread-mode flags or MCP routing can starve or misclassify interrupts. Status clear masks must be precise.

Test signals: IRQ dispatch from all groups, default priority setup, MCP status read/clear, device-tree init failures, and mixed internal/external interrupt load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ipic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq.h

Purpose: Declares PowerPC generic IRQ constants, per-CPU interrupt stacks, lost interrupt accounting, and architecture IRQ helper functions.

Important APIs, types, and functions: Defines `NR_IRQS`, `NR_IRQS_LEGACY`, `ppc_n_lost_interrupts`, `virq_to_hw()`, `irq_canonicalize()`, `distribute_irqs`, BookE critical/debug/mcheck stacks, hardirq/softirq stacks, `__do_IRQ()`, `irq_choose_cpu()`, and optional `arch_trigger_cpumask_backtrace()`.

Control flow: Generic IRQ code uses `__do_IRQ()` for dispatch and architecture helpers for virq/hwirq mapping and CPU target selection. Low-level exception code switches to per-CPU IRQ stacks.

State and persistence: Runtime state includes per-CPU stack pointers, lost interrupt counter, and IRQ distribution policy.

Dependencies and integration points: Depends on Linux IRQ core, cpumasks, radix-tree types, and platform interrupt controllers.

Risks: Stack pointers must be initialized before interrupt delivery. IRQ CPU selection affects affinity and load balancing. Legacy IRQ count must align with i8259 assumptions.

Test signals: SMP IRQ affinity/distribution, hardirq/softirq stack use, BookE critical/debug/mcheck interrupt stacks, virq mapping, and NMI backtrace IPI where configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq_work.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq_work.h

Purpose: Tells generic irq_work that PowerPC has an interrupt mechanism suitable for irq_work callbacks.

Important APIs, types, and functions: Implements `arch_irq_work_has_interrupt()` returning `true`.

Control flow: Generic irq_work uses this predicate to decide that queued work can be raised via an interrupt rather than relying only on timer/context fallback.

State and persistence: No state.

Dependencies and integration points: Integrates generic irq_work with PowerPC interrupt delivery.

Risks: If a platform cannot deliver the expected interrupt, irq_work latency assumptions would be wrong; the architecture declares support globally.

Test signals: Queue irq_work from process, interrupt, and NMI-like contexts; verify prompt execution on SMP and idle CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irqflags.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irqflags.h

Purpose: Provides the standard architecture IRQ flag include point by importing PowerPC `arch_local_save_flags()` and related helpers from `hw_irq.h`.

Important APIs, types, and functions: Includes `asm/hw_irq.h` for non-assembly code. It intentionally contains no additional logic.

Control flow: Generic code includes `irqflags.h`, then uses the arch-local IRQ save/restore/enable/disable functions defined by `hw_irq.h`.

State and persistence: No independent state.

Dependencies and integration points: Tight wrapper around `hw_irq.h` for generic Linux include conventions.

Risks: Any include-order or assembler mismatch would expose missing IRQ flag helpers. Behavior risk lives in `hw_irq.h`.

Test signals: Build generic locking/irq code, compile assembly and C users, and run IRQ save/restore nesting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/isa-bridge.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/isa-bridge.h

Purpose: Declares early ISA bridge discovery and helper logic for recognizing legacy IO-port virtual addresses on PPC64.

Important APIs, types, and functions: On PPC64 exposes `isa_bridge_find_early()`, `isa_bridge_init_non_pci()`, and `isa_vaddr_is_ioport()`. On PPC32, `isa_vaddr_is_ioport()` always returns false.

Control flow: Platform PCI or non-PCI setup identifies an ISA bridge early. Later code can test whether an `__iomem` address falls inside the reserved ISA I/O range.

State and persistence: Bridge state is held externally by PCI/ISA setup code.

Dependencies and integration points: Depends on `pci_controller`, OF device nodes, and ISA I/O base range constants. It integrates legacy port I/O with PPC64 PCI host bridge setup.

Risks: Incorrect early bridge detection can make `arch_has_dev_port()` and legacy I/O probing wrong. Address-range checks are PPC64-specific.

Test signals: PPC64 boot with PCI ISA bridge, non-PCI ISA initialization, legacy serial/i8042 probing, and PPC32 compile behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/isa-bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/jump_label.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/jump_label.h

Purpose: Implements PowerPC static key/jump-label architecture support for patching conditional branches at runtime.

Important APIs, types, and functions: Defines architecture jump-label instruction layout and helpers for emitting/evaluating branch or NOP sequences. It integrates with `arch_static_branch()` and `arch_static_branch_jump()` style static-key calls.

Control flow: Static key sites compile to patchable branch/NOP instructions. Runtime key changes patch the instruction stream so hot paths avoid a memory load when the key is disabled or enabled.

State and persistence: Static key state lives in generic jump-label structures and patched kernel text. No independent persistent state.

Dependencies and integration points: Depends on PowerPC branch encodings, text patching, and generic jump-label infrastructure.

Risks: Branch displacement and instruction cache synchronization are critical. Patching must be atomic enough for running CPUs. Incorrect sense of default branch can invert static key behavior.

Test signals: Static key enable/disable stress, module jump labels, SMP patching while executing, branch range tests, and objdump verification of generated sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kasan.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kasan.h

Purpose: Defines PowerPC KASAN shadow memory layout, early initialization hooks, and address conversion helpers.

Important APIs, types, and functions: Provides architecture KASAN constants/macros for shadow offsets and declares initialization helpers for mapping KASAN shadow regions, with config-dependent stubs when KASAN is disabled or unsupported.

Control flow: Early boot initializes shadow mappings before broad memory use. KASAN instrumentation converts kernel addresses to shadow addresses and checks poison state.

State and persistence: Shadow memory is runtime kernel memory mirroring poisoned/unpoisoned state. No disk persistence.

Dependencies and integration points: Depends on MMU/page-table setup, memory layout, and generic KASAN instrumentation.

Risks: Shadow offset or mapping mistakes can fault during early boot or hide memory bugs. Interaction with vmalloc/modules and radix/hash layouts is config-sensitive.

Test signals: KASAN boot, slab/stack/global out-of-bounds reports, vmalloc/module shadow coverage, early memory access, and builds with KASAN disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdebug.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdebug.h

Purpose: Defines PowerPC debug/trap notification values for die-chain users and low-level exception diagnostics.

Important APIs, types, and functions: Provides architecture-specific `DIE_*` event constants used by notifier callbacks around oops, breakpoint, single-step, and other trap conditions.

Control flow: Exception code raises die notifications with these event IDs; registered kernel debuggers, kprobes, and diagnostics decide whether to handle or pass through.

State and persistence: No state in the header. Notification state is in generic notifier chains.

Dependencies and integration points: Integrates with `die()`/notifier, kprobes, kgdb, xmon, and exception handling.

Risks: Event ID compatibility matters for notifier users. Mislabeling trap types can cause a debugger/probe to consume the wrong exception.

Test signals: Breakpoint, single-step, oops, kprobe, and kgdb notifier paths; verify notifier return behavior and event IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdump.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdump.h

Purpose: Declares PowerPC kdump/crash-dump helpers and constants for detecting and preparing crash kernels.

Important APIs, types, and functions: Provides crash dump macros and declarations such as kdump state checks, reserve/setup helpers, and architecture-specific crash memory handling when crash dump support is configured.

Control flow: Boot code reserves crash kernel memory, crash paths prepare CPU/register state and memory metadata, and kdump kernels identify that they are running as a dump capture kernel.

State and persistence: Runtime state includes reserved crash memory and crash flags. Dump output persistence is handled outside this header by kdump tooling.

Dependencies and integration points: Integrates kexec, crash reserve, FDT/elfcorehdr setup, RTAS/OPAL/platform crash code, and CPU stop/IPI flows.

Risks: Reserved ranges must not overlap normal allocations. Crash context is fragile, with interrupts/CPUs possibly broken. Hotplug memory/CPU changes must update dump metadata where supported.

Test signals: Crashkernel reservation, panic-to-kdump boot, elfcorehdr validity, CPU hotplug crash metadata, memory hotplug, and builds with crash dump disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kdump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec.h

Purpose: Defines PowerPC kexec and crash-kexec limits, architecture image metadata, file-load hooks, crash shutdown callbacks, and reset helpers.

Important APIs, types, and functions: Defines kexec source/control memory limits, page size, `KEXEC_ARCH`, state constants, `crash_shutdown_t`, `kimage_arch`, `kexec_copy_flush()`, file-loader ops/probes, FDT setup helpers, crash reserve APIs, `crash_setup_regs()`, crash hotplug hooks, `crashing_cpu`, crash IPI callbacks, shutdown register/unregister, `kdump_in_progress()`, `is_kdump_kernel()`, `update_cpus_node()`, and `reset_sprs()`.

Control flow: Normal kexec loads an image, prepares architecture metadata/FDT, copies/flushes control pages, shuts down devices/CPUs, and jumps to the new kernel. Crash kexec records registers, notifies crash handlers, stops secondary CPUs, and boots the capture kernel.

State and persistence: State includes loaded `kimage`, arch metadata, crash reservation, registered shutdown handlers, and global crash flags. It is runtime-only until a crash dump kernel writes data elsewhere.

Dependencies and integration points: Integrates generic kexec, crash dump, FDT, RTAS, Book3S 64 reset logic, CPU hotplug, and SMP crash IPI.

Risks: Address limits differ for 32-bit and 64-bit. Crash paths cannot rely on normal locking/device state. Handler registration order can affect shutdown. FDT memory ranges must exclude crash/reserved regions correctly.

Test signals: `kexec -l/-e`, `kexec_file_load`, panic crash dump, CPU/memory hotplug metadata, handler register/unregister, 32-bit and 64-bit builds, and Book3S reset SPR coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec_ranges.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec_ranges.h

Purpose: Declares helpers for building, sorting, adding, removing, and querying PowerPC memory ranges used by kexec and crash dump setup.

Important APIs, types, and functions: Defines `MEM_RANGE_CHUNK_SZ` and declares `sort_memory_ranges()`, `realloc_mem_ranges()`, `add_mem_range()`, `remove_mem_range()`, `get_exclude_memory_ranges()`, `get_reserved_memory_ranges()`, `get_crash_memory_ranges()`, and `get_usable_memory_ranges()`.

Control flow: Kexec code collects usable/reserved/excluded ranges, dynamically grows `struct crash_mem`, sorts/merges ranges, removes overlaps, and passes final ranges into FDT or elfcorehdr setup.

State and persistence: Range arrays are runtime allocations tied to image load/crash preparation.

Dependencies and integration points: Depends on `struct crash_mem` from crash/kexec infrastructure and platform memory discovery.

Risks: Range merging/removal bugs can include reserved memory or exclude usable memory. Allocation growth must preserve existing ranges on failure.

Test signals: Overlapping range add/remove, sorting with merge enabled/disabled, crashkernel overlap, hotplug memory ranges, and low-memory edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec_ranges.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/keylargo.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/keylargo.h

Purpose: Defines register offsets and feature-control/GPIO bit masks for Apple KeyLargo, Pangea, Intrepid, K2, and Shasta I/O controller families.

Important APIs, types, and functions: Provides offsets for MBCR/FCR/GPIO registers, GPIO lines for modem/sound/FireWire/timebase/Ethernet/CPU reset/PMU/media bay/AirPort, extensive feature bits for serial, IrDA, USB, audio/I2S, IDE, cardslot, MPIC, PLL/clock control, K2 GMAC/SATA/FireWire/UATA, and Shasta I2S. No functions are declared.

Control flow: Platform feature code reads/modifies controller registers using these constants to enable clocks, release resets, configure wake sources, and power subdevices.

State and persistence: State is controller MMIO register content and board wiring. Header has no runtime state.

Dependencies and integration points: Integrates old PowerMac feature control, MacIO, media bay, PMU, CPU bringup/reset, and suspend/resume paths.

Risks: Several bit positions are chip-revision-specific or shared under different names. Wrong masks can stop clocks, hold devices in reset, or break wakeup. One typo-like constant (`KEYLARGO_GPIO_OUTOUT_DATA`) is part of existing API spelling.

Test signals: Boot on KeyLargo/Pangea/Intrepid/K2/Shasta systems, USB/audio/IDE/SATA/GMAC enablement, GPIO read/write, CPU reset lines, timebase enable, and suspend wake-source configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/keylargo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kfence.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kfence.h

Purpose: Provides PowerPC KFENCE initialization and page-protection hooks, including early-disable state and ABI function-prefix handling.

Important APIs, types, and functions: Defines `ARCH_FUNC_PREFIX` for ELFv1, declares `kfence_early_init` and `kfence_disabled`, implements `disable_kfence()`, `arch_kfence_init_pool()`, `kfence_early_init_enabled()`, and `kfence_protect_page()` with PPC64 page-table protection support or permissive stubs.

Control flow: Early boot checks whether KFENCE should initialize, may disable it, initializes the guard-object pool, and toggles page protections around KFENCE objects to catch invalid accesses.

State and persistence: Runtime state includes global enable/disable booleans and KFENCE pool page protections.

Dependencies and integration points: Depends on generic KFENCE, `linux/mm.h`, PowerPC page table helpers, and PPC64 ABI conventions.

Risks: Early init must run after enough MMU setup but before allocator use. Page protection support differs between PPC64 and stubs. Incorrect disabling can hide KFENCE coverage or fault valid memory.

Test signals: KFENCE boot enabled/disabled, guard-page fault reports, PPC64 page protect/unprotect, ELFv1 symbol prefix builds, and non-PPC64 stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kgdb.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kgdb.h

Purpose: Defines PowerPC KGDB breakpoint instruction, register buffer sizing, and architecture breakpoint helper for kernel debugging.

Important APIs, types, and functions: Defines `BREAK_INSTR_SIZE`, `BUFMAX`, `BREAK_INSTR`, `arch_kgdb_breakpoint()`, `CACHE_FLUSH_IS_SAFE`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `NUMCRITREGBYTES`, and `MAXREG` with PPC64, PPC32, and e500 differences.

Control flow: KGDB inserts/executes the trap instruction, collects architecture register state into protocol buffers sized by these constants, and communicates with a remote debugger.

State and persistence: KGDB session state is external. The header defines register serialization sizes and emits a trap instruction when requested.

Dependencies and integration points: Integrates KGDB core, ptrace register numbering, exception handling, and cache flush/text patching safety.

Risks: Register buffer sizes must match GDB protocol expectations and architecture register sets. Wrong breakpoint instruction or cache flush assumptions can fail to stop or resume correctly.

Test signals: KGDB break-in, software breakpoint hit/resume, register read/write packets on PPC32/PPC64/e500, single-step if supported, and module/text breakpoint cache coherency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kprobes.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kprobes.h

Purpose: Defines PowerPC kprobes and optimized kprobes architecture data structures, instruction slot sizing, handlers, and trampoline symbols.

Important APIs, types, and functions: Defines `kprobe_opcode_t`, optprobe template symbols, instruction size constants, `flush_insn_slot()`, `kretprobe_blacklist_size`, `__kretprobe_trampoline()`, `arch_remove_kprobe()`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe_ctlblk`, `struct arch_optimized_insn`, and handler prototypes/stubs.

Control flow: Kprobes copies/analyzes the target instruction, installs a breakpoint, emulates or single-steps as needed, tracks nested probes in per-CPU control blocks, and optimized probes patch a branch to an out-of-line template.

State and persistence: Probe state lives in kprobe structs, per-CPU control blocks, instruction slots, and patched kernel text. No disk persistence.

Dependencies and integration points: Depends on generic kprobes, PowerPC instruction analysis, text patching, modules, ptrace regs, and optprobe assembly templates.

Risks: PowerPC instruction emulation and prefixed instruction handling must be correct. Optimized probe branch length is only one instruction. Probes must not recurse into unsafe handlers and text patching must synchronize I-cache.

Test signals: Basic kprobe/kretprobe hits, nested probes, fault handling, optimized probe enable/disable, module probes, blacklist behavior, and prefixed-instruction targets where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kup.h -->
## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kup.h

Purpose: Selects and declares Kernel Userspace Access/Execution Protection (KUAP/KUEP) support for PowerPC, providing common masks, setup APIs, and config-dependent stubs.

Important APIs, types, and functions: Defines `KUAP_READ`, `KUAP_WRITE`, `KUAP_READ_WRITE`, declares `kuap_is_disabled()`, includes MMU-family-specific KUP headers, exposes `disable_kuep`, `disable_kuap`, `setup_kup()`, `setup_kuep()`, `setup_kuap()`, and lock/save/assert helper fallbacks depending on architecture implementation macros.

Control flow: Boot setup calls KUP/KUEP initialization, architecture-specific code locks or unlocks user access around copy-to/from-user, and assertion helpers validate that kernel access to userspace is disabled when expected.

State and persistence: Runtime state includes boot disable flags and MMU/register state controlling user access/execution. No persistent storage.

Dependencies and integration points: Integrates uaccess, page table permissions, Book3S 64, Book3S 32, BookE, and 8xx implementations.

Risks: Missing locks around uaccess can leave userspace accessible to kernel code. Overly strict locking can break legitimate copy routines. Config stubs must preserve generic call semantics without silently weakening enabled platforms.

Test signals: Uaccess with KUAP enabled, deliberate missing unlock/lock assertions, KUEP execute-from-user prevention, boot parameters disabling protections, and builds for Book3S64/Book3S32/BookE/8xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kup.h -->
