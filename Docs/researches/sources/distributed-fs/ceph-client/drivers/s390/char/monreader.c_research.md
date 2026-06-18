<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monreader.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/monreader.c

**Purpose:** `monreader.c` provides `/dev/monreader`, a misc character device for reading z/VM `*MONITOR` records from a shared DCSS segment via IUCV messages.

**Important APIs and functions:** Core types are `struct mon_msg` for queued IUCV monitor messages and `struct mon_private` for one opener's ring state. File operations are `mon_open()`, `mon_close()`, `mon_read()`, and `mon_poll()`. IUCV callbacks are `mon_iucv_path_complete()`, `mon_iucv_path_severed()`, and `mon_iucv_message_pending()`. Helpers validate monitor control areas using `mon_check_mca()` and acknowledge records through `mon_send_reply()`.

**Control flow, state, and persistence:** Module init requires z/VM, registers the IUCV handler, validates that the configured `mondcss` segment is shared code, loads it, converts the DCSS name to EBCDIC, and finally registers the misc device. Only one opener is allowed via `mon_in_use`. Incoming IUCV messages fill a 255-entry ring. `read()` first emits the 12-byte monitor control element, then the referenced records from the DCSS, advancing MCA offsets and replying when complete. Message-limit overflow is reported as `-EOVERFLOW` after the limit record is acknowledged.

**Dependencies and integration:** It depends on z/VM IUCV, DCSS extmem APIs, EBCDIC conversion, wait queues, miscdevice, and user-copy helpers.

**Risks and test signals:** Risks include malformed MCA pointers into the shared segment, races in the ring counters, blocking open waiting for connection confirmation, and correct reply accounting when the queue is full. Tests should cover non-z/VM load refusal, invalid DCSS type, single-open exclusion, poll readiness, nonblocking reads, disconnect handling, overflow, and partial reads across MCA and record boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monreader.c -->
