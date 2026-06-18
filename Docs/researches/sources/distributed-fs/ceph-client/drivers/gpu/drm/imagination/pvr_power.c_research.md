# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.c

## Purpose
Implements PowerVR GPU power sequencing, firmware power transitions, watchdog-based firmware stall detection, reset recovery, runtime PM callbacks, and multi-power-domain attachment. It is the central integration point between DRM device lifetime, platform clocks/resets or power sequencers, firmware start/stop, queue reset handling, and device-loss reporting.

## Important APIs, types, and functions
- Public APIs: `pvr_device_lost()`, `pvr_power_is_idle()`, `pvr_watchdog_init()`, `pvr_watchdog_fini()`, `pvr_power_device_suspend()`, `pvr_power_device_resume()`, `pvr_power_device_idle()`, `pvr_power_reset()`, `pvr_power_domains_init()`, and `pvr_power_domains_fini()`.
- Firmware power helpers: `pvr_power_send_command()`, `pvr_power_request_idle()`, `pvr_power_request_pwr_off()`, `pvr_power_fw_disable()`, and `pvr_power_fw_enable()`.
- Watchdog helpers: `pvr_watchdog_kccb_stalled()` and `pvr_watchdog_worker()`.
- Platform sequencing implementations: `pvr_power_sequence_ops_manual` for clocks/reset controls and `pvr_power_sequence_ops_pwrseq` for `pwrseq` providers.
- Recovery helpers: `pvr_power_clear_error()` and `pvr_power_get_clear()`.

## Control flow
Firmware disable optionally cancels the watchdog, asks firmware to forced-idle and power off, disables IRQs for runtime suspend, and stops firmware. Firmware enable optionally reenables IRQs, starts firmware, waits for boot, queues the watchdog, and rolls IRQ state back on failure. Runtime suspend enters the DRM device, disables firmware if booted, then calls the platform `power_off()` operation. Runtime resume powers hardware on and restarts firmware if it had been booted before suspend.

The watchdog runs every 500 ms while the device is active. It takes a runtime PM reference only if the device is already in use, skips unbooted firmware, and checks KCCB progress. Two consecutive polls with pending KCCB work and unchanged executed-command count are treated as a stall and trigger a hard reset. When command progress is unchanged but KCCB is idle and there are no active queue-list entries, it sends a firmware health-check command to prove liveness.

`pvr_power_reset()` holds a runtime PM reference, serializes with `reset_sem`, disables IRQs, optionally stops all queues for hard reset, then loops through firmware disable and enable. A hard reset powers the device down, runs `pvr_fw_hard_reset()`, powers it back up, and restarts firmware. A soft reset clears firmware HWR fault flags and restarts firmware; if it fails, the loop escalates to hard reset. Hard reset failure marks the DRM device lost and leaves IRQs disabled.

Power-domain initialization counts device-tree `power-domains`. With more than one domain it attaches named domains `a` through `e`, creates stateless runtime-PM device links from later domains to the first domain, and stores the domain list/link array in `pvr_dev->power`. Finalization deletes links in reverse, detaches domains, frees the link array, and zeros the state.

## State and persistence
Persistent state lives in `pvr_device`: `lost`, `irq`, `reset`, `pwrseq`, clocks, `fw_dev.booted`, firmware shared memory fields, watchdog delayed work and counters, queue lists, runtime PM status, and attached power-domain metadata. The watchdog mutates `old_kccb_cmds_executed` and `kccb_stall_count`. Reset temporarily changes queue scheduler state and may update firmware boot state around hard reset.

## Dependencies and integration points
Depends on DRM unplug/device-enter helpers, runtime PM, IRQ control, clocks, reset controls, generic power sequencer consumer API, OF power-domain helpers, device links, firmware start/stop/hard-reset helpers, KCCB command submission, queue pre/post reset hooks, and Rogue firmware shared structures. It is called from PM ops, watchdog workqueue, MMU flush recovery, firmware interrupt recovery paths, and driver probe/remove domain setup.

## Risks
Reset and PM paths are concurrency-sensitive: IRQ disable mode differs for hard reset and threaded-IRQ soft reset, and runtime PM error clearing temporarily disables PM. If `pvr_power_get_clear()` fails, `pvr_power_reset()` only warns and still proceeds, which can complicate recovery on persistent PM errors. Watchdog health-check logic depends on queue active/idle list correctness. Device-loss handling intentionally prevents further DRM access, so false positives are severe. Multi-domain support is limited to five named domains and assumes link direction/order matches platform requirements.

## Test signals
Expected signals include clean suspend/resume with firmware booted and unbooted, watchdog recovery after injected KCCB stalls, escalation from soft reset to hard reset, device-lost logs on hard reset failure, IRQ state remaining correct after failures, and no active queue deadlocks across reset. Platform tests should cover manual clock/reset sequencing, pwrseq sequencing, one-domain and multi-domain DT configurations, deferred power-sequencer probe, and runtime PM idle returning `-EBUSY` while firmware or KCCB work is active.
