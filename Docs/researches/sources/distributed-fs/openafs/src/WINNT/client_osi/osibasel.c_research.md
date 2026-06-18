## sources/distributed-fs/openafs/src/WINNT/client_osi/osibasel.c

Purpose: Implements the base OSI mutex and read/write lock primitives for Windows.

Important APIs/functions: `osi_BaseInit` initializes hash critical sections, TLS indexes, and lock-reference free list state. Lock APIs include obtain/release read/write/mutex, try read/write/mutex, convert read/write, sleep while releasing a lock, finalize/init locks, and query lock state. Optional lock-order validation records held locks in thread-local queues.

Control flow/state: Each lock is assigned an atomic critical-section bucket. Obtain paths enter the bucket, inspect flags/readers/waiters, either set ownership or wait via `osi_TWait`; release paths clear ownership and signal sleepers via `osi_TSignalForMLs`. TLS lock-reference queues are maintained only when validation is enabled. Process-global state includes critical sections, TLS indexes, validation flag, atomic index counter, and a free list.

Dependencies/integration: Uses Windows critical sections/interlocked operations, OSI sleep queues, queue helpers, thread ID helpers, panic/assert/log infrastructure, and pluggable lock type operations for non-base lock types.

Risks/tests: Correctness depends on handing the critical section to sleep/signal helpers exactly once. TLS indexes are never freed, acceptable for process lifetime but relevant to repeated init tests. Validation free list can grow without bound. Test read/write fairness under waiters, recursive/self-lock assertions, conversion races, sleep/reacquire paths, try-lock failure with waiters, lock hierarchy violations, and stat-lock delegation.
