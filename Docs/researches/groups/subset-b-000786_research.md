# subset-b-000786 research

Grouped research for PowerPC KVM XIVE, BookE, and e500 virtualization files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.c

Purpose: Implements the Book3S KVM XICS-compatible interrupt controller backed by the POWER XIVE hardware. It lets a guest use legacy XICS hcalls while KVM manages XIVE VPs, interrupt queues, escalation interrupts, emulated IPIs, pass-through IRQs, source state, migration state, and debugfs visibility.

Important APIs/types/functions: Exports `kvm_xive_ops`, `kvmppc_xive_xics_hcall()`, `kvmppc_xive_connect_vcpu()`, `kvmppc_xive_cleanup_vcpu()`, `kvmppc_xive_set_xive()`, `kvmppc_xive_get_xive()`, `kvmppc_xive_int_on()`, `kvmppc_xive_int_off()`, `kvmppc_xive_set_irq()`, `kvmppc_xive_set_mapped()`, `kvmppc_xive_clr_mapped()`, `kvmppc_xive_get_icp()`, `kvmppc_xive_set_icp()`, `kvmppc_xive_push_vcpu()`, `kvmppc_xive_pull_vcpu()`, `kvmppc_xive_rearm_escalation()`, source allocation/free helpers, queue debug helpers, and VP/server sizing helpers.

Control flow: Device creation allocates or reuses a `kvmppc_xive`, initializes queue geometry and flags, and stores it in `kvm->arch.xive`. `connect_vcpu` allocates a VP, IPI, queues, and escalation IRQs. Guest XICS hcalls dispatch through `kvmppc_xive_xics_hcall()`: `H_XIRR` acknowledges TIMA pending bits, scans queues, and returns XIRR; `H_CPPR` changes CPPR and either pushes pending work or rescans rerouted entries; `H_EOI` performs ESB EOI and pending re-evaluation; `H_IPI` updates MFRR and triggers the target IPI; `H_IPOLL` peeks without consuming. Source configuration provisions queues, masks/unmasks via ESB PQ transitions, retargets through OPAL `xive_native_configure_irq()`, and maintains queue counts. Migration get/set converts XIVE queue/PQ state into XICS-compatible source and ICP state.

State and persistence: Persistent VM state includes VP block IDs, per-vCPU CPPR/hardware CPPR/MFRR/pending bits, queue pages, queue counters, escalation IRQs, source blocks, guest/saved/actual priority, P/Q snapshots, LSI assertion, pass-through hardware IRQ data, delayed restore IRQs, and source migration counters. State is protected by `xive->lock`, per-source `arch_spinlock_t`, `vcpu->mutex` during teardown, atomics for queue occupancy, and explicit barriers around CPPR/MFRR/PQ/EOI races.

Dependencies and integration points: Depends on Linux KVM Book3S, XICS ABI constants, XIVE native/OPAL helpers, irqdomain/IRQ affinity, debugfs/seq_file, KVM device attributes, hcall dispatch, and Book3S guest entry code that pushes/pulls XIVE context. Native XIVE mode uses its shared helpers and `reset_mapped` hook when ESB pages are exposed to guests.

Risks: The main risk is interrupt loss, duplication, or queue overflow across mask/unmask, retargeting, EOI, and migration. The code relies on subtle memory ordering between `guest_priority`, `in_eoi`, MFRR, CPPR, ESB MMIO, and escalation state. Pass-through mapping must preserve host IRQ ownership and clear guest ESB mappings. Device release intentionally recycles `kvmppc_xive` storage, so lifetime assumptions are delicate.

Test signals: Strong signals include POWER9/POWER10 KVM guests in XICS-on-XIVE mode, hotplugged vCPUs, hcall stress for XIRR/CPPR/EOI/IPI/IPOLL, LSI and MSI injection, irqfd/MSI pass-through map/unmap, migration save/restore with pending interrupts, cede/escalation wakeups, debugfs source/queue inspection, lockdep/KCSAN, and Book3S KVM selftests or QEMU pseries interrupt-controller tests.

Source read size: 2976 lines, 77630 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.h

Purpose: Defines the shared in-kernel data model and helper API for Book3S KVM XIVE support, covering both XICS-on-XIVE compatibility and native XIVE device mode.

