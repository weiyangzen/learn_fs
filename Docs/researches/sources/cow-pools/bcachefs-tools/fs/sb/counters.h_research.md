# File Research: sources/cow-pools/bcachefs-tools/fs/sb/counters.h

This header declares counter APIs and defines event/trace helper macros.

Key responsibilities:
- Declares superblock counter load/store and filesystem counter lifecycle functions.
- Declares counter reset, recent-counter text output, and ioctl query.
- Exposes counter names, flags, stable map, and field ops.
- Defines `event_inc()` and `event_add()` for typed counter updates.
- Defines trace-coupled counter macros:
  - `event_trace()`
  - `event_add_trace()`
  - `event_inc_trace()`
  - `_fn` variants for out-of-line cold trace formatting.

Important invariants:
- `counter_typecheck()` uses `BUILD_BUG_ON()` to ensure sector counters use `event_add()` and event counters use `event_inc()`.
- Trace macros only build printbuf text when the tracepoint is enabled.
- `_fn` variants keep hot paths smaller by moving formatting into a function call.

Dependencies:
- Uses tracepoint naming conventions, printbuf, superblock I/O, and counter format/types.

Research notes:
- These macros are used throughout journal, btree, allocator, and data paths to keep accounting type-safe at compile time.
