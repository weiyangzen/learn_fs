# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo9039.c

Purpose: Provides Fermi `NV9039` M2MF buffer copy support and object initialization for BO migration.

Important APIs/functions: `nvc0_bo_move_m2mf()` emits copy method sequences; `nvc0_bo_move_init()` binds the object handle.

Control flow: The copy path reads prepared source/destination VMAs from `nouveau_mem(old_reg)`, loops over page batches up to 2047 pages, programs destination and source offsets, page pitches, line length/count, and issues `LAUNCH_DMA` with pitch-to-pitch layout, no interrupt, no completion flush, and one-word semaphore struct size.

State/persistence: Stateless except channel push state. It relies on the BO core's temporary VMA preparation and fence cleanup.

Dependencies/integration: Chosen from `nouveau_bo_move_init()` for class `0x9039`. Depends on `nvif/push906f.h` and `cl9039.h`.

Risks/test signals: LAUNCH flags control synchronization behavior and must pair correctly with the BO core's explicit fence wait. Test with Fermi M2MF migration, multi-batch large BOs, GPU fault/reset injection, and software-copy fallback when method submission fails.
