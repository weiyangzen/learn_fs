# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.c

Purpose: this optional debugfs file implements the SNIC in-memory circular trace buffer.

Important APIs, types, and functions: `snic_trc_init()` allocates a vmalloc trace buffer sized by `snic_trace_max_pages`, initializes lock and indexes, creates debugfs trace files, and enables tracing. `snic_get_trc_buf()` reserves the next trace record with wraparound and overwrite handling. `snic_get_trc_data()` returns the next complete formatted record and advances the read index. `snic_trc_free()` disables tracing, removes debugfs files, and frees the buffer.

Control flow: hot paths call `SNIC_TRC()` from `snic_trc.h`, which calls `snic_trace()`, which obtains a record and writes data fields, setting timestamp last as the completion marker. Debugfs trace reads call `snic_get_trc_data()` to drain records.

State and persistence: state is `snic_glob->trc`: spinlock, buffer pointer, max index, read/write indexes, and enable flag. It is runtime-only and lost on unload.

Dependencies and integration: compiled only with `CONFIG_SCSI_SNIC_DEBUG_FS`. It uses vmalloc, jiffies/time formatting, debugfs setup from `snic_debugfs.c`, and trace record definitions/macros from `snic_trc.h`.

Risks: trace records store `char *fn` function-name pointers, which are valid only while module text remains loaded. Reads are destructive. The writer marks `td->ts = 0` only when overwriting read index, so readers use timestamp as a coarse write-complete marker.

Test signals: enable tracing under I/O, read trace repeatedly, force wraparound with a small page count, unload while trace files are open, and verify no invalid memory access with KASAN.
