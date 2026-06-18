# subset-b-000818 research

This grouped report covers RISC-V KVM SBI/vCPU support, low-level RISC-V library routines, and RISC-V memory-management code under the Ceph client source tree. Each section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi.c

## Purpose
`vcpu_sbi.c` is the central RISC-V KVM SBI dispatcher. It defines the ordered SBI extension table, records per-vCPU extension availability, routes guest ECALLs to extension handlers, forwards unsupported/vendor calls to userspace, and exposes SBI extension and extension-state registers through KVM ONE_REG.

## Important APIs, Types, And Functions
The key table is `sbi_ext[]`, whose entries bind `KVM_RISCV_SBI_EXT_*` ids to `struct kvm_vcpu_sbi_extension` implementations. `kvm_vcpu_sbi_find_ext()` finds an enabled handler by SBI extension id. `kvm_riscv_vcpu_sbi_ecall()` is the hot-path ECALL dispatcher. `kvm_riscv_vcpu_sbi_forward_handler()` formats `KVM_EXIT_RISCV_SBI` for userspace. `kvm_riscv_vcpu_sbi_system_reset()`, `kvm_riscv_vcpu_sbi_request_reset()`, and `kvm_riscv_vcpu_sbi_load_reset_state()` coordinate reset and boot state. ONE_REG support is split between extension enable registers and extension-specific state registers.

## Control Flow
Initialization probes every extension, marks it unavailable/disabled/enabled, and calls optional per-extension init. An ECALL reads `a7` as extid and `a6` as funcid, looks up a handler, executes it, then either advances `sepc`, redirects a virtual trap, exits to userspace, or returns SBI error/output values in `a0/a1`. State register enumeration skips disabled extensions and delegates register layout to each extension when available.

## State And Persistence
State is per-vCPU in `arch.sbi_context.ext_status`, `return_handled`, extension private state, and reset state protected by `reset_state.lock`. System reset writes all vCPUs to stopped MP state and requests sleep. There is no disk persistence; migration persistence is via ONE_REG state.

## Dependencies And Integration Points
This file integrates all RISC-V KVM SBI extension modules, KVM run exits, KVM ONE_REG, vCPU MP state, reset requests, and trap redirection. Userspace VMMs observe forwarded calls through `run->riscv_sbi` and system events through `KVM_EXIT_SYSTEM_EVENT`.

## Risks
Extension status and default-disabled behavior are ABI-sensitive. ECALL completion must advance `sepc` exactly once and must not clobber `a1` for SBI v0.1 semantics. ONE_REG setters reject changes after a vCPU has run, which is important for migration correctness. Forwarded calls rely on userspace returning through `kvm_riscv_vcpu_sbi_return()` exactly once.

## Test Signals
Useful tests boot guests using legacy and modern SBI, probe enable/disable through ONE_REG, migrate FWFT/STA state, exercise vendor/experimental forwarding, and verify reset/shutdown exits and unsupported extension return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_base.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_base.c

## Purpose
`vcpu_sbi_base.c` implements the SBI BASE extension for RISC-V KVM guests. It answers specification, implementation, machine identity, and extension probing queries.

## Important APIs, Types, And Functions
`kvm_sbi_ext_base_handler()` handles `GET_SPEC_VERSION`, `GET_IMP_ID`, `GET_IMP_VERSION`, `PROBE_EXT`, `GET_MVENDORID`, `GET_MARCHID`, and `GET_MIMPID`. `vcpu_sbi_ext_base` exports the handler for `SBI_EXT_BASE`.

## Control Flow
The handler switches on guest `a6`. Most calls fill `retdata->out_val` directly. `PROBE_EXT` forwards experimental and vendor probes to userspace; otherwise it calls `kvm_vcpu_sbi_find_ext()` and optional extension probes. Unknown functions set `SBI_ERR_NOT_SUPPORTED`.

## State And Persistence
The file does not own mutable state. It reads per-vCPU architectural id fields and effective extension availability maintained by `vcpu_sbi.c`.

## Dependencies And Integration Points
It depends on Linux version metadata, SBI constants, and the shared KVM SBI dispatcher. Guest firmware and operating systems use this extension to discover the virtual SBI surface.

## Risks
Probe behavior is ABI-visible. Experimental/vendor ranges must remain forwardable so userspace VMMs can implement policy. Reported implementation version is `LINUX_VERSION_CODE`, so guests can infer host kernel lineage.

## Test Signals
Run SBI probe selftests for every enabled/disabled extension, legacy guests expecting BASE, and userspace-forwarding tests for vendor/experimental ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_forward.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_forward.c

## Purpose
`vcpu_sbi_forward.c` declares SBI extension descriptors whose calls are intentionally handled by userspace rather than KVM kernel code.

## Important APIs, Types, And Functions
It exports `vcpu_sbi_ext_experimental`, `vcpu_sbi_ext_vendor`, `vcpu_sbi_ext_dbcn`, and `vcpu_sbi_ext_mpxy`. Each descriptor maps an SBI extension range or id to `kvm_riscv_vcpu_sbi_forward_handler()`. DBCN and MPXY are default-disabled.

## Control Flow
When the central dispatcher finds one of these descriptors and it is enabled, control jumps to the shared forward handler, which populates `KVM_EXIT_RISCV_SBI` and exits the KVM_RUN ioctl to userspace.

## State And Persistence
No private state is kept. Enabled/disabled status lives in the vCPU SBI context and can be exposed through SBI extension ONE_REG controls before first run.

## Dependencies And Integration Points
This file is a policy bridge between kernel KVM and VMM userspace for debug console, message proxy, vendor, and experimental SBI behavior.

## Risks
Default-disabled extensions must not be accidentally exposed to guests. VMMs need to handle forwarded calls and write return values; otherwise guests see not-supported defaults or hang.

## Test Signals
Tests should enable DBCN/MPXY via ONE_REG, confirm KVM exits with expected extension/function ids and argument registers, and verify disabled extensions probe as absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_forward.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_fwft.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_fwft.c

## Purpose
`vcpu_sbi_fwft.c` implements the SBI Firmware Features extension for KVM. It virtualizes feature discovery, set/get calls, lock flags, and migration-visible state for currently supported FWFT features.

## Important APIs, Types, And Functions
`struct kvm_sbi_fwft_feature` describes a feature id, ONE_REG base, support probe, reset, set, and get callbacks. Implemented features include misaligned exception delegation and, on 64-bit, pointer masking PMLEN. `kvm_sbi_ext_fwft_handler()` handles guest `SBI_EXT_FWFT_SET/GET`. `kvm_sbi_ext_fwft_{init,deinit,reset}` manage per-vCPU configs. `kvm_sbi_ext_fwft_get_reg_id/get_reg/set_reg` expose state via ONE_REG.

## Control Flow
Init allocates a config array, probes each feature, and enables supported features. Guest set/get first validates that the feature is known and enabled, honors lock flags, then invokes the feature callback. ONE_REG access maps every feature to three registers: enabled, flags, and value.

## State And Persistence
State lives in allocated `fwft->configs` plus architectural config bits such as `arch.cfg.hedeleg`, `arch.cfg.henvcfg`, and probed pointer-masking capability flags. Reset clears locks and restores feature values. ONE_REG is the migration persistence surface.

## Dependencies And Integration Points
The file depends on RISC-V CSR helpers, ISA probing, `misaligned_traps_can_delegate()`, `SMNPM`, and shared KVM SBI state register plumbing. It directly writes `CSR_HEDELEG` and `CSR_HENVCFG` on in-guest set operations.

## Risks
CSR updates must distinguish live guest SBI calls from ONE_REG restore, because migration restore should update memory state without touching the currently loaded CSR unexpectedly. Lock semantics are guest-visible. Pointer-masking probing mutates HENVCFG temporarily and must preserve host expectations.

## Test Signals
Probe FWFT in guests, set/get misaligned delegation, restore ONE_REG state before first run, test lock denial, and test PMLEN 0/7/16 behavior on hosts with and without SMNPM support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_fwft.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_hsm.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_hsm.c

## Purpose
`vcpu_sbi_hsm.c` implements the SBI Hart State Management extension for KVM vCPUs: start, stop, status, and retentive suspend handling.

