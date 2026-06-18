# Research: subset-b-006846

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/aperfmperf_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/aperfmperf_test.c

Purpose: Tests `KVM_X86_DISABLE_EXITS_APERFMPERF`, i.e. KVM's ability to stop intercepting guest reads of `MSR_IA32_APERF` and `MSR_IA32_MPERF` so the guest observes host counter values. It also verifies the default negative behavior: without the capability, guest `RDMSR` of APERF/MPERF injects `#GP`.

Important APIs/types/functions: Host helpers `open_dev_msr()` and `read_dev_msr()` read `/dev/cpu/<cpu>/msr`; guest helpers `guest_read_aperf_mperf()`, `guest_no_aperfmperf()`, `l1_svm_code()`, `l1_vmx_code()`, and `l2_guest_code()` exercise L1 and optional L2 reads. The test uses `KVM_CAP_X86_DISABLE_EXITS`, `KVM_X86_DISABLE_EXITS_APERFMPERF`, `vcpu_alloc_svm()`, `vcpu_alloc_vmx()`, VMX MSR bitmaps, and SVM/VMX nested helpers.

Control flow: `main()` first creates a normal one-vCPU VM and proves APERF/MPERF reads fault. It then pins the host thread, opens the matching host MSR device, creates a VM before adding vCPUs so `KVM_ENABLE_CAP` is legal, enables APERF/MPERF exit disablement, and runs guest code. The guest repeatedly syncs APERF/MPERF values to userspace, then launches nested L2 when SVM or VMX is available. The host brackets each guest value with host MSR reads and asserts `host_before < guest_value < host_after` for both counters.

State and persistence behavior: No persistent storage is used. State consists of the host CPU pinning, the open MSR file descriptor, APERF/MPERF monotonic counter snapshots, and optional nested control pages. Nested setup persists only for the lifetime of the VM.

Dependencies and integration points: Depends on readable `/dev/cpu/*/msr`, x86 APERF/MPERF support, KVM disable-exit capability reporting, selftest ucall plumbing, and nested VMX/SVM helpers. It reaches into host CPU MSRs, so permissions and CPU migration are critical integration points.

Risks and maintenance notes: The strict monotonic bracketing can be sensitive to scheduling, counter behavior, permissions, or systems where APERF/MPERF are unavailable or virtualized differently. The test intentionally requires nonstandard VM construction order because `KVM_ENABLE_CAP` must occur before vCPU creation. Nested VMX relies on explicitly enabling MSR bitmaps because Intel normally requires MSR exiting.

Test signals: Passing means APERF/MPERF are hidden by default, the disable-exits capability exposes live host counter reads to L1 and L2, and nested MSR interception configuration does not break the passthrough behavior. Failures identify capability gating, MSR permission, counter monotonicity, or nested MSR-bitmap regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/aperfmperf_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/apic_bus_clock_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/apic_bus_clock_test.c

Purpose: Verifies KVM's APIC timer bus-frequency emulation when userspace configures `KVM_CAP_X86_APIC_BUS_CYCLES_NS`. It programs the APIC timer with a long initial count, waits for a configurable interval, and checks that the current count drops by the amount implied by the configured APIC bus rate and TDCR divide value.

Important APIs/types/functions: `tdcrs[]` enumerates legal APIC divide configurations; `apic_enable()`, `apic_read_reg()`, and `apic_write_reg()` abstract xAPIC versus x2APIC access; `apic_guest_code()` performs the in-guest timing check; `run_apic_bus_clock_test()` creates/configures the VM; `test_apic_bus_clock()` validates each TDCR case. It uses `KVM_CAP_X86_APIC_BUS_CYCLES_NS`, APIC `TMICT`, `TMCCT`, `TDCR`, and selftest delay helpers.

Control flow: Command-line options select APIC frequency, wait duration, and APIC mode. The host enables the VM capability before running the vCPU. Guest code enables the APIC, iterates over the TDCR table, arms a large-count periodic timer, delays, reads the current count, computes expected decrement, and allows a tolerance around the expected elapsed bus cycles.

State and persistence behavior: State is fully in-memory: configured bus cycles per nanosecond, APIC mode, APIC timer registers, and per-case timing observations. No VM state is saved across process runs.

Dependencies and integration points: Integrates with KVM local APIC emulation, xAPIC MMIO or x2APIC MSR access, the selftest APIC helpers, and host support for the APIC bus clock capability. Timing accuracy depends on guest delay calibration and host scheduling.

Risks and maintenance notes: The 1% tolerance is deliberate but still sensitive to noisy hosts, coarse delays, or unexpected APIC timer implementation details. Changes in APIC divide encoding, x2APIC enablement, or capability units would require corresponding updates.

Test signals: Passing means all supported APIC divide settings decrement `TMCCT` consistently with the configured bus frequency. Failures indicate incorrect APIC timer scaling, xAPIC/x2APIC register access issues, or capability setup regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/apic_bus_clock_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cpuid_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cpuid_test.c

Purpose: Validates KVM CPUID ABI behavior for guest-visible CPUID data, including consistency between userspace-provided CPUID, in-guest `CPUID` results, `KVM_GET_CPUID2`, and immutability rules after a vCPU has run.

Important APIs/types/functions: `struct cpuid_mask` models constant CPUID bits that KVM should not allow userspace to override. `guest_main()` walks guest CPUID entries, `compare_cpuids()` compares expected versus observed entries with masks, `vcpu_alloc_cpuid()` copies CPUID data into guest memory, `run_vcpu()` handles staged ucalls, `set_cpuid_after_run()` tests post-run failure behavior, and `test_get_cpuid2()` validates get/set round trips. It uses `KVM_SET_CPUID2`, `KVM_GET_CPUID2`, `vcpu_get_cpuid()`, `kvm_get_supported_cpuid()`, and ucall syncs.

Control flow: The host prepares a vCPU CPUID table, maps a copy into guest memory, and runs the guest through stages. The guest compares hardware `CPUID` instruction output with the userspace table for each entry. The host then tests that changing CPUID after `KVM_RUN` is rejected where the ABI requires it and that `KVM_GET_CPUID2` returns a coherent table.

State and persistence behavior: CPUID state is vCPU-local and becomes effectively frozen after first run. The only shared state is a guest-memory copy of the expected `kvm_cpuid2` structure.

Dependencies and integration points: Depends on KVM CPUID ioctl semantics, x86 CPUID leaf handling, selftest processor helpers, and paravirtual CPUID leaves. It is a direct ABI conformance test for userspace VMM CPUID management.

Risks and maintenance notes: CPUID constant masks must be updated when KVM or architecture rules change. New leaves or subleaves can expose stale comparison assumptions. Post-run CPUID mutability is ABI-sensitive and should not be relaxed accidentally.

Test signals: Passing means guest CPUID output matches the KVM-configured table except for documented constant bits, `KVM_GET_CPUID2` returns expected data, and post-run `KVM_SET_CPUID2` behavior is preserved. Failures point to CPUID filtering, ioctl ABI, or feature-masking regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cpuid_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cr4_cpuid_sync_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cr4_cpuid_sync_test.c

Purpose: Tests synchronization between guest CR4 feature bits and CPUID exposure for features whose availability depends on CR4 state. The guest toggles CR4 controls and checks CPUID reflects KVM's expected dynamic behavior.

Important APIs/types/functions: `MAGIC_HYPERCALL_PORT` provides a host sync point; `guest_code()` performs CR4/CPUID transitions and port I/O exits; `main()` creates the VM and drives the expected exits. It relies on selftest `set_cr4()`, CPUID helpers, and KVM I/O exits.

Control flow: The guest runs through staged CR4 mutations, using port I/O to give userspace a chance to inspect or continue execution. The host expects KVM I/O exits at the magic port and reports guest assertions on failure.

State and persistence behavior: CR4 state is vCPU architectural state; CPUID exposure is vCPU configuration plus any KVM dynamic synchronization. No persistent external state is touched.

Dependencies and integration points: Integrates with KVM's x86 register emulation, guest CPUID instruction handling, and feature exposure rules. The test is particularly relevant for features that are legal only when their CR4 enabling bit is set.

Risks and maintenance notes: Dynamic CPUID behavior is subtle because some CPUID fields are fixed by userspace while others are derived from runtime state. Architecture additions may require new assertions or mask updates.

Test signals: Passing shows KVM keeps CR4-dependent CPUID output coherent across guest CR4 writes. Failures suggest stale CPUID caching, missed CR4 validation, or incorrect feature exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/cr4_cpuid_sync_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/debug_regs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/debug_regs.c

