# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/loongarch/ucall.c

## Purpose
This LoongArch ucall backend uses an MMIO write exit to pass guest ucall payload pointers back to userspace.

## Important APIs, Types, and Functions
`ucall_arch_init()` maps a free guest virtual page to the selected MMIO GPA, records `vm->ucall_mmio_addr`, and writes guest global `ucall_exit_mmio_addr`. `ucall_arch_get_ucall()` recognizes `KVM_EXIT_MMIO` writes to that GPA and returns the pointer stored in MMIO data.

## Control Flow
Generic ucall setup calls init during VM construction. Guest code writes a u64 to the mapped MMIO page; host exit handling recognizes the physical address and extracts the payload.

## State, Dependencies, and Integration
State is per-VM MMIO GPA plus a guest global GVA. The code depends on generic virtual mapping and global writing helpers, matching the arm64 MMIO ucall pattern.

## Risks and Test Signals
Unexpected access direction or length asserts. Misconfigured mapping breaks `GUEST_SYNC()` and `GUEST_ASSERT()` delivery and typically appears as an unexpected KVM exit.
