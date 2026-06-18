# subset-b-003741 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_regs.h

## Purpose

`rcar_du_regs.h` is the register map for the Renesas R-Car Display Unit (DU) driver. It provides offsets and bitfield macros for display control, timing generation, planes, palettes, capture, external sync, dual-output routing, PLLs, and color conversion blocks used by the rest of the R-Car DU KMS implementation.

## Important APIs, Types, and Functions

This file has no functions or persistent state. Its important API is the macro namespace: `DU0_REG_OFFSET` through `DU3_REG_OFFSET` locate DU channels; `DSYSR`, `DSMR`, `DSSR`, `DSRCR`, `DIER`, `DEFR*`, `DIDSR`, `DPLLCR`, and `DPLLC2R` describe global display control and SoC-specific routing; `HDSR` through `DEWR` describe timing; `Pn*` and `APn*` describe primary/additional plane programming; `ESCR*`, `OTAR*`, `DORCR`, `DPTSR`, and `DAPTSR` describe external/dual-output routing; `YNCR` through `BCBCR` are color conversion coefficients.

## Control Flow

Control flow is indirect: C files include the header and compose register writes from these macros during CRTC setup, plane setup, interrupt handling, clock routing, and output selection. The header encodes hardware constraints such as protected write codes (`DEFR_CODE`, `DAPCR_CODE`, `DCPCR_CODE`) and bit masks used to preserve unrelated register fields.

## State and Persistence Behavior

The macros describe hardware state that persists in MMIO registers until reset, suspend, or subsequent programming. There is no software state in the header; correctness depends on callers writing the right register block for the active DU channel and SoC generation.

## Dependencies and Integration Points

The macros are consumed by the R-Car DU CRTC, plane, group, encoder, LVDS, DSI, and writeback paths. Integration points include Linux bit operations where `BIT()` is used for newer fields, DRM pixel/plane state code that selects register values, and DT/SoC data that chooses which channel offsets and routing fields are valid.

## Risks and Edge Cases

- Register macros are hardware ABI. Incorrect shifts, masks, or protected codes can silently misprogram display output.
- Several fields are generation-specific or SoC-specific; callers must avoid using Gen3/Gen4 fields on older DU blocks.
- `DD1SRCR_FRM` is defined twice with the same value, which is harmless for preprocessing but is a maintenance warning.
- Plane address masks such as `PnDSA_MASK` assume caller alignment validation.

## Test Signals

Build coverage should include all R-Car DU configurations that include this header. Runtime signals are correct CRTC timing, plane positioning, interrupt clearing, LVDS/DSI clock routing, dual-output behavior, and no unexpected reserved-bit writes under register tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.c

## Purpose

`rcar_du_vsp.c` implements the R-Car DU compositor path backed by a VSP1 device. It exposes DRM planes for VSP RPF inputs, maps GEM framebuffers into the VSP DMA domain, forwards atomic plane/pipe configuration to `vsp1_du_*()`, and converts VSP completion callbacks into vblank, page-flip, CRC, and writeback completion signals.

## Important APIs, Types, and Functions

Public entry points are `rcar_du_vsp_init()`, `rcar_du_vsp_enable()`, `rcar_du_vsp_disable()`, `rcar_du_vsp_atomic_begin()`, `rcar_du_vsp_atomic_flush()`, `rcar_du_vsp_map_fb()`, and `rcar_du_vsp_unmap_fb()`. The main internal helpers are `rcar_du_vsp_complete()`, `rcar_du_vsp_state_get_format()`, `rcar_du_vsp_plane_setup()`, and the DRM plane helper/state callbacks. Format arrays advertise Gen2/Gen3 formats and a Gen4 superset including 10-bit RGB and Y210/Y212.

## Control Flow

Initialization finds the VSP platform device from a DT node, adds a devm cleanup action, creates a device link from DU to VSP for suspend ordering, calls `vsp1_du_init()`, allocates one primary plane per connected CRTC and the remaining planes as overlays, and attaches alpha, zpos, and blend-mode properties. CRTC enable programs a dummy DU plane state for VSPD input selection and calls `vsp1_du_setup_lif()` with the active mode and completion callback. Atomic begin/flush wraps VSP atomic pipe transactions and passes CRC/writeback config. Plane updates translate DRM source/destination rectangles, alpha, zpos, blend mode, pitch, V4L2 pixel format, and SG DMA addresses into `vsp1_du_atomic_config`.

## State and Persistence Behavior

`struct rcar_du_vsp` stores the VSP device, device link, plane array, and plane count for the lifetime of the DRM device. Each `rcar_du_vsp_plane_state` stores the resolved `rcar_du_format_info` and mapped SG tables for the current framebuffer. Mapping is transient per visible plane state and must be released in cleanup. Hardware programming persists in the VSP pipeline until the next atomic update or LIF disable.

## Dependencies and Integration Points

This file depends on DRM atomic helpers, GEM DMA helpers, scatterlist/DMA APIs, `media/vsp1.h`, R-Car DU format helpers, CRTC state, and optional writeback support. It integrates tightly with `rcar_du_crtc.c` for enable/flush/page-flip sequencing and with VSP1 for all composition and DMA.

## Risks and Edge Cases

- Imported dma-bufs with non-contiguous SG tables are copied and mapped to VSP; failure unwinding must unmap only planes already mapped.
- The map/unmap helpers assume framebuffer plane count does not exceed the fixed three-table storage.
- `rcar_du_vsp_plane_atomic_update()` derives the old CRTC and must only dereference it when an old CRTC exists for disable updates.
- Format alpha-stripping for `DRM_MODE_BLEND_PIXEL_NONE` must stay synchronized with advertised formats and `rcar_du_format_info()`.
- Device-link ordering is state-less; runtime PM behavior still depends on the VSP and DU drivers honoring their PM contracts.

## Test Signals

Useful tests include KMS atomic plane updates for all advertised formats, imported dma-buf planes, multi-plane YUV buffers, alpha/blend-mode changes, zpos ordering, page-flip completion, CRC capture, writeback completion, suspend/resume with DU/VSP ordering, and fault injection for SG allocation/map failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.h

## Purpose

`rcar_du_vsp.h` declares the R-Car DU to VSP compositor interface and the DRM plane/private-state structures used by the implementation.

## Important APIs, Types, and Functions

`struct rcar_du_vsp_plane` embeds a `drm_plane`, a parent `rcar_du_vsp *`, and a VSP input index. `struct rcar_du_vsp` stores the VSP index, supplier device, DU device, optional `device_link`, plane array, and plane count. `struct rcar_du_vsp_plane_state` extends `drm_plane_state` with resolved format metadata and up to three SG tables. The header exports conversion helpers and the init/enable/disable/atomic/map/unmap functions, with stubs when `CONFIG_VIDEO_RENESAS_VSP1` is disabled.

## Control Flow

Consumers call `rcar_du_vsp_init()` while building KMS objects, then CRTC code calls enable/disable and atomic begin/flush around DU commits. Plane helpers use the private state to carry map results from prepare to cleanup and format results from atomic check to update.

## State and Persistence Behavior

The header defines lifetime ownership: VSP data lives under the DU device, plane state is duplicated/destroyed through DRM atomic state, and SG tables are valid only for the prepared framebuffer state.

## Dependencies and Integration Points

It depends on DRM planes, Linux scatterlists, forward-declared R-Car DU types, and `media/vsp1.h` structures exposed in function signatures. Optional stubs let the rest of the DU code compile without VSP1 but make initialization return `-ENXIO`.

## Risks and Edge Cases

- The fixed `sg_tables[3]` array must match supported framebuffer plane counts.
- Stub behavior means callers must treat `-ENXIO` as a real missing-compositor failure.
- The header exposes internal structures to multiple DU files, so layout changes require coordinated updates.

## Test Signals

