# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo85b5.c

Purpose: Implements NVA3-class DMA copy engine support for BO migration.

Important APIs/functions: `nva3_bo_move_copy()` copies page-sized lines from source to destination VMA addresses using the `NV85B5` push interface. A comment notes class compatibility with NVIDIA/Kepler DMA copy is not fully normalized.

Control flow: The function computes source/destination offsets from prepared memory VMAs, converts the destination size to page count, then loops in batches of at most 8191 pages. Each batch emits source/destination upper/lower addresses, input/output pitches, line length, line count, and a launch/control word.

State/persistence: Stateless besides channel push cursor and memory VMA addresses.

Dependencies/integration: Selected by BO core for class `0x85b5`. Depends on `nouveau_bo.h`, `nouveau_dma.h`, `nouveau_mem.h`, and `nvif/push206e.h`.

Risks/test signals: Batch limits and raw method offsets must match the class. The function assumes page-granular copy and does not explicitly handle sub-page tails, relying on TTM resource sizing. Test on NVA3/NVAF hardware with large migrations, VRAM-to-VRAM and TT/VRAM paths, and fence completion under GPU reset or channel kill.
