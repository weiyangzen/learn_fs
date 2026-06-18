# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/driver.c

## Purpose

This file implements the native `/dev/sgx_enclave` misc device. It allocates per-file enclave objects, validates mmap permissions, dispatches ioctls, and registers the enclave device after SGX launch-control and SGX1 capabilities are confirmed.

## Important APIs, Types, And Functions

Global masks `sgx_attributes_reserved_mask`, `sgx_xfrm_reserved_mask`, and `sgx_misc_reserved_mask` constrain enclave attributes. Core functions are `sgx_open()`, `sgx_release()`, `sgx_mmap()`, `sgx_get_unmapped_area()`, optional `sgx_compat_ioctl()`, and `sgx_drv_init()`. The file defines `sgx_encl_fops` and miscdevice `sgx_dev_enclave`.

## Control Flow

Open increments SGX usage, allocates and initializes `struct sgx_encl`, xarray, mutexes, VA/MM lists, spinlock, and SRCU. Release drains remaining mm-notifier records, unregisters notifiers, and drops enclave references. mmap validates requested VMA permissions with `sgx_encl_may_map()`, adds the mm to the enclave, and installs SGX VM ops with PFNMAP/IO/DONTDUMP flags. Init queries SGX CPUID leaves for supported attributes/misc/xfrm bits and registers the device only if launch control and SGX1 are available.

## State, Dependencies, And Integration

State persists per open file in `file->private_data`. Device registration is boot-lifetime. Dependencies include miscdevice, mmu notifiers, mmap flags, CPU SGX CPUID data, LSM/security attribute handling through ioctl paths, and SGX core usage accounting.

## Risks And Test Signals

Release ordering must avoid mm-notifier and SRCU lifetime races. Attribute masks must match CPUID or invalid enclaves may be accepted. mmap permissions are security-sensitive. Test by opening/closing devices, mmap/fork/exit races, invalid MAP_PRIVATE use, attribute-mask validation, and running SGX SDK enclave create/add/init flows.
