# sources/distributed-fs/ceph-client/kernel/events/internal.h

Purpose: shared private definitions for perf event internals, centered on `struct perf_buffer` and inline helpers for ring-buffer output, AUX sizing, recursion protection, and user stack support.

Important APIs/types/functions: `struct perf_buffer` holds refcounts, RCU/freeing state, data ring metadata, poll/wakeup state, mmap ownership/accounting, AUX metadata, and `data_pages[]`. It declares `rb_alloc()`, `rb_free()`, `rb_alloc_aux()`, `rb_free_aux()`, `ring_buffer_get()`, `ring_buffer_put()`, `perf_mmap_to_page()`, and `perf_event_aux_event()`. Helpers include `rb_free_rcu()`, `rb_toggle_paused()`, `rb_has_aux()`, `page_order()`, `data_page_nr()`, `perf_data_size()`, and `perf_aux_size()`.

Control flow: `DEFINE_OUTPUT_COPY()` creates copy/skip/user-copy helpers around `__DEFINE_OUTPUT_COPY_BODY`, which advances `perf_output_handle` state across pages and wraps ring indices. User copies disable page faults and use `__copy_from_user_inatomic()`. Recursion helpers use `interrupt_context_level()` to reject same-context re-entry.

State and persistence: `perf_buffer` state is transient kernel memory associated with mmaped perf events. It tracks writer head, nesting, lost records, wakeup stamps, user pages, mmap refcounts, user accounting, and AUX producer/consumer metadata. The mmap user page exposes selected state to userspace while the event mapping lives.

Dependencies and integration points: depends on hardirq context helpers, uaccess, refcounts, perf event types, page allocation configuration, architecture `arch_perf_out_copy_user()`, and optional user stack dump support. The copy macros are tightly coupled to `struct perf_output_handle`.

Risks: callers must initialize output handles correctly before invoking copy helpers. User copies can partially fail with page faults disabled. Recursion counters must be balanced. Zero-page buffers are forced paused by `rb_toggle_paused()`.

Test signals: perf ring-buffer, mmap sampling, AUX tracing, static analysis, lockdep, and user-copy fault injection exercise the contracts defined here.
