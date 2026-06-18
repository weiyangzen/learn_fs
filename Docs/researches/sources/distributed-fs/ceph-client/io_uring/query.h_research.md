# sources/distributed-fs/ceph-client/io_uring/query.h

Purpose: exposes the single `io_query()` registration handler.

Important APIs/types/functions: `int io_query(void __user *arg, unsigned nr_args)` is the only declaration.

Control flow: none in this header.

State and persistence: no state is declared.

Dependencies/integration: includes `io_uring_types.h` and is used by `register.c` for both `IORING_REGISTER_QUERY` on a ring and the blind fd `-1` query path.

Risks/test signals: compatibility depends on the prototype matching `register.c`. Build coverage and userspace query tests are the signal.
