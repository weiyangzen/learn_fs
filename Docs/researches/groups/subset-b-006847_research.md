# subset-b-006847 Research

Grouped source research for x86 KVM selftests. Each source file has a marker-delimited section so reconciliation can split the report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_event_filter_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_event_filter_test.c

## Purpose
This selftest validates the x86 `KVM_SET_PMU_EVENT_FILTER` ABI. It checks PMU event allow and deny lists, masked event matching, fixed-counter bitmap semantics, invalid ioctl inputs, and PMU disablement through `KVM_CAP_PMU_CAPABILITY`. It runs on Intel architectural PMUs and AMD Zen/Hygon PMUs and skips when the host PMU or required KVM capabilities are unavailable.

## Important APIs, Types, and Functions
The central data type is the local ABI mirror `struct __kvm_pmu_event_filter`, which is cast to `struct kvm_pmu_event_filter` for `KVM_SET_PMU_EVENT_FILTER`. Important helpers are `intel_guest_code()`, `amd_guest_code()`, `sanity_check_pmu()`, `test_with_filter()`, `run_vcpu_and_sync_pmc_results()`, `test_masked_events()`, `test_filter_ioctl()`, `test_fixed_counter_bitmap()`, and `test_pmu_config_disable()`. The code uses PMU constants from `pmu.h`, MSR helpers from `processor.h`, KVM VM/vCPU helpers from `kvm_util.h`, and PMU feature probes such as `kvm_pmu_has()` and `kvm_cpu_property()`.

## Control Flow, State, and Persistence
`main()` requires PMU filtering and masked-event support, selects Intel or AMD guest PMU code, performs a guest MSR sanity check, then runs no-filter, member/non-member allow-list, and member/non-member deny-list cases. A second vCPU is created for masked-event tests when suitable counters exist. The guest repeatedly configures two or three PMCs, executes small instruction or load/store sequences, and copies deltas through the global `pmc_results`. Later tests validate ioctl rejection paths and fixed-counter filtering over every fixed-counter bitmap combination. State is transient in KVM VM/vCPU objects, PMU MSRs, the global result struct mirrored into guest memory, and KVM capability state; nothing is persisted.

## Dependencies and Integration Points
The test integrates with KVM's PMU virtualization, PMU event-filter ioctl, masked-event encoding, fixed performance counters, host CPUID PMU enumeration, AMD K7/Zen PMU aliases, and Intel architectural/event-specific encodings. It also exercises selftests infrastructure for guest exception handlers, `GUEST_SYNC`, and VM capabilities.

## Risks and Test Signals
Risks include host model-specific event availability, PMU errata such as branch-retired overcounting, nested virtualization or disabled vPMU making PMU MSRs unusable, and ABI drift in event-filter flags or fixed-counter masks. Strong signals are zero counts for filtered events, non-zero counts for allowed events, expected ioctl failures for invalid action/flags/nevents/masked entries, and fixed-counter count/no-count behavior matching allow/deny bitmap policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/pmu_event_filter_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_conversions_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_conversions_test.c

## Purpose
This test stresses software-protected VM private-memory conversion flows backed by `guest_memfd`. It verifies explicit shared/private transitions through `KVM_HC_MAP_GPA_RANGE`, host visibility of shared memory, host invisibility of private memory, `PUNCH_HOLE` behavior, page/2 MiB range handling, multiple memslots, and multiple vCPUs.

## Important APIs, Types, and Functions
Key guest helpers are `guest_test_explicit_conversion()`, `guest_test_punch_hole()`, `guest_map_shared()`, `guest_map_private()`, `guest_sync_shared()`, and `guest_sync_private()`. Host-side control is in `handle_exit_hypercall()`, `__test_mem_conversions()`, and `test_mem_conversions()`. The test uses `KVM_X86_SW_PROTECTED_VM`, `vm_create_guest_memfd()`, `vm_mem_add(... KVM_MEM_GUEST_MEMFD ...)`, `vm_guest_mem_fallocate()`, `vm_set_memory_attributes()`, `vm_enable_cap(KVM_CAP_EXIT_HYPERCALL)`, and selftests backing-source parsing.

## Control Flow, State, and Persistence
`main()` parses optional backing source, vCPU count, and memslot count, then creates a protected VM. Each vCPU receives a private GPA window above 4 GiB. Guest code first initializes shared memory, asks the host to verify and rewrite shared bytes, converts selected ranges private, verifies private data from the guest while the host still sees shared backing, then converts holes and whole ranges back to shared. It also punches holes without full conversion and expects refaulted private memory to read as zero. Per-vCPU host threads run `KVM_RUN`, service hypercall exits, and handle `UCALL_SYNC` content checks. After VM destruction the test fallocates and punches the guest_memfd to verify lifetime/reference handling.

## Dependencies and Integration Points
This file depends on `KVM_CAP_VM_TYPES` advertising `KVM_X86_SW_PROTECTED_VM`, guest_memfd, memory attributes, hypercall exits, pthreads, and fallocate semantics. It integrates with KVM memory-slot registration, selftests address translation, and backing source helpers.

## Risks and Test Signals
Risks include races between vCPU threads and host memory checks, misaligned memslot sizing, incorrect folio/page granularity for 2 MiB ranges, stale SPTEs after punching holes, and broken guest_memfd lifetime after VM close. Test signals are guest assertions on byte patterns, host assertions on shared visibility, successful hypercall handling, zero reads after hole punching, and no failure across different vCPU/memslot configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_conversions_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_kvm_exits_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_kvm_exits_test.c

## Purpose
This protected-VM test verifies that impossible private accesses exit to userspace as `KVM_EXIT_MEMORY_FAULT` with accurate private-fault metadata. It covers private access after deleting a guest_memfd memslot and private access to a memslot that was not created as private-capable.

## Important APIs, Types, and Functions
Important pieces are `protected_vm_shape`, `guest_repeatedly_read()`, `run_vcpu_get_exit_reason()`, `test_private_access_memslot_deleted()`, and `test_private_access_memslot_not_private()`. The test uses `KVM_X86_SW_PROTECTED_VM`, `vm_userspace_mem_region_add()`, `vm_mem_set_private()`, `vm_mem_region_delete()`, `virt_map()`, `_vcpu_run()`, and `struct kvm_run.memory_fault`.

## Control Flow, State, and Persistence
The guest loops reading a fixed virtual address mapped to a single GPA. In the deletion case, the host marks the page private and starts `KVM_RUN` on a pthread while deleting the memslot, expecting the run to fail with `EFAULT` and `KVM_EXIT_MEMORY_FAULT`. In the non-private-slot case, the VM maps ordinary anonymous memory, marks the GPA private, runs the vCPU, and expects the same exit. State exists only in the protected VM, one memslot, one page mapping, and the run-page fault fields.

## Dependencies and Integration Points
The file integrates with KVM's software-protected VM type, guest memory attributes, guest_memfd slot flags, memslot deletion, and userspace memory-fault exit ABI.

## Risks and Test Signals
Risks are race sensitivity in the memslot-deleted case and regressions in private-fault size/GPA reporting. Passing signals are `KVM_EXIT_MEMORY_FAULT`, `KVM_MEMORY_EXIT_FLAG_PRIVATE`, GPA equal to `EXITS_TEST_GPA`, and size equal to one page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/private_mem_kvm_exits_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/recalc_apic_map_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/recalc_apic_map_test.c

## Purpose
This is a race/regression test for `kvm_recalculate_apic_map()`. It tries to widen the APIC-map recalculation window with the maximum selftests vCPU count while concurrently toggling APIC state.

## Important APIs, Types, and Functions
The test uses `race()` as a pthread loop issuing `KVM_SET_LAPIC`, and `main()` creates `KVM_MAX_VCPUS`, sets `MSR_IA32_APICBASE`, and repeatedly toggles one vCPU between x2APIC enabled and LAPIC disabled. It depends on `struct kvm_lapic_state`, `vcpu_ioctl(KVM_SET_LAPIC)`, `vcpu_set_msr()`, and APIC constants from `apic.h`.

## Control Flow, State, and Persistence
All vCPUs are first put into x2APIC mode to avoid APIC-ID aliasing. A racing thread continuously sets a zeroed LAPIC state on vCPU0, which forces APIC-map recalculation. The main thread toggles the last vCPU's APIC base between enabled x2APIC and disabled for five seconds, then cancels the worker. The only state is volatile VM/vCPU APIC state.

## Dependencies and Integration Points
It integrates with LAPIC state ioctls, APIC base MSR virtualization, x2APIC mode handling, pthread cancellation, and KVM's APIC destination map internals.

## Risks and Test Signals
The test is probabilistic and may not hit a narrow race every run, but should reliably expose crashes, use-after-free, lock inversions, or invalid APIC-map handling under stress. Passing is simply completing without assertion, hang, or kernel failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/recalc_apic_map_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_boot_cpu_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_boot_cpu_id.c