Compilation with and without `CONFIG_VIDEO_RENESAS_VSP1`, atomic state duplication tests, and framebuffer map/unmap lifecycle testing are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_vsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.c

## Purpose

`rcar_du_writeback.c` implements DRM writeback connector support for R-Car DU when the display pipeline is VSP-backed. It validates writeback jobs, maps the destination framebuffer for VSP DMA, programs VSP writeback configuration during atomic flush, and signals completion from the VSP callback.

## Important APIs, Types, and Functions

Driver-private `rcar_du_wb_conn_state` adds the selected `rcar_du_format_info` to DRM connector state, and `rcar_du_wb_job` stores mapped SG tables. Public functions are `rcar_du_writeback_init()`, `rcar_du_writeback_setup()`, and `rcar_du_writeback_complete()`. Internal callbacks implement connector modes, job prepare/cleanup, connector state duplication/reset, and encoder atomic validation.

## Control Flow

Initialization registers a writeback connector for one CRTC and advertises RGB-only formats. During an atomic commit with a writeback job, encoder atomic check verifies the framebuffer matches the active mode size and a supported R-Car DU format. `prepare_writeback_job` allocates private job state and maps the framebuffer through `rcar_du_vsp_map_fb()`. During CRTC/VSP atomic flush, `rcar_du_writeback_setup()` copies V4L2 format, pitch, and DMA addresses into `vsp1_du_writeback_config` and queues the job. The VSP completion callback later invokes `drm_writeback_signal_completion()`.

## State and Persistence Behavior

Connector state persists across atomic commits and carries the resolved format for the active job. Job-private SG mappings persist only between prepare and cleanup. Queued DRM writeback jobs are owned by the DRM writeback core after `drm_writeback_queue_job()`.

## Dependencies and Integration Points

This file depends on DRM writeback helpers, connector/encoder atomic helpers, R-Car DU format lookup, CRTC writeback storage, and VSP framebuffer mapping. It is invoked from `rcar_du_vsp_atomic_flush()` and `rcar_du_vsp_complete()`.

## Risks and Edge Cases

- Only RGB writeback formats are advertised because VSP outputs RGB to DU; YUV writeback is intentionally unsupported.
- `rcar_du_writeback_setup()` assumes atomic check and prepare populated `wb_state->format` and `job->priv`.
- Destination framebuffer plane count must fit the three SG table slots inherited from the VSP map helper.
- Completion depends on VSP reporting `VSP1_DU_STATUS_WRITEBACK`; missing status would leave jobs incomplete.

## Test Signals

Run DRM writeback tests for supported RGB formats, mismatched framebuffer sizes, unsupported formats, imported dma-buf destinations, completion signaling, cancellation/cleanup, and no leaked SG mappings after job failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.h

## Purpose

`rcar_du_writeback.h` exposes the small writeback integration surface between R-Car DU CRTC/VSP code and the optional DRM writeback implementation.

## Important APIs, Types, and Functions

It declares `rcar_du_writeback_init()`, `rcar_du_writeback_setup()`, and `rcar_du_writeback_complete()` when `CONFIG_DRM_RCAR_WRITEBACK` is enabled. Stubs return `-ENXIO` for init and no-op for setup/completion otherwise.

## Control Flow

CRTC setup can call init while building KMS objects. VSP atomic flush passes a `vsp1_du_writeback_config` to setup, and the VSP completion callback calls complete.

## State and Persistence Behavior

The header owns no state. It defines whether writeback is active at build time and controls the fallback behavior when writeback support is absent.

## Dependencies and Integration Points

It forward-declares R-Car DU and VSP config structures and includes DRM plane definitions. It integrates with `rcar_du_vsp.c` and CRTC initialization code.

## Risks and Edge Cases

Callers must tolerate `-ENXIO` when writeback is disabled. Setup and completion stubs silently drop work, so code must not queue writeback jobs unless init succeeded.

## Test Signals

Compile both with and without `CONFIG_DRM_RCAR_WRITEBACK`, and verify connector presence only when support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_writeback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_dw_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_dw_hdmi.c

## Purpose

`rcar_dw_hdmi.c` is the Renesas R-Car Gen3 wrapper around the Synopsys DesignWare HDMI bridge. It supplies R-Car PHY programming tables and a mode clock limit to the common `dw_hdmi` driver.

## Important APIs, Types, and Functions

`struct rcar_hdmi_phy_params` maps maximum pixel clocks to three PHY register values. `rcar_hdmi_mode_valid()` rejects modes above 297 MHz. `rcar_hdmi_phy_configure()` selects the first table entry whose `mpixelclock` covers the requested clock and writes PHY I2C registers through `dw_hdmi_phy_i2c_write()`. Probe/remove call `dw_hdmi_probe()` and `dw_hdmi_remove()` with `rcar_dw_hdmi_plat_data`.

## Control Flow

Platform probe creates the common DW-HDMI device and stores it as driver data. During mode validation the bridge rejects unsupported high clocks. During PHY setup the wrapper picks table parameters and programs PLL operation, current/GMP, and divider registers. Remove tears down the common bridge.

## State and Persistence Behavior

Persistent state is owned by the common DW-HDMI object. This wrapper keeps only constant platform data and PHY tables. PHY register state persists in hardware until the common HDMI driver reprograms or powers down the block.

## Dependencies and Integration Points

It depends on `drm/bridge/dw_hdmi.h`, DRM mode validation, module/platform driver APIs, and the DT compatible `renesas,rcar-gen3-hdmi`. It integrates with DU encoder/bridge chains through the generic DW-HDMI bridge.

## Risks and Edge Cases

- PHY table coverage ends at 297 MHz; modes above that are rejected.
- The table uses upper-bound matching, so boundary values must match hardware characterization.
- No runtime PM or clock/reset handling is in this wrapper; those responsibilities are either unnecessary for this integration or owned elsewhere.

## Test Signals

Probe/remove under DT, EDID mode validation around 297 MHz, HDMI modes across all table thresholds, and PHY I2C write traces are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_dw_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.c

## Purpose

`rcar_lvds.c` implements the R-Car LVDS DRM bridge. It configures LVDS channel routing, bus format, simple and extended PLLs, dual-link companion encoders, runtime PM, resets, and bridge chaining to panels or downstream bridges.

## Important APIs, Types, and Functions

Important types are `rcar_lvds_device_info` for generation/quirks/PLL setup and `rcar_lvds` for bridge, clocks, reset, MMIO, companion, and link type. Exported helpers are `rcar_lvds_pclk_enable()`, `rcar_lvds_pclk_disable()`, `rcar_lvds_dual_link()`, and `rcar_lvds_is_connected()`. Key internals include PLL setup for Gen2/Gen3/D3/E3, `rcar_lvds_enable()`, `rcar_lvds_disable()`, bridge atomic enable/disable, DT companion parsing, clock acquisition, probe/remove, and runtime suspend/resume.

## Control Flow

Probe allocates a DRM bridge, applies SoC match quirks including an R8A7790 ES1 override, parses the downstream panel/bridge and optional companion LVDS encoder, maps MMIO, gets module and optional PLL input clocks, gets reset, enables runtime PM, and registers the bridge. Atomic enable resumes the device, recursively enables the companion for dual-link, programs control-signal routing and channel lane order, configures stripe mode, programs a PLL unless an extended PLL was already enabled explicitly, selects LVDS mode from connector bus format, powers channels/PLL/PHY in hardware-required order, waits for PLL startup, and releases reset. Disable reverses the sequence and handles companion shutdown. D3/E3 extended PLL users call the exported pixel-clock enable/disable path from DU clock code.

## State and Persistence Behavior

`rcar_lvds` persists as devm bridge storage. It stores the downstream bridge/panel, optional companion bridge reference, link type, MMIO, clocks, and reset. Hardware state persists in LVDS registers and PLL until bridge disable or explicit pclk disable. Runtime PM asserts reset and disables the module clock when idle.

