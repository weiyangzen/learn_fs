# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/main.c

## Purpose

This file is the SGX EPC page-cache core. It discovers EPC sections, maps them, manages NUMA free lists and poisoned pages, runs the `ksgxd` reclaimer/sanitizer, handles EPC memory failures, registers provisioning support, updates launch-key hash MSRs, tracks active SGX users for EUPDATESVN, and initializes native/KVM SGX devices.

## Important APIs, Types, And Functions

Important globals are `sgx_epc_sections[]`, `sgx_epc_address_space`, `sgx_active_page_list`, `sgx_nr_free_pages`, `sgx_numa_mask`, `sgx_numa_nodes`, and `sgx_dirty_page_list`. Public APIs include `__sgx_alloc_epc_page()`, `sgx_alloc_epc_page()`, `sgx_free_epc_page()`, `sgx_reclaim_direct()`, `sgx_mark_page_reclaimable()`, `sgx_unmark_page_reclaimable()`, `current_is_ksgxd()`, `arch_is_platform_page()`, `arch_memory_failure()`, `sgx_update_lepubkeyhash()`, `sgx_set_attribute()`, `sgx_inc_usage_count()`, and `sgx_dec_usage_count()`.

## Control Flow

`sgx_init()` checks SGX, enumerates EPC CPUID sections, maps EPC with `memremap()`, allocates `sgx_epc_page` arrays, sanitizes dirty pages through EREMOVE, starts `ksgxd`, registers `/dev/sgx_provision`, and tries both native and vEPC drivers. Allocation prefers the caller's NUMA node, can reclaim when allowed, and wakes `ksgxd` below watermarks. Reclaim ages pages via PTE accessed bits, allocates shmem backing, marks pages being reclaimed, EBLOCKs/zaps PTEs, EWB-writes EPC contents/PCMD, and frees EPC pages. Memory failure maps physical EPC addresses back to `sgx_epc_page` and quarantines poison.

## State, Dependencies, And Integration

State is boot-lifetime EPC section metadata and runtime lists protected by per-node locks and `sgx_reclaimer_lock`. Dependencies include CPUID SGX EPC leaves, ENCLS, NUMA, xarray, miscdevice, kthreads/freezer, shmem/highmem, memory-failure, RDRAND retry constants for EUPDATESVN, and KVM export symbols. It integrates with `encl.c` and `virt.c` through EPC allocation, reclaimability, and launch-control MSR updates.

## Risks And Test Signals

Risks include reclaim races, poisoned EPC handling, SECS/child ordering, deadlocks if direct reclaim is called with mm/enclave locks held, failure cleanup after partially mapped sections, and usage-count mistakes around EUPDATESVN. Test EPC discovery on NUMA systems, kexec sanitization, EPC pressure reclaim, memory failure injection for EPC pages, provisioning fd validation, native and KVM device registration, and EUPDATESVN retry/error paths.