## Purpose
This test validates `KVM_SET_BOOT_CPU_ID`: valid BSP selection before vCPU creation, rejection of invalid IDs, and `EBUSY` once vCPU state has been created or run.

## Important APIs, Types, and Functions
Important helpers are `guest_bsp_vcpu()`, `guest_not_bsp_vcpu()`, `test_set_invalid_bsp()`, `test_set_bsp_busy()`, `create_vm()`, `run_vm_bsp()`, and `check_set_bsp_busy()`. It uses `get_bsp_flag()` from APIC helpers, `KVM_CAP_SET_BOOT_CPU_ID`, `KVM_CAP_MAX_VCPU_ID`, `vm_ioctl(KVM_SET_BOOT_CPU_ID)`, and selftests `GUEST_SYNC`/`GUEST_DONE`.

## Control Flow, State, and Persistence
`main()` requires the capability, runs VMs with BSP IDs 0 and 1, then exercises busy-state rejection. `create_vm()` validates out-of-range values, sets the BSP ID, and adds two vCPUs whose guest code asserts whether the BSP flag matches the selected ID. `run_vcpu()` also attempts to change the BSP while the VM is running and after termination. State is limited to VM boot CPU ID, vCPU IDs, APIC BSP flag, and ucall stages.

## Dependencies and Integration Points
The file integrates KVM boot CPU ID selection, APIC reset/BSP semantics, maximum vCPU ID capability, and selftests VM/vCPU creation ordering.

## Risks and Test Signals
Risks include allowing high 32-bit ID garbage, accepting IDs greater than `KVM_CAP_MAX_VCPU_ID`, or changing BSP after vCPUs exist. Signals are guest BSP flag assertions and expected `EINVAL`/`EBUSY` ioctl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_boot_cpu_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_sregs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_sregs_test.c

## Purpose
This regression test validates `KVM_SET_SREGS` enforcement for invalid `IA32_APIC_BASE`, unsupported CR4 bits, and illegal CR0 combinations. It also checks that CPUID-dependent CR4 state is honored even when userspace never calls `KVM_SET_CPUID2`.

## Important APIs, Types, and Functions
Key logic is in `calc_supported_cr4_feature_bits()`, `test_cr_bits()`, and the `TEST_INVALID_CR_BIT` macro. The test uses `struct kvm_sregs`, `_vcpu_sregs_set()`, `vcpu_sregs_get()`, feature probes such as `kvm_cpu_has()`, CPUID checks through `vcpu_cpuid_has()`, and control-register/APIC constants from `processor.h`.

## Control Flow, State, and Persistence
The first VM is barebones and avoids CPUID setup to verify KVM still rejects unsupported CR4 bits. The second VM has normal guest CPUID, attempts invalid and valid APIC base values, then sets all supported CR4 bits. For each unsupported CR4 bit and illegal CR0 bit combination, the test attempts `KVM_SET_SREGS`, expects failure, and verifies KVM left the original sregs unchanged. State is transient in the vCPU's special-register block and CPUID model.

## Dependencies and Integration Points
It integrates with x86 feature enumeration, KVM special-register validation, APIC base MSR constraints, CR0/CR4 architectural rules, and OSXSAVE/OSPKE CPUID side effects.

## Risks and Test Signals
Risks include KVM accepting unsupported features, partially modifying sregs on a failed ioctl, or failing to reflect CR4.OSXSAVE/CR4.PKE into guest CPUID. Test signals are expected `_vcpu_sregs_set()` failures and exact sregs preservation after rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_sregs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_init2_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_init2_tests.c

## Purpose
This test validates the `KVM_SEV_INIT2` memory-encryption command across SEV, SEV-ES, and SNP VM types. It checks VM type acceptance, invalid flag rejection, and VMSA feature filtering against the kernel-reported feature mask.

## Important APIs, Types, and Functions
Important helpers are `__sev_ioctl()`, `test_init2()`, `test_init2_invalid()`, `test_vm_types()`, `test_flags()`, and `test_features()`. It uses `struct kvm_sev_cmd`, `struct kvm_sev_init`, `KVM_MEMORY_ENCRYPT_OP`, `KVM_SEV_INIT2`, `KVM_X86_GRP_SEV/KVM_X86_SEV_VMSA_FEATURES`, `KVM_CAP_VM_TYPES`, and CPUID probes for SEV, SEV-ES, and SEV-SNP.

## Control Flow, State, and Persistence
`main()` opens KVM, fetches supported VMSA features, checks that VM-type capability bits match CPUID, and then creates throwaway barebones VMs for valid and invalid `KVM_SEV_INIT2` calls. It tests the default SEV type, SEV-ES and SNP when present, rejects default and software-protected VM types, rejects every flag bit, and allows only known supported VMSA feature bits. No persistent state is kept beyond firmware/KVM initialization of each temporary VM.

## Dependencies and Integration Points
The test integrates with `/dev/sev`, KVM SEV device attributes, KVM VM-type creation, PSP firmware return codes, and SEV feature enumeration.

## Risks and Test Signals
Risks include CPUID/capability mismatch, accepting unknown flags/features, or misclassifying SEV-ES/SNP feature dependencies. Signals are successful `KVM_SEV_INIT2` for supported combinations and `EINVAL` for invalid VM types, flags, and unknown VMSA feature bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_init2_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_migrate_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_migrate_tests.c

## Purpose
This test exercises KVM SEV encrypted-context move and copy capabilities. It verifies migration chains, dead-source behavior, mirror VM creation, parameter validation, concurrent migration locking, and mirror/migration interactions for SEV and SEV-ES where available.

## Important APIs, Types, and Functions
Key helpers are `sev_vm_create()`, `aux_vm_create()`, `__sev_migrate_from()`, `test_sev_migrate_from()`, `test_sev_migrate_locking()`, `test_sev_migrate_parameters()`, `__sev_mirror_create()`, `verify_mirror_allowed_cmds()`, `test_sev_mirror()`, `test_sev_mirror_parameters()`, and `test_sev_move_copy()`. It uses `KVM_CAP_VM_MOVE_ENC_CONTEXT_FROM`, `KVM_CAP_VM_COPY_ENC_CONTEXT_FROM`, SEV launch helpers from `sev.h`, and `KVM_SEV_*` commands.

## Control Flow, State, and Persistence
`main()` requires SEV and relevant capabilities. Migration tests create launched SEV/SEV-ES VMs with four vCPUs, move encrypted context through a chain of destination VMs, and verify moving back from a dead source fails. Locking tests repeatedly call migration from several threads to stress internal serialization. Parameter tests reject non-SEV sources, already encrypted destinations, vCPU count mismatches, and missing SEV-ES VMSA updates. Mirror tests copy encrypted context into vCPU-less VMs, add vCPUs later, verify allowed/disallowed SEV commands, and combine move/copy chains. State is encrypted VM context, launch state, vCPU count, and mirror ownership; it is destroyed with each VM.

## Dependencies and Integration Points
The file integrates with SEV firmware ioctls, KVM encrypted-context ownership, vCPU creation rules, SEV-ES VMSA update requirements, pthread concurrency, and selftests SEV helpers.

## Risks and Test Signals
Risks include context ownership leaks, allowing migration to/from invalid VM states, races in encrypted-context locks, and mirror command over-permissiveness. Signals are expected success through valid chains, `EINVAL` or `EIO` for invalid moves, no crashes under concurrent migration attempts, and successful `KVM_SEV_GUEST_STATUS` on mirrors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_migrate_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_smoke_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_smoke_test.c

## Purpose
This is a functional smoke test for SEV, SEV-ES, and SNP guests. It verifies SEV status MSRs, selected control-register/MSR round trips, GHCB termination exits for SEV-ES/SNP, shutdown handling, and VMSA XSAVE synchronization.

## Important APIs, Types, and Functions
Important guest functions are `guest_sev_code()`, `guest_sev_es_code()`, `guest_snp_code()`, `guest_shutdown_code()`, and the assembly entry `guest_code_xsave`. Host helpers are `test_sev()`, `test_sev_shutdown()`, `test_sync_vmsa()`, `compare_xsave()`, and `test_sev_smoke()`. The test uses `vm_sev_create_with_one_vcpu()`, `vm_sev_launch()`, `vcpu_xsave_set()`, `KVM_EXIT_SYSTEM_EVENT`, `KVM_SYSTEM_EVENT_SEV_TERM`, GHCB MSR protocol constants, and SEV/SNP policy bits.