## Dependencies and Integration Points

The file depends on DRM bridge/panel/of helpers, media bus format definitions, Linux clk/reset/runtime PM, SoC revision matching, and `rcar_lvds_regs.h`. It is used by R-Car DU encoder routing and by DU clock code for extended PLL platforms.

## Risks and Edge Cases

- PLL calculation for D3/E3 assumes at least one input clock and a valid candidate; callers must avoid using an uninitialized `pll_info`.
- Dual-link setup reaches into the companion bridge's private data, which the source marks as a FIXME.
- Extended PLL disable intentionally defers full LVDS disable to avoid DU vblank timeouts; sequencing changes can reintroduce stalls.
- Unsupported or absent LVDS bus formats fall back to JEIDA with warnings.
- The code is SoC-quirk-heavy; wrong compatible data can invert lanes, miss LVEN/PWD ordering, or disable dual-link.

## Test Signals

Test single-link and dual-link LVDS panels, even/odd and odd/even pixel ordering, JEIDA/VESA/mirror bus formats, D3/E3 extended PLL dot-clock-only use, runtime suspend/resume, probe deferral of companion bridges, and mode clamping between minimum and 148.5 MHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.h

## Purpose

`rcar_lvds.h` declares the public helper interface for the R-Car LVDS bridge, mainly for DU code that needs to control LVDS-provided pixel clocks or query link/connection state.

## Important APIs, Types, and Functions

The exported functions are `rcar_lvds_pclk_enable()`, `rcar_lvds_pclk_disable()`, `rcar_lvds_dual_link()`, and `rcar_lvds_is_connected()`. Build-time stubs return `-ENOSYS` or `false` when `CONFIG_DRM_RCAR_LVDS` is disabled.

## Control Flow

DU clock/output code calls the pclk helpers around modeset on extended-PLL platforms. Encoder-routing code can query whether the bridge is dual-link or connected.

## State and Persistence Behavior

The header has no state. The bridge implementation owns clock and connection state.

## Dependencies and Integration Points

It only forward-declares `struct drm_bridge`. It is included by R-Car DU code without forcing the LVDS implementation to be built in.

## Risks and Edge Cases

Callers must handle `-ENOSYS` on disabled builds and must not assume a disconnected LVDS bridge can provide a valid output, except for D3/E3 dot-clock-only cases handled by the implementation.

## Test Signals

Build matrix coverage with LVDS enabled/disabled and modesets that use LVDS as both an output bridge and a clock provider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds_regs.h

## Purpose

`rcar_lvds_regs.h` defines register offsets and bitfields for the R-Car LVDS encoder and its Gen2, Gen3, D3, and E3 PLL variants.

## Important APIs, Types, and Functions

The macro API covers `LVDCR0`, `LVDCR1`, `LVDPLLCR`, `LVDCTRCR`, `LVDCHCR`, `LVDSTRIPE`, `LVDSCR`, and `LVDDIV`. Fields encode LVDS mode, power/reset/enable ordering, channel standby/routing, simple PLL delays/dividers, extended PLL source and multiplier/divider settings, control-signal muxing, dual-link striping, and output divider control.

## Control Flow

`rcar_lvds.c` uses these definitions to build register values during enable, disable, PLL setup, lane routing, and dual-link striping. The macros encode generation-specific fields that must be selected by SoC quirk data.

## State and Persistence Behavior

The header owns no software state. It describes persistent hardware register state written by the LVDS driver.

## Dependencies and Integration Points

It integrates only with the R-Car LVDS bridge implementation and hardware documentation. No external Linux APIs are required beyond the preprocessor.

## Risks and Edge Cases

- Many bits have different meanings between Gen2 and Gen3 (`BEN` vs `PWD`, simple vs extended PLL fields).
- Extended PLL field macros do not mask inputs, so callers must validate ranges.
- Incorrect channel or stripe settings can produce swapped lanes or wrong dual-link pixel order.

## Test Signals

Register trace comparison against expected LVDS enable/disable sequences on Gen2, Gen3, D3, and E3 platforms is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_lvds_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.c

## Purpose

`rcar_mipi_dsi.c` implements the R-Car V3U/V4H MIPI DSI host and DRM bridge. It calculates PLL/PHY parameters, initializes the D-PHY, configures video timings, starts/stops HS/video transmission, registers a MIPI DSI host for panel commands, and exposes DU pixel-clock enable/disable hooks.

## Important APIs, Types, and Functions

Key types are `rcar_mipi_dsi_device_info`, `rcar_mipi_dsi`, `dsi_setup_info`, and `dsi_clk_config`. Exported functions are `rcar_mipi_dsi_pclk_enable()` and `rcar_mipi_dsi_pclk_disable()`. Internals include PHTW write helpers, V3U/V4H PHY init tables, PLL calculation, display timing programming, startup/shutdown, HS clock and video start/stop, bridge callbacks, host attach/detach, and command TX/RX transfer handlers.

## Control Flow

Probe allocates the bridge object, parses DT data-lane count, maps MMIO, gets module/PLL/DSI clocks, gets reset, and registers a MIPI DSI host. Host attach validates lanes, records panel format/mode flags, resolves the downstream bridge, and registers the DRM bridge. DU modeset code calls `pclk_enable()`, which enables clocks/reset, calculates DSI PLL and D-PHY settings from adjusted mode clock, initializes PHY test registers, programs lane count and VCLK, writes video timing registers, and starts the HS clock. Bridge atomic enable starts video transmission; atomic disable stops it. Host transfer builds DSI packets, writes register-based payloads up to 16 bytes, polls completion, optionally performs BTA/RX parsing, and delays between commands for panel tolerance.

## State and Persistence Behavior

The `rcar_mipi_dsi` object persists as the host/bridge state and stores clocks, reset, format, mode flags, lane count, and downstream bridge. Startup state persists in DSI registers until shutdown. Command transfers use only stack payload buffers and hardware registers. There is no runtime PM wrapper here; clock/reset state is controlled explicitly by pclk hooks.

## Dependencies and Integration Points

The driver depends on DRM bridge/MIPI DSI helpers, Linux clk/reset/iopoll/io APIs, `rcar_mipi_dsi_regs.h`, and DU encoder code that calls pclk hooks. It integrates with downstream panel/bridge devices via the MIPI DSI host attach flow.

## Risks and Edge Cases

- Register-based command mode supports only 16-byte TX/RX payloads; larger panel commands return `-EOPNOTSUPP`.
- `rcar_mipi_dsi_parameters_calc()` can leave `setup_info` incomplete if no clock config fits; later use must be covered by mode validation and tested.
- RX long-packet loop uses `RXPPD0R + i`, which increments by bytes while registers are 32-bit spaced in the header; this deserves hardware verification.
- Clock enable error unwinding must keep reset/clock state balanced.
- Mode validation only caps pixel clock at 297 MHz, not all lane/bpp/PLL corner cases.

## Test Signals

Build/probe for V3U and V4H compatibles, DSI panels using 1-4 lanes and 16/18/24 bpp, mode validation around clock limits, command-mode short/long read/write up to 16 bytes, HS clock start/stop polling, video start/stop polling, and failure injection for clock/PHY timeouts are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.h

## Purpose

`rcar_mipi_dsi.h` declares the DU-facing pixel-clock control hooks for the R-Car MIPI DSI bridge.

## Important APIs, Types, and Functions

It exposes `rcar_mipi_dsi_pclk_enable(struct drm_bridge *, struct drm_atomic_state *)` and `rcar_mipi_dsi_pclk_disable(struct drm_bridge *)`, with no-op stubs when `CONFIG_DRM_RCAR_MIPI_DSI` is disabled.