## Important APIs, Types, And Functions
`kvm_sbi_hsm_vcpu_start()`, `kvm_sbi_hsm_vcpu_stop()`, and `kvm_sbi_hsm_vcpu_get_status()` operate on vCPU MP state. `kvm_sbi_ext_hsm_handler()` decodes SBI function ids. `vcpu_sbi_ext_hsm` registers the extension.

## Control Flow
Start resolves the target hart id, locks its `mp_state_lock`, verifies it is stopped, stores reset pc/a1, and powers it on. Stop locks the current vCPU and powers it off if not already stopped. Status returns stopped, suspended when generic blocking is set, or started. Retentive suspend maps to KVM WFI; non-retentive suspend is unsupported.

## State And Persistence
The file mutates vCPU MP state and reset state. It does not persist to disk; reset pc/a1 and MP state are part of VM/vCPU runtime and migration state elsewhere.

## Dependencies And Integration Points
It integrates with KVM vCPU lookup, `mp_state_lock`, `kvm_riscv_vcpu_sbi_request_reset()`, power on/off helpers, and WFI blocking.

## Risks
Start/stop races depend on correct lock use. Invalid hart ids and already-started harts must return SBI errors rather than Linux errno. Status uses `stat.generic.blocking` as a suspended signal, which is an approximation.

## Test Signals
SBI HSM guest tests should start secondary vCPUs, reject duplicate starts, stop and restart harts, query status during WFI, and validate suspend return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_hsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_pmu.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_pmu.c

## Purpose
`vcpu_sbi_pmu.c` implements the SBI PMU extension dispatch layer. It translates SBI calls into KVM RISC-V PMU helper operations.

## Important APIs, Types, And Functions
`kvm_sbi_ext_pmu_handler()` handles counter count/info, config-match, start, stop, firmware counter read/read-hi, snapshot shared memory, and event info. `kvm_sbi_ext_pmu_probe()` reports availability from `kvpmu->init_done`. `vcpu_sbi_ext_pmu` exports the descriptor.

## Control Flow
The handler first rejects all calls when PMU init is not done. It switches on `a6`, reconstructs 64-bit arguments from paired registers on RV32, and delegates to PMU helpers. Some perf setup failures intentionally return SBI errors to the guest without aborting KVM_RUN.

## State And Persistence
PMU state lives in `struct kvm_pmu` and perf events outside this file. This file only reads initialization state and routes requests.

## Dependencies And Integration Points
It depends on `asm/csr.h`, SBI PMU constants, and KVM PMU helpers for counters, firmware events, snapshots, and event metadata.

## Risks
RV32 argument packing is easy to break. PMU setup errors should remain guest-visible SBI failures, not userspace exits. Probe state must match actual PMU init to avoid advertising dead counters.

## Test Signals
KVM PMU selftests, guest `perf` use, RV32 high-half reads, snapshot shared-memory tests, and disabled-PMU probe tests are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_replace.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_replace.c

## Purpose
`vcpu_sbi_replace.c` implements SBI v0.2 replacement extensions for timer, IPI, RFENCE, and system reset.

## Important APIs, Types, And Functions
Handlers include `kvm_sbi_ext_time_handler()`, `kvm_sbi_ext_ipi_handler()`, `kvm_sbi_ext_rfence_handler()`, and `kvm_sbi_ext_srst_handler()`. Exported descriptors are `vcpu_sbi_ext_time`, `vcpu_sbi_ext_ipi`, `vcpu_sbi_ext_rfence`, and `vcpu_sbi_ext_srst`.

## Control Flow
TIME validates `SET_TIMER`, forms the next cycle value, increments firmware PMU accounting, and programs the vCPU timer. IPI iterates vCPUs selected by hbase/hmask and injects VS software interrupts. RFENCE translates remote fence requests into KVM fence/hfence requests with the current VMID. SRST maps shutdown/reboot to KVM system event exits.

## State And Persistence
The file updates timer state, pending interrupt state, PMU firmware counters, system event exit state, and indirectly remote TLB/icache request queues. There is no disk persistence.

## Dependencies And Integration Points
It integrates with KVM timer, interrupt injection, PMU firmware counters, RISC-V TLB/fence helpers, VMID management, and userspace-visible KVM reset/shutdown events.

## Risks
Hart mask validation is guest ABI-sensitive; partial IPI delivery must report invalid parameters. RFENCE range interpretation must preserve zero/-1 full-range semantics. SRST must stop all vCPUs and exit cleanly to userspace.

## Test Signals
Run guest timer tests, SMP IPI tests with sparse hart masks, TLB shootdown stress, reboot/shutdown SBI tests, and PMU firmware event counter checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_replace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_sta.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_sta.c

## Purpose
`vcpu_sbi_sta.c` implements SBI Steal-Time Accounting for RISC-V KVM. It lets a guest provide a shared memory page where KVM records host scheduling delay.

## Important APIs, Types, And Functions
`kvm_riscv_vcpu_record_steal_time()` updates the guest `sbi_sta_struct`. `kvm_sbi_sta_steal_time_set_shmem()` validates and registers guest shared memory. `kvm_sbi_ext_sta_handler()` handles `STEAL_TIME_SET_SHMEM`. State register callbacks expose `shmem_lo` and `shmem_hi`.

## Control Flow
Set-shmem rejects nonzero flags, accepts the disable sentinel, checks 64-byte alignment, builds RV32 high bits when needed, zeroes the guest structure with `kvm_vcpu_write_guest()`, then records the GPA and current run delay. Record path maps the GPA to HVA, increments the sequence field before and after updating the little-endian steal value, marks the page dirty, and disables the GPA on invalid mapping.

## State And Persistence
Per-vCPU state is `arch.sta.shmem` and `arch.sta.last_steal`. Guest-visible persistence is the shared memory structure. Migration state is available through SBI state ONE_REG registers.

## Dependencies And Integration Points
It depends on scheduler `sched_info`, KVM guest memory translation, user access helpers for HVA writes, dirty logging, and the shared SBI dispatcher.

## Risks
The shared memory structure must remain within one page, hence strict 64-byte alignment. HVA errors must not continue writing stale addresses. Sequence updates are lockless and rely on guest seqlock-style reads.

## Test Signals
Enable STA in a guest, validate nonzero steal accumulation under vCPU preemption, test dirty logging, disable sentinel handling, alignment rejection, and migration restore of shmem registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_system.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_system.c

## Purpose
`vcpu_sbi_system.c` implements the SBI System Suspend extension wrapper for KVM.

## Important APIs, Types, And Functions
`kvm_sbi_ext_susp_handler()` handles `SBI_EXT_SUSP_SYSTEM_SUSPEND`. `vcpu_sbi_ext_susp` registers the extension as default-disabled.

## Control Flow
The handler validates suspend-to-RAM type, verifies the guest is in supervisor mode, checks the resume address GPA is valid, requires all other vCPUs to be stopped, stores reset state for the current vCPU, and forwards the actual suspend operation to userspace.

## State And Persistence
It records current-vCPU reset pc and opaque argument through shared reset-state helpers. It otherwise relies on userspace for suspend persistence and platform behavior.

## Dependencies And Integration Points
The file integrates SBI dispatch, KVM guest address validation, HSM stopped-state checks, reset-state helpers, and `KVM_EXIT_RISCV_SBI` forwarding.

## Risks
Suspend is default-disabled because userspace policy is required. Incorrect privilege, address, or stopped-vCPU checks could let a guest enter an impossible resume state. Forwarded calls depend on VMM support.

## Test Signals
Tests should verify disabled probe behavior, enable-and-forward exits, invalid type/address/privilege errors, and denial when another vCPU is still running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_v01.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_v01.c

## Purpose
`vcpu_sbi_v01.c` implements legacy SBI v0.1 calls for older RISC-V guests.

## Important APIs, Types, And Functions
`kvm_sbi_ext_v01_handler()` handles legacy set timer, clear/send IPI, shutdown, console forwarding, remote fence.i, and remote sfence.vma variants. `vcpu_sbi_ext_v01` registers the legacy extension id range.

## Control Flow
The handler switches on `a7` rather than `a6`. Console calls are forwarded to userspace. Timer and shutdown use modern KVM timer/reset helpers. IPI and RFENCE obtain a hart mask either from guest memory through `kvm_riscv_vcpu_unpriv_read()` or from the online vCPU count, then inject interrupts or issue fence requests.

