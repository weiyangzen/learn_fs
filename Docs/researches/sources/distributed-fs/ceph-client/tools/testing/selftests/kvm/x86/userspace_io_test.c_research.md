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
