# Research: subset-b-000688

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.c

## Purpose
This is the main arm64 KVM system register emulation and userspace register ABI implementation. It defines the descriptor tables for AArch64 system registers, AArch32 CP14/CP15 aliases, trapped system instructions, feature ID registers, timer/PMU/debug/GIC traps, nested virtualization EL2 register exposure, reset behavior, and the `KVM_GET_ONE_REG` / `KVM_SET_ONE_REG` plumbing.

## Important APIs, Types, And Functions
- `vcpu_read_sys_reg()` / `vcpu_write_sys_reg()` choose whether a virtual register is read from backing memory, live CPU state, a mapped EL1 register, or special merged state such as `CNTHCTL_EL2` when VHE/E2H applies.
- `sys_reg_descs[]`, `sys_insn_descs[]`, `cp14_regs[]`, `cp14_64_regs[]`, `cp15_regs[]`, and `cp15_64_regs[]` are sorted descriptor tables. Each `struct sys_reg_desc` entry supplies encoding, access handler, reset callback, backing register index, userspace get/set callbacks, value or writable mask, and visibility callback.
- Generic helpers include `access_rw()`, `access_vm_reg()`, `trap_raz_wi()`, `undef_access()`, `read_from_write_only()`, `write_to_read_only()`, `perform_access()`, `emulate_cp()`, and `emulate_sys_reg()`.
- Feature-ID logic is concentrated in `kvm_read_sanitised_id_reg()`, `read_id_reg()`, `arm64_check_features()`, `set_id_reg()`, and per-register setters such as `set_id_aa64pfr0_el1()`, `set_id_aa64dfr0_el1()`, `set_id_aa64mmfr0_el1()`, and `set_ctr_el0()`.
- Runtime trap entry points are `kvm_handle_sys_reg()`, `kvm_handle_cp15_64()`, `kvm_handle_cp15_32()`, `kvm_handle_cp14_64()`, `kvm_handle_cp14_32()`, `kvm_handle_cp10_id()`, and `kvm_handle_cp14_load_store()`.
- Userspace ABI entry points are `kvm_arm_sys_reg_get_reg()`, `kvm_arm_sys_reg_set_reg()`, `kvm_sys_reg_get_user()`, `kvm_sys_reg_set_user()`, `kvm_arm_num_sys_reg_descs()`, `kvm_arm_copy_sys_reg_indices()`, and `kvm_vm_ioctl_get_reg_writable_masks()`.
- Lifecycle functions include `kvm_reset_sys_regs()`, `kvm_calculate_traps()`, `kvm_finalize_sys_regs()`, `kvm_sys_regs_create_debugfs()`, and `kvm_sys_reg_table_init()`.

## Control Flow
On a trapped AArch64 MRS/MSR or system instruction, `kvm_handle_sys_reg()` decodes ESR into `sys_reg_params`, asks `triage_sysreg_trap()` for the descriptor index, selects `sys_reg_descs[]` for Op0 2/3 or `sys_insn_descs[]` otherwise, and calls `perform_access()`. `perform_access()` traces the access, rejects hidden registers with UNDEF, requires an access callback, calls it, and increments the guest PC if the callback reports completion. Reads write `params.regval` back to the guest general register.

AArch32 CP14/CP15 traps follow a similar flow but decode CP encodings from ESR. 64-bit CP traps combine two guest registers into `params.regval`; 32-bit traps use one register. AArch32 feature ID reads are rerouted into the AArch64 descriptor table so KVM has one feature-ID policy source. Unmatched accesses log an unimplemented sysreg message and inject UNDEF.

Reset iterates `sys_reg_descs[]`, runs reset callbacks, writes VM-scoped ID registers only once under `config_lock`, and reloads PMU state when PMU is enabled. Finalization adjusts ID registers just before first run, including nested virtualization setup and GIC/GICv5 ID-field reconciliation.

## State And Persistence Behavior
Most emulated registers persist in `vcpu->arch.ctxt.sys_regs[]` through descriptor `.reg` indexes. Some state is VM-wide, especially feature ID registers stored under `kvm->arch`, and is immutable after the VM has run. PMU counter counts and event types route through PMU helpers rather than only the raw sysreg array. Debug breakpoint/watchpoint state is stored in `vcpu->arch.vcpu_debug_state` and accessed through demux helpers. Cache geometry overrides allocate `vcpu->arch.ccsidr` lazily. Sanitized registers may be masked through per-VM RES0/RES1 mask state. Debugfs exposes current VM ID registers and RESX masks via seq files.