## State And Persistence
It updates timer compare state, VS software interrupt pending bits, system event exit state, and remote TLB/icache request state. No private persistent state is owned.

## Dependencies And Integration Points
It integrates legacy SBI ABI, unprivileged guest memory reads, KVM timer, interrupt injection, VMID-based hfence helpers, and userspace console handling.

## Risks
Legacy calls use different return conventions and the top-level dispatcher must avoid writing `a1`. Guest memory faults during mask reads are redirected through `retdata->utrap`. Mask construction from online vCPU count must avoid invalid vCPU ids.

## Test Signals
Boot older firmware/guest images, exercise console forwarding, legacy IPI/fence calls with NULL and explicit masks, timer programming, and shutdown exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_v01.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_switch.S -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_switch.S

## Purpose
`vcpu_switch.S` is the low-level RISC-V KVM world-switch and floating-point save/restore code. It moves execution between host supervisor context and guest virtual supervisor context.

## Important APIs, Types, And Functions
Macros save and restore host/guest GPRs and CSRs: `SAVE_HOST_GPRS`, `SAVE_HOST_AND_RESTORE_GUEST_CSRS`, `RESTORE_GUEST_GPRS`, `SAVE_GUEST_GPRS`, `SAVE_GUEST_AND_RESTORE_HOST_CSRS`, and `RESTORE_HOST_GPRS`. Exported entry points are `__kvm_riscv_switch_to`, `__kvm_riscv_nacl_switch_to`, `__kvm_riscv_unpriv_trap`, and F/D floating-point save/restore functions under `CONFIG_FPU`.

## Control Flow
The normal switch saves host registers to `struct kvm_vcpu_arch`, swaps SSTATUS/STVEC/SEPC/SSCRATCH to guest values, restores guest GPRs, and enters with `sret`. Trap return lands on the host resume label, saves guest GPR/CSR state, restores host CSR/GPR state, and returns to C. NaCl switch uses an SBI ECALL instead of `sret`. The unpriv trap handler records trap CSRs and advances SEPC by one 4-byte instruction.

## State And Persistence
The file mutates only in-memory CPU context fields and architectural CSRs. FP helpers serialize FCSR and all F registers into the KVM context.

## Dependencies And Integration Points
It depends on asm offset definitions matching `struct kvm_vcpu_arch`, CSR numbers, RISC-V calling convention, and KVM C code that prepares/load/saves optional FPU/vector state around this switch.

## Risks
Any offset drift corrupts host or guest state. The unpriv trap handler assumes a 4-byte instruction. CSR ordering around SSTATUS/STVEC/SSCRATCH is critical for safe trap return. FP helpers must restore SSTATUS after temporarily enabling FS.

## Test Signals
Signals include guest boot under interrupt load, nested-acceleration path tests, FPU-heavy guest workloads, unprivileged emulation fault tests, and objtool/assembler checks against generated offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_switch.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_timer.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_timer.c

## Purpose
`vcpu_timer.c` virtualizes the RISC-V timer for KVM guests. It handles time delta, compare programming, hrtimer fallback, SSTC support, ONE_REG timer state, and save/restore around vCPU scheduling.

## Important APIs, Types, And Functions
`kvm_riscv_current_cycles()`, `kvm_riscv_delta_cycles2ns()`, hrtimer callbacks, `kvm_riscv_vcpu_timer_next_event()`, `kvm_riscv_vcpu_timer_pending()`, timer get/set ONE_REG handlers, init/deinit/reset, restore/sync/save, and `kvm_riscv_guest_timer_init()` are the main APIs.

## Control Flow
Without SSTC, next-event clears pending timer interrupt and starts an hrtimer that injects `IRQ_VS_TIMER` at expiry. With SSTC, next-event writes `VSTIMECMP`; VM exit syncs the CSR back into `next_cycles`, save disables host-local `VSTIMECMP`, and blocking vCPUs get an hrtimer to wake them. Time register writes adjust guest `time_delta`.

## State And Persistence
Per-vCPU state includes `next_cycles`, `next_set`, `sstc_enabled`, `init_done`, hrtimer, and function pointer. Per-VM state includes `time_delta`, `nsec_mult`, and `nsec_shift`. ONE_REG exposes frequency, time, compare, and state.

## Dependencies And Integration Points
It depends on `riscv_timebase`, clocksource conversion helpers, hrtimer, NaCl CSR wrappers, KVM interrupts, KVM blocking hooks, and the SBI TIME handler.

## Risks
Timer behavior differs sharply between SSTC and hrtimer fallback. RV32 high/low CSR write ordering must prevent transient wrong compare values. `set_reg_timer(state)` uses the provided register value as a next-event argument when enabling, so migration tooling must set compare before state.

## Test Signals
Guest clockevent tests, timer interrupt latency checks, migration of timer ONE_REG state, blocking WFI wakeups, SSTC vs non-SSTC host coverage, and RV32 compare tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_vector.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_vector.c

## Purpose
`vcpu_vector.c` manages RISC-V vector extension state for KVM vCPUs, including allocation, reset, lazy save/restore, and ONE_REG access to vector CSRs/registers.

## Important APIs, Types, And Functions
Under `CONFIG_RISCV_ISA_V`, it defines vector reset, guest/host vector save/restore, vector context allocation/free, and helper cleanup. `kvm_riscv_vcpu_vreg_addr()` maps ONE_REG ids to vector CSR fields or per-register data. `kvm_riscv_vcpu_get_reg_vector()` and `set_reg_vector()` copy state to/from userspace.

## Control Flow
Reset disables VS bits, sets `vlenb`, and either zeroes allocated vector state and marks initial state or marks vector off when the guest ISA lacks V. Save only writes dirty guest state; restore skips off state. ONE_REG access first verifies guest V availability, validates sizes, and computes addresses inside `vector.datap`.

## State And Persistence
Per-vCPU guest and host contexts own vector data buffers sized by `riscv_v_vsize`. CSRs and 32 vector registers are migration-visible through ONE_REG. `vlenb` is read-only in practice and must match host-derived value.

## Dependencies And Integration Points
It depends on host vector support, guest ISA bitmaps, vector assembly helpers, KVM vCPU create/destroy paths, and userspace migration code.

## Risks
Buffer allocation must be paired and freed on partial failure. Register size validation must use `riscv_v_vsize / 32`. Saving/restoring when VS is dirty/clean/off must preserve guest lazy-vector semantics and not leak host vector state.

## Test Signals
Run vector-enabled guests, migration with vector registers, negative ONE_REG size tests, no-V guest tests, and host vector stress during KVM entry/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_vector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vm.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vm.c

## Purpose
`vm.c` implements RISC-V architecture-specific KVM VM lifecycle, VM capabilities, IRQ routing, and selected VM ioctls.

## Important APIs, Types, And Functions
`kvm_arch_init_vm()` allocates G-stage page tables, initializes VMID, AIA, and guest timer. `kvm_arch_destroy_vm()` destroys vCPUs and AIA state. IRQ APIs include `kvm_vm_ioctl_irq_line()`, `kvm_set_msi()`, `kvm_riscv_setup_default_irq_routing()`, `kvm_set_routing_entry()`, and `kvm_arch_set_irq_inatomic()`. Capability paths are `kvm_vm_ioctl_check_extension()` and `kvm_vm_ioctl_enable_cap()`.

## Control Flow
VM init unwinds page-table allocation if VMID init fails. IRQ routing converts user routing entries to in-kernel callbacks for AIA IRQ or MSI injection. Capability queries return booleans or numeric limits. Enabling GPA bits validates requested G-stage levels, then under `kvm->lock` and `slots_lock` rejects changes after vCPU creation or memslot population.

## State And Persistence
VM state includes G-stage PGD, VMID metadata, AIA state, timer conversion state, MP reset mode, and configured G-stage page-table levels. All state is in-memory and VMM-managed through KVM APIs.

## Dependencies And Integration Points
It integrates KVM common VM lifecycle, RISC-V MMU/G-stage, VMID allocator, AIA irqchip/MSI, memory slots, and capability ABI exposed to userspace VMMs.

## Risks
Capability values are ABI. GPA-bit changes must be locked and denied once memory/vCPUs exist. MSI injection ignores deasserted level. VM destroy relies on common KVM vCPU destruction before AIA cleanup.

