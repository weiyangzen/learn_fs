# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_ops.c

Purpose: implements VFIO AP mediated-device behavior: matrix assignment sysfs, queue ownership, KVM guest APCB updates, PQAP(AQIC) interception, interrupt resource pinning, queue reset/hotplug, VFIO ioctls, AP queue probe/remove, and host AP configuration change handling.

Important APIs and functions: lock helpers enforce `guests_lock`, `kvm->lock`, then `mdevs_lock`. `vfio_ap_irq_enable()` validates/pins guest NIB pages, handles PV shared-page checks, registers GISC, and issues `ap_aqic()`. `handle_pqap()` handles guest AQIC interception through the KVM crypto hook. Assignment sysfs handlers update AP adapter/domain/control-domain bitmaps, validate no sharing/default-driver conflict, link queues, filter guest shadow APCB, and reset filtered queues. `ap_config_store()` atomically parses three hex masks and applies bulk add/remove. VFIO callbacks implement open/close, reset, IRQ eventfd setup, request signaling, DMA unmap cleanup, and device info. Queue probe/remove creates per-queue status sysfs, links APQNs to matching mdevs, filters guest exposure, and resets on removal. Config callbacks track added resources until scan completion and hot-unplug removed resources.

Control flow: userspace creates an mdev, writes matrix sysfs masks, opens the VFIO device with a KVM, then the driver installs a PQAP hook and writes filtered masks into the guest CRYCB/APCB. AP bus probe/remove and config-change callbacks dynamically link/unlink queues and update guests.

State and persistence: each `ap_matrix_mdev` stores assigned matrix masks, filtered `shadow_apcb`, KVM pointer, APQN queue hash, eventfds, and pending add bitmaps. Each `vfio_ap_queue` stores APQN, owning mdev, saved NIB IOVA/ISC, reset status, and reset work. State is in kernel memory and sysfs; it is not persisted across module unload.

Dependencies and integration: depends on AP bus queue objects, KVM s390 crypto masks and GISA/GISC interfaces, VFIO/mdev/iommufd APIs, eventfd, AP instructions (`TAPQ`, `ZAPQ`, `AQIC`), AP permissions, and s390 UV shared-page handling for protected guests.

Risks: lock ordering is critical to avoid deadlocks across AP bus, sysfs, VFIO, and KVM callbacks. Queue filtering at adapter granularity can remove more guest APQNs than a single missing queue. Interrupt setup must cleanly unpin NIB pages and unregister GISC on all AQIC failures. Some bitmap calls use AP device/domain widths and require careful bounds testing.

Test signals: concurrent sysfs assignment/unassignment, APQN sharing rejection, default-driver ownership rejection, VFIO open with duplicate KVM use, AQIC enable/disable for normal and PV guests, DMA unmap of saved NIB, queue reset response codes, AP queue hotplug/remove, config add/remove plus scan-complete, eventfd request/config notifications, and VFIO ioctl validation.
