# subset-b-000891 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.c

## Purpose

`cpuid.c` owns x86 KVM's CPUID model construction, userspace CPUID ioctl plumbing, vCPU CPUID installation, runtime CPUID adjustments, and CPUID instruction emulation. It bridges raw host CPUID, KVM's feature support policy, kernel feature state, vendor hooks, paravirtual leaves, and the guest-visible `struct kvm_cpuid_entry2` array stored on each vCPU.

The file has two main responsibilities:

- Build global KVM-supported feature masks in `kvm_cpu_caps[]`, then use those masks to produce supported/emulated CPUID leaf arrays for userspace.
- Accept a userspace-provided CPUID model for a vCPU, derive KVM's cached guest capability state from it, and answer guest CPUID instructions from that model with runtime corrections.

## Important APIs, Types, And Functions

- `u32 kvm_cpu_caps[NR_KVM_CPU_CAPS]`: global KVM CPU capability bitmap indexed by reverse CPUID feature leaves.
- `bool kvm_is_configuring_cpu_caps`: guards mutation of `kvm_cpu_caps[]` during initialization.
- `struct cpuid_xstate_sizes` and `xstate_sizes[]`: cached CPUID.0xD subleaf sizes used to compute XSAVE area requirements.
- `kvm_init_xstate_sizes()`: init-time probe of xstate component size/offset metadata.
- `xstate_required_size()`: computes standard or compacted XSAVE size for an xfeature bitmap.
- `kvm_find_cpuid_entry2()`: linear CPUID-entry lookup with significant-index handling and a lockdep assertion against hotpath/IRQ-disabled use.
- `kvm_check_cpuid()`: validates installed vCPU CPUID, including virtual-address widths and dynamic user xfeatures that need guest FPU enabling.
- `kvm_vcpu_after_set_cpuid()`: core post-install hook that rebuilds `vcpu->arch.cpu_caps`, dynamic feature bits, xcr0/xss support, max physical address state, paravirtual feature state, PMU state, Hyper-V state, MMU state, vendor hooks, and intercept recalculation.
- `kvm_set_cpuid()`: transactional setter for a vCPU's CPUID array. It swaps new entries into the vCPU, validates, updates derived state, and rolls back on failure.
- `kvm_vcpu_ioctl_set_cpuid()`, `kvm_vcpu_ioctl_set_cpuid2()`, `kvm_vcpu_ioctl_get_cpuid2()`: ABI handlers for legacy and current vCPU CPUID ioctls.
- `kvm_initialize_cpu_caps()`: initializes global supported CPU feature masks using `kvm_cpu_cap_init()` and feature-class macros such as `F`, `EMULATED_F`, `SYNTHESIZED_F`, `PASSTHROUGH_F`, `VENDOR_F`, and `RUNTIME_F`.
- `__do_cpuid_func()` / `do_cpuid_func()` / `get_cpuid_func()`: generate supported or emulated CPUID arrays for `KVM_GET_SUPPORTED_CPUID` and `KVM_GET_EMULATED_CPUID`.
- `kvm_dev_ioctl_get_cpuid()`: device-level supported/emulated CPUID ioctl implementation.
- `kvm_cpuid()`: guest CPUID query engine used by emulation and other KVM code.
- `kvm_emulate_cpuid()`: emulates the guest `CPUID` instruction, including CPUID-faulting checks and register updates.

## Control Flow

Global feature setup starts at `kvm_initialize_cpu_caps()`. The function clears `kvm_cpu_caps[]`, enables the configuration guard, then initializes many CPUID feature words. Each `kvm_cpu_cap_init()` block combines KVM policy, raw host CPUID, Linux kernel capabilities, synthesized mitigation bits, passthrough bits, and emulated bits. Follow-up policy clears or sets features based on TDP, OSPKE, shadow stacks, smaller MAXPHYADDR emulation, mitigation availability, PMU support, SEV/SGX/SVM vendor enablement, and MSR sanity checks.

Userspace supported-CPUID discovery enters through `kvm_dev_ioctl_get_cpuid()`. It allocates a bounded temporary `kvm_cpuid_array`, validates padding for the emulated ioctl, then walks basic, extended, Centaur, and KVM hypervisor bases through `get_cpuid_func()`. `__do_cpuid_func()` pins to one CPU with `get_cpu()`, reads host leaves through `do_host_cpuid()`, and applies leaf-specific KVM overrides. Indexed leaves such as 4, 7, 0xD, 0x12, 0x14, 0x1D, 0x1E, and 0x24 may append subleaf entries until architectural or KVM-imposed limits are reached.