## Dependencies And Integration Points
This file depends on arm64 sysreg encoding helpers, cpufeature sanitization, PMU virtualization, VGIC interfaces, nested virtualization helpers, arch timer helpers, KVM MMU/stage-2 invalidation, debug monitor support, tracepoints from `trace.h`, and userspace copy helpers. It imports VGIC sysreg descriptors through `vgic_v3_get_sysreg_table()` during table validation. GIC trap handlers call VGIC functions for SGI dispatch, deactivate, GICv5 PPI enables, and virtual ICH state. Timer descriptors delegate to `kvm_arm_timer_*`. TLBI and AT system instructions delegate to nested MMU helpers and stage-2 unmap/invalidations.

## Risks And Edge Cases
- Descriptor tables must remain strictly sorted by encoding; `kvm_sys_reg_table_init()` fails if ordering or required reset callbacks are wrong.
- Feature ID writes are ABI-sensitive. KVM must allow old userspace-restored values in some cases while preventing guests from seeing impossible capabilities.
- VM-scoped ID registers become immutable once the VM has run; late userspace writes may fail with `-EBUSY`.
- Live CPU sysreg access is only valid with VHE-style loaded state. The register location logic warns if non-VHE paths try to read loaded CPU registers.
- Nested virtualization paths have special mappings for EL2 registers, VNCR-backed registers, redirected EL2-to-EL1 registers, E2H/TGE behavior, and TLBI shadow stage-2 invalidation.
- PMU access must enforce `PMUSERENR_EL0` privilege and accessible counter masks, or guests can observe/influence unsupported counters.
- Cache line and CLIDR/CCSIDR values are deliberately fabricated for stable migration; accepting invalid userspace cache geometry could create guest-visible inconsistency.
- GICv5 and legacy GICv3 ID field compatibility is explicitly handled and is easy to regress.

## Test Signals
- Build coverage should catch descriptor initializer and symbol errors.
- Boot/init tests should exercise `kvm_sys_reg_table_init()` table ordering and reset validation.
- KVM selftests for `KVM_GET_ONE_REG`, `KVM_SET_ONE_REG`, writable ID masks, feature ID immutability after run, and migration restore are direct signals.
- Guest tests for PMU, arch timers, GICv3 SGIs, GICv5 PPIs, debug register traps, MTE/SVE/Pointer Authentication visibility, and AArch32 CP15 ID reads cover major descriptor classes.
- Nested virtualization tests should cover EL2 sysregs, VNCR, AT/TLBI handlers, E2H/TGE combinations, and GIC ICH register visibility.
- Tracepoint observation through `kvm_sys_access` and debugfs `idregs`/`resx` provides runtime diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.h

## Purpose
This private KVM arm64 header defines the common data model and lookup helpers for system register emulation. It is shared by the main sysreg implementation and smaller integrations such as VGIC system register userspace access.

## Important APIs, Types, And Functions
- `struct sys_reg_params` carries decoded Op0/Op1/CRn/CRm/Op2, the transferred value, and access direction.
- `struct sys_reg_desc` describes one trapped or userspace-visible register: name, AArch32 mapping, encoding, trap access callback, reset callback, backing `enum vcpu_sysreg`, value/writable mask, custom get/set callbacks, and visibility callback.
- Encoding helpers include `reg_to_encoding()`, `encoding_to_params()`, `esr_sys64_to_params()`, and `esr_cp1x_32_to_params()`.
- `in_feat_id_space()` identifies the AArch64 feature-ID encoding space.
- Visibility flags `REG_HIDDEN`, `REG_RAZ`, and `REG_USER_WI` distinguish hidden, read-as-zero, and userspace-write-ignore behavior.
- Inline helpers include `print_sys_reg_msg()`, `print_sys_reg_instr()`, `ignore_write()`, `read_zero()`, `reset_unknown()`, `reset_val()`, `sysreg_visibility()`, `sysreg_hidden()`, `sysreg_visible_as_raz()`, `sysreg_user_write_ignore()`, `cmp_sys_reg()`, `match_sys_reg()`, and `find_reg()`.
- Exported declarations include `get_reg_by_id()`, `kvm_arm_sys_reg_get_reg()`, `kvm_arm_sys_reg_set_reg()`, generic sysreg get/set helpers, `triage_sysreg_trap()`, and `kvm_finalize_sys_regs()`.
- Descriptor initializer macros include `AA32()`, `Op0()`, `Op1()`, `CRn()`, `CRm()`, `Op2()`, `SYS_DESC()`, and `CP15_SYS_DESC()`.

