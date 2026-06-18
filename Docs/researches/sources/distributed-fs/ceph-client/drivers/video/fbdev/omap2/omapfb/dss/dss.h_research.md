# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.h

## Purpose

This header is the internal OMAP DSS subsystem contract. It centralizes logging macros, bitfield helpers, clock-source and PLL types, LCD manager clock/config structs, and function prototypes shared by DSS core, DISPC, DSI, DPI, SDI, VENC, HDMI, overlay, manager, PLL, and compatibility layers. The complete 519-line header was read.

## Important APIs, Types, and Functions

Key macros are `DSSDBG`, `DSSERR`, `DSSINFO`, `DSSWARN`, `FLD_MASK`, `FLD_VAL`, `FLD_GET`, and `FLD_MOD`. Important enums include `omap_dss_clk_source`, `dss_io_pad_mode`, `dss_hdmi_venc_clk_source_select`, `dss_dsi_content_type`, and `dss_pll_id`.

Important structs are `dss_pll_clock_info`, `dss_pll_ops`, `dss_pll_hw`, `dss_pll`, `dispc_clock_info`, `dss_lcd_mgr_config`, and `dss_mgr_ops`. The prototypes cover runtime PM, display suspend/resume/disable, sysfs init, overlay manager setup/checks, overlay setup/checks, DSS clock/source control, OF helpers, SDI/DPI/DSI/DISPC/VENC/HDMI platform driver entry points, PLL registration/calculation/programming, and legacy manager operation wrappers.

## Control Flow

There is no runtime flow in the header, but it defines the call graph used by the subsystem. Core init files register platform drivers declared here; output drivers call manager and clock helpers declared here; DISPC exports low-level manager/overlay programming used through wrappers; PLL providers register `struct dss_pll` objects whose operations are invoked by DPI, DSI, HDMI, and video PLL users.

## State and Persistence Behavior

The header stores no state. It defines the in-memory structures that carry PLL dividers/rates, DISPC clock divisors, and LCD manager config between calculation code and hardware programming code. The bitfield macros are used throughout the subsystem for hardware register state.

## Dependencies and Integration Points

It depends on Linux interrupt declarations and OMAP DSS public video types. It is included by most files in `omapfb/dss`, making it the main integration boundary between component drivers. Compile-time feature guards provide no-op DPI/SDI helpers when those drivers are not built and a warning fallback for `dsi_get_pixel_size()` when DSI is disabled.

## Risks and Edge Cases

Because this header is widely included, signature drift can break many drivers. The bitfield helpers use `1 << width` style arithmetic and assume valid field widths below the integer limit. Several prototypes expose low-level functions that rely on caller-side PM, locking, or valid channel/source combinations. Stubs can hide missing feature support at compile time while runtime graph data still names a disabled output type.

## Test Signals

Build coverage is the main signal: all relevant Kconfig combinations for DPI, DSI, SDI, HDMI4/5, VENC, DISPC, debugfs, and IRQ stats should compile. Runtime validation should exercise PLL registration/lookups, manager wrappers, clock-source helpers, and disabled-driver stubs on configs that omit optional outputs.
