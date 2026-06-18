# sources/distributed-fs/ceph-client/include/linux/ring_buffer.h

Purpose: this header declares the generic tracing ring buffer API used by ftrace and related tracing code for per-CPU event storage, reading, polling, mmap, and remote-buffer support.

Important APIs/types/functions: `struct ring_buffer_event` encodes `type_len` and 27-bit time delta. `enum ring_buffer_type` defines padding, time-extend, absolute timestamp, and data event encodings. APIs cover event length/data/timestamp, discard/commit, allocation and range/remote allocation, wait/poll/wakeup, resize, overwrite mode, reserve/commit/write, nesting guards, peek/consume, iterator reads, size/statistics, reset, optional CPU swap, record enable/disable, timestamp clock control, dirty page counts, read-page operations, print helpers, sub-buffer order/size, mmap/unmap, descriptor walking, and remote callbacks.

Control flow: writers reserve an event, fill its payload, and commit, or use `ring_buffer_write()`. Readers peek/consume directly, use iterators, read pages, poll for availability, or mmap buffers. Timestamp records encode short deltas inline and use extension records when needed. Recording can be disabled globally or per CPU; overwrite mode changes producer behavior when buffers fill.

State and persistence: opaque `trace_buffer` owns per-CPU buffers, timestamps, counters, clock callback, overwrite/recording flags, page lists, mmap state, and reader pages. Event headers persist in buffer pages until consumed or overwritten.

Dependencies and integration points: depends on MM, seq_file, poll, trace mmap UAPI, lock class keys, guard macros, tracing `trace_seq`, and CPU hotplug preparation through `trace_rb_cpu_prepare`.

Risks: commit/discard ordering is strict; discarded events must not be committed. Timestamp encoding depends on 27-bit deltas and architecture alignment. mmap descriptor sizing must match page counts. Test signals include tracing ring-buffer selftests, concurrent producer/consumer stress, timestamp normalization, overwrite/non-overwrite behavior, mmap readers, CPU hotplug, nested write guard usage, and remote buffer callbacks.