## Control Flow
Callers decode ESR or KVM register IDs into `sys_reg_params`, then use `find_reg()` over a sorted descriptor table. The comparator uses a packed sysreg encoding and inline binary search, so the descriptor arrays must be sorted and unique. Access handlers and userspace accessors then use the descriptor’s callback fields and visibility flags to choose emulation behavior.

## State And Persistence Behavior
The header itself owns no persistent state. It defines how descriptors point at persistent vCPU or VM state through `.reg`, `.reset`, `.get_user`, `.set_user`, `.val`, and `.visibility`. The reset helpers write into `vcpu->arch` sysreg storage and deliberately use a recognizable poison-like value for architecturally unknown resets.

## Dependencies And Integration Points
It depends on Linux `bsearch` and arm64/KVM types supplied by included translation units. It is a contract between sysreg trap dispatch, VGIC sysreg user attributes, nested virtualization trap triage, debugfs, and KVM one-reg UAPI code.

## Risks And Edge Cases
- The comparator calls `BUG_ON(i1 == i2)` and assumes valid descriptor inputs.
- Tables must be sorted by encoding for `find_reg()` to work.
- `reset_unknown()` and `reset_val()` require a valid nonzero `.reg` index below `NR_SYS_REGS`.
- Visibility flags have distinct guest and userspace semantics; mixing `REG_HIDDEN`, `REG_RAZ`, and `REG_USER_WI` can change migration ABI.

## Test Signals
- Table validation during KVM init catches ordering and missing reset callbacks.
- One-reg enumeration and get/set tests verify descriptor lookup.
- Negative tests for hidden, RAZ, and userspace write-ignore registers validate visibility semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/sys_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trace.h

## Purpose
This is a small umbrella trace header for arm64 KVM. It includes the architecture tracepoint definitions split across `trace_arm.h` and `trace_handle_exit.h`.

## Important APIs, Types, And Functions
- Includes `trace_arm.h` for guest entry/exit, fault, MMIO, timer, nested exception, and forwarded sysreg trap tracepoints.
- Includes `trace_handle_exit.h` for exit handling tracepoints such as WFx, HVC, sysreg trap, sysreg access, and guest debug changes.

## Control Flow
Translation units include this header to make the trace event prototypes available. The included headers define trace events and instantiate trace metadata through `trace/define_trace.h`.

## State And Persistence Behavior
No runtime state is stored here. It gates compile-time inclusion of tracepoint definitions.

## Dependencies And Integration Points
This header is consumed by arm64 KVM code such as `sys_regs.c`. It integrates with Linux ftrace/perf tracepoint infrastructure under `TRACE_SYSTEM kvm`.

## Risks And Edge Cases
Because both included trace headers define trace metadata, include guards and `TRACE_HEADER_MULTI_READ` behavior must remain correct. Include path macros in the child headers must point at the source layout expected by trace generation.

## Test Signals
Successful kernel build with tracepoints enabled is the primary signal. Runtime enabling of KVM trace events should show events from both included headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_arm.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_arm.h

## Purpose
This trace header defines arm64 KVM tracepoints for guest entry/exit, faults, MMIO, cache maintenance traps, arch timer state, nested virtualization exceptions, and forwarded sysreg traps.

## Important APIs, Types, And Functions
- `TRACE_EVENT(kvm_entry)` records guest PC at entry.
- `TRACE_EVENT(kvm_exit)` records exception return code, ESR exception class, and PC.
- Fault/MMIO events include `kvm_guest_fault`, `kvm_access_fault`, `kvm_mmio_emulate`, and `kvm_mmio_nisv`.
- Interrupt/cache events include `kvm_irq_line`, `kvm_set_way_flush`, and `kvm_toggle_cache`.
- Timer events include `kvm_timer_update_irq`, `kvm_get_timer_map`, `kvm_timer_save_state`, `kvm_timer_restore_state`, `kvm_timer_hrtimer_expire`, and `kvm_timer_emulate`.
- Nested virtualization events include `kvm_nested_eret`, `kvm_inject_nested_exception`, and `kvm_forward_sysreg_trap`.

## Control Flow
KVM runtime code calls generated `trace_kvm_*` helpers at relevant points. Each event records fields in `TP_fast_assign()` and formats output with `TP_printk()`. The header sets `TRACE_SYSTEM` to `kvm`, then sets `TRACE_INCLUDE_FILE` to `trace_arm` before including `trace/define_trace.h`.

## State And Persistence Behavior
Trace events store transient samples in the kernel tracing buffers when enabled. They do not mutate KVM state. Field values are captured by value except pointer fields such as vCPU pointers in nested events.