## Control Flow

DU modeset code calls enable before video output is started so the DSI block can configure clocks, PHY, and timings from the atomic state. Disable tears down the DSI block after video is stopped.

## State and Persistence Behavior

No state is owned by the header. The bridge implementation stores lane/format/mode information gathered during host attach.

## Dependencies and Integration Points

The header forward-declares DRM atomic state and bridge types and is included by R-Car DU output code.

## Risks and Edge Cases

No-op stubs can hide missing DSI support if callers do not gate output availability on bridge presence. The enable hook returns void, so startup failures are logged but not propagated to atomic commit.

## Test Signals

Build with DSI enabled/disabled and modeset a DSI panel while checking that failures in clock/PHY startup are visible in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi_regs.h

## Purpose

`rcar_mipi_dsi_regs.h` defines register offsets and bitfields for the R-Car V3U/V4H DSI link, command transfer engine, video mode engine, PPI, clocks, PHY setup, PLL, and PHY test interface.

## Important APIs, Types, and Functions

Macro groups cover link status (`LINKSR`), lane count (`TXSETR`), command TX/RX registers (`TXCM*`, `RX*`, `TOS*`), video mode registers (`TXVM*`), PPI lane status/control (`PPI*`), clock controls (`LPCLKSET`, `CFGCLKSET`, `VCLKSET`, `VCLKEN`), `PHYSETUP`, `CLOCKSET*`, and PHY test registers (`PHTW`, `PHTR`, `PHTC`). Bitfield helpers use `FIELD_PREP()` and `GENMASK_U32()`.

## Control Flow

The MIPI DSI driver composes these macros during PHY/PLL initialization, lane setup, timing programming, HS clock transitions, video start/stop, and command-mode transfers.

## State and Persistence Behavior

The header defines hardware state only. Registers retain configuration until shutdown, reset assertion, or subsequent writes.

## Dependencies and Integration Points

It requires Linux bitfield/bit macros through included driver context and is consumed by `rcar_mipi_dsi.c`.

## Risks and Edge Cases

- Register offsets and bit widths are tightly coupled to V3U/V4H hardware manuals.
- RX payload registers are defined as 32-bit spaced (`RXPPD0R`..`RXPPD3R`), so consumers must increment by register spacing rather than byte count.
- Macro inputs are generally not range-checked.

## Test Signals

Register write tracing for DSI startup/shutdown and command transfers, plus compile checks for field macros, provide the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_mipi_dsi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Kconfig

## Purpose

`rz-du/Kconfig` defines build-time options for the RZ/G2L Display Unit DRM driver and its embedded MIPI DSI encoder.

## Important APIs, Types, and Functions

`DRM_RZG2L_DU` is the main tristate driver option. It depends on Renesas architecture or compile testing, DRM, OF, and `VIDEO_RENESAS_VSP1`, and selects DRM client, GEM DMA, KMS, display-helper, bridge-connector, and videomode helpers. `DRM_RZG2L_USE_MIPI_DSI` is a user-visible bool gated by DRM bridge/OF and the DU driver. `DRM_RZG2L_MIPI_DSI` is a derived tristate selecting `DRM_MIPI_DSI`.

## Control Flow

Kconfig controls whether `rzg2l-du-drm.o`, `rzg2l_du_vsp.o`, and `rzg2l_mipi_dsi.o` are built. The MIPI DSI implementation is enabled when the DU driver and DSI support option are enabled.

## State and Persistence Behavior

No runtime state exists. Build configuration determines available modules and stub behavior in headers.

## Dependencies and Integration Points

The options integrate with the DRM subsystem, VSP1 media driver, OF graph, MIPI DSI core, and the Makefile in the same directory.

## Risks and Edge Cases

The main DU depends on VSP1 because the driver is VSP-fed. Disabling MIPI DSI still permits DPAD-style output where supported by DT/SoC routing.

## Test Signals

