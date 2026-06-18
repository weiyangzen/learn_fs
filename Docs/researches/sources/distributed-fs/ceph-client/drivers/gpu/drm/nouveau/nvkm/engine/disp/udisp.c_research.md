<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/udisp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/udisp.c

## Purpose

`udisp.c` exposes the display engine root object to NVIF clients. It reports connector/output/head masks and enumerates generic and generation-specific display child classes.

## Important APIs, Types, And Functions

`nvkm_udisp_sclass()` enumerates `NVIF_CLASS_CONN`, `NVIF_CLASS_OUTP`, `NVIF_CLASS_HEAD`, then the generation-specific `disp->func->user[]` channel/capability classes. `nvkm_udisp_new()` validates ABI arguments, enforces a single display root object per client display instance, constructs the object, and fills masks from `disp->conns`, `disp->outps`, and `disp->heads`. `nvkm_udisp_dtor()` clears the root object function pointer.

## Control Flow

Userspace opens the display engine root. The constructor returns topology masks, then userspace can enumerate child classes and open connectors, outputs, heads, or display channels. Child enumeration is purely table-driven from the generation's display function table.

## State And Persistence Behavior

The object is embedded in `disp->client.object`. `disp->client.lock` serializes open and destroy state. The masks are snapshots of the persistent lists built during display oneinit.

## Dependencies And Integration Points

It depends on `priv.h`, connector/head/output lists, NVIF display ABI `if0010`, and generation `nvkm_disp_func.user` tables.

## Risks And Edge Cases

The `disp->func->user[index]` lookup follows the three generic classes, so user arrays must be correctly terminated and aligned. Only one display root object can exist at a time for this embedded object.

## Test Signals

Signals are correct topology masks, successful enumeration of connector/output/head classes, expected generation channel class IDs, duplicate display opens returning `-EBUSY`, and cleanup allowing reopen after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/udisp.c -->