Purpose: Exercises KVM handling of debug registers, including guest writes to DR6/DR7, general-detect behavior, and interrupt/event interactions around debug-register access.

Important APIs/types/functions: Defines debug bits `DR6_BD` and `DR7_GD`, test interrupt vector `IRQ_VECTOR`, `guest_code()` for in-guest debug-register operations, `vcpu_skip_insn()` for host-side instruction advancement, and `main()` to install handlers and interpret exits. It uses `KVM_GET/SET_REGS`, debug register instructions, APIC helpers, and exception/interrupt plumbing.

Control flow: The guest configures debug-register state, triggers cases that should produce debug exceptions or exits, and uses ucalls to synchronize. The host inspects exit reasons, may skip trapped instructions, and confirms that architectural debug bits are set or cleared as expected.

State and persistence behavior: Debug-register values are vCPU architectural state and must persist across exits. APIC/interrupt state is transient but used to validate that debug-register exceptions do not corrupt event delivery.

Dependencies and integration points: Depends on KVM x86 debug-register emulation, exception injection, APIC interrupt delivery, and selftest register helpers. It probes host/guest behavior that debuggers and VMMs rely on.

Risks and maintenance notes: Debug-register semantics are detail-heavy and differ between trap-like and fault-like paths. Instruction lengths used by `vcpu_skip_insn()` must stay aligned with the guest instruction sequence.

Test signals: Passing indicates KVM preserves and reports debug-register state correctly, honors GD/BD semantics, and handles related exits without losing pending event state. Failures usually implicate DR emulation or exception delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/debug_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/dirty_log_page_splitting_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/dirty_log_page_splitting_test.c

Purpose: Verifies eager page splitting and hugepage restoration behavior when dirty logging is enabled, cleared, and disabled under the TDP MMU. It ensures dirty logging splits huge mappings to 4K pages and that disabling dirty logging allows huge mappings to repopulate.

Important APIs/types/functions: `struct kvm_page_stats` captures `pages_4k`, `pages_2m`, `pages_1g`, and total hugepages; `get_page_stats()`, `run_vcpu_iteration()`, `vcpu_worker()`, and `run_test()` drive the workload. It uses `memstress_create_vm()`, `memstress_enable_dirty_logging()`, `memstress_get_dirty_log()`, `memstress_clear_dirty_log()`, `KVM_CAP_MANUAL_DIRTY_LOG_PROTECT2`, and KVM VM stats.

Control flow: For each guest mode, the test creates a two-vCPU/two-slot memstress VM backed by HugeTLB by default. Worker threads dirty all memory by iteration. The host records page stats after population, after dirty logging enablement, after each dirtying pass, after optional manual clear, after disabling dirty logging, and after repopulation. It runs once without manual dirty-log protection and, if supported, once with manual protection.

State and persistence behavior: Global `iteration`, `host_quit`, and per-vCPU completion counters coordinate threads. Dirty bitmaps are host memory. KVM page stats and memslot dirty logging state are transient VM state. No disk persistence exists.

Dependencies and integration points: Requires `eager_page_split` and `tdp_mmu` KVM parameters, HugeTLB or best-effort THP backing, memstress helpers, guest mode enumeration, and KVM dirty-log ioctls/statistics.

Risks and maintenance notes: The test is strongest with HugeTLB; THP can be nondeterministic. Busy-wait coordination assumes worker vCPUs progress. Page-stat expectations are tightly coupled to TDP MMU hugepage accounting and manual dirty-log semantics.

Test signals: Passing means hugepages are initially populated, split at dirty-log enablement or first manual clear as appropriate, and restored after dirty logging is disabled and memory is touched again. Failures indicate eager-splitting, dirty-log clear, or hugepage repopulation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/dirty_log_page_splitting_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/evmcs_smm_controls_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/evmcs_smm_controls_test.c

Purpose: Tests that VMX SMM exit/resume handling validates eVMCS/VMCS12 controls before re-entering nested guest mode on `RSM`. It is a targeted regression test for invalid nested controls during `vmx_leave_smm()`.

Important APIs/types/functions: The real-mode `smi_handler[]` reports `SMRAM_STAGE` then executes `RSM`; `sync_with_host()` does port I/O on `SYNC_PORT`; `l2_guest_code()` and `guest_code()` set up Hyper-V enlightenments, eVMCS, and nested VMX. Host setup uses `smm.h`, `hyperv.h`, `vmx.h`, SMRAM mapping, `vcpu_enable_evmcs()`, and Hyper-V test pages.

Control flow: The guest enables Hyper-V guest OS ID, VP assist, eVMCS, VMX operation, loads eVMCS, and launches L2. L2 syncs to host, then host injects an SMI path through the installed SMRAM handler. The test expects invalid controls to prevent successful return to L2; reaching the post-RSM `vmcall` path is a failure signal.

State and persistence behavior: Important state lives in SMRAM, eVMCS fields, Hyper-V VP assist pages, and nested VMX state. The test persists only within a single VM execution.

Dependencies and integration points: Requires VMX, Hyper-V enlightened VMCS support, SMM selftest helpers, and correct KVM interaction between SMM, eVMCS, and nested VM-entry validation.

Risks and maintenance notes: This is highly architecture- and KVM-internals-sensitive. eVMCS field layout, SMM handler staging, or nested control validation changes can require careful updates. The real-mode handler is raw opcodes, so edits are easy to break.

Test signals: Passing shows KVM refuses to re-enter nested guest mode from SMM with invalid eVMCS controls and exits in the expected host-observable way. Failure implies an SMM/nested VMX validation regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/evmcs_smm_controls_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/exit_on_emulation_failure_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/exit_on_emulation_failure_test.c

Purpose: Verifies that an unsupported emulated instruction exits to userspace with `KVM_EXIT_INTERNAL_ERROR` and an emulation-failure payload when `KVM_CAP_EXIT_ON_EMULATION_FAILURE` behavior is exercised.

Important APIs/types/functions: `guest_code()` executes `flds()` against an MMIO address; `main()` creates an MMIO-backed hole and uses `handle_flds_emulation_failure_exit()` from `flds_emulation.h` to validate the exit. The file depends directly on the shared `flds` failure helper.

Control flow: The guest attempts `flds [eax]` using an address that forces KVM instruction emulation. Since the emulator is known not to support this instruction, the vCPU exits to userspace. The host checks internal-error subtype, instruction bytes, instruction size, advances RIP, and can continue or finish the test.

State and persistence behavior: No durable state. The only mutation is host-side RIP advancement after the expected emulation failure.

Dependencies and integration points: Depends on KVM instruction emulator failure reporting, MMIO-triggered emulation, and the `flds_emulation.h` helper's exact opcode expectations.

Risks and maintenance notes: If KVM learns to emulate `flds`, this test must choose a different unsupported instruction or update expectations. Payload layout and instruction-byte flags are ABI-sensitive.

Test signals: Passing means KVM exits to userspace with complete emulation-failure metadata instead of silently failing or injecting an unexpected guest exception. Failures point to emulator reporting or exit-on-failure regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/exit_on_emulation_failure_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fastops_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fastops_test.c

Purpose: Exercises KVM's x86 emulator fastop paths for common arithmetic, bit-test, shift, and divide instructions. It compares normal and forced-emulation execution for correctness of result values and EFLAGS.

Important APIs/types/functions: Macro families `guest_execute_fastop_*()`, `guest_test_fastop_*()`, `guest_execute_fastop_cl()`, and `guest_execute_fastop_div()` generate inline assembly for many operand sizes and instruction forms. `vals[]` supplies edge-case input values; `guest_test_fastops()` expands the matrix; `guest_code()` runs it; `main()` creates a one-vCPU VM.

Control flow: The guest runs a deterministic matrix of fastop instruction tests. For each instruction/input pair, it executes the operation without forced emulation and with KVM forced-emulation prefix where applicable, then asserts output registers and flags are identical or architecturally expected.

State and persistence behavior: All state is guest register/flag state within a single vCPU run. No host persistence exists.

Dependencies and integration points: Depends on the KVM instruction emulator, selftest forced-emulation prefix support, compiler inline assembly constraints, and x86 arithmetic flag semantics.

Risks and maintenance notes: Inline assembly constraints are fragile and instruction encodings are hand-driven by macros. Compiler changes may expose constraint issues. Divide tests must handle faulting/overflow cases carefully.

Test signals: Passing means emulator fastop shortcuts match hardware behavior for the tested instruction matrix, including EFLAGS. Failures identify arithmetic, shift, bit-test, divide, or forced-emulation discrepancies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fastops_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/feature_msrs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/feature_msrs_test.c

