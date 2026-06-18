# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm.h

Purpose: defines the shared Windfarm thermal-control API for PowerMac fan controls, sensors, clients, and overtemperature notifications.

Important APIs and types: `struct wf_control_ops` and `struct wf_control` describe controllable devices with set/get/min/max/release operations, kref lifetime, sysfs attribute, type, and private data. `struct wf_sensor_ops` and `struct wf_sensor` describe readable sensors. Inline helpers wrap control set/get min/max and sensor get. External APIs register/unregister/get/put controls and sensors, register/unregister notifier clients, and set/clear refcounted overtemperature.

Control flow: provider drivers allocate/populate `wf_control` or `wf_sensor`, register them with the Windfarm core, and rely on kref release callbacks after unregister. Client drivers register notifier blocks and react to events such as new sensors/controls and ticks.

State and persistence: no state in the header, but it defines lifetime ownership rules. Registered objects persist until the provider unregisters and final references drop.

Dependencies and integration: depends on Linux list, kref, module, notifier, and device attribute APIs. Used by Windfarm sensor/control providers such as `windfarm_ad7417_sensor.c` and policy clients elsewhere in the Macintosh tree.

Risks: notifier callbacks for all events except `WF_EVENT_TICK` run with an internal mutex held, and the header warns clients not to call core routines from those callbacks. Notifier blocks have no module owner, creating potential lifetime races. Fixed 16.16 formatting macro assumes signed 32-bit values.

Test signals: provider registration/unregistration lifetime, kref balancing through get/put, sysfs attribute creation by the core, notifier delivery ordering, overtemp refcount behavior, and client behavior that defers work from mutex-held callbacks to tick/work context.