## Dependencies And Integration Points
The file depends on `asm/kvm_emulate.h`, `kvm/arm_arch_timer.h`, and Linux tracepoint machinery. Symbol formatting relies on shared symbolic tables such as `kvm_arm_exception_type`, `kvm_arm_exception_class`, `kvm_mode_names`, and `kvm_exception_type_names`.

## Risks And Edge Cases
- Tracepoint field choices are ABI-like for tooling; renaming events or changing field meanings can break scripts.
- Some fields are derived, for example ESR class is zeroed for non-trap exits.
- Timer map tracepoints dereference timer context pointers and must tolerate absent optional direct/emulated timers.
- `kvm_forward_sysreg_trap` prints decoded sysreg fields from a raw encoding; bad encodings can still be traced but may be misleading.

## Test Signals
Enable tracefs events under `events/kvm/` and run guests that trigger entry/exit, MMIO faults, timers, nested exits, and sysreg forwarding. Kernel build with tracing enabled validates macro expansion and include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_handle_exit.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_handle_exit.h

## Purpose
This trace header covers arm64 KVM exit handling events that are close to trap dispatch: WFx instructions, HVC calls, sysreg handling, individual sysreg accesses, and guest debug flag updates.

## Important APIs, Types, And Functions
- `kvm_wfx_arm64` records WFI/WFE traps and the guest PC.
- `kvm_hvc_arm64` records HVC PC, x0/r0 value, and immediate.
- `kvm_arm_set_dreg32` records debug register name/value writes; the name is historical and values are 64-bit.
- `kvm_handle_sys_reg` records raw HSR/ESR for sysreg traps.
- `kvm_sys_access` records PC, access direction, descriptor name, and decoded sysreg fields.
- `kvm_set_guest_debug` records vCPU pointer and guest debug flags.

## Control Flow
Exit handling and sysreg emulation code call generated `trace_kvm_*` helpers. `kvm_sys_access` receives `struct sys_reg_params` and `struct sys_reg_desc`, which ties this header directly to `sys_regs.h`.

## State And Persistence Behavior
The tracepoints only emit samples to tracing buffers. The `kvm_sys_access` event stores the descriptor name pointer and decoded fields; it does not keep ownership of any dynamic state.

## Dependencies And Integration Points
It includes Linux tracepoint support and `sys_regs.h`. `sys_regs.c` calls `trace_kvm_handle_sys_reg()` and `trace_kvm_sys_access()` to provide sysreg trap diagnostics.

## Risks And Edge Cases
- Trace output depends on descriptor names being stable and valid.
- The `TP_fast_assign` block assigns `Op0` twice; this is harmless duplication but worth noting if editing.
- Tracepoints run on hot paths, so additional fields or expensive formatting would affect enabled tracing overhead.

## Test Signals
Run a guest that executes trapped sysregs, WFI/WFE, HVC, and debug operations with corresponding tracefs events enabled. Build coverage validates macro expansion and include path configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trace_handle_exit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trng.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/trng.c

## Purpose
This file implements KVM’s emulation of the ARM SMCCC TRNG service for guests. It answers TRNG version/features/UUID calls and returns host-generated random bits for TRNG RND32/RND64 calls.

## Important APIs, Types, And Functions
- `kvm_trng_call(struct kvm_vcpu *vcpu)` is the external entry point for SMCCC TRNG handling.
- `kvm_trng_do_rnd(struct kvm_vcpu *vcpu, int size)` validates requested bit count, fills a temporary bitmap with `get_random_long()`, clears unused bits, returns up to three result registers, and wipes the temporary buffer.
- Constants define SMCCC TRNG version 1.0, TRNG return codes, maximum returned bits, and the service UUID.

## Control Flow
`kvm_trng_call()` reads the SMCCC function ID from the vCPU. Version returns `0x10000`. Features reports success for supported TRNG functions. UUID returns four little-endian words from the static UUID. RND32 sets `size = 32` and falls through to RND64 handling; both call `kvm_trng_do_rnd()`. Unsupported functions return `TRNG_NOT_SUPPORTED`.

## State And Persistence Behavior
No persistent guest or VM state is stored. Random bits exist in a stack bitmap and are erased with `memzero_explicit()` before return. The only persistent data is the static UUID constant.

## Dependencies And Integration Points
The implementation depends on SMCCC argument/return helpers, KVM vCPU state, the kernel random API, and `kvm/arm_hypercalls.h`. It is reached from KVM hypercall dispatch for SMCCC calls.

