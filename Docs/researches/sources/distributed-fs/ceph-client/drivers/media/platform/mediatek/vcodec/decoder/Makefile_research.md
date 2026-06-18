# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/Makefile

## Purpose
This Makefile builds the MediaTek decoder modules and selects codec-specific implementation objects.

## Important APIs, Types, And Functions
`mtk-vcodec-dec.o` includes decoder interface implementations for H.264, VP8, VP9, AV1, HEVC request paths, common request helpers, driver probe, firmware VPU interface, message queue, shared decoder ioctls, stateful/stateless APIs, and decoder PM. `mtk-vcodec-dec-hw.o` contains subdevice hardware support. Both are built under `CONFIG_VIDEO_MEDIATEK_VCODEC`.

## Control Flow
Kbuild aggregates all listed objects into the decoder module and hardware-subdevice module. Runtime platform data decides which stateful/stateless and hardware architecture paths are used.

## State, Persistence, And Dependencies
No runtime state in this file. Build state depends on Kconfig and object list correctness.

## Integration Points
Connects common vcodec objects to codec-specific decoder implementations and parent/subdevice platform drivers.

## Risks
The decoder module includes many codec implementations unconditionally under the main vcodec config, so missing symbols in any one break all decoder builds. Adding a codec requires updating both this object list and capability/format/control tables.

## Test Signals
Full decoder build, module load with parent and subdevice objects, and compile coverage for all codec-specific paths.