## Control Flow, State, and Persistence
For SEV, the guest checks CPUID/MSR state, touches EFER and control registers, then exits with `GUEST_DONE`. For SEV-ES and SNP, the guest verifies SEV status bits, tests registers, writes `GHCB_MSR_TERM_REQ`, and performs `vmgexit()`, which the host expects as a system-event termination. Shutdown tests deliberately corrupt the IDT and execute `ud2`. VMSA sync tests seed host XSAVE state, launch an encrypted guest that saves its initial XSAVE image into a shared page, and compare bytes. State is per-VM encrypted launch state, guest VMSA, shared page data, and XSAVE contents.

## Dependencies and Integration Points
This integrates with SEV/SEV-ES/SNP CPU features, SEV launch helpers, GHCB MSR termination, KVM XCRS/XSAVE support, shared-page allocation in encrypted VMs, and SNP/SEV policy handling.

## Risks and Test Signals
Risks include missing SEV MSR bits, bad GHCB termination mapping, VMSA state not synced before guest entry, and shutdown exits being misreported. Signals are `UCALL_DONE` for SEV guests, exact `KVM_SYSTEM_EVENT_SEV_TERM` data for SEV-ES/SNP, `KVM_EXIT_SHUTDOWN` for corrupted IDT, and byte-identical XSAVE images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sev_smoke_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smaller_maxphyaddr_emulation_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smaller_maxphyaddr_emulation_test.c

## Purpose
This test validates KVM behavior when guest `MAXPHYADDR` is smaller than the host physical-address width and a guest page table entry sets a reserved bit above guest MAXPHYADDR. With TDP enabled KVM must emulate after an EPT violation; without TDP the guest should receive a reserved-bit page fault.

## Important APIs, Types, and Functions
The file uses `guest_code()`, `FLDS_MEM_EAX` from `flds_emulation.h`, `handle_flds_emulation_failure_exit()`, `vcpu_set_cpuid_property(X86_PROPERTY_MAX_PHY_ADDR)`, `KVM_CAP_SMALLER_MAXPHYADDR`, and `KVM_CAP_EXIT_ON_EMULATION_FAILURE`. It directly modifies the guest PTE returned by `vm_get_pte()`.

## Control Flow, State, and Persistence
`main()` creates one vCPU, sets guest MAXPHYADDR to 36, enables emulation-failure exits, maps one page at a high GPA, and sets bit 36 in the PTE to make the GPA reserved from the guest's perspective. The guest executes `flds` through a safe exception wrapper. In TDP mode userspace handles the expected emulation-failure exit and skips the instruction; in shadow/non-TDP mode the guest expects `#PF` with `PFERR_RSVD_MASK`. State is limited to the VM page tables, CPUID property, and the one emulation-failure exit.

## Dependencies and Integration Points
It integrates with KVM smaller-MAXPHYADDR emulation, TDP vs shadow MMU behavior, emulation-failure exit ABI, CPUID property overrides, and the selftests FLDS emulation helper.

## Risks and Test Signals
Risks include incorrect reserved-bit detection, failure to exit on unsupported emulation, or misrouting the fault between guest #PF and userspace exit. Signals are a handled emulation failure with TDP and a guest `#PF(RSVD)` without TDP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smaller_maxphyaddr_emulation_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smm_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smm_test.c

## Purpose
This test validates System Management Mode save/restore behavior, including SMI handling while nested VMX or SVM state is active. It verifies that state snapshots taken inside and around SMM can be restored into a recreated VM.

## Important APIs, Types, and Functions
Important pieces are `smi_handler[]`, `setup_smram()`, `self_smi()`, `guest_code()`, `l2_guest_code()`, `inject_smi()`, `vcpu_save_state()`, `vm_recreate_with_one_vcpu()`, and `vcpu_load_state()`. It uses `KVM_CAP_X86_SMM`, optional `KVM_CAP_NESTED_STATE`, VMX helpers, SVM helpers, x2APIC self-SMI delivery, and an I/O sync port.

## Control Flow, State, and Persistence
The host sets up SMRAM and optional nested virtualization pages. The guest enables x2APIC, triggers SMI to itself, optionally enters nested L2, and syncs fixed stage numbers through port I/O. The host loops over every sync, validates reported stages or the fixed SMRAM stage, injects additional SMIs during L2 execution, and on almost every stage saves KVM x86 state, releases/recreates the VM, reloads state, and continues. State spans SMRAM contents, SMM save state, nested VMCS/VMCB state, APIC mode, and selftest stage counters.

## Dependencies and Integration Points
The file integrates KVM SMM capability, SMRAM setup, APIC SMI delivery, nested VMX/SVM execution, KVM x86 state serialization, and VM recreation.

## Risks and Test Signals
Risks include losing SMM state during migration-style save/restore, corrupting nested state while in SMM, incorrect RSM return, and save/restore while an SMI is active. Signals are sequential stage reports, expected SMRAM-stage reports while in SMM, and eventual `DONE` without guest assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/smm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/state_test.c

## Purpose
This broad save/restore test validates `KVM_GET/SET_*` vCPU state, XSAVE restoration, and nested VMX/SVM state preservation. It is a migration-style regression test for regular and nested guest execution.

## Important APIs, Types, and Functions
Important functions are `guest_code()`, `svm_l1_guest_code()`, `svm_l2_guest_code()`, `vmx_l1_guest_code()`, `vmx_l2_guest_code()`, `svm_check_nested_state()`, and `check_nested_state()`. Host logic uses `vcpu_save_state()`, `kvm_vm_release()`, `vm_recreate_with_one_vcpu()`, `vcpu_load_state()`, `vcpu_xsave_set()`, `vcpu_init_cpuid()`, and nested allocation helpers.

## Control Flow, State, and Persistence
The guest first dirties XSAVE-managed state for x87, SSE, AVX, AVX-512, MPX, and PKRU when available. If nested state is available, it then runs either SVM or VMX L1 code. SVM validates VGIF and next-RIP preservation; VMX validates VMCS launch state, `vmptrst`, VMRESUME/VMLAUNCH behavior, and shadow VMCS interaction. On every `GUEST_SYNC`, the host saves full x86 state, releases and recreates the VM, reloads the state, verifies register equality, and separately attempts XSAVE loading into dummy vCPUs with and without CPUID.

## Dependencies and Integration Points
This integrates with x86 state ioctls, nested-state capability, VMX/SVM selftests helpers, XSAVE ABI rules, CPUID/XCR0 feature state, and VM recreation as a migration proxy.

## Risks and Test Signals
Risks include lost launched VMCS state, incorrect shadow-VMCS pointer state, SVM VGIF/nRIP mismatch, XSAVE rejection based on guest CPUID, and register drift after restore. Signals are guest assertions across staged syncs, host nested-state checks, successful dummy XSAVE loads, and identical pre/post-restore general registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/state_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_int_ctl_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_int_ctl_test.c

## Purpose
This nested SVM test validates simultaneous delivery of L1 physical interrupts and L2 virtual interrupts through the VMCB `int_ctl` path. It specifically checks that with virtual interrupt masking disabled, L2 receives both the real LAPIC interrupt and the pending virtual interrupt.

## Important APIs, Types, and Functions
Key functions are `vintr_irq_handler()`, `intr_irq_handler()`, `l2_guest_code()`, and `l1_guest_code()`. It uses `generic_svm_setup()`, `run_guest()`, `struct vmcb.control.int_ctl`, `V_IRQ_MASK`, `V_INTR_PRIO_SHIFT`, `V_INTR_MASKING_MASK`, `INTERCEPT_INTR`, `INTERCEPT_VINTR`, x2APIC self-IPI, and SVM exit-code checking.

## Control Flow, State, and Persistence
L1 enables x2APIC, prepares L2, clears virtual interrupt masking and interrupt intercepts, and marks a virtual interrupt pending in the VMCB. L2 sends itself a fixed interrupt through the LAPIC and executes `sti_nop()`. The two guest handlers set globals, and L2 asserts both fired before exiting through `vmcall`. The host only runs until `UCALL_DONE` or guest abort.

## Dependencies and Integration Points
The file depends on AMD SVM support, nested SVM VMCB control semantics, LAPIC interrupt delivery, and selftests IDT exception-handler installation.