Configuration tests should build DU as built-in and module, with MIPI DSI enabled and disabled, and under `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Makefile

## Purpose

`rz-du/Makefile` wires the RZ/G2L Display Unit and MIPI DSI source files into kernel objects.

## Important APIs, Types, and Functions

It builds `rzg2l-du-drm.o` from `rzg2l_du_crtc.o`, `rzg2l_du_drv.o`, `rzg2l_du_encoder.o`, and `rzg2l_du_kms.o`, conditionally adds `rzg2l_du_vsp.o` under `CONFIG_VIDEO_RENESAS_VSP1`, and builds `rzg2l_mipi_dsi.o` under `CONFIG_DRM_RZG2L_MIPI_DSI`.

## Control Flow

Kbuild uses the config symbols from `Kconfig` to select the DU aggregate object and optional DSI bridge module.

## State and Persistence Behavior

No runtime state exists. The Makefile defines link composition and module boundaries.

## Dependencies and Integration Points

It integrates with kernel Kbuild and the local Kconfig symbols.

## Risks and Edge Cases

Because `DRM_RZG2L_DU` depends on VSP1, omitting `rzg2l_du_vsp.o` would normally not happen for valid configs; compile-test combinations should still cover the conditional object.

## Test Signals

Run kernel builds for enabled, module, disabled, and MIPI DSI combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.c

## Purpose

`rzg2l_du_crtc.c` implements the single CRTC used by the RZ/G2L DU driver. It programs DU timing registers, manages clocks/reset, starts/stops display output, coordinates VSP enable/flush, and handles vblank/page-flip events.

## Important APIs, Types, and Functions

Public functions are `rzg2l_du_crtc_create()` and `rzg2l_du_crtc_finish_page_flip()`. Important internals include `rzg2l_du_crtc_set_display_timing()`, `rzg2l_du_crtc_setup()`, `rzg2l_du_crtc_get()`, `rzg2l_du_crtc_put()`, `rzg2l_du_crtc_start/stop()`, atomic enable/disable/flush callbacks, custom CRTC state duplication/reset, and vblank enable/disable callbacks.

## Control Flow

Creation gets shared reset and `aclk`, `pclk`, and `vclk`, initializes the flip wait queue, obtains the primary VSP plane for the selected pipe, initializes the DRM CRTC, and attaches helper callbacks. Atomic enable idempotently enables bus/peripheral clocks, deasserts reset, programs display timings and pixel clock, enables VSP LIF, turns vblank on, then sets `DU_MCR0_DI_EN`. Atomic flush arms a pending page-flip event under `event_lock` and flushes the VSP pipe. The VSP completion callback calls `finish_page_flip()`, which sends the vblank event and drops the vblank reference. Atomic disable waits for pending flips, disables vblank and VSP, stops DU output, gates clocks, asserts reset, and sends any disable event.

## State and Persistence Behavior

`struct rzg2l_du_crtc` persists inside `rzg2l_du_device` and stores clock/reset handles, VSP pointer/pipe, event pointer, wait queue, vblank flag, and `initialized` guard. Hardware timing and enable bits persist while clocks/reset are active.

## Dependencies and Integration Points

The CRTC depends on DRM atomic/vblank helpers, Linux clock/reset APIs, `rzg2l_du_vsp`, and the DU MMIO block in `rzg2l_du_device`. It is created from `rzg2l_du_modeset_init()`.

## Risks and Edge Cases

- `rzg2l_du_crtc_set_display_timing()` enables `dclk` before setting its rate and does not check return values.
- Page flip timeout forcibly completes the event after 50 ms; this prevents userspace hangs but can mask hardware/VSP stalls.
- Atomic enable ignores the return from `rzg2l_du_crtc_get()`, so a clock/reset failure may still fall through to start.
- The driver assumes one CRTC and one DU register block.

## Test Signals

Mode-set tests should check timing register programming, vclk rate, enable/disable sequencing, page-flip completion under VSP callbacks, vblank enable/disable, suspend/shutdown paths, and failure injection for clocks/resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.h

## Purpose

`rzg2l_du_crtc.h` defines the RZ/G2L DU CRTC private data and CRTC state extensions.

## Important APIs, Types, and Functions

`struct rzg2l_du_crtc` embeds `drm_crtc` and stores DU device, initialization flag, vblank flag, pending event, flip wait queue, VSP pointer/pipe, optional source names, reset, and three clocks. `struct rzg2l_du_crtc_state` extends DRM CRTC state with output routing bits. Inline conversions expose container lookups. Public declarations are `rzg2l_du_crtc_create()` and `rzg2l_du_crtc_finish_page_flip()`.

## Control Flow

KMS init populates the structure before registering the CRTC. Atomic callbacks duplicate/destroy/reset the extended state and use the private data for VSP and clock control.

## State and Persistence Behavior

The structure persists for the DRM device lifetime. The `event` field is protected by DRM `event_lock`; `initialized` protects repeated clock/reset enable.

## Dependencies and Integration Points

It depends on DRM CRTC/writeback headers, Linux wait/spinlock/container helpers, `media/vsp1.h`, and forward declarations for reset/clock/VSP types.

## Risks and Edge Cases

The `outputs` field is defined but not heavily used in this subset, so future routing changes must keep it synchronized with encoder possible CRTC masks. Event locking rules must be preserved.

## Test Signals

Atomic state duplication/reset tests and page-flip event lifecycle tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.c

## Purpose

`rzg2l_du_drv.c` is the platform DRM driver for RZ/G2L Display Unit devices. It provides SoC routing data, allocates the DRM device, maps MMIO, sets DMA constraints, initializes KMS, registers the DRM device, and handles remove/shutdown.

## Important APIs, Types, and Functions

SoC data tables describe `r9a07g043u`, `r9a07g044`, and `r9a09g057` channel masks and output ports. `rzg2l_du_output_name()` formats output names. `rzg2l_du_probe()`, `rzg2l_du_remove()`, and `rzg2l_du_shutdown()` implement platform lifecycle. `rzg2l_du_driver` advertises GEM, modeset, and atomic support with GEM DMA/fbdev helpers.

## Control Flow

Probe exits when firmware-only DRM drivers are requested, allocates a managed DRM device, stores device info from OF match data, maps MMIO, coerces DMA to 32-bit coherent, initializes modeset objects, registers the DRM device, logs probe success, and starts DRM client setup. Remove unregisters the DRM device, performs atomic shutdown, and finalizes polling. Shutdown performs atomic shutdown only.

## State and Persistence Behavior

`struct rzg2l_du_device` persists as the DRM private object and stores MMIO, device info, CRTC, and VSP structures. Hardware state is shut down through DRM atomic helper paths on remove/shutdown.

## Dependencies and Integration Points

The file depends on platform/OF APIs, DRM core/client/GEM DMA helpers, DMA mask helpers, and `rzg2l_du_modeset_init()`. It binds to Renesas DU compatible strings.

## Risks and Edge Cases

- DMA is forced to 32-bit; buffers outside addressable range must be rejected or bounced by DMA infrastructure.
- Probe error path only finalizes KMS polling after modeset init failure; managed DRM allocation handles most object cleanup.
- Routing tables must match DT port numbering and hardware output capabilities.

## Test Signals

Probe/remove/shutdown on all compatibles, 32-bit DMA buffer allocation, no encoder case, firmware-only suppression, and module unload/reload are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.h

## Purpose

`rzg2l_du_drv.h` defines the top-level RZ/G2L DU device model, output identifiers, routing metadata, and conversion helper used across the driver.

## Important APIs, Types, and Functions

`enum rzg2l_du_output` names DSI0 and DPAD0. `rzg2l_du_output_routing` maps output IDs to possible CRTCs and DT ports. `rzg2l_du_device_info` contains the available channel mask and route array. `rzg2l_du_device` stores the Linux device, SoC info, MMIO, DRM device, one CRTC, and one VSP. `to_rzg2l_du_device()` and `rzg2l_du_output_name()` are the public helpers.

## Control Flow

Probe fills `rzg2l_du_device`, KMS init reads its routing data to create CRTCs/VSPs/encoders, and encoder code uses output names for diagnostics.

## State and Persistence Behavior

The structure persists for the platform device lifetime. Compile-time constants cap the driver to one CRTC, one VSP, and one DSI.

## Dependencies and Integration Points

It includes DRM device definitions and local CRTC/VSP headers, making it the central include for driver-private state.

## Risks and Edge Cases

The maximum counts encode current hardware support; adding multi-channel SoCs requires coordinated changes across arrays, routing, and modeset init loops.

## Test Signals

Compile-time coverage and probe tests for every route table validate this header's assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.c

## Purpose

`rzg2l_du_encoder.c` creates DRM encoders and bridge connectors for RZ/G2L DU outputs. It supports DPAD panel bridges and generic OF bridge chains, then attaches a bridge connector to the encoder.

## Important APIs, Types, and Functions

`rzg2l_du_encoder_count_ports()` detects simple panel-style DPAD nodes. `rzg2l_du_encoder_mode_valid()` caps DPAD0 mode clocks at 83.5 MHz. `rzg2l_du_encoder_init()` is the public constructor. The private `rzg2l_du_encoder` stores the output ID in addition to `drm_encoder`.

## Control Flow

KMS output enumeration passes an output enum and connected DT node. For DPAD with a single port, the code treats the node as a panel and creates a DPI panel bridge. Otherwise it looks up a DRM bridge and may defer probe. It allocates a managed DRM encoder, sets the output ID, attaches the bridge without creating a connector, creates a `drm_bridge_connector`, and attaches it to the encoder.

## State and Persistence Behavior

The encoder is managed by DRM and stores only the output enum. Downstream bridge/panel objects own their own state.

## Dependencies and Integration Points

It depends on OF graph helpers, DRM bridge/panel/connector helpers, and `rzg2l_du_output_name()`. It is called from `rzg2l_du_kms.c`.

## Risks and Edge Cases

- `rzg2l_du_encoder_count_ports()` treats a single-port DPAD node as a panel; unusual DT graph layouts can alter behavior.
- DPAD has an 83.5 MHz clock cap; other output-specific limits are delegated to downstream bridges.
- Bridge lookup returns `-EPROBE_DEFER` when missing, which bubbles to modeset init.

## Test Signals

DT tests for DPAD panel, DPAD external bridge, DSI bridge, disabled remote nodes, and DPAD clock validation around 83.5 MHz are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.h

## Purpose

`rzg2l_du_encoder.h` declares the RZ/G2L DU encoder private type and constructor.

## Important APIs, Types, and Functions

`struct rzg2l_du_encoder` embeds `drm_encoder` and stores the `enum rzg2l_du_output`. `to_rzg2l_encoder()` provides container conversion. `rzg2l_du_encoder_init()` creates encoders for DT output nodes.

## Control Flow

KMS init creates encoders through this header and later casts DRM encoder objects back to private encoders when assigning possible CRTCs and clones.

## State and Persistence Behavior

The output enum persists with the DRM encoder and is used for routing decisions and validation.

## Dependencies and Integration Points

It depends on DRM encoder types, Linux `container_of`, and `struct rzg2l_du_device`.

## Risks and Edge Cases

The header references `enum rzg2l_du_output`, so include ordering must provide the enum via the driver header.

## Test Signals

Compile coverage and encoder-list iteration in KMS init are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.c

## Purpose

`rzg2l_du_kms.c` builds the RZ/G2L KMS topology and format/framebuffer policy. It defines supported framebuffer formats, validates framebuffer creation, initializes mode config, discovers VSPs and output encoders from DT, creates the CRTC, and assigns encoder routing masks.

## Important APIs, Types, and Functions

Public functions are `rzg2l_du_format_info()`, `rzg2l_du_dumb_create()`, and `rzg2l_du_modeset_init()`. Important internals are `rzg2l_du_fb_create()`, `rzg2l_du_encoders_init_one()`, `rzg2l_du_encoders_init()`, and `rzg2l_du_vsps_init()`.

## Control Flow

Modeset init creates mode config, sets size limits to 1920x1920, initializes vblank for available CRTCs, parses `renesas,vsps` to bind CRTC indices to VSP devices/pipes, initializes VSP planes, creates the CRTC, scans DT endpoints for outputs, maps endpoint ports to SoC routes, initializes encoders, errors if none are usable, assigns `possible_crtcs` and clone masks, resets mode config, and starts connector polling. Framebuffer creation rejects unsupported formats and pitches above the VSP 65535-byte limit. Dumb buffer creation aligns pitch to `16 * cpp`.

## State and Persistence Behavior

Supported format metadata is static. Runtime KMS state is stored in `rzg2l_du_device`, DRM mode_config, VSP objects, CRTC, planes, encoders, and connectors. DT node references acquired during VSP parsing are released in all exit paths.

## Dependencies and Integration Points

It depends on DRM atomic/GEM framebuffer/vblank helpers, OF graph/platform APIs, VSP1, local CRTC/encoder/VSP types, and V4L2 pixel format constants.

## Risks and Edge Cases

- `rzg2l_du_vsps_init()` computes `cells = ret / rcdu->num_crtcs - 1` without first checking `ret < 0`, so malformed/missing `renesas,vsps` can produce misleading results.
- The driver is currently sized for one CRTC/VSP; multi-CRTC hardware requires revisiting loops and arrays.
- Only the first pitch is validated; multi-plane pitch relationships are delegated to helpers/VSP behavior.
- Encoder probe deferral aborts the whole modeset init, while other encoder failures are skipped.

## Test Signals

Test all supported formats, invalid pitches, DT endpoint route matching, missing/disabled remote endpoints, absent encoders, VSP phandle parsing errors, and boot to fbdev on each supported SoC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.h

## Purpose

`rzg2l_du_kms.h` declares KMS-level format metadata and entry points for RZ/G2L DU mode setting and dumb-buffer creation.

## Important APIs, Types, and Functions

`struct rzg2l_du_format_info` maps DRM fourcc to V4L2 format, plane count, and horizontal subsampling. The public functions are `rzg2l_du_format_info()`, `rzg2l_du_modeset_init()`, `rzg2l_du_dumb_create()`, and a declared GEM prime SG import helper.

## Control Flow

Driver probe calls `rzg2l_du_modeset_init()`. Framebuffer creation and VSP plane setup call `rzg2l_du_format_info()`. DRM dumb-buffer ioctl handling uses `rzg2l_du_dumb_create()`.

## State and Persistence Behavior

No state is owned here; it defines static format metadata interfaces.

## Dependencies and Integration Points

It forward-declares DRM and DMA-buf types and is included by CRTC/VSP/KMS implementation files.

## Risks and Edge Cases

The declared `rzg2l_du_gem_prime_import_sg_table()` is not implemented in this subset, so link coverage should confirm no stale reference exists or an implementation is elsewhere.

## Test Signals

Compile/link tests and format lookup coverage for every advertised VSP format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.c

## Purpose

`rzg2l_du_vsp.c` implements the RZ/G2L DU compositor interface to VSP1. It creates DRM planes backed by VSP inputs, configures the VSP LIF for the CRTC, converts plane state to VSP atomic updates, and converts VSP completion callbacks into vblank/page-flip/CRC events.

## Important APIs, Types, and Functions

Public functions are `rzg2l_du_vsp_init()`, `rzg2l_du_vsp_enable()`, `rzg2l_du_vsp_disable()`, `rzg2l_du_vsp_atomic_flush()`, and `rzg2l_du_vsp_get_drm_plane()`. Internals include `rzg2l_du_vsp_complete()`, `rzg2l_du_vsp_plane_setup()`, `__rzg2l_du_vsp_plane_atomic_check()`, and DRM plane state callbacks.

## Control Flow

VSP init finds the VSP device from DT, registers cleanup, calls `vsp1_du_init()`, and allocates two managed universal planes: one primary for the connected CRTC and one overlay. CRTC enable calls `vsp1_du_setup_lif()` with mode size and completion callback. Atomic plane check validates no scaling and resolves format. Plane update converts source/destination rectangles, DMA addresses from GEM DMA objects, alpha, zpos, blend mode, and V4L2 pixel format into VSP config. Atomic flush sends the pipe config to VSP.

## State and Persistence Behavior

`rzg2l_du_vsp` stores only VSP index, supplier device, and DU pointer. Plane-private state stores the resolved format for the current atomic state. Unlike the R-Car version, this code uses contiguous GEM DMA addresses directly instead of SG map/unmap state.

## Dependencies and Integration Points

It depends on DRM atomic/GEM DMA helpers, VSP1 media API, RZ/G2L KMS format metadata, and CRTC page-flip functions.

## Risks and Edge Cases

- Direct `gem->dma_addr` use assumes buffers are contiguous and mapped for the VSP/DMA domain.
- Only ARGB1555/4444/8888 are converted to XRGB variants for pixel-none blending; other alpha-capable formats are not listed here.
- `rzg2l_du_vsp_get_drm_plane()` iterates all planes and returns `ERR_PTR(-EINVAL)` if no index matches; CRTC creation depends on VSP planes already being initialized.
- There is no explicit device link to enforce DU/VSP suspend ordering, unlike the R-Car VSP path.

## Test Signals

Plane updates for all supported formats, primary/overlay selection by VSP pipe, page-flip/vblank completion, CRC events, contiguous DMA buffer assumptions, and suspend/resume with VSP are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.h

## Purpose

`rzg2l_du_vsp.h` declares the RZ/G2L DU to VSP compositor types and function interface.

## Important APIs, Types, and Functions

`struct rzg2l_du_vsp_plane` embeds a DRM plane and stores VSP index/parent. `struct rzg2l_du_vsp` stores index, VSP device, and DU device. `struct rzg2l_du_vsp_plane_state` extends plane state with resolved format metadata. The header exports VSP init, enable/disable, atomic flush, and plane lookup, with `CONFIG_VIDEO_RENESAS_VSP1` stubs returning `-ENXIO` or `ERR_PTR(-ENXIO)`.

## Control Flow

KMS init creates VSP planes before CRTC creation. CRTC and plane callbacks then use the declared functions for display enable and atomic updates.

## State and Persistence Behavior

The header defines persistent VSP/plane structures and per-atomic plane state. No state is allocated by the header.

## Dependencies and Integration Points

It depends on DRM plane types, Linux scatterlist/container helpers, and forward declarations for RZ/G2L DU/CRTC types.

## Risks and Edge Cases

Stub behavior must be handled by KMS init. Include ordering must make `struct rzg2l_du_crtc` visible where inline stubs are used.

## Test Signals

Build with VSP1 enabled and disabled; verify CRTC creation fails cleanly without VSP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_vsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi.c

## Purpose

`rzg2l_mipi_dsi.c` implements the RZ/G2L and RZ/V2H MIPI DSI host/bridge driver. It handles SoC-specific D-PHY/PLL setup, runtime PM resets, video timing programming, HS/video start-stop, MIPI DSI command transfers through descriptor memory, and bridge chaining to panels.

## Important APIs, Types, and Functions

Key types are `rzg2l_mipi_dsi_hw_info`, `rzv2h_dsi_mode_calc`, `rzg2l_mipi_dsi`, timing tables, and RZ/V2H PLL limit data. Important functions include RZ/G2L D-PHY init/exit, RZ/V2H timing lookup and PLL calculation, startup/stop, display timing programming, HS clock/video start-stop, bridge atomic pre-enable/enable/disable/post-disable, host attach/detach/transfer, runtime PM callbacks, probe/remove, and SoC info tables.

## Control Flow

Probe allocates a bridge object, reads DT data lanes, maps MMIO, gets `vclk`/`lpclk` and resets, enables runtime PM, temporarily initializes the D-PHY at 80 Mbps to read lane capability, exits the PHY, registers the DSI host, and allocates a coherent 128-byte DCS buffer. Host attach validates lane count and bpp, records format/lane/mode flags, resolves the downstream bridge, registers the DRM bridge, and programs a CPG DSI divider. Atomic pre-enable resumes runtime PM, configures clocks and D-PHY for the adjusted mode, and writes video timing registers. Atomic enable starts HS clock and video. Atomic disable stops video and HS clock; post-disable exits the PHY and releases runtime PM. Host transfers build descriptors, copy long payloads into coherent memory, start sequence channel 0, poll completion, and parse optional responses.

## State and Persistence Behavior

`rzg2l_mipi_dsi` persists as the platform driver's host/bridge state, storing lane/format/mode flags, clock/reset handles, MMIO, SoC function table, CPG mode calculation cache, and coherent DCS buffer. Runtime PM asserts/deasserts APB/peripheral resets; D-PHY reset/PLL state is separately controlled by SoC-specific init/exit functions.

## Dependencies and Integration Points

The file depends on DRM bridge/MIPI DSI helpers, Linux clk/reset/runtime PM/DMA/iopoll APIs, Renesas CPG PLL helpers (`RZV2H_CPG` namespace), `rzg2l_mipi_dsi_regs.h`, and downstream panel/bridge drivers. It integrates with the RZ DU encoder through the bridge chain.

## Risks and Edge Cases

- `rzv2h_dsi_timings_tables[TLPXCTL]` contains duplicate `.base_value = 0` initializers, which is a compile-time warning/error depending on compiler settings and should be cleaned up.
- `rzg2l_mipi_dsi_set_display_timing()` has no default case for unsupported bpp; host attach prevents most cases, but defensive initialization is still weak.
- Coherent DCS buffer allocation happens after host registration; an allocation failure returns without unregistering the host or disabling runtime PM.
- Descriptor command transfer payload is capped at 128 bytes by `RZG2L_DCS_BUF_SIZE`.
- `rzg2l_cpg_dsi_div_set_divider()` is global SoC clock state; multi-DSI or concurrent mode changes would need care.

## Test Signals

Probe/remove for both compatibles, host attach for 1-4 lanes and 16/18/24 bpp rules, mode validation for min/max clocks and RZ/V2H PLL fit, DCS short/long read/write including 128-byte boundary, runtime PM reset sequencing, video start/stop polling, and fault injection around DCS allocation and PHY startup are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi_regs.h

## Purpose

`rzg2l_mipi_dsi_regs.h` defines register offsets and bitfields for the RZ/G2L and RZ/V2H MIPI DSI D-PHY and link blocks.

## Important APIs, Types, and Functions

Macro groups cover classic RZ/G2L D-PHY control/timing registers, RZ/V2H PLL/PHY reset and timing registers, link status, lane and HS clock controls, DSI receive result slots, clock-lane and LP transition timing, video-input channel programming, and sequence-channel descriptor registers for command transfer.

## Control Flow

`rzg2l_mipi_dsi.c` uses these macros during SoC-specific D-PHY initialization, PLL programming, HS clock start/stop, video timing programming, command descriptor setup, and response parsing.

## State and Persistence Behavior

No software state exists. The macros describe hardware register state that persists until reset, runtime suspend, or driver reprogramming.

## Dependencies and Integration Points

It depends on Linux `bits.h` and is consumed by the RZ/G2L MIPI DSI implementation.

## Risks and Edge Cases

- Some macros use plain shifts while others use `GENMASK`; callers must use `FIELD_PREP()` only with mask macros.
- Register offsets are interpreted relative to SoC-specific `phy_reg_offset` and `link_reg_offset`.
- Descriptor address register stores a 32-bit physical address, matching the current coherent buffer assumption.

## Test Signals

Compile checks, register trace validation for RZ/G2L and RZ/V2H startup, and descriptor command transfer tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_mipi_dsi_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Kconfig

## Purpose

`shmobile/Kconfig` defines the build option for the legacy Renesas SH Mobile DRM driver.

## Important APIs, Types, and Functions

`DRM_SHMOBILE` is a tristate option depending on DRM, PM, Renesas/SH Mobile architecture or compile testing, and selecting backlight, DRM client, KMS/display helpers, bridge connector, GEM DMA helper, and videomode helpers.

## Control Flow

The option controls whether `shmob-drm.o` is built by the Makefile.

## State and Persistence Behavior

No runtime state exists; this file affects build composition only.

## Dependencies and Integration Points

It integrates with kernel Kconfig, DRM helper libraries, and the local Makefile.

## Risks and Edge Cases

The driver supports both platform-data and OF paths, so build coverage should include PM and OF-dependent helper availability.

## Test Signals

Build as built-in, module, and under `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Makefile

