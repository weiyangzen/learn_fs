# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dispc.c

## Purpose

`dispc.c` is the hardware-facing OMAP Display Controller driver for the legacy fbdev DSS stack. The complete 4059-line source was read. It owns DISPC MMIO access, context save/restore, runtime PM, overlay setup, scaler calculations, FIFO/MFLAG setup, manager timing and clock programming, IRQ request plumbing, debug register dumps, and platform/component binding.

## Important APIs, Types, and Functions

Key types are `struct dispc_features`, the static `dispc` device state, `enum mgr_reg_fields`, `struct dispc_reg_field`, and color/scaler helper types. Exported or externally used APIs include `dispc_runtime_get()/put()`, manager IRQ accessors, `dispc_mgr_go_busy()`, `dispc_mgr_go()`, `dispc_ovl_set_channel_out()`, `dispc_ovl_set_fifo_threshold()`, `dispc_ovl_compute_fifo_thresholds()`, `dispc_ovl_check()`, `dispc_ovl_setup()`, `dispc_ovl_enable()`, `dispc_ovl_enabled()`, `dispc_mgr_enable()`, `dispc_mgr_is_enabled()`, `dispc_mgr_setup()`, `dispc_mgr_set_lcd_config()`, `dispc_mgr_timings_ok()`, `dispc_mgr_set_timings()`, clock/divider helpers, IRQ status/enable helpers, and platform driver init/uninit.

## Control Flow

Probe registers a component. Bind selects SoC features from `omapdss_get_version()`, maps MMIO, gets IRQ, optionally finds a `syscon-pol` regmap, enables runtime PM, performs initial hardware configuration, reads revision, initializes overlay managers, and creates debugfs. Overlay setup validates color mode, addresses, YUV alignment, interlace field mode, scaling limits, predecimation, and clock requirements; then it calculates DMA/VRFB/TILER offsets, row/pixel increments, FIR coefficients, chroma handling, color conversion, z-order, alpha, replication, and base addresses. Manager setup programs default color, transparency key, alpha/z-order, CPR, LCD timing, data lines, stall mode, and clock divisors.

## State and Persistence Behavior

The static `dispc` struct stores MMIO base, IRQ, user IRQ handler, clock rates, FIFO sizes/assignments, saved register context, SoC feature table, enabled flag, syscon polarity regmap, and a control/config spinlock. Runtime suspend marks DISPC disabled, synchronizes IRQ, and saves register context; resume reinitializes hardware if load mode indicates context loss and restores saved context before re-enabling IRQ handling. Hardware register state is authoritative only while powered.

## Dependencies and Integration Points

The file integrates with DSS clock/PLL helpers, feature tables, overlay manager initialization, `dispc_coefs.c` for scaler coefficient tables, runtime PM, component framework, DT compatibles, debugfs from `core.c`, regmap/syscon polarity bits, and `dispc-compat.c` through IRQ request and MMIO IRQ helpers. `apply.c` uses most overlay/manager programming exports.

## Risks and Edge Cases

Many helper paths use `BUG()` for impossible enum values, so invalid callers can panic the kernel. Scaling calculations are SoC-specific and depend on current clock rates; wrong divisors or `CONFIG_FB_OMAP2_DSS_MIN_FCK_PER_PCK` can reject valid-looking modes. Rotation offset math is format-specific and has special NV12 and interlace behavior. Context save/restore intentionally delays CONTROL and IRQENABLE restore until late. FIFO/MFLAG setup includes documented hardware workarounds. IRQ handler dispatch uses memory barriers around `is_enabled` and user handler state.

## Test Signals

Signals include SoC feature selection across OMAP24xx/34xx/44xx/54xx/DRA7, runtime suspend/resume with context loss, overlay setup for RGB/YUV/NV12, scaling up/down including 3-tap/5-tap, interlace and rotation modes, FIFO threshold calculations, manager timing bounds, clock divisor search, debugfs register dumps, IRQ request/free, and DT `syscon-pol` behavior.
