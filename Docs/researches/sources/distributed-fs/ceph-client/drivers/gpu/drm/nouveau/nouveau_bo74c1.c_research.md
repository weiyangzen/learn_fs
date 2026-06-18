# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo74c1.c

Purpose: Provides an NV84-era copy path using the `NV74C1` engine, labelled CRYPT in the BO move method table.

Important APIs/functions: `nv84_bo_move_exec()` emits a compact sequence of `PUSH_NVSQ()` writes containing size, source VMA address, destination VMA address, and copy mode/query settings.

Control flow: The function waits for seven push entries, writes source/destination upper/lower addresses from `nouveau_mem(old_reg)->vma[0/1]`, writes `new_reg->size`, and launches a mode-copy operation without query reporting.

State/persistence: Stateless beyond channel push state and prepared memory VMAs.

Dependencies/integration: Used by `nouveau_bo_move_init()` for class `0x74c1` when available. Depends on `nouveau_dma.h`, `nouveau_mem.h`, and `nvif/push206e.h`.

Risks/test signals: Because register offsets are raw literals, class compatibility is fragile. It assumes the BO core prepared temporary VMAs and that one launch can cover `new_reg->size`. Test with NV84/NV9x BO moves, error handling when `PUSH_WAIT()` fails, and verification that copy fences complete before TTM cleanup.
