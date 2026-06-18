# File Research: sources/cow-pools/openzfs/lib/libzpool/arc_os.c

Userland ARC OS hooks for libzpool. These are simplified memory-sizing and pressure callbacks for tests/tools rather than real kernel memory-management integration.

Key behavior:
- `arc_default_max()` derives a default ARC cap from physical memory, reserving roughly 1 GiB when possible and otherwise using the minimum.
- `arc_available_memory()` normally reports abundant memory but occasionally returns `-1024` to simulate pressure.
- `arc_all_memory()` reports half of `physmem`.
- `arc_free_memory()` returns a random amount up to 20% of all memory.
- Memory throttle and hotplug registration are no-ops.

This gives libzpool enough ARC policy input to run SPA/ZIO logic in userland.