## Risks And Edge Cases
- Requests above `3 * size` bits are rejected as `TRNG_INVALID_PARAMETER`.
- The code always reports success for supported RND calls once parameters are valid; it does not currently surface `TRNG_NO_ENTROPY`.
- Return register ordering differs between RND32 and RND64 and must match SMCCC TRNG ABI.
- Temporary entropy must stay wiped even if implementation changes.

## Test Signals
Guest SMCCC tests should query version, features, UUID, valid RND32/RND64 bit counts, and invalid oversized bit counts. Repeated calls should return masked high bits beyond the requested bit count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/va_layout.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/va_layout.c

## Purpose
This file computes and patches the non-VHE hypervisor virtual address layout. It chooses a randomized HYP VA tag that avoids the ID map, initializes the HYP physical/virtual offset, applies HYP relocations, and emits alternative instruction sequences for fast kernel-to-HYP VA conversion and Spectre vector branching.

## Important APIs, Types, And Functions
- `kvm_hyp_va_bits()` returns the HYP VA size as the maximum of ID map VA bits and actual kernel VA bits.
- `kvm_compute_layout()` computes `tag_lsb`, `va_mask`, and `tag_val`, optionally randomizing tag bits, then initializes `hyp_physvirt_offset`.
- `kvm_apply_hyp_relocations()` walks `.hyp.reloc` entries and rewrites kernel image VAs to HYP VAs.
- `kvm_update_va_mask()` patches a 5-instruction alternative sequence for `kern_hyp_va()` style translation.
- `kvm_patch_vector_branch()` patches a Spectre V3A vector branch sequence to jump into HYP vectors.
- `kvm_get_kimage_voffset()` and `kvm_compute_final_ctr_el0()` patch immediate constants with `kimage_voffset` and sanitized `CTR_EL0`.

## Control Flow
Early init computes layout from the physical ID map address and linear-map DRAM span. The low bits remain the kernel linear VA, while higher tag bits select the HYP region opposite the ID map and may include random bits when KASLR is enabled. Relocation application later rewrites listed HYP-only pointers. Alternative patch callbacks decode original registers and generate replacement AArch64 instructions using the instruction encoder helpers.

## State And Persistence Behavior
Static state `tag_lsb`, `tag_val`, and `va_mask` is initialized once during early boot and then used by relocation and patch callbacks. `hyp_physvirt_offset` is written as EL2-owned shared state. Alternative patching persists in kernel text alternatives.

## Dependencies And Integration Points
The file depends on memblock, randomization, arm64 alternatives, instruction generation, KVM MMU symbols, memory layout helpers, and HYP linker symbols. It integrates with the arm64 alternatives framework and KVM HYP initialization.

## Risks And Edge Cases
- HYP VA layout must not collide with the ID map or lose significant linear-map bits.
- The alternative callbacks assert exact instruction counts; mismatches are fatal.
- VHE bypasses HYP VA translation and NOPs the translation sequence.
- Spectre V3A vector patching must preserve vector slot selection with PC bits and skip the expected preamble.
- Relocation entries must point to valid kernel image VA slots; incorrect linker data corrupts HYP-only pointers.

## Test Signals
Boot tests on VHE and non-VHE systems, KASLR enabled/disabled, different VA sizes, and Spectre V3A-affected hardware are important. KVM init failures, HYP relocation faults, or invalid alternative instruction BUGs are strong signals. Guest entry on non-VHE systems validates the patched translation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/va_layout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic-sys-reg-v3.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic-sys-reg-v3.c

## Purpose
This file provides userspace access descriptors for GICv3 CPU interface system registers. It lets KVM device attributes and the generic sysreg one-reg helpers save, restore, and validate ICC_* and selected ICH_* virtual interrupt controller state.

## Important APIs, Types, And Functions
- `vgic_v3_get_sysreg_table()` returns the local `gic_v3_icc_reg_descs[]` table to sysreg table validation.
- `vgic_v3_has_cpu_sysregs_attr()` checks whether a VGIC sysreg device attribute names a visible descriptor.
- `vgic_v3_cpu_sysregs_uaccess()` maps a `kvm_device_attr` to a `kvm_one_reg` and delegates to generic sysreg get/set helpers.
- ICC VMCR-backed accessors include `set/get_gic_ctlr`, `set/get_gic_pmr`, `set/get_gic_bpr0`, `set/get_gic_bpr1`, `set/get_gic_grpen0`, and `set/get_gic_grpen1`.
- APR accessors include `set/get_gic_ap0r`, `set/get_gic_ap1r`, and shared `set_apr_reg()` / `get_apr_reg()`.
- EL2/ICH accessors include `set/get_gic_ich_reg`, `set/get_gic_ich_apr`, `set/get_gic_icc_sre`, and `set/get_gic_ich_vtr`.

