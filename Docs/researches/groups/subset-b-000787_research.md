# Research: subset-b-000787

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu.c

## Purpose
Implements software guest TLB management for Freescale BookE/e500 KVM, including guest TLB search, MAS register emulation, userspace-visible TLB configuration, translation, and lifecycle allocation. It owns the guest-facing TLB arrays and calls host-shadow helpers in `e500_mmu_host.c` whenever guest TLB entries need to be mapped or invalidated on the real hardware.

## Important APIs, Types, And Functions
Key entry points include `kvmppc_e500_emul_tlbivax()`, `kvmppc_e500_emul_tlbilx()`, `kvmppc_e500_emul_tlbre()`, `kvmppc_e500_emul_tlbsx()`, `kvmppc_e500_emul_tlbwe()`, `kvmppc_core_vcpu_translate()`, `kvmppc_mmu_itlb_index()`, `kvmppc_mmu_dtlb_index()`, `kvmppc_mmu_xlate()`, `kvm_vcpu_ioctl_config_tlb()`, `kvm_vcpu_ioctl_dirty_tlb()`, `kvmppc_e500_tlb_init()`, and `kvmppc_e500_tlb_uninit()`. The file manipulates `struct kvmppc_vcpu_e500`, `struct kvm_book3e_206_tlb_entry`, `struct kvm_book3e_206_tlb_params`, and per-entry `struct tlbe_priv` storage allocated alongside the guest TLB arrays.

## Control Flow
Guest TLB lookup starts in `kvmppc_e500_tlb_index()`, which searches TLB0 by set/way and TLB1 by full entry range after checking the cached TLB1 effective-address min/max. Miss handling fills MAS0/MAS1/MAS2/MAS6 via `kvmppc_e500_deliver_tlb_miss()`. Emulated invalidate instructions clear matching guest entries and either flush all host shadow entries or call `inval_gtlbe_on_host()` for targeted teardown. `tlbwe` writes MAS values into the guest TLB array, invalidates any old host mapping, updates TLB1 range caches, and pre-maps host-safe entries through `kvmppc_mmu_map()`.

## State And Persistence
State lives in the vCPU: guest TLB arrays (`gtlb_arch`), TLB geometry (`gtlb_params`, `gtlb_offset`), next-victim state (`gtlb_nv`), TLB1 min/max search cache, private host shadow metadata, and optional userspace-pinned shared TLB pages. `kvm_vcpu_ioctl_config_tlb()` can replace the default kernel-owned arrays with userspace-backed pages via `get_user_pages_fast()` and `vmap()`. `free_gtlb()` flushes host mappings, releases private arrays, marks shared pages dirty, and drops page references.

## Dependencies And Integration Points
Depends on BookE MAS helpers/macros from e500 headers, host-shadow hooks from `e500_mmu_host.h`, KVM SRCU, usercopy, GUP/vmap, and tracepoints from `trace_booke.h`. Integrated with generic register ioctls via `kvmppc_get_one_reg_e500_tlb()`/`kvmppc_set_one_reg_e500_tlb()` and with e500mc setup through `kvmppc_e500_tlb_init()`.

## Risks
The correctness boundary is tight around guest-provided TLB geometry, pinned userspace pages, and TLB1 range caching. Bad geometry is rejected, but shared TLB mappings still rely on userspace arrays remaining valid until reconfiguration or teardown. Host shadow invalidation is deliberately conservative in some cases, which is safe but can be expensive. `tlbwe` pre-mapping is protected by SRCU but still depends on `tlbe_is_host_safe()` and host-shadow code honoring MMU notifier races.

## Test Signals
No direct tests in this subset target e500 TLB behavior. Useful signals are KVM selftests or QEMU BookE/e500 guests exercising `KVM_CAP_SW_TLB`, TLB invalidation instructions, migration/register save-restore of MAS/TLB state, and tracepoints `kvm_booke206_gtlb_write` plus host shadow write/release events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.c

## Purpose
Provides the host-side shadow TLB implementation for e500 KVM. It translates guest TLB entries to real host TLB entries, installs them with MAS registers and `tlbwe`, tracks guest-to-host TLB1 mappings, invalidates shadow entries, handles the magic page on e500v2, and supplies MMU notifier callbacks.

## Important APIs, Types, And Functions
Externally used functions are `inval_gtlbe_on_host()`, `kvmppc_core_flush_tlb()`, `kvmppc_mmu_map()`, `kvmppc_load_last_inst()`, `kvm_unmap_gfn_range()`, `kvm_age_gfn()`, `kvm_test_age_gfn()`, `e500_mmu_host_init()`, and `e500_mmu_host_uninit()`. Core internals include `__write_host_tlbe()`, `get_host_mas0()`, `write_stlbe()`, `kvmppc_e500_shadow_map()`, `kvmppc_e500_tlb0_map()`, and `kvmppc_e500_tlb1_map()`.

## Control Flow
`kvmppc_mmu_map()` dispatches by guest TLB selection. TLB0 entries map one page through host TLB0, reusing existing private metadata if present. TLB1 entries call `kvmppc_e500_shadow_map()`, which resolves GFN to HVA/PFN under the KVM MMU invalidation sequence, inspects Linux PTE WIMG bits, chooses a shadow page size bounded by host page size and memslot alignment, records private PFN/permission metadata, flushes icache, and emits a shadow TLBE. Large safe mappings are placed into reserved host TLB1 slots with reverse maps; 4 KiB fallbacks use host TLB0.

## State And Persistence
Global host geometry is cached in `host_tlb_params`. Per-vCPU persistent state includes `gtlb_priv`, `g2h_tlb1_map`, `h2g_tlb1_rmap`, and `host_tlb1_nv`. Shadow entries live in hardware TLBs and are reconstructed as needed. `kvmppc_core_flush_tlb()` invalidates all host shadow TLB state and clears metadata. PFN/page references are released through `kvm_release_faultin_page()` after shadow setup.

