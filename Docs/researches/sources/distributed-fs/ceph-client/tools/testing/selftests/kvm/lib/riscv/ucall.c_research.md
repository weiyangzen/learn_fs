# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/riscv/ucall.c

## Purpose
This RISC-V ucall backend uses KVM's RISC-V SBI exit path for guest-to-userspace selftest communication.

## Important APIs, Types, and Functions
`ucall_arch_get_ucall()` inspects `KVM_EXIT_RISCV_SBI` exits with extension `KVM_RISCV_SELFTESTS_SBI_EXT`. Function `KVM_RISCV_SELFTESTS_SBI_UCALL` returns the ucall pointer from SBI arg0. Function `KVM_RISCV_SELFTESTS_SBI_UNEXP` dumps vCPU state and fails the test.

## Control Flow
Guest code performs an SBI ecall through the selftest extension. Host exit handling checks extension and function IDs, extracts payloads for ordinary ucalls, or treats unexpected-trap notifications as hard failures.

## State, Dependencies, and Integration
There is no per-VM MMIO mapping state in this backend. It depends on RISC-V KVM SBI exit fields, `processor.h`, and generic `get_ucall()` integration.

## Risks and Test Signals
Wrong extension/function IDs return NULL and may look like an unexpected exit to callers. Unexpected traps produce immediate vCPU dump output and assertion failure.
