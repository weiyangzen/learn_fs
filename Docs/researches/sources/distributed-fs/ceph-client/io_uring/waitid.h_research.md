# sources/distributed-fs/ceph-client/io_uring/waitid.h

Purpose: declares waitid operation and cancellation helpers plus async wait option state.

Important APIs/types/functions: `struct io_waitid_async` stores the owning request and `struct wait_opts`. Prototypes cover prep, issue, cancel, and remove-all.

Control flow: none in the header.

State and persistence: defines per-request async wait state that owns wait options and pid refs until completion/free.

Dependencies/integration: includes `../kernel/exit.h` for `wait_opts`; used by waitid implementation and cancel paths.

Risks/test signals: changes to kernel wait internals can affect this header. Build and waitid cancellation tests are the signal.