## Test Signals
KVM selftests for capability probing, VM GPA bits, irqchip routing/MSI delivery, memory-slot ordering, and VM lifecycle failure unwind are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vmid.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vmid.c

## Purpose
`vmid.c` allocates and rolls RISC-V G-stage VMIDs for KVM guests so guest TLB entries can be tagged and invalidated safely.

## Important APIs, Types, And Functions
`kvm_riscv_gstage_vmid_detect()` probes hardware VMID width. `kvm_riscv_gstage_vmid_init()` initializes per-VM ids. `kvm_riscv_gstage_vmid_ver_changed()` checks version staleness. `kvm_riscv_gstage_vmid_update()` allocates or refreshes VMIDs and requests HGATP updates.

## Control Flow
Boot-time detection writes a max VMID into HGATP, reads back implemented bits, clears HGATP, and flushes guest TLBs. Update returns if VMID version is current; otherwise under `vmid_lock` it rechecks, rolls global version and flushes all CPUs when ids wrap, assigns the next VMID, stores the global version, and requests `KVM_REQ_UPDATE_HGATP` on all vCPUs.

## State And Persistence
Global state is `vmid_version`, `vmid_next`, `vmid_bits`, and `vmid_lock`. Per-VM state is `kvm->arch.vmid`. State is runtime only and recomputed across host boot.

## Dependencies And Integration Points
It depends on HGATP CSR access, G-stage mode selection, local hfence helpers, CPU masks, and KVM request delivery to vCPUs.

## Risks
VMID wrap requires global guest TLB flush and vCPU HGATP updates. Insufficient VMID bits disables tagging. Bit arithmetic around `(1 << vmid_bits)` must match supported widths.

## Test Signals
Stress many VMs/vCPUs to force VMID rollover, verify remote TLB flushes, and run guest memory isolation tests across VMID reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vmid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/Makefile

## Purpose
This Makefile selects architecture-specific RISC-V library routines for the kernel build.

## Important APIs, Types, And Functions
It includes delay, memcpy, memset, memmove, checksum, uaccess, 128-bit shift helpers, Zicboz clear-page, vector helper, and optional error-injection objects. String routines are excluded under generic/software-tag KASAN so instrumented generic implementations can be used.

## Control Flow
Kbuild conditionals add objects based on `CONFIG_MMU`, `CONFIG_64BIT`, `CONFIG_RISCV_ISA_V`, `CONFIG_RISCV_ISA_ZICBOZ`, `CONFIG_FUNCTION_ERROR_INJECTION`, and KASAN modes.

## State And Persistence
No runtime state is defined. Build configuration determines which symbols exist in the final kernel.

## Dependencies And Integration Points
It integrates assembly/C helper objects with core kernel library symbols such as `memcpy`, `clear_user`, checksums, and string APIs.

## Risks
Changing object conditions can break early boot, user access, KASAN compatibility, or missing compiler helper symbols on 64-bit builds.

## Test Signals
Build matrix coverage across MMU/no-MMU, 32/64-bit, KASAN, vector, Zicboz, and error-injection configs is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/clear_page.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/clear_page.S

## Purpose
`clear_page.S` provides an optimized RISC-V `clear_page()` implementation using Zicboz cache-block zero when available, with a memset fallback.

## Important APIs, Types, And Functions
`clear_page` is the exported symbol. `CBOZ_ALT` wraps alternative patching for block-size-specific loop exits. The code reads `riscv_cboz_block_size` and emits repeated `CBO_ZERO` operations.

## Control Flow
The function starts with PAGE_SIZE bytes. If Zicboz is absent or the block size is too large, it tails to `__memset(page, 0, PAGE_SIZE)`. Otherwise it loops over cache blocks, using alternatives for block-size orders 8 through 12 to minimize loop overhead.

## State And Persistence
It writes zeros to one physical page through the provided virtual address. No persistent state is held.

## Dependencies And Integration Points
It depends on alternative patching, RISC-V hwcap detection, CBO instruction definitions, `riscv_cboz_block_size`, and the generic page allocator/users that call `clear_page()`.

## Risks
Wrong block-size assumptions can overrun or under-clear pages. Alternative order encoding must match discovered CBOZ size. Fallback must be available before and after boot alternatives.

## Test Signals
Boot on Zicboz and non-Zicboz systems, page allocator poisoning/zero-page tests, and memory selftests checking newly allocated zero pages are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/clear_page.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/csum.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/csum.c

## Purpose
`csum.c` implements RISC-V Internet checksum helpers, including optimized IPv6 pseudo-header checksum on 64-bit and the generic `do_csum()` buffer checksum.

## Important APIs, Types, And Functions
`csum_ipv6_magic()` is exported on non-RV32. `do_csum_common()` accumulates word-sized data and carry. `do_csum_with_alignment()` handles misaligned buffers using controlled over-reads and KASAN checks. `do_csum_no_alignment()` is used for aligned or fast-misaligned systems. `do_csum()` chooses the path.

## Control Flow
The code performs word-sized additions, folds carry, masks over-read bytes at head/tail, and folds to 16 bits. When Zbb and toolchain support are present, inline assembly uses bit-manipulation instructions for rotation, byte reversal, and faster folding.

## State And Persistence
No state is retained. It reads packet memory and returns checksum values.

## Dependencies And Integration Points
It depends on KASAN read checking, RISC-V feature static keys, endian configuration, network checksum types, and optional Zbb toolchain support.

## Risks
The alignment path intentionally over-reads within aligned words; KASAN checks and same-page/cache-line assumptions are important. Endian and offset folding must preserve Internet checksum semantics. Inline asm variants must match C fallback results.

## Test Signals
Network checksum selftests, IPv6 traffic tests, KASAN builds, misaligned buffer tests, RV32/RV64 builds, and Zbb vs non-Zbb comparison tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/csum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/delay.c

## Purpose
`delay.c` provides RISC-V busy-wait delay primitives backed by the cycle counter and calibrated loop constants.

## Important APIs, Types, And Functions
`__delay()` spins until a cycle delta elapses. `udelay()` converts microseconds to cycles, using a fast scaled `lpj_fine` path for small delays and `riscv_timebase` division for larger ones. `ndelay()` performs nanosecond conversion with a 64-bit scaled multiplier.

## Control Flow
`__delay()` snapshots `get_cycles()` and loops with `cpu_relax()`. `udelay()` chooses between fixed-point multiplication and direct timebase conversion based on `MAX_UDELAY_US`. `ndelay()` always uses the scaled nanosecond conversion.

## State And Persistence
The file reads `lpj_fine`, `riscv_timebase`, and the cycle counter. It stores no state.

## Dependencies And Integration Points
It integrates with kernel delay APIs and early/driver code that requires busy waits before scheduler timers are usable.

## Risks
Integer scaling constants assume `HZ <= 1000`. Very inaccurate timebase or cycle counter behavior affects all busy waits. Busy-wait delays burn CPU and must not be used for long sleeps.

## Test Signals
Boot timing sanity, driver delay-sensitive hardware tests, and build-time checks for HZ limits are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/error-inject.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/error-inject.c

## Purpose
`error-inject.c` supports function error injection on RISC-V by skipping the probed function body and returning immediately.

## Important APIs, Types, And Functions
`override_function_with_return()` sets the instruction pointer in `pt_regs` to the return address register. It is marked `NOKPROBE_SYMBOL`.

## Control Flow
When error injection triggers at function entry, the helper changes `regs->epc`/instruction pointer to `regs->ra`, causing execution to resume at the caller return site.

## State And Persistence
It mutates only the live trap/register frame. No persistent state is stored.

## Dependencies And Integration Points
It depends on kprobes, Linux error-injection framework, and RISC-V `pt_regs` layout.

## Risks
This must not itself be probed. It assumes the return address register contains a valid call return address and is only safe for functions approved by the error injection framework.

## Test Signals
Function error injection selftests and kprobe tests on RISC-V validate the behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/error-inject.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/memcpy.S

## Purpose
`memcpy.S` implements RISC-V `memcpy` and early-boot aliases for non-overlapping memory copies.

## Important APIs, Types, And Functions
`__memcpy` is the main symbol, with weak `memcpy` and `__pi_memcpy` aliases. It uses byte copying for small or poorly aligned cases and unrolled word copying for co-aligned large buffers.

