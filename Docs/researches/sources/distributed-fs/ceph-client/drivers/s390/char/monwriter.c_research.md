<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monwriter.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/monwriter.c

**Purpose:** `monwriter.c` exposes `/dev/monwriter`, allowing user space to submit z/VM APPLDATA monitor records through the `appldata_asm()` diagnose interface.

**Important APIs and functions:** `struct mon_buf` stores an active APPLDATA record buffer and its header. `struct mon_private` stores write parsing state for one file descriptor. `monwrite_diag()` builds `appldata_product_id` and parameter-list structures and issues the monitor command. `monwrite_new_hdr()` validates and allocates or finds records; `monwrite_new_data()` starts interval/config records or emits one-shot events.

**Control flow, state, and persistence:** Each write stream is parsed as repeated `struct monwrite_hdr` followed by `datalen` bytes. Partial writes are supported through `hdr_to_read` and `data_to_read`. Interval and config records persist in the descriptor list and consume global `mon_buf_count` capacity until stopped or file close. Event records are sent and immediately freed. `monwrite_close()` stops remaining non-event records and releases all buffers.

**Dependencies and integration:** The driver is z/VM-only, uses miscdevice registration, per-file mutex serialization, `asm/appldata.h`, `asm/monwriter.h`, DMA-capable record data allocations, and Linux user-copy APIs.

**Risks and test signals:** Risks include the global `mon_buf_count` being updated without a global lock across file descriptors, diagnostic errors mapped only coarsely, partial write errors resetting parser state, and ensuring stop records find matching interval/config records. Test signals include fragmented header/data writes, invalid header lengths/functions, max buffer exhaustion, close-time stop calls, event freeing, concurrent writers, and z/VM gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/monwriter.c -->
