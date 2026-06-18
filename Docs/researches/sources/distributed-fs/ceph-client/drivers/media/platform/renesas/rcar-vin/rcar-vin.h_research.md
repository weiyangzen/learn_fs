# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-vin.h

## Purpose
`rcar-vin.h` is the private shared header for the three VIN implementation files. It defines hardware sizing constants, SoC model enums, CSI/ISP remote IDs, shared format and topology structures, the main VIN device/group state structures, logging macros, and cross-file function prototypes.

## Important APIs, Types, And Functions
Constants include `HW_BUFFER_NUM` (three hardware slots), `HW_BUFFER_MASK` (128-byte alignment mask), `RCAR_VIN_NUM` (32 instances), and `RVIN_REMOTES_MAX`. Important enums are `model_id`, `rvin_csi_id`, and `rvin_isp_id`. Important structs are `rvin_video_format`, `rvin_parallel_entity`, `rvin_group_route`, `rvin_info`, `rvin_dev`, and `rvin_group`. Prototypes connect DMA, V4L2, routing, scaler, alpha, and streaming operations across files.

## Control Flow
No executable control flow is implemented in the header. It defines the contracts used by `rcar-core.c` to allocate/register devices, `rcar-dma.c` to operate hardware and buffers, and `rcar-v4l2.c` to expose userspace operations.

## State And Persistence
`struct rvin_dev` is the key per-device state container: platform resources, V4L2/video/control objects, parallel subdev info, group membership, vb2 queue and scratch DMA buffer, `qlock`-protected hardware buffers/list/sequence/running flag, route state, media bus code, active format, crop/compose, scaler callback, and alpha. `struct rvin_group` stores shared media device, notifier, platform info, VIN pointer array, link setup callback, and remote subdev slots. All state is runtime memory only.

## Dependencies And Integration Points
The header imports V4L2 async, controls, device, fwnode, and vb2 types plus kernel `kref`. It is the internal integration point between the VIN core/media graph, DMA engine, and V4L2 node implementation.

## Risks
The header centralizes locking expectations but does not enforce them; callers must honor `lock` for queue operations and `qlock` for hardware buffer state. Struct layout changes affect all three objects. `RVIN_REMOTES_MAX` depends on enum ordering and casts. Documentation typos in comments do not affect code but can mislead maintainers.

## Test Signals
Compile all VIN objects after structure/prototype changes, run sparse/lockdep for locking assumptions, verify `RCAR_VIN_NUM` indexed arrays are bounded by ID validation, and validate that all cross-file prototypes match definitions.