## Risks and Test Signals
Risks include priority/masking mishandling, L1 intercepting interrupts that should reach L2, or losing the V_IRQ event. Signals are both handler globals set and L1 observing `SVM_EXIT_VMMCALL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_int_ctl_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_lbr_nested_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_lbr_nested_state.c

## Purpose
This test validates last-branch-record state preservation across nested SVM save/restore, both with nested LBR virtualization enabled and disabled. It checks separation between L1 and L2 LBR state when virtual LBR is active.

## Important APIs, Types, and Functions
Important items are `struct lbr_branch`, `RECORD_AND_CHECK_BRANCH`, `CHECK_BRANCH_MSRS`, `CHECK_BRANCH_VMCB`, `l2_guest_code()`, `l1_guest_code()`, and `test_lbrv_nested_state()`. It uses `MSR_IA32_DEBUGCTLMSR`, `MSR_IA32_LASTBRANCHFROMIP`, `MSR_IA32_LASTBRANCHTOIP`, `SVM_MISC2_ENABLE_V_LBR`, `vcpu_save_state()`, and `vcpu_load_state()`.

## Control Flow, State, and Persistence
L1 records a branch into LBR MSRs, triggers a save/restore, then runs L2. L2 records its own branch, triggers another save/restore, and exits. L1 syncs once more after L2, then verifies either that L1 MSRs remain intact and L2 branch data is stored in VMCB fields when nested LBRV is enabled, or that the shared MSRs contain L2 branch data when disabled. The test runs both modes.

## Dependencies and Integration Points
It depends on SVM support and KVM LBRV enablement. It integrates with debug-control MSRs, nested VMCB save fields, and KVM x86 state serialization.

## Risks and Test Signals
Risks include lost LBR MSRs during migration, failure to copy virtual LBR fields to/from VMCB, and incorrect sharing when LBRV is off. Signals are non-zero recorded branch addresses and exact MSR/VMCB comparisons after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_lbr_nested_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_clear_efer_svme.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_clear_efer_svme.c

## Purpose
This short nested SVM regression test verifies that clearing `EFER.SVME` from L2 causes a shutdown path instead of returning normally to L1 or corrupting host state.

## Important APIs, Types, and Functions
The test uses `l2_guest_code()`, `l1_guest_code()`, `generic_svm_setup()`, `run_guest()`, `rdmsr(MSR_EFER)`, `wrmsr(MSR_EFER)`, and `vcpu_alloc_svm()`.

## Control Flow, State, and Persistence
L1 prepares and enters L2 through generic SVM setup. L2 asserts `EFER_SVME` is initially set, clears it, and should never execute the following guest assertion. The host runs one vCPU and expects `KVM_EXIT_SHUTDOWN`. State is limited to the nested VMCB and EFER.

## Dependencies and Integration Points
It requires AMD SVM support and nested SVM execution through selftests helpers.

## Risks and Test Signals
Risks include mishandling architectural shutdown conditions or allowing illegal nested SVM state to continue. The decisive signal is `KVM_EXIT_SHUTDOWN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_clear_efer_svme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_shutdown_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_shutdown_test.c

## Purpose
This nested SVM test verifies that an unintercepted L2 shutdown does not crash KVM and is surfaced as `KVM_EXIT_SHUTDOWN`.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()` and `l1_guest_code()`. The test uses `generic_svm_setup()`, `run_guest()`, `vmcb->control.intercept`, `INTERCEPT_SHUTDOWN`, and guest IDT entry manipulation.

## Control Flow, State, and Persistence
L2 executes `ud2`. L1 clears the shutdown intercept and marks the #UD, #NP, and #DF IDT entries not-present so injection cascades through faults to shutdown. The host expects `KVM_EXIT_SHUTDOWN` from `KVM_RUN`. State is volatile in guest IDT descriptors and the nested VMCB.

## Dependencies and Integration Points
The file integrates with AMD nested SVM exception injection, IDT descriptor validity, shutdown intercept control, and KVM shutdown exits.

## Risks and Test Signals
Risks include host crashes from recursive exception handling or incorrect interception of shutdown. Passing is the expected shutdown exit and no guest return to L1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_shutdown_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_soft_inject_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_soft_inject_test.c

## Purpose
This test validates nested SVM soft interrupt, breakpoint, and NMI injection corner cases, especially interactions with next-RIP, intervening nested page-fault-like IDT changes, GIF/NMI blocking, and guest debug state.

## Important APIs, Types, and Functions
Key functions are `guest_bp_handler()`, `guest_int_handler()`, `guest_nmi_handler()`, `l2_guest_code_int()`, `l2_guest_code_nmi()`, `l1_guest_code()`, and `run_test()`. It uses `vmcb->control.event_inj`, `SVM_EVTINJ_TYPE_SOFT`, `SVM_EVTINJ_TYPE_EXEPT`, `SVM_EVTINJ_TYPE_NMI`, `next_rip`, `clgi()/stgi()`, APIC self-NMI, alternate IDT pages, and `vcpu_guest_debug_set()`.

## Control Flow, State, and Persistence
For soft interrupts, L1 injects vector 0x20 into L2, expects the handler RIP to equal the L2 entry, exits on VMMCALL, advances RIP, swaps to an alternate IDT, injects #BP with a next-RIP that skips an embedded `ud2`, and expects an HLT exit. For NMI, L1 injects an NMI, handles a VMMCALL from the NMI handler, then uses `clgi/stgi` and a self-NMI to verify nested NMI state resumes correctly. Host installs handlers, disables guest debug content, wraps execution in an alarm, and checks `UCALL_DONE`.

## Dependencies and Integration Points
It requires SVM and nRIP support. It integrates with nested SVM event injection fields, APIC NMI delivery, IDT copying, atomic guest-visible counters, and guest debug ioctls.

## Risks and Test Signals
Risks include wrong next-RIP on soft-event injection, lost NMI blocking, bad event type encoding, or hangs in NMI/GIF state. Signals include exact handler counters, expected VMMCALL/HLT exits, and final `UCALL_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_soft_inject_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_vmcb12_gpa.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_vmcb12_gpa.c

## Purpose
This harness-based nested SVM test validates handling of invalid and unmappable VMCB12 physical addresses for VMRUN, VMLOAD, VMSAVE, and nested VM-exit paths.

## Important APIs, Types, and Functions
Important helpers are `l1_vmrun()`, `l1_vmload()`, `l1_vmsave()`, `l1_vmexit()`, `unmappable_gpa()`, `test_invalid_vmcb12()`, `test_unmappable_vmcb12()`, and `test_unmappable_vmcb12_vmexit()`. It uses `KVM_ONE_VCPU_TEST_SUITE`, SVM assembly instructions, GP exception handling, `vcpu_save_state()`, `vcpu_load_state()`, and `state->nested.hdr.svm.vmcb_pa`.

## Control Flow, State, and Persistence
Invalid `-1ULL` VMCB GPA cases install a #GP handler and expect a sync from the handler. Unmappable VMCB GPA cases compute a GPA just after all VM memory regions and expect `KVM_EXIT_INTERNAL_ERROR` with emulation suberror. The VM-exit case first enters L2 with a valid VMCB, saves state while L2 has started, mutates nested-state `vmcb_pa` to an unmappable GPA, reloads state, and expects shutdown when KVM cannot map VMCB12 on nested exit. State includes VM memory-region layout and nested-state serialized VMCB GPA.

## Dependencies and Integration Points
The file depends on SVM support, selftests harness macros, KVM nested-state load validation, and KVM internal-error/shutdown exit paths.

## Risks and Test Signals
Risks include accepting invalid physical addresses, reporting the wrong exit reason, or failing late on nested VM-exit state. Signals are `SYNC_GP`, `KVM_INTERNAL_ERROR_EMULATION`, and `KVM_EXIT_SHUTDOWN` for the respective scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_nested_vmcb12_gpa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_vmcall_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_vmcall_test.c

## Purpose
This minimal nested SVM test verifies that an L2 `vmcall` instruction exits to L1 as `SVM_EXIT_VMMCALL`.

## Important APIs, Types, and Functions
The file uses `l2_guest_code()`, `l1_guest_code()`, `generic_svm_setup()`, `run_guest()`, `vcpu_alloc_svm()`, and VMCB `exit_code`.

## Control Flow, State, and Persistence
The host creates one VM, allocates SVM state, passes it to L1, and repeatedly runs until `UCALL_DONE`. L1 prepares L2, enters it, and asserts the VMCB exit code is `SVM_EXIT_VMMCALL`. State is the nested VMCB and ucall stream only.

## Dependencies and Integration Points
It requires AMD SVM support and the selftests nested SVM helper stack.