Purpose: Validates KVM's feature MSR index list and access semantics. It checks that KVM-controlled feature MSRs are visible through the expected APIs, hidden VMX MSRs stay hidden when appropriate, and unsupported or quirked MSRs behave consistently.

Important APIs/types/functions: `is_kvm_controlled_msr()`, `is_hidden_vmx_msr()`, `is_quirked_msr()`, and `test_feature_msr()` classify and test each MSR. The program uses `KVM_GET_MSR_FEATURE_INDEX_LIST`, `KVM_GET_MSRS`, `KVM_SET_MSRS`, and x86 feature MSR constants.

Control flow: `main()` obtains KVM's feature MSR list and iterates every entry. For each MSR, host-side ioctls validate read behavior, classification exceptions, and write rejection/acceptance as appropriate.

State and persistence behavior: Feature MSRs are host/KVM capability state, not per-VM durable state. The test creates temporary structures for ioctl lists and results only.

Dependencies and integration points: Integrates with KVM's global MSR feature enumeration ABI and x86 VMX/feature MSR filtering logic.

Risks and maintenance notes: New feature MSRs, hidden MSR rules, or compatibility quirks require updating the classifier helpers. The test is intentionally ABI-facing and should not encode transient implementation details except documented quirks.

Test signals: Passing means feature MSR enumeration and access behavior match KVM's public ABI. Failures indicate stale MSR lists, incorrect hidden MSR exposure, or broken feature MSR ioctl handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/feature_msrs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fix_hypercall_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fix_hypercall_test.c

Purpose: Tests `KVM_X86_QUIRK_FIX_HYPERCALL_INSN`, which patches a guest hypercall instruction from the wrong vendor opcode to the native opcode. It verifies both enabled and disabled quirk behavior.

Important APIs/types/functions: `guest_ud_handler()` catches invalid-opcode fallback, opcode arrays `vmx_vmcall[]` and `svm_vmmcall[]` model vendor hypercalls, `do_sched_yield()` calls a mutable `hypercall_insn` blob, `guest_main()` validates the patched bytes and return value, and `test_fix_hypercall()` toggles `KVM_CAP_DISABLE_QUIRKS2`. It uses `KVM_ONE_VCPU_TEST` harness macros.

Control flow: The guest writes the non-native hypercall opcode into its instruction blob and executes `KVM_HC_SCHED_YIELD`. With the quirk enabled, KVM patches the instruction and the hypercall succeeds. With the quirk disabled, the guest gets `#UD`, the handler returns `-EFAULT`, and the bytes remain unmodified.

State and persistence behavior: The test mutates executable guest memory at `hypercall_insn` and syncs the global `quirk_disabled` flag into the guest. APIC mapping is added for APIC ID lookup. No data persists beyond the VM.

Dependencies and integration points: Depends on KVM paravirtual hypercalls, disable-quirks capability, APIC ID access, exception handling, and the selftest harness.

Risks and maintenance notes: The instruction size is hardcoded to three bytes and must match both `VMCALL` and `VMMCALL`. Host vendor detection controls expected native opcode. Quirk ABI must remain stable for older VMM compatibility.

Test signals: Passing proves KVM patches wrong-vendor hypercalls only when the quirk is enabled and cleanly lets `#UD` occur when disabled. Failures identify paravirt hypercall patching or quirk gating regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fix_hypercall_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/flds_emulation.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/flds_emulation.h

Purpose: Provides a shared helper for tests that intentionally force KVM emulation failure on the unsupported `flds [eax]` instruction and then validate userspace-visible failure metadata.

Important APIs/types/functions: `FLDS_MEM_EAX` defines the raw opcode bytes `0xd9 0x00`; `flds(u64 address)` emits the instruction with the target address in EAX; `handle_flds_emulation_failure_exit()` validates `KVM_EXIT_INTERNAL_ERROR`, `KVM_INTERNAL_ERROR_EMULATION`, instruction-byte flags, opcode bytes, and advances guest RIP by two bytes.

Control flow: A test calls `flds()` on an address that forces KVM emulation, then invokes `handle_flds_emulation_failure_exit()` after `KVM_RUN` exits. The helper checks the emulation failure payload and rewrites RIP to resume after the failed instruction.

State and persistence behavior: The helper only mutates the vCPU RIP via `KVM_GET_REGS`/`KVM_SET_REGS`. It has no standalone state or persistence.

Dependencies and integration points: Integrates with `struct kvm_run.emulation_failure`, KVM internal-error ABI, and tests such as `exit_on_emulation_failure_test.c`.

Risks and maintenance notes: It assumes `flds [eax]` remains unsupported by the KVM emulator. If support is added, tests using this helper will no longer get the expected failure. Opcode-size assumptions must remain aligned with the emitted instruction.

Test signals: In downstream tests, successful helper validation means KVM reported exact failing instruction bytes and userspace can recover by advancing RIP. Failure indicates missing or malformed emulation-failure metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/flds_emulation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hwcr_msr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hwcr_msr_test.c

Purpose: Tests KVM emulation/filtering of AMD `MSR_K7_HWCR` bits. It verifies that only valid bits are stored, ignored bits are accepted but not persisted, and illegal bits are rejected.

Important APIs/types/functions: `test_hwcr_bit()` defines ignored bits 3/6/8, valid bits 18/24, and the derived legal mask. It uses `_vcpu_set_msr()`, `vcpu_get_msr()`, and `vcpu_set_msr()` against `MSR_K7_HWCR`. `main()` iterates every bit in `BITS_PER_LONG`.

Control flow: For each bit, the host writes a single-bit value through KVM_SET_MSRS, asserts success for legal bits and failure for illegal bits, reads back HWCR, checks only valid bits persist, and resets HWCR to zero.

State and persistence behavior: HWCR state is vCPU MSR state and is reset after each bit case. No external persistence exists.

Dependencies and integration points: Depends on KVM's AMD HWCR MSR emulation and host-side MSR ioctl return semantics.

Risks and maintenance notes: If KVM adds support for additional HWCR bits, the valid/ignored masks must be updated. The test is intentionally bit-exhaustive, so it catches both overly permissive and overly strict changes.

Test signals: Passing means HWCR write filtering and readback semantics match KVM's intended ABI. Failures identify invalid MSR acceptance, legal MSR rejection, or incorrect bit persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hwcr_msr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_clock.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_clock.c

Purpose: Tests Hyper-V clocksource emulation, including time reference count MSR, TSC frequency MSR, and the Hyper-V TSC reference page. It verifies that guest-observed Hyper-V time advances consistently with `RDTSC`.

Important APIs/types/functions: `struct ms_hyperv_tsc_page` mirrors the TSC reference page layout; `mul_u64_u64_shr64()` computes scaled TSC values; `check_tsc_msr_rdtsc()` compares `HV_X64_MSR_TIME_REF_COUNT` against TSC; `get_tscpage_ts()` and `check_tsc_msr_tsc_page()` validate the reference page; `guest_main()` and `host_check_tsc_msr_rdtsc()` coordinate guest and host checks.

Control flow: The host enables Hyper-V CPUID/MSRs, allocates a TSC page, and runs guest checks. The guest sets Hyper-V guest OS ID and hypercall/time configuration, reads TSC frequency and time reference values around a delay, and checks the TSC page sequence/scale/offset data. Host-side checks also validate MSR monotonicity where relevant.

State and persistence behavior: State includes Hyper-V synthetic MSRs and the shared TSC reference page. The TSC page fields are KVM-maintained guest memory and valid only while the VM is alive.

Dependencies and integration points: Depends on KVM Hyper-V CPUID support, `hyperv.h` helpers, synthetic MSR emulation, stable TSC frequency reporting, and guest memory mapping for the TSC page.

Risks and maintenance notes: Timing tolerance is necessary because host scheduling and VM exits add noise. The scale calculation duplicates Hyper-V reference-page math, so layout or semantics changes need careful updates.

Test signals: Passing means Hyper-V time reference count, frequency, and TSC page all produce coherent advancing time. Failures identify Hyper-V clock MSR or reference-page regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_cpuid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_cpuid.c

Purpose: Validates `KVM_GET_SUPPORTED_HV_CPUID` behavior and the Hyper-V CPUID leaves exposed to a vCPU, including eVMCS-related feature expectations and buffer sizing errors.

Important APIs/types/functions: `guest_code()` is a minimal guest body; `test_hv_cpuid()` fetches and inspects Hyper-V CPUID entries; `test_hv_cpuid_e2big()` verifies the `E2BIG` path for undersized structures. It uses `vcpu_set_hv_cpuid()`, `kvm_get_supported_hv_cpuid()`, VMX/eVMCS feature checks, and KVM CPUID ioctls.

