# sources/distributed-fs/ceph-client/io_uring/fdinfo.h

## Purpose
This header declares the procfs fdinfo printer for io_uring files.

## Important APIs, Types, And Functions
- `io_uring_show_fdinfo(struct seq_file *m, struct file *f)`.

## Control Flow
No local control flow.

## State And Persistence
No state is defined here.

## Dependencies And Integration Points
The declaration is used by io_uring file operations/proc integration when `CONFIG_PROC_FS` includes `fdinfo.o`.

## Risks And Edge Cases
Prototype drift would break fdinfo integration. The implementation relies on callers passing an io_uring file with `private_data` set to `struct io_ring_ctx`.

## Test Signals
Build coverage with procfs and readable `/proc/<pid>/fdinfo/<fd>` output validate it.