Important APIs/types/functions: Provides `struct kvmppc_xive_irq_state`, `struct kvmppc_xive_src_block`, `struct kvmppc_xive_ops`, `struct kvmppc_xive`, and `struct kvmppc_xive_vcpu`; constants `KVMPPC_XIVE_FIRST_IRQ`, `KVMPPC_XIVE_NR_IRQS`, `KVMPPC_XIVE_Q_COUNT`, and feature flags; helpers `kvmppc_xive_select_irq()`, `kvmppc_xive_find_server()`, `kvmppc_xive_find_source()`, `kvmppc_xive_vp()`, `kvmppc_xive_vp_in_use()`, `xive_prio_from_guest()`, `xive_prio_to_guest()`, `__xive_read_eq()`, and common function declarations used by both implementations.

Control flow: The header itself has inline lookup and decoding logic. Source lookup splits guest IRQs into ICS-like blocks and per-block source indexes. VP lookup packs a guest vCPU/server number into a hardware VP inside the VM VP block. Queue reads advance index/toggle state only when a valid entry is observed. Priority mapping clamps guest priorities above 5 to host priority 6 while preserving `0xff` masked state.

State and persistence: The structures describe all long-lived XIVE VM state: source validity, emulated IPI or pass-through backing IRQ, guest and actual target, PQ snapshots, LSI assertion, migration flags, native EISN, VP identifiers, queue pages, escalation IRQs, pending ICP state, queue provisioning bitmap, mapping inode, locks, and delayed restore counters.

Dependencies and integration points: Gated by `CONFIG_KVM_XICS` and includes `book3s_xics.h`. It integrates with `book3s_xive.c`, `book3s_xive_native.c`, Book3S KVM architecture state, Linux XIVE structs, KVM device ioctls, and guest entry code that consumes `xive_cam_word` and saved TIMA state.

Risks: Field semantics are shared across two modes, so changes can break XICS compatibility or native XIVE differently. `kvmppc_xive_find_server()` is a linear vCPU scan and assumes stable vCPU attachment under caller serialization. `__xive_read_eq()` depends on XIVE queue toggle format and correct big-endian entry reads.

Test signals: Compile coverage for `CONFIG_KVM_XICS`, XICS-on-XIVE and native-XIVE runtime tests, vCPU hotplug, queue wraparound tests, migration state tests, and pass-through IRQ mapping tests are the main signals.

Source read size: 313 lines, 8417 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive_native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive_native.c

Purpose: Implements the native KVM XIVE device for Book3S guests. Unlike the XICS compatibility layer, this path exposes XIVE-style source, queue, ESB, and TIMA configuration directly to userspace and the guest.

Important APIs/types/functions: Exports `kvm_xive_native_ops`, `kvmppc_xive_native_connect_vcpu()`, `kvmppc_xive_native_cleanup_vcpu()`, `kvmppc_xive_native_supported()`, `kvmppc_xive_native_get_vp()`, and `kvmppc_xive_native_set_vp()`. Internal key functions include native queue configure/cleanup wrappers, ESB/TIMA fault handlers, `kvmppc_xive_native_mmap()`, source creation/config/sync, EQ config get/set, global reset, EQ sync, device attr dispatch, release/create/init, and debugfs reporting.

Control flow: Device creation initializes a reusable `kvmppc_xive`, mapping lock, VP block defaults, native ops, and host XIVE feature flags. VCPU connect allocates a VP ID, enables the VP in OPAL, and installs CAM/saved TIMA state for guest entry. Userspace creates sources, configures source target/effective IRQ numbers, configures guest event queues by pinning the guest queue page, and attaches escalation IRQs. Mmap faults map either guest-visible ESB trigger/EOI pages or the OS TIMA page. Reset disables queues, escalations, and source routing. EQ sync synchronizes source/queue state and marks guest EQ pages dirty for migration.

State and persistence: State persists in `kvmppc_xive` source blocks, per-vCPU VP and queue state, guest queue GPA/qshift, pinned queue pages, EISN values, escalation IRQs, device file mapping, and saved TIMA word state. Queue pages are page-pinned and released with `put_page()`, and mapping invalidation clears stale ESB PFNs on pass-through changes.

Dependencies and integration points: Integrates with the common XIVE header and helpers, OPAL `xive_native_*` calls, KVM device attribute groups `KVM_DEV_XIVE_*`, VM mmap fault handling, KVM memory slots/SRCU, page dirty tracking for migration, irqdomain, debugfs, and the shared pass-through reset hook used by `book3s_xive.c`.