Control flow: The host creates a VM/vCPU, queries supported Hyper-V CPUID, optionally enables eVMCS-related support, and validates advertised leaves and feature bits. It also intentionally supplies a too-small CPUID buffer to ensure KVM reports the required size.

State and persistence behavior: CPUID state is vCPU-local and configuration-only. No external state is persisted.

Dependencies and integration points: Depends on `KVM_CAP_HYPERV_CPUID`, Hyper-V CPUID leaf definitions, and VMX/eVMCS capability reporting. It is an ABI check for VMMs that query Hyper-V features.

Risks and maintenance notes: Hyper-V feature expansion requires updating expected leaves and eVMCS bit logic. The `E2BIG` path is sensitive to structure sizing and kernel ioctl conventions.

Test signals: Passing means Hyper-V CPUID enumeration is complete, correctly sized, and consistent with eVMCS availability. Failures point to CPUID ABI or feature advertisement regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_cpuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_evmcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_evmcs.c

Purpose: Provides broad regression coverage for Hyper-V enlightened VMCS, including nested state save/restore, eVMCS pointer behavior, invalid revision handling, NMI exits, enlightened MSR bitmap behavior, direct nested TLB flush hypercalls, synthetic exits, and invalid enlightened `vmptrld`.

Important APIs/types/functions: `guest_ud_handler()` counts invalid-opcode traps for bad eVMCS use; `guest_nmi_handler()` consumes injected NMI; `l2_guest_code()` issues syncs, `VMCALL`, `RDMSR`, and Hyper-V flush hypercalls; `guest_code()` sets up VMX/eVMCS and performs nested checks; `inject_nmi()` manipulates `KVM_SET_VCPU_EVENTS`; `save_restore_vm()` exercises `KVM_GET/SET_NESTED_STATE` via full vCPU save/load. It uses Hyper-V VP assist, partition assist, direct hypercall controls, and VMX MSR bitmaps.

Control flow: The guest enables Hyper-V guest OS ID/hypercall page, x2APIC, VP assist, and eVMCS, then launches L2. The host runs through numbered sync stages and after each stage saves VM/vCPU state, recreates the VM, reloads state, and verifies registers match. At stage 8 it injects NMI before L2 resumes; at stage 9 it performs an extra nested-state save/restore. L1 then tests invalid eVMCS revision, NMI exit reason, MSR bitmap clean-field behavior, direct nested flush handling, synthetic trap-after-flush exit, and invalid eVMCS pointer behavior.

State and persistence behavior: The test deliberately persists nested state through save/restore cycles. Critical state includes eVMCS GPA/content, VP assist page, partition assist page, Hyper-V synthetic MSRs, NMI pending state, MSR bitmaps, and L2 RIP. State must survive `kvm_vm_release()` and recreation.

Dependencies and integration points: Requires VMX, `KVM_CAP_NESTED_STATE`, `KVM_CAP_HYPERV_ENLIGHTENED_VMCS`, Hyper-V nested direct flush, selftest VMX and Hyper-V helpers, and correct `KVM_GET/SET_NESTED_STATE` serialization.

Risks and maintenance notes: This test is dense and sensitive to eVMCS clean-field semantics. Guest code notes that L1 does not preserve all GPRs during vmexits, so inline assembly clobbers broadly. The stage protocol must remain in lockstep with host save/restore expectations.

Test signals: Passing demonstrates eVMCS nested execution remains correct across state migration, NMI delivery, MSR bitmap updates, and nested flush hypercalls. Failures are high-signal for eVMCS state serialization or Hyper-V nested enlightenment regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_evmcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_extended_hypercalls.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_extended_hypercalls.c

Purpose: Tests userspace handling of Hyper-V extended hypercall `HV_EXT_CALL_QUERY_CAPABILITIES`. It verifies that KVM exits to userspace and that a userspace-supplied result is visible to the guest.

Important APIs/types/functions: `EXT_CAPABILITIES` is the expected output token; `guest_code()` enables Hyper-V, executes the extended hypercall, and checks the output page; `main()` allocates input/output pages and handles the KVM Hyper-V exit. It uses `KVM_CAP_HYPERV_CPUID`, `HV_ENABLE_EXTENDED_HYPERCALLS`, `KVM_EXIT_HYPERV`, and `hyperv_hypercall()`.

Control flow: The host skips if extended hypercalls are unsupported. The guest sets guest OS ID and hypercall MSR, then invokes `HV_EXT_CALL_QUERY_CAPABILITIES`. KVM exits to userspace; the host validates call metadata, writes `EXT_CAPABILITIES` into the output page, resumes the vCPU, and the guest asserts the value.

State and persistence behavior: Hypercall input/output pages are guest memory. Output content is written by userspace and read by the guest in the same VM lifetime.

Dependencies and integration points: Integrates with KVM Hyper-V hypercall exit ABI and the guest/host shared-memory contract for extended hypercalls.

Risks and maintenance notes: Only the positive path is covered here; negative cases are in `hyperv_features.c`. Hypercall exit structure changes or TLFS output-size changes would require updates.

Test signals: Passing means KVM exposes extended hypercalls to userspace and the guest receives userspace-completed results. Failures indicate Hyper-V hypercall exit ABI or page-translation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_extended_hypercalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_features.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_features.c

Purpose: Exhaustively tests Hyper-V feature gating for synthetic MSRs and hypercalls. It checks that accesses succeed only when the relevant Hyper-V CPUID feature is exposed and fail with the expected guest exception or hypercall status when absent.

Important APIs/types/functions: `struct msr_data` and `struct hcall_data` describe target MSRs/hypercalls and expected access properties; `is_write_only_msr()`, `guest_msr()`, `guest_hcall()`, `vcpu_reset_hv_cpuid()`, `guest_test_msrs_access()`, and `guest_test_hcalls_access()` implement the matrix. The file uses many Hyper-V constants, `HV_X64_MSR_*`, `HVCALL_*`, VP assist/hypercall pages, and CPUID feature toggling.

Control flow: The host creates vCPUs with selected Hyper-V CPUID feature sets and syncs test descriptors into guest memory. Guest code attempts reads/writes of Hyper-V MSRs or hypercalls, records fault vectors/statuses, and asserts access matches the exposed feature bits. The host resets Hyper-V CPUID between cases to isolate features.

State and persistence behavior: Synthetic MSR state, hypercall page state, and guest CPUID state are vCPU-local. Test data is shared through guest memory. No external persistence exists.

Dependencies and integration points: Depends on KVM Hyper-V CPUID/MSR/hypercall emulation, exception injection, and the selftest Hyper-V helper layer. It overlaps with but is broader than positive functional tests such as `hyperv_extended_hypercalls.c`.

Risks and maintenance notes: The feature matrix must track TLFS and KVM feature definitions closely. Write-only MSR exceptions and unsupported hypercall statuses are easy to regress. Adding a Hyper-V feature should be reflected here to avoid silent coverage gaps.

Test signals: Passing means KVM enforces Hyper-V feature dependencies for MSRs and hypercalls, including negative paths. Failures point to overexposed features, missing access checks, or incorrect fault/status reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_ipi.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_ipi.c

Purpose: Tests Hyper-V synthetic cluster IPI hypercalls, including `HvCallSendSyntheticClusterIpi` and `HvCallSendSyntheticClusterIpiEx` in slow, fast, and XMM-fast forms.

Important APIs/types/functions: `struct hv_vpset`, `struct hv_send_ipi`, and `struct hv_send_ipi_ex` model hypercall inputs; `ipis_rcvd[]` records per-VP interrupt counts; `receiver_code()` halts receiver vCPUs; `guest_ipi_handler()` increments counters and writes Hyper-V EOI; `sender_guest_code()` runs the hypercall matrix; pthread helpers run and cancel receiver vCPUs.

Control flow: The host creates one sender vCPU and two receiver vCPUs with sparse VP IDs 2 and 65 to cover multiple VP-set banks. Receiver threads enable x2APIC/Hyper-V and wait in `safe_halt()`. Sender waits for readiness, then sends IPIs to each receiver and both receivers using simple masks, sparse VP sets, and `HV_GENERIC_SET_ALL`, validating counts after each stage.

State and persistence behavior: `ipis_rcvd[]` is volatile guest global state shared by vCPUs. Hypercall input pages are reused and cleared between calls. Receiver threads run until host cancellation.

Dependencies and integration points: Requires `KVM_CAP_HYPERV_SEND_IPI`, Hyper-V CPUID setup, x2APIC, synthetic interrupt delivery, Hyper-V EOI MSR handling, XMM fast input helpers, and pthread scheduling.

