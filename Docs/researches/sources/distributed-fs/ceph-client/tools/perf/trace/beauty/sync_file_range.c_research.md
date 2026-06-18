# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/sync_file_range.c

Purpose: Formats `sync_file_range(2)` flag arguments.

Important APIs/types/functions: `syscall_arg__scnprintf_sync_file_range_flags` delegates to `sync_file_range__scnprintf_flags`, which recognizes the composite `SYNC_FILE_RANGE_WRITE_AND_WAIT` before formatting individual bits.

Control flow: The formatter first checks whether the input contains the full write-and-wait composite and prints that name while clearing the component bits. It then appends remaining flags through `strarray__scnprintf_flags`.

State and persistence: Stateless formatting.

Dependencies and integration points: Includes generated `sync_file_range_arrays.c`, Linux fs flags, and perf beauty helpers.

Risks: Composite-first output can produce no separator before later flags depending on `strarray__scnprintf_flags` behavior with a non-empty destination; tests should catch formatting around mixed composite and extra bits.

Test signals: Trace zero, wait-before, write, wait-after, full write-and-wait, and unknown flag combinations.