## Dependencies And Integration Points
Depends on low-level PowerPC MAS/TLB instructions, KVM memslot and MMU notifier infrastructure, Linux PTE walking via `find_linux_pte()`, page fault-in helpers, e500 TLB helper macros, and BookE tracepoints. It is called by `e500_mmu.c` for pre-maps and invalidations and by instruction emulation paths that need to fetch the trapped instruction in BookE HV mode.

## Risks
Hardware TLB manipulation requires interrupts/preemption control and careful MAS5/MAS8 cleanup. The GFN notifier path is coarse: unmap requests return true to force global shadow invalidation, while age/test-age do nothing, trading performance for simplicity. Large-page shadow selection has subtle alignment and memslot-boundary requirements. `kvmppc_load_last_inst()` refuses non-RAM or execute-disallowed mappings, so failures may cause retry loops if guests continually fault on evicted or unsafe instruction pages.

## Test Signals
No local unit tests exist. Regression signals include successful e500 guest boot, MMU notifier stress with memory hot-unplug/memslot updates, tracepoints `kvm_booke206_stlb_write` and `kvm_booke206_ref_release`, and negative tests around execute permission, storage attributes, and non-RAM instruction fetches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.h

## Purpose
Declares the small host-shadow MMU interface consumed by guest-side e500 MMU code and e500 vCPU setup. It is the boundary between software guest TLB emulation and hardware host TLB shadowing.

## Important APIs, Types, And Functions
The header exposes `inval_gtlbe_on_host(struct kvmppc_vcpu_e500 *, int tlbsel, int esel)`, `e500_mmu_host_init(struct kvmppc_vcpu_e500 *)`, and `e500_mmu_host_uninit(struct kvmppc_vcpu_e500 *)`. It relies on `struct kvmppc_vcpu_e500` being declared by including e500-specific headers before or around this header.

## Control Flow
`e500_mmu.c` calls `inval_gtlbe_on_host()` before invalidating or overwriting guest TLB entries that may have host shadow mappings. `e500mc.c`/e500 setup indirectly call `e500_mmu_host_init()` during TLB initialization and `e500_mmu_host_uninit()` during teardown.

## State And Persistence
The header owns no state. Its implementation allocates per-vCPU reverse-map state and reads global host TLB geometry.

## Dependencies And Integration Points
Included by both `e500_mmu.c` and `e500_mmu_host.c`; it prevents either side from reaching through implementation details. It forms part of the BookE/e500 KVM private interface rather than a userspace ABI.

## Risks
Because only targeted invalidation and lifecycle hooks are declared here, callers must still separately call broader flush APIs such as `kvmppc_core_flush_tlb()` when they invalidate all software TLB state. Incorrect call ordering around guest TLB writes can leave stale host shadow mappings.

## Test Signals
Build coverage catches signature drift. Runtime evidence comes from e500 TLB invalidation tests or guest workloads that overwrite TLB entries and verify stale translations are not observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_mmu_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500mc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500mc.c

## Purpose
Registers and implements the KVM PR backend for e500mc/e5500/e6500 BookE processors. It handles vCPU load/put hardware register context, LPID allocation policy, interrupt doorbells, hardware TLB invalidation primitives, e500mc special registers, and the `kvmppc_ops` table that connects common KVM PowerPC code to e500-specific behavior.

## Important APIs, Types, And Functions
Important functions include `kvmppc_set_pending_interrupt()`, `kvmppc_e500_tlbil_one()`, `kvmppc_e500_tlbil_all()`, `kvmppc_set_pid()`, `kvmppc_core_vcpu_load_e500mc()`, `kvmppc_core_vcpu_put_e500mc()`, `kvmppc_core_vcpu_setup()`, e500mc get/set sregs and one-reg helpers, `kvmppc_core_vcpu_create_e500mc()`, `kvmppc_core_vcpu_free_e500mc()`, `kvmppc_core_init_vm_e500mc()`, and `kvmppc_core_destroy_vm_e500mc()`.

## Control Flow
Module init validates processor compatibility, initializes BookE support, sizes the LPID allocator, calls `kvm_init()`, and publishes `kvmppc_pr_ops`. VM creation allocates an LPID, doubling allocation spacing on dual-threaded cores. vCPU creation initializes e500 TLB state and allocates the shared page. vCPU load writes LPID, EPCR, GPIR, MSRP, EPLC/EPSC, guest IVPR/IVORs, guest SPRGs/SRRs, EPR, DAR, and ESR to hardware SPRs; it flushes LPID-scoped TLBs when moving between physical cores or vCPUs. vCPU put snapshots the corresponding guest-visible SPR state back into memory.

## State And Persistence
Persistent state spans VM LPID (`kvm->arch.lpid`), vCPU shared page, e500 TLB state, cached SVR/HID0/MCAR, shadow EPCR/MSRP, old PIR, per-CPU `last_vcpu_of_lpid`, and interrupt identity fields. Module exit unregisters PR ops and BookE support; VM/vCPU teardown frees LPIDs, shared pages, and e500 TLB resources.

## Dependencies And Integration Points
Depends on BookE/e500 headers, low-level SPR/MAS instructions, doorbell support, `kvmppc_booke_*` helpers, `e500_mmu.c`, timing debugfs, and common PowerPC KVM dispatch in `powerpc.c`. MPIC/external interrupt paths can call into this backend through common IRQ queueing.

## Risks
Incorrect LPID or stale hardware TLB management can leak translations between vCPUs or VMs. Processor compatibility is string-based and feature-gated, especially for e6500 AltiVec. The vCPU load/put path must remain synchronized with the hardware guest SPR set; missing registers can corrupt guest exception return state. The file also contains a spelling error in a comment only; behavior is unaffected.