## Risks and Test Signals
The test is narrow; its risk signal is a regression in VMCALL intercept/exit-code mapping. Passing requires L1 assertion success and `GUEST_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/svm_vmcall_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sync_regs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sync_regs_test.c

## Purpose
This test validates the x86 `KVM_CAP_SYNC_REGS` shared `kvm_run.s.regs` ABI. It covers valid/invalid register masks, synchronization direction controlled by `kvm_valid_regs` and `kvm_dirty_regs`, and races while KVM processes events or special registers.

## Important APIs, Types, and Functions
Important functions are `guest_code()`, `compare_regs()`, `race_sync_regs()`, `race_events_inj_pen()`, `race_events_exc()`, and `race_sregs_cr4()`. The harness tests include `read_invalid`, `set_invalid`, `req_and_verify_all_valid`, `set_and_verify_various`, `clear_kvm_dirty_regs_bits`, `clear_kvm_valid_and_dirty_regs`, `clear_kvm_valid_regs_bits`, and three race tests. It uses `KVM_SYNC_X86_REGS`, `KVM_SYNC_X86_SREGS`, `KVM_SYNC_X86_EVENTS`, `KVM_TRANSLATE`, and `vcpu_save_state()`.

## Control Flow, State, and Persistence
The guest loops on port I/O and increments RBX after each exit. Tests set valid/dirty masks before `KVM_RUN`, compare shared-page register data with ioctl-returned state, and mutate RBX/APIC base to check copy-in/copy-out behavior. Race tests save a known-good state, spawn a pthread that continuously dirties event or sregs fields in `struct kvm_run`, run for a timeout, and reload state after shutdowns caused by injected bad events. State is the shared `kvm_run` page, vCPU register/event/sreg state, and a temporary saved x86 state snapshot.

## Dependencies and Integration Points
It integrates with KVM_RUN register synchronization, exception injection validation, CR4/EFER long-mode validity, KVM translation, shutdown behavior, and the one-vCPU test harness.

## Risks and Test Signals
Risks include accepting invalid sync masks, stale shared-page fields, applying dirty values when not requested, ignoring dirty values when requested, or racing into invalid MMU state. Signals are expected `EINVAL`, exact RBX/APIC-base behavior, matching ioctl/shared regs, and no kernel failure during race loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/sync_regs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/triple_fault_event_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/triple_fault_event_test.c

## Purpose
This test validates `KVM_CAP_X86_TRIPLE_FAULT_EVENT`, including injecting a pending triple-fault event while L2 is stopped at a userspace I/O exit. It covers VMX and SVM paths.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code_vmx()`, and `l1_guest_code_svm()`. Host logic uses `vm_enable_cap(KVM_CAP_X86_TRIPLE_FAULT_EVENT)`, `vcpu_events_get()`, `vcpu_events_set()`, `KVM_VCPUEVENT_VALID_TRIPLE_FAULT`, `vcpu_run_complete_io()`, VMX/SVM nested helpers, and `run->immediate_exit`.

## Control Flow, State, and Persistence
L1 launches L2, which exits to L0 userspace through an `inb`. The host confirms the I/O port, reads vCPU events, marks a triple fault pending, sets `immediate_exit`, completes the I/O, and verifies the pending event remains. Resuming then should produce shutdown on SVM or a VMX L1-observed triple-fault VM-exit leading to `UCALL_DONE`. State is pending vCPU event state plus nested VMCS/VMCB execution.

## Dependencies and Integration Points
This integrates with KVM vCPU event get/set ABI, triple-fault event capability, nested VMX/SVM triple-fault handling, and KVM I/O completion.

## Risks and Test Signals
Risks include dropping pending triple-fault events across I/O completion, losing event validity flags, or mishandling nested triple-fault delivery. Signals are retained pending flags, `KVM_EXIT_SHUTDOWN` for SVM, or VMX `EXIT_REASON_TRIPLE_FAULT` observed by L1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/triple_fault_event_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_msrs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_msrs_test.c

## Purpose
This test validates interactions between `MSR_IA32_TSC`, `MSR_IA32_TSC_ADJUST`, and host-side TSC offsetting. It checks both guest and host MSR writes.

## Important APIs, Types, and Functions
Important elements are `guest_code()`, `run_vcpu()`, `rounded_rdmsr()`, `rounded_host_rdmsr()`, `vcpu_get_msr()`, and `vcpu_set_msr()`. The test uses kselftest result reporting with a five-stage plan.

## Control Flow, State, and Persistence
The guest starts from zeroed rounded TSC/TSC_ADJUST, writes TSC, writes TSC_ADJUST, observes a host-applied TSC offset, writes TSC_ADJUST again, and finally writes TSC. The host mirrors each stage, sets a host-side TSC offset through `MSR_IA32_TSC`, verifies host writes to TSC_ADJUST do not modify TSC, and restores expected values. Rounding masks natural TSC progression. State is vCPU TSC offset and TSC_ADJUST MSR state.

## Dependencies and Integration Points
It integrates with KVM MSR virtualization for TSC/TSC_ADJUST, guest ucall stage sequencing, and kselftest TAP-style reporting.

## Risks and Test Signals
Risks include conflating guest writes with host offset writes, corrupting TSC_ADJUST, or time drift exceeding rounding tolerance. Signals are exact rounded MSR equality at each stage and five kselftest passes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_msrs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_scaling_sync.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_scaling_sync.c

## Purpose
This test checks that TSC scaling and synchronization remain monotonic across many concurrently created vCPUs. It targets regressions where scaled TSC values can move backward between vCPUs.

## Important APIs, Types, and Functions
Important code includes `guest_code()`, `run_vcpu()`, `pthread_spinlock_t create_lock`, `KVM_SET_TSC_KHZ`, `KVM_CAP_VM_TSC_CONTROL`, `vcpu_set_msr(MSR_IA32_TSC)`, and the shared global `tsc_sync`.

## Control Flow, State, and Persistence
`main()` creates a 20-vCPU VM, sets a test TSC frequency, and starts 20 pthreads. Each thread serializes vCPU creation under a spinlock because selftests creation is not thread-safe; the first created vCPU sets an initial TSC offset. Guests loop for a bounded TSC duration, repeatedly comparing their local TSC against the last shared TSC and reporting a sync if time regresses. Threads return failure counts, and the host sums them. State is the VM TSC frequency, one initial offset, guest shared `tsc_sync`, and per-thread failure counters.

## Dependencies and Integration Points
It integrates with KVM TSC scaling control, MSR TSC writes, concurrent vCPU execution, pthread synchronization, and ucall reporting.

## Risks and Test Signals
Risks include false positives from unsynchronized shared memory, vCPU creation races, or insufficient runtime. The signal is zero guest-reported regressions across all vCPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_scaling_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/ucna_injection_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/ucna_injection_test.c

## Purpose
This test verifies userspace injection of UnCorrectable No Action required machine-check errors through KVM MCE APIs. It checks both CMCI interrupt delivery and recording of UCNA data in machine-check bank registers.

## Important APIs, Types, and Functions
Key functions are `ucna_injection_guest_code()`, `guest_cmci_handler()`, `inject_ucna()`, `run_ucna_injection()`, `test_ucna_injection()`, `setup_mce_cap()`, `create_vcpu_with_mce_cap()`, and `run_vcpu_expect_gp()`. It uses `KVM_X86_GET_MCE_CAP_SUPPORTED`, `KVM_X86_SETUP_MCE`, `KVM_X86_SET_MCE`, `struct kvm_x86_mce`, MCE MSRs, xAPIC CMCI vector programming, and APIC default GPA mapping.

## Control Flow, State, and Persistence
The host creates three vCPUs: one with CMCI support for the main injection flow, one without CMCI support, and one for reserved-bit validation. The main guest enables xAPIC, programs LVTCMCI, enables per-bank CMCI, syncs for a first UCNA injection, records the bank address, disables CMCI, syncs for a second UCNA, and records again. The host injects two MCEs and verifies only the first caused a CMCI interrupt while both updated bank address registers. The other guests intentionally write invalid/unsupported MCI_CTL2 bits and should #GP.

## Dependencies and Integration Points
This integrates with KVM MCE setup, machine-check bank MSRs, CMCI delivery through LAPIC, xAPIC mapping, guest exception handlers, and host MCE capability filtering.

## Risks and Test Signals
Risks include incorrect MCG capability masking, signaling UCNA despite CMCI disabled, missing register recording, and reserved-bit validation failures. Signals are one CMCI interrupt, matching first/second UCNA addresses, and expected guest #GP syncs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/ucna_injection_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_io_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_io_test.c

## Purpose
This test stresses KVM userspace I/O exits for repeated string input (`rep insb`) when userspace modifies RCX/count between exits. It ensures KVM does not overflow or crash even when userspace abuses internal batching behavior.

## Important APIs, Types, and Functions
Important functions are `guest_ins_port80()` and `guest_code()`. Host code uses `KVM_EXIT_IO`, `run->io.data_offset`, `vcpu_regs_get()`, `vcpu_regs_set()`, and direct filling of the KVM I/O data buffer.

## Control Flow, State, and Persistence
The guest performs three port-0x80 `rep insb` operations: count 2, count 3, and count 8192. For the first two, the host changes RCX from 2 to 1 and from 3 to 8192 after the userspace exit. For every I/O exit the host fills the run-page data buffer with 0xaa. The final 8192-byte transfer is checked byte-by-byte by the guest. State is the guest buffer, RCX/RDI string state, and KVM run-page I/O buffer.

## Dependencies and Integration Points
It integrates with KVM userspace I/O exit ABI, x86 string-I/O emulation, vCPU register get/set, and selftests ucall handling.

