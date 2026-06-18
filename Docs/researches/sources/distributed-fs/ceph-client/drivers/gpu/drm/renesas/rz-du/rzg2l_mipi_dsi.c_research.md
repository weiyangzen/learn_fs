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
