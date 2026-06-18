# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-common.h

## Purpose

`c3-isp-common.h` defines the shared data model and cross-file function contracts for the Amlogic C3 ISP driver. It centralizes limits, pad indexes, resizer/capture ids, pixel-plane ids, buffer wrappers, media entity structs, the top-level device struct, register access prototypes, registration prototypes, and ISR/pre-configuration hooks.

## Important APIs, Types, And Symbols

- Driver limits: `C3_ISP_DRIVER_NAME`, `C3_ISP_CLOCK_NUM_MAX`, default/min/max width and height, and `C3_ISP_DMA_SIZE_ALIGN_BYTES`.
- Graph enums: `c3_isp_core_pads`, `c3_isp_resizer_ids`, `c3_isp_resizer_pads`, `c3_isp_cap_devs`, and `c3_isp_planes`.
- Format/buffer structs: `c3_isp_cap_format_info`, `c3_isp_cap_buffer`, `c3_isp_stats_buffer`, `c3_isp_params_buffer`, and `c3_isp_dummy_buffer`.
- Entity/device structs: `c3_isp_core`, `c3_isp_resizer`, `c3_isp_stats`, `c3_isp_params`, `c3_isp_capture`, `c3_isp_info`, and `c3_isp_device`.
- Shared function prototypes: register read/write/update helpers, core/resizer/capture/stats/params register/unregister functions, ISR handlers, and stats/params pre-configuration hooks.

## Control Flow

The header has no executable control flow. It defines how the component implementation files cooperate: the top-level device code owns `struct c3_isp_device`, initializes hardware/base clocks/media devices, calls component registration functions, and dispatches ISR work into core, capture, stats, and params handlers. Capture, stats, params, core, and resizer implementation files manipulate their portion of the shared device struct.

## State And Persistence

Runtime state is organized under `struct c3_isp_device`: device pointer, register base, clocks, V4L2 async notifier, V4L2 and media devices, media pipeline, core subdev, three resizers, stats node, params node, three capture nodes, frame sequence, and version information. Per-node structs store vb2 queues, video devices, pads, locks, active buffers, and pending lists. None of this persists beyond driver lifetime.

## Dependencies And Integration Points

The header depends on Linux clocks and media/V4L2/vb2 headers. It is included by all C3 ISP component files and acts as the internal ABI between the aggregate module objects listed in the Makefile. The capture file uses the capture enums, format info, buffer structs, parent device, resizer pointers, and register access prototypes from this header.

## Risks

Because this header defines shared structs across multiple implementation files, field layout changes have broad impact. Locking comments are part of the contract: `mutex lock` protects queue/video-device state while spinlocks protect active/pending buffers. Format and dimension constants must stay consistent with hardware and all format-setting paths. Function prototypes must remain matched with the objects linked into `c3-isp.o`.

## Test Signals

Build tests are strong signals for cross-file contract drift. Runtime tests should validate media entity registration, async notifier binding, all component unregister paths, ISR dispatch, concurrent buffer queue/complete locking, and width/height boundary handling across capture and resizer components.
