# sources/distributed-fs/openafs/src/audit/audit-file.c

## Purpose
`audit-file.c` implements the file audit backend. It writes formatted audit records to a file or FIFO.

## Important APIs, types, and functions
`struct file_context` holds `FILE *auditout`. Backend callbacks are `send_msg`, `open_file`, `print_interface_stats`, `create_interface`, and `close_interface`, collected in `audit_file_ops`.

## Control flow
`create_interface` allocates context. `open_file` detects FIFOs with `lstat`; FIFOs are opened write-only/nonblocking, while regular paths are rotated to `<name>.old` with `rk_rename` and reopened with truncate/create. It then wraps the fd with `fdopen("a")`. `send_msg` writes the message bytes, appends newline, and flushes. `close_interface` closes the stream and frees context.

## State and persistence
Persistent effects are audit log file rotation and appending audit records. FIFO mode does not rotate. The context owns the open stream until shutdown.

## Dependencies and integration points
Used by `audit.c` through `audit_file_ops` and is the default audit interface. It depends on roken portability wrappers and standard file APIs.

## Risks
If `fdopen` fails, the opened fd is not closed in that branch. Regular-file open mode uses `0666`, relying on umask. Rotation unconditionally renames an existing file and can overwrite the `.old` target depending on platform rename semantics. FIFO nonblocking open can fail when no reader exists, disabling that audit sink.

## Test signals
Cover regular-file rotation, FIFO open with and without reader, unwritable paths, `fdopen` failure injection, message newline/flush behavior, and close idempotence with null context.
