# Research Report: subset-b-000745

This grouped report covers the MIPS kernel VPE/watch files and the MIPS KVM backend files listed for work item `subset-b-000745`. Each source section preserves the original source path for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vpe.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/vpe.c

Purpose: Implements the MIPS VPE loader character-device path for loading an ELF service-processor program into a secondary VPE, primarily `/dev/vpe1`. The loader accepts a user-written ELF image, lays out/relocates allocated sections, locates `__start` and `vpe_shared`, flushes caches, then starts the VPE on close when `CONFIG_MIPS_VPE_LOADER_MT` is enabled.

Important APIs, types, and functions: `vpecontrol` stores global VPE/TC lists protected by spinlocks. `get_vpe()`, `alloc_vpe()`, `release_vpe()`, `get_tc()`, and `alloc_tc()` manage `struct vpe` and `struct tc` lifetimes. `alloc_progmem()` and `release_progmem()` allocate target program memory, either from top-of-memory or heap depending on `CONFIG_MIPS_VPE_LOADER_TOM`. ELF helpers include `layout_sections()`, `simplify_symbols()`, `find_vpe_symbols()`, and relocation handlers for `R_MIPS_NONE`, `R_MIPS_32`, `R_MIPS_26`, `R_MIPS_HI16`, `R_MIPS_LO16`, `R_MIPS_GPREL16`, and `R_MIPS_PC16`. The file operations are `vpe_open()`, `vpe_write()`, and `vpe_release()`. Exported integration points are `vpe_get_shared()` and `vpe_notify()`.

Control flow: Opening `/dev/vpe1` validates the minor, obtains the APRP VPE, transitions its state to `VPE_STATE_INUSE`, stops/reclaims any previous TC if already in use, and allocates a fixed-size vmalloc program buffer. Writes append user data into `v->pbuffer` until `P_SIZE` is reached. Release validates ELF magic; for relocatable objects it records section addresses, lays out alloc sections, copies them into `v->load_addr`, simplifies symbols, applies relocations, finds start/shared symbols, flushes the I-cache, and calls `vpe_run(v)`. Executable ELF images use program headers and physical addresses directly.

State and persistence: Runtime state lives in global VPE/TC linked lists, per-VPE buffers, `load_addr`, `shared_ptr`, `__start`, `len`, and notification lists. It is kernel-memory-only state; no persistent storage exists. The loaded VPE program can remain running after the loader buffer is freed. `vpe_get_shared()` exposes the loaded program's shared symbol pointer to other kernel users.

Dependencies and integration points: The file depends on MIPS MT/APRP primitives from `asm/vpe.h`, `asm/mips_mt.h`, `asm/mipsmtregs.h`, CP0/cache helpers, ELF/module relocation helpers, and VPE module init/exit symbols supplied elsewhere. It integrates with character-device registration through `vpe_fops`, user access via `copy_from_user()`, and notification callbacks registered by `vpe_notify()`.

Risks: `get_vpe()` and `alloc_vpe()` ignore their minor argument and hard-code `VPE_MODULE_MINOR`, limiting multi-device correctness. The loader accepts privileged ELF data and performs relocation/writeback in kernel context, so malformed offsets, unrecognized relocation types, missing symbol tables, and oversized images are high-risk paths. `vpe_release()` only clears `shared_ptr` on failure and does not obviously free `load_addr` for all error paths after partial allocation. The global HI16 relocation list must be drained correctly or later relocations could be contaminated. Top-of-memory allocation depends on boot-time memory reservation discipline.