## Test Signals
Signals include successful module load only on supported e500mc/e5500/e6500 hosts, e500 guest boot, migration/register save-restore of sregs/one-regs, interrupt delivery through guest doorbells, and TLB flush correctness when scheduling vCPUs across physical CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate.c

## Purpose
Implements generic PowerPC instruction emulation used by KVM when a guest traps on privileged or special instructions. It handles decrementer programming, common SPR reads/writes, traps, KVM software breakpoints, and dispatches unknown core-specific instructions to the active backend.

## Important APIs, Types, And Functions
Exports `kvmppc_emulate_instruction()`. Other important functions are `kvmppc_emulate_dec()`, `kvmppc_get_dec()`, `kvmppc_emulate_mtspr()`, and `kvmppc_emulate_mfspr()`. It uses `enum emulation_result`, `ppc_inst_t`, disassembly helpers such as `get_op()`, `get_xop()`, `get_rs()`, `get_rt()`, and `get_sprn()`, and backend callbacks `emulate_mtspr`, `emulate_mfspr`, and `emulate_op`.

## Control Flow
`kvmppc_emulate_instruction()` fetches the trapped instruction with `kvmppc_get_last_inst()`, decodes primary opcode and extended opcode, and first handles generic traps, `mfspr`, `mtspr`, `tlbsync`, and the KVM software breakpoint opcode. SPR emulation reads/writes SRR, PVR, PIR, timebase/decrementer, and SPRG registers locally; unrecognized SPRs are delegated to backend ops. If generic decoding fails, the backend `emulate_op` gets a final chance. Successful emulation advances PC by 4.

## State And Persistence
Touches vCPU architectural state: GPRs, PC, SRR, SPRGs, decrementer values, hrtimer state, `last_exit_type`, and debug exit fields. `kvmppc_emulate_dec()` stores `dec`, starts/cancels the decrementer hrtimer, and records the timebase at programming time. No global persistent state is created.

## Dependencies And Integration Points
Depends on KVM host structures, PowerPC disassembly/opcode helpers, timebase conversion, Book3S/BookE exception queue helpers, `timing.h`, and tracepoint `kvm_ppc_instr`. It is called from backend run loops after instruction-related exits.

## Risks
The emulator only covers a small generic subset; unsupported instructions become backend responsibilities or inject errors. PC advancement is fixed at 4 and the source comment notes prefixed instructions would need `ppc_inst_len()`. Decrementer behavior differs between BookE and Book3S, and wrong interrupt dequeue/requeue behavior can cause timer loss or storms.

## Test Signals
Tracepoint `kvm_ppc_instr` shows decoded emulation results. Useful tests include guests executing SPR accesses, decrementer programming, trap instructions, KVM breakpoints producing `KVM_EXIT_DEBUG`, and backend-specific fallback instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate_loadstore.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate_loadstore.c

## Purpose
Emulates load/store instructions that trap on MMIO or cache-inhibited mappings. It decodes instructions through the PowerPC single-step analyzer and routes scalar, floating-point, VMX, VSX, and cache operation cases to common MMIO handlers in `powerpc.c`.

## Important APIs, Types, And Functions
Exports `kvmppc_emulate_loadstore(struct kvm_vcpu *)`. Internal feature checks are `kvmppc_check_fp_disabled()`, `kvmppc_check_vsx_disabled()`, and `kvmppc_check_altivec_disabled()`. It uses `struct instruction_op`, instruction type bits such as `LOAD`, `STORE`, `LOAD_FP`, `LOAD_VMX`, `LOAD_VSX`, `STORE_FP`, `STORE_VMX`, `STORE_VSX`, `CACHEOP`, flags like `SIGNEXT`, `BYTEREV`, `UPDATE`, `FPCONV`, and VSX flags.

## Control Flow
The function fetches the last instruction, clears all MMIO copy/extension bookkeeping, mirrors current MSR into `vcpu->arch.regs`, and calls `analyse_instr()`. Scalar loads/stores call `kvmppc_handle_load()`, `kvmppc_handle_loads()`, or `kvmppc_handle_store()`. FPU/VMX/VSX paths first inject unavailable exceptions if the relevant MSR enable bit is off, configure copy type, offsets, sign/precision conversion, and then call vector-aware handlers. Update-form instructions write the effective address back to the update register after successful decode.

## State And Persistence
Uses transient vCPU fields including `mmio_vsx_copy_nums`, `mmio_vsx_offset`, `mmio_vmx_copy_nums`, `mmio_vmx_offset`, `mmio_copy_type`, `mmio_sp64_extend`, `mmio_sign_extend`, `mmio_host_swabbed`, `vaddr_accessed`, `paddr_accessed`, and `mmio_is_write`. It may flush guest FP/VMX/VSX extension state via backend `giveup_ext()` before stores.

## Dependencies And Integration Points
Depends on `asm/sstep.h`, KVM MMIO handlers in `powerpc.c`, exception queue helpers, MSR feature definitions, and tracepoint `kvm_ppc_instr`. It is called by `kvmppc_emulate_mmio()` in the common PowerPC KVM layer.

## Risks
Unsupported or incorrectly decoded load/store forms return `EMULATE_FAIL`, which the caller converts into data-storage or program exceptions. Vector and VSX accesses are alignment-sensitive and split into repeated MMIO operations; partial completion state must be resumed correctly by `kvm_arch_vcpu_ioctl_run()`. Endianness and floating-point conversion flags are subtle and architecture-dependent.

## Test Signals
Good coverage would include scalar byte-reversed and sign-extending MMIO, update-form loads/stores, FPU unavailable injection, VMX/VSX split loads/stores, and cache operations returning done without MMIO. Tracepoint output should identify emulated instruction and result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/emulate_loadstore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/fpu.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/fpu.S

