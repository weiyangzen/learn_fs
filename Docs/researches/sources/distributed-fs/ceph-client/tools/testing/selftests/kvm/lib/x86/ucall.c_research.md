<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/ucall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/ucall.c

## Purpose
`ucall.c` is the x86 backend for KVM selftest ucalls. It implements the guest exit mechanism using PIO from a fixed port and extracts the guest-provided ucall pointer from vCPU registers on the host.

## Important APIs, Types, and Functions
The file defines `UCALL_PIO_PORT` as `0x1000`, `ucall_arch_do_ucall()`, and `ucall_arch_get_ucall()`. The guest path passes the ucall pointer in RDI and executes `in` from the port. The host path checks `KVM_EXIT_IO` and the port, then reads RDI via `vcpu_regs_get()`.

## Control Flow
Guest code saves nonvolatile registers plus RDX/RDI, performs the PIO instruction, and restores registers. The extra save/restore is a nested-VMX workaround because L2 ucalls may exit to L1, which can clobber registers before returning. Host code returns NULL for non-ucall exits.

## State and Persistence
No persistent state is stored. The PIO exit and RDI pointer are transient communication state between guest and host.

## Dependencies and Integration Points
The file depends on `kvm_util.h`, x86 PIO behavior, and common ucall code in `ucall_common.c`. It integrates with every x86 guest selftest using `GUEST_SYNC`, `GUEST_DONE`, `GUEST_PRINTF`, or `GUEST_ASSERT`.

## Risks and Test Signals
Risks include port conflicts, register clobbering in nested guests, missing KVM I/O completion, and returning an invalid guest pointer. Test signals are host `get_ucall()` receiving expected commands and nested tests preserving guest registers across ucalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/x86/ucall.c -->