## Risks and Test Signals
Risks include buffer overflow, count underflow, stale RCX/RDI handling, or undefined behavior from relying on KVM batching. Signals are guest assertions on final count, final pointer, and all buffer bytes equal to 0xaa.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_io_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_msr_exit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_msr_exit_test.c

## Purpose
This test validates userspace MSR exits and MSR filtering. It covers allow-list filtering, default-deny filtering, unknown MSR exits, filter permission-bitmap updates, forced-emulation-prefix paths, and ioctl flag validation.

## Important APIs, Types, and Functions
Key data structures are `struct kvm_msr_filter` instances `filter_allow`, `filter_deny`, `filter_fs`, `filter_gs`, and `no_filter_deny`. Important functions include `test_rdmsr()`, `test_wrmsr()`, `test_em_rdmsr()`, `test_em_wrmsr()`, `guest_code_filter_allow()`, `guest_code_filter_deny()`, `guest_code_permission_bitmap()`, `process_rdmsr()`, `process_wrmsr()`, `handle_rdmsr()`, `handle_wrmsr()`, `run_user_space_msr_flag_test()`, and `run_msr_filter_flag_test()`. It uses `KVM_CAP_X86_USER_SPACE_MSR`, `KVM_CAP_X86_MSR_FILTER`, `KVM_EXIT_X86_RDMSR`, `KVM_EXIT_X86_WRMSR`, and MSR exit reason flags.

## Control Flow, State, and Persistence
The allow-filter test traps known, semi-known, and fabricated MSRs, lets userspace return data or errors, and verifies guest #GP handling for rejected accesses; it repeats through forced emulator paths when enabled. The deny-filter test defaults to trapping, allows specific ranges through bitmaps, disables filtering mid-test through a ucall, and counts userspace reads/writes. The permission-bitmap test alternates FS/GS base traps and verifies KVM updates interception. Flag tests iterate all bits in enable-cap and filter flags expecting success only for valid masks. State is per-VM MSR filter configuration, user-maintained fake MSR data, guest exception counters, and run-page MSR exit fields.

## Dependencies and Integration Points
It integrates with KVM MSR filtering, userspace MSR exit reasons (`FILTER`, `UNKNOWN`, `INVAL`), in-kernel MSR emulation, forced emulation prefix support, GP handler RIP fixups, and the one-vCPU harness.

## Risks and Test Signals
Risks include wrong exit reason, stale permission bitmap after filter changes, accepting invalid flag bits, failing to inject #GP from `run->msr.error`, or mishandling fabricated MSRs. Signals are expected exit sequence, exact read/write counters, guest assertions on returned values, and ioctl `EINVAL` for invalid flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/userspace_msr_exit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apic_access_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apic_access_test.c

## Purpose
This nested VMX test validates APIC-access address handling. It verifies that L2 can launch with a memory-backed APIC-access page and that using a valid but unbacked L1 physical address produces a KVM internal emulation error rather than unsafe behavior.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code()`, `prepare_virtualize_apic_accesses()`, `prepare_vmcs()`, `vmlaunch()`, and `vmresume()`. It writes VMCS fields `CPU_BASED_VM_EXEC_CONTROL`, `SECONDARY_VM_EXEC_CONTROL`, and `APIC_ACCESS_ADDR`.

## Control Flow, State, and Persistence
L1 prepares VMX, enables secondary controls and APIC-access virtualization, sets `APIC_ACCESS_ADDR` to the allocated page, syncs to host, launches L2, and observes VMCALL. It then changes `APIC_ACCESS_ADDR` to a high unbacked GPA, syncs again, and resumes L2. The host treats the second sync as a predictor and expects the following `KVM_RUN` to exit with `KVM_EXIT_INTERNAL_ERROR` and `KVM_INTERNAL_ERROR_EMULATION`. State is nested VMCS APIC-access address and VM memory backing.

## Dependencies and Integration Points
The file requires VMX support and integrates with nested VMX APIC-access virtualization, selftests VMX page allocation, and KVM internal-error reporting.

## Risks and Test Signals
Risks include KVM dereferencing unbacked APIC-access memory, returning the wrong exit reason, or failing valid launch. Signals are a successful first L2 VMCALL and an internal emulation error for the unbacked APIC-access address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apic_access_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apicv_updates_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apicv_updates_test.c

## Purpose
This nested VMX test validates APICv inhibition and updates when APIC mode and APIC ID are changed across L1/L2 transitions. It checks that IRQ state, APIC virtualization, and TLB behavior remain coherent.

## Important APIs, Types, and Functions
Important functions are `good_ipi_handler()`, `bad_ipi_handler()`, `l2_guest_code()`, and `l1_guest_code()`. The test uses APIC register helpers, `prepare_virtualize_apic_accesses()`, VMX MSR bitmaps, APICv/APIC-access controls, ISR/EOI checks, and `vcpu_get_stat(vcpu, irq_injections)`.

## Control Flow, State, and Persistence
L1 enables xAPIC and writes a modified APIC ID to inhibit APICv, sends itself a good IPI, and verifies it is in-service. L2 first switches to x2APIC, causing KVM to restore the APIC ID and potentially uninhibit APICv. L1 then scribbles APIC access registers, verifies a bad IPI write is ignored, checks ISR state in x2APIC, EOIs, resumes L2 to switch back to xAPIC, sends another good IPI, and checks ISR/EOI again. State includes APIC mode, APIC ID, vISR/SVI-like in-service state, and KVM IRQ-injection stats.

## Dependencies and Integration Points
It requires VMX and APIC-access virtualization setup. It integrates with APICv inhibition, APIC ID virtualization, xAPIC/x2APIC transitions, APIC access page MMIO, and IRQ injection accounting.

## Risks and Test Signals
Risks include stale APICv state after L2 APIC mode changes, failure to flush L1 TLB for APIC access page changes, bad IPI delivery, or lost in-service vector propagation. Signals are exactly two guest-observed good IPIs, no bad IPI, cleared ISR after EOI, and at least two KVM IRQ injections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_apicv_updates_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_exception_with_invalid_guest_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_exception_with_invalid_guest_state.c

## Purpose
This Intel-only test verifies KVM behavior when exceptions are pending while guest state is invalid and unrestricted guest mode is disabled. It checks repeated internal emulation-failure exits and signal-timed races.

## Important APIs, Types, and Functions
Important functions are `guest_ud_handler()`, `guest_code()`, `run_vcpu_with_invalid_state()`, `set_invalid_guest_state()`, `clear_invalid_guest_state()`, `sigalrm_handler()`, and `set_timer()`. It uses `struct kvm_sregs.tr.unusable`, `vcpu_events_get()`, `KVM_EXIT_INTERNAL_ERROR`, and `KVM_INTERNAL_ERROR_EMULATION`.

## Control Flow, State, and Persistence
The guest loops on `ud2` under a #UD handler. The host first marks TR unusable and runs the vCPU twice, expecting internal emulation failures both times. It then restores valid state, arms a frequent SIGALRM, and the signal handler waits until an exception is pending, marks state invalid, and runs the vCPU from the handler to exercise the pending-exception plus invalid-state path. State is vCPU TR usability, exception pending state, and timer-driven host control.

## Dependencies and Integration Points
It depends on Intel VMX behavior, unrestricted guest being disabled, KVM invalid guest-state emulation limits, POSIX interval timers, and vCPU event ioctls.

## Risks and Test Signals
Risks include KVM crashing or losing pending exceptions when userspace re-enters with invalid state. Signals are repeated `KVM_EXIT_INTERNAL_ERROR` exits with emulation suberror and no assertion from the signal race.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_exception_with_invalid_guest_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_invalid_nested_guest_state.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_invalid_nested_guest_state.c

## Purpose
This nested VMX test verifies that if userspace makes L2 guest state invalid while L2 is stopped at an I/O exit, KVM reports the condition to L1 as a triple-fault VM-exit rather than trying unsupported invalid-state emulation for L2.

## Important APIs, Types, and Functions
Key functions are `l2_guest_code()` and `l1_guest_code()`. Host logic uses `vcpu_sregs_get()`, `vcpu_sregs_set()`, `struct kvm_sregs.tr.unusable`, VMX setup helpers, and `KVM_EXIT_IO` validation.

## Control Flow, State, and Persistence
L1 launches L2, which exits to L0 userspace through an `inb` at a fixed port. The host confirms the I/O exit, marks TR unusable in vCPU sregs, and resumes. L1 expects VMX exit reason `EXIT_REASON_TRIPLE_FAULT` and signals done. State is nested VMCS state, L2 special registers, and one userspace I/O exit.

## Dependencies and Integration Points
It requires VMX and the selftests VMX helper framework. It integrates with KVM nested guest-state validation and triple-fault injection into L1.

## Risks and Test Signals
Risks include attempting invalid-state emulation for L2, wrong VM-exit reason, or state corruption after userspace changes sregs. Passing signal is L1 `UCALL_DONE` after reading `EXIT_REASON_TRIPLE_FAULT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_invalid_nested_guest_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_msrs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_msrs_test.c