## Purpose

`shmobile/Makefile` defines the object composition for the legacy SH Mobile DRM module.

## Important APIs, Types, and Functions

`shmob-drm-y` links `shmob_drm_crtc.o`, `shmob_drm_drv.o`, `shmob_drm_kms.o`, and `shmob_drm_plane.o`. `obj-$(CONFIG_DRM_SHMOBILE)` adds the aggregate object to the build.

## Control Flow

Kbuild includes the module when `DRM_SHMOBILE` is enabled.

## State and Persistence Behavior

No runtime state exists.

## Dependencies and Integration Points

It integrates with the local Kconfig and Kbuild.

## Risks and Edge Cases

The plane implementation is outside this work item but is required for link completeness.

## Test Signals

Full module link tests confirm all listed objects and symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.c

## Purpose

`shmob_drm_crtc.c` implements CRTC, encoder, and connector handling for the legacy SH Mobile LCDC DRM driver. It programs display timing/format registers, handles page flips and vblank events, creates primary/overlay planes, supports platform-data connectors, and supports OF bridge connectors.

## Important APIs, Types, and Functions

Public functions are `shmob_drm_crtc_create()`, `shmob_drm_crtc_finish_page_flip()`, `shmob_drm_encoder_create()`, and `shmob_drm_connector_create()`. Internals include bus format mapping, `shmob_drm_crtc_setup_geometry()`, start/stop, atomic enable/disable/flush, legacy page flip, vblank enable/disable, encoder mode fixup, and platform-data connector helpers.