Risks and maintenance notes: Busy-wait readiness and nop delays can be sensitive to scheduling. Sparse VP IDs intentionally test bank indexing; changing IDs without updating masks would weaken coverage.

Test signals: Passing means KVM routes Hyper-V synthetic IPIs to the requested vCPUs for all tested input formats and leaves untargeted vCPUs unchanged. Failures implicate VP-set parsing, fast hypercall input handling, or interrupt delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_ipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_svm_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_svm_test.c

Purpose: Tests Hyper-V enlightenments for nested SVM, including enlightened MSR bitmap behavior and nested direct TLB flush hypercalls on AMD virtualization.

Important APIs/types/functions: `rdmsr_from_l2()` forces L2 exits through `RDMSR`; `l2_guest_code()` performs `VMMCALL`, MSR reads, and Hyper-V flush calls; `guest_code()` sets up SVM VMCB and Hyper-V test pages. It uses `generic_svm_setup()`, Hyper-V VP assist/partition assist pages, clean-field controls, and direct hypercall feature bits.

Control flow: The guest enables Hyper-V synthetic MSRs, initializes nested SVM, launches L2, and validates expected L2 exits. It toggles intercept bits and clean-field notifications to ensure KVM observes or ignores MSR bitmap changes correctly. It then tests direct handling versus synthetic exit behavior for Hyper-V nested TLB flush.

State and persistence behavior: State lives in the SVM VMCB, MSR permission map, Hyper-V assist pages, and partition assist page. No state is persisted beyond one VM run.

Dependencies and integration points: Requires SVM, Hyper-V nested enlightenment support, selftest SVM utilities, and KVM's AMD nested virtualization implementation.

Risks and maintenance notes: Like the eVMCS test, this is sensitive to clean-field semantics and assumes broad GPR clobbering around L2 exits. AMD-specific exit codes and VMCB fields must remain aligned with KVM headers.

Test signals: Passing means nested SVM honors Hyper-V MSR-bitmap and direct-flush enlightenments. Failures indicate AMD nested Hyper-V enlightenment regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_svm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_tlb_flush.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_tlb_flush.c

Purpose: Tests Hyper-V TLB flush hypercalls across slow and fast forms: `HvFlushVirtualAddressSpace`, `HvFlushVirtualAddressList`, and their `Ex` variants. It verifies that targeted vCPUs observe updated page mappings only after the correct flush.

Important APIs/types/functions: `struct hv_tlb_flush`, `struct hv_tlb_flush_ex`, `struct hv_vpset`, and `struct test_data` model hypercall inputs and shared test pages. `worker_guest_code()` continuously checks mapped page contents; `prepare_to_test()` disables checks and swaps guest PTEs; `post_test()` sets per-vCPU expected values; `sender_guest_code()` runs a large flush matrix; pthread helpers manage worker vCPUs.

Control flow: The host maps test pages and guest-visible PTEs, creates one sender and two worker vCPUs with VP IDs 2 and 65, then runs workers in threads. For each case, sender swaps two PTEs, issues a Hyper-V flush targeting one worker, both workers, or all processors, and then publishes expected values. Workers assert their TLB view matches whether they were flushed. The matrix covers address-space/list calls, Ex VP sets, all processors, slow memory inputs, and fast XMM inputs.

State and persistence behavior: Shared guest memory stores hypercall pages, test pages, PTE pointers, and per-vCPU expected values. Worker vCPU state persists in running threads until host cancellation.

Dependencies and integration points: Requires `KVM_CAP_HYPERV_TLBFLUSH`, guest page-table manipulation helpers, Hyper-V CPUID, x86 memory barriers, XMM input helper support, and multi-vCPU scheduling.

Risks and maintenance notes: The test uses delay loops rather than precise synchronization, so very slow systems can affect timing. It intentionally maps PTE pages into the guest, which is powerful but fragile if selftest page-table helpers change. Banked VP set indexing is a key coverage point.

Test signals: Passing means KVM parses all tested Hyper-V TLB flush formats and invalidates remote vCPU TLBs with correct targeting. Failures indicate TLB shootdown, VP-set parsing, fast input, or page-table synchronization bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/hyperv_tlb_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_buslock_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_buslock_test.c

Purpose: Tests `KVM_CAP_X86_BUS_LOCK_EXIT` by deliberately generating split-cacheline atomic operations in L1 and optional L2 and verifying KVM exits to userspace on each bus lock.

Important APIs/types/functions: A cacheline-aligned `buffer` and misaligned `atomic_t *val` create bus locks; `guest_generate_buslocks()` performs `NR_BUS_LOCKS_PER_LEVEL` atomic increments; `l1_svm_code()`, `l1_vmx_code()`, and `l2_guest_code()` extend coverage to nested guests; `main()` enables `KVM_BUS_LOCK_DETECTION_EXIT`.

Control flow: The host enables bus-lock exits before adding the vCPU, allocates nested data if SVM or VMX is available, and runs until `UCALL_DONE`. Non-ucall exits must be `KVM_EXIT_X86_BUS_LOCK`. For each bus-lock exit, the host syncs `val` from guest memory and verifies the counter has advanced according to Intel trap-like or AMD fault-like semantics.

State and persistence behavior: `val` is guest global memory shared back to the host for verification. Nested control pages persist for the VM lifetime only.

Dependencies and integration points: Depends on KVM bus-lock detection, host CPU vendor semantics, Linux atomic helpers, and nested VMX/SVM setup.

Risks and maintenance notes: Bus-lock exit timing differs by vendor, and the test explicitly accounts for that. Hardware or kernel changes in bus-lock detection policy can alter expected exit counts.

Test signals: Passing means KVM exits for every generated bus lock in L1 and L2 without skipping or double-executing the instruction. Failures indicate detection, nested propagation, or vendor semantic regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_buslock_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_clock_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_clock_test.c

Purpose: Tests userspace adjustment of KVM clock state via `KVM_SET_CLOCK` and guest observation through the paravirtual KVM clock MSR.

Important APIs/types/functions: `struct test_case` defines base clock and realtime offset cases; `guest_main()` enables `MSR_KVM_SYSTEM_TIME_NEW` and reports pvclock cycles; `setup_clock()` writes `struct kvm_clock_data`; `handle_sync()` compares guest-observed values with host `KVM_GET_CLOCK` ranges; `enter_guest()` runs all cases.

Control flow: For each test case, the host sets KVM clock data, captures start clock, runs the guest until a sync, captures end clock, and asserts the guest pvclock value lies between start and end. Cases include zero base, positive base offset, and positive/negative realtime offsets.

State and persistence behavior: KVM clock data is VM-wide state. Guest pvclock structure is shared guest memory enabled through the KVM system-time MSR.

Dependencies and integration points: Uses KVM clock ioctls, pvclock ABI structures, realtime clock reads, and KVM paravirtual MSRs.

Risks and maintenance notes: Clock comparisons depend on monotonic ordering around `KVM_RUN`; excessive scheduling delays widen but should not invalidate the range. Flag expectations require `KVM_CLOCK_REALTIME` and `KVM_CLOCK_HOST_TSC`.

Test signals: Passing means userspace-set KVM clock state is reflected to the guest pvclock page and `KVM_GET_CLOCK` flags are correct. Failures implicate clock offset, realtime, or pvclock update regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_clock_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_pv_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_pv_test.c

Purpose: Tests KVM paravirtual MSR and hypercall behavior, including feature disablement and PV unhalt behavior.

Important APIs/types/functions: `struct msr_data` and `struct hcall_data` define KVM PV MSRs and hypercalls; `test_msr()` and `test_hcall()` run guest-side access attempts; `guest_main()` executes the matrix; `enter_guest()` handles ucalls; `test_pv_unhalt()` tests paravirtual halt/wakeup behavior. It uses KVM paravirt constants such as `KVM_FEATURE_PV_UNHALT`, `KVM_HC_KICK_CPU`, and `KVM_HC_SCHED_YIELD`.

Control flow: The guest iterates supported PV MSRs and hypercalls, reporting progress through special ucalls. The host validates guest assertions and logs names. The PV unhalt section creates vCPU conditions that should be woken by KVM's PV halt mechanism.

State and persistence behavior: PV MSR values and feature exposure are vCPU state. Hypercall effects are transient. No external persistence exists.

Dependencies and integration points: Depends on KVM paravirtual CPUID leaves, KVM-specific MSRs, hypercall instruction handling, and APIC/vCPU wakeup paths.

