# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/tlbflush-radix.h

Purpose: declares radix-MMU TLB invalidation interfaces for Book3S64.

Important APIs/types/functions: exposes radix flush functions for TLB mm, page, range, kernel range, PID/LPID contexts, and page-size-aware invalidations used by radix page-table and memory hotplug paths.

Control flow: callers route radix flush requests here; implementation code chooses local versus global invalidation and appropriate `tlbie/tlbiel` or hypervisor sequences.

State and persistence: modifies processor/hypervisor translation caches. No header-owned state.

Dependencies and integration points: integrates with radix page-table updates, process/partition table management, KVM/LPID handling, memory hotplug, and kernel mapping changes.

Risks: radix invalidation must use correct PID/LPID and page-size encodings. Under-flushing can leave stale translations; over-flushing hurts performance.

Test signals: radix SMP TLB shootdown tests, KVM/LPID invalidation tests, memory hotplug, kernel ioremap changes, and page-size matrix testing.
