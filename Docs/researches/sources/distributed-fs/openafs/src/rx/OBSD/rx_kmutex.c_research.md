# sources/distributed-fs/openafs/src/rx/OBSD/rx_kmutex.c

Purpose: OpenBSD Rx kernel mutex source placeholder.

Important APIs/types/functions: none defined; locking is implemented by macros in `rx_kmutex.h`.

Control flow: the file contains only comments and relies on header-only behavior.

State/persistence: no runtime state.

Dependencies/integration: OpenBSD Rx kernel build.

Risks: no source-level synchronization code is present, and the header itself notes incomplete SMP support. Test signals are OpenBSD compile and runtime lock assertions.
