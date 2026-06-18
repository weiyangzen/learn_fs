# sources/distributed-fs/ceph-client/drivers/s390/char/vmlogrdr.c

Purpose: character driver for reading z/VM system service records from LOGREC, ACCOUNT, and SYMPTOM services through IUCV.

Important APIs/types/functions: defines `struct vmlogrdr_priv_t`, static `sys_ser[]` service descriptors, IUCV callbacks `vmlogrdr_iucv_path_complete`, `vmlogrdr_iucv_path_severed`, `vmlogrdr_iucv_message_pending`, CP recording helper `vmlogrdr_recording`, file ops `vmlogrdr_open`, `release`, `read`, sysfs attributes `autopurge`, `purge`, `autorecording`, `recording`, and driver/device registration helpers.

Control flow: module init checks z/VM, discovers recording privilege class, allocates minors and buffers, registers IUCV driver/class/devices, and adds one cdev covering three minors. Open is blocking-only and single-user per service, optionally starts CP recording, connects to the service over IUCV, and waits for connection completion/sever. Pending-message callback stores the IUCV message metadata and wakes readers. Read receives one record or record fragment into the page buffer, prefixes total length, appends `EOR` when complete, and copies buffered data to userspace.

State and persistence: each service keeps path pointer, connection/sever flags, pending message, receive count, page buffer position/remaining/residual, single-open flag, sysfs device pointers, and auto recording/purge settings. CP RECORDING state and queues exist in z/VM outside the driver.

Dependencies and integration: depends on z/VM, CP command interface, IUCV bus, EBCDIC-related headers, Linux cdev/class/device sysfs, wait queues, atomics, spinlocks, and user-copy APIs.

Risks: service buffers are only one page minus framing; oversized IUCV records rely on residual-length continuation. Some state updates such as `dev_in_use` cleanup are not always under the same spinlock used on open. CP command parsing expects English response text. Blocking open/read semantics require wakeups on severed paths.

Test signals: load only under VM, one-open enforcement, auto recording on/off and purge sysfs behavior, IUCV connect/sever wakeups, fragmented large record reads with length/EOR framing, queue-empty blocking read, and cleanup after partial init failure.
