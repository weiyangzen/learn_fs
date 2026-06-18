# sources/distributed-fs/ceph-client/arch/x86/mm/maccess.c

## Purpose
This file supplies the x86 policy for `copy_from_kernel_nofault_allowed()`, deciding whether a kernel no-fault read source address is permissible.

## Important APIs, Types, and Functions
- `copy_from_kernel_nofault_allowed(const void *unsafe_src, size_t size)` returns whether no-fault kernel copying may try the address.
- On x86_64 it rejects userspace plus the guard page, rejects vsyscall addresses, permits early boot before virtual-address width is initialized, and checks canonicality.
- On 32-bit it permits addresses at or above `TASK_SIZE_MAX`.

## Control Flow and State
The function is a pure policy check. x86_64 first compares the address against `TASK_SIZE_MAX + PAGE_SIZE`, then calls `is_vsyscall_vaddr()`, then handles early boot by checking `boot_cpu_data.x86_virt_bits`, and finally validates canonical address form. It does not persist state.

## Dependencies and Integration Points
It depends on uaccess, task-size constants, vsyscall address classification, and CPU virtual-address-width discovery. It is consumed by generic no-fault memory access helpers used by debugging, probing, and fault-tolerant kernel reads.

## Risks
Allowing userspace or vsyscall addresses can turn kernel no-fault reads into unsafe user access or unhandled faults. Rejecting too much during early boot can break early exception decoding before CPU address-width state is initialized. The `size` parameter is not used here, so callers must handle range overflow elsewhere.

## Test Signals
Tests should confirm rejection of userspace, guard-page, and vsyscall addresses; acceptance of canonical kernel addresses; and early-boot functionality in fault handlers. Fault-injection around no-fault copy helpers is useful.
