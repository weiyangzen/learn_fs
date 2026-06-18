<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.h

**Purpose:** This header defines the SCLP message-buffer layout and writer API used by s390 line-mode console and tty code.

**Important APIs and types:** Packed hardware-facing structures are `mto`, `go`, `mdb_header`, `mdb`, and `msg_buf`. `struct sclp_buffer` overlays caller-provided SCCB pages with list linkage, embedded `sclp_req`, current message/line pointers, retry count, formatting settings, statistics, and completion callback. `NR_EMPTY_MSG_PER_SCCB` estimates worst-case newline capacity.

**Control flow, state, and persistence:** A `struct sclp_buffer` persists while being filled, queued, emitted, and returned to the caller's free-page list. Its embedded request means callers must not reuse the buffer page until the callback returns.

**Dependencies and integration:** It depends on Linux list handling and `struct sclp_req` from `sclp.h`. Console and tty drivers allocate pages, make buffers, write text, emit, and recycle pages through this interface.

**Risks and test signals:** Risks include callers passing non-DMA pages, reusing buffers before callbacks, inconsistent `columns`/`htab` settings, and assumptions about exact free-character capacity from `NR_EMPTY_MSG_PER_SCCB`. Test signals include buffer creation/unmake round trips, callback recycling, counter accuracy, and worst-case newline capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.h -->
