# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.c

Purpose: this file provides small reusable helpers for changelog library I/O, path encoding, buffered line reading over file descriptors, seek/truncate state reset, and pthread cleanup.

Important APIs: `gf_changelog_write` loops until a buffer is fully written or write fails. `gf_rfc3986_encode_space_newline` percent-encodes bytes using an exception table. `gf_readline` reads one line with a thread-local `read_line_t` buffer. `gf_lseek` and `gf_ftruncate` wrap syscall operations and reset the thread-local line buffer. `gf_thread_cleanup` cancels and joins a thread, validating `PTHREAD_CANCELED`.

Control flow: `gf_readline` uses `my_read` to fill a per-thread buffer with `sys_read`, then returns on newline, EOF, max length, or error. Reset wrappers clear that buffer because tracker files are truncated and repositioned during scans. `gf_thread_cleanup` logs warning messages for cancel, join, or non-canceled termination failures.

State and persistence behavior: no persistent state is owned here, but file descriptor writes, truncates, and seeks affect changelog tracker files. Thread-local state is intentionally reset on seek/truncate to avoid stale buffered data.

Dependencies and integration points: depends on changelog mem types, helper declarations, message IDs, and GlusterFS syscall wrappers. It is used by live and history changelog APIs.

Risks: `gf_ftruncate` ignores its `length` parameter and always truncates to zero, which matches current callers but is surprising API behavior. `gf_rfc3986_encode_space_newline` uses `sprintf` while advancing through the output buffer; callers must provide sufficient space. `gf_readline` is thread-local but only supports one active fd buffer per thread.

Test signals: partial writes, EOF without newline, long-line truncation at `maxlen`, seek/truncate followed by reads, thread cleanup for cancellable and non-cancellable threads, and encoding of spaces/newlines versus reserved bytes.
