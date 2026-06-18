# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kexec_ranges.h

Purpose: Declares helpers for building, sorting, adding, removing, and querying PowerPC memory ranges used by kexec and crash dump setup.

Important APIs, types, and functions: Defines `MEM_RANGE_CHUNK_SZ` and declares `sort_memory_ranges()`, `realloc_mem_ranges()`, `add_mem_range()`, `remove_mem_range()`, `get_exclude_memory_ranges()`, `get_reserved_memory_ranges()`, `get_crash_memory_ranges()`, and `get_usable_memory_ranges()`.

Control flow: Kexec code collects usable/reserved/excluded ranges, dynamically grows `struct crash_mem`, sorts/merges ranges, removes overlaps, and passes final ranges into FDT or elfcorehdr setup.

State and persistence: Range arrays are runtime allocations tied to image load/crash preparation.

Dependencies and integration points: Depends on `struct crash_mem` from crash/kexec infrastructure and platform memory discovery.

Risks: Range merging/removal bugs can include reserved memory or exclude usable memory. Allocation growth must preserve existing ranges on failure.

Test signals: Overlapping range add/remove, sorting with merge enabled/disabled, crashkernel overlap, hotplug memory ranges, and low-memory edge cases.
