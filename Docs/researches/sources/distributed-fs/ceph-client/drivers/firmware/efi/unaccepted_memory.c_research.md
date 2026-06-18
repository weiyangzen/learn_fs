# sources/distributed-fs/ceph-client/drivers/firmware/efi/unaccepted_memory.c

Purpose: Manages EFI unaccepted-memory bitmaps for confidential-computing guests, accepting pages on demand and reporting whether ranges still contain unaccepted memory.

Important APIs/types/functions: `accept_memory()` accepts a physical range and clears the corresponding bitmap bits. `range_contains_unaccepted_memory()` checks bitmap state. `accept_range` and `accepting_list` coordinate concurrent acceptance of overlapping unit-size ranges. Optional vmcore callback `unaccepted_memory_vmcore_pfn_is_ram()` excludes unaccepted pages from crash dump RAM.

Control flow: Calls first obtain the EFI unaccepted table and clamp the request to the bitmap-covered physical range. Both acceptance and lookup extend unit-aligned end boundaries by one unit to avoid speculative or unaligned loads into unaccepted memory. `accept_memory()` serializes overlapping ranges, iterates set bit ranges, calls `arch_accept_memory()`, clears bits, removes the active range, and touches the soft lockup watchdog.

State and persistence behavior: The persistent state is the EFI-provided bitmap, modified in place as memory becomes accepted. `accepting_list` is transient in-kernel synchronization state protected by `unaccepted_memory_lock`.

Dependencies and integration points: Depends on `efi_get_unaccepted_table()`, architecture acceptance hooks, bitmap helpers, spinlocks, crash dump vmcore callbacks, and confidential-computing platform semantics such as TDX.

Risks and test signals: Deadlock avoidance depends on interrupt-disabled locking around acceptance. Off-by-one bitmap translation can accept too little or scan outside the represented range. Test signals include concurrent acceptance stress, unit-boundary lookups, kdump filtering, and platform-specific acceptance validation under TDX/SEV-SNP-like guests.
