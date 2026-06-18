# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/event.h

Purpose: declares the firmware event workqueue entry point for qtnfmac.

Important APIs/functions: exposes `qtnf_event_work_handler(struct work_struct *work)`, which is initialized by core attach as `bus->event_work`.

Control flow: lower transport receives QLINK event packets into `bus->trans.event_queue` and schedules the work item. The implementation in `event.c` drains and dispatches those packets to cfg80211.

State and persistence: no state in the header; state lives in the bus event queue and MAC/VIF structures.

Dependencies and integration points: includes Linux kernel/module headers and `qlink.h` for event protocol context. It is included by `core.c` and event-related transport code.

Risks: minimal header-level risk. The single exported work handler assumes `work` is embedded in a valid `struct qtnf_bus` and that the bus/event queue remain alive while work runs.

Test signals: compile coverage plus runtime checks that core attach initializes the work item, transport schedules it, and detach cancels or drains event processing safely.