Risks: Incorrect queue page validation or pin lifetime can leak pages or corrupt guest memory. ESB/TIMA fault offsets must reject unsupported pages or guests can access privileged TIMA areas. Source config races require source-block locking. EQ sync and dirty marking are migration-critical. A notable code risk is that `kvmppc_xive_native_mmap()` stores `xive->mapping` without taking `mapping_lock`, while reset/release use the lock.

Test signals: Native XIVE QEMU pseries guests, mmap tests for TIMA/ESB offsets, invalid source and queue attr tests, queue reset/reconfigure, migration with active EQs, pass-through IRQ map/unmap with ESB remap, OPAL queue state support detection, and debugfs inspection are useful signals.

Source read size: 1284 lines, 31453 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive_native.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.c

Purpose: Provides the generic PowerPC BookE KVM core for vCPU state management, exception prioritization and delivery, guest run/exit handling, timer/watchdog emulation, register ioctls, debug support, memory-slot hooks, and subarchitecture delegation.

Important APIs/types/functions: Defines BookE VM/vCPU stats descriptors, `kvmppc_dump_vcpu()`, `kvmppc_set_msr()`, exception queue helpers, `kvmppc_core_prepare_to_enter()`, `kvmppc_core_check_requests()`, `kvmppc_vcpu_run()`, `kvmppc_handle_exit()`, get/set regs and sregs ioctls, one-reg get/set, timer setters `kvmppc_set_tcr()`, `kvmppc_set_tsr_bits()`, `kvmppc_clr_tsr_bits()`, decrementer/watchdog functions, `kvmppc_xlate()`, guest-debug ioctl support, vCPU load/put wrappers, VM/vCPU lifecycle wrappers, and `kvmppc_booke_init()/exit()`.

Control flow: The run path prepares entry, loads guest FP/AltiVec/debug context, calls assembly `__kvmppc_vcpu_run()`, then restores host context. Low-level assembly returns to `kvmppc_handle_exit()`, which restarts host-owned interrupts, fetches faulting instructions when needed, accounts guest exit time, dispatches by BookE interrupt number, either queues a guest exception, handles MMIO/TLB misses, emulates privileged instructions, exits to userspace, or resumes the guest. Before entry, pending exception bits are scanned in priority order and delivered only when the guest MSR allows the relevant class.

State and persistence: Owns `vcpu->arch.pending_exceptions`, queued DEAR/ESR, IVPR/IVORs, CSRR/DSRR/MCSRR, MSR/shadow MSR, timer TSR/TCR/DEC/DECAR, watchdog timer and lock, FP/SPE/AltiVec/debug state, guest debug registers, EPR state, shared page registers, and timing/stat counters. VM memory-slot hooks are mostly no-ops for this nohash BookE path.

Dependencies and integration points: Depends on BookE assembly handlers, subarch `kvmppc_ops` for e500/e500mc-specific MMU and SPR behavior, PowerPC timebase and interrupt APIs, KVM generic request/exit machinery, KVM user ABI structs, `trace_booke`, FPU/SPE/AltiVec helpers, MPIC/EPR integration, and host exception handlers for restarted host interrupts.

Risks: Exception delivery depends on correct priority masks, critical-section detection, and MSR class gating. Guest/host FP, AltiVec, SPE, debug, PID, and interrupt state transitions are sensitive to preemption and interrupt state. Watchdog arithmetic can flood timers if final expiry is mishandled. Exit dispatch has many architecture-specific cases where a wrong resume flag can corrupt nonvolatile registers or lose a userspace exit.

Test signals: BookE/e500 KVM boot tests, TLB miss and MMIO tests, timer/decrementer/watchdog tests, guest debug break/watch/singlestep tests, FP/SPE/AltiVec context switching, signal-interrupted `KVM_RUN`, register ioctl round trips, and KVM selftests/QEMU e500 guests are the strongest signals.

Source read size: 2242 lines, 58285 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.h

Purpose: Declares the common BookE KVM interrupt-priority model, public helper interfaces, and low-level assembly hooks shared by BookE core, e500 code, and BookE PR/HV interrupt handlers.