## Purpose
Provides assembly helper routines that execute PowerPC floating-point instructions in kernel context for KVM paired-single/FPU emulation. The helpers load caller-provided FPSCR/CR and operands, execute one native FPU instruction, store the result, and return updated FPSCR/CR state.

## Important APIs, Types, And Functions
The file generates many exported symbols through macros: single-precision `fps_*` helpers, double-precision `fpd_*` helpers, comparison helpers that update CR, and conversion helpers `kvm_cvt_fd` and `kvm_cvt_df`. Local helpers `fpd_load_none`, `fpd_load_one`, `fpd_load_two`, `fpd_load_three`, and `fpd_return` consolidate double-precision setup/teardown.

## Control Flow
Single-precision macros load FPSCR from `r3`, operands from `r5`/`r6`/`r7`, run the instruction, store the single result at `r4`, save FPSCR back to `r3`, and return. Double-precision macros save LR, branch to the appropriate load helper, execute the instruction with record form where needed, and branch to `fpd_return`, which saves result, FPSCR, and CR. Comparison macros load CR explicitly and only update FPSCR/CR outputs. Conversion helpers directly use `lfs`/`stfd` and `lfd`/`stfs`.

## State And Persistence
No persistent state is allocated. The visible state is entirely through memory pointers passed in registers for FPSCR, CR, results, and operands. The code uses FPR0-FPR3 and GPR scratch registers according to the PowerPC ABI expectations of its callers.

## Dependencies And Integration Points
Depends on PowerPC assembly macros, linkage definitions, FPU instructions, FPSCR manipulation via `MTFSF_L`, and KVM FPU emulation callers elsewhere in the PowerPC KVM tree. It is build-time architecture-specific and not directly called from userspace.

## Risks
Calling convention mismatches are high impact because the interface is raw register/pointer based. The helpers assume kernel code has enabled and protected FPU use before entry. Record-form double operations update CR, so wrong CR pointer handling would corrupt guest-visible condition state. Host endianness and alignment assumptions are inherited from native load/store instructions.

## Test Signals
Coverage should come from paired-single/FPU emulation tests comparing guest results and FPSCR/CR side effects against hardware. Build tests catch symbol/linkage regressions. Runtime stress should include exceptional FPSCR conditions, comparisons, fused multiply-add variants, and conversion helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/guest-state-buffer.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/guest-state-buffer.c

## Purpose
Implements guest state buffer construction, parsing, bitmap iteration, and message send/receive helpers for PowerPC nested/pseries guest state exchange. It serializes typed guest-state elements into hypervisor buffers and wraps `H_GUEST_SET_STATE` / `H_GUEST_GET_STATE` hcalls.

## Important APIs, Types, And Functions
Exports allocation and buffer helpers `kvmppc_gsb_new()`, `kvmppc_gsb_free()`, `kvmppc_gsb_put()`, element helpers `__kvmppc_gse_put()`, `kvmppc_gse_parse()`, ID metadata helpers `kvmppc_gsid_flags()`, `kvmppc_gsid_size()`, `kvmppc_gsid_mask()`, parser helpers `kvmppc_gsp_insert()`, `kvmppc_gsp_lookup()`, bitmap helpers `kvmppc_gsbm_set()`, `kvmppc_gsbm_clear()`, `kvmppc_gsbm_test()`, `kvmppc_gsbm_next()`, message helpers `kvmppc_gsm_init()`, `kvmppc_gsm_new()`, `kvmppc_gsm_size()`, `kvmppc_gsm_free()`, `kvmppc_gsm_fill_info()`, `kvmppc_gsm_refresh_info()`, and hcall wrappers `kvmppc_gsb_send()`/`kvmppc_gsb_recv()`.

## Control Flow
Buffers are allocated with power-of-two capacity and start with a big-endian header element count. Adding an element validates the ID's expected size, appends a `struct kvmppc_gs_elem`, copies data, and increments the header count. Parsing iterates serialized elements, validates lengths against ID metadata, and builds a flattened-ID lookup table plus iterator bitmap. Message helpers delegate sizing/fill/refresh to caller-provided `struct kvmppc_gs_msg_ops`. Send/receive translate internal flags to hcall flags and pass the physical buffer address to firmware.

## State And Persistence
State is heap-allocated per `struct kvmppc_gs_buff` and `struct kvmppc_gs_msg`. Parser state stores pointers into an existing buffer, so it is valid only while that buffer remains alive and unchanged. The file encodes class/type/mask knowledge in static switch logic and a size table.

## Dependencies And Integration Points
Depends on `asm/guest-state-buffer.h`, hcall definitions/wrappers, Linux allocation helpers, endian helpers, bit operations, and exported symbols for nested/pseries KVM code. It is directly tested by `test-guest-state-buffer.c`.

## Risks
`kvmppc_gsb_put()` intentionally does not check capacity; callers should use higher-level put functions that validate size first. Parser lookup aliases duplicate IDs to the last parsed element. `kvmppc_gsm_refresh_info()` checks `fill_info` instead of `refresh_info` before calling refresh, which looks suspicious and should be reviewed. Buffers passed to hcalls must be physically addressable and sized for firmware expectations.

## Test Signals
KUnit tests cover buffer allocation, element insertion, parser lookup, bitmap iteration, message fill/refresh, and host-wide counter retrieval. Additional tests should cover invalid IDs, invalid lengths, duplicate elements, near-capacity insertion, missing `refresh_info`, and hcall error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/guest-state-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/mpic.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/mpic.c

## Purpose
Implements an in-kernel Freescale/OpenPIC MPIC device model for PowerPC KVM. It provides MMIO register emulation, interrupt source/destination state, IPI/timer/MSI support, KVM device attributes, vCPU connection, and IRQ routing callbacks.

