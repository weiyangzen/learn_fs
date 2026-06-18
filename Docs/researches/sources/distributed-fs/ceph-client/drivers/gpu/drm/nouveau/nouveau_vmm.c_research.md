# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vmm.c

## Purpose
This file manages the older per-client Nouveau VMM and per-BO VMA references. It allocates GPU virtual address ranges, maps/unmaps `nouveau_mem`, shares mappings for repeated BO/VMM pairs, and destroys associated SVMM state during VMM teardown.

## Important APIs, Types, and Functions
Entry points are `nouveau_vma_new`, `nouveau_vma_del`, `nouveau_vma_find`, `nouveau_vma_map`, `nouveau_vma_unmap`, `nouveau_vmm_init`, and `nouveau_vmm_fini`.

## Control Flow
`nouveau_vma_new` first reuses an existing BO/VMM VMA and bumps refs. Otherwise it allocates a VMA, links it to the BO list, and either reserves a lazy mapped range for non-system memory with matching page size or reserves PTEs for deferred mapping. On failure it deletes the partially built VMA. `nouveau_vma_del` decrements refs, puts the NVIF VMA if allocated, unlinks, and frees. VMM init creates an unmanaged NVIF VMM; fini tears down SVM and the NVIF VMM.

## State and Persistence Behavior
Per-VMA state includes VMM pointer, refcount, BO list link, GPU VA, mapped `nouveau_mem`, and optional fence pointer. Per-VMM state includes client pointer, NVIF VMM object, and optional SVMM.

## Dependencies and Integration Points
It depends on NVIF VMM get/put/map/unmap, Nouveau BO resource state, Nouveau memory mapping, and SVM teardown. It is used by fence memory mapping and classic BO GPU VA management.

## Risks
Reference counting must match all callers or GPU VA ranges leak or are freed early. The lazy mapping path assumes resource memory page size matches BO page preference. `nouveau_vma_unmap` only clears `mem`, so callers must ensure VMM address lifetime is separately released.

## Test Signals
Signals include repeated VMA lookup/ref/drop, BO move map/unmap, fence BO mapping on nv84+, VMM teardown with SVM enabled, and error injection in `nvif_vmm_get`/`nouveau_mem_map`.