## Control Flow
Userspace supplies a VGIC sysreg attribute encoding. `attr_to_id()` converts it to an ARM64 sysreg one-reg ID. Lookup uses the same `get_reg_by_id()` and descriptor visibility semantics as the main sysreg ABI. Reads and writes then call `kvm_sys_reg_get_user()` or `kvm_sys_reg_set_user()` against the VGIC descriptor table.

## State And Persistence Behavior
ICC_* user-visible state is stored in VGIC CPU state, mostly `struct vgic_vmcr` and `vcpu->arch.vgic_cpu.vgic_v3`. ICH_* EL2 state is stored in vCPU sysreg backing slots when nested virtualization exposes it. Host capability-derived values such as `ICH_VTR_EL2`, SRE, priority bits, ID bits, SEIS, and A3V are validated rather than blindly restored.

## Dependencies And Integration Points
The file depends on GICv3 register definitions, KVM host types, `asm/kvm_emulate.h`, `sys_regs.h`, and VGIC internals. It is called by VGIC device attribute handlers and checked by the main sysreg table initialization.

## Risks And Edge Cases
- Restored `ICC_CTLR_EL1` values must not claim more priority/ID bits or different SEIS/A3V support than host virtual hardware.
- APR indexes are limited by `vgic_v3_max_apr_idx()`; invalid indexes return `-EINVAL`.
- `ICC_SRE_EL1` restore requires SRE set; `ICC_SRE_EL2` and `ICH_VTR_EL2` are fixed values.
- EL2 descriptors are hidden unless nested virtualization is enabled for the vCPU.
- `get_gic_grpen1()` uses `FIELD_GET` rather than `FIELD_PREP` for the returned value, which is worth scrutinizing if behavior looks asymmetric.

## Test Signals
Migration/save-restore tests for VGICv3 CPU sysregs are direct coverage. Negative tests should try invalid priority bits, ID bits, APR indexes, disabled SRE, and hidden EL2 attributes without NV. Nested virtualization tests should verify ICH_* exposure and values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic-sys-reg-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/trace.h -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/trace.h

## Purpose
This VGIC trace header defines a tracepoint for pending interrupt state updates in the virtual interrupt controller.

## Important APIs, Types, And Functions
- `TRACE_EVENT(vgic_update_irq_pending)` records vCPU ID, IRQ number, and pending level.

## Control Flow
VGIC code calls the generated `trace_vgic_update_irq_pending()` helper when an interrupt pending state changes. The trace event captures fields and formats a concise line for tracefs/perf consumers.

## State And Persistence Behavior
No VGIC state is mutated or persisted here. Event samples are transient trace buffer data when tracing is enabled.

## Dependencies And Integration Points
It depends on Linux tracepoint infrastructure and is part of `TRACE_SYSTEM kvm`. `TRACE_INCLUDE_PATH` points back to the VGIC source directory so trace generation can find this header.

## Risks And Edge Cases
Tracepoint field names and event names are consumed by tooling. Because this is on interrupt paths, enabled tracing overhead should stay small.

## Test Signals
Enable `events/kvm/vgic_update_irq_pending` and inject SGIs, PPIs, SPIs, or LPIs. Kernel build validates trace macro paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-debug.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-debug.c

## Purpose
This file implements VGIC debugfs views. It exposes distributor/vCPU IRQ state through `vgic-state` and ITS device/event translation table state through `vgic-its-state@<base>`.

## Important APIs, Types, And Functions
- `vgic_debug_init()` creates the VM-level `vgic-state` debugfs file.
- `vgic_debug_destroy()` is currently a no-op.
- `vgic_its_debug_init()` creates an ITS-specific debugfs file.
- `vgic_its_debug_destroy()` is currently a no-op.
- `struct vgic_state_iter` tracks distributor, vCPU, and INTID iteration for the VGIC state seq file.
- `struct vgic_its_iter` tracks current ITS device and interrupt translation entry.
- Seq operations are implemented by `vgic_debug_start/next/stop/show` and `vgic_its_debug_start/next/stop/show`.

## Control Flow
For `vgic-state`, seq iteration starts with distributor metadata, then walks private IRQs for each vCPU, SPIs, and LPIs in the distributor xarray. `vgic_debug_show()` prints distributor state first, skips IRQ details until VGIC initialization, obtains the current IRQ object, locks `irq_lock`, prints stable fields, unlocks, and drops the IRQ reference.

