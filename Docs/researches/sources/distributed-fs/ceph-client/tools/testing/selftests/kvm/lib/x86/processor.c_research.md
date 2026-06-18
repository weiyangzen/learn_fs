<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/processor.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/processor.c

## Purpose
`processor.c` is the main x86 architecture backend for KVM selftests. It provides guest page table construction, nested TDP mapping, descriptor table setup, exception routing, vCPU creation and register initialization, CPUID/MSR utilities, save/restore of x86 vCPU state, hypercall helpers, address-space limits, SEV address properties, SMM setup, and architecture-wide initialization.

## Important APIs, Types, and Functions
Major APIs include `virt_arch_pgd_alloc()`, `__virt_pg_map()`, `virt_arch_pg_map()`, `virt_map_level()`, `vm_get_pte()`, `tdp_get_pte()`, `addr_arch_gva2gpa()`, `vm_enable_tdp()`, `tdp_mmu_init()`, `tdp_map()`, `tdp_identity_map_default_memslots()`, `tdp_identity_map_1g()`, `vm_install_exception_handler()`, `route_exception()`, `kvm_arch_vm_post_create()`, `vm_arch_vcpu_add()`, `vcpu_arch_set_entry_point()`, `vcpu_args_set()`, `kvm_get_supported_cpuid()`, `vcpu_init_cpuid()`, `vcpu_set_cpuid_property()`, `vcpu_set_or_clear_cpuid_feature()`, `vcpu_get_msr()`, `_vcpu_set_msr()`, `vcpu_save_state()`, `vcpu_load_state()`, `kvm_get_cpu_address_width()`, `kvm_init_vm_address_properties()`, `kvm_hypercall()`, `xen_hypercall()`, `vm_compute_max_gfn()`, `kvm_selftest_arch_init()`, `setup_smram()`, and `inject_smi()`.

## Control Flow
VM creation allocates page tables, an IRQ chip, GDT/IDT/TSS pages, exception handler arrays, CPUID, XCR0, SREGS, stack, and initial registers. Page mapping walks or creates multi-level PTEs, supports huge leaves, checks alignment and canonicality, and applies SEV/TDX C/S bits only to final stage-1 leaves. Exception stubs from `handlers.S` enter `route_exception()`, which dispatches installed handlers, fixes expected exception probes, or reports guest failure. State migration first completes pending I/O, then captures events, MP state, regs, XSAVE/XCRS, SREGS, nested state, MSRs, and debug regs; loading restores the same classes in KVM-compatible order.

## State and Persistence
The file maintains global host CPU vendor flags, forced-emulation state, guest TSC frequency, PMU errata, supported CPUID cache, and guest exception handler pointer. Per-VM state includes page-table roots, architecture bit masks, descriptor-table pages, TSS, handlers page, SEV fd and C/S-bit tags, and maximum GFN. Per-vCPU state includes CPUID caches and KVM register state.

## Dependencies and Integration Points
Dependencies include `kvm_util.h`, `processor.h`, `pmu.h`, `smm.h`, `svm_util.h`, `sev.h`, `vmx.h`, sparsebit tracking, KVM ioctls, x86 CPUID/MSR definitions, and the assembly IDT stubs. It is the integration layer between generic selftest VM APIs and x86-specific KVM ABI details.

## Risks and Test Signals
Risks are broad: incorrect PTE masks, mapping protected guests' page tables, stale CPUID after XCR/SREG changes, wrong descriptor entries, incomplete save/restore ordering, AMD HyperTransport address-hole mistakes, and SEV C-bit mishandling. Test signals include `TEST_ASSERT()`s on mapping validity, KVM ioctl return checks, guest exception reports, CPUID/MSR sanity checks, successful migration/save-restore tests, and architecture setup failures when required caps such as `KVM_GET_TSC_KHZ` are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/processor.c -->
