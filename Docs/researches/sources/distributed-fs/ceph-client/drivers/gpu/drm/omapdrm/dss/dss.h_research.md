<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.h

## Purpose
`dss.h` is the private OMAP DSS subsystem header. It defines logging and bitfield helpers, DSS model and clock enums, PLL hardware descriptions, LCD manager configuration, the shared `struct dss_device`, and the internal function prototypes used across DSS, DISPC, DSI, DPI, SDI, VENC, HDMI, and PLL implementation files.

## Important APIs, types, and functions
Core definitions include `enum dss_model`, `enum dss_clk_source`, `enum dss_pll_id`, `struct dss_pll_clock_info`, `struct dss_pll_hw`, `struct dss_pll`, `struct dispc_clock_info`, `struct dss_lcd_mgr_config`, and `struct dss_device`. The header declares runtime PM helpers, DSS clock-source selectors, DPI/SDI/DISPC interfaces, debugfs helpers, PLL registration and calculation functions, and external platform driver objects for the DSS hardware modules.

## Control flow
The header does not execute directly. It defines the shared call graph used by `dss.c` to initialize and orchestrate components, by DSI and HDMI code to select clocks and register PLLs, by DISPC to expose manager and overlay functions, and by module init code to register the platform driver set.

## State and persistence
The persistent state model is primarily `struct dss_device`, which holds the DSS register base, syscon PLL control regmap, clock handles and cached rates, selected clock sources, saved context array, feature table, debugfs pointers, PLL objects, DISPC pointer, and manager operations private data. PLL state persists in `struct dss_pll::cinfo`, and LCD manager state is passed through `struct dss_lcd_mgr_config`.

## Dependencies and integration points
The header depends on Linux IRQ declarations and `omapdss.h`, and it ties together the internal DSS display stack. It is the main contract between DSS core, DISPC, DSI, HDMI, DPI, SDI, VENC, and the common PLL helpers. Conditional stubs keep callers buildable when optional subsystems such as debugfs, SDI, DSI, or DPI are disabled.

## Risks
The broad scope makes this a high-coupling header. Changes to PLL structures, clock source enums, or DISPC function prototypes affect many display paths. Bitfield helper macros assume valid bit ranges and 32-bit shifts; misuse can corrupt unrelated register fields. Conditional stubs returning success can hide missing optional functionality during tests unless Kconfig coverage is explicit.

## Test signals
Useful signals include all OMAP DRM Kconfig combinations building, driver registration symbols resolving, PLL calculation tests through DSI/HDMI/video PLL users, DISPC manager and overlay calls still matching prototypes, debugfs enabled and disabled builds, and runtime display tests for each enabled output class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.h -->
