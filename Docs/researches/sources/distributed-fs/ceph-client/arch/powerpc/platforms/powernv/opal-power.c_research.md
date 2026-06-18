## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-power.c

### Purpose
`opal-power.c` connects OPAL shutdown, EPOW, and DPO firmware messages to Linux orderly reboot or poweroff handling.

### Important APIs, Types, And Functions
Important functions are `detect_epow()`, `poweroff_pending()`, `opal_power_control_event()`, and `opal_power_control_init()`. It registers three notifier blocks for `OPAL_MSG_SHUTDOWN`, `OPAL_MSG_EPOW`, and `OPAL_MSG_DPO`.

### Control Flow
Initialization always registers the shutdown notifier, then checks `/ibm,opal/epow` for `ibm,opal-v3-epow` support. If supported, it registers EPOW/DPO notifiers and immediately checks for pending DPO/EPOW conditions. Shutdown messages decode parameter 0 as soft reboot or soft off. EPOW status masks out non-shutdown power-change classes before deciding whether to power off.

### State, Persistence, And Dependencies
There is no mutable local state beyond notifier registration. Firmware state persists as power-control events and EPOW/DPO status. Dependencies include OPAL status calls, OPAL message notifiers, device tree compatibility, and Linux `orderly_poweroff()`/`orderly_reboot()`.

### Integration Points
`opal_init()` calls this late in OPAL service setup. It consumes messages delivered by `opal.c` and affects global system power state.

### Risks
Failure to register one notifier does not prevent initialization from returning success. EPOW interpretation depends on firmware class semantics. Unknown shutdown types are logged but otherwise ignored.

### Test Signals
Test existing DPO/EPOW at boot, shutdown messages for soft off and reboot, unsupported EPOW DT nodes, `opal_get_epow_status()` failures, filtered power class bits, and notifier registration failures.
