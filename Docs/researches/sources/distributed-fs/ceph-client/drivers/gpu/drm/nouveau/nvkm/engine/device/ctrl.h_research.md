## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/ctrl.h

### Purpose
`ctrl.h` defines the private NVKM control object wrapper and exports its class descriptor to the device engine.

### Important APIs, types, and functions
It defines `nvkm_control(p)` as a `container_of()` helper, declares `struct nvkm_control` with base object and device pointer, and declares `extern const struct nvkm_device_oclass nvkm_control_oclass`.

### Control flow
The header has no runtime control flow.

### State and persistence behavior
It describes the per-control-object state allocated in `ctrl.c`; it owns no storage itself.

### Dependencies
It includes `core/object.h`, which provides `struct nvkm_object` and object callback contracts.

### Integration points
`ctrl.c` implements the declared class. Device object construction code can expose `nvkm_control_oclass` as the NVIF control class.

### Risks
The container helper assumes the embedded object is the first relevant member of `struct nvkm_control`; layout changes must preserve the helper's intent. Prototype or type drift breaks control object construction.

### Test signals
Compile coverage of `ctrl.c` and any device user code referencing `nvkm_control_oclass`, plus control object create/destroy tests, validate this header.