vCPU CPUID installation enters through one of the set ioctls. Legacy `KVM_SET_CPUID` entries are converted to `kvm_cpuid_entry2`; `KVM_SET_CPUID2` copies the current ABI format directly from userspace. `kvm_set_cpuid()` swaps the incoming array into `vcpu->arch.cpuid_entries` so validation can inspect the new model in place. If the vCPU has already run or nested state prevents CPUID changes, the new model must compare equal to the old model after runtime updates. Otherwise KVM initializes Hyper-V/Xen side state if present, validates dynamic xfeatures, and calls `kvm_vcpu_after_set_cpuid()`. On any failure, the old CPUID array and `cpu_caps` snapshot are restored.

Guest CPUID execution is handled by `kvm_cpuid()`. It updates dynamic bits if dirty, looks for an exact function/index match, optionally falls back to Intel-style out-of-range semantics via `get_out_of_range_cpuid_entry()`, copies entry registers, then applies per-query runtime adjustments such as TSX masking through `MSR_IA32_TSX_CTRL`, Hyper-V invariant TSC suppression, and Xen TSC leaf refresh. If no entry exists, most outputs become zero, with topology leaves preserving index low bits and x2APIC ID when an indexed topology model exists.

## State And Persistence

Global persistent state is `kvm_cpu_caps[]`, `kvm_is_configuring_cpu_caps`, and init-only `xstate_sizes[]`. Per-vCPU persistent state includes `arch.cpuid_entries`, `arch.cpuid_nent`, `arch.cpu_caps`, `arch.cpuid_dynamic_bits_dirty`, `guest_supported_xcr0`, `guest_supported_xss`, `pv_cpuid.features`, `is_amd_compatible`, `maxphyaddr`, and `reserved_gpa_bits`.

Runtime CPUID bits are deliberately not permanent userspace ownership: `kvm_update_cpuid_runtime()` rewrites OSXSAVE, APIC, MWAIT, OSPKE, and XSAVE size fields based on CR4, APIC base, `IA32_MISC_ENABLE`, XCR0, and IA32_XSS. This makes the vCPU CPUID array both guest ABI state and a live view with KVM-owned dynamic fields.

Memory ownership is explicit. Set ioctls allocate copied arrays with `vmemdup_array_user()` or `kvmalloc_objs()`. On success, the incoming array becomes the vCPU's CPUID storage and the old array is freed. On failure, the incoming array is freed by the caller after rollback.

## Dependencies And Integration Points

The file depends on Linux x86 CPUID helpers, FPU xstate helpers, KVM x86 core state, vendor callbacks, PMU, LAPIC, MMU, Hyper-V, Xen, SGX, and uaccess allocation/copy helpers. Important integration calls include `kvm_pmu_refresh()`, `kvm_hv_set_cpuid()`, `kvm_hv_vcpu_init()`, `kvm_x86_call(vcpu_after_set_cpuid)`, `kvm_mmu_after_set_cpuid()`, `kvm_make_request(KVM_REQ_RECALC_INTERCEPTS)`, and `fpu_enable_guest_xfd_features()`.

The header `cpuid.h` exposes most external entry points and inline predicates used by MMU, MSR, emulator, PMU, and vendor code. `emulate.c` ultimately reaches this logic through the emulator ops `get_cpuid()` hook and the dedicated `kvm_emulate_cpuid()` fast path in KVM x86.

## Risks And Maintenance Notes

- CPUID feature masks encode ABI policy. Accidentally advertising a feature before all MSR, CR, XSAVE, MMU, PMU, or emulator pieces exist can expose unusable guest state.
- Dynamic CPUID bits are stored in the same entries userspace set. Callers must update dirty state before comparing, copying, or emulating CPUID, or userspace-visible equality and guest-visible answers can diverge.
- `kvm_find_cpuid_entry2()` is linear and explicitly discouraged in IRQ-disabled hotpaths. New call sites should cache derived feature decisions in `vcpu->arch.cpu_caps` or other vCPU fields.
- CPUID after `KVM_RUN` is intentionally constrained. The equality escape hatch is legacy compatibility, not permission to mutate guest CPU topology, MAXPHYADDR, page-size support, or nested virtualization behavior.
- XSTATE handling depends on consistency among CPUID.0xD, host xstate support, KVM filtered xcr0/xss masks, and guest FPU state sizing.
- Out-of-range CPUID behavior differs by vendor and hypervisor sub-class. Incorrect fallback semantics can affect guest OS CPU vendor probing.

