# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/device.h

## Purpose
Declares the NVIF GPU device wrapper, including cached device information, runlist data, and usermode object.

## Important APIs, Types, And Functions
Defines `struct nvif_device`, `struct nvif_fifo_runlist`, and APIs `nvif_device_ctor`, `nvif_device_dtor`, `nvif_device_map`, and `nvif_device_time`.

## Control Flow
Construction queries device info and optional runlists. Map exposes device MMIO/object mapping. Time reads GPU timer data through the NV_DEVICE method interface.

## State And Persistence
State includes device object, `nv_device_info_v0`, runlist array/count, and embedded `nvif_user`. It persists for the lifetime of the Nouveau device wrapper.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/cl0080.h`, and `nvif/user.h`; used by MMU, FIFO, timer, and display setup.

## Risks
Incorrect runlist cache or device info can break engine/channel selection. Mapping lifetime must match object lifetime.

## Test Signals
Probe logs, `nvif_device_time()` monotonicity, runlist discovery, usermode construction, and suspend/resume validate behavior.