## Important APIs, Types, And Functions
Main exported/integrated functions are `kvm_mpic_ops`, `kvmppc_mpic_connect_vcpu()`, `kvmppc_mpic_disconnect_vcpu()`, `kvmppc_mpic_set_epr()`, `kvm_set_msi()`, and `kvm_set_routing_entry()`. Important types are `struct openpic`, `struct irq_source`, `struct irq_dest`, `struct irq_queue`, `struct mem_reg`, and `struct fsl_mpic_info`. Core internals include `openpic_set_irq()`, `openpic_update_irq()`, `IRQ_local_pipe()`, `openpic_iack()`, `openpic_cpu_write_internal()`, and the MMIO bank read/write handlers.

## Control Flow
Device creation initializes register banks, model-specific flags for FSL MPIC 2.0 or 4.2, default routing, and reset state, then publishes `kvm->arch.mpic`. Userspace sets the MMIO base via device attributes, causing `map_mmio()`/`unmap_mmio()` under `slots_lock`. Guest MMIO accesses are routed through `kvm_mpic_read()`/`kvm_mpic_write()` to bank handlers. IRQ assertion updates source pending/activity, masks, priority, destination mode, and either raises/lower KVM external interrupts or tracks non-INT output counters. IACK moves raised interrupts to servicing; EOI clears servicing and notifies acked IRQ listeners.

## State And Persistence
All MPIC state lives in one spinlock-protected `struct openpic`: global registers, source IVPR/IDR/ILR-derived output/destination state, per-CPU CTPR/raised/servicing queues, timer registers, MSI registers, routing base, model flags, and connected vCPU pointers. Destruction disconnects from the VM and frees the device model.

## Dependencies And Integration Points
Depends on KVM device API, MMIO bus, irqfd routing, `kvm_vcpu_ioctl_interrupt()`, `kvm_notify_acked_irq()`, PowerPC EPR helpers, and userspace device attributes (`KVM_DEV_MPIC_*`). It integrates with common `powerpc.c` capability and vCPU enable-cap handling.

## Risks
The model supports only one MPIC per VM and uses a single spinlock for all state. Non-INT outputs are mostly TODO and only INT output is actively queued/dequeued. Some register behavior is simplified, summary registers are placeholders, and return values from routing callbacks are intentionally not meaningful. Lock dropping around EOI notification requires care because state can change before the lock is reacquired.

## Test Signals
Useful tests include KVM device creation for both MPIC models, base-address alignment, register get/set attributes, IRQ active attributes, MMIO IACK/EOI ordering, IPI delivery to multiple vCPUs, MSI bank clear-on-read, irqfd routing, and EPR proxy mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/mpic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/powerpc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/powerpc.c

## Purpose
Provides the common PowerPC KVM architecture layer. It selects HV vs PR backends, implements vCPU entry preparation, paravirtual hypercalls, MMIO emulation completion, arch ioctls, capability reporting, memory-slot hooks, vCPU lifecycle hooks, interrupt controller plumbing, LPID allocation, and debugfs dispatch.

## Important APIs, Types, And Functions
Key functions include `kvmppc_prepare_to_enter()`, `kvmppc_kvm_pv()`, `kvmppc_sanity_check()`, `kvmppc_emulate_mmio()`, `kvmppc_st()`, `kvmppc_ld()`, `kvm_arch_init_vm()`, `kvm_arch_destroy_vm()`, `kvm_vm_ioctl_check_extension()`, `kvm_arch_vcpu_create()`, `kvm_arch_vcpu_destroy()`, `kvm_arch_vcpu_ioctl_run()`, `kvm_vcpu_ioctl_interrupt()`, `kvm_arch_vcpu_ioctl()`, `kvm_arch_vm_ioctl()`, `kvm_vm_ioctl_enable_cap()`, `kvm_vm_ioctl_irq_line()`, `kvmppc_alloc_lpid()`, `kvmppc_free_lpid()`, and `kvmppc_init_lpid()`. It exports backend pointers `kvmppc_hv_ops` and `kvmppc_pr_ops`.

## Control Flow
VM creation picks a backend from requested VM type and loaded modules, gets the module reference, and calls backend init. Guest entry preparation loops with hard IRQs disabled, handling reschedule, signals, pending requests, backend readiness, and `guest_enter_irqoff()`. Run ioctl resumes outstanding userspace MMIO/OSI/hcall/EPR state, activates signal masks, runs the backend, and normalizes resume codes. MMIO load/store helpers first try in-kernel MMIO buses, otherwise set up `KVM_EXIT_MMIO`; completion writes values back into GPR/FPR/QPR/VSX/VMX/nested GPR targets with endian and precision handling.

## State And Persistence
Persistent state includes VM backend ops pointer, module reference, LPID allocator state, vCPU decrementer hrtimer, wait object, pending MMIO continuation fields, extension copy counters, interrupt-controller pointers, magic page addresses, paravirtual flags, and enabled capabilities. Memory-slot operations delegate to backend hooks.

## Dependencies And Integration Points
Depends on the generic KVM core, PowerPC backend ops, MMIO bus, irqfd/irqbypass, XICS/XIVE/MPIC optional backends, pseries hcalls, Open Firmware CPU-characteristic discovery, timing helpers, and tracepoint creation for `trace.h`.

## Risks
The file is a high-blast-radius ABI surface. Capability answers vary by loaded backend, CPU features, platform firmware, and config options. MMIO continuation across userspace exits is subtle for VSX/VMX repeated transfers. Endian conversion, magic page mapping, and nested GPR writes are fragile. Backend module references and vCPU lifecycle ordering must remain balanced to avoid use-after-free or leaked modules.

## Test Signals
Regression signals include KVM capability selftests, VM type selection, vCPU run with signals/requests, scalar and vector MMIO exits/resume, PV info/hypercall behavior, one-reg get/set for vector registers, interrupt controller enable caps, LPID allocation exhaustion, and debugfs creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/test-guest-state-buffer.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/test-guest-state-buffer.c

