# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-ss.c

## Purpose
Programs the DCSS subsampler/synchronization stage. It writes output timing, sync polarity, data-enable window, subsampling coefficients, clip values, and run/stop state through the DCSS context loader.

## Important APIs, types, and functions
- `struct dcss_ss` stores the mapped SS register base, context-loader reference, context id, and `in_use` flag.
- Lifecycle functions are `dcss_ss_init()` and `dcss_ss_exit()`.
- Programming functions are `dcss_ss_subsam_set()`, `dcss_ss_sync_set()`, `dcss_ss_enable()`, and `dcss_ss_shutoff()`.
- Local helper `dcss_ss_write()` mirrors pre-enable writes directly to hardware and always queues the context-loader write.

## Control flow
Initialization allocates the SS object, maps the register window, records the register base offset, and uses `CTX_SB_HP` for context-loader writes. `dcss_ss_subsam_set()` programs fixed coefficients and clipping for the subsampler path. `dcss_ss_sync_set()` converts a `videomode` into total display size, hsync/vsync start/end, data-enable upper-left/lower-right coordinates, and polarity bits. Enable writes `RUN_EN` through the normal write path and marks the block active; shutoff directly clears the hardware control register and marks it idle.

## State and persistence
Runtime state is limited to the mapped address, context-loader identity, and `in_use`. Hardware timing and coefficients persist in the SS registers and in the context-loader buffer. The `in_use` flag controls whether writes are immediate plus queued or queued only.

## Dependencies and integration points
Depends on DCSS common register helpers, `dcss_ctxld_write()`, and Linux videomode data. It is called by the DCSS CRTC mode path before enabling output, alongside DTG and scaler programming.

## Risks
Timing derivation has small off-by-one differences from DTG, notably `de_ulc_y` without a `- 1`, so the two blocks must remain hardware-consistent. The subsampling coefficients are fixed magic values and not recomputed by mode or format. Direct shutoff bypasses the context loader, which is intentional for stop but must be ordered with other blocks.

## Test signals
Signals include stable modeset across polarity combinations, correct data-enable window, no shifted/blank output after enable, clean stop on shutdown, and visual validation when subsampling is active.
