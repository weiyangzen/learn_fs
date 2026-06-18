<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dpr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dpr.c

Purpose: Implements the DCSS Display Prefetch Resolver channels, including format/tile setup, framebuffer address/resolution programming, rotation, and deferred run-control writes through CTXLD.

Important APIs/types/functions: Public APIs are `dcss_dpr_init()`, `dcss_dpr_exit()`, `dcss_dpr_set_res()`, `dcss_dpr_addr_set()`, `dcss_dpr_enable()`, `dcss_dpr_format_set()`, `dcss_dpr_write_sysctrl()`, and `dcss_dpr_set_rotation()`. Important internal types are `struct dcss_dpr_ch` and `struct dcss_dpr`.

Control flow: Init maps three channel register spaces, stores channel offsets, masks IRQs, and chooses CTXLD high-priority SB context. Format setup records DRM format, configures YUV enable, pixel size, component order/swaps, two-plane mode, RTRAM buffering, and tiling. Resolution setup adjusts width/height to tile and RTRAM alignment and queues per-plane dimensions. Enable queues mode/frame/rtram state and records pending system-control changes. `dcss_dpr_write_sysctrl()` emits deferred run/stop control entries while CTXLD lock is held.

State and persistence behavior: Each channel caches format, pixel size, tile type, RTRAM flags, frame/mode/system/rtram control words, `sys_ctrl_chgd`, base offset, and MMIO base. Most programming is persisted as queued CTXLD writes; exit directly stops all channels.

Dependencies: DRM format/modifier/rotation definitions, DCSS CTXLD, low-level MMIO helpers, device-managed ioremap, and scaler/plane callers.

Integration points: DCSS plane update paths configure DPR before CTXLD flush. CTXLD kick calls `dcss_dpr_write_sysctrl()` to append deferred run-control writes.

Risks: Width/height adjustment is format/tile dependent and can cause fetch underruns if wrong. Only channel 0 supports Vivante tiled modifiers; channels 1/2 force linear. `to_comp_sel()` fallback may hide unsupported RGB swizzles.

Test signals: Scanout for RGB/YUV formats, NV12/NV21 two-plane addresses, Vivante tiled/super-tiled on channel 0, rotations/reflections, DPR enable/disable through CTXLD, and FIFO/AXI error IRQ status on stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dpr.c -->
