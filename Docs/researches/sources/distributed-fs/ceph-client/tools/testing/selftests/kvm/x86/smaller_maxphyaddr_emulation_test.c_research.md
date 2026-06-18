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
