# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.c

## Purpose

This is the Cadence MIPI DSI host and DRM bridge implementation. It exposes one DPI input bridge to the DRM bridge chain and one MIPI DSI host to downstream DSI panels/bridges. It programs DSI link, D-PHY timing, video packetization, direct command transfer, interrupts, runtime PM, and platform wrapper callbacks.

## Important APIs, Types, And Functions

Important callbacks are `cdns_dsi_drm_probe()`, `cdns_dsi_attach()`, `cdns_dsi_transfer()`, and `cdns_dsi_bridge_atomic_pre_enable/post_disable/check()`. `struct cdns_dsi_bridge_state` stores computed `cdns_dsi_cfg` timing across atomic check and enable. `cdns_dsi_mode2cfg()`, `cdns_dsi_check_conf()`, `cdns_dsi_round_pclk()`, `cdns_dsi_init_link()`, and `cdns_dsi_hs_init()` are the core mode-to-hardware helpers.

## Control Flow

Probe maps registers, enables the APB clock long enough to validate the Cadence vendor ID, discovers FIFO depths, masks interrupts, initializes runtime PM, runs optional platform init, and registers the DSI host. A DSI peripheral attach resolves the downstream bridge through OF graph and only then adds the DPI input bridge. Atomic check forces negative syncs, rounds pixel clock through D-PHY validation, and stores converted DSI timing. Pre-enable resumes runtime PM, invokes wrapper enable, initializes link/PHY, waits for lanes ready, writes video timing/packet registers, configures timeouts and packet format, and enables the input interface. Post-disable shuts video/link bits down after the upstream DPI stream has stopped, invokes wrapper disable, powers down the PHY, and releases runtime PM.

## State And Persistence Behavior

Driver state is in `struct cdns_dsi`: mapped MMIO, host/bridge endpoints, FIFO depths, completion, clocks/reset, D-PHY handle, platform ops, and `link_initialized`/`phy_initialized` flags. There is no persistent storage; hardware state is rebuilt on probe, command transfer, and atomic enable. Direct commands synchronize through `direct_cmd_comp` and IRQ status bits.

## Dependencies And Integration Points

The file integrates Linux DRM bridge atomic state, MIPI DSI host ops, OF graph bridge discovery, generic PHY MIPI D-PHY helpers, clocks, reset controls, IRQ completions, and optional platform ops such as TI J721E. It requires atomic DRM devices and supports a single attached DSI device.

## Risks And Test Signals

Risks include incorrect byte timing overheads, clock rounding that the upstream CRTC cannot satisfy, missing runtime-PM unwind when pre-enable returns early, direct-command FIFO/RX length rejection, and color shifts if enable/disable order changes. Test signals are successful DSI panel attach, DCS read/write transfers, mode validation failures for illegal timings, runtime suspend/resume, IRQ completion for direct commands, and visual modeset/hotplug smoke tests.