Important APIs/types/functions: Defines `BOOKE_IRQPRIO_*` priority constants, `BOOKE_IRQMASK_EE`, `BOOKE_IRQMASK_CE`, external handler symbols `kvmppc_booke_handlers` and `kvmppc_booke_handler_addr`, MSR/timer setters, BookE instruction and SPR emulation entry points, SPE save/load assembly routines, vCPU load/put helpers, `enum int_class`, `kvmppc_set_pending_interrupt()`, e500-specific emulation dispatch declarations, `kvmppc_clear_dbsr()`, and `kvmppc_handle_exit()`.

Control flow: The header has no runtime control flow beyond `kvmppc_clear_dbsr()`. It defines the numeric priority ordering consumed by `booke.c` when scanning `pending_exceptions` and by assembly/C handlers when converting hardware exception numbers into guest exception classes.

State and persistence: It names state rather than storing it. The priority constants map pending-exception bit positions in `vcpu->arch.pending_exceptions`; masks summarize exceptions gated by MSR[EE] and MSR[CE]. Assembly symbols point to copied PR-mode handlers or linked HV handlers.

Dependencies and integration points: Includes KVM host types, PowerPC KVM arch state, `switch_to.h`, and `timing.h`. Used by `booke.c`, `booke_emulate.c`, both BookE assembly files, and e500/e500mc code.

Risks: Priority values are ABI-like inside this implementation; reordering can change exception delivery semantics. Conditional SPE and AltiVec priority definitions overlap intentionally by platform and must stay consistent with IVOR mapping code. The duplicate e500 SPR declarations are harmless but brittle for cleanup.

Test signals: BookE builds across `CONFIG_SPE_POSSIBLE`, `CONFIG_PPC_E500MC`, `CONFIG_KVM_BOOKE_HV`, and PR-mode configs, plus runtime interrupt-priority tests, are the main signals.

Source read size: 115 lines, 3757 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_emulate.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_emulate.c

Purpose: Emulates generic BookE privileged instructions and special-purpose register accesses that cannot execute directly in the guest context.

Important APIs/types/functions: Implements `kvmppc_booke_emulate_op()`, `kvmppc_booke_emulate_mtspr()`, and `kvmppc_booke_emulate_mfspr()`. Internal helpers emulate `rfi`, `rfci`, and `rfdi`. It decodes op 19 return instructions and op 31 MSR operations (`mfmsr`, `mtmsr`, `wrtee`, `wrteei`) plus a large set of BookE SPRs including DEAR/ESR, CSRR/DSRR, debug registers, TSR/TCR/DECAR, SPRG4-7, IVPR/IVORs, MCSR, and EPCR.

Control flow: Instruction emulation first switches on primary opcode and extended opcode, updates vCPU architectural state, sets exit accounting type, and controls whether the PC advances. SPR writes update vCPU state, optionally mask unsupported debug bits, synchronize debug hardware when guest-owned debug registers change, preserve TCR WRC semantics, and defer to failure when an unknown SPR is seen. SPR reads return the virtualized backing state and expose `DBCR0_EDM` when userspace owns debugging.

State and persistence: Persists guest return state in SRR/CSRR/DSRR, exception metadata in DEAR/ESR/MCSR, timer state in TSR/TCR/DECAR, IVPR/IVOR exception vector offsets, debug address/control/status registers, EPCR, SPRG values, and guest-visible MSR. Writes often have side effects such as clearing TSR/DBSR bits, dequeuing debug exceptions, or updating shadow MSR through `kvmppc_set_msr()`.

Dependencies and integration points: Depends on `asm/disassemble.h` decoders, `booke.h` setters and queue helpers, PowerPC SPR constants, debug register switching, and e500 fallback dispatch from `e500_emulate.c`.

Risks: SPR behavior is architecture-visible and migration-visible. Incorrect DBCR/DBSR ownership can leak host debug resources or hide guest debug events. `wrtee/wrteei` update only MSR[EE], so callers must not use them as full MSR synchronization. The BookE-HV note warns that some registers are real hardware-backed in GS mode and these helpers can be wrong outside the intended trap context.

Test signals: Privileged instruction emulation tests, guest return-from-interrupt paths, timer SPR read/write tests, guest debug register tests with and without userspace debug, EPCR/IVOR migration round trips, and e500 fallback SPR tests are relevant.

Source read size: 511 lines, 11297 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_emulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_interrupts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_interrupts.S

