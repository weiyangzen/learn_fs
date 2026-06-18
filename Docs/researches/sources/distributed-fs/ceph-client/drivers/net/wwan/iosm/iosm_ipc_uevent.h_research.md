# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_uevent.h

Purpose: defines IOSM userspace event names and the work item structure used to send modem state uevents.

Important APIs/types: constants include `UEVENT_MDM_NOT_READY`, `UEVENT_ROM_READY`, `UEVENT_MDM_READY`, `UEVENT_CRASH`, `UEVENT_CD_READY`, `UEVENT_CD_READY_LINK_DOWN`, and `UEVENT_MDM_TIMEOUT`. `MAX_UEVENT_LEN` caps the formatted `IOSM_EVENT=` string at 64 bytes. `struct ipc_uevent_info` stores the target device, formatted event buffer, and work item. `ipc_uevent_send()` is the public sender.

Control flow and state: callers pass a device and one of the event strings; implementation allocates a transient work item and emits one uevent. There is no durable state or retry.

Dependencies and integration points: tied to Linux workqueues and kobject uevents. It is part of the IOSM modem lifecycle notification surface consumed by userspace modem-management services.

Risks and test signals: event spelling is externally visible, so renames are compatibility risks. The fixed buffer requires guarding new event names against truncation. Test by observing generated environment variables for every constant and by checking behavior under memory pressure.