Test signals: Useful coverage includes opening/writing/releasing valid ET_REL and ET_EXEC images, malformed/truncated ELF rejection, missing `__start`/`vpe_shared`, relocation range failures, repeated open while a VPE is in use, max-size writes, notification stop callbacks, and boot configurations for both `CONFIG_MIPS_VPE_LOADER_TOM` and `CONFIG_MIPS_VPE_LOADER_MT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/vpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/watch.c -->
## sources/distributed-fs/ceph-client/arch/mips/kernel/watch.c

Purpose: Manages MIPS hardware watchpoint registers for thread debug/watch support. It installs a thread's watch state on context switch, reads result bits for debugger consumption, clears hardware watch registers, and probes CPU watch capabilities.

Important APIs, types, and functions: `mips_install_watch_registers()` writes up to four usable watchlo/watchhi pairs from `task_struct.thread.watch.mips3264`. `mips_read_watch_registers()` reads watchhi result/mask bits into the current task. `mips_clear_watch_registers()` disables all probed watchlo registers, up to eight. `mips_probe_watch_registers()` discovers supported I/R/W and mask bits in `struct cpuinfo_mips`.

Control flow: Install and read functions use fallthrough switches keyed by `current_cpu_data.watch_reg_use_cnt`, so higher register counts cascade down to lower registers. Clear uses `watch_reg_count`, not use count, to wipe every implemented register and avoid repeat traps. Probe starts at watch0, writes test bits, reads back supported masks, follows the M bit chain to detect more registers, and caps actively used registers at four while counting up to eight.

State and persistence: State is split between per-thread saved watch arrays and per-CPU capability fields (`watch_reg_masks`, `watch_reg_count`, `watch_reg_use_cnt`). Hardware watch registers are volatile CP0 state restored/cleared by kernel control paths.

Dependencies and integration points: Relies on `asm/watch.h`, CP0 watch read/write helpers, `current_cpu_data`, and scheduler/debug code that calls install/read/clear. The user-visible behavior is mediated through ptrace/debug register handling elsewhere.

Risks: The functions call `BUG()` on unexpected counts, so bad CPU probing or corrupted state can crash the kernel. Only four registers are installed/read even if more exist; callers must respect that design. Release 1 CPUs that do not report result bits are handled by inferring conditions from watchlo, which is intentionally approximate.

Test signals: Exercise CPUs or emulators with 0, 1, 4, and 8 watch registers; ptrace watchpoint hits; context-switch save/restore; watch clear after exception; and old Release 1 behavior where watchhi condition bits are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kernel/watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/Kconfig

Purpose: Defines the MIPS architecture KVM configuration menu and feature gates.

Important APIs, types, and functions: The main symbol is `CONFIG_KVM`, a tristate dependent on `CPU_SUPPORTS_VZ` and `MIPS_FP_SUPPORT`. It selects common KVM infrastructure (`KVM_COMMON`, `KVM_MMIO`, dirty-log read-protect, generic hardware enabling, readonly memory support, and `EXPORT_UASM`). `CONFIG_KVM_MIPS_DEBUG_COP0_COUNTERS` optionally enables COP0 access histograms.

Control flow: `VIRTUALIZATION` is a menuconfig wrapper. If disabled, all nested KVM options are hidden/disabled. Enabling KVM pulls in common virtualization support and allows the KVM MIPS module objects to build.

State and persistence: No runtime state. It controls compile-time inclusion and selected common KVM features.

Dependencies and integration points: Ties the MIPS backend to `virt/kvm/Kconfig` and CPU feature detection. The FPU dependency is important because MIPS KVM context handling expects FPU support paths even when guest FPU exposure is capability-gated.

Risks: Incorrect dependencies can expose KVM on CPUs without VZ/FPU support, producing build or runtime failures. Debug COP0 counters can add overhead and log noise when enabled.

Test signals: Kconfig matrix builds with virtualization disabled, KVM module built-in/module, missing VZ, missing FPU, and debug counters enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/Makefile

Purpose: Builds the MIPS KVM backend and related TLB helper object.

Important APIs, types, and functions: Includes `virt/kvm/Makefile.kvm`, adds include paths for `virt/kvm` and `arch/mips/kvm`, and composes `kvm.o` from `mips.o`, `emulate.o`, `entry.o`, `interrupt.o`, `stats.o`, `fpu.o`, `hypcall.o`, `mmu.o`, `vz.o`, optional `msa.o`, and optional `loongson_ipi.o`. `tlb.o` is built into `obj-y`.

Control flow: `obj-$(CONFIG_KVM) += kvm.o` gates the main backend. `obj-y += tlb.o` keeps TLB helper code available from the architecture tree even outside the KVM module linkage pattern.

State and persistence: No runtime state; this is a build graph declaration.

Dependencies and integration points: Integrates MIPS KVM with generic KVM build infrastructure, optional MSA support (`CONFIG_CPU_HAS_MSA`), and Loongson IPI support (`CONFIG_CPU_LOONGSON64`).

Risks: Missing optional object gates can break references in CPU-specific paths. Because `tlb.o` is unconditional, symbols and dependencies in that file must remain buildable for the broader MIPS configuration matrix.

Test signals: Build with KVM built-in/module/off, MSA on/off, Loongson64 on/off, and generic MIPS VZ targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/emulate.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/emulate.c

Purpose: Implements MIPS KVM instruction/exception emulation helpers, especially branch-delay PC advancement, guest CP0 Count/Compare timer emulation, WAIT handling, and MMIO load/store emulation.

Important APIs, types, and functions: PC helpers are `kvm_compute_return_epc()` and `update_pc()`. Instruction fetch helpers are `kvm_get_badinstr()` and `kvm_get_badinstrp()`. Timer APIs include `kvm_mips_read_count()`, `kvm_mips_write_count()`, `kvm_mips_init_count()`, `kvm_mips_set_count_hz()`, `kvm_mips_write_compare()`, `kvm_mips_set_count_ctl()`, `kvm_mips_set_count_resume()`, `kvm_mips_count_timeout()`, and DC helpers for CP0 Cause. MMIO APIs are `kvm_mips_emulate_store()`, `kvm_mips_emulate_load()`, and `kvm_mips_complete_mmio_load()`.

Control flow: Branch-delay exceptions call `kvm_compute_return_epc()` to decode the prior branch and compute the correct resume PC, including link-register updates for branch-and-link forms and compact branch rules on R6. Timer reads derive Count from `ktime_get()`, `count_hz`, `count_period`, and bias fields unless disabled. Timer updates freeze hrtimers before changing Count/Compare/frequency, adjust bias or GTOffset, preserve/ack pending timer interrupts as requested, and resume hrtimers at the next Compare boundary. WAIT exits mark the VCPU halted when no pending exception exists and can return an IRQ-window exit. MMIO stores advance PC first, translate GVA to GPA, marshal data into `run->mmio`, attempt in-kernel MMIO bus write, and otherwise return to userspace. MMIO loads compute and save a future PC in `io_pc`, defer GPR writeback until completion, and encode sign/partial-load behavior in `mmio_needed`.

State and persistence: Uses per-VCPU state such as `arch.pc`, GPRs, `host_cp0_*`, `count_bias`, `count_dyn_bias`, `count_period`, `count_ctl`, `count_resume`, `comparecount_timer`, `io_pc`, `io_gpr`, `mmio_needed`, and `mmio_is_write`. State persists for the VCPU lifetime and across exits to userspace; timer hrtimer state is active kernel runtime state.

Dependencies and integration points: Depends on MIPS instruction encodings, CP0 helpers, hrtimer/ktime APIs, KVM MMIO bus helpers, `kvm_mips_callbacks` for timer interrupt queuing and GVA-to-GPA translation, VZ htimer helpers, tracepoints, and Loongson-specific load/store encodings under `CONFIG_CPU_LOONGSON64`.

Risks: Branch emulation is correctness-critical and returns `EMULATE_FAIL` for unsupported COP1/compact cases. Timer code has concurrency and ordering sensitivity around hrtimer cancellation, Compare writes, GTOffset changes, and pending TI preservation. Partial unaligned load/store emulation is endian/width sensitive and depends on `mmio_needed` magic values. Failed store emulation rolls PC back, but load emulation deliberately leaves PC saved for completion, so state mismatches can corrupt guest execution.

Test signals: Branch-delay exceptions for every supported branch class; Count/Compare wraparound; frequency changes; DC transitions through CP0 Cause and KVM count control; pending timer preservation on Compare writes; WAIT wakeups; MMIO bus-handled and userspace-handled loads/stores; unaligned LWL/LWR/LDL/LDR/SWL/SWR/SDL/SDR paths; 32-bit and 64-bit builds; Loongson GS load/store paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/emulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/entry.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/entry.c

Purpose: Dynamically generates the low-level MIPS guest entry, exception, TLB-refill, exit, re-entry, and host-return code used by the KVM MIPS backend.

Important APIs, types, and functions: Public builders include `kvm_mips_entry_setup()`, `kvm_mips_build_vcpu_run()`, `kvm_mips_build_tlb_refill_exception()`, `kvm_mips_build_exception()`, and `kvm_mips_build_exit()`. Internal builders are `kvm_mips_build_enter_guest()`, `kvm_mips_build_ret_from_exit()`, `kvm_mips_build_ret_to_guest()`, `kvm_mips_build_ret_to_host()`, plus scratch/EBase helpers.

Control flow: Setup picks CP0 scratch registers, preferring KScratch registers not already used by the PGD register. The generated run function saves host callee-saved state/status/scratch registers, stores host stack and GP in the VCPU arch, switches status and EBase for guest exception vectors, then enters guest mode. Entry loads guest EPC, saves host PGD, installs the KVM GPA PGD, sets GuestCtl0.GM, configures GuestID or root ASID, disables RDHWR, restores guest GPRs and HI/LO, and executes `eret`. Generated exception vectors save guest K0/K1 and branch to the common exit handler. Exit saves guest GPRs, PC, BadVAddr, Cause, optional BadInstr/BadInstrP, restores host EBase/status/PGD/ASID/RDHWR/stack/GP, calls `kvm_mips_handle_exit()`, then either re-enters guest or unwinds to host.

State and persistence: The generated code reads/writes `struct kvm_vcpu_arch` fields for host stack/GP/PGD/EntryHi, guest EBase, guest GPRs, PC, HI/LO, FPU/MSA status registers, and saved exception CP0 fields. The emitted code resides in per-VCPU memory allocated by `mips.c` and flushed into the instruction cache.

Dependencies and integration points: Uses `uasm` emission helpers, MIPS CP0 definitions, Linux TLB refill builder helpers, `tlbmiss_handler_setup_pgd()`, VZ GuestCtl registers, KScratch/PGD conventions, FPU/MSA CSR save handling, and the C exit dispatcher `kvm_mips_handle_exit()`.

Risks: Emitted code relies on exact `struct kvm_vcpu_arch` offsets and architecture hazard ordering. Scratch register selection must avoid collision with host PGD usage. GuestID/root ASID and HTW/PGD transitions are highly ordering-sensitive. The code has comments noting assumptions about stack size and branch labels. FPU/MSA CSR clearing is intentionally tied to die-notifier recovery, so instruction offset changes in assembly helpers can break exception stepping.

Test signals: Boot/run VCPU on CPUs with/without KScratch, GuestID, HTW, VEIC/VINT, 64-bit KX, Loongson64 TLB refill, FPU, and MSA. Validate generated code dumping, guest exits for TLB/refill/general exceptions, host return codes, ASID/GuestID isolation, and FPU/MSA exception recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/entry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/fpu.S -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/fpu.S

Purpose: Provides assembly routines for saving/restoring guest FPU register state and restoring FCSR for MIPS KVM.

Important APIs, types, and functions: Exports leaf routines `__kvm_save_fpu`, `__kvm_restore_fpu`, and `__kvm_restore_fcsr`. They use offsets from `asm-offsets.h` into `struct kvm_vcpu_arch`.

Control flow: Save/restore routines inspect CP0 Status.FR by shifting status and branching. If FR=1, odd double registers are saved/restored; even registers are always handled. `__kvm_restore_fcsr` loads `VCPU_FCR31` and writes FCR31 with `ctc1`.

State and persistence: Reads/writes guest FPU state in the VCPU arch save area: FPR0-FPR31 and FCR31. Hardware FPU registers are volatile CPU state owned temporarily by the guest when KVM enables CU1.

Dependencies and integration points: Called from `mips.c` FPU ownership paths and exit re-entry handling. The `ctc1` instruction offset in `__kvm_restore_fcsr` is part of the contract with `kvm_mips_csr_die_notify()`, which steps over harmless FP exceptions caused by guest FCSR cause bits.

Risks: Offset or instruction-order changes can break die-notifier matching. FR mode handling must match the guest CP0 Status state or odd doubles can be corrupted. These routines require hard-float assembly support and correct hazard handling by callers.

Test signals: Guest FPU enable/disable, FR=0 and FR=1 modes, odd-double access rejection in userspace register APIs, migration/save-restore cycles, and FCSR values with pending exception bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/fpu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/hypcall.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/hypcall.c

Purpose: Handles MIPS KVM hypercall instruction recognition and dispatch.

Important APIs, types, and functions: `kvm_mips_emul_hypcall()` decodes the hypercall code from the instruction and returns `EMULATE_HYPERCALL` only for code 0. `kvm_mips_handle_hypcall()` reads the hypercall number from `v0` and up to four arguments from `a0`-`a3`, then calls `kvm_mips_hypercall()`. The current dispatcher reports `-KVM_ENOSYS` in `v0`.

Control flow: Emulation identifies whether a decoded instruction should become a hypercall exit/handler path. Handling extracts ABI registers, invokes the local dispatcher, and returns `RESUME_GUEST`; no userspace exit is produced for unimplemented calls.

State and persistence: Only VCPU GPR state is read and `gprs[2]` (`v0`) is overwritten with the return value. No persistent hypercall state exists.

Dependencies and integration points: Includes KVM host and paravirtual headers. It is called by the instruction emulation/guest-exit backend when a hypercall instruction is encountered.

Risks: Hypercall surface is intentionally skeletal; all numbers are unimplemented. If future calls are added, ABI width/sign handling and userspace compatibility need careful definition.

Test signals: Hypercall code 0 returns `-KVM_ENOSYS`; nonzero instruction code fails emulation; argument registers remain intact except return register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/hypcall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.c

Purpose: Delivers queued MIPS KVM virtual exceptions/interrupts to callback-provided IRQ injection logic.

Important APIs, types, and functions: `kvm_mips_deliver_interrupts()` walks `vcpu->arch.pending_exceptions_clr` and `pending_exceptions` and invokes `kvm_mips_callbacks->irq_clear()` or `irq_deliver()` for each set priority. `kvm_mips_pending_timer()` checks the timer exception bit.

Control flow: Clear requests are processed before delivery requests, preserving a deterministic priority pass through bit order. Each bit index corresponds to exception priorities defined in `interrupt.h`.

State and persistence: Uses per-VCPU bitmaps `pending_exceptions` and `pending_exceptions_clr`. The actual IRQ line state is delegated to the active KVM MIPS callback implementation.

Dependencies and integration points: Depends on `interrupt.h`, `kvm_mips_callbacks`, and exit handling in `mips.c`, which calls delivery before re-entering the guest.

Risks: The function does not clear bits itself; callback implementations must manage bitmap state correctly. Priority definitions and callback IRQ mappings must stay in sync.

Test signals: Timer, IO, and IPI queue/dequeue paths; simultaneous clear and deliver bits; Loongson priority mapping; re-entry delivery after guest exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.h -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.h

Purpose: Defines MIPS KVM exception priority numbers, timer interrupt bit helpers, and interrupt-related function declarations.

Important APIs, types, and functions: Priority constants run from `MIPS_EXC_RESET` through `MIPS_EXC_MAX`, including timer, IO, execute, and IPI priorities. `C_TI` represents the Cause.TI bit. Externs include `kvm_priority_to_irq`, `kvm_irq_to_priority()`, `kvm_mips_pending_timer()`, `kvm_mips_deliver_interrupts()`, and optional `kvm_init_loongson_ipi()`.

Control flow: This header establishes the priority ordering used by interrupt delivery and IRQ ioctl mapping. It does not execute code directly.

State and persistence: Declares the global priority-to-IRQ mapping pointer implemented in `mips.c`.

Dependencies and integration points: Used by `interrupt.c`, `mips.c`, `emulate.c`, and `loongson_ipi.c`. The priority values must match callback implementation expectations and guest CP0 Cause/IP line usage.

Risks: Priority and IRQ mapping mismatches can deliver interrupts on incorrect guest lines. `MIPS_EXC_MAX` bounds bitmap iteration, so adding priorities requires updating all arrays and loops.

Test signals: Compile-time coverage for Loongson and non-Loongson builds; IRQ-to-priority lookups for timer/IO/IPI; bitmap iteration through all declared priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/interrupt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/loongson_ipi.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/loongson_ipi.c

Purpose: Implements a Loongson-3 virtual IPI MMIO device for MIPS KVM guests.

Important APIs, types, and functions: `loongson_vipi_read()` and `loongson_vipi_write()` implement device register semantics. `kvm_ipi_read()` and `kvm_ipi_write()` adapt those helpers to `struct kvm_io_device_ops` with locking. `kvm_init_loongson_ipi()` registers four node MMIO windows on the KVM MMIO bus.

Control flow: MMIO address bits select core and node, producing an IPI state index. Reads expose status, enable, zero for set/clear, and buffer words. Writes update enable, OR status and inject IRQ 6 on SET, clear status bits and deassert IRQ 6 when all status is clear on CLEAR, or update buffer storage. Device registration initializes one `kvm_io_device` per node at `IPI_BASE + (node << 44)`.

State and persistence: State lives in `kvm->arch.ipi`, including a spinlock, per-VCPU/node `ipi_state` status/en/buffer fields, and IO-device wrappers. It persists for the VM lifetime.

Dependencies and integration points: Depends on KVM MMIO bus, `kvm_vcpu_ioctl_interrupt()`, Loongson CPU configuration, `interrupt.h`, and VM initialization in `mips.c` under `CONFIG_CPU_LOONGSON64`.

Risks: Uses `BUG_ON()` for alignment failures. It assumes core/node indexing maps into allocated `ipistate` entries and that `kvm_get_vcpu(kvm, id)` is valid. SET injects IRQ 6 regardless of `en`, so enable semantics may be incomplete or implemented elsewhere. Register width handling assumes len 4 or 8.

Test signals: MMIO read/write for status/en/set/clear/buffer, aligned access enforcement, IRQ assertion/deassertion behavior, multi-node address decoding, missing VCPU edge cases, and concurrent access under the spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/loongson_ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/mips.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/mips.c

Purpose: Provides the core MIPS architecture implementation for KVM: VM/VCPU lifecycle, run-loop entry, userspace ioctl register access, guest exit dispatch, FPU/MSA ownership, interrupt injection, stats, and module init/exit.

Important APIs, types, and functions: VM functions include `kvm_arch_init_vm()`, `kvm_arch_destroy_vm()`, shadow flush hooks, memory-region hooks, and capability checks. VCPU functions include `kvm_arch_vcpu_create()`, `kvm_arch_vcpu_destroy()`, `kvm_arch_vcpu_ioctl_run()`, register ioctls, interrupt ioctl handling, and state dump helpers. Exit handling is split between `kvm_mips_handle_exit()` and `__kvm_mips_handle_exit()`. FPU/MSA helpers include `kvm_own_fpu()`, `kvm_own_msa()`, `kvm_drop_fpu()`, and `kvm_lose_fpu()`. Init registers a die notifier and calls `kvm_init()`.

Control flow: VM creation validates type and allocates a GPA page table, optionally registering Loongson IPI MMIO. VCPU creation initializes backend callbacks, hrtimer, per-VCPU exception-handler memory, emits TLB/exception/exit/run code, flushes I-cache, and delegates setup to callbacks. Running a VCPU handles pending MMIO completion, loads VCPU state, enters guest timing and `IN_GUEST_MODE`, calls the backend run callback, accounts interrupt timing, then unloads. Guest exits enter `__kvm_mips_handle_exit()`, classify CP0 Cause exception codes, update stats, delegate most architectural handling to `kvm_mips_callbacks`, deliver pending virtual interrupts, process signals, and optionally re-enter guest.

State and persistence: Persistent VM state includes `arch.gpa_mm.pgd` and optional Loongson IPI state. VCPU state includes generated code memory, guest registers, COP0 state, hrtimer, pending exception bitmaps, `wait`, FPU/MSA live-state flags, MMIO completion fields, and scheduling CPU markers. Stats are exposed through KVM stats descriptors.

Dependencies and integration points: Integrates with generic KVM core, MIPS VZ callback table, dynamic entry builders, MMU/TLB helpers, hrtimers, tracepoints, KVM ioctl ABI, die notifiers, FPU/MSA assembly helpers, and Loongson IRQ mapping. Many operations are callback-driven, so `vz.o` supplies critical implementation details.

Risks: Exit dispatch is broad and correctness depends on callback behavior. Mode transitions use memory barriers to avoid missed TLB flush requests. Generated handler memory must fit CP0 EBase constraints. FPU/MSA ownership has tricky FR/MSA interactions and die-notifier offset coupling. `KVM_SET_ONE_REG` for 128-bit registers appears to return immediately after `copy_from_user(vs, ...)`, so the later switch handling for vector writes is unreachable in this snapshot. Several architecture ioctls are unimplemented and return `-ENOIOCTLCMD`.

Test signals: VM create/destroy, VCPU create/run/destroy, every exception dispatch path, pending signal exits, MMIO completion, register-list/get/set ABI including FPU/MSA, interrupt ioctl queue/dequeue, dirty logging transition, hrtimer wakeups, FPU/MSA enable capabilities, generated EBase range failure, Loongson priority mapping, and module init failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/mips.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/mmu.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/mmu.c

Purpose: Manages the MIPS KVM GPA page tables used to map guest physical addresses to host physical pages and supports dirty/access tracking, unmapping, and root TLB fault handling.

Important APIs, types, and functions: Allocation helpers are `kvm_pgd_alloc()` and `kvm_mmu_free_memory_caches()`. Page-table walking uses `kvm_mips_walk_pgd()` and `kvm_mips_pte_for_gpa()`. Flush and tracking APIs include `kvm_mips_flush_gpa_pt()`, `kvm_mips_mkclean_gpa_pt()`, `kvm_arch_mmu_enable_log_dirty_pt_masked()`, `kvm_unmap_gfn_range()`, `kvm_age_gfn()`, and `kvm_test_age_gfn()`. Fault handling is in `_kvm_mips_map_page_fast()`, `kvm_mips_map_page()`, and `kvm_mips_handle_vz_root_tlb_fault()`. VCPU scheduling hooks are `kvm_arch_vcpu_load()` and `kvm_arch_vcpu_put()`.

Control flow: GPA PGDs are initialized to invalid PTE/PMD tables. Fault handling first tries a fast path under `mmu_lock` to mark old pages young or writable clean pages dirty. Slow path tops up the VCPU MMU cache, samples `mmu_invalidate_seq`, faults in a PFN through KVM core, retries on invalidation races, allocates GPA page-table levels, installs a PTE with readable/cacheable/writeable bits, marks dirty on write faults, and releases the page reference. Root TLB faults map the GPA page then invalidate the matching host TLB entry.

State and persistence: VM state is `kvm->arch.gpa_mm.pgd`, a GPA page-table hierarchy. Per-VCPU state includes `arch.mmu_page_cache`, `last_sched_cpu`, and callback-owned CPU register state. Page dirty/young bits persist in GPA PTEs until flushed, aged, or cleaned.

Dependencies and integration points: Depends on Linux KVM MMU notifier sequencing, SRCU, `kvm_faultin_pfn()`, dirty-page APIs, MIPS page-table helpers, TLB invalidation in `tlb.c`, and backend callbacks for VCPU load/put. Called by `mips.c` memory-slot and VCPU lifecycle code.

Risks: Page-table walking/allocation assumes MIPS folding configuration and uses `BUG()` for unexpected `pgd_none()`. Range flush functions must free lower-level tables only when full ranges are removed. The slow path requires correct memory barriers around `mmu_invalidate_seq` to avoid stale PFNs. `kvm_arch_mmu_enable_log_dirty_pt_masked()` converts a bit mask into a continuous start/end range, so sparse masks may write-protect pages between set bits.

Test signals: GPA faults for present, absent, readonly, clean writeable, old, dirty, and MMIO/noslot pages; concurrent MMU notifier invalidation; dirty logging enable and masked updates; aging/test-age; full and partial memslot unmap; VCPU migration hrtimer restart; and root TLB fault invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/msa.S -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/msa.S

Purpose: Provides assembly routines for saving/restoring MIPS SIMD Architecture vector state and MSACSR for KVM guests.

Important APIs, types, and functions: Exports `__kvm_save_msa`, `__kvm_restore_msa`, `__kvm_restore_msa_upper`, and `__kvm_restore_msacsr`. The `kvm_restore_msa_upper` macro restores upper 64 bits of each 128-bit vector, with 64-bit and endian-specific 32-bit variants.

Control flow: Full save/restore stores or loads all 32 vector registers through `st_d`/`ld_d` macros into the FPR save area. Upper restore patches only the high half of each vector when FPU lower state is already live. MSACSR restore loads `VCPU_MSA_CSR` and writes it with `_ctcmsa`.

State and persistence: Reads/writes MSA vector state in the VCPU FPR storage and `msacsr`. Hardware MSA registers are temporary live guest CPU state when MSA is enabled.

Dependencies and integration points: Used by `mips.c` MSA ownership paths. The `_ctcmsa` instruction location is part of the die-notifier contract in `kvm_mips_csr_die_notify()` for harmless MSA FP exceptions during MSACSR restore.

Risks: Endianness and 32/64-bit paths must preserve vector lane order. Instruction offset changes in `__kvm_restore_msacsr` can break exception recovery. Upper-only restore assumes lower FPU state is already valid and FR/MSA enable sequencing is correct.

Test signals: MSA capability enable, full restore from cold state, upper restore after FPU-only state, endian-specific vector register ABI checks, MSACSR pending exception bits, and VCPU migration/save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/msa.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/stats.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/stats.c

Purpose: Provides optional COP0 access histogram strings and dumping for MIPS KVM debugging.

Important APIs, types, and functions: `kvm_cop0_str[]` maps COP0 register indices to human-readable names. `kvm_mips_dump_stats()` prints nonzero COP0 access counters when `CONFIG_KVM_MIPS_DEBUG_COP0_COUNTERS` is enabled.

Control flow: VCPU destruction calls the dump helper from `mips.c`. With debug counters disabled, the function compiles to a no-op body. With counters enabled, it iterates all COP0 register/select slots and logs nonzero counts.

State and persistence: Reads `vcpu->arch.cop0.stat[i][j]`; it does not mutate state. Output is kernel log text only.

Dependencies and integration points: Depends on `N_MIPS_COPROC_REGS`, `N_MIPS_COPROC_SEL`, and COP0 stat fields in the VCPU architecture structure. Controlled by Kconfig debug option.

Risks: Histogram strings must remain aligned with COP0 register indices. Enabling debug counters can increase overhead and produce shutdown log volume.

Test signals: VCPU teardown with debug counters enabled, accesses across multiple select values, and default no-op behavior when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/tlb.c -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/tlb.c

Purpose: Implements MIPS KVM VZ TLB helpers that must run from host kernel address space: root TLB invalidation, guest TLB lookup, local guest/root flushes, guest TLB save/load, and Loongson-specific invalidations.

Important APIs, types, and functions: Exported globals are `GUESTID_MASK`, `GUESTID_FIRST_VERSION`, and `GUESTID_VERSION_MASK`. Public helpers include `kvm_vz_host_tlb_inv()`, `kvm_vz_guest_tlb_lookup()`, `kvm_vz_local_flush_roottlb_all_guests()`, `kvm_vz_local_flush_guesttlb_all()`, `kvm_vz_save_guesttlb()`, `kvm_vz_load_guesttlb()`, and optional Loongson clear functions. Internal helpers manage root ASID and GuestCtl1.RID.

Control flow: Host TLB invalidation disables interrupts and HTW, sets root GuestID to the active guest ID when supported, probes a root TLB entry by VPN2 plus root ASID, invalidates it if found, restores EntryHi/RID/HTW, and flushes VTag I-cache if necessary. Guest TLB lookup probes guest TLB registers, reads matching EntryLo/PageMask, restores clobbered guest registers, validates the selected EntryLo, and computes GPA. Flush functions iterate root or guest TLB entries, replacing them with unique invalid entries. Save/load functions preserve guest TLB CP0 registers, set the appropriate root GuestID, then read or write indexed guest TLB entries.

State and persistence: Operates on hardware TLB and GuestCtl registers, preserving original CP0 state around operations. Save/load serializes entries into caller-provided `struct kvm_mips_tlb` buffers. GuestID globals are exported for VZ backend coordination.

Dependencies and integration points: Depends on CP0/TLB hazard helpers, HTW controls, CPU type data, GuestID/VZ registers, MIPS ASID context, and Loongson diagnostic registers. Called by MMU fault handling, VZ backend code, and remote flush paths.

Risks: These functions are highly sensitive to interrupt disabling, HTW state, hazard barriers, and CP0 register restoration. `BUG_ON(idx >= tlbsize)` can panic on unexpected probe state. Guest TLB lookup explicitly does not handle MIPS32 XPA PFN splitting. Root GuestID must be cleared or host root TLB operations can target guest entries accidentally.

Test signals: Root TLB invalidation with and without GuestID, guest TLB lookup hit/miss/invalid-entry cases, full root and guest flushes, Octeon3 machine-check inhibit path, save/load ranges with foreign GuestID entries, Loongson VTLB/FTLB invalidation, and HTW restart after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/trace.h -->
## sources/distributed-fs/ceph-client/arch/mips/kvm/trace.h

Purpose: Defines tracepoints and symbolic decoding tables for MIPS KVM transitions, exits, hardware register accesses, auxiliary FPU/MSA state changes, ASID/GuestID changes, and guest-mode state snapshots.

Important APIs, types, and functions: Trace events include `kvm_enter`, `kvm_reenter`, `kvm_out`, `kvm_exit`, `kvm_hwr`, `kvm_aux`, `kvm_asid_change`, `kvm_guestid_change`, and `kvm_guest_mode_change`. It declares `kvm_trace_guest_mode_change` plus registration hooks implemented in `mips.c`. Symbol tables map exit reasons, COP0/HWR operations, and auxiliary state operations to strings.

Control flow: Tracepoints capture fields from `struct kvm_vcpu` and COP0 accessors at call sites in the KVM backend. `TRACE_EVENT_FN(kvm_guest_mode_change, ...)` toggles a global flag through registration/unregistration callbacks, allowing expensive guest-mode-change tracing to be gated.

State and persistence: Trace events are transient kernel tracing records. Persistent state is limited to the global guest-mode-change trace enable flag.

Dependencies and integration points: Includes Linux tracepoint infrastructure and `trace/define_trace.h`. Used by `mips.c`, `emulate.c`, and auxiliary ownership paths. Exit reason constants align with MIPS Cause.ExcCode and VZ GuestCtl0.GExcCode values.

Risks: Symbolic constants must stay aligned with exit dispatch and VZ exception definitions or traces become misleading. Tracepoint field sizes use `unsigned long`, `u8`, and `u16`; ABI changes should preserve trace consumers. Guest-mode-change trace reads COP0 state and should remain gated to avoid overhead.

Test signals: Enable ftrace/perf events for guest enter/exit, MMIO/hardware register emulation, FPU/MSA ownership, ASID/GuestID rollover, and guest-mode-change registration; verify printed symbolic names match actual exit causes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/kvm/trace.h -->
