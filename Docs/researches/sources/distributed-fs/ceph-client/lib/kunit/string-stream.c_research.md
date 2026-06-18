# sources/distributed-fs/ceph-client/lib/kunit/string-stream.c

Purpose: provides a small append-only string builder used by KUnit logs and assertion formatting.

Important APIs/types/functions: `alloc_string_stream()`, `string_stream_add()`, `string_stream_vadd()`, `string_stream_get_string()`, `string_stream_append()`, `string_stream_clear()`, `string_stream_is_empty()`, `string_stream_destroy()`, `kunit_alloc_string_stream()`, and `kunit_free_string_stream()`.

Control flow: each add computes formatted length with a copied `va_list`, allocates a fragment and char buffer, formats into it, optionally appends one newline if missing, then adds the fragment to the tail under a spinlock while updating total length. `get_string()` allocates a full buffer and concatenates all fragments. Managed allocation queues a KUnit action to destroy the stream; managed free releases that action immediately.

State/persistence: maintains `length`, fragment list, spinlock, GFP mask, and `append_newlines` flag. The stream persists until explicit destroy or KUnit cleanup.

Dependencies/integration: used by KUnit logging and assertion rendering. Uses slab allocation, list APIs, spinlocks, and static stub redirection in `string_stream_destroy()`.

Risks: `string_stream_append()` passes another stream's content as the format string to `string_stream_add()`, so content containing percent sequences could be interpreted. Fragment-per-add design may be allocation-heavy. `string_stream_is_empty()` reads list state without taking the stream lock.

Test signals: `string-stream-test.c` covers initialization, exact concatenation, append behavior, automatic newlines, empty adds, managed cleanup, and basic performance metrics.
