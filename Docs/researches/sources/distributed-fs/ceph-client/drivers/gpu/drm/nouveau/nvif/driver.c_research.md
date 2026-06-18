# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/driver.c

## Purpose
This file initializes the NVIF driver backend and root client object.

## Important APIs, Types, and Functions
The single public function is `nvif_driver_init`.

## Control Flow
Initialization selects the built-in `nvif_driver_nvkm` backend, calls its `init` hook with name, device, cfg, and debug strings to obtain backend private state, then constructs the root NVIF client.

## State and Persistence Behavior
State is stored in the provided `nvif_client`: driver vtable pointer and object private pointer from backend initialization.

## Dependencies and Integration Points
It depends on NVIF client construction and the NVKM backend driver implementation.

## Risks
The `drv` parameter is currently ignored, so only the NVKM backend is selected. If client construction fails after backend init, cleanup responsibilities must be handled by callers/backend.

## Test Signals
Signals include driver init success/failure, root client construction, debug/cfg option propagation, and later ioctl dispatch through the selected backend.
