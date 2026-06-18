# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/clock_source.h

## Purpose

`clock_source.h` defines the display clock-source abstraction for pixel clock generation. It describes PLL inputs, spread-spectrum and de-spread metadata, computed divider settings, and function pointers for programming or querying pixel clock sources.

## Important APIs, Types, And Functions

Important types include `spread_spectrum_data`, `delta_sigma_data`, `pixel_clk_flags`, `csdp_ref_clk_ds_params`, `pixel_clk_params`, `pll_settings`, `calc_pll_clock_source_init_data`, `calc_pll_clock_source`, `clock_source_funcs`, and `clock_source`. Operations include `cs_power_down`, `program_pix_clk`, `get_pix_clk_dividers`, `get_pixel_clk_frequency_100hz`, and `override_dp_pix_clk`.

## Control Flow

Callers populate `pixel_clk_params` from stream timing, signal type, encoder/controller IDs, DP reference clock data, color depth, pixel encoding, and programming flags. A clock-source implementation calculates `pll_settings` and optionally programs the pixel clock for the requested DP/HDMI/LVDS/analog output. Query and override functions support readback and DP-specific clock adjustment.

## State And Persistence Behavior

`clock_source` persists as a resource-pool object with a context, clock-source ID, DP-clock-source flag, and vtable. `pll_settings` is stored in `pipe_ctx` when a pipe is mapped. Hardware state changes occur when `program_pix_clk` or power-down functions run.

## Dependencies And Integration Points

The file includes DC types, graphics object IDs, and BIOS parser types. It integrates with resource allocation, stream/link programming, VBIOS PLL calculations, DCCG/DP DTO setup, and HWSS link-output callbacks. `core_types.h` stores clock sources in `resource_pool` and `pipe_ctx`.

## Risks And Edge Cases

Clock units differ across fields: requested pixel clock is in 100 Hz, requested symbol/DP ref clocks are kHz, and PLL frequencies are also 100 Hz or kHz depending on field. Spread-spectrum percentage divider can be 100 or 1000 and must match firmware interpretation. Wrong encoder/controller IDs can program the wrong PLL path. DP de-spread and on-the-fly tuning are DP-specific and should not leak to non-DP signals.

## Test Signals

Builds catch vtable drift. Runtime tests should validate exact pixel-clock generation for HDMI, DP, eDP, LVDS, and analog paths; spread-spectrum on/off; YCbCr 4:2:0; DP ref-clock de-spread; clock readback; and clock-source power-down. Link training failures and mode timing drift are major practical signals.