## Purpose
Defines KUnit tests for the guest state buffer APIs implemented in `guest-state-buffer.c`. It validates buffer allocation, element serialization, parser lookup, bitmap flatten/unflatten iteration, message callback use, and host-wide counter retrieval through `H_GUEST_GET_STATE`.

## Important APIs, Types, And Functions
Test cases include `test_creating_buffer()`, `test_adding_element()`, `test_gs_parsing()`, `test_gs_bitmap()`, `test_gs_msg()`, `test_gs_hostwide_msg()`, and `test_gs_hostwide_counters()`. It defines mock message data structs and two `struct kvmppc_gs_msg_ops` implementations for normal and host-wide messages.

## Control Flow
Tests allocate buffers/messages, call public helpers such as `kvmppc_gsb_new()`, `__kvmppc_gse_put()`, typed put/get wrappers, `kvmppc_gse_parse()`, bitmap set/clear/test/iterate macros, `kvmppc_gsm_fill_info()`, and `kvmppc_gsm_refresh_info()`, then assert serialized IDs, lengths, and recovered values. The host-wide counter test skips unless running as a KVM-HV pseries guest, then sends a real host-wide get-state hcall and parses returned counters.

## State And Persistence
All state is test-local heap or stack data, except the host-wide counter test depends on the actual hypervisor environment. Some tests allocate `gsb` without freeing it on all paths (`test_gs_msg()` and `test_gs_hostwide_msg()` free the message but not the buffer), which is acceptable for short KUnit execution but worth noting if leak detection is strict.

## Dependencies And Integration Points
Depends on KUnit, guest state buffer headers, KVM PowerPC helpers, and optionally a pseries KVM-HV environment. The test suite is registered with `kunit_test_suites()`.

## Risks
The mock `test1_fill_info()` calls `kvmppc_gse_put_proc_table()` with `KVMPPC_GSID_PARTITION_TABLE`, which appears inconsistent with the inclusion check for `KVMPPC_GSID_PROCESS_TABLE`; the test still passes because it only refreshes GPR/CR values. The environment-dependent host-wide test can be skipped in most CI, leaving hcall behavior lightly covered.

## Test Signals
The suite name is `guest_state_buffer_test`. Passing tests indicate basic buffer encoding/parsing and bitmap mapping remain intact. Additional negative tests for bad sizes, missing callbacks, capacity errors, and duplicate IDs would improve confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/test-guest-state-buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.c

## Purpose
Implements optional per-vCPU exit timing statistics for PowerPC KVM when `CONFIG_KVM_EXIT_TIMING` is enabled. It records time spent in host exit handling and guest execution by exit type and exposes a resettable debugfs file.

## Important APIs, Types, And Functions
Public functions are `kvmppc_init_timing_stats()`, `kvmppc_update_timing_stats()`, and `kvmppc_create_vcpu_debugfs_e500()`. Internals include `add_exit_timing()`, `kvmppc_exit_timing_show()`, `kvmppc_exit_timing_write()`, `kvmppc_exit_timing_open()`, the `kvmppc_exit_timing_fops` file operations, and `kvm_exit_names[]`.

## Control Flow
Initialization clears counters, sum, squared sum, min, max, and timestamp fields under `exit_timing_lock`. Each update shifts the last exit timestamp, skips incomplete cycles, adds the duration from prior exit to guest enter to the recorded exit type, and adds guest runtime to the `TIMEINGUEST` bucket. Debugfs `show` converts timebase ticks to microseconds and prints a table; writing a single `c` clears stats.

## State And Persistence
All counters live in `vcpu->arch`: last exit type, count per type, min/max/sum/squared-sum durations, last exit, exit timestamp, and last enter timestamp. The debugfs file persists for the vCPU lifetime.

## Dependencies And Integration Points
Depends on `timing.h`, KVM vCPU arch fields, PowerPC timebase conversion, debugfs, seq_file, and Linux file operations. e500mc exposes it through the backend `create_vcpu_debugfs` hook.

## Risks
Squared duration accumulation can overflow; the code logs wrap detection but continues. Min values initialize to `0xffffffff`, which may be awkward if durations exceed that before first update. Debugfs write validation only accepts one byte, so newline-containing writes may fail. Locking protects stats but debugfs readers still report live, changing counters.

## Test Signals
Runtime signals are presence of `timing` debugfs files, readable tables with named exit buckets, and successful clear via `c`. Stress tests should exercise frequent exits and confirm counters grow without lockdep warnings or crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.h

## Purpose
Provides the compile-time interface for PowerPC KVM exit timing and always-on lightweight exit accounting. When timing is disabled, it supplies no-op stubs while preserving call sites.

## Important APIs, Types, And Functions
Declares or defines `kvmppc_init_timing_stats()`, `kvmppc_update_timing_stats()`, `kvmppc_create_vcpu_debugfs_e500()`, `kvmppc_set_exit_type()`, `kvmppc_account_exit_stat()`, and `kvmppc_account_exit()`. `kvmppc_account_exit_stat()` increments `vcpu->stat` fields for constants such as `MMIO_EXITS`, `DEC_EXITS`, `EXT_INTR_EXITS`, TLB miss exits, doorbells, and emulated instruction exits.

## Control Flow
With `CONFIG_KVM_EXIT_TIMING`, callers set `last_exit_type` and timing.c records durations. Without it, timing calls compile away. `kvmppc_account_exit()` always sets the timing type if available and increments the matching statistics field through a switch that requires the type to be a compile-time constant.

## State And Persistence
This header updates only vCPU stat and optional timing fields. It does not allocate state.

## Dependencies And Integration Points
Included by common emulation, MMU, e500mc, and timing implementation files. It depends on `linux/kvm_host.h` and exit-type/stat definitions in the PowerPC KVM arch structures.

