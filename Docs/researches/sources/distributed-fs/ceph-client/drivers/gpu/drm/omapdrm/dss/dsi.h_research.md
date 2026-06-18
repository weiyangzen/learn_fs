<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.h

## Purpose
`dsi.h` is the private DSI register, interrupt, timing, clock, and state definition header for the OMAP DSI implementation. It names the protocol, PHY, and PLL register windows, exposes hardware bit masks used by `dsi.c`, and defines the core data structures that carry DSI configuration and runtime state.

## Important APIs, types, and functions
`struct dsi_reg` and `DSI_REG()` encode a register as module plus offset, allowing `dsi.c` to dispatch accesses to protocol, PHY, or PLL bases. Register macros cover global DSI control and IRQ registers, per-virtual-channel registers, DSIPHY configuration registers, and DSI PLL registers. Interrupt masks define global, virtual-channel, and ComplexIO error and event bits.

Configuration types include `enum omap_dss_dsi_mode`, `enum omap_dss_dsi_trans_mode`, `struct omap_dss_dsi_videomode_timings`, and `struct omap_dss_dsi_config`. Runtime and hardware description types include `struct dsi_data`, `struct dsi_of_data`, `struct dsi_clk_calc_ctx`, `struct dsi_lane_config`, `struct dsi_isr_tables`, `struct dsi_irq_stats`, and `struct dsi_lp_clock_info`.

## Control flow
The header has no executable control flow, but it establishes the contracts used by `dsi.c`. SoC match data fills `struct dsi_of_data`, probe populates `struct dsi_data`, lane parsing fills the `lanes` array, host attach fills the public DSI config, clock calculation uses `struct dsi_clk_calc_ctx`, bridge enable programs values into hardware, and IRQ handling consults the ISR table arrays and masks declared here.

## State and persistence
The key persistent driver state is stored in `struct dsi_data`: mapped register bases, module ID, IRQ, runtime enabled flags, clocks, syscon, DSS pointer, MIPI host, calculated clock structures, PLL object, regulator state, attached MIPI device, per-VC FIFO/source state, bus and mutex locks, IRQ tables, update state, TE state, delayed work, cached clock values, error bits, debugfs pointers, lane configuration, DSI mode, videomode, DSS output, DRM bridge, and delayed disable work. This state survives across individual transfers and is reset only through detach, bridge disable, remove, or power-management paths.

## Dependencies and integration points
The header depends on DRM MIPI DSI declarations and OMAP DSS types included indirectly through users. Its structures are shared with the OMAP DSS PLL, DISPC clock, DRM bridge, runtime PM, regulator, GPIO, and debugfs paths in `dsi.c`. It also encodes SoC quirks that determine behavior for OMAP3, OMAP4, and OMAP5 hardware.

## Risks
Because this header describes bit positions and packed state, incorrect register offsets or masks can silently program the wrong hardware field. The interrupt masks are safety critical for error reporting and transfer completion. `struct dsi_data` is concurrency-sensitive because several fields are touched under different locks (`lock`, `bus_lock`, `irq_lock`, and `errors_lock`); adding fields without matching lock discipline can introduce races.

## Test signals
Build coverage should compile all DSI-enabled OMAP DRM code paths. Runtime signals are successful register dumps, correct SoC module detection, working PLL and lane setup on supported SoCs, IRQ statistics matching actual traffic, successful MIPI DSI transfers, and command/video mode operation without error IRQ masks being latched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.h -->