Risks and maintenance notes: PV feature behavior is ABI-sensitive for Linux guests. The test matrix must evolve with new KVM PV MSRs/hypercalls. Wakeup timing can be scheduler-sensitive.

Test signals: Passing means PV MSRs/hypercalls are accessible and fault as expected under the exposed feature set, and PV unhalt wakeup behavior works. Failures point to KVM paravirt ABI regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/kvm_pv_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/max_vcpuid_cap_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/max_vcpuid_cap_test.c

Purpose: Tests the `KVM_CAP_MAX_VCPU_ID` limit by attempting to create vCPUs at and around the reported maximum vCPU ID.

Important APIs/types/functions: `MAX_VCPU_ID` is a small requested ID used in the test; `main()` queries KVM caps and creates a VM/vCPUs. It uses `kvm_check_cap(KVM_CAP_MAX_VCPU_ID)` and vCPU creation helpers.

Control flow: The host checks the maximum supported vCPU ID and verifies KVM accepts legal IDs and rejects IDs beyond the cap. The test is host-only and does not need guest execution.

State and persistence behavior: Only VM/vCPU file descriptors are created. No guest or external persistence exists.

Dependencies and integration points: Depends on KVM vCPU creation ioctl semantics and capability reporting.

Risks and maintenance notes: This is a narrow ABI test. If KVM changes whether the cap is inclusive or exclusive, the expected boundary must remain aligned with documentation.

Test signals: Passing means max-vCPU-ID capability reporting and enforcement agree. Failures indicate vCPU ID bound-checking or cap-reporting bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/max_vcpuid_cap_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/monitor_mwait_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/monitor_mwait_test.c

Purpose: Tests KVM handling of `MONITOR` and `MWAIT` under different CPUID and emulation configurations, ensuring the instructions either execute or fault as expected.

Important APIs/types/functions: `CPUID_MWAIT` names the CPUID feature bit; `enum monitor_mwait_testcases` identifies scenarios; `GUEST_ASSERT_MONITOR_MWAIT()` emits an instruction and validates the fault vector; `guest_monitor_wait()` runs the guest cases. Host setup toggles CPUID exposure and KVM capability/quirk behavior.

Control flow: The host creates a vCPU with selected MONITOR/MWAIT exposure, runs the guest, and the guest executes monitor/mwait instruction sequences for each testcase. Expected vectors are compared to actual exception results.

State and persistence behavior: CPUID feature exposure is vCPU state. No persistent data is used.

Dependencies and integration points: Depends on x86 instruction emulation, CPUID filtering, KVM monitor/mwait capability behavior, and exception reporting.

Risks and maintenance notes: Hardware support, KVM policy, and userspace CPUID choices all affect expected results. The test must track KVM's intended virtualization policy for these power-management instructions.

Test signals: Passing means KVM consistently allows or rejects MONITOR/MWAIT according to CPUID/capability state. Failures indicate instruction-emulation or CPUID gating regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/monitor_mwait_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/msrs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/msrs_test.c

Purpose: Provides broad MSR ABI coverage for common x86 MSRs, including supported/unsupported access, reserved-value rejection, reset values, host ioctl visibility, save/restore list consistency, and optional `KVM_{GET,SET}_ONE_REG` paths.

Important APIs/types/functions: `struct kvm_msr` describes feature dependency, reset/write/reserved values, MSR index, and whether it is KVM-defined. Macros such as `MSR_TEST`, `MSR_TEST_CANONICAL`, and `MSR_TEST_KVM` build the matrix. Guest helpers `__rdmsr()`, `__wrmsr()`, `guest_test_supported_msr()`, `guest_test_unsupported_msr()`, and `guest_test_reserved_val()` validate in-guest behavior. Host helpers `host_test_kvm_reg()`, `host_test_msr()`, `do_vcpu_run()`, and `test_msrs()` validate ioctl behavior.

Control flow: The host creates three vCPUs: two with normal features and one with selected CPUID features cleared. For every MSR descriptor, it checks save/restore list consistency, syncs the index to the guest, and runs all vCPUs twice to validate state reset and context switching. If `KVM_CAP_ONE_REG` exists, the entire matrix is repeated using one-reg access where possible.

State and persistence behavior: MSR values are per-vCPU architectural state. The test intentionally runs multiple vCPUs on one host thread without CPU pinning to exercise KVM context switching across host CPUs. Global `idx` and descriptor arrays are shared with the guest.

Dependencies and integration points: Depends on x86 MSR definitions, CPUID feature filtering, KVM MSR ioctls, `KVM_GET_MSR_INDEX_LIST`, `KVM_CAP_ONE_REG`, and KVM's `ignore_msrs` behavior.

Risks and maintenance notes: MSR behavior is highly feature-dependent. AMD truncation of some SYSENTER/TSC_AUX values is handled by `fixup_rdmsr_val()`. `ignore_msrs` weakens negative checks by necessity. New MSRs or new one-reg entries require updating the matrix and maximum reg-list assumptions.

Test signals: Passing means KVM guest MSR access, host MSR ioctls, reset behavior, reserved-bit checks, unsupported-feature faults, and one-reg access are consistent. Failures point to MSR emulation, CPUID gating, save/restore, or context-switch bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/msrs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_close_kvm_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_close_kvm_test.c

Purpose: Verifies that closing a KVM VM/process while a nested guest is active and has open file descriptors does not crash or corrupt kernel state.

Important APIs/types/functions: `l2_guest_code()` exits to L0 through port I/O; `l1_vmx_code()` and `l1_svm_code()` launch L2; `l1_guest_code()` selects VMX or SVM; `main()` drives the vCPU until the L0 exit point. It uses nested VMX/SVM setup and `PORT_L0_EXIT`.

Control flow: L1 launches L2. L2 performs port I/O intended to exit all the way to userspace/L0. The host observes the exit and then allows process teardown with nested state still present.

State and persistence behavior: Nested VMCS/VMCB state exists at process close time. The test's value is in cleanup behavior, not persisted data.

Dependencies and integration points: Requires VMX or SVM nested virtualization and KVM cleanup paths for active nested guests.

Risks and maintenance notes: The test is intentionally small and may not catch all teardown races, but it is a focused regression for file-descriptor/VM destruction cleanup. Exit path must continue to reach L0 as expected.

Test signals: Passing means KVM handles VM destruction with active nested state without kernel errors. Failures can be crashes, unexpected exits, or nested teardown assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_close_kvm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_dirty_log_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_dirty_log_test.c

Purpose: Tests dirty logging of nested guest memory accesses, including read faults, write faults, alias mappings, and behavior with nested TDP enabled or disabled.

Important APIs/types/functions: Defines test memslot constants, alias GPA range, `TEST_SYNC_*` stage bits, `l2_guest_code_tdp_enabled()`, `l2_guest_code_tdp_disabled()`, `l1_vmx_code()`, `l1_svm_code()`, `test_handle_ucall_sync()`, and `test_dirty_log()`. It uses dirty log bitmaps, `KVM_MEM_LOG_DIRTY_PAGES`, nested VMX/SVM helpers, and bit operations.

Control flow: The host sets up a test memory slot and alias mapping, enables dirty logging, then runs L1/L2. L2 performs reads and writes that should or should not fault depending on nested TDP mode. On each guest sync, the host checks dirty bitmaps and host memory contents, clears logs as needed, and validates that alias writes dirty the canonical page.

State and persistence behavior: Dirty bitmap state is maintained by KVM per memslot. Test pages persist in VM memory and are inspected through host virtual addresses. Nested page-table state differs by TDP mode.

Dependencies and integration points: Requires nested VMX or SVM, KVM dirty logging, guest memory aliasing, and optional nested TDP controls.

Risks and maintenance notes: Dirty logging semantics differ depending on nested TDP. The stage protocol is tight, and bitmap index calculations must match page layout exactly. Alias mapping makes false positives possible if page accounting changes.

Test signals: Passing means nested guest reads/writes trigger dirty logging and faults exactly as expected across TDP modes. Failures indicate nested MMU dirty-bit propagation or alias handling bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_dirty_log_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_emulation_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_emulation_test.c

Purpose: Tests KVM instruction emulation for selected instructions executed by L2 under nested virtualization, including use of the forced-emulation prefix.

Important APIs/types/functions: `struct emulated_instruction` describes instruction bytes and expected length; `instructions[]` is the test matrix; `kvm_fep[]` is the forced-emulation prefix; `l2_guest_code[]` is dynamically populated; `get_instruction_length()` and `guest_code()` drive execution. It uses nested VMX/SVM helpers and KVM forced emulation.

Control flow: The guest/L1 copies each instruction after the forced-emulation prefix into the L2 code buffer, launches L2, and expects KVM to emulate the instruction or produce the correct nested exit. It repeats through the instruction matrix and reports completion through ucalls.

