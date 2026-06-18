# sources/distributed-fs/ceph-client/kernel/events/ring_buffer.c

Purpose: implements perf event data and AUX ring buffers. It reserves space for records, publishes producer heads to mmap consumers, emits lost-record notifications, handles wakeups, allocates/free storage, and coordinates AUX tracing buffers used by PMU drivers.

Important APIs/types/functions: normal data APIs are `perf_output_begin_forward()`, `perf_output_begin_backward()`, `perf_output_begin()`, `perf_output_copy()`, `perf_output_skip()`, and `perf_output_end()`. AUX APIs are `perf_aux_output_begin()`, `perf_aux_output_end()`, `perf_aux_output_skip()`, `perf_aux_output_flag()`, `perf_get_aux()`, `perf_output_copy_aux()`, `rb_alloc_aux()`, and `rb_free_aux()`. Allocation/mapping APIs are `rb_alloc()`, `rb_free()`, and `perf_mmap_to_page()`.

Control flow: `__perf_output_begin()` resolves inherited events to the parent, obtains the RCU-protected ring buffer, rejects paused/missing buffers, accounts pending lost samples, enters nested writer tracking, atomically advances `rb->head` after checking `data_tail` unless overwrite mode is active, computes the handle page/offset, and optionally writes `PERF_RECORD_LOST`. `perf_output_end()` publishes the head through `perf_output_put_handle()` and drops RCU. AUX begin/end creates a refcounted producer transaction, checks space in non-overwrite mode, commits `aux_head`, optionally emits `PERF_RECORD_AUX`, and wakes consumers on watermarks or truncation.

State and persistence: data ring state includes `head`, `user_page->data_head`, `data_tail`, `lost`, `wakeup`, `poll`, `nest`, `paused`, and `overwrite`. AUX state includes `aux_head`, `aux_tail`, `aux_nest`, `aux_wakeup`, `aux_watermark`, `aux_refcount`, `aux_mmap_count`, page arrays, and PMU private `aux_priv`. State is mmap-visible for the lifetime of the perf event mapping.

Dependencies and integration points: integrates perf ownership and fasync wakeups, irq_work, PMU AUX setup/free callbacks, page allocator or vmalloc backing, RCU lifetime helpers, mmap page fault translation, and output copy helpers from `internal.h`. PMU drivers must satisfy hardware ordering before ending AUX output.

Risks: memory ordering is critical between kernel data writes, `data_head`, userspace reads, and `data_tail`. NMI/IRQ nested writers can advance the head during publication, so stale publication must be retried. AUX nesting is unsupported. Refcount ordering prevents freeing AUX pages from atomic contexts. Large contiguous AUX allocations may fail or fragment.

Test signals: perf mmap sampling, overwrite/non-overwrite ring tests, lost sample tests, wakeup watermark tests, AUX PMU tests, mmap page translation tests, and allocation fault injection cover the important paths.