## Control Flow
The function preserves the destination return value, rejects word copy for sizes under 128 or mismatched low alignment, byte-copies to alignment, runs a 16*SZREG unrolled load/store loop, and finishes with word or byte tail copying.

## State And Persistence
It writes `n` bytes to destination and keeps no state.

## Dependencies And Integration Points
It uses RISC-V ABI register conventions and `SZREG` macros. It is used throughout the kernel, including position-independent early code through aliases.

## Risks
`memcpy` does not handle overlap; callers needing overlap must use `memmove`. Alignment and tail handling must preserve return value in `a0`. Early boot aliases require this code to remain relocation-safe.

## Test Signals
lib/string tests, boot smoke tests, KASAN-excluded build variants, and randomized alignment/size memcpy tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memcpy.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memmove.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/memmove.S

## Purpose
`memmove.S` implements overlap-safe RISC-V memory copying with forward and reverse paths.

## Important APIs, Types, And Functions
`__memmove` is the main symbol, with weak `memmove` and `__pi_memmove` aliases. Internal labels implement byte copy, co-aligned word copy, and misaligned fixup copy in both directions.

## Control Flow
The function returns immediately for identical pointers or zero length. It decides forward vs reverse based on source/destination order, byte-copies small ranges, aligns destination, then uses co-aligned word loops or shift-combine loops for misaligned source. Reverse paths copy from the end to preserve overlapping source bytes.

## State And Persistence
It writes destination memory and stores no state.

## Dependencies And Integration Points
It depends on little-endian shift direction, RISC-V calling convention, `SZREG`, and early boot aliases.

## Risks
The file explicitly notes big-endian would require reversed shifts. Overlap correctness depends on exact direction selection and tail byte loops. Misaligned fixup loops are complex and sensitive to off-by-one endpoints.

## Test Signals
Randomized overlap tests across all alignments and lengths, early boot use, and lib/string selftests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memmove.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memset.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/memset.S

## Purpose
`memset.S` implements RISC-V `memset` and early aliases.

## Important APIs, Types, And Functions
`__memset` is the main symbol, with weak `memset` and `__pi_memset` aliases. It uses byte fill for small or tail ranges and an unrolled Duff-style XLEN store loop for bulk fill.

## Control Flow
The function preserves destination in `a0`, byte-fills until aligned, broadcasts the low byte of the input across a word, computes a 32-store loop entry offset, stores word chunks, and byte-fills the tail.

## State And Persistence
It writes the requested byte pattern to memory and holds no state.

## Dependencies And Integration Points
It uses RISC-V assembly macros, CONFIG_64BIT handling for byte broadcast, and early boot aliases used before the full kernel is relocated.

## Risks
The computed jump into the unrolled loop assumes 32-bit instruction lengths. Broadcast and tail behavior must handle negative/int input by masking to 8 bits.

## Test Signals
lib/string tests, randomized fill alignment/length cases, boot tests, and RV32/RV64 build coverage are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memset.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/riscv_v_helpers.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/riscv_v_helpers.c

## Purpose
`riscv_v_helpers.c` bridges scalar and vector user-copy implementations for RISC-V vector-capable kernels.

## Important APIs, Types, And Functions
`riscv_v_usercopy_threshold` controls when vector copy is attempted. `enter_vector_usercopy()` is the exported C entry used by assembly. It calls `__asm_vector_usercopy` or `_sum_enabled` inside `kernel_vector_begin/end`, then falls back to scalar routines for remaining bytes or when SIMD use is not allowed.

## Control Flow
The caller has already checked vector ISA availability. The helper verifies `may_use_simd()`, starts a kernel vector section, performs vector copy, ends the section, and if a fault leaves bytes remaining, adjusts source/destination pointers and invokes the matching scalar fallback.

## State And Persistence
Only the tunable threshold is persistent runtime state. Copies affect user/kernel memory but the helper does not own that memory.

## Dependencies And Integration Points
It depends on vector context management, SIMD preemption rules, assembly usercopy symbols, and MMU-only uaccess integration.

## Risks
The boolean `enable_sum` selects whether SUM is already enabled; mixing the two paths could fault or leave SUM handling wrong. Vector use is only safe inside kernel vector guards.

## Test Signals
Usercopy tests with vector enabled/disabled, threshold tuning, page-fault fallback tests, and preemption/SIMD stress are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/riscv_v_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strchr.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strchr.S

## Purpose
`strchr.S` implements bytewise search for the first occurrence of a character in a NUL-terminated string.

## Important APIs, Types, And Functions
The exported `strchr` symbol masks the search character to 8 bits and returns either the matching address or zero. `__pi_strchr` aliases it for position-independent early code.

## Control Flow
The loop loads one unsigned byte, compares it with the target, advances on mismatch, and stops with NULL if the NUL terminator is reached first.

## State And Persistence
No state is stored; it reads the input string.

## Dependencies And Integration Points
It is a core string helper used throughout the kernel when generic/KASAN string replacements are not selected.

## Risks
The function assumes a valid NUL-terminated string. It must match C semantics where searching for `\0` returns the terminator address.

## Test Signals
lib/string tests covering target present, absent, and NUL target validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strcmp.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strcmp.S

## Purpose
`strcmp.S` implements RISC-V string comparison with an optional Zbb-accelerated aligned path.

## Important APIs, Types, And Functions
`strcmp` is exported and aliased as `__pi_strcmp`. The scalar loop compares bytes. The `strcmp_zbb` alternative uses `orc.b`, `rev8`, and branchless result synthesis when Zbb/toolchain support is present.

## Control Flow
Boot alternatives patch a jump to the Zbb path when available. The scalar path advances byte by byte until mismatch or NUL. The Zbb path uses word loads for aligned strings until a word differs or contains NUL, falling back to byte comparison for misalignment or NUL/mismatch resolution.

## State And Persistence
No state is retained.

## Dependencies And Integration Points
It depends on alternative patching, RISC-V Zbb hwcap/toolchain support, endian handling, and kernel string API users.

## Risks
The optimized path must return negative/zero/positive with correct lexicographic byte order. Word loads require aligned addresses. Endian reversal is required before word comparison on little-endian.

## Test Signals
String selftests with aligned/misaligned inputs, Zbb and non-Zbb boots, and early boot alias use are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strcmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strlen.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strlen.S

## Purpose
`strlen.S` implements RISC-V string length with scalar and optional Zbb word-at-a-time variants.

## Important APIs, Types, And Functions
`strlen` is exported and aliased as `__pi_strlen`. The Zbb path uses `orc.b`, `not`, and `ctz`/`clz` to find the first NUL byte in a word.

## Control Flow
The scalar path increments a pointer until it reads NUL, then subtracts the original pointer. The Zbb path aligns down, masks irrelevant first-word bytes by shifting, scans word chunks for a NUL indicator, and adds byte offsets to produce the length.

## State And Persistence
No state is retained; it reads a NUL-terminated string.

## Dependencies And Integration Points
It depends on alternatives, Zbb support, endian-specific bit scan direction, and kernel string API callers.

## Risks
The first unaligned word handling intentionally reads before the string's start at the aligned word; this assumes the access is valid in kernel contexts. Endian shifts and count calculations are subtle.

## Test Signals
String tests across all alignments, empty strings, page-boundary cases, Zbb/non-Zbb builds, and early boot users are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strncmp.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strncmp.S

## Purpose
`strncmp.S` implements bounded string comparison with scalar and optional Zbb accelerated paths.

## Important APIs, Types, And Functions
`strncmp` is exported and aliased as `__pi_strncmp`. It accepts two strings and a count. The Zbb path uses aligned word comparison while respecting the byte limit.

## Control Flow
The scalar path iterates until count is reached, a mismatch occurs, or NUL terminates both equal strings. The Zbb path computes an end pointer, processes aligned full words while no NUL and equal, then falls back to byte comparison near limits, misalignment, or termination.

## State And Persistence
No state is retained.

## Dependencies And Integration Points
It depends on alternative patching, Zbb support, endian handling, and kernel string callers.

## Risks
Bounded behavior must never read past the intended safe range in ways that fault. The optimized path must respect count exactly and handle `count == 0` as equal.

