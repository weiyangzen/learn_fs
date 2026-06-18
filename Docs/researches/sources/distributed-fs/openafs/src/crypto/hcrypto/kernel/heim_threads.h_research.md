# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/heim_threads.h

This kernel threading shim maps Heimdal mutex macros to OpenAFS kernel mutexes. `HEIMDAL_MUTEX` is `afs_kmutex_t *`, initialized to the global `hckernel_mutex`, and lock operations expand to `MUTEX_INIT`, `MUTEX_ENTER`, `MUTEX_EXIT`, and `MUTEX_DESTROY`.

It also disables userspace random methods by defining `NO_RAND_UNIX_METHOD` and `NO_RAND_EGD_METHOD`. State is the external global mutex declared in `rand.c` and initialized by `init_hckernel_mutex`.

Dependencies are `rx_kmutex.h` and OpenAFS kernel synchronization primitives. Integration is hcrypto PRNG/global state in kernel builds. Risks include all Heimdal mutex users sharing one global mutex and the initializer macro's trailing semicolon style. Test signals are kernel crypto concurrency tests and successful initialization from `osi_Init` before first hcrypto use.
