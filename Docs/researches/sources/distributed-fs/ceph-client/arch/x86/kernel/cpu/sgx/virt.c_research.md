# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/virt.c

## Purpose

This file implements SGX virtualization support for KVM: `/dev/sgx_vepc`, virtual EPC mmap/fault allocation, cleanup of guest-owned EPC pages, a remove-all ioctl, and exported helpers for KVM to run ECREATE/EINIT on guest-provided pages.

## Important APIs, Types, And Functions

The private `struct sgx_vepc` owns an xarray of EPC pages and a mutex. Device functions include `sgx_vepc_open()`, `sgx_vepc_release()`, `sgx_vepc_mmap()`, `sgx_vepc_fault()`, and `sgx_vepc_ioctl()`. Cleanup helpers are `sgx_vepc_remove_page()`, `sgx_vepc_free_page()`, and `sgx_vepc_remove_all()`. Exported KVM APIs are `sgx_virt_ecreate()` and `sgx_virt_einit()`.

## Control Flow

vEPC faults allocate an EPC page owned by the vEPC file, store it by mmap page offset, and insert the EPC PFN into userspace. Release EREMOVE's all pages, handles SECS pages that still have children by retrying after child removal, and keeps cross-instance SECS pages on a protected zombie list until later releases can remove them. `SGX_IOC_VEPC_REMOVE_ALL` lets userspace attempt explicit removal and reports remaining SECS failures. KVM ECREATE/EINIT helpers validate user pointers, temporarily enable user access, execute ENCLS, return guest trap numbers for faults, and update launch-key hash MSRs when launch control is available.

## State, Dependencies, And Integration

State lives per vEPC file and in global zombie SECS list protected by `zombie_secs_pages_lock`. Dependencies include SGX EPC allocation/free, ENCLS wrappers, miscdevice, mmap PFN insertion, xarray, KVM export macros, and VMX feature detection. It integrates with KVM's SGX support and the global SGX usage count.

## Risks And Test Signals

Guest-owned EPC pages may be in arbitrary states, so cleanup must tolerate `SGX_CHILD_PRESENT` while warning on unexpected failures. Concurrent removal while vCPUs run can return busy. User-pointer handling in KVM ENCLS helpers is security-sensitive. Test KVM SGX guests, mmap/fault/unmap cycles, `SGX_IOC_VEPC_REMOVE_ALL` retries, cross-vEPC SECS-child ordering, and trapped guest ECREATE/EINIT success and fault injection.
