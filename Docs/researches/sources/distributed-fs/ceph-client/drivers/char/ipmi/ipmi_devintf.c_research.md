# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_devintf.c

Purpose: `/dev/ipmiN` character device interface to the kernel IPMI message handler.

Important APIs, types, and functions: `struct ipmi_file_private`, receive handler, file ops (`open`, `release`, `poll`, `fasync`, `ioctl`), `handle_send_req()`, `handle_recv()`, compat ioctl helpers, SMI watcher callbacks, and module init/exit.

Control flow: open creates an IPMI user for the minor interface and initializes a receive queue. Incoming IPMI messages are queued under spinlock and wake waiters/fasync. Send ioctls copy request/address/data from userspace and call `ipmi_request_settime()`. Receive ioctls serialize dequeues with `recv_mutex`, copy address/data to userspace, optionally truncate, and put messages back on error. Init registers class, chrdev, and SMI watcher; watcher creates/destroys `ipmi%d` devices.

State and persistence: per-open user, receive queue, fasync queue, wait queue, retry defaults. Global class, major, and registered device list persist while module is loaded.

Dependencies and integration: IPMI message handler APIs, chrdev/class device model, userspace copy, compat ioctl ABI, poll/fasync, spinlocks/mutexes.

Risks and test signals: release destroys the user before draining queued messages; ordering must prevent new callbacks. Tests should cover all ioctls, compat structs, truncation and put-back on copy failure, poll/fasync wakeup, watcher add/remove, custom major handling, and module unload with registered devices.