## Test Signals
String tests for zero count, partial prefixes, mismatches before/after count, NUL before count, alignment, and Zbb/non-Zbb coverage are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strncmp.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strnlen.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strnlen.S

## Purpose
`strnlen.S` implements bounded string length with scalar and optional Zbb word scanning.

## Important APIs, Types, And Functions
`strnlen` is exported and aliased as `__pi_strnlen`. It returns the smaller of the first NUL position and the supplied maximum.

## Control Flow
The scalar path advances until the end pointer or NUL. The Zbb path handles maxlen zero, scans the first unaligned word with masking, clamps by maxlen, then scans aligned words until NUL or boundary.

## State And Persistence
No state is stored; it reads bounded string memory.

## Dependencies And Integration Points
It uses RISC-V alternatives, Zbb instructions, endian-specific bit scans, and kernel string API integration.

## Risks
The Zbb path must clamp results and avoid unsafe reads around maxlen/page boundaries. Initial unaligned word handling is subtle.

## Test Signals
Tests should cover zero length, no NUL within bound, NUL at each alignment, Zbb vs scalar comparison, and page-boundary strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strnlen.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strrchr.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strrchr.S

## Purpose
`strrchr.S` implements search for the last occurrence of a character in a NUL-terminated string.

## Important APIs, Types, And Functions
The exported `strrchr` masks the search byte, scans from the start, keeps the most recent match in `a0`, and aliases `__pi_strrchr`.

## Control Flow
The loop loads the current byte, updates the saved result when it matches, advances, and stops after processing the NUL terminator. Searching for NUL therefore returns the terminator address.

## State And Persistence
No persistent state is used.

## Dependencies And Integration Points
It is used by kernel string callers when architecture string routines are selected.

## Risks
It assumes a valid terminated string. A typo in comments is non-functional; behavior must match C `strrchr`.

## Test Signals
String tests for multiple matches, absent character, first/last character, and NUL target are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strrchr.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/tishift.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/tishift.S

## Purpose
`tishift.S` provides 128-bit integer shift helper routines needed by the compiler on 64-bit RISC-V.

## Important APIs, Types, And Functions
It exports `__lshrti3`, `__ashrti3`, and `__ashlti3` for logical right, arithmetic right, and arithmetic left shifts of TImode values carried in `a1:a0` with shift amount in `a2`.

## Control Flow
Each helper returns unchanged for shift zero, handles shifts below 64 by combining shifted low/high halves, and handles shifts of 64 or more by moving or sign-extending the high/low half into the result.

## State And Persistence
No state is retained.

## Dependencies And Integration Points
It is selected for CONFIG_64BIT and satisfies compiler-generated libcalls in kernel code.

## Risks
Wrong sign extension in arithmetic right shift or boundary handling at exactly 64 bits would corrupt compiler-generated 128-bit math.

## Test Signals
Builds that generate `__int128` shifts and arithmetic tests across shift counts 0, 1, 63, 64, 65, and 127 are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/tishift.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess.S

## Purpose
`uaccess.S` implements RISC-V assembly user-copy and clear-user primitives, including scalar fallback and optional vector dispatch.

## Important APIs, Types, And Functions
It exports `__asm_copy_to_user`, `__asm_copy_from_user`, `_sum_enabled` variants, `fallback_scalar_usercopy`, `fallback_scalar_usercopy_sum_enabled`, and `__clear_user`. The `fixup` macro emits exception table entries for fault recovery.

## Control Flow
Top-level copy wrappers enable SUM when needed, optionally dispatch to vector usercopy for large copies on vector-capable systems, then fall back to scalar copy. The scalar copy aligns destination, uses word copy or shift-copy for misaligned source, copies tail bytes, and returns remaining bytes on exception. `__clear_user` enables SUM, zeroes aligned words and edge bytes, and returns uncleared bytes on fault.

## State And Persistence
The routines mutate user/kernel memory and temporarily set/clear `SR_SUM`. No persistent state is stored.

## Dependencies And Integration Points
They depend on exception-table fixups, CSR_STATUS/SUM semantics, vector threshold helpers, RISC-V alternatives, and core `copy_{to,from}_user`/`clear_user` APIs.

## Risks
SUM must be cleared on all exit paths. Exception fixups must report exact remaining bytes. Vector dispatch must preserve fault semantics. Misaligned shift-copy is sensitive to page faults and endpoint calculations.

## Test Signals
Usercopy selftests, fault-injection on invalid user pages, KASAN/KMSAN builds, vector and non-vector systems, and hardened usercopy tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess_vector.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess_vector.S

## Purpose
`uaccess_vector.S` provides vectorized byte user-copy loops for RISC-V vector-capable MMU kernels.

## Important APIs, Types, And Functions
It exports `__asm_vector_usercopy` and `__asm_vector_usercopy_sum_enabled`. The code uses `vsetvli`, `vle8.v`, and `vse8.v` with exception-table fixups.

## Control Flow
The non-SUM wrapper enables SUM, calls the SUM-enabled loop, then clears SUM. The loop sets vector length for remaining bytes, loads bytes from source, subtracts the vector length, stores to destination, advances pointers, and repeats. Load faults return current remaining bytes; store faults adjust remaining bytes using `CSR_VSTART`.

## State And Persistence
It temporarily mutates SUM and vector state while copying memory. No persistent state is kept.

## Dependencies And Integration Points
It is called from `enter_vector_usercopy()` and relies on vector context guards in C, exception table fixups, and RISC-V vector ISA.

## Risks
Fault accounting on partial vector stores must be exact so scalar fallback resumes at the right byte. SUM cleanup must run after wrapper calls. Vector state must only be used inside kernel vector critical sections.

## Test Signals
Large usercopy tests with page faults at load and store boundaries, vector preemption stress, and comparison with scalar remaining-byte behavior are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess_vector.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/Makefile

## Purpose
This Makefile selects RISC-V architecture memory-management objects and build flags.

## Important APIs, Types, And Functions
It sets special flags for `init.o`, removes ftrace from early MM/cacheflush objects when needed, disables KCOV for `init.o`, disables KASAN instrumentation for early KASAN/MM files, and selects MMU, cacheflush, context, pmem, hugetlb, ptdump, debug virtual, DMA noncoherent, and nonstandard cache-op objects.

## Control Flow
Kbuild conditionals wire objects based on MMU, HUGETLB, PTDUMP, KASAN, DEBUG_VIRTUAL, RISCV_DMA_NONCOHERENT, and RISCV_NONSTANDARD_CACHE_OPS.

## State And Persistence
No runtime state is defined; build configuration controls which MM features are compiled.

## Dependencies And Integration Points
It integrates RISC-V MM code with kernel build instrumentation constraints and feature-specific object selection.

## Risks
Instrumenting early page-table code with ftrace/KASAN/KCOV can break boot. Missing conditional objects can remove required hooks for configured subsystems.

## Test Signals
Build matrix coverage across relocatable, ftrace, KASAN, MMU/no-MMU, hugetlb, DMA noncoherent, and debug virtual configs is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cache-ops.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/cache-ops.c

## Purpose
`cache-ops.c` stores and exports nonstandard cache operation callbacks for RISC-V noncoherent DMA support.

## Important APIs, Types, And Functions
`noncoherent_cache_ops` is a `__ro_after_init` global. `riscv_noncoherent_register_cache_ops()` copies a supplied `struct riscv_nonstd_cache_ops` into it and is exported GPL-only.

## Control Flow
Registration is a simple null check followed by structure copy. DMA maintenance paths later call populated callbacks when present.

## State And Persistence
The registered callback table persists after init as read-only kernel data. There is no disk persistence.

## Dependencies And Integration Points
It integrates platform/vendor cache maintenance implementations with `dma-noncoherent.c`.

## Risks
Callbacks must be registered before `__ro_after_init` protection and must implement correct cache semantics. Null ops fall back to standard CMO operations.

## Test Signals
Platform boot on nonstandard-cache systems, DMA correctness tests, and verifying fallback behavior with no registered ops are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cache-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cacheflush.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/cacheflush.c

## Purpose
`cacheflush.c` implements RISC-V instruction-cache flush and CBO block-size initialization, plus prctl control for userspace `fence.i` context behavior.