## Purpose
This test validates KVM ownership and validation of VMX control MSRs and `IA32_FEATURE_CONTROL`. It checks that KVM restores owned fixed bits where appropriate and rejects unsupported feature-control bits.

## Important APIs, Types, and Functions
Important helpers are `vmx_fixed1_msr_test()`, `vmx_fixed0_msr_test()`, `vmx_fixed0and1_msr_test()`, `vmx_save_restore_msrs_test()`, `__ia32_feature_control_msr_test()`, and `ia32_feature_control_msr_test()`. It uses `vcpu_get_msr()`, `vcpu_set_msr()`, `_vcpu_set_msr()`, VMX MSR constants, `FEAT_CTL_*` bits, CPUID feature mutation helpers, and bitmap iteration macros.

## Control Flow, State, and Persistence
The test creates one vCPU without guest code. It tries clearing fixed-1 bits and setting fixed-0 bits across VMX control MSRs, expecting KVM to accept writes through selftests helpers and normalize/restore as required. It toggles feature-control bits while related CPUID features are hidden or exposed, then iterates unsupported bits and expects writes to fail. State is the vCPU's synthetic VMX MSR set and CPUID feature model.

## Dependencies and Integration Points
It requires VMX and `KVM_CAP_DISABLE_QUIRKS2`. It integrates with VMX MSR virtualization, KVM quirks around tweaking VMX control MSRs, feature-control lock semantics, and CPUID dependency enforcement.

## Risks and Test Signals
Risks include KVM allowing reserved feature-control bits, failing to preserve owned VMX capabilities, or mishandling CPUID-dependent bits. Signals are successful normalization writes and expected `_vcpu_set_msr()` failures for unsupported reserved bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_msrs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_nested_la57_state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_nested_la57_state_test.c

## Purpose
This test validates nested VMX state save/restore when L1 uses 5-level paging and L2 uses 4-level paging. It targets canonical-address checks around state whose validity depends on CR4.LA57.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code()`, and `guest_code()`. The test uses `LA57_GS_BASE`, `MSR_GS_BASE`, `GUEST_CR3`, `GUEST_CR4`, `X86_CR4_LA57`, `vcpu_save_state()`, `vcpu_load_state()`, and `virt_map()` of the PML5 page.

## Control Flow, State, and Persistence
L1 writes GS_BASE to a value canonical only with LA57 enabled, prepares VMX, points L2 CR3 at L1's first PML4, clears L2 CR4.LA57, and launches L2. L2 syncs with host while active, causing host save/release/recreate/load of vCPU state, then resumes and exits via VMCALL. State includes L1 5-level page tables, L2 4-level CR3/CR4, nested VMCS, and GS_BASE.

## Dependencies and Integration Points
It requires VMX, LA57 support, and `KVM_CAP_NESTED_STATE`. It integrates with KVM canonical-address modeling, nested VMX state serialization, and page-table identity mapping.

## Risks and Test Signals
Risks include checking L1 state with L2 LA57 rules, rejecting valid GS_BASE on restore, or corrupting nested CR3/CR4 state. Signals are successful restore while L2 is active and final `UCALL_DONE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_nested_la57_state_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_pmu_caps_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_pmu_caps_test.c

## Purpose
This test validates virtualization of `MSR_IA32_PERF_CAPABILITIES` for VMX/vPMU guests. It checks guest write rejection, host-controlled immutability after run, fungible versus immutable feature bits, LBR behavior, and PDCM/PMU CPUID dependencies.

## Important APIs, Types, and Functions
Key data is `union perf_capabilities host_cap`, `immutable_caps`, and `format_caps`. Important tests are `guest_wrmsr_perf_capabilities`, `basic_perf_capabilities`, `fungible_perf_capabilities`, `immutable_perf_capabilities`, `lbr_perf_capabilities`, and `perf_capabilities_unsupported`. It uses `kvm_get_feature_msr()`, `vcpu_set_msr()`, `_vcpu_set_msr()`, `vcpu_clear_cpuid_feature()`, `vcpu_clear_cpuid_entry()`, `MSR_LBR_TOS`, and guest `wrmsr_safe()`.

## Control Flow, State, and Persistence
`main()` requires enabled PMU, PDCM, and nonzero PMU version, then captures host PERF_CAPABILITIES. Guest code attempts to write the current value, zero, and every single-bit variation and expects #GP. Host tests set supported values before first run, verify values remain unchanged after guest execution, reject changes after KVM_RUN, allow fungible features within host support, reject immutable/reserved LBR and PEBS formats, and verify disabling PMU/PDCM clears or rejects dependent state. State is vCPU PERF_CAPABILITIES MSR, CPUID PMU/PDCM model, and LBR MSRs.

## Dependencies and Integration Points
It integrates with vPMU exposure, VMX performance capability MSR virtualization, CPUID feature filtering, LBR MSR availability, and the KVM one-vCPU harness.

## Risks and Test Signals
Risks include allowing guest writes, accepting impossible LBR/PEBS formats, failing to clear capabilities without PDCM, or allowing LBR writes after vPMU removal. Signals are guest #GPs, exact host MSR readback, and expected `_vcpu_set_msr()` failures for invalid capability values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_pmu_caps_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_preemption_timer_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_preemption_timer_test.c

## Purpose
This nested VMX migration-style test verifies that VMX preemption timer state is saved and restored with the decayed timer value, not restarted from the original value after restore.

## Important APIs, Types, and Functions
Important functions are `l2_guest_code()`, `l1_guest_code()`, and `guest_code()`. The test uses `VMX_PREEMPTION_TIMER_VALUE`, `PIN_BASED_VMX_PREEMPTION_TIMER`, `VM_EXIT_SAVE_VMX_PREEMPTION_TIMER`, `MSR_IA32_VMX_MISC` timer rate, `vcpu_save_state()`, and `vcpu_load_state()`.

## Control Flow, State, and Persistence
L1 verifies preemption timer controls are supported, runs L2 once to a VMCALL, enables the preemption timer with a large value, records TSC-derived deadlines, and resumes L2. L2 waits until a threshold has elapsed, syncs to host to force save/release/recreate/load, then spins until the preemption timer exits to L1. L1 reports observed finish times and deadlines to host; host validates the timer did not expire too early from L1's perspective and did not restart too late from L2's perspective. State is nested VMCS preemption-timer value, saved x86 nested state, and timing globals.

## Dependencies and Integration Points
It requires VMX and `KVM_CAP_NESTED_STATE`, and integrates with VMX timer controls, nested-state migration, TSC timing, and KVM x86 state serialization.

## Risks and Test Signals
Risks include restoring the original timer instead of decayed value, losing timer-save control state, or timing flakiness. Signals are L2 reaching save/restore before expiry, `EXIT_REASON_PREEMPTION_TIMER`, and deadline comparisons passing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/vmx_preemption_timer_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_ipi_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_ipi_test.c

## Purpose
This stress test validates xAPIC IPI delivery to a halted vCPU, optionally while userspace pages are migrated across NUMA nodes. It targets APIC access page relocation and wake-from-HLT behavior.

## Important APIs, Types, and Functions
Important data is `struct test_data_page` and `struct thread_params`. Key functions are `halter_guest_code()`, `sender_guest_code()`, `guest_ipi_handler()`, `vcpu_thread()`, `do_migrations()`, `cancel_join_vcpu_thread()`, and `get_cmdline_args()`. It uses xAPIC register helpers, `migrate_pages()`, `kvm_get_mempolicy()`, pthread cancellation, `virt_pg_map(APIC_DEFAULT_GPA)`, and vCPU stats such as `halt_exits`.

## Control Flow, State, and Persistence
The host starts a halter vCPU that enables xAPIC, records APIC diagnostics, then repeatedly disables interrupts, increments `hlt_count`, executes safe HLT, and increments `wake_count`. After the first halt, a sender vCPU repeatedly writes ICR2/ICR to send fixed IPIs and waits for IPI, wake, and re-halt counters to advance. The host either sleeps for the configured runtime or repeatedly migrates process pages between NUMA nodes, then cancels both vCPU threads and validates HLT exit accounting. State is shared guest data page counters, global `ipis_rcvd`, APIC ICR state, migration counters, and KVM vCPU stats.

## Dependencies and Integration Points
It integrates with xAPIC MMIO/APIC access page mapping, HLT wakeup, APIC interrupt delivery, optional NUMA page migration, pthreads, and KVM statistics.

## Risks and Test Signals
Risks include hangs if IPIs are lost, false failures on single-node NUMA when migration is requested, APIC access backing page relocation bugs, and idle-HLT stat differences. Signals are continuously increasing IPI/HLT/wake counters, no guest abort, and halt-exit count matching or not exceeding HLT count under idle-HLT rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_ipi_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_state_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_state_test.c

