# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_private.h

Purpose: defines private VFIO AP data structures and cross-file function prototypes. It is the shared contract between driver setup and operations for matrix devices, mdev assignment state, and queue ownership.

Important APIs and types: `struct ap_matrix_dev` wraps the root matrix `device`, current `ap_config_info`, mdev list, `mdevs_lock`, `guests_lock`, AP driver pointer, and mdev parent/type data. `struct ap_matrix` carries adapter (`apm`), queue/domain (`aqm`), and control-domain (`adm`) bitmaps plus max IDs. `struct ap_queue_table` contains a hash table of assigned queues. `struct ap_matrix_mdev` embeds `vfio_device`, list node, desired matrix, filtered `shadow_apcb`, KVM pointer, PQAP hook, mdev pointer, queue table, request/config eventfds, and pending add masks. `struct vfio_ap_queue` records APQN, owning mdev, saved AQIC NIB/ISC, hash/list nodes, reset status, and reset work.

Control flow: this header has no executable flow. It enables `vfio_ap_drv.c` to create global matrix state and `vfio_ap_ops.c` to mutate it through declared mdev/AP bus callbacks.

State and persistence: all structs describe in-memory kernel state. Assignment state is visible through sysfs while the mdev exists, but it is not written to stable storage. Queue interrupt state persists only while a queue is linked and a guest has configured AQIC.

Dependencies and integration: includes Linux mdev, eventfd, mutex, KVM, VFIO, hashtable, and `ap_bus.h`. External callbacks connect to AP bus registration, mdev registration, resource-in-use checks, and AP config notifications.

Risks: because this header defines lock ownership and shared state, field semantics must stay synchronized with operations code. Misinterpreting `matrix` versus `shadow_apcb` can expose unavailable queues to guests. `VFIO_AP_ISC_INVALID` must be honored before unregistering interrupt subclasses.

Test signals: compile-time structure use across driver files, mdev create/remove lifecycle, queue link/unlink hash behavior, saved IOVA/ISC cleanup, and configuration-change callbacks updating pending add masks.
