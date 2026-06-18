# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys.h

## Purpose
Declares the top-level IPU7 ISYS driver state, firmware message wrapper, async sensor connection metadata, global geometry/queue limits, and cross-file helper prototypes.

## Important APIs, Types, and Constants
Defines `IPU_ISYS_ENTITY_PREFIX`, `IPU_ISYS_MAX_STREAMS` as 16, firmware queue sizing constants, min/max image dimensions, and `FW_CALL_TIMEOUT_JIFFIES`. `struct isys_fw_log` tracks firmware log buffer state under a mutex. `struct ipu7_isys` owns media/V4L2 devices, bus device, power state and lock, CSI IRQ mask, stream array/refcounts, PHY flags, firmware open and stream-open counts, mutexes, platform data, CSI2 receivers, firmware log, request and firmware-message lists, PM QoS, async notifier, and subsystem config DMA. `struct isys_fw_msgs` stores one DMA-backed firmware command union plus list node and DMA address. Sensor async metadata stores CSI2 lane/port/bus information.

## Control Flow and State
This header describes state initialized in probe and consumed by video, queue, CSI2, firmware, and ISR paths. Firmware message buffers move between `framebuflist` and `framebuflist_fw`; streams move through refcounted allocation, command completions, and release; power and interrupt state are coordinated with runtime PM.

## Dependencies and Integration Points
Includes Linux locking/list/PM QoS primitives, media and V4L2 device/notifier types, firmware ABI headers, and CSI2/video declarations. Public functions are used by queue/video/firmware modules to obtain command buffers, return buffers, clean stale firmware buffers, handle one firmware ISR response, and set up hardware.

## Risks and Test Signals
Shared lists and refcounts are central correctness points. Risks include unsigned `ref_count` underflow if close paths mispair, stale `stream_opened` blocking suspend, firmware buffer union pointer assumptions in `ipu7_put_fw_msg_buf()`, and locks being acquired in inconsistent order across stream setup and ISR. Test with lockdep, repeated stream open/close, failed firmware command submissions, runtime PM transitions, and message-pool exhaustion.
