# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pm.h

Purpose: declares the IOSM PM state machines and public PM operations. It also provides macros that map sleep-control and HPDA updates to doorbell writes.

Important types/APIs: `ipc_pm_cond`, `ipc_mem_host_pm_state`, `ipc_mem_dev_pm_state`, `iosm_pm`, `ipc_pm_unit`, and prototypes for init/deinit, device sleep notification, s2idle update, host sleep/active preparation, active wait, HPDA signaling, and PM trigger. Macros `ipc_cp_irq_sleep_control` and `ipc_cp_irq_hpda_update` centralize doorbell IDs/data.

Control flow role: protocol suspend/resume and runtime HP updates use these APIs to avoid sending head-pointer updates while host or device sleep state makes the link unavailable. State is volatile per protocol instance, with a completion used for active-state waits.

Dependencies: requires `ipc_doorbell_fire`, `IPC_DOORBELL_IRQ_SLEEP`, `IPC_DOORBELL_IRQ_HPDA`, and IOSM PM constants from protocol/imem context. Risks: include-order reliance, bitfield condition races, stale `pending_hpda_update`, and CP/AP state mismatch. Test signals: enum-to-wire values for sleep doorbells, PM unit condition transitions, compile coverage from protocol.c, and suspend/resume sequencing with mocked CP notifications.