For ITS debugfs, `vgic_its_debug_start()` locks `its_lock`, finds the first device and ITE, advances to the requested seq offset, and returns an iterator. `next` advances within a device or to the next device. `show` prints a device header at the first ITE and then event ID to INTID/HWINTID/target/collection mapping.

## State And Persistence Behavior
The file does not own VGIC state; it snapshots existing distributor, IRQ, LPI xarray, and ITS tables. It allocates short-lived iterators per seq read. IRQ fields are protected by `irq_lock`; LPI xarray enumeration uses RCU; ITS table traversal holds `its_lock` for the seq session.

## Dependencies And Integration Points
It depends on debugfs, seq_file, interrupt APIs, KVM host structures, VGIC internals, RCU/xarray for LPIs, and ITS data structures. It is initialized from `vgic_init()` and ITS device creation paths.

## Risks And Edge Cases
- Iteration over LPIs switches from sequential INTIDs to xarray-driven lookup after SPIs; off-by-one errors can skip or repeat high INTIDs.
- Debug output must handle uninitialized VGICs and missing IRQ objects.
- Hardware SGI pending state may need `irq_get_irqchip_state()` rather than the cached latch.
- `vgic_its_debug_start()` returns `NULL` without unlocking `its_lock` if no device exists, which is a subtle path to review against seq_file expectations.
- Debugfs lifetime relies on KVM/debugfs teardown to remove files; explicit destroy hooks are no-ops.

## Test Signals
Read debugfs `vgic-state` before and after VGIC init, with multiple vCPUs, SPIs, LPIs, and hardware-backed interrupts. Read ITS debugfs with empty and populated device tables. Lockdep and RCU debug builds are useful for iterator/locking mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-init.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-init.c

## Purpose
This file implements VGIC lifecycle management for arm64 KVM: early initialization, in-kernel interrupt controller creation, vCPU private interrupt allocation, distributor initialization, lazy/full init, resource mapping, teardown, CPU hotplug hooks, host GIC probing, maintenance interrupt setup, and VGIC-related ID register finalization.

## Important APIs, Types, And Functions
- `kvm_vgic_early_init()` initializes static VM VGIC state such as the LPI xarray.
- `kvm_vgic_create()` creates the in-kernel VGIC model requested by userspace or legacy irqchip creation.
- `kvm_vgic_vcpu_init()` initializes per-vCPU VGIC structures and redistributor iodev registration for GICv3.
- `vgic_init()` allocates distributor/SPIs or GICv5 state, initializes direct IRQ support, resets vCPUs, sets default routing, creates debugfs, and marks initialized.
- `kvm_vgic_map_resources()` maps/registers distributor and redistributor/MMIO resources on first vCPU run.
- `kvm_vgic_destroy()` and `kvm_vgic_vcpu_destroy()` tear down VM and vCPU VGIC resources.
- `vgic_lazy_init()` supports legacy GICv2 lazy initialization.
- `kvm_vgic_finalize_idregs()` updates VM ID registers to advertise GICv3 or GICv5 capabilities consistently.
- `kvm_vgic_hyp_init()`, `vgic_set_kvm_info()`, `kvm_vgic_init_cpu_hardware()`, `kvm_vgic_cpu_up()`, and `kvm_vgic_cpu_down()` handle host-side VGIC probing and per-CPU maintenance IRQ/hyp state.

## Control Flow
VM creation starts with `kvm_vgic_early_init()`. Userspace then creates an irqchip with `kvm_vgic_create()` under `kvm->lock`; the function locks all visible vCPUs and `config_lock`, rejects races with vCPU creation and already-run vCPUs, selects max vCPUs/model-specific state, finalizes GIC ID registers, and allocates private IRQ arrays.

`vgic_init()` runs once under `config_lock`, freezes SPI count, allocates distributor IRQs for GICv2/v3 or calls GICv5 init, initializes direct injection if supported, resets all vCPUs, installs default IRQ routing, creates debugfs, and marks the distributor initialized. `kvm_vgic_map_resources()` later registers MMIO iodevs under `slots_lock`/`config_lock` and publishes `dist->ready` with release ordering.

Host probing stores `gic_kvm_info`, probes v2/v3/v5 backends, enables the GICv3 CPU interface static branch when available, registers the maintenance IRQ, and initializes per-CPU list registers.