## Control Flow

CRTC creation initializes the flip wait queue, creates one primary and four overlay planes, initializes the DRM CRTC, attaches helpers, and starts with vblank off. Atomic enable resumes runtime PM, resets/enables LCDC, stops output and masks interrupts, configures power/dot clock, writes geometry and bus format based on connector display info, enables display output, starts LCDC, and turns vblank on. Disable waits for any page flip, disables vblank, stops LCDC, disables output, and drops runtime PM. IRQ-side completion is in the driver file. Encoder creation either attaches a simple DPI encoder for platform-data mode or attaches an OF bridge. Connector creation either builds a legacy fixed-mode connector from platform data or uses `drm_bridge_connector_init()`.

## State and Persistence Behavior

`struct shmob_drm_crtc` stores the DRM CRTC, pending event pointer, and wait queue. Platform-data connectors store a fixed `videomode`. Hardware state persists in LCDC registers while runtime PM keeps the clock enabled.

## Dependencies and Integration Points

The file depends on DRM atomic/bridge/connector/vblank helpers, Linux OF/PM runtime/clk headers, video mode conversion, local plane code, driver state, KMS format metadata, and LCDC register macros.

## Risks and Edge Cases

- `shmob_drm_crtc_start_stop()` busy-waits on power status with no timeout.
- The atomic flush path sends CRTC state events immediately, while legacy page flip events wait for vblank; this difference should be intentional.
- Clock divider programming has a FIXME for SH7724 divider limitations.
- Platform-data connector cleanup path calls `drm_connector_cleanup()` on error, while the allocated wrapper may require careful ownership handling.

