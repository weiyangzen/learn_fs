# sources/distributed-fs/ceph-client/arch/mips/mm/c-octeon.c

Purpose: Cavium Octeon-specific cache initialization, cache flush operations, and cache error notification handling.

Important APIs/functions: `octeon_cache_init()` probes caches, initializes global cache flush function pointers, builds page routines, and installs the Octeon cache error vector. `register_co_cache_error_notifier()` and `unregister_co_cache_error_notifier()` expose a raw notifier chain. Exception handlers `cache_parity_error_octeon_recoverable()` and `_non_recoverable()` report or panic.

Control flow: data-cache flushing is mostly no-op because Octeon flushes dcache on TLB changes. I-cache operations use local `synci` and SMP IPIs/calls for other cores. `probe_octeon()` derives cache metadata from CPU type/config registers and logs it.

State and persistence: global `cache_err_dcache[NR_CPUS]` stores dcache error state captured by the low-level vector; cache function pointers become global runtime MM behavior.

Dependencies and integration: depends on Octeon CPU helpers, SMP, `set_handler()`, `asm/octeon/octeon.h`, and common `cache.c` globals.

Risks and test signals: test on Octeon generations, SMP I-cache invalidation, notifier behavior, recoverable versus nested error paths, and unsupported CPU panic. Validate cache metadata logged during boot.