Purpose: Provides the 32-bit BookE PR-mode low-level KVM guest entry, guest exit, copied exception handlers, and optional SPE register save/restore routines.

Important APIs/types/functions: Defines handler macros `KVM_HANDLER`, `KVM_DBG_HANDLER`, `KVM_HANDLER_ADDR`, the copied handler range `kvmppc_handlers_start/end`, `kvmppc_resume_host`, `__kvmppc_vcpu_run`, the handler address table `kvmppc_booke_handler_addr`, and `kvmppc_save_guest_spe()`/`kvmppc_load_guest_spe()` under `CONFIG_SPE`.

Control flow: At init, `booke.c` copies handler snippets into a 64 KiB IVPR-aligned page matching host IVOR offsets. Guest entry saves host nonvolatile registers and stack metadata, loads guest nonvolatiles, switches PID/PID1 and IVPR to the KVM handler page, reloads guest SPRG4-7 and volatile state, sets SRR0/SRR1 to guest PC/shadow MSR, clears stale debug status, and executes `rfi`. On guest exception, a tiny handler records the exit number and key registers, branches to `kvmppc_resume_host`, saves fault context and guest volatile state, restores host PID/IVPR/stack, calls `kvmppc_handle_exit()`, then either resumes the guest through a lightweight path or returns to C through a heavyweight exit.

State and persistence: Saves and restores host stack, LR, CR, r2, nonvolatile GPRs, guest GPRs, CTR, LR, XER, CR, PC, PID, PID1, IVPR, SPRG4-7, last instruction, DEAR, ESR, timing stamps, and SPE accumulator/EVRs. The assembly is the authoritative boundary between host thread state and guest vCPU state.

Dependencies and integration points: Depends on asm offsets, BookE interrupt numbers, KVM resume flags, PowerPC SPR definitions, copied-handler setup in `kvmppc_booke_init()`, and C exit handling in `kvmppc_handle_exit()`.

Risks: Any offset mismatch, missing register save, or wrong resume flag corrupts host or guest state. Switching IVPR before all memory references are guaranteed resident is dangerous, as noted by the source comment. Debug handler filtering has a small window where a breakpoint intended for guest context can fire in host context.

Test signals: PR-mode e500v2 guest boot, exception-heavy workloads, instruction emulation requiring nonvolatile reload, host interrupt delivery while in guest, SPE state tests, debug interrupt tests, and objdump/relocation inspection after asm-offset changes are important.

Source read size: 535 lines, 14587 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_interrupts.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/bookehv_interrupts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/bookehv_interrupts.S

Purpose: Provides BookE HV/GS-mode low-level KVM guest entry and exit handlers for e500mc/e6500-style hardware virtualization, derived from the PR-mode assembly but using PACA exception save areas, guest state registers, and HV-specific MAS handling.

Important APIs/types/functions: Defines common handler macro `kvm_handler_common`, 64-bit and 32-bit `kvm_handler`/`kvm_lvl_handler` variants, exception handlers named `kvmppc_handler_<int>_<srr1>`, `kvmppc_resume_host`, and `__kvmppc_vcpu_run`. It uses flags `NEED_EMU`, `NEED_DEAR`, and `NEED_ESR` to decide what state each exception must preserve.

Control flow: HV exception stubs retrieve the current vCPU from PACA or thread state, save clobbered volatile registers and SRR/CSRR/MCSRR/GSRR/DSRR state, restore host stack/PID, optionally collect ESR/DEAR or mark last instruction fetch failed, then branch to `kvmppc_resume_host`. The resume path saves guest SPRGs, VRSAVE, MAS registers, XER/LR, restores host MAS4/MAS6 and EPCR behavior, calls `kvmppc_handle_exit()`, and either reloads guest state for another `rfi` or returns to C. Guest entry saves host state, loads guest PID, MAS registers, SPRGs, VRSAVE, volatile/nonvolatile GPRs, MSR/PC, and enters the guest.

State and persistence: Manages guest and host GPRs, CR, CTR, LR, XER, PID, MAS0-7, MAS4/MAS6 host backups, EPCR DMIUH, SPRG4-9, VRSAVE, shared MSR, PC, DEAR, ESR, last instruction sentinel, timing fields, and host stack/nonvolatile registers. It also contains guest doorbell, critical, machine-check, debug, TLB, LRAT, HV-privilege, and HV-syscall exit paths.

