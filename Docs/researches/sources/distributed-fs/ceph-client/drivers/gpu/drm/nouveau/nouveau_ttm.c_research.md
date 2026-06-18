# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_ttm.c

## Purpose
This file initializes and tears down Nouveau's TTM memory managers for VRAM and GART/system memory. It bridges Nouveau memory objects into TTM resource-manager callbacks and records NVIF memory type indices needed by BO placement and mapping.

## Important APIs, Types, and Functions
Resource managers are exposed as `nouveau_vram_manager`, `nouveau_gart_manager`, and `nv04_gart_manager`. Main lifecycle functions are `nouveau_ttm_init` and `nouveau_ttm_fini`. Internal helpers initialize host types, VRAM manager, GTT manager, and their finalizers.

## Control Flow
Initialization first discovers coherent and non-coherent host memory types, optional kind-aware host memory, and a mappable VRAM type for Tesla+ non-SoC devices. It initializes `ttm_device`, records AGP bridge data, reserves BAR1 WC memory type, installs a VRAM manager, adds an MTRR/WC mapping, computes GART size from the client VMM or AGP aperture, installs the TT manager, initializes IO reserve state, and logs available memory. Finalization evicts and removes VRAM/GTT managers, finalizes TTM, and releases WC/MTRR reservations.

## State and Persistence Behavior
Persistent driver state includes `drm->ttm.bdev`, `type_host`, `type_ncoh`, `type_vram`, AGP details, TTM resource managers, IO reserve lists, MTRR handle, and GEM available memory counters. Resource allocation callbacks create `nouveau_mem` objects and, for old GART, reserve VMM PTEs.

## Dependencies and Integration Points
It depends on TTM device/resource-manager APIs, Nouveau memory allocation (`nouveau_mem_*`), NVIF MMU type discovery, BAR1 resource helpers, PCI/AGP information, and architecture WC/MTRR functions.

## Risks
Initialization failure paths after partial setup must avoid leaking managers or WC reservations. Wrong memory type discovery causes BO placement failures. Old pre-Tesla GART allocation reserves GPU VA in the client VMM and must be paired with memory finalization.

## Test Signals
Signals include module load/unload on pre-Tesla, Tesla+, AGP, SoC, and SWIOTLB/DMA32 systems; VRAM/GART BO allocation and eviction; BAR1 WC reservation cleanup; and memory-type discovery failures.
