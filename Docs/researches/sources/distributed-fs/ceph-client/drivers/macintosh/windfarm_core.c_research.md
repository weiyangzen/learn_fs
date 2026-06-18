# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_core.c

## Purpose
Implements the core Windfarm framework used by PowerMac thermal-control drivers. It owns the global lists of `wf_control` and `wf_sensor` objects, exposes them as attributes on a synthetic `windfarm` platform device, broadcasts notifier events to platform control-loop clients, and runs the once-per-second `kwindfarm` tick thread.

## Important APIs, Types, And Functions
Exports `wf_register_control()`, `wf_unregister_control()`, `wf_get_control()`, `wf_put_control()`, `wf_register_sensor()`, `wf_unregister_sensor()`, `wf_get_sensor()`, `wf_put_sensor()`, `wf_register_client()`, `wf_unregister_client()`, `wf_set_overtemp()`, and `wf_clear_overtemp()`. Sysfs helpers call each object's ops: controls support `get_value`, `set_value`, `get_min`, and `get_max`; sensors expose fixed-point values with `FIX32TOPRINT`. `wf_thread_func()` emits `WF_EVENT_TICK` once per second and performs critical overtemperature escalation.

## Control Flow
Providers register controls and sensors under `wf_lock`, receive duplicate-name protection, and trigger `WF_EVENT_NEW_CONTROL` or `WF_EVENT_NEW_SENSOR`. Clients register a blocking notifier, immediately receive callbacks for all existing objects, and start the tick thread when the first client appears. The thread calls notifiers without the core mutex only for ticks, matching the locking warning in `windfarm.h`.

## State, Dependencies, And Integration
State is process-global: `wf_controls`, `wf_sensors`, `wf_client_list`, reference counts, overtemperature counters, and `wf_thread`. It depends on krefs, blocking notifiers, kthreads/freezer support, platform devices, sysfs device attributes, module ownership, and `call_usermodehelper("/sbin/critical_overtemp")`. Platform model drivers bind to the `"windfarm"` platform device and use the notifier stream.

## Risks And Test Signals
Lifetime is subtle: sysfs attributes embed in provider-owned objects, and notifier callbacks except ticks run under `wf_lock`, so recursive core calls can deadlock. Overtemperature handling invokes usermode after roughly 10 ticks and powers off after roughly 30 ticks. Test signals include duplicate registration, module get/put balance, sysfs read/write paths, notifier ordering for late clients, tick thread start/stop, freezer behavior, and overtemperature refcount transitions.
