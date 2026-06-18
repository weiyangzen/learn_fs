# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_boa0b5.c

Purpose: Implements Kepler+ `NVA0B5` DMA copy support used by the BO migration method table.

Important APIs/functions: `nve0_bo_move_copy()` programs virtual source/destination offsets, pitches, line length/count, and `LAUNCH_DMA`; `nve0_bo_move_init()` binds the object handle through a push sequence.

Control flow: The move path waits for push space, writes upper/lower source and destination VMA addresses from `nouveau_mem(old_reg)->vma[0/1]`, uses page-sized pitch and line length, sets line count from `PFN_UP(new_reg->size)`, and launches a non-pipelined, flush-enabled, pitch-to-pitch virtual copy with no semaphore or interrupt.

State/persistence: Stateless except channel push state and the BO core's copy object lifetime.

Dependencies/integration: Preferred for many COPY/GRCE classes in `nouveau_bo_move_init()` from `0xa0b5` through newer class IDs. Depends on `nvif/push906f.h` and `cla0b5.h`.

Risks/test signals: The launch flags choose virtual addressing and no semaphore, so synchronization must come from the fence created by the BO core. Test on Kepler and newer GPUs, including copy-engine class fallback order, large migrations, compressed/kind memory, and GPU reset paths.