State and persistence behavior: L2 code bytes are mutable guest memory. Nested control state persists across individual instruction runs within the same VM.

Dependencies and integration points: Depends on KVM nested virtualization, emulator support for the selected instructions, and the selftest forced-emulation prefix contract.

Risks and maintenance notes: Dynamic code generation requires exact instruction lengths and writable/executable guest memory. Adding instructions requires careful expected-length and exit updates.

Test signals: Passing means selected instructions emulate correctly in nested context, including forced-emulation paths. Failures point to nested emulator, instruction-length, or exit-propagation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_emulation_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_exceptions_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_exceptions_test.c

Purpose: Tests pending versus injected exception handling for L2, especially a queued `#SS` that becomes `#GP`, `#DF`, or nested shutdown/triple fault depending on L1 intercepts.

Important APIs/types/functions: Defines expected error-code constants for AMD and Intel, intercept masks, `l2_ss_*` sync functions, `svm_run_l2()`, `vmx_run_l2()`, `l1_svm_code()`, `l1_vmx_code()`, `assert_ucall_vector()`, and `queue_ss_exception()`. It uses `KVM_CAP_EXCEPTION_PAYLOAD` and `KVM_GET/SET_VCPU_EVENTS`.

Control flow: L2 first syncs asking the host to queue `#SS`. The host tests a pending `#SS` with immediate exit, verifies event payload round trip, then runs and observes L1 intercepting `#SS`. It repeats with injected `#SS` cases where vectoring through an empty IDT causes `#GP`, then `#DF`, then final shutdown/triple fault as L1 disables intercepts.

State and persistence behavior: Pending/injected exception state is vCPU event state manipulated by userspace. Nested intercept bitmaps are L1 VMCS/VMCB state. Error payloads must survive get/set events.

Dependencies and integration points: Requires nested VMX or SVM, exception payload capability, event ioctls, and precise x86 exception-vectoring semantics.

Risks and maintenance notes: Intel and AMD differ in `#GP` error-code external-bit semantics, and the test encodes both. Injected versus pending semantics are subtle and easy to regress in nested event handling.

Test signals: Passing means KVM preserves event payloads, honors L1 intercepts, and morphs nested exceptions into `#GP`, `#DF`, and triple fault correctly. Failures identify nested exception delivery or event-ioctl bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_exceptions_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_invalid_cr3_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_invalid_cr3_test.c

Purpose: Verifies that L1 cannot enter L2 with an invalid CR3 and can successfully enter L2 after restoring a valid CR3.

Important APIs/types/functions: `l2_guest_code()` exits by `vmcall`; `l1_svm_code()` corrupts/restores `vmcb->save.cr3`; `l1_vmx_code()` corrupts/restores `GUEST_CR3`; `l1_guest_code()` selects VMX or SVM. It uses `SVM_EXIT_ERR`, `EXIT_REASON_FAILED_VMENTRY`, and `EXIT_REASON_INVALID_STATE`.

Control flow: L1 prepares nested state, saves the original CR3, writes `-1ull` as invalid CR3, tries to run L2, and asserts failed entry. It then restores CR3, launches L2 again, and asserts a normal VMCALL/VMMCALL exit.

State and persistence behavior: Only nested CR3 state is mutated and restored. No persistence beyond the VM.

Dependencies and integration points: Requires nested VMX/SVM and KVM's nested entry validation for guest CR3.

Risks and maintenance notes: Invalid CR3 validation can vary with paging mode and address-width support; using all ones is meant to be universally invalid. Expected VMX/SVM exit codes must remain architecture-correct.

Test signals: Passing means KVM rejects invalid nested CR3 at entry and does not poison subsequent valid entry. Failures indicate nested entry validation or state recovery bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_invalid_cr3_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_set_state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_set_state_test.c

Purpose: Tests integrity and validation of `KVM_SET_NESTED_STATE` for VMX and SVM. It covers valid default state, malformed sizes, bad flags, bad addresses, revision mismatches, eVMCS-specific cases, and SVM enable/disable transitions.

Important APIs/types/functions: `test_nested_state*()` wrappers assert success or errno; `set_revision_id_for_vmcs12()`, `set_default_state()`, `set_default_vmx_state()`, and `set_default_svm_state()` build test structures; `test_vmx_nested_state()` and `test_svm_nested_state()` contain the validation matrices; `vcpu_efer_enable_svm()` and `vcpu_efer_disable_svm()` manipulate SVM enablement.

Control flow: `main()` creates a VM/vCPU, detects VMX/SVM/eVMCS support, and runs the relevant nested-state tests. Each matrix mutates one field at a time from a known-good nested-state structure and verifies KVM accepts or rejects it with the expected errno.

State and persistence behavior: Nested state is userspace-provided serialized vCPU state. The test repeatedly overwrites it through ioctls and checks validation behavior; no external persistence exists.

Dependencies and integration points: Depends on `KVM_CAP_NESTED_STATE`, VMX/SVM support, eVMCS support where available, Linux `struct kvm_nested_state`, and KVM's ioctl validation paths.

Risks and maintenance notes: Structure layout, `VMCS12_REVISION`, and accepted flag combinations are tightly coupled to KVM internals exposed through UAPI. Updates to nested-state UAPI require synchronized test changes.

Test signals: Passing means KVM accepts valid nested serialized state and rejects malformed VMX/SVM state with stable errno values. Failures identify UAPI validation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_set_state_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_adjust_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_adjust_test.c

Purpose: Tests `IA32_TSC_ADJUST` behavior when L1 and L2 write `IA32_TSC`, including the unusual case where L2 writes TSC without L1 intercepting and thereby changes L1's TSC adjust accounting.

Important APIs/types/functions: Constants `TSC_ADJUST_VALUE` and `TSC_OFFSET_VALUE` define expected offsets; `check_ia32_tsc_adjust()` reads and reports adjust; `l2_guest_code()` writes TSC from L2; `l1_guest_code()` writes TSC in L1 and launches L2 through VMX or SVM with a TSC offset; `report()` logs observed values.

Control flow: L1 first writes TSC so `TSC_ADJUST` becomes negative one unit. It then launches L2 with a TSC offset. L2 computes L1-relative TSC, writes TSC again, and asserts adjust is now about negative two units. After L2 exits, L1 checks the final adjust value and reports done.

State and persistence behavior: `IA32_TSC` and `IA32_TSC_ADJUST` are vCPU MSR state. Nested TSC offset is VMCS/VMCB state. No persistent external state exists.

Dependencies and integration points: Requires nested VMX/SVM, TSC adjust MSR support, and correct interaction between nested TSC offsetting and non-intercepted MSR writes.

Risks and maintenance notes: TSC behavior can be host-sensitive, but the test compares large adjust deltas rather than exact TSC values. Intercept policy changes could alter which level's TSC is affected.

Test signals: Passing means KVM accounts TSC writes into `IA32_TSC_ADJUST` correctly across L1 and L2 with offsets. Failures implicate nested TSC offset or adjust emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_adjust_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_scaling_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_scaling_test.c

Purpose: Verifies nested TSC scaling when L1 and L2 run with different TSC ratios. L1's apparent frequency should remain stable while L2 observes a scaled frequency.

Important APIs/types/functions: `compare_tsc_freq()` checks a 1% tolerance; `check_tsc_freq()` measures TSC delta over a host-controlled one-second sleep; `l1_svm_code()` uses `MSR_AMD64_TSC_RATIO`; `l1_vmx_code()` uses `SECONDARY_EXEC_TSC_SCALING`, `TSC_OFFSET`, and `TSC_MULTIPLIER`; `l2_guest_code()` measures L2 frequency.

Control flow: Guest code measures L1 frequency, configures nested TSC scaling for L2, launches L2, has L2 measure its scaled frequency, then measures L1 again after L2 exits. Host ucalls perform sleeps and compare reported frequencies against expected L1 and L2 values.

State and persistence behavior: TSC scaling ratio/offset is nested VMCS/VMCB state. TSC measurements are transient. No external persistence exists.

Dependencies and integration points: Requires nested VMX or SVM with TSC scaling support, host sleep timing, and KVM TSC frequency reporting.

Risks and maintenance notes: Timing tests can be flaky on heavily loaded hosts despite 1% tolerance. VMX and SVM use different ratio encodings, so both paths require independent maintenance.

Test signals: Passing means nested TSC scaling applies to L2 without leaking into L1 before or after L2 execution. Failures indicate TSC multiplier, offset, or nested scaling isolation bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_tsc_scaling_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_vmsave_vmload_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_vmsave_vmload_test.c

