# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_mutex.c

Purpose: Implements NFP hardware mutexes using MU atomic read/write/test-set operations, keyed by a 32-bit resource key and owned by the current CPP interface ID.

Important APIs/types/functions: `struct nfp_cpp_mutex` tracks CPP handle, MU target, recursion depth, address, and key. Public APIs are `nfp_cpp_mutex_init()`, `_alloc()`, `_free()`, `_lock()`, `_unlock()`, `_trylock()`, and `_reclaim()`.

Control flow: Allocation validates interface/target/address alignment and checks the stored key. `trylock()` verifies the key, performs MU `test_set_imm`, writes the owner if unlocked, and supports recursive locking by the same handle. `lock()` polls `trylock()` with warning/error timeouts. `unlock()` verifies key and owner, writes the unlocked value, and decrements recursion. `reclaim()` clears locks owned by the local interface.

State and persistence: Mutex state is device memory: owner/locked bits and key at a 64-bit MU location. Kernel state is only the handle depth and metadata.

Dependencies/integration: Used by `nfp_resource.c` to serialize resource table and resource entry access. Requires CPP scalar access and MU atomic target semantics from `nfp_target.c`.

Risks: Only MU target and 64-bit aligned addresses are supported. Force reclaim is dangerous if local users still exist. Recursive depth is per handle, not global. Timeout waits are polling-based because unlockers may be remote.

Test signals: Lock/unlock/trylock contention, recursion depth overflow, key mismatch, invalid target/address, timeout warning paths, and resource-table reclaim during probe.
