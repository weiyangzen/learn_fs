# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispstat.c

## Purpose
Provides the generic statistics-engine core used by OMAP3 ISP H3A AF, H3A AEWB, and histogram blocks. It handles configuration, DMA/coherent buffer allocation, magic-word integrity checks, V4L2 statistics events, userspace copyout, enable/disable state transitions, SBL overflow recovery, and common ISR sequencing.

## Important APIs, Types, and Functions
Public APIs include `omap3isp_stat_config()`, `omap3isp_stat_request_statistics()`, `omap3isp_stat_request_statistics_time32()`, `omap3isp_stat_enable()`, `omap3isp_stat_s_stream()`, ISR hooks, suspend/resume, entity register/unregister, init, and cleanup. Key helpers include `isp_stat_bufs_alloc()`, `isp_stat_buf_get()`, `isp_stat_buf_queue()`, `isp_stat_buf_process()`, `isp_stat_try_enable()`, and `__stat_isr()`.

## Control Flow
Userspace config calls module-specific `validate_params()` and `set_params()`, sizes/reallocates the coherent buffer pool, and returns the future config counter. Enable requests move from disabled to enabling; frame-sync calls `isp_stat_try_enable()` to pick an active buffer, set up registers, insert magic, and enable PCR. ISR handling disables the module, optionally invokes module-specific buffer processing, queues completed buffers, applies normal or recovery configuration, reinserts magic, re-enables PCR, and queues V4L2 events. Userspace statistics requests lock one completed buffer, verify magic, copy to user memory, fill timestamp/frame/config metadata, then release it.

## State and Persistence
`struct ispstat` owns a fixed pool of `STAT_MAX_BUFS` buffers, `active_buf`, `locked_buf`, `configured/update/buf_processing/sbl_ovl_recover` flags, frame/config counters, event type, DMA channel, module-private config, and state enum. All state is volatile, but it persists across stream toggles while the subdevice exists.

## Dependencies and Integration Points
The generic layer depends on module-specific `ispstat_ops`, ISP global `stat_lock`, DMA mapping APIs, V4L2 events/subdevs, media entities, timekeeping, and userspace copy APIs. H3A-specific behavior is selected by comparing `stat` against `isp_af` and `isp_aewb`.

## Risks and Edge Cases
The file documents hardware workarounds: AF writes one extra paxel, H3A may resume at the wrong address after SBL overflow, and recovery configs reduce repeated overflows. Magic checks intentionally require the beginning marker to be overwritten and the ending marker to remain intact. Buffer allocation is forbidden while enabled or processing, and `BUG_ON(locked_buf)` enforces no userspace copyout during reallocation. DMA-engine and ISP-IOMMU allocation paths use different devices.

## Test Signals
Test valid/invalid configs, buffer-size correction, time32 compatibility, event delivery with and without errors, EBUSY/EINVAL paths, SBL overflow recovery, streamoff during pending histogram DMA, magic corruption detection, and concurrent userspace statistic requests.
