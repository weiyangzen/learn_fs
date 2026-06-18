# sources/distributed-fs/ceph-client/include/media/dvb_ca_en50221.h

Purpose: Defines the DVB Common Interface EN50221 conditional-access core interface between CI hardware drivers and the DVB CA device layer.

Important APIs/types/functions: Poll and IRQ flags describe CAM presence/change/ready and FR/DA events. `struct dvb_ca_en50221` contains module ownership, attribute-memory accessors, CAM control accessors, block-mode data read/write, slot reset/shutdown/TS-enable callbacks, slot status polling, driver private `data`, and core-private storage. APIs report CAM change, CAM ready, and FR/DA IRQs, plus initialize/release a CA device.

Control flow: A hardware driver fills callbacks and calls `dvb_ca_en50221_init` with flags and slot count. Slot access callbacks may run concurrently for different slots. Hardware IRQ handlers notify the core through the IRQ helpers; polling is used when CAM-change IRQs are unavailable.

State and persistence: Driver-private state hangs off `data`; core-private per-slot protocol/device state hangs off `private`. No persistent storage beyond device lifetime.

Dependencies and integration: Depends on DVB adapter/device core and Linux DVB CA userspace definitions. Integrates CAM slots with `/dev/dvb/adapterX/caY`.

Risks and test signals: Risks include callback concurrency, slot hotplug races, block transfer length handling, missing TS enable, and release during active CA sessions. Test multi-slot access, insertion/removal IRQs, ready and FR/DA events, userspace CA ioctls, polling fallback, and teardown.
