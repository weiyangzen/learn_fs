# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_sysfs.c

Purpose: sysfs control plane for vudc. It exposes device descriptor bytes, USB/IP socket attach/detach, and current USBIP device status.

Important APIs/types/functions: `get_gadget_descs()` synthesizes a GET_DESCRIPTOR setup request through the bound gadget driver and caches `udc->dev_desc`. `dev_desc_read()` serves the binary `dev_desc` attribute once cached. `usbip_sockfd_store()` accepts a userspace socket fd or `-1`, validates gadget readiness and socket type, creates RX/TX kthreads, installs `udc->ud.tcp_socket`, transitions status to `SDEV_ST_USED`, starts the transfer timer, and wakes threads. `usbip_status_show()` returns `udc->ud.status`. `vudc_groups` exports the attributes to the platform driver.

Control flow: attach path takes `sysfs_lock`, checks `driver` and `pullup`, validates availability, looks up a stream socket, creates RX/TX threads outside spinlocks, then publishes socket/thread/status under locks and starts timer. Detach path checks current connection and adds `VUDC_EVENT_DOWN`; teardown is handled by event processing elsewhere. Descriptor read simply fails with `-ENODEV` until descriptor cache is populated.

State and persistence: caches `struct usb_device_descriptor`, `desc_cached`, `connected`, `start_time`, socket pointer, thread task pointers, and USBIP status. State is protected by `udc->lock`, `udc->ud.lock`, and `udc->ud.sysfs_lock`; no disk persistence.

Dependencies and integration: integrates Linux sysfs, socket fd lookup, kthreads (`v_rx_loop`, `v_tx_loop`), gadget driver `setup()`, transfer timer, and usbip event handling. It is the user-visible attach point used by usbip tooling.

Risks: `get_gadget_descs()` assumes the ep0 request queue contains the descriptor request after calling gadget `setup()`. Attach failure paths must release socket/task references in the right order. `dev_desc_read()` trusts sysfs to bound offset/count to the bin attribute size.

Test signals: write valid TCP socket fd, invalid fd, datagram fd, duplicate attach, detach with `-1`, detach when not connected, descriptor read before/after gadget binding, and race attach/detach under sysfs locking.
