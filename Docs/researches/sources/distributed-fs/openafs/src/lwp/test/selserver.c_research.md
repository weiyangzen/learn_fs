# sources/distributed-fs/openafs/src/lwp/test/selserver.c

Purpose: server-side IOMGR select test for high-numbered fds, connection handling, read/write readiness, and exception/OOB fd sets.

Important APIs/types/functions: defines `clientHandle_t` pool entries with fd sets and LWP process IDs. `getClientHandle` reserves a pool slot. `handleRequest` waits for an accepted connection signal and processes commands. `handleWrite` reads client data with `IOMGR_Select` and echoes it back.

Control flow: `main` initializes IOMGR and a pool of LWP handler threads, creates/listens on a socket, then selects for accept readiness and exceptions. Accepted sockets are stored in a free client handle and signaled to the corresponding LWP. Handler LWPs wait on `ch_state`, select on their socket, read a `selcmd_t`, branch on `SC_PROBE`, `SC_WRITE`, or `SC_END`, and return the handle to the pool.

State and persistence: in-memory pool `clientHandles`, `nThreads`, socket fds, and fd sets. No disk persistence.

Dependencies/integration: uses LWP process creation/signaling, IOMGR fd-set allocation and select, and `selsubs` helpers.

Risks and test signals: the condition `while (nThreads > MAX_THREADS)` appears off by one for a full pool and may not throttle at exactly `MAX_THREADS`; `nThreads` is cooperative-thread shared. Assertions check fd-set cleanup and read/write results. A successful client roundtrip validates IOMGR readiness paths.
