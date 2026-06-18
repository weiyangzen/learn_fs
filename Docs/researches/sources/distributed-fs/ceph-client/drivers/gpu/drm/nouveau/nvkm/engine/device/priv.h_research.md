<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/priv.h

Purpose: private device-engine header that gathers the subdevice and engine type declarations needed by the NVKM device constructor and lifecycle implementation. It is a dependency hub rather than a behavior implementation.

Important APIs and types: declares `nvkm_device_ctor()`, `nvkm_device_init()`, and `nvkm_device_fini()`. The constructor takes a transport-specific `nvkm_device_func`, optional quirk data, Linux `struct device`, `enum nvkm_device_type`, unique handle, name, configuration/debug strings, and the destination `struct nvkm_device`.

Control flow: files such as `pci.c`, `tegra.c`, and `user.c` include this header to call or expose device lifecycle functions. The many `#include <subdev/...>` and `#include <engine/...>` entries make the complete set of possible NVKM children visible to the device implementation.

State and persistence: none directly; it defines the private interface by which transport constructors populate persistent `struct nvkm_device` instances and by which user-facing objects refcount initialization.

Dependencies and integration points: tightly coupled to nearly every NVKM subdevice and engine family: ACR, BAR, BIOS, bus, clock, display, FIFO, graphics, MMU, PMU, GSP, thermal, video engines, and others. This header is an integration point between transport discovery and engine/subdevice instantiation.

Risks: because it is a broad private include hub, changes can trigger wide rebuilds and expose circular include problems. Prototype changes affect every transport constructor and the user object lifetime path.

Test signals: successful kernel build is the main signal. Runtime validation comes indirectly through PCI/Tegra device probe, user device open/close, and init/fini sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/priv.h -->