## Test Signals

- KVM selftests for `KVM_GET_SUPPORTED_CPUID`, `KVM_GET_EMULATED_CPUID`, `KVM_SET_CPUID2`, and post-run CPUID equality behavior.
- Guest CPUID instruction tests for indexed leaves, out-of-range leaves, vendor differences, KVM/Hyper-V/Xen hypervisor ranges, topology leaves, TSX masking, invariant TSC suppression, and CPUID faulting.
- XSAVE/XFD tests that expose dynamic xfeatures and verify guest FPU state sizing, XCR0/XSS masks, and CPUID.0xD size fields.
- MMU tests around MAXPHYADDR, GuestPhysAddrSize, GBPAGES, LA57, smaller MAXPHYADDR emulation, SHSTK/IBT exposure, and TDP versus shadow paging.
- PMU and mitigation tests for CPUID.0xA, 0x80000022, SPEC_CTRL/STIBP/SSBD/IBPB-derived leaves, and unsupported MSR sanity clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.h

## Purpose

`cpuid.h` is the shared interface for x86 KVM CPUID capability management and guest CPUID queries. It declares the CPUID ioctl and emulation entry points implemented by `cpuid.c`, exposes global KVM CPU capability storage, and provides hot inline helpers for querying guest features, physical-address legality, paravirtual feature enforcement, and selected MSR availability.

## Important APIs, Types, And Functions

- `extern u32 kvm_cpu_caps[NR_KVM_CPU_CAPS]`: global KVM feature words.
- `extern bool kvm_is_configuring_cpu_caps`: mutation guard for initialization-time capability edits.
- `kvm_initialize_cpu_caps()` and `kvm_finalize_cpu_caps()`: bracket global capability initialization.
- `kvm_find_cpuid_entry2()`, `kvm_find_cpuid_entry_index()`, `kvm_find_cpuid_entry()`: CPUID entry lookup helpers. `KVM_CPUID_INDEX_NOT_SIGNIFICANT` is a private sentinel for non-indexed lookups.
- `kvm_dev_ioctl_get_cpuid()`, `kvm_vcpu_ioctl_set_cpuid()`, `kvm_vcpu_ioctl_set_cpuid2()`, `kvm_vcpu_ioctl_get_cpuid2()`: ioctl-facing CPUID API declarations.
- `kvm_cpuid()`: guest CPUID query helper.
- `kvm_init_xstate_sizes()` and `xstate_required_size()`: xstate sizing helpers.
- `cpuid_query_maxphyaddr()`, `cpuid_query_maxguestphyaddr()`, `kvm_vcpu_reserved_gpa_bits_raw()`: physical-address width helpers.
- GPA validation helpers: `cpuid_maxphyaddr()`, `kvm_vcpu_is_legal_gpa()`, `kvm_vcpu_is_legal_aligned_gpa()`, and `page_address_valid()`.
- Capability bit helpers: `cpuid_entry_override()`, `kvm_cpu_cap_clear()`, `kvm_cpu_cap_set()`, `kvm_cpu_cap_get()`, `kvm_cpu_cap_has()`, `kvm_cpu_cap_check_and_set()`.
- Guest capability helpers: `guest_cpuid_has()`, `guest_cpu_cap_set()`, `guest_cpu_cap_clear()`, `guest_cpu_cap_change()`, `guest_cpu_cap_has()`.
- Guest model helpers: `guest_cpuid_is_amd_compatible()`, `guest_cpuid_is_intel_compatible()`, `guest_cpuid_family()`, `guest_cpuid_model()`, `guest_cpuid_stepping()`, `cpuid_model_is_consistent()`.
- MSR exposure helpers: `supports_cpuid_fault()`, `cpuid_fault_enabled()`, `guest_has_spec_ctrl_msr()`, `guest_has_pred_cmd_msr()`.

## Control Flow

Most functions are inline helpers consumed by other KVM x86 compilation units. Capability initialization code calls `kvm_cpu_cap_set()` and `kvm_cpu_cap_clear()` while `kvm_is_configuring_cpu_caps` is true; `kvm_finalize_cpu_caps()` flips that guard off. CPUID-generation code uses `cpuid_entry_override()` to overwrite a register in a leaf with a KVM capability word.

