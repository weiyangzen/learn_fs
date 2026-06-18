# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encl.c

## Purpose

This file manages SGX enclave runtime objects below the ioctl layer: EPC page reload from backing storage, page faults, SGX2 dynamic page addition, VMA permission enforcement, debug access, mmu-notifier tracking, backing shmem pages, VA slots, PTE zapping, and enclave teardown.

## Important APIs, Types, And Functions

Public APIs include `sgx_encl_may_map()`, `sgx_encl_release()`, `sgx_encl_mm_add()`, `sgx_encl_cpumask()`, `sgx_encl_alloc_backing()`, `sgx_encl_put_backing()`, `sgx_encl_test_and_clear_young()`, `sgx_encl_page_alloc()`, `sgx_zap_enclave_ptes()`, `sgx_alloc_va_page()`, VA slot helpers, `sgx_encl_free_epc_page()`, and `sgx_encl_load_page()`. VM operations are `sgx_vm_ops`.

## Control Flow

Faults load existing enclave pages through ELDU or, on SGX2, dynamically allocate a new REG page with EAUG. ELDU pins shmem contents and PCMD pages, loads the EPC page, clears PCMD metadata, truncates no-longer-needed backing pages, and restores VA slots. VMA checks ensure requested mappings stay within declared page permissions and reject READ_IMPLIES_EXEC tasks. Debug access uses EDBGRD/EDBGWR only for debug enclaves. MMU notifier registration tracks all mms mapping the enclave so reclaimer and SGX2 operations can zap PTEs and compute CPU masks after ETRACK.

## State, Dependencies, And Integration

The enclave state is `struct sgx_encl`: xarray page map, SECS page, backing file, VA page list, mm list, SRCU, mm-list version, reference count, attributes, and flags. Backing storage is private shmem laid out as encrypted pages, SECS, and PCMD pages. Dependencies include ENCLS wrappers, shmem, mmu notifiers, SRCU/RCU, xarray, memcg charging, page-table walking, and SGX EPC allocation/reclaim.

## Risks And Test Signals

The highest risks are lifetime races with reclaim, mmu notifier teardown, PCMD truncation while reclaim writes, PTE zapping across forked mms, and correct lock ordering around `encl->lock` versus mmap locks. Test with SGX SDK workloads, EPC pressure/reclaim, fork/exit/mmap/mprotect races, SGX2 EAUG faults, debug enclave ptrace-like access, and teardown after partially built or heavily reclaimed enclaves.
