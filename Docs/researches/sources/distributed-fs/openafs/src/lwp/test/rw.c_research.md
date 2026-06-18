# sources/distributed-fs/openafs/src/lwp/test/rw.c

Purpose: readers/writer stress test for LWP scheduling and OpenAFS lock primitives.

Important APIs/types/functions: defines an intrusive queue with an embedded `struct Lock`, helpers `init`, `empty`, `insert`, and `Remove`, and LWP entry points `read_process` and `write_process`. `main` initializes LWP, a shared queue, reader LWPs, and one writer LWP.

Control flow: readers start, dispatch once, then repeatedly take a read lock, wait on the queue event while empty, remove a message, and dispatch. The writer takes a write lock, inserts fixed messages, releases the lock, and signals the queue event. `main` spins dispatching until all readers plus writer are asleep, then destroys LWPs and terminates support.

State and persistence: all state is in process memory: shared queue `q`, lock state, `asleep`, reader IDs, and LWP PCBs. No disk state.

Dependencies/integration: includes `lwp.h` and `afs/afs_lock.h`, linking with `liblwp` and `libopr`. It exercises LWP wait/signal plus lock read/write paths.

Risks and test signals: it intentionally demonstrates concurrent cooperative access but has simplistic queue locking, fixed messages, and busy delay loops. Success is visible through orderly message printing and clean process termination.
