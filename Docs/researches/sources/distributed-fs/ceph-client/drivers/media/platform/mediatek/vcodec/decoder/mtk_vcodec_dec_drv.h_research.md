# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/mtk_vcodec_dec_drv.h

## Purpose
This is the main decoder private header. It defines chip IDs, capability bits, platform-data callbacks, per-request data, per-context state, device state, and decoder logging/wakeup helpers.

## Important APIs, Types, And Functions
Enums cover supported chip names, decoder format/capability flags, hardware count, and hardware architecture. `struct vdec_pic_info` stores visible/aligned dimensions, framebuffer sizes, and capture fourcc. `struct mtk_vcodec_dec_pdata` is the per-platform behavior table, including init, controls, worker, flush, capture-buffer hooks, vb2 ops, formats, defaults, hardware architecture, subdevice support, and stateless flag. `struct mtk_vcodec_dec_ctx` contains all per-instance V4L2, codec, interrupt, request, color, queue, worker, and hardware state. `struct mtk_vcodec_dec_dev` contains parent device state, resources, firmware, locks, workqueues, subdevice pointers, capability, racing state, and debugfs.

## Control Flow
The header defines the state machine and callback model used by the driver. Pdata chosen at probe determines whether stateful or stateless callbacks handle queues and decode workers.

## State, Persistence, And Dependencies
All state is runtime kernel state. Context state tracks `FREE`, `INIT`, `HEADER`, `FLUSH`, and `ABORT`. Interrupt arrays and queues are per hardware index. Dependencies include common vcodec types, debugfs, firmware private API, utilities, and LAT/core message queue types.

## Integration Points
Included by every decoder file, common debugfs/util/firmware modules, and codec-specific implementation files.

## Risks
The first field of `mtk_vcodec_dec_ctx` is used polymorphically by common helpers. Capability bits drive format/control exposure and must match firmware. Subdevice arrays are indexed by `enum mtk_vdec_hw_id`. `wake_up_dec_ctx()` has no internal bounds or NULL checks.

## Test Signals
Compile coverage, platform pdata matching, state-machine tests, multi-hardware interrupt wakeups, request lifecycle validation, and debugfs context-list tests.
