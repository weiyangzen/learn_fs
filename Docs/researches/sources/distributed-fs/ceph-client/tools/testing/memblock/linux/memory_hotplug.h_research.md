<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/memory_hotplug.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/memory_hotplug.h

## Purpose

`linux/memory_hotplug.h` provides the small memory-hotplug surface needed by memblock code in the simulator, mainly the movable-node enablement query.

## Important APIs, Types, and Functions

It includes NUMA, PFN, cache, and type headers; declares external `bool movable_node_enabled`; and defines `movable_node_is_enabled()` to return that global.

## Control Flow

The only behavior is reading `movable_node_enabled`. Memblock code can branch on the same API it uses in the kernel.

## State and Persistence Behavior

`movable_node_enabled` is external process-local state. The header does not define or persist it.

## Dependencies and Integration Points

It integrates with memblock code and `linux/mmzone.h` in this simulator. Test setup may control `movable_node_enabled` through command-line or common helpers.

## Risks and Edge Cases

The simulator models only the boolean gate, not real memory hotplug operations. Hotplug-specific page lifecycle, zone growth, or online/offline transitions are outside this test harness.

## Test Signals

Build success and tests that toggle movable-node behavior through common memblock parameters are the useful signals. New unresolved references to hotplug APIs indicate the shim is incomplete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/memory_hotplug.h -->