Guest feature queries normally use `guest_cpu_cap_has()`, which reads KVM's cached `vcpu->arch.cpu_caps` instead of scanning raw CPUID entries. The exception is `guest_cpuid_has()` for `X86_FEATURE_XSAVES`, which intentionally reads raw userspace CPUID because KVM may need to treat XSAVES as usable internally while still rejecting direct XSS access if userspace did not expose it.

Physical address validation uses the per-vCPU cached `reserved_gpa_bits` mask. `kvm_vcpu_is_legal_cr3()` additionally strips LAM CR3 tag bits when the guest has LAM before checking GPA legality.

## State And Persistence

The header itself stores no state, but it defines access patterns for persistent state from `cpuid.c` and `struct kvm_vcpu_arch`: `cpuid_entries`, `cpuid_nent`, `cpu_caps`, `maxphyaddr`, `reserved_gpa_bits`, `pv_cpuid`, `msr_platform_info`, and `msr_misc_features_enables`.

The distinction between raw CPUID entries and cached guest CPU capabilities is important. Raw entries preserve the userspace ABI model; `cpu_caps` is KVM's operational view after masking with KVM-supported and emulated features.

## Dependencies And Integration Points

The header depends on `reverse_cpuid.h`, Linux CPU/processor helpers, and the KVM paravirtual UAPI. It is included by KVM x86 core files that need feature predicates, address validation, CPUID ioctls, and MSR exposure checks. `emulate.c` indirectly relies on these helpers through the emulator operations that check `guest_has_*` features and validate page addresses.

## Risks And Maintenance Notes

- `KVM_CPUID_INDEX_NOT_SIGNIFICANT` must remain consumed as a `u64`; using it as a `u32` could collide with valid guest CPUID indices.
- `guest_cpu_cap_has()` forbids dynamic APIC, OSXSAVE, and OSPKE queries at compile time because those bits require runtime updates. New dynamic features should get the same treatment.
- `guest_cpuid_has()` is intentionally restricted to XSAVES. Expanding its special-case allowlist risks bypassing KVM's derived capability model.
- GPA legality is only as current as `vcpu->arch.reserved_gpa_bits`; callers that change CPUID/MAXPHYADDR must refresh derived state before using these helpers.
- Capability mutation helpers warn if used outside initialization. Vendor code that wants to enable features after the generic pass must still run during the guarded configuration window.

## Test Signals

- Build-time coverage from `BUILD_BUG_ON()` in feature helpers and dynamic-feature guards.
- Unit or selftest coverage for CPUID entry lookup with significant and non-significant indices.
- Guest behavior tests for XSAVES/XSS, CPUID fault MSRs, SPEC_CTRL/PRED_CMD exposure, LAM-tagged CR3, and GPA alignment/legal-address predicates.
- Regression checks that new features are queried through `guest_cpu_cap_has()` unless they have a documented raw-CPUID exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/debugfs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/debugfs.c

## Purpose

`debugfs.c` creates x86-specific KVM debugfs files for per-vCPU timing state and per-VM MMU reverse-map statistics. The file is diagnostic-only: it exposes read-only or seqfile views of live KVM state so developers can inspect guest mode, TSC virtualization parameters, LAPIC timer advancement, and rmap density by page size.

## Important APIs, Types, And Functions

- `kvm_arch_create_vcpu_debugfs()`: creates per-vCPU debugfs files under a vCPU debugfs directory.
- `kvm_arch_create_vm_debugfs()`: creates VM-level `mmu_rmaps_stat`.
- Simple attribute getters:
  - `vcpu_get_timer_advance_ns()`
  - `vcpu_get_guest_mode()`
  - `vcpu_get_tsc_offset()`
  - `vcpu_get_tsc_scaling_ratio()`
  - `vcpu_get_tsc_scaling_frac_bits()`
- `DEFINE_SIMPLE_ATTRIBUTE(...)`: binds each getter to a read-only file operation.
- `kvm_mmu_rmaps_stat_show()`: seqfile renderer that builds histograms of rmap-list counts for 4K, 2M, and 1G page levels.
- `kvm_mmu_rmaps_stat_open()` / `kvm_mmu_rmaps_stat_release()`: safely pin and release the VM while the seqfile is open.
- `mmu_rmaps_stat_fops`: file operations for the VM rmap statistics file.

