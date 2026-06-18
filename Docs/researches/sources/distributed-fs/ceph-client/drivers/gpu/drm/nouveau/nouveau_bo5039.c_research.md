# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo5039.c

Purpose: Implements NV50 `NV5039` M2MF copy support for TTM BO migration, including pitch and blocklinear memory layout handling.

Important APIs/functions: `nv50_bo_move_m2mf()` performs the copy; `nv50_bo_move_init()` binds the copy object and notification/VRAM context DMA handles.

Control flow: The move path obtains temporary source and destination VMAs from `nouveau_mem(old_reg)->vma[0/1]`, copies up to 4 MiB per push sequence, derives a 64-byte stride and height, configures source and destination layouts based on each resource's `kind`, programs upper/lower offsets, pitches, line length/count, format, and buffer notify, then advances offsets and remaining length.

State/persistence: No local persistent state. It relies on `nouveau_bo_move_prep()` having mapped old/new memory into the temporary VMA slots before execution.

Dependencies/integration: Selected by the BO core for class `0x5039` on suitable channels. Depends on `nouveau_mem`, `nvif/push206e.h`, and `cl5039.h`. It bridges TTM resources to hardware copy engine push methods.

Risks/test signals: Tiled layout programming is sensitive to `kind`, block-size fields, and VMA preparation. Incorrect height/stride math could under-copy tail bytes if resource sizes are not aligned by TTM. Test with tiled and linear BO migration, large BOs over 4 MiB, TT/VRAM transitions, and fallback behavior if push waits fail.
