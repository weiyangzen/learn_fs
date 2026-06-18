# sources/distributed-fs/ceph-client/include/uapi/linux/kernel-page-flags.h

## Purpose
`kernel-page-flags.h` assigns bit numbers for page flags exported through kernel page-monitoring interfaces such as `/proc/kpageflags`.

## Important APIs, Types, and Functions
Constants include `KPF_LOCKED`, `KPF_REFERENCED`, `KPF_UPTODATE`, `KPF_DIRTY`, `KPF_LRU`, `KPF_ACTIVE`, `KPF_SLAB`, `KPF_WRITEBACK`, `KPF_RECLAIM`, `KPF_BUDDY`, `KPF_MMAP`, `KPF_ANON`, `KPF_SWAPCACHE`, `KPF_SWAPBACKED`, compound page bits, huge/THP bits, unevictable, hwpoison, nopage, KSM, offline, zero page, idle, and page-table markers.

## Control Flow
Userspace reads page-flag bitmasks from procfs and decodes set bits using these constants. The kernel sets and clears underlying page flags during memory-management operations.

## State and Persistence
The bitmasks reflect live physical page state and are highly volatile. No state is stored by the header.

## Dependencies and Integration Points
It has no includes. Integration points include procfs page monitors, memory diagnostics, NUMA/VM tooling, crash analysis, and tests for reclaim/compaction behavior.

## Risks and Test Signals
Tests should validate bit numbering against `/proc/kpageflags`, reserved/unused flags, THP/compound transitions, idle-page tracking, and permission restrictions for page-monitoring files. ABI risk is that bit numbers are externally decoded and must remain stable.
