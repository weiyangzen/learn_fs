# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_cpu.c

## Purpose

This file implements the CPU-backed VM page-table update backend. It is selected for graphics or compute VMs when `vm_update_mode` requests CPU writes, usually on large-BAR systems where VRAM page tables are CPU-visible.

## Important APIs, types, and functions

The exported object is `amdgpu_vm_cpu_funcs`, a `struct amdgpu_vm_update_funcs`. Its methods are `amdgpu_vm_cpu_map_table()`, `amdgpu_vm_cpu_prepare()`, `amdgpu_vm_cpu_update()`, and `amdgpu_vm_cpu_commit()`.

## Control flow, state, and persistence behavior

`amdgpu_vm_cpu_map_table()` marks a page-table BO as CPU-access-required and kmap's it. `amdgpu_vm_cpu_prepare()` waits synchronously on an optional `amdgpu_sync`. `amdgpu_vm_cpu_update()` waits for kernel-usage fences on the target PD/PT reservation object, converts the page-entry byte offset to a CPU pointer, traces the operation, maps GART DMA addresses when `pages_addr` is supplied, and writes each entry with `amdgpu_gmc_set_pte_pde()`. `amdgpu_vm_cpu_commit()` increments the VM TLB sequence if needed, issues a memory barrier, and flushes HDP unless a reset is already holding the reset-domain semaphore. State changes are direct writes to CPU-mapped page-table memory plus TLB sequence updates.

## Dependencies and integration points

The backend depends on AMDGPU BO kmap helpers, DMA reservation waits, GMC PTE/PDE encoding, reset-domain locking, HDP flushing, and VM tracepoints. It is installed into `vm->update_funcs` by `amdgpu_vm_init()` or `amdgpu_vm_make_compute()`.

## Risks and test signals

Risks include using CPU update on systems without fully visible VRAM, missing synchronization with pending GPU page-table moves, stale HDP visibility, and long blocking waits in paths expecting asynchronous SDMA behavior. Test signals are successful compute VM conversion to CPU updates, no page faults after BO moves, correct TLB invalidation sequence increments, and no reset-time deadlocks around HDP flushing.