Purpose: Tests nested SVM `VMSAVE` and `VMLOAD` handling for L2 VMCB state, including access through multiple VMCB GPAs.

Important APIs/types/functions: Memory constants define two test VMCB pages; `l2_guest_code_vmsave()`, `l2_guest_code_vmload()`, and `l2_guest_code_vmcb*()` execute the SVM instructions; `l1_guest_code()` sets up nested SVM and validates saved/loaded state. It uses SVM utilities and guest memory slots.

Control flow: The host creates a nested SVM VM with a test memory slot. L1 launches L2 payloads that perform `VMSAVE` or `VMLOAD` against selected VMCB addresses and checks that state is saved to or loaded from the expected guest physical memory.

State and persistence behavior: VMCB save areas in guest memory are the main state. The test intentionally uses two pages to ensure operations target the requested VMCB, not stale cached state.

Dependencies and integration points: Requires SVM nested virtualization and KVM support for virtualizing `VMSAVE`/`VMLOAD`.

Risks and maintenance notes: AMD-only coverage. The VMCB memory layout must match the helper structures. If KVM changes which state fields are virtualized for these instructions, assertions may need updates.

Test signals: Passing means nested `VMSAVE`/`VMLOAD` read and write the correct guest VMCB memory. Failures indicate SVM nested state serialization or GPA targeting bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nested_vmsave_vmload_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.c

Purpose: Tests NX huge page splitting and recovery behavior. It verifies that executing from hugepage-backed guest memory splits mappings when NX huge pages are enabled, that the recovery thread reclaims split mappings, and that per-VM disabling of NX huge pages requires reboot permission.

Important APIs/types/functions: Constants define a three-2MB-page slot at 4GB; `guest_code()` performs reads and calls into hugepage memory; `check_2m_page_count()` and `check_split_count()` read KVM VM stats; `wait_for_reclaim()` sleeps for recovery; `run_test()` creates the VM, maps HugeTLB memory, optionally calls `__vm_disable_nx_huge_pages()`, and validates page counts.

Control flow: The program requires a magic token from the shell wrapper. It runs once with NX huge pages enabled and once with them disabled. Guest reads create 2MB mappings; guest execution from those mappings causes split counts to rise unless disabled; later recovery should reset split counts and allow huge mappings to return.

State and persistence behavior: VM page-stat counters and KVM NX hugepage state are transient. HugeTLB backing is supplied by the wrapper. Per-VM disablement is VM-local but permission-gated by process capabilities.

Dependencies and integration points: Requires `KVM_CAP_VM_DISABLE_NX_HUGE_PAGES`, HugeTLB pages, KVM `nx_huge_pages` module parameters, VM stats, and the wrapper script for environment setup.

Risks and maintenance notes: The test is not intended to be run directly; without wrapper setup, hugepage availability and reclaim period may be wrong. Timing of recovery is based on sleeping five periods, which assumes the recovery thread runs.

Test signals: Passing means read/execute transitions produce expected 2MB mapping and split counts, reclaim clears split accounting, and disabling NX huge pages succeeds only with permissions. Failures implicate NX hugepage splitting, reclaim, stats, or permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.sh

Purpose: Provides privileged setup and cleanup for `nx_huge_pages_test`. It configures KVM NX hugepage module parameters, ensures enough 2MB HugeTLB pages, runs the binary with and without `CAP_SYS_BOOT`, and restores host settings afterward.

Important APIs/types/functions: Shell variables capture original `/sys/module/kvm/parameters/nx_huge_pages`, recovery ratio, recovery period, and HugeTLB count. `do_sudo()` abstracts root versus sudo execution; `sudo_echo()` writes sysfs values; `NXECUTABLE` points to the compiled test binary.

Control flow: The script checks sudo/root access, writes test values to KVM parameters and HugeTLB count, optionally grants `cap_sys_boot+ep` to the binary for the permission-positive case, runs the binary with magic token `887563923` and reclaim period 100 ms, removes the capability, then runs the permission-negative case when not root. A cleanup block restores all saved sysfs values and exits with the test result.

State and persistence behavior: Temporarily mutates host KVM module parameters, host HugeTLB pool size, and possibly file capabilities on the test executable. Cleanup restores original sysfs values and removes the added capability in the non-root positive path.

Dependencies and integration points: Depends on root or sudo, writable sysfs KVM parameters, HugeTLB sysfs, Linux file capabilities via `setcap`, and the compiled `nx_huge_pages_test` binary.

Risks and maintenance notes: This script modifies host-wide KVM settings; failure before cleanup could leave changed parameters, though the subshell cleanup path restores after the main run. Systems without sudo or setcap skip relevant cases. The file has a minor comment typo in the SPDX line but shell execution is unaffected.

Test signals: Passing wrapper execution means the C test ran under controlled NX hugepage/reclaim/HugeTLB settings and both permission paths were exercised where possible. Failures can reflect environment setup issues rather than KVM behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/platform_info_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/platform_info_test.c

Purpose: Tests x86 `KVM_CAP_MSR_PLATFORM_INFO` handling, specifically guest read visibility and userspace configuration of `MSR_PLATFORM_INFO`.

Important APIs/types/functions: `MSR_PLATFORM_INFO_MAX_TURBO_RATIO` identifies the tested field; `guest_code()` reads `MSR_PLATFORM_INFO` and asserts expected behavior; `main()` checks/enables the capability and writes test MSR values through KVM ioctls.

Control flow: The host verifies the capability, creates a VM/vCPU, configures platform-info MSR state, and runs the guest. The guest reads the MSR and validates that the exposed max turbo ratio/state matches what userspace configured.

State and persistence behavior: Platform-info MSR state is vCPU/VM configuration state. No data is persisted externally.

Dependencies and integration points: Depends on `KVM_CAP_MSR_PLATFORM_INFO`, MSR emulation, and x86 processor helpers.

Risks and maintenance notes: The test focuses on a specific platform-info field; future KVM support for additional fields may need expanded assertions. Feature availability is host/KVM dependent.

Test signals: Passing means userspace can configure platform-info MSR exposure and the guest observes the expected value. Failures point to capability gating or MSR emulation regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/platform_info_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_counters_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_counters_test.c

Purpose: Provides extensive Intel vPMU counter coverage. It tests architectural events, general-purpose counters, fixed counters, RDPMC behavior, event masks, PMU versions through v5, and `MSR_IA32_PERF_CAPABILITIES` fixed-counter write support.

Important APIs/types/functions: `struct kvm_intel_pmu_event` maps Intel architectural event indexes to selftest PMU features; `pmu_vm_create_with_one_vcpu()` configures PMU CPUID and perf capabilities; `guest_assert_event_count()` validates measured event counts; `GUEST_MEASURE_EVENT()` and `GUEST_TEST_EVENT()` produce tightly controlled assembly measurement windows; `guest_test_arch_event()`, `guest_test_gp_counters()`, and `guest_test_fixed_counters()` implement guest matrices; `test_intel_counters()` drives host-side PMU version/counter/mask/perf-cap permutations.

Control flow: `main()` requires PMU enabled, Intel host, and a positive PMU version. Host code records hardware-supported architectural events, then iterates PMU versions from 0 through at least 5, perf capability variants, event-mask lengths and unavailable masks, general-purpose counter counts, fixed counter counts, and fixed-counter bitmasks. Each configuration creates a VM, adjusts CPUID/MSRs, runs a guest test, and destroys the VM.

State and persistence behavior: PMU state is vCPU-local MSR and CPUID state. Guest tests write counter MSRs, event-select MSRs, fixed-control MSRs, and global control MSRs. No external state is persisted.

Dependencies and integration points: Depends on Intel PMU hardware, KVM vPMU support, `pmu.h` feature helpers, RDPMC safe wrappers, forced-emulation support for optional instruction-retirement checks, CLFLUSH/CLFLUSHOPT for LLC event stimulation, and `MSR_IA32_PERF_CAPABILITIES` when PDCM is present.

Risks and maintenance notes: Runtime can be large because the matrix is broad. Counts for instructions and branches account for known overcount errata. The test deliberately fails when hardware exposes new architectural events not represented in `NR_INTEL_ARCH_EVENTS`, forcing test updates. Timing-independent assembly minimizes compiler noise but is fragile.

Test signals: Passing means KVM's Intel vPMU exposes and virtualizes counters, event masks, RDPMC, fixed counters, global controls, and perf capabilities consistently across advertised PMU versions. Failures are strong signals for vPMU CPUID enumeration, MSR filtering, event counting, or counter access regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_counters_test.c -->
