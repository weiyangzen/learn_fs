# sources/distributed-fs/ceph-client/drivers/s390/char/vmur.c

Purpose: z/VM virtual unit-record device driver for reader, punch, and printer devices, exposed as character devices mapped directly by minor number to VM device number.

Important APIs/types/functions: defines ccw driver `ur_driver`, class `vmur`, debug area, reference helpers `urdev_alloc/get/put`, write CCW helpers `alloc_chan_prog`, `free_chan_prog`, `do_ur_io`, interrupt handler `ur_int_handler`, diagnose helpers for reader files, file ops `ur_open`, `ur_release`, `ur_read`, `ur_write`, `ur_llseek`, and ccw lifecycle methods `ur_probe`, `ur_set_online`, `ur_set_offline`, `ur_remove`.

Control flow: probe allocates `struct urdev`, creates `reclen`, uses diagnose 0x210 to validate VM class, stores drvdata, and installs interrupt handler. Online creates cdev and class node named `vmrdr-*`, `vmpun-*`, or `vmprt-*`. Writes build chained WRITE CCWs with a final NOP and synchronously wait for interrupt completion. Reads use diagnose 0x14 to position/read spool pages, optionally inject file record length into the first page, and copy page chunks to userspace.

State and persistence: `struct urdev` holds ccw device, record length, VM class, char device, open flag/wait queue, refcount, I/O completion pointer, and uevent work. `struct urfile` stores per-open access data and file record length. Spool file/device state lives in z/VM.

Dependencies and integration: depends on ccw bus/device APIs, z/VM diagnose calls 0x14/0x210, `asm/scsw.h`, Linux cdev/class, completions, mutexes, wait queues, and direct minor-to-devno mapping with 65,536 minors.

Risks: only one opener is allowed per device; read seek offsets must be page-aligned; writes require integral record lengths and cap to 511 records per I/O; offline refuses active references unless forced by remove; unsolicited device-end uevents hold references through workqueue scheduling.

Test signals: z/VM-only module load, reader vs punch/printer access-mode rejection, blocking/nonblocking open contention, diag14 EOF/no-medium cases, write record-length validation and interrupt status mapping, online/offline with active file descriptors, and unsolicited DE uevents.