## Important APIs, Types, And Functions
`flush_icache_all()`, `flush_icache_mm()`, `flush_icache_pte()`, `riscv_init_cbo_blocksizes()`, and `riscv_set_icache_flush_ctx()` are key APIs. Globals export CBOM, CBOZ, and CBOP block sizes.

## Control Flow
On SMP, global icache flush runs local `fence.i`, orders prior data writes with `RISCV_FENCE(w,o)`, then uses SBI remote fence or IPIs. Per-mm flush marks all harts stale, flushes local, and flushes active remote harts or defers work for later context switch. CBO init reads DT CPU nodes or ACPI RHCT. The prctl path toggles per-process/per-thread flush permissions and marks icaches stale when disabling user fence.i.

## State And Persistence
State includes exported CBO block sizes and per-mm/per-thread icache stale/force flags. No disk persistence exists.

## Dependencies And Integration Points
It depends on SBI rfence, SMP IPIs, mm context `icache_stale_mask`, OF/ACPI discovery, PTE cache-clean flags, and RISC-V prctl ABI.

## Risks
Incorrect ordering can let remote harts execute stale instructions. CBO block-size mismatches across harts are warned but still globally recorded. The prctl state must preserve migration-time icache coherency guarantees.

## Test Signals
JIT/self-modifying-code tests, BPF/module execution, SMP migration tests, OF/ACPI CBO discovery, and prctl fence.i selftests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/context.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/context.c

## Purpose
`context.c` implements RISC-V MM context switching, ASID allocation/rollover, and deferred instruction-cache flushing for tasks.

## Important APIs, Types, And Functions
Global ASID state includes `use_asid_allocator`, `num_asids`, `current_version`, `context_lock`, `context_tlb_flush_pending`, `context_asid_map`, per-CPU `active_context`, and `reserved_context`. Key functions are `asids_init()`, `set_mm_asid()`, `set_mm_noasid()`, `set_mm()`, `flush_icache_deferred()`, and `switch_mm()`.

## Control Flow
Boot probes writable SATP ASID bits, enables ASID allocation only when enough ASIDs exist, and initializes the bitmap. Context switch marks CPU membership, assigns an ASID with versioning or flushes with ASID 0, writes SATP, and performs queued TLB flushes. Rollover preserves per-CPU reserved contexts and queues all CPUs for local flush. Deferred icache flush runs when a CPU switches into an mm marked stale.

## State And Persistence
Per-mm state is `mm->context.id` and icache masks/flags. Per-CPU active/reserved contexts cache ASID usage. Runtime-only state is reset at boot.

## Dependencies And Integration Points
It depends on SATP CSR, TLB flush helpers, mm cpumasks, membarrier, task switch hooks, and cacheflush stale-mask logic.

## Risks
ASID rollover races require strict locking and cmpxchg behavior. Missing TLB flushes can expose stale translations. With ASIDs enabled, CPUs remain in `mm_cpumask` until mm reset, which differs from no-ASID behavior.

## Test Signals
Fork/exec/mmap stress, ASID rollover under many address spaces, membarrier tests, SMP migration with self-modifying code, and TLB shootdown tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/dma-noncoherent.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/dma-noncoherent.c

## Purpose
`dma-noncoherent.c` provides RISC-V cache maintenance hooks for noncoherent DMA devices.

## Important APIs, Types, And Functions
It exports `dma_cache_alignment`, `arch_sync_dma_for_device()`, `arch_sync_dma_for_cpu()`, `arch_dma_prep_coherent()`, `arch_setup_dma_ops()`, `riscv_noncoherent_supported()`, and `riscv_set_dma_cache_alignment()`. Internal helpers perform writeback, invalidate, and writeback+invalidate through nonstandard ops or `ALT_CMO_OP`.

## Control Flow
DMA sync for device chooses clean/invalidate/flush based on direction and whether CPU post-flush is expected. Sync for CPU invalidates FROM_DEVICE/BIDIRECTIONAL buffers. Setup warns when noncoherent devices lack supported operations or block alignment exceeds `ARCH_DMA_MINALIGN`, then records `dev->dma_coherent`.

## State And Persistence
Runtime state is `noncoherent_supported` and exported `dma_cache_alignment`. Device DMA coherency is stored in each `struct device`.

## Dependencies And Integration Points
It depends on CBO block sizes, nonstandard cache callback registration, DMA mapping core, and device-tree/ACPI coherency decisions.

## Risks
Wrong maintenance direction corrupts DMA data. Unsupported noncoherent devices are tainted but may still malfunction. Cache block size larger than DMA alignment risks partial-line sharing.

## Test Signals
DMA mapping tests on coherent and noncoherent devices, streaming DMA to/from devices, SWIOTLB bounce tests, and nonstandard cache-op platforms are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/dma-noncoherent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/extable.c

## Purpose
`extable.c` implements RISC-V exception table fixup dispatch for fault-tolerant kernel access sequences.

## Important APIs, Types, And Functions
`fixup_exception()` searches exception tables and dispatches by type. Handlers include generic fixup, BPF fixup, uaccess error/zero register fixup, and load-unaligned-zeropad. Helpers read and write GPRs in `pt_regs` using encoded register offsets.

## Control Flow
On exception, the code finds the entry matching `regs->epc`, decodes `ex->type`, optionally writes error/zero/data registers from encoded metadata, sets `regs->epc` to the relative fixup address, and returns true. Unknown types BUG.

## State And Persistence
It mutates only the live `pt_regs` frame. No persistent state is stored.

## Dependencies And Integration Points
It integrates with assembly `_asm_extable` users, uaccess copy/clear routines, BPF exception handling, page fault `no_context()`, and unaligned zeropad helpers.

## Risks
Encoded register offsets must match `pt_regs`. Fixups must not write x0 except by ignoring offset zero. Load-unaligned-zeropad dereferences the aligned address and assumes the fault model matches the intended use.

## Test Signals
Uaccess fault tests, BPF probe tests, exception-table unit coverage, and page fault paths that recover instead of oopsing validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/fault.c

## Purpose
`fault.c` is the RISC-V page fault handler. It diagnoses kernel faults, handles vmalloc synchronization on limited configurations, invokes generic MM fault handling, and delivers signals or oopses.

## Important APIs, Types, And Functions
Key helpers are `show_pte()`, `die_kernel_fault()`, `no_context()`, `mm_fault_error()`, `bad_area_nosemaphore()`, `bad_area()`, `vmalloc_fault()`, `access_error()`, and exported `handle_page_fault()`.

## Control Flow
The handler records cause/address, lets kprobes consume faults, traces user/kernel faults, handles vmalloc faults without locks in applicable builds, enables interrupts when safe, rejects faults in atomic/no-mm contexts, checks kernel access to user memory without SUM, sets fault flags, tries lockless VMA handling for user faults, falls back to mmap locking, calls `handle_mm_fault()`, retries as requested, and maps final errors to SIGSEGV/SIGBUS/OOM or kernel oops.

## State And Persistence
It mutates task bad-cause state, page tables through generic fault handling, and may synchronize vmalloc top-level mappings. No disk persistence exists.

## Dependencies And Integration Points
It depends on Linux MM fault core, kprobes, kfence, perf software events, exception fixups, RISC-V trap fields, TLB flushes, and signal/trap delivery.

## Risks
Kernel faults in atomic context must never take mmap locks. SUM checks prevent unsafe direct user access. VMA lock retry logic must release locks correctly. Vmalloc fault synchronization assumes global kernel mappings and explicit TLB flushes.

## Test Signals
Page fault selftests, user SIGSEGV/SIGBUS cases, COW/mmap stress, kprobes, KFENCE, invalid kernel access tests, and vmalloc fault tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/hugetlbpage.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/hugetlbpage.c

## Purpose
`hugetlbpage.c` implements RISC-V hugepage support, including Svnapot contiguous PTE mappings when available.

## Important APIs, Types, And Functions
It defines huge PTE lookup/allocation, NAPOT-aware get/clear/set/protect/access flag operations, hugepage valid-size checks, hstate registration, migration support, and CMA order selection.

## Control Flow
Allocation walks pgd/p4d/pud/pmd levels, using PUD/PMD huge mappings or pte-level NAPOT mappings. NAPOT updates use break-before-make: clear all contiguous PTEs, flush the covered range, then install new PTEs. Access flag and write-protect paths merge dirty/young bits from all contiguous entries before rewriting.

