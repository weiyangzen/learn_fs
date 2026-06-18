# sources/distributed-fs/ceph-client/io_uring/register.h

Purpose: small public registration header for helpers needed outside `register.c`.

Important APIs/types/functions: declares `io_eventfd_unregister()` and `io_unregister_personality()`.

Control flow: no control flow.

State and persistence: no state defined; declarations operate on `io_ring_ctx` eventfd and personality state.

Dependencies/integration: used by registration dispatch and teardown paths that need to remove eventfd notification or credentials personalities.

Risks/test signals: prototype drift would break cleanup and unregister call sites. Build and personality/eventfd registration tests are the signal.
