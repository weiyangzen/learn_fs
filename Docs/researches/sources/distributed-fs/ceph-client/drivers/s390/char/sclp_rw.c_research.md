<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.c

**Purpose:** `sclp_rw.c` is the reusable line-mode SCLP message writer used by the console and tty drivers.

**Important APIs and functions:** Public functions are `sclp_rw_init()`, `sclp_make_buffer()`, `sclp_unmake_buffer()`, `sclp_write()`, `sclp_buffer_space()`, `sclp_chars_in_buffer()`, and `sclp_emit_buffer()`. Internals `sclp_initialize_mto()` and `sclp_finalize_mto()` construct SCLP message text objects inside an SCCB page. `sclp_writedata_callback()` handles Write Event Data completion and retry logic.

**Control flow, state, and persistence:** A caller supplies a 4 KiB DMA page; `sclp_make_buffer()` places `struct sclp_buffer` at the end and uses the front as the SCCB. `sclp_write()` parses ASCII text, filters nonprintables, translates printable characters to SCLP EBCDIC, expands tab/form/vertical/backspace behavior, and accumulates MTO objects. `sclp_emit_buffer()` finalizes any open line, prepares the embedded `sclp_req`, and submits it. Completion retries selected equipment/resource responses once, including removing processed event buffers for partial completion.

**Dependencies and integration:** It registers send capability for `EVTYP_MSG_MASK`, depends on `sclp.h` request APIs and EBCDIC helpers, and is shared by `sclp_con.c` and `sclp_tty.c`.

**Risks and test signals:** Risks include SCCB space accounting, partial processed-buffer retry, message loss after retry exhaustion, tab/backspace formatting quirks, and `init_done` not synchronized. Tests should cover newline splitting, long-line buffer exhaustion, bell flag, null termination behavior, retry response codes, and buffer space/character counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_rw.c -->
