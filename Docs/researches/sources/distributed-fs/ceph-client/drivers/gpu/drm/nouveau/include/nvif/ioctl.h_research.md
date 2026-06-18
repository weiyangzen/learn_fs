# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ioctl.h

## Purpose
Defines the low-level NVIF ioctl command envelopes used for object construction, destruction, method calls, map/unmap, and supported-class queries.

## Important APIs, Types, And Functions
Defines `nvif_ioctl_v0` with grouped header fields version, type, owner, route, token, and target object; ioctl types for supported-class query, new, delete, method, map, and unmap; `nvif_ioctl_sclass_v0` with class/version ranges; `nvif_ioctl_new_v0` with route/token/object/handle/class and trailing class data; `nvif_ioctl_mthd_v0` with method id and trailing method data; and `nvif_ioctl_map_v0` with IO/VA map type, handle, length, and trailing map data.

## Control Flow
No executable flow. Front-end object helpers pack an envelope and backend `nvif_driver.ioctl` dispatches it to NVKM. Static assertions keep variable-data offsets equal to the tagged header sizes.

## State And Persistence
Ioctl payloads are transient; successful calls create/destroy/query persistent NVKM objects or mappings.

## Dependencies And Integration Points
Used by `nvif/object.h`, `nvif/driver.h`, and all NVIF object constructors/method calls.

## Risks
This is a central ABI boundary. Version, size, owner/route, token/object handles, class, method id, and embedded pointer/trailing-data handling must be exact to avoid object leaks or invalid dispatch.

## Test Signals
Object constructor/method/map tests, unsupported class queries, and ioctl trace logs validate behavior.
