# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_phy.h

## Purpose
`link_dp_phy.h` declares the DP PHY control interface for link output, lane drive settings, FEC control, and sink receiver power state.

## Important APIs
- `dp_enable_link_phy()` and `dp_disable_link_phy()` manage hardware link output and current link state.
- `dp_set_hw_lane_settings()` and `dp_set_drive_settings()` program per-lane PHY/DPCD settings.
- `dp_set_fec_ready()` and `dp_set_fec_enable()` manage FEC readiness and enablement around training.
- `dpcd_write_rx_power_ctrl()` writes sink receiver power state.

## Control Flow And Integration
Generic and specialized link training code include this header to prepare PHY output, send test/training patterns, apply lane settings, and transition FEC state. Capability verification also uses it while probing maximum link capability.

## State, Risks, And Test Signals
The APIs mutate `dc_link` current settings, lane settings, FEC state, hardware encoder state, and sink DPCD state. Tests should cover compile integration with training/capability modules and runtime behavior across DP, eDP, LTTPR, FEC, and disable paths.
