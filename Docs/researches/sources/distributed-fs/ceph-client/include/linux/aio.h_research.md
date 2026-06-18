<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aio.h -->
# sources/distributed-fs/ceph-client/include/linux/aio.h

## Purpose
`aio.h` declares kernel asynchronous I/O hooks needed by process teardown and kiocb cancellation.

## Important APIs, types, and functions
It forward-declares `struct kioctx`, `struct kiocb`, and `struct mm_struct`, defines `kiocb_cancel_fn`, and declares `exit_aio()` and `kiocb_set_cancel_fn()` when `CONFIG_AIO` is enabled. Disabled stubs are no-ops.

## Control flow
`exit_aio()` is called during mm/process teardown to release AIO contexts. `kiocb_set_cancel_fn()` lets a request install cancellation behavior.

## State and persistence behavior
AIO context and request state live in implementation structures. Cancellation function pointers persist on requests until completion/cancel.

## Dependencies and integration points
It includes AIO UAPI definitions and integrates fs/aio code, kiocb users, and mm lifetime.

## Risks and test signals
Risks include no-op stubs hiding missing cleanup in non-AIO builds, cancellation races, and teardown ordering with outstanding I/O. Test signals include AIO syscall tests, process exit with pending I/O, request cancellation, and config-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/aio.h -->