## Control Flow

For vCPU debugfs setup, `kvm_arch_create_vcpu_debugfs()` unconditionally creates `guest_mode` and `tsc-offset`. It conditionally creates `lapic_timer_advance_ns` only when the vCPU has an in-kernel LAPIC, and creates TSC scaling files only when `kvm_caps.has_tsc_control` is true.

The VM-level rmap seqfile starts in `kvm_mmu_rmaps_stat_open()`, which uses `kvm_get_kvm_safe()` to avoid dereferencing a dying VM. `kvm_mmu_rmaps_stat_show()` returns early if the VM has no rmaps. Otherwise it allocates one histogram array per KVM page size, locks `slots_lock`, takes the MMU write lock, walks every address-space id and memory slot, and counts `pte_list_count()` for each `struct kvm_rmap_head`. Counts are bucketed by `ffs(count)` into logarithmic ranges up to `RMAP_LOG_SIZE - 1`. It then unlocks, prints a header and one line per page size, frees the histograms, and returns the status.

## State And Persistence

No persistent KVM state is modified. The simple debugfs files read live fields from `struct kvm_vcpu` and `kvm_caps`. The rmap report temporarily allocates per-read histograms with `kcalloc()` and frees them before returning. The open path pins the VM reference for the lifetime of the seqfile and release drops that reference with `kvm_put_kvm()`.

The rmap show path takes `kvm->slots_lock` and `kvm->mmu_lock` to snapshot memory-slot and rmap structures consistently enough for diagnostics.

## Dependencies And Integration Points

The file depends on Linux `debugfs`, `seq_file`, KVM host structures, LAPIC helpers, MMU internals, and memory-slot iteration helpers. It integrates with generic KVM debugfs creation through architecture hooks named `kvm_arch_create_vcpu_debugfs()` and `kvm_arch_create_vm_debugfs()`.

`mmu_rmaps_stat` reaches into MMU internals through `kvm_memslots_have_rmaps()`, `kvm_arch_nr_memslot_as_ids()`, `__kvm_memslots()`, `kvm_for_each_memslot()`, `kvm_mmu_slot_lpages()`, and `pte_list_count()`.

## Risks And Maintenance Notes

- `vcpu_get_timer_advance_ns()` assumes `vcpu->arch.apic` exists; the file is only created when `lapic_in_kernel(vcpu)` is true.
- `mmu_rmaps_stat` can be expensive for large VMs because it walks every rmap entry under MMU locking. It is a debugfs diagnostic, not a low-overhead telemetry path.
- The rmap histogram saturates into the last bucket if `ffs(count)` exceeds `RMAP_LOG_SIZE - 1`, guarded by `WARN_ON_ONCE()`.
- Lock ordering matters: the code takes `slots_lock` before `mmu_lock`. Future diagnostics should preserve established KVM MMU lock ordering.
- Debugfs ABI is less formal than KVM ioctls, but scripts may still consume these names and formats.

## Test Signals