## Test Signals

Legacy platform-data fixed panel, OF bridge panel, all supported bus formats/flags, page flip/vblank event ordering, overlay plane creation, runtime PM enable/disable, and LCDC stop timeout behavior should be tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.h

## Purpose

`shmob_drm_crtc.h` declares the legacy SH Mobile CRTC, connector wrapper, and CRTC/encoder/connector constructors.

## Important APIs, Types, and Functions

`struct shmob_drm_crtc` embeds `drm_crtc` and stores pending page-flip event/wait queue. `struct shmob_drm_connector` embeds `drm_connector`, stores a preferred encoder, and points to a fixed `videomode`. The header declares CRTC creation, page-flip completion, encoder creation, and connector creation.

## Control Flow

Driver modeset init calls the constructors, and IRQ handling calls `shmob_drm_crtc_finish_page_flip()` on vblank.

## State and Persistence Behavior

The CRTC persists in `shmob_drm_device`. Connector wrappers are dynamically allocated for platform-data mode and destroyed through connector funcs.

## Dependencies and Integration Points

It depends on DRM CRTC/connector/encoder headers and video mode definitions.

## Risks and Edge Cases

Event fields require DRM `event_lock` synchronization. The connector wrapper is only valid for platform-data fixed-panel mode.

## Test Signals

Compile coverage and page-flip event lifecycle tests validate the header contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.c

## Purpose

`shmob_drm_drv.c` is the platform DRM driver for legacy Renesas SH Mobile LCDC hardware. It selects clocks, allocates the DRM device, maps MMIO, initializes KMS and IRQ handling, manages runtime/system PM, and registers the DRM device.

## Important APIs, Types, and Functions

Important functions are `shmob_drm_setup_clocks()`, `shmob_drm_irq()`, system/runtime PM callbacks, `shmob_drm_probe()`, `shmob_drm_remove()`, and `shmob_drm_shutdown()`. `shmob_drm_driver` advertises GEM/modeset/atomic support with GEM DMA and fbdev helpers. OF match data supplies `shmob_arm_config`.

## Control Flow

Probe accepts either OF match config or platform data, allocates managed DRM private data, copies config, maps MMIO, selects the dot-clock source, enables runtime PM, initializes vblank, initializes modeset, gets and requests the IRQ, registers DRM, and starts a DRM client with RGB565. The IRQ handler locks around `LDINTR`, acknowledges pending status bits, handles vblank, and completes page flips. Runtime suspend/resume gates the selected clock. System sleep delegates to DRM mode config suspend/resume. Remove unregisters, atomic-shuts down, and finalizes polling.

## State and Persistence Behavior

`struct shmob_drm_device` persists as DRM private state and stores config/platform data, MMIO, clock, prepared `lddckr`, IRQ lock/number, CRTC, encoder, and connector. Runtime PM controls clock lifetime, while CRTC enable/disable controls LCDC register state.

## Dependencies and Integration Points

The driver depends on platform/OF/PM runtime/clock/IRQ APIs, DRM core/client/GEM/vblank helpers, local KMS/CRTC/plane/register code, and optional platform data.

## Risks and Edge Cases

- Interrupt enable and status share `LDINTR`, requiring the spinlock discipline used here; all other writers must follow it.
- Probe supports platform data and OF; missing both fails early.
- `shmob_drm_setup_clocks()` maps logical clock sources to clock names and register selectors; wrong platform data breaks output clocking.
- Remove ordering must prevent IRQ/page-flip activity after DRM unregister/shutdown.

## Test Signals

Probe with OF and platform data, IRQ/vblank/page-flip completion, runtime PM clock gating, system suspend/resume, remove/shutdown, and clock source selection for bus/peripheral/external clocks are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.h

## Purpose

`shmob_drm_drv.h` defines the top-level private state for the legacy SH Mobile DRM driver.

## Important APIs, Types, and Functions

`struct shmob_drm_config` stores clock source and divider. `struct shmob_drm_device` stores Linux device, optional platform data, copied config, MMIO, clock, `lddckr`, IRQ number/lock, DRM device, CRTC, encoder, and connector. `to_shmob_device()` converts from `drm_device`.

## Control Flow

Probe initializes this structure; CRTC/KMS/IRQ/PM code read and mutate it throughout device lifetime.

## State and Persistence Behavior

The structure persists as the managed DRM private object. `irq_lock` protects `LDINTR` register access, while runtime PM controls the clock.

## Dependencies and Integration Points

It depends on Linux platform-data definitions, spinlocks, and local CRTC declarations.

## Risks and Edge Cases

The structure mixes OF-derived config and legacy platform data; code must check `pdata` before using fixed-panel fields. IRQ lock usage must remain consistent.

## Test Signals

OF and platform-data probe coverage plus lockdep under IRQ/vblank paths validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.c

## Purpose

`shmob_drm_kms.c` implements mode-setting initialization and framebuffer format validation for the legacy SH Mobile DRM driver.

## Important APIs, Types, and Functions

`shmob_drm_format_infos[]` maps DRM formats to LCDC data format, swap, bus source, and bpp register values. Public functions are `shmob_drm_format_info()` and `shmob_drm_modeset_init()`. `shmob_drm_fb_create()` validates formats and pitch constraints before creating GEM framebuffers.

## Control Flow

Modeset init initializes mode config, creates CRTC, encoder, and connector, resets mode config, starts polling, and sets min/max size and mode config funcs. Framebuffer creation rejects unsupported formats, primary pitches not 8-byte aligned or >=65536, and YUV chroma pitches that do not match the required relationship to luma pitch.

## State and Persistence Behavior

Format metadata is static. DRM mode_config persists in the DRM device. Framebuffer objects are managed by DRM GEM helpers.

## Dependencies and Integration Points

It depends on DRM atomic/GEM framebuffer helpers, local CRTC/plane/register definitions, and `shmob_drm_device`.

## Risks and Edge Cases

- Mode config funcs are assigned after `drm_mode_config_reset()`, which is unusual; users should confirm no reset path needs funcs earlier.
- YUV pitch validation assumes specific chroma layout rules from the LCDC hardware.
- Max mode size is 4095x4095, but timing register fields and external panels may impose smaller limits.

## Test Signals

Framebuffer creation tests for every supported format, pitch alignment, pitch upper bound, YUV chroma pitch mismatch, CRTC/encoder/connector init failures, and connector polling startup are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.h

## Purpose

`shmob_drm_kms.h` declares SH Mobile KMS format metadata and modeset initialization.

## Important APIs, Types, and Functions

`struct shmob_drm_format_info` maps DRM fourcc to LCD data format register bits, source-image format bits, data swap bits, and bpp. `shmob_drm_format_is_yuv()` tests the color-conversion bit. Public declarations are `shmob_drm_format_info()` and `shmob_drm_modeset_init()`.

## Control Flow

Plane and framebuffer code use `shmob_drm_format_info()` to validate and program LCDC formats. Probe calls `shmob_drm_modeset_init()`.

## State and Persistence Behavior

No state is owned by the header; it defines metadata shape for static tables.

## Dependencies and Integration Points

It forward-declares GEM DMA and driver state types and depends on LCDC register macros for `LDDFR_CC` in the YUV helper.

## Risks and Edge Cases

The inline YUV helper requires `shmob_drm_regs.h` to be included before or alongside this header in C files that use it.

## Test Signals

Compile coverage and format validation tests for RGB/YUV formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_kms.h -->