## Risks
The `BUILD_BUG_ON(!__builtin_constant_p(type))` requirement prevents dynamic exit-type accounting through this helper. Missing switch cases silently produce no stat increment for new exit types unless the helper is updated. Stub behavior must stay signature-compatible with timing.c.

## Test Signals
Build coverage under both `CONFIG_KVM_EXIT_TIMING=y` and disabled configurations is the main signal. Runtime stats should increment for common exits even when timing debugfs is not built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/timing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/tm.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/tm.S

## Purpose
Implements low-level save and restore of PowerPC transactional memory state for KVM, including checkpointed GPRs, FP/VMX/VSX state, TM SPRs, CR, LR, CTR, XER, AMR, TAR, PPR, and DSCR. It is active only under `CONFIG_PPC_TRANSACTIONAL_MEM`.

## Important APIs, Types, And Functions
Core symbols are `__kvmppc_save_tm`, `_kvmppc_save_tm_pr`, `__kvmppc_restore_tm`, and `_kvmppc_restore_tm_pr`. PR wrappers export `_kvmppc_save_tm_pr` and `_kvmppc_restore_tm_pr`. It uses offsets such as `VCPU_GPRS_TM`, `VCPU_TEXASR`, `VCPU_TFHAR`, `VCPU_TFIAR`, `VCPU_FPRS_TM`, and `VCPU_VRS_TM`, plus helpers `store_fp_state`, `store_vr_state`, `load_fp_state`, and `load_vr_state`.

## Control Flow
Save enables TM/FP/VEC/VSX in MSR, checks the guest TS bits, and if transactional state is active, uses `treclaim` to expose checkpointed state. It preserves host scratch, CR, DSCR, optional nonvolatile GPRs, captures GPRs and TM SPRs into the vCPU, saves FP/vector state, restores host CR/DSCR/nonvolatile state, and optionally restores MSR bits. Restore writes TFHAR/TFIAR/TEXASR, verifies active TS, forces TEXASR failure summary, loads checkpointed FP/vector and scalar state, clears RI around volatile register replacement, executes `trechkpt`, restores host state, and restores MSR bits when requested.

## State And Persistence
Persistent guest TM state is stored in the vCPU arch save area. Temporary host state is kept on the stack, PACA scratch, and HSTATE scratch registers. PR wrappers preserve TAR around calls for C callers.

## Dependencies And Integration Points
Depends on PowerPC transactional memory instructions, PACA/HSTATE conventions, asm offsets generated from C structs, CPU feature sections for P9 TM HV assist, and FP/vector save helpers. Called by HV and PR KVM paths that need to context-switch transactional state.

## Risks
This is highly sensitive assembly: RI is cleared while stack/PACA state is transient, and any offset or calling-convention drift can corrupt host or guest state. TEXASR is adjusted to avoid host program checks on restore. Feature-specific behavior around P9 TM assist must match hardware. Incorrect nonvolatile preservation can break C callers.

## Test Signals
Signals include TM-enabled guest workloads, suspend/resume of active transactions across KVM exits, migration/register tests for TM SPRs, and stress on PR/HV wrappers. Build coverage should include TM disabled, TM enabled, and P9 TM assist configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/tm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace.h

## Purpose
Defines generic PowerPC KVM tracepoints for instruction emulation, shadow/guest TLB writes, shadow TLB invalidation, and request checks. `powerpc.c` defines `CREATE_TRACE_POINTS` before including this header, making it the tracepoint definition source.

## Important APIs, Types, And Functions
Trace events are `kvm_ppc_instr`, `kvm_stlb_inval`, `kvm_stlb_write`, `kvm_gtlb_write`, and `kvm_check_requests`. Each declares its argument list, trace entry fields, assignment block, and printk format.