- Boot/run KVM with debugfs mounted and verify per-vCPU files appear according to LAPIC and TSC-scaling capabilities.
- Read `guest_mode`, `tsc-offset`, `tsc-scaling-ratio`, and LAPIC timer advance files while vCPUs are active.
- Read `mmu_rmaps_stat` on VMs with and without rmaps, with multiple memslots, and with large pages enabled.
- Use lockdep/KASAN/KCSAN signals for concurrent VM teardown, memslot updates, and debugfs reads.
- Fault-injection or allocation-failure tests for histogram allocation in `kvm_mmu_rmaps_stat_show()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/emulate.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/emulate.c

## Purpose

`emulate.c` is KVM's generic x86 instruction decoder and emulator. It decodes x86 instruction bytes into an `x86_emulate_ctxt`, performs architectural privilege, mode, segment, memory, and intercept checks, executes supported instructions either through C handlers or small inline assembly snippets, and writes back guest-visible register/memory/FPU state through the `x86_emulate_ops` callback table.

The emulator is used when KVM cannot or should not let hardware execute an instruction directly, such as MMIO accesses, shadow page-table writes, selected privileged instructions, emulation-on-#UD instructions, string I/O, task switching, real-mode interrupt handling, and some FPU/SIMD state instructions.

## Important APIs, Types, And Functions

- Operand/decoder flag macros: `Op*`, `Dst*`, `Src*`, `ByteOp`, `ModRM`, `Lock`, `Priv`, `Prot`, `String`, `PageTable`, `Intercept`, `CheckPerm`, `Sse`, `Mmx`, `Avx`, `ShadowStack`, `IsBranch`, and related flags.
- Decode table structures: `struct opcode`, `struct group_dual`, `struct gprefix`, `struct escape`, `struct instr_dual`, and `struct mode_dual`.
- Opcode tables: `opcode_table[256]`, `twobyte_table[256]`, `opcode_map_0f_38[256]`, plus grouped and prefix-selected sub-tables.
- Public entry points:
  - `x86_decode_insn()`
  - `x86_emulate_insn()`
  - `init_decode_cache()`
  - `emulator_task_switch()`
  - `emulate_int_real()`
  - `x86_page_table_writing_insn()`
  - `emulator_invalidate_register_cache()`
  - `emulator_writeback_register_cache()`
  - `emulator_can_use_gpa()`
- Address and memory helpers: `__linearize()`, `linearize()`, `segmented_read()`, `segmented_write()`, `segmented_cmpxchg()`, `read_emulated()`, `linear_read_system()`, `linear_write_system()`.
- Decode helpers: `decode_modrm()`, `decode_abs()`, `decode_operand()`, `decode_imm()`, `x86_decode_avx()`, `read_descriptor()`.
- Execution helpers: many `em_*` instruction handlers for arithmetic, stack, segment, branches, syscalls, control/debug registers, MSRs, CPUID, I/O, FXSAVE/FXRSTOR, XSETBV, task switches, and string instructions.
- Inline assembly generator macros: `EM_ASM_*`, which implement many ALU operations while preserving and updating emulated EFLAGS.

## Control Flow

`init_decode_cache()` clears conditionally written decode fields, register-cache state, and read-ahead caches. `x86_decode_insn()` then initializes fetch pointers, determines default operand/address size from emulator mode and CS attributes, consumes legacy/REX/VEX prefixes, selects opcode table entries, resolves group/prefix/escape/mode-dual indirections, rejects unsupported encodings, adjusts operand sizes for mode-specific flags, decodes ModR/M and SIB addressing, sets segment defaults, fetches immediates/register operands, and records memory operands for later access. Decode returns `EMULATION_OK` only if all fetch and decode steps reach `X86EMUL_CONTINUE`.

`x86_emulate_insn()` executes a decoded instruction. It first validates LOCK legality, mode restrictions, undefined/no64 cases, SIMD/FPU CR0 and CR4 prerequisites, AVX XCR0 prerequisites, MMX pending x87 faults, intercept callbacks, protected/privileged instruction checks, instruction-specific permissions, and REP string early termination. It then performs source and destination memory reads unless suppressed by flags such as `NoAccess`, `Mov`, or implicit operands.

Execution happens either through a table-provided handler (`ctxt->execute`) or through switch statements for simple one-byte/two-byte instructions. After execution, `writeback()` writes changed source and destination operands to registers, memory, XMM/YMM, or MMX state. String instructions update RSI/RDI/RCX and may return `EMULATION_RESTART` to resume long REP operations in bounded chunks. On success `_eip` becomes committed to `eip`; on faults, exceptions are stored in `ctxt->exception` and `ctxt->have_exception`.

Segment and control-transfer emulation flows through `__load_segment_descriptor()`, `assign_eip()`, `assign_eip_far()`, and specialized handlers such as `em_call_far()`, `em_ret_far()`, `em_syscall()`, `em_sysenter()`, and `em_sysexit()`. These paths enforce selector, descriptor, CPL/RPL/DPL, present-bit, long-mode, canonical-address, CET-related, and task-switch semantics where implemented.

Task switching is handled by `emulator_task_switch()`, which invalidates register caches, calls `emulator_do_task_switch()`, saves old TSS state, loads new 16-bit or 32-bit TSS state, updates busy/NT/TS/debug state, optionally pushes an error code, then writes registers back.

## State And Persistence

The primary mutable state is `struct x86_emulate_ctxt`. It holds decoded flags, opcode bytes, operand structures, effective IP, EFLAGS, exception state, read caches, register cache dirty/valid bitmaps, prefix state, memory operands, intercept metadata, and operation callbacks. The emulator persists guest-visible changes only through `ctxt->ops`: GPR writes, segment loads, CR/DR/MSR writes, xcr writes, memory writes/cmpxchg, PIO, FPU register access, interruptibility state, NMI mask, halt, SMM exit, TLB invalidation, and descriptor-table updates.

Memory read caching in `ctxt->mem_read` allows MMIO re-emulation to replay reads in the same order without dangling stack pointers. PIO input read-ahead uses `ctxt->io_read` to batch REP INS data. Register writeback is deferred through the register cache and committed by `writeback_registers()` unless the instruction faults or is intercepted.

FPU/SIMD state is transiently accessed through `kvm_fpu_get()`/`kvm_fpu_put()` and helpers from `fpu.h`. The emulator does not own FPU state permanently; it reads/writes current vCPU FPU registers while holding the kernel FPU state lock.

## Dependencies And Integration Points

The file depends on `kvm_emulate.h` for `struct x86_emulate_ctxt`, operand definitions, return codes, and `x86_emulate_ops`. It integrates heavily with KVM x86 core through callbacks for register, memory, segment, descriptor-table, MSR, CPUID, PMU, PIO, SMM, halt, intercept, and TLB operations. It depends on `fpu.h` for SSE/AVX/MMX register access, `tss.h` for task-state layouts, `mmu.h` for page-table write classification, and x86 architectural headers for descriptors, debug registers, CET, EFER, CR bits, and exception vectors.

Decode table intercept metadata lets vendor-specific VMX/SVM code receive pre-exception, post-exception, and post-memory-access intercept checks. CPUID emulation calls `ctxt->ops->get_cpuid()`, which is backed by the CPUID model maintained in `cpuid.c`. Page-table-writing flags are exposed through `x86_page_table_writing_insn()` so MMU code can identify instructions that modify page tables.

## Risks And Maintenance Notes

- Decode table flags are dense and semantic. Missing `Priv`, `Prot`, `Lock`, `PageTable`, `NoAccess`, `Intercept`, `CheckPerm`, or operand flags can cause architectural faults, security checks, MMIO behavior, or MMU invalidation decisions to be wrong.
- The emulator intentionally does not support all x86 instructions or all modes. Several protected-mode interrupt/IRET cases, far transfer error recovery, 64-bit FXSAVE/FXRSTOR formats, and CET shadow-stack/IBT affected emulation are rejected or unhandleable.
- Segment loading and task switching are high-risk because partial memory writes or descriptor updates can occur before later faults. Some paths explicitly warn that memory may be tainted on a faulting far call.
- REP string emulation restarts rely on consistent decode, read caches, RF handling, and register updates. Bugs can duplicate or skip MMIO/PIO operations.
- Inline assembly ALU helpers execute host instructions with controlled operands and EFLAGS. Exception tables and flag save/restore must remain correct across compiler and architecture changes.
- SIMD/FPU emulation depends on correct CR0.TS/EM, CR4.OSFXSR/OSXSAVE, XCR0, pending x87 fault, and FPU lock behavior.
- CET-aware rejection is defensive. If future work adds shadow-stack or IBT emulation, control-transfer classification must be audited carefully.

## Test Signals

- KVM emulator selftests and guest tests for MMIO instruction decoding, page-table writes, LOCK/cmpxchg, REP MOVS/CMPS/INS/OUTS, and restart behavior.
- x86 instruction emulator tests covering prefixes, REX/VEX decoding, ModR/M and SIB addressing, RIP-relative addressing, 16/32/64-bit modes, segment overrides, alignment faults, and canonical-address checks.
- Privilege and fault tests for CR/DR/MSR access, CPUID faulting, I/O bitmap permissions, UMIP, RDPMC/RDTSC restrictions, SVME instructions, protected-mode segment loads, and descriptor-table operations.
- FPU/SIMD tests for FNINIT/FNSTCW/FNSTSW, FXSAVE/FXRSTOR, MMX/SSE/AVX moves, CR0.TS/EM, CR4.OSFXSR/OSXSAVE, and XCR0 gating.
- Control-flow tests for near/far call, jmp, ret, syscall/sysenter/sysexit, real-mode int/iret, task switch, CET rejection, and EFLAGS updates.
- Fuzzing of instruction bytes with comparison against hardware behavior where feasible, especially for decode/fault ordering and MMIO side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/emulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/fpu.h

## Purpose

`fpu.h` provides small inline helpers for KVM's x86 emulator to read and write host FPU register files that currently represent guest SIMD/MMX state. It defines vector types for SSE and AVX operands, conversion macros for 128-bit values, raw inline-assembly accessors for XMM/YMM/MM registers, and locking wrappers that ensure the kernel FPU state is loaded and protected while registers are accessed.

## Important APIs, Types, And Functions

- `typedef u32 __attribute__((vector_size(16))) sse128_t`: 128-bit SSE vector representation.
- `typedef u32 __attribute__((vector_size(32))) avx256_t`: 256-bit AVX/YMM vector representation.
- `sse128_lo()`, `sse128_hi()`, `sse128_l0()` through `sse128_l3()`, `sse128(lo, hi)`: helpers to inspect or build `sse128_t` values via 64-bit or 32-bit lanes.
- Raw register helpers:
  - `_kvm_read_avx_reg()` / `_kvm_write_avx_reg()`
  - `_kvm_read_sse_reg()` / `_kvm_write_sse_reg()`
  - `_kvm_read_mmx_reg()` / `_kvm_write_mmx_reg()`
- FPU ownership helpers:
  - `kvm_fpu_get()`
  - `kvm_fpu_put()`
- Public locked wrappers:
  - `kvm_read_avx_reg()` / `kvm_write_avx_reg()`
  - `kvm_read_sse_reg()` / `kvm_write_sse_reg()`
  - `kvm_read_mmx_reg()` / `kvm_write_mmx_reg()`

## Control Flow

Public read/write helpers call `kvm_fpu_get()`, perform a raw register move, and then call `kvm_fpu_put()`. `kvm_fpu_get()` locks FPU register state with `fpregs_lock()`, asserts consistency, and calls `switch_fpu_return()` if `TIF_NEED_FPU_LOAD` indicates registers need to be loaded before direct access. `kvm_fpu_put()` releases the lock.

The raw helpers switch on a numeric register index and emit fixed inline assembly such as `vmovdqa` for YMM, `movdqa` for XMM, and `movq` for MMX. On 64-bit builds, XMM/YMM registers 8 through 15 are available; on 32-bit builds only registers 0 through 7 are handled. Invalid register indices call `BUG()`.

## State And Persistence

The header directly accesses live CPU FPU registers. It does not allocate or own persistent storage; persistence is in the surrounding KVM/vCPU FPU state machinery that has loaded guest state into hardware registers before the emulator touches them. Callers pass stack or context-owned buffers for the copied vector values.

The locking discipline is the key state behavior: direct register access is only safe between `fpregs_lock()` and `fpregs_unlock()`, after any lazy FPU load has been completed.

## Dependencies And Integration Points

The file depends on `<asm/fpu/api.h>` and x86 inline assembly. Its primary consumer in this subset is `emulate.c`, where decode/writeback paths read and write XMM/YMM/MM operands and FPU instruction handlers temporarily execute instructions such as `fninit`, `fnstcw`, `fxsave`, and `fxrstor` under the same FPU locking model.

Because these helpers use architectural register names directly, they are tied to x86 build mode and `CONFIG_X86_64` availability for high SIMD registers.

## Risks And Maintenance Notes

- The helpers assume the caller has already validated that guest instruction state allows SSE/AVX/MMX access. `fpu.h` only enforces FPU loading/locking, not architectural CR0/CR4/XCR0 checks.
- Invalid register indices are fatal via `BUG()`. Decode logic must not pass impossible register numbers.
- AVX helpers use `vmovdqa`, which requires appropriate CPU/toolchain support in contexts where this header is compiled and called.
- XMM/YMM high-register availability differs across 32-bit and 64-bit builds; emulator decode must respect build-mode limits.
- Direct FPU register access is sensitive to preemption/lazy-FPU rules. Any future change to kernel FPU ownership APIs should audit `kvm_fpu_get()` and all raw helper call sites.

## Test Signals

- Emulator tests for SSE, AVX, and MMX register-to-memory and memory-to-register moves, including XMM/YMM 8-15 on 64-bit builds.
- CR0.TS/EM, CR4.OSFXSR/OSXSAVE, and XCR0 gating tests in `emulate.c` before these helpers are reached.
- KASAN/KCSAN/lockdep signals around nested FPU access, preemption, and lazy FPU load paths.
- Build tests for 32-bit and 64-bit x86 configurations to catch invalid high-register assembly cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/fpu.h -->
