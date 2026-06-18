# sources/distributed-fs/openafs/src/lwp/test/seltest.h

Purpose: shared protocol and helper declarations for LWP IOMGR select tests.

Important APIs/types/functions: defines `selcmd_t` with command, delay, flags, and info fields. Commands are `SC_PROBE`, `SC_WRITE`, and `SC_END`; flags include `SC_WAIT_ONLY` and `SC_WAIT_OOB`. It defines data marker range constants and declares helpers from `selsubs.c`.

Control flow: no runtime control flow. It shapes the client/server command contract.

State and persistence: no state or persistence.

Dependencies/integration: used by `selclient.c`, `selserver.c`, and `selsubs.c`. Under `NEEDS_ALLOCFDSET` it declares IOMGR fd-set allocation functions for compatibility testing.

Risks and test signals: structure layout is sent directly over TCP without byte-order conversion, so tests assume same-endian compatible client/server. Protocol constants are small and stable.
