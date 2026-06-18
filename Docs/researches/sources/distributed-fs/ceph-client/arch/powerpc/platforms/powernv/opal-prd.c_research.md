## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-prd.c

### Purpose
`opal-prd.c` implements the `/dev/opal-prd` runtime diagnostics channel used by user-space PRD daemons to exchange messages with OPAL firmware and map firmware-provided diagnostic memory ranges.

### Important APIs, Types, And Functions
Important types are `struct opal_prd_msg`, `struct opal_prd_msg_queue_item`, and `struct opal_prd_scom`. Key functions include `opal_prd_open()`, `opal_prd_mmap()`, `opal_prd_poll()`, `opal_prd_read()`, `opal_prd_write()`, `opal_prd_ioctl()`, `opal_prd_msg_notifier()`, `opal_prd_probe()`, and `opal_prd_remove()`.

### Control Flow
Probe registers notifiers for `OPAL_MSG_PRD` and `OPAL_MSG_PRD2`, then registers a misc device. Only one opener is allowed through `prd_usage`. Firmware messages are copied in notifier context into a spinlock-protected queue and wake waiters. Reads block or return `-EAGAIN`, pop one queued message, validate user buffer size, and requeue on copy failure. Writes copy a sized PRD message from user space and forward it with `opal_prd_msg()`. IOCTLs expose kernel version info and SCOM read/write passthroughs. `mmap()` validates the requested physical range against reserved-memory children with `ibm,prd-label`.

### State, Persistence, And Dependencies
State includes the active PRD node, message queue, waitqueue, spinlock, and single-open atomic. Persistent behavior is firmware diagnostics state and reserved memory mappings. Dependencies include OPAL PRD messages, OPAL XSCOM calls, miscdevice, user-copy, remap APIs, and reserved-memory DT metadata.

### Integration Points
`opal.c` instantiates the platform device for `ibm,opal-prd`. The user-space PRD daemon uses reads/writes/poll/ioctls, while firmware sends messages through the OPAL message notifier bus.

### Risks
`opal_prd_write()` trusts the user-provided header size after only checking the initial count is at least a header; malformed sizes are delegated to `memdup_user()`. `opal_prd_range_is_valid()` requires labeled reserved-memory ranges but otherwise maps raw physical memory. Queue allocation can fail in atomic context and drop firmware messages.

### Test Signals
Test single-open enforcement, blocking and nonblocking reads, requeue on undersized buffers or copy faults, PRD and PRD2 message delivery, malformed user message sizes, FINI on release, SCOM ioctl endianness, mmap range overflow and label checks, and probe/remove notifier unwinding.