Dependencies and integration points: Depends on BookE HV asm ABI, PACA exception layouts, `asm-offsets`, 64e exception definitions, KVM BookE C exit handling, e500 MMU/MAS emulation, and guest doorbell pending-interrupt support.

Risks: The code is highly sensitive to 32-bit versus 64-bit save-area differences, PACA offset correctness, MAS register ordering, and EPCR DMIUH toggling. Missing state save on an exception class can break emulation or corrupt guest TLB state. Branch-target-buffer flush sections are security-sensitive.

Test signals: e500mc/e6500 HV guest boot, TLB miss and LRAT tests, MAS register stress, guest doorbells, HV privileged instruction exits, debug/critical/machine-check paths, 32-bit and 64-bit BookE HV builds, and objdump validation against asm-offset changes are key signals.

Source read size: 673 lines, 19481 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/bookehv_interrupts.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500.c

Purpose: Implements the Freescale/NXP e500v2 PR-mode KVM subarchitecture, including shadow PID/TID allocation, e500 TLB setup and invalidation glue, subarch register exposure, vCPU allocation, and module registration.

Important APIs/types/functions: Defines local shadow-ID structures `struct id`, `struct vcpu_id_table`, `struct pcpu_id_table`; exports `kvmppc_e500_get_sid()`, `kvmppc_e500_get_tlb_stid()`, `kvmppc_set_pid()`, `kvmppc_e500_tlbil_one()`, `kvmppc_e500_tlbil_all()`, `kvmppc_mmu_msr_notify()`, and `kvmppc_core_vcpu_setup()`. Internal key functions handle ID table allocation/reset, shadow PID recalculation, processor compatibility, initial TLB setup, sregs/one-reg delegation, vCPU create/free/load/put, and `kvm_ops_e500` registration.

Control flow: Module init checks for `e500v2`, initializes common BookE handlers, copies additional e500 IVOR32-34 handlers, starts `kvm_init()`, and installs `kvmppc_pr_ops`. VCPU creation allocates e500 private state, TLB state, and the shared page. Setup installs initial guest TLB1 mappings and captures PVR/SVR. On PID/MSR/TLB changes, shadow PID mappings are recalculated or invalidated. Shadow IDs are per-host-CPU and recycled by flushing all local TLB mappings when the 1..255 pool is exhausted.

State and persistence: Maintains per-vCPU guest PID array, guest-to-shadow ID table, per-CPU reverse SID table and last SID counter, shadow PID/PID1, guest TLB arrays owned by e500 TLB code, SVR/HID/MCAR-like state, and the shared page. Initial guest state includes a 256 MiB low mapping and a serial MMIO mapping for the wrapper.

Dependencies and integration points: Depends on `booke.c` lifecycle, `booke_interrupts.S` copied handlers, e500 TLB implementation functions declared in `e500.h`, nohash e500 MMU helpers, `kvm_init()`, and module aliasing for `/dev/kvm`.

Risks: Shadow PID mappings require preemption disabled; using a SID after migration to another host CPU is invalid. TLB invalidation must handle cases where a shadow PID is valid only on a remote CPU by resetting vCPU mappings. A likely bug appears in `kvmppc_set_one_reg_e500()`, which calls `kvmppc_get_one_reg_e500_tlb()` instead of the set helper. Initial hard-coded mappings are legacy assumptions.

Test signals: e500v2 KVM module load on matching CPU, guest boot with TLB misses, PID/TID context-switch stress, tlbil/tlbivax tests, sregs/one-reg TLB round trips, migration or vCPU reload tests across CPUs, and static review of one-reg setter behavior are important.

Source read size: 553 lines, 14514 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500.h

Purpose: Defines the e500 KVM private vCPU structure, TLB geometry, MAS/TLB helper macros, MMU feature helpers, and interfaces between e500 core, TLB management, and emulation code.

Important APIs/types/functions: Provides `enum vcpu_ftr`, constants for PID and TLB counts, TLB private flags, `struct tlbe_priv`, `struct kvmppc_e500_tlb_params`, `struct kvmppc_vcpu_e500`, `to_e500()`, TLB index helpers, MAS attribute masks, TLB emulation prototypes, sregs/one-reg TLB prototypes, SID helper declarations, inline TLB field decoders, current PID/AS/PR helpers, MAS0/MAS6 helpers, `tlbe_is_host_safe()`, `get_entry()`, invalidation prototypes, HV-specific LPID helpers, and `has_feature()`.

