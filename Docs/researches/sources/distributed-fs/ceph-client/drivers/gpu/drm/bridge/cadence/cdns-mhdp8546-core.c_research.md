# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.c

## Purpose

This is the Cadence MHDP8546 DisplayPort bridge driver. It loads the controller firmware, exposes a DRM bridge and DP AUX channel, handles HPD, EDID, DPCD access, link training, video framer programming, optional HDCP, and platform wrapper hooks.

## Important APIs, Types, And Functions

Core paths include `cdns_mhdp_probe/remove()`, `cdns_mhdp_attach/detach()`, `cdns_mhdp_atomic_check/enable/disable()`, `cdns_mhdp_transfer()`, `cdns_mhdp_link_up/down()`, `cdns_mhdp_link_training()`, `cdns_mhdp_configure_video()`, `cdns_mhdp_update_link_status()`, and `cdns_mhdp_wait_for_sw_event()`. Mailbox helpers serialize firmware commands with `mbox_mutex`; link and modeset state are protected by `link_mutex`; firmware/bridge attach races use `start_lock`.

## Control Flow

Probe enables the functional clock, maps main and optional SAPB registers, gets the DP PHY, initializes AUX, runtime PM, platform ops, firmware clock registers, IRQ, host caps, PHY, work items, firmware loading, optional HDCP, and the bridge. Firmware is loaded asynchronously, copied to IMEM, activated through mailbox, and then HPD interrupts are enabled if the bridge is attached. Atomic enable links up when plugged, runs platform enable, enables VIF clock, optionally starts HDCP, validates bandwidth, computes TU/line thresholds, writes DP MSA/framer registers, and caches the current mode. HPD work rereads events/status, retrains if needed, and notifies the bridge.

## State And Persistence Behavior

State includes host/sink/link capability structures, `link_up`, `plugged`, `bridge_enabled`, current mode in bridge state, `sw_events`, firmware `hw_state`, connector pointer, work items, and optional HDCP state. There is no disk persistence; firmware and hardware registers are reinitialized at runtime. Removal waits briefly for firmware readiness before sending standby.

## Dependencies And Integration Points

The driver depends on `cadence/mhdp8546.bin`, DRM DP helper APIs, DP AUX, generic DP PHY configuration, OF match data, runtime PM, threaded IRQs, and optional platform info such as TI J721E bus flags/ops. HDCP sidecar code uses `cdns_mhdp_wait_for_sw_event()`.

## Risks And Test Signals

Risks include asynchronous firmware races, mailbox timeouts, link-training fallback errors, stale connector pointer use in retry work, ignoring HDCP work cleanup in remove, and bandwidth checks before a trained link exists. Test signals are firmware keepalive/version logs, AUX DPCD/EDID reads, HPD events, successful CR/EQ training at lane/rate fallbacks, modeset retry on failed training, and DP display at expected color depth.