## Control Flow
Callers invoke generated `trace_kvm_*` functions at emulation, TLB, and request-processing sites. The trace subsystem records event fields only when tracing is enabled. The bottom of the header sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`, then includes `trace/define_trace.h` outside the guard.

## State And Persistence
No runtime state is owned by the header beyond generated static tracepoint definitions. Trace records are emitted into the kernel tracing infrastructure.

## Dependencies And Integration Points
Depends on `linux/tracepoint.h` and KVM vCPU definitions for request tracing. Export of `kvm_ppc_instr` from `powerpc.c` allows module users to attach to that tracepoint.

## Risks
Tracepoint field formats become observability ABI for tooling; changing field names or units can break scripts. Tracepoints that dereference vCPU fields must be called with valid vCPU lifetime. The header must maintain the trace include pattern exactly to avoid duplicate or missing definitions.

## Test Signals
Build and ftrace/perf availability are the main signals. Enabling `kvm:kvm_ppc_instr` and TLB events during guest execution should show decoded instruction and TLB writes/invalidation data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_book3s.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_book3s.h

## Purpose
Provides a shared symbolic exception-number map for Book3S trace headers. It is included by both PR and HV tracepoint headers to keep exception name formatting consistent.

## Important APIs, Types, And Functions
Defines macro `kvm_trace_symbol_exit`, mapping Book3S exception vectors such as system reset, machine check, data/instruction storage, external, decrementer, syscall, hypervisor storage, emulation assist, performance monitor, AltiVec, and VSX.

## Control Flow
There is no executable control flow. `trace_pr.h` and `trace_hv.h` expand the macro inside `__print_symbolic()` calls for `kvm_exit` or guest exit events.

## State And Persistence
No state is created. The macro contributes static symbolic trace metadata at compile time.

## Dependencies And Integration Points
Integrated with Linux tracepoint formatting. It must be included before the Book3S trace headers use `kvm_trace_symbol_exit`.

## Risks
Missing or stale vector names reduce trace readability and can mislead debugging. Because the macro is shared by PR and HV, edits affect both trace systems.

## Test Signals
Build success for Book3S trace headers and readable ftrace output for Book3S exits are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_book3s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_booke.h

## Purpose
Defines BookE-specific KVM tracepoints and symbolic decoders for exits, BookE 2.06 TLB operations, reference release, and queued interrupt priorities.

## Important APIs, Types, And Functions
Events are `kvm_exit`, `kvm_booke206_stlb_write`, `kvm_booke206_gtlb_write`, `kvm_booke206_ref_release`, and `kvm_booke_queue_irqprio`. Symbol macros include `kvm_trace_symbol_exit`, optional SPE/e500mc IRQ priority mappings, and `kvm_trace_symbol_irqprio`.

## Control Flow
Callers in e500 MMU and BookE interrupt code emit generated trace functions. `kvm_exit` snapshots PC, MSR, DAR, and last instruction from the vCPU. TLB events record MAS fields or PFN/flags. IRQ priority tracing records vCPU ID, priority, and pending exception bitmap.

## State And Persistence
No owned state. Trace events carry snapshots of vCPU and TLB metadata into the kernel tracing subsystem.

## Dependencies And Integration Points
Depends on BookE KVM structures/macros, optional `CONFIG_SPE_POSSIBLE` and `CONFIG_PPC_E500MC`, and Linux tracepoint infrastructure. It is included by e500 MMU and BookE backend code.

## Risks
The event name `kvm_exit` overlaps with PR trace headers under different `TRACE_SYSTEM` values, so trace tooling must select the correct system (`kvm_booke`). Optional symbol mappings must match configured interrupt priorities. MAS fields are architecture-specific and require consumers to know BookE encodings.

## Test Signals
Enable `kvm_booke:*` tracepoints while running e500 guests. TLB write/release events should appear during TLB misses and invalidations; queue IRQ priority events should appear when BookE exceptions are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_booke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_hv.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_hv.h

## Purpose
Defines tracepoints for Book3S HV KVM guest entry/exit, page faults, hypercalls, vcore scheduling/blocking, vCPU run loop entry/exit, and nested/pseries vCPU timing counters.

## Important APIs, Types, And Functions
Defines large symbolic maps `kvm_trace_symbol_hcall`, `kvm_trace_symbol_kvmret`, and `kvm_trace_symbol_hcall_rc`, then events `kvm_guest_enter`, `kvm_guest_exit`, `kvm_page_fault_enter`, `kvm_page_fault_exit`, `kvm_hcall_enter`, `kvm_hcall_exit`, `kvmppc_run_core`, `kvmppc_vcore_blocked`, `kvmppc_vcore_wakeup`, `kvmppc_run_vcpu_enter`, `kvmppc_run_vcpu_exit`, and conditional `kvmppc_vcpu_stats`.

## Control Flow
HV code emits tracepoints at guest transitions, hash/radix page fault handling, hcall dispatch, and scheduling paths. The tracepoint callbacks snapshot vCPU IDs, PC/MSR/trap state, HPTE/GPTE fields, memslot metadata, hcall arguments/return values, runnable counts, wait duration, and nested transition timing. `kvmppc_vcpu_stats` is conditionally emitted only when counters are nonzero and uses registration callbacks.

## State And Persistence
No owned state. The header defines trace metadata and event snapshots consumed by ftrace/perf/BPF.

## Dependencies And Integration Points
Depends on `trace_book3s.h`, `asm/hvcall.h`, `asm/kvm_asm.h`, optional `CONFIG_PPC_PSERIES`, and HV KVM structures such as `struct kvmppc_vcore`. It is part of the Book3S HV observability surface.

## Risks
The hcall symbolic table is extensive and must track firmware ABI additions. Some trace entries dereference memslots or HPTE arrays, so call sites must provide valid pointers. Trace output exposes low-level addresses and guest state, so it is powerful but sensitive in production diagnostics.

## Test Signals
Enable `kvm_hv:*` tracepoints under Book3S HV guests. Expected signals include enter/exit pairs, hcall enter/exit pairs with symbolic names, page fault records, and vcore scheduling events during multi-vCPU workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_hv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_pr.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_pr.h

## Purpose
Defines tracepoints for Book3S PR KVM reentry, MMU mapping/invalidations, SLB mapping, SLB failures, SLBMTE operations, and PR guest exits.

## Important APIs, Types, And Functions
Events include `kvm_book3s_reenter`, optional 64-bit `kvm_book3s_64_mmu_map`, `kvm_book3s_mmu_map`, `kvm_book3s_mmu_invalidate`, `kvm_book3s_mmu_flush`, `kvm_book3s_slb_found`, `kvm_book3s_slb_fail`, `kvm_book3s_slb_map`, `kvm_book3s_slbmte`, and `kvm_exit`. It uses `kvm_trace_symbol_exit` from `trace_book3s.h`.

## Control Flow
PR code emits these tracepoints around reentry decisions, HPTE/cache updates, MMU flushes, SLB translations, and guest exits. Events capture PTE cache fields, host VPN/PFN, effective/virtual/real addresses, permission flags, SLB masks, and vCPU exit state including PC, MSR, DAR, SRR1, and last instruction.

## State And Persistence
No state is owned. Events snapshot PR MMU and vCPU state into tracing buffers.

## Dependencies And Integration Points
Depends on Book3S PR types such as `struct hpte_cache` and `struct kvmppc_pte`, `trace_book3s.h`, and Linux tracepoints. It is compiled under the `kvm_pr` trace system.

## Risks
Tracepoint consumers rely on field names and formats. Some events expose address mappings and permission bits, so output can be sensitive. The 64-bit map tracepoint is config-gated and tooling must handle absence on non-64-bit builds.

## Test Signals
Enable `kvm_pr:*` tracepoints with a Book3S PR guest. MMU map/flush and SLB events should correlate with guest memory activity; exit events should show symbolic Book3S exception names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/trace_pr.h -->