## State And Persistence
State is page-table entries and registered hugetlb hstates. Runtime hugepage mappings persist in process page tables; no disk persistence exists.

## Dependencies And Integration Points
It depends on hugetlb core, Svnapot feature detection, RISC-V PTE helpers, TLB flush APIs, huge PMD/PUD sharing, migration, and CMA configuration.

## Risks
NAPOT contiguity requires every PTE in the range to remain consistent. Missing break-before-make can violate the privileged spec. Valid-size logic must match hardware and compiled page-table levels.

## Test Signals
Hugetlb selftests, NAPOT hugepage mapping tests, dirty/young tracking, migration, fork/COW, and gigantic page allocation tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/hugetlbpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/init.c

## Purpose
`init.c` is the main RISC-V memory initialization file. It builds early and final page tables, establishes kernel and linear mappings, handles KASLR/relocation, reserves boot memory, initializes zones, vmemmap, execmem ranges, and memory hotplug mapping removal.

## Important APIs, Types, And Functions
Important globals include `kernel_map`, `satp_mode`, `pgtable_l4_enabled`, `pgtable_l5_enabled`, `phys_ram_base`, `new_vmalloc`, and page-table roots. Key functions include `arch_mm_preinit()`, `setup_bootmem()`, `relocate_kernel()`, `__set_fixmap()`, page-table allocation/mapping helpers, `set_satp_mode()`, `setup_vm()`, `create_kernel_page_table()`, `setup_vm_final()`, `paging_init()`, `misc_mem_init()`, `vmemmap_populate()`, `pgtable_cache_init()`, `execmem_arch_setup()`, and memory hotplug add/remove helpers.

## Control Flow
Early setup computes kernel virtual/physical offsets, optional KASLR, SATP mode, early fixmap/trampoline mappings, kernel mappings, and FDT fixmap before enabling final allocation helpers. Bootmem reserves kernel, initrd, DTB, reserved-memory regions, crashkernel, DMA limits, and contiguous DMA. Final setup creates swapper mappings for fixmap, linear memory, kernel text/rodata with strict permissions, KASAN shadow, switches SATP, flushes TLBs, and moves to late page-table allocation. Hotplug paths add/remove linear and vmemmap mappings and free empty page-table pages.

## State And Persistence
Persistent runtime state is kernel page tables, memblock reservations during boot, zone PFNs, vmemmap mappings, SATP mode, page-table level enable flags, and execmem range metadata. These are in-memory kernel state only.

## Dependencies And Integration Points
It integrates with memblock, FDT/ACPI reserved memory, KASAN, KFENCE, SWIOTLB, crashkernel, NUMA, sparsemem/vmemmap, set_memory, execmem/BPF/modules, TLB flushes, and RISC-V boot head code.

## Risks
This is boot-critical. Alignment of kernel, PAGE_OFFSET, fixmap, and huge mappings is enforced by BUG_ONs. Page-table level downgrade must match valid virtual addresses and DTB accessibility. Strict RWX, KASAN, relocation, and hotplug all alter mappings and can expose subtle alias/TLB bugs.

## Test Signals
Boot matrix across Sv39/Sv48/Sv57, 32-bit, KASLR, relocatable, KASAN, KFENCE, strict RWX, sparsemem, crashkernel, memory hotplug, and module/BPF execmem tests is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/kasan_init.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/kasan_init.c

## Purpose
`kasan_init.c` builds RISC-V KASAN shadow mappings from early boot through final swapper page tables.

## Important APIs, Types, And Functions
It defines early temporary page-table roots and helpers to populate pgd/p4d/pud/pmd/pte levels, clear early shadow entries, shallow-populate vmalloc/module shadow, create a temporary mapping, `kasan_early_init()`, `kasan_swapper_init()`, `kasan_populate_early_vm_area_shadow()`, and `kasan_init()`.

## Control Flow
Early init maps the entire KASAN shadow to shared early shadow pages at all enabled page-table levels. Swapper init mirrors this into final page tables. Final `kasan_init()` switches to a temporary page table, clears early shadow for the KASAN range, populates fixmap/vmalloc/modules/linear/kernel shadow ranges with real pages or shallow page tables, makes the early shadow page read-only, restores swapper SATP, flushes TLBs, and calls generic KASAN init.

## State And Persistence
Runtime state is KASAN shadow page-table mappings and initialized shadow memory. Temporary pgd/p4d/pud arrays are boot-only.

## Dependencies And Integration Points
It depends on memblock allocation, RISC-V page-table level flags, fixmap, `pt_ops`, KASAN generic initialization, VMALLOC shadow support, module/BPF address ranges, and TLB flushes.

## Risks
KASAN shadow must live at a fixed address across Sv39/Sv48/Sv57. Shared page-table levels with kernel mapping require temporary copies before clearing. Incorrect shallow population can break vmalloc KASAN or leak writable early shadow pages.

## Test Signals
KASAN boot tests on Sv39/Sv48/Sv57, vmalloc KASAN tests, module/BPF allocation tests, and memory error detection selftests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/kasan_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pageattr.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/pageattr.c

## Purpose
`pageattr.c` implements RISC-V kernel page attribute changes, including set_memory APIs, direct-map validity changes, huge linear mapping splitting, and page presence queries.

## Important APIs, Types, And Functions
`struct pageattr_masks` carries set/clear masks. Walk callbacks update P4D/PUD/PMD/PTE leaves. `split_linear_mapping()` and helpers split huge mappings down to smaller tables when partial permission changes are needed. Public APIs include `set_memory_rw_nx`, `set_memory_ro`, `set_memory_rw`, `set_memory_x`, `set_memory_nx`, direct-map helpers, debug pagealloc mapping, and `kernel_page_present()`.

## Control Flow
`__set_memory()` builds masks, locks `init_mm`, translates vmalloc/module pages to linear aliases when needed, splits linear huge mappings for the affected physical pages, walks page tables to apply masks on both aliases, unlocks, and flushes either all TLBs on 64-bit or the specific range on 32-bit.

## State And Persistence
It mutates kernel page-table entries and direct-map present/permission bits. Effects persist until changed again.

## Dependencies And Integration Points
It integrates with `set_memory` users, modules/BPF, STRICT_KERNEL_RWX, DEBUG_PAGEALLOC, vmalloc metadata, page table walking, and TLB flush APIs.

## Risks
Kernel and linear aliases must stay permission-consistent. Splitting huge mappings requires memory allocation and barriers before publishing tables. Full TLB flushes are used because split mappings can exceed requested ranges.

## Test Signals
Module text permission tests, BPF JIT permission transitions, debug pagealloc, strict RWX checks, `kernel_page_present()` tests, and vmalloc alias tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pageattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/pgtable.c

## Purpose
`pgtable.c` supplies RISC-V page-table helper operations used by generic MM, huge vmap, transparent hugepage, and shadow-stack-aware write helpers.

## Important APIs, Types, And Functions
Functions include `ptep_set_access_flags()`, `ptep_test_and_clear_young()`, runtime `pud_offset()`/`p4d_offset()` for folded levels, huge vmap helpers, PUD/PMD page freeing, `pmdp_collapse_flush()`, `pudp_invalidate()`, `pte_mkwrite()`, and `pmd_mkwrite()`.

## Control Flow
Access-flag updates either set and flush immediately for SVVPTC-sensitive systems or update and rely on `update_mmu_cache()`. Huge vmap functions install/clear huge PUD/PMD mappings and free lower page tables after TLB flush. THP collapse globally flushes the mm because leaf-level conversion semantics require eager fencing. Write helpers choose normal or shadow-stack writable encodings based on VMA flags.

## State And Persistence
It mutates process/kernel page-table entries and accessed bits. No private persistent state exists.

## Dependencies And Integration Points
It depends on RISC-V PTE bit definitions, page-table level enable flags, huge vmap, THP, shadow stack VM flags, TLB flush APIs, and generic MM callers.

## Risks
SVVPTC changes TLB invalidation requirements. Freeing huge-vmap lower tables must happen only after clearing and flushing. Folded level offset helpers must match `pgtable_l4_enabled`/`l5_enabled` runtime state.

## Test Signals
MM selftests for access/young bits, huge vmap, THP collapse, shadow stack mappings, and Sv48/Sv57 runtime folded-level configurations are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/pgtable.c -->
