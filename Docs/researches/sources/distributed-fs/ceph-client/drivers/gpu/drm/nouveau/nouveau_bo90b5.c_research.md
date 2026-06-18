# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_bo90b5.c

Purpose: Implements Fermi `NV90B5` DMA copy support for BO migration.

Important APIs/functions: `nvc0_bo_move_copy()` loops over page batches and emits raw `NV90B5` copy method offsets plus an immediate launch command.

Control flow: Source and destination offsets come from prepared memory VMAs. The function loops over up to 8191 pages at a time, writes address and pitch/line registers, emits line count, then launches the copy with `PUSH_NVIM()`. Offsets advance by pages copied.

State/persistence: No persistent local state. It consumes channel push state and relies on caller-provided TTM old/new resources.

Dependencies/integration: Used by `nouveau_bo_move_init()` for `COPY0`/`COPY1` class entries and also by some later GRCE/COPY combinations through shared init. Depends on `nouveau_mem` and `nvif/push906f.h`.

Risks/test signals: Raw register offsets and launch value are hardware-specific. Migration correctness depends on VMA preparation and page-aligned TTM sizing. Test with Fermi copy-engine migration, dual copy engine selection, large page-batched BOs, and forced fallback after push wait failure.