## State And Persistence Behavior
Persistent VM state lives in `kvm->arch.vgic`: model, in-kernel flag, initialized/ready flags, base addresses, SPI array, redistributor regions, LPI xarray, maintenance INTID, GICv5 VM state, implementation revision, and direct IRQ capability. Per-vCPU state includes private IRQ arrays, active/pending lists, redistributor iodev base, and GICv3/v5 CPU interface fields. Destruction frees SPIs, private IRQs, redistributor regions, direct IRQ/v4 state, and xarray state.

## Dependencies And Integration Points
The file integrates with KVM vCPU creation locks, KVM memory slots/iodev registration, VGIC v2/v3/v4/v5 backend helpers, arch timer PPI initialization, IRQ routing, debugfs, host GIC driver-provided `gic_kvm_info`, percpu maintenance IRQs, nested virtualization maintenance handling, and sysreg ID register helpers.

## Risks And Edge Cases
- Creation must exclude concurrent vCPU creation and vCPU ioctls; otherwise private IRQ arrays or model limits can become inconsistent.
- VGIC creation is forbidden after any vCPU has run.
- GICv2 supports lazy initialization; GICv3/GICv5 require explicit initialization.
- Resource mapping failures mark the VM dead after partial mapping errors.
- Lock ordering between `slots_lock`, `config_lock`, and vCPU teardown is explicitly managed to avoid inversions.
- GICv5 creation reinitializes arch timer PPIs because INTID assignments differ.
- ID registers must match the actual in-kernel irqchip model, especially on GICv5 hosts that can emulate legacy GICv3.

## Test Signals
KVM selftests and QEMU boots should cover GICv2 legacy irqchip, GICv3 device API, GICv5 where available, vCPU creation races, creation-after-run rejection, default IRQ routing, first-run MMIO resource mapping, VM teardown, CPU hotplug maintenance IRQ enable/disable, and ID register values before and after irqchip creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-irqfd.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-irqfd.c

## Purpose
This file connects KVM irqfd/routing infrastructure to arm64 VGIC interrupt injection. It supports IRQCHIP routing for SPIs and MSI routing through a VGIC ITS, including an atomic fast path.

## Important APIs, Types, And Functions
- `kvm_set_routing_entry()` converts userspace `kvm_irq_routing_entry` records into kernel routing entries for IRQCHIP and MSI routes.
- `kvm_set_msi()` injects an MSI via VGIC ITS for irqfd and userspace MSI injection.
- `kvm_arch_set_irq_inatomic()` attempts fast in-atomic irqfd injection for MSI cached translations or SPI line injection.
- `kvm_vgic_setup_default_irq_routing()` creates default IRQCHIP routing entries for all SPIs.
- `vgic_irqfd_set_irq()` is the IRQCHIP route callback that maps a pin to an SPI INTID and calls `kvm_vgic_inject_irq()`.
- `kvm_populate_msi()` copies MSI fields from the kernel routing entry into `struct kvm_msi`.

## Control Flow
Userspace routing updates call `kvm_set_routing_entry()`, which validates IRQCHIP pins/chips or stores MSI address/data/flags/devid. IRQCHIP injection adds `VGIC_NR_PRIVATE_IRQS` to the pin to form the SPI INTID, validates it, and injects the level. MSI injection requires an ITS and ignores deasserted level calls.

The atomic path rejects deassertions with `-EWOULDBLOCK`. MSI routes use cached ITS translation when an ITS exists. IRQCHIP routes can inject SPIs in atomic context if the VGIC is initialized. Otherwise callers fall back to the non-atomic path.

## State And Persistence Behavior
Routing entries persist in KVM’s generic IRQ routing table, not in this file. Default routing allocation is temporary and freed after `kvm_set_irq_routing()`. Injection mutates VGIC IRQ pending/line state through VGIC helpers.

## Dependencies And Integration Points
The file depends on KVM IRQ routing, irqfd callbacks, VGIC IRQ injection, ITS MSI injection and cached translation, and VGIC initialization state. It is called from generic KVM irqfd/eventfd and irq routing paths.

## Risks And Edge Cases
- IRQCHIP pins are zero-based SPIs and must be translated by `VGIC_NR_PRIVATE_IRQS`.
- Invalid SPI ranges return `-EINVAL`.
- MSI injection requires an ITS and returns `-ENODEV` without one.
- Deasserted MSI or atomic deassertion is not injected.
- Atomic SPI injection is only valid after VGIC initialization.
- Default routing count follows `dist->nr_spis`; incorrect SPI sizing propagates into routing setup.

## Test Signals
Tests should cover default SPI route creation, irqfd SPI injection, userspace SPI injection, MSI injection with and without ITS, atomic irqfd fast path, invalid pins/chips, invalid SPI ranges, and deassertion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-irqfd.c -->
