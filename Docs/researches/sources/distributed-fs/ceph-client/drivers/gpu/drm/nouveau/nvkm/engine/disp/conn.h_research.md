<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.h

Purpose: private connector header defining `struct nvkm_conn`, constructor/destructor prototypes, and connector-scoped logging macros.

Important APIs and types: `struct nvkm_conn` stores the owning display, connector index, VBIOS `nvbios_connE` data, list node, and embedded `nvkm_object`. `nvkm_conn_new()` and `nvkm_conn_del()` manage lifetime. `CONN_ERR`, `CONN_DBG`, and `CONN_TRACE` format messages with connector index/location/type.

Control flow: no runtime control flow; this header is consumed by connector construction, display teardown, output handling, and user connector wrappers.

State and persistence: defines the connector object state that is linked into `disp->conns` and referenced by outputs.

Dependencies and integration points: includes display private state, BIOS connector definitions, and NVKM logging macros through display subdev.

Risks: connector info is copied from BIOS and may be referenced by output code; layout changes must preserve users of `conn->info`. Logging macros assume `conn->disp` is valid.

Test signals: build and connector lifetime tests, especially teardown ordering with outputs still referencing connectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/conn.h -->