## Purpose
This test validates xAPIC/x2APIC LAPIC state behavior for ICR writes and APIC ID transitions. It checks reserved bits, readback semantics, destination encodings, and KVM's xAPIC/x2APIC APIC_ID formatting ABI.

## Important APIs, Types, and Functions
Important data is `struct xapic_vcpu`. Key functions are `xapic_guest_code()`, `x2apic_guest_code()`, `____test_icr()`, `__test_icr()`, `test_icr()`, `test_apic_id()`, and `test_x2apic_id()`. It uses `KVM_GET_LAPIC`, `KVM_SET_LAPIC`, `MSR_IA32_APICBASE`, `KVM_CAP_X2APIC_API`, xAPIC/x2APIC register helpers, and APIC ICR constants.

## Control Flow, State, and Persistence
The x2APIC guest reads values from IRR, writes them to ICR, and expects faults for reserved x2APIC bits. The xAPIC guest writes split ICR2/ICR and syncs the value. Host code stuffs arbitrary ICR values into IRR via `KVM_SET_LAPIC`, runs the guest, reads ICR back, and compares expected masks while accounting for AMD AVIC errata. Additional tests toggle APICBASE between xAPIC and x2APIC and verify APIC_ID formatting, then try to set x2APIC ID through LAPIC state and expect KVM to ignore it. State is LAPIC register image, APICBASE mode, CPUID x2APIC exposure, and AVIC behavior.

## Dependencies and Integration Points
It integrates with KVM LAPIC get/set ioctls, xAPIC and x2APIC register semantics, APICBASE transitions, `KVM_X2APIC_API_USE_32BIT_IDS`, and AMD AVIC quirks.

## Risks and Test Signals
Risks include accepting reserved x2APIC ICR bits, preserving illegal APIC IDs, incorrect BUSY bit behavior, or mishandling ICR destination fields. Signals are exact ICR readbacks under mode-specific masks and APIC_ID matching vCPU ID in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_state_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_tpr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_tpr_test.c

## Purpose
This test validates APIC Task Priority Register behavior in both xAPIC and x2APIC modes, including synchronization between LAPIC TPR, PPR, and CR8 and interrupt masking/unmasking based on priority.

## Important APIs, Types, and Functions
Important functions are `tpr_guest_code()`, `tpr_guest_irq_queue()`, `tpr_guest_check_tpr_ppr_cr8_equal()`, `test_tpr_check_tpr_zero()`, `test_tpr_check_tpr_cr8_equal()`, `test_tpr_set_tpr_for_irq()`, and `test_tpr()`. It uses atomic guest counters, xAPIC/x2APIC EOI handlers, `KVM_GET_LAPIC`, `KVM_SET_LAPIC`, `vcpu_sregs_get()`, and APIC priority macros.

## Control Flow, State, and Persistence
For each APIC mode, the guest disables interrupts, enables APIC, verifies reset TPR is zero and equals PPR/CR8, queues a self-IPI, verifies it is masked by IF=0, enables interrupts and observes delivery, syncs to host to raise TPR enough to mask the next IRQ, then syncs again to lower TPR and observes pending IRQ delivery. Host services syncs by editing LAPIC TPR through `KVM_SET_LAPIC` and checks CR8/TPR equality. State is APIC mode flag, guest interrupt counter, LAPIC TPR/PPR, CR8, and pending self-IPI.

## Dependencies and Integration Points
It integrates with LAPIC state ioctls, CR8/sregs ABI, xAPIC MMIO mapping, x2APIC MSR mode, interrupt priority masking, and APIC EOI.

## Risks and Test Signals
Risks include TPR/CR8 divergence, wrong PPR computation, pending IRQ lost while masked, or mode-specific APIC behavior differences. Signals are guest counter transitions 0 to 1 to 2 and host assertions that CR8 equals LAPIC TPR at every sync.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xapic_tpr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xcr0_cpuid_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xcr0_cpuid_test.c

## Purpose
This test validates that KVM exposes a sane guest XCR0/CPUID xfeature model. It checks architectural dependencies among XSAVE features and rejects enabling unsupported XCR0 bits.

## Important APIs, Types, and Functions
Important macros are `ASSERT_XFEATURE_DEPENDENCIES` and `ASSERT_ALL_OR_NONE_XFEATURE`. `guest_code()` uses `set_cr4(OSXSAVE)`, `xgetbv(0)`, `this_cpu_supported_xcr0()`, `xsetbv_safe()`, feature masks for FP/SSE/YMM/MPX/AVX512/AMX, and guest assertions.

## Control Flow, State, and Persistence
`main()` requires XSAVE, creates one vCPU, and runs until `GUEST_DONE`. The guest enables OSXSAVE, compares initial XCR0 against supported XCR0, validates dependency/all-or-none rules, successfully sets XCR0 to FP-only and then all supported bits, and iterates all unsupported bit positions expecting #GP if any unsupported bit is added. State is guest CR4.OSXSAVE, XCR0, and CPUID-derived supported xfeature mask.

## Dependencies and Integration Points
It integrates with KVM CPUID xfeature enumeration, XSETBV emulation/hardware execution, CR4.OSXSAVE handling, and XSAVE feature masks.

## Risks and Test Signals
Risks include advertising incoherent xfeature sets, initializing XCR0 to a value unusable by the guest, or allowing unsupported bits. Signals are guest dependency assertions, successful supported `XSETBV`, and `#GP` for every unsupported bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xcr0_cpuid_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_shinfo_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_shinfo_test.c

## Purpose
This large Xen HVM selftest validates KVM's Xen shared-info, vCPU info, runstate, event-channel, timer, hypercall, poll, and clock integration. It also stress-tests shared-info cache locking while event delivery and polling race with host attribute updates.

## Important APIs, Types, and Functions
Important guest-side structures mirror Xen ABI layout: `struct shared_info`, `struct vcpu_info`, `struct pvclock_vcpu_time_info`, `struct pvclock_wall_clock`, `struct vcpu_runstate_info`, `struct compat_vcpu_runstate_info`, `struct evtchn_send`, and `struct sched_poll`. Key functions are `evtchn_handler()`, `guest_wait_for_irq()`, `guest_code()`, `juggle_shinfo_state()`, and `handle_alrm()`. Host code uses `KVM_CAP_XEN_HVM`, `KVM_XEN_HVM_CONFIG`, `KVM_XEN_HVM_SET_ATTR`, `KVM_XEN_VCPU_SET_ATTR`, `KVM_XEN_HVM_EVTCHN_SEND`, `KVM_SET_GSI_ROUTING`, irqfd/eventfd, Xen hypercall interception, and `KVM_GET_CLOCK`.

## Control Flow, State, and Persistence
`main()` detects Xen HVM capability flags, creates a VM, maps a three-page shared-info region, configures Xen long mode, shared-info via GPA or HVA, vCPU info, pvclock info, upcall vector, optional runstate, IRQ routes, eventfds, and a Xen timer port. The guest executes a long staged script: host-injected upcall vector, runstate current/adjust/data checks, steal-time generation, masked and unmasked event-channel delivery, slow paths after memslot changes, ioctl-based event send, guest `EVTCHNOP_send` hypercalls, eventfd-backed event channels, one-shot timer setup/restore/past-expiry tests, `SCHEDOP_poll` ready/timeout/masked/wake paths, vCPU-info HVA setup, and shared-info locking races. The host loop handles each sync by mutating shared info, setting attributes, writing eventfds, arming timers, or checking expected IRQ delivery. After the guest finishes, the host resets event channels, sanity-checks Xen wallclock and pvclock versions against `KVM_GET_CLOCK`, and exercises runstate writes across a page boundary in both compatibility and long mode.

## Dependencies and Integration Points
The test integrates with the KVM Xen HVM ABI, shared-info caching by GFN/HVA, event-channel routing and irqfd, Xen hypercall interception for `event_channel_op`, `sched_op`, and `set_timer_op`, vCPU runstate accounting, pvclock/wallclock generation, memslot invalidation slow paths, pthread cancellation, alarms for timeout diagnostics, and host scheduler run-delay observation.

## Risks and Test Signals
Risks include stale shared-info mappings after HVA remap or memslot changes, lost event-channel interrupts, incorrect pending/mask bits, timer IRQ drops while shinfo is invalid, runstate structure overruns at page boundaries, clock version instability, and lock corruption under concurrent shared-info attr updates. Signals are every staged `GUEST_SYNC`, `TEST_GUEST_SAW_IRQ` only when expected, successful poll/timer wake behavior, sane pvclock/wallclock versions, runstate sums matching state-entry time, and clean completion of shared-info race threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_shinfo_test.c -->
