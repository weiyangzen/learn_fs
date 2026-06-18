## sources/distributed-fs/ceph-client/drivers/s390/cio/vfio_ccw_drv.c

Purpose: provides the css subchannel driver and module lifecycle for VFIO mediated non-QDIO CCW passthrough. It binds I/O subchannels, creates the mdev parent, handles interrupts and channel-path events, initializes debug/workqueue/region caches, and tears everything down on module exit.

Important APIs/types/functions: global resources include `vfio_ccw_work_q`, region kmem caches, and s390 debug IDs. Core functions are `vfio_ccw_sch_quiesce()`, `vfio_ccw_sch_io_todo()`, `vfio_ccw_crw_todo()`, `vfio_ccw_sch_irq()`, `vfio_ccw_sch_probe()/remove()/shutdown()`, `vfio_ccw_sch_event()`, `vfio_ccw_chp_event()`, and module init/exit.

Control flow: probe rejects QDIO, allocates a `vfio_ccw_parent`, registers a child device, and registers the mdev parent. Open/close behavior is handled by the mdev/FSM code, while hardware interrupts enter `vfio_ccw_sch_irq()` and dispatch `VFIO_CCW_EVENT_INTERRUPT`. Deferred I/O work copies the IRB into the user-visible region, frees completed channel programs, transitions back to IDLE on final solicited interrupt, and signals the I/O eventfd. Channel-path events update path masks, cancel/halt/clear affected paths, queue CRWs, and signal userspace through CRW work.

State and persistence: persistent module state is the workqueue, caches, debug features, css driver registration, ISC registration, and per-subchannel parent device. Per-device runtime state lives in `vfio_ccw_private`. CRWs are queued in a list until userspace reads them through the CRW region.

Dependencies and integration: depends on css/cio/chp infrastructure, mdev, eventfd workqueues, s390 debug, and vfio-ccw FSM/private structures. It is the bridge from host subchannel events into userspace VFIO notification.

Risks and test signals: key risks are lock ordering around `sch->lock`, quiesce completion races, CRW drops under GFP_ATOMIC failure, and correct cleanup after partial init. Test bind/unbind, unexpected interrupts, not-oper transitions, channel-path vary/offline/online events, final versus intermediate interrupts, and module init failure unwind.
