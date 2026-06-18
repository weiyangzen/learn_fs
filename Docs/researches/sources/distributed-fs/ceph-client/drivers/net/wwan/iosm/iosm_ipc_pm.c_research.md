# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.c

Purpose: implements IOSM protocol power management for host sleep, device sleep notifications, link wake/sleep handshakes, pending HPDA doorbells, and s2idle state forcing.

Important functions: `ipc_pm_init`, `ipc_pm_deinit`, `ipc_pm_signal_hpda_doorbell`, `ipc_pm_trigger`, `ipc_pm_wait_for_device_active`, `ipc_pm_prepare_host_sleep`, `ipc_pm_prepare_host_active`, `ipc_pm_set_s2idle_sleep`, and `ipc_pm_dev_slp_notification`.

Control flow: HPDA doorbell requests are gated by host PM state and link readiness; if link wake is needed or host sleep disallows update, `pending_hpda_update` is set. Device sleep notifications update CP/AP states and may fire sleep-control doorbells. Host suspend prepares sleep, wakes device if needed, waits for active, then sends host sleep through protocol. Resume prepares active and sends exit sleep. When link wakes, pending host-sleep completions and pending HPDA updates are replayed.

State/dependencies: `iosm_pm` tracks host PM state, AP/CP device PM states, condition bitfield, last device sleep notification, completion, pending bit, and PCIe/device pointers. Dependencies include protocol/imem for doorbells and completions. Risks include state-machine desynchronization, pending HPDA starvation, timeouts in active wait, and no explicit locking around PM fields in IRQ/task contexts. Test signals: state transition matrix, pending HPDA replay, active wait timeout, duplicate sleep notifications, s2idle force sleep/active, and suspend/resume failure restoration.
