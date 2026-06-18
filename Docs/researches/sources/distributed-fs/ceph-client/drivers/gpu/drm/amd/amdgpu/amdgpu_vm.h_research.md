# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.h

## Purpose

This header defines AMDGPU GPUVM data structures, page table bit encodings, VM manager state, update backends, lifecycle APIs, mapping APIs, and helper macros. It is the contract shared by VM core code, page-table walkers, CPU/SDMA update implementations, TLB-fence code, submission paths, KFD, and fault handlers.

## Important APIs, types, and functions

Important constants include `AMDGPU_VM_MAX_UPDATE_SIZE`, `AMDGPU_VM_PTE_COUNT()`, PTE/PDE flag bits (`AMDGPU_PTE_VALID`, `SYSTEM`, `SNOOPED`, `TMZ`, `READABLE`, `WRITEABLE`, `PRT`, `TF`, `NOALLOC`, `IS_PTE`), mtype macros for GFX9/GFX10/GFX12, `AMDGPU_VM_NORETRY_FLAGS`, VM fault-stop modes, reserved VA ranges, VM update mode bits, VMHUB indices, and `enum amdgpu_vm_level`. Core types include `struct amdgpu_vm_bo_base`, `struct amdgpu_vm_pte_funcs`, `struct amdgpu_vm_update_params`, `struct amdgpu_vm_update_funcs`, `struct amdgpu_vm_fault_info`, `struct amdgpu_mem_stats`, `struct amdgpu_vm`, and `struct amdgpu_vm_manager`. It declares the CPU and SDMA update function tables plus all exported VM, mapping, page-table, fault, and debug APIs.

## Control flow, state, and persistence behavior

The header encodes the main state model. `struct amdgpu_vm` owns the VA interval tree, eviction lock, status lock, memory stats, BO state lists, freed mappings, root page directory, update entities, TLB sequence/fences, generation token, PASID, reserved VMIDs, update backend selection, fault FIFO, KFD process linkage, task info, LRU bulk move data, compute/TLB-fence flags, memory partition id, and cached fault info. `struct amdgpu_vm_manager` stores device-wide VMID managers, address-space sizing, page-table format, PTE writer functions, PTE schedulers, PRT state, update-mode policy, PASID XArray, and global fault info. Inline helpers expose `amdgpu_vm_tlb_seq()` and eviction lock/unlock wrappers that use `memalloc_noreclaim_save()` to avoid reclaim-FS deadlocks from MMU notifiers.

## Dependencies and integration points

The header depends on Linux IDR/KFIFO/RB-tree/sched-mm, DRM scheduler/file/TTM BO types, and AMDGPU sync/ring/ID/TTM headers. It integrates with `amdgpu_vm_pt.c`, `amdgpu_vm_cpu.c`, `amdgpu_vm_sdma.c`, `amdgpu_vm_tlb_fence.c`, ring submission code, KFD, debugfs, and user IOCTL handling. The update abstraction is the key integration point: page-table code calls `vm->update_funcs`, while hardware-specific SDMA packet functions come through `adev->vm_manager.vm_pte_funcs`.

## Risks and test signals

Risks are ABI-like coupling across many VM users. Incorrect bit definitions can corrupt page tables, wrong list semantics can break update state machines, and lock helper misuse can deadlock with MMU notifiers. GFX12 flag differences and no-retry flag translations are especially sensitive. Test signals are full driver compile coverage, successful VM init/fini for graphics and compute contexts, correct page fault status reporting, KFD TLB flush behavior, and no lockdep complaints around eviction locks.