Control flow: Inline helpers decode e500 MAS fields, compute guest TLB entry size/range/real address/TID/TS/V/IPROT, validate whether a guest TLB entry can be shadowed by the host, select the current guest address space and PID, and choose HV versus PR-mode TID semantics. The header also centralizes the e500 private object layout used by container conversions.

State and persistence: `struct kvmppc_vcpu_e500` persists the unmodified guest TLB shared with userspace, per-entry host-private TLB metadata, TLB geometry and next-victim indexes, host TLB1 mapping/rmap arrays, min/max TLB1 effective address, shared TLB pages, SVR/L1CSR/HID/MCAR state, and PR-mode PID/SID tables.

Dependencies and integration points: Depends on Linux KVM host types, nohash e500 MMU definitions, TLB helpers, CPU thread topology, BookE HV config, and implementation files such as e500 core, e500 TLB, and e500 emulation.

Risks: TLB bitfield helpers are architecture-contract code; incorrect masks can corrupt shadow translations. `tlbe_is_host_safe()` intentionally simplifies permissions and relies on memslot presence, so callers must enforce access rights elsewhere. HV thread-specific LPID composition depends on `threads_per_core` and CPU numbering.

Test signals: Compile coverage for PR and HV e500 configs, TLB emulation selftests, MAS field round trips through sregs/one-reg ioctls, large-page and TLB1 mapping tests, permission/MMIO translation tests, and multi-threaded-core LPID tests are useful.

Source read size: 337 lines, 8844 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_emulate.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_emulate.c

Purpose: Implements e500-specific privileged instruction and SPR emulation on top of the generic BookE emulator, including e500 TLB operations, doorbells, cache-lock behavior, thread-management reads, EHPRIV debug exits, and Freescale SPRs.

Important APIs/types/functions: Provides `kvmppc_core_emulate_op_e500()`, `kvmppc_core_emulate_mtspr_e500()`, and `kvmppc_core_emulate_mfspr_e500()`. Internal helpers cover doorbell priority mapping, `msgsnd`, `msgclr`, `ehpriv`, `dcbtls`, and `mftmr`. It dispatches TLB instructions to `kvmppc_e500_emul_tlbre/tlbwe/tlbsx/tlbilx/tlbivax()` and MMUCSR0 writes to `kvmppc_e500_emul_mt_mmucsr0()`.

Control flow: Opcode emulation handles primary opcode 31 e500 extensions first, computes effective addresses for TLB instructions, and falls back to `kvmppc_booke_emulate_op()` on failure. SPR write emulation updates PR-mode PID/MAS backing state, cache/HID registers, MMUCSR0 side effects, power-management state, extra IVORs, and falls back to generic BookE SPR writes. SPR read emulation returns PID/MAS, TLB config/page-size, cache/HID/SVR/MMUCFG/EPTCFG, power-management, and extra IVOR state, again falling back to generic BookE reads.

State and persistence: Updates vCPU shared MAS registers, e500 private PID array, L1CSR0/1, HID0/1, SVR, guest TLB configuration fields, EP/TLB page-size state, power management control, pending doorbell exceptions, and extra IVOR vectors for SPE, AltiVec, performance monitor, and HV doorbell interrupts.

Dependencies and integration points: Depends on BookE generic emulation, e500 TLB emulation, PowerPC disassembly helpers, doorbell constants, e500 private state, and KVM exit accounting/debug ABI.

Risks: Doorbell emulation contains a suspicious call to `dbell2prio(rb)` in `kvmppc_e500_emul_msgsnd()` rather than using the decoded parameter, which can misclassify message type. SPR handling differs under `CONFIG_KVM_BOOKE_HV`, so PR/HV coverage matters. Cache and branch-predictor SPRs are approximated and may not match hardware side effects exactly.

Test signals: e500 guest TLB instruction tests, Linux guest boot with MAS/PID activity, doorbell send/clear tests on e500mc, EHPRIV debug-exit tests, SPR get/set migration round trips, cache-control instruction tests, and config-matrix builds for SPE/AltiVec/HV are relevant.

Source read size: 452 lines, 9851 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/e500_emulate.c -->
