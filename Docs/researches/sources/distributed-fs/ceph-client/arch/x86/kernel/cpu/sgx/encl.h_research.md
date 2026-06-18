# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.h

## Purpose

This header defines software data structures and function contracts for native SGX enclaves. It is the central model for enclave pages, enclave-wide state, mm tracking, VA pages, and backing storage.

## Important APIs, Types, And Functions

Important types are `struct sgx_encl_page`, `enum sgx_encl_flags`, `struct sgx_encl_mm`, `struct sgx_encl`, `struct sgx_va_page`, and `struct sgx_backing`. Important constants are `SGX_ENCL_PAGE_VA_OFFSET_MASK`, `SGX_ENCL_PAGE_BEING_RECLAIMED`, and `SGX_VA_SLOT_COUNT`. It declares `sgx_vm_ops`, lookup helper `sgx_encl_find()`, permission checks, backing helpers, page load/allocation helpers, VA page helpers, PTE zapping, and enclave grow/shrink functions.

## Control Flow

The header has only inline lookup flow: `sgx_encl_find()` checks whether an address belongs to a VMA using `sgx_vm_ops`. Other control is implemented in `encl.c`, `ioctl.c`, and `main.c`.

## State, Dependencies, And Integration

`struct sgx_encl` persists per open enclave device and owns the xarray of pages, SECS, backing file, VA pages, mm-list/SRCU, and refcount. The header depends on mm, mmu-notifier, list, mutex, xarray, and `sgx.h`. It integrates native driver, ioctl, fault, and reclaim code.

## Risks And Test Signals

Bit overlap between VA offset and `BEING_RECLAIMED` is intentional and requires careful checks. Structure fields are shared across locking domains. Test by compiling all SGX configurations and exercising page reclaim, VA slot allocation, mm notifier release, and SGX2 dynamic operations.
