## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/dev.h

Purpose: this header defines `struct lbs_private`, the central per-device state object for the Libertas driver, plus related sleep and mesh stats structures.

Important types: `struct sleep_params` mirrors firmware sleep parameter fields. `struct lbs_mesh_stats` collects mesh forwarding/drop counters under mesh config. `struct lbs_private` contains networking state, cfg80211 state, mesh/debugfs pointers, power/deep-sleep/host-sleep state, hardware callbacks, adapter identity, command queues and timers, response buffers, event FIFO, worker threads, encryption/WOL/TX state, locks, radio/channel/rate/power state, scanning state, and async firmware loading fields. `lbs_iface_active()` checks normal and mesh netdev running state.

Control flow and integration: almost every Libertas subsystem receives `lbs_private`. Bus drivers fill hardware callbacks and card pointer; main initializes locks, queues, threads, and netdevs; cfg/command/debugfs/ethtool mutate their slices of state.

State and persistence: all fields are in-memory runtime state. Firmware and EEPROM-derived values such as `fwrelease`, `fwcapinfo`, `regioncode`, and MAC address persist only while the device is loaded. Firmware settings are mirrored through commands.

Dependencies and risks: the struct depends on defs, decls, host command definitions, kfifo, cfg80211, netdev, timers, wait queues, and workqueues. Because it is large and shared, locking discipline matters: `lock`, `driver_lock`, serialized netdev xmit, wait queues, and timers protect different subsets. Test signals include probe/remove failure unwinds, suspend/resume, concurrent command/event/TX paths, scan cancellation, debugfs removal, and mesh-enabled builds.
