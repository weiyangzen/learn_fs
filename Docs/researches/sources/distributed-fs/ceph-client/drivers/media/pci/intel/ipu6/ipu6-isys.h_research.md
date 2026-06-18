# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys.h

## Purpose
This header defines the central IPU6 ISYS device state, platform limits, firmware message buffer wrapper, async sensor data, CSI-2 configuration, iWake watermark state, and exported ISYS helper declarations.

## Important APIs, Types, And Data
Constants define entity naming, maximum firmware streams, firmware queue sizes, ISYS frame dimension limits, SRAM granularity/size by generation, and IPU6EP iWake LTR/mem-open defaults. `struct ipu6_isys` owns the media/V4L2 devices, auxiliary device, power state, stream tables/refcounts, firmware communication pointer, locks, platform data, PHY power callback, CSI-2 receivers, PM QoS request, firmware message buffer lists, async notifier, and watermark state. `struct isys_fw_msgs` is the DMA-visible union for frame-buffer-set and stream-config firmware messages.

## Control Flow
Consumers use this header to access shared ISYS state from video, queue, CSI-2, and core files. Runtime PM and firmware paths operate through fields such as `fwcom`, `need_reset`, `streams`, `framebuflist`, and `iwake_watermark`.

## State And Persistence
All fields are in-memory device-lifetime state. The stream array supports up to 16 firmware streams. `need_reset`, `power`, `ref_count`, and `stream_opened` are central state gates for open, runtime PM, and suspend behavior.

## Dependencies And Integration Points
The header depends on Linux mutex/spinlock/PM QoS/list types, media and V4L2 async/device types, IPU6 platform state, firmware ABI, CSI-2 receiver definitions, and video definitions. It exports PHY power functions and firmware message helpers across ISYS submodules.

## Risks And Test Signals
Because this is a shared state contract, field lifetime and locking are critical. Test signals include lockdep coverage for `streams_lock`, `power_lock`, `stream_mutex`, and watermark mutex; firmware buffer list leak checks; and stream refcount validation across multi-node capture.
