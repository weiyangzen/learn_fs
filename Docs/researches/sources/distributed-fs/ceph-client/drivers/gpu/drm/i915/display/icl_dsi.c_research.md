# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/icl_dsi.c

## Purpose

`icl_dsi.c` implements Gen11+ Intel MIPI DSI encoder, connector, host-transfer, PHY, transcoder, panel power, backlight, DSC, and mode-configuration support. It translates VBT DSI panel data and DRM atomic state into DSI packet transfers, Combo PHY setup, DSI PLL/escape clock setup, transcoder timing registers, panel command sequences, and connector properties.

## Important APIs, Types, And Functions

The exported functions are `icl_dsi_init()` and `icl_dsi_frame_update()`. Initialization allocates `struct intel_dsi` and `struct intel_connector`, registers a DRM DSI encoder and connector, creates per-port `struct intel_dsi_host` objects with `gen11_dsi_host_ops`, initializes VBT panel data, computes D-PHY timing registers in `icl_dphy_param_init()`, and adds scaling/orientation properties. Packet transmission uses `gen11_dsi_host_transfer()`, `dsi_send_pkt_payld()`, `dsi_send_pkt_hdr()`, and credit wait helpers. Power and enable sequencing is split across encoder hooks: `gen11_dsi_pre_pll_enable()`, `gen11_dsi_pre_enable()`, `gen11_dsi_enable()`, `gen11_dsi_disable()`, and `gen11_dsi_post_disable()`.

Key programming helpers include `gen11_dsi_program_esc_clk_div()`, `gen11_dsi_map_pll()`, `gen11_dsi_enable_io_power()`, `gen11_dsi_power_up_lanes()`, `gen11_dsi_config_phy_lanes_sequence()`, `gen11_dsi_voltage_swing_program_seq()`, `gen11_dsi_setup_dphy_timings()`, `gen11_dsi_setup_timings()`, `gen11_dsi_setup_timeouts()`, `gen11_dsi_configure_transcoder()`, `gen11_dsi_set_transcoder_timings()`, and `configure_dual_link_mode()`. Atomic state support comes through `gen11_dsi_compute_config()`, `gen11_dsi_get_config()`, `gen11_dsi_get_hw_state()`, and `gen11_dsi_initial_fastset_check()`.

## Control Flow

Probe-time initialization starts from a VBT encoder entry, determines the port, allocates objects, wires DRM callbacks, loads fixed panel modes and backlight data, determines single or dual-link ports, creates MIPI DSI hosts, runs VBT DSI initialization, and computes D-PHY register values from panel timing parameters. A host transfer builds a `mipi_dsi_packet`, writes long-packet payload DWORDs when needed, then writes the header with low-power or high-speed flags after checking hardware credits.

During enable, the pre-PLL hook waits panel power-cycle timing, runs VBT power/reset sequences, switches IO mode to DSI, takes IO power references, and programs escape clock divisors. The pre-enable hook maps the PLL, powers lanes, programs PHY sequencing, voltage swing, D-PHY timing, DDI buffer, clocks, utility TE pin, timeouts, protocol mode, dual-link splitter, and panel initialization commands, then writes DSC PPS and transcoder timings. The enable hook applies workarounds, enables the DSI transcoder, sends display/backlight-on sequences, prepares the panel, and enables vblank. Disable reverses this order: panel unprepare and backlight off first, then vblank off, transcoder disable, panel display off, ULPS entry, DDI function disable, DSC/scaler cleanup, port and IO power disable, reset assert, power off, and panel power-off timestamp update.

## State And Persistence Behavior

Persistent driver state lives in `struct intel_dsi`: selected ports/phys, lane count, pixel format, dual-link mode, VBT sequence data, panel timings, D-PHY register values, DSI hosts, IO wakerefs, panel power-off time, and attached connector. Hardware state persists in DSI command, timing, timeout, transcoder, DDI, PLL clock, Combo PHY, DSS splitter, utility pin, DSC, and backlight registers until the disable path or modeset rewrites them. Atomic state records output format, bpp, compressed DSC parameters, selected DSI transcoder, port clock, TE flags, and periodic command mode readout.

## Dependencies And Integration Points

The file integrates DRM MIPI DSI helpers, DRM atomic connector helpers, Intel VBT DSI parser, panel/backlight helpers, Combo PHY and DDI code, DPLL state, DSC helpers, scaler helpers, CRTC vblank control, power domains, and DSI register definitions from `icl_dsi_regs.h`. It plugs into the generic Intel encoder lifecycle through function pointers installed in `icl_dsi_init()`.

## Risks And Edge Cases

Enable/disable ordering is hardware-sensitive: IO power refs, PLL mapping, DDI buffer state, ULPS, command credit waits, panel command dispatch, DSC PPS, vblank, and backlight must remain ordered. Dual-link front/back mode depends on buffer-depth and overlap calculations. Command mode TE uses GPIO/UTIL pin assumptions and port-specific frame update flags. DSC intentionally forces full modesets in the fastset check. Several sanity failures log errors rather than aborting, so invalid timing inputs may still be programmed. Error cleanup in `icl_dsi_init()` must balance partially initialized connectors, encoders, hosts, and allocated objects.

## Test Signals

Useful tests include single-link and dual-link DSI panels, command and video modes, TE0/TE1 frame updates, long and short MIPI packet transfers, low-power transfer mode, DSC-enabled modes, backlight and VBT sequence ordering, suspend/resume, fastboot readout, hot-unplug or missing fixed-mode error paths, ADL escape-clock programming, JSL/EHL/TGL PHY branches, DDI buffer idle waits, ULPS entry, and IGT panel/backlight/modeset tests on real DSI hardware.
