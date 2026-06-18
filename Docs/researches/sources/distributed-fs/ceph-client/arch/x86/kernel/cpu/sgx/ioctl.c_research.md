# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/ioctl.c

## Purpose

This file implements the `/dev/sgx_enclave` ioctl API for enclave lifecycle and SGX2 dynamic management: create, add pages, initialize, authorize provisioning, restrict permissions, modify page types, and remove accepted trimmed pages.

## Important APIs, Types, And Functions

The public dispatcher is `sgx_ioctl()`. Key helpers are `sgx_encl_grow()`, `sgx_encl_shrink()`, `sgx_encl_create()`, `sgx_ioc_enclave_create()`, `sgx_validate_secinfo()`, `sgx_encl_add_page()`, `sgx_ioc_enclave_add_pages()`, `sgx_encl_init()`, `sgx_ioc_enclave_init()`, `sgx_ioc_enclave_provision()`, `sgx_enclave_etrack()`, and SGX2 ioctl handlers for permission/type/remove flows.

## Control Flow

`sgx_ioctl()` serializes ioctl execution with `SGX_ENCL_IOCTL`. Create copies SECS, allocates backing/SECS/VA resources, runs ECREATE, and records base, size, attributes, and debug flag. Add-pages validates source/offset/length/SECINFO, allocates enclave/EPC/VA pages, inserts xarray entries before irreversible EADD/EEXTEND, and reports partial progress. Init validates attributes and SIGSTRUCT masks, computes MRSIGNER, updates launch-control MSRs, retries EINIT around unmasked events, and marks the enclave initialized. SGX2 operations require initialized SGX2 enclaves, load pages, run EMODPR/EMODT/ETRACK, zap PTEs when needed, and remove pages only after enclave-side EACCEPT of TRIM.

## State, Dependencies, And Integration

The file mutates `struct sgx_encl` flags, page count, page xarray, VA pages, backing file, SECS child count, attributes mask, and page metadata. Dependencies include UAPI ioctl structs, ENCLS wrappers, shmem-backed storage, mmap locks, user-copy helpers, SHA-256 for MRSIGNER, provisioning file descriptors, and core EPC allocation/reclaim.

## Risks And Test Signals

This is a security boundary. Risks include accepting invalid permissions, mishandling partial progress, losing xarray/backing consistency after irreversible EADD/EEXTEND, lock-order bugs around PTE zapping, and failure to serialize ETRACK-dependent operations. Test native SGX SDK lifecycle, invalid SECINFO/SIGSTRUCT/misc/xfrm inputs, signal interruption during add/init, provisioning authorization, SGX2 permission/type/remove workflows, and concurrent ioctl attempts.
