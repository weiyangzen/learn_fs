# sources/distributed-fs/ceph-client/mm/numa_emulation.c

## Purpose

`numa_emulation.c` implements `numa=fake` boot-time NUMA emulation. It splits physical NUMA memory blocks into synthetic nodes, remaps CPU-to-node and APIC-to-node relationships, and rebuilds NUMA distance tables so the rest of the kernel can exercise NUMA policy on hardware with fewer or differently shaped physical nodes.

For Ceph-client development and validation, this is useful because page cache, writeback throttling, reclaim, and memory allocation behavior can be tested across synthetic NUMA nodes without requiring matching hardware.

## Important APIs, Types, And Functions

- `int emu_nid_to_phys[MAX_NUMNODES]`: maps emulated node IDs to the physical node they are carved from.
- `numa_emu_cmdline(char *str)`: stores the `numa=fake` command-line payload for later boot parsing.
- Split helpers: `split_nodes_interleave()`, `split_nodes_size_interleave_uniform()`, `split_nodes_size_interleave()`, `find_end_of_node()`, `uniform_size()`, and `mem_hole_size()`.
- Block helpers: `emu_find_memblk_by_nid()` and `emu_setup_memblk()`.
- `numa_emulation(struct numa_meminfo *numa_meminfo, int numa_dist_cnt)`: main transformation function.
- CPU mask hooks: `numa_add_cpu()` and `numa_remove_cpu()`, with debug and non-debug implementations.

## Control Flow

Early parameter parsing calls `numa_emu_cmdline()` and preserves the raw fake-NUMA string. Later `numa_emulation()` receives the physical `numa_meminfo` and current distance count. If no command line was provided, it builds identity `emu_nid_to_phys[]` and exits.

When emulation is requested, the function copies physical meminfo into `pi`, clears the emulated meminfo `ei`, initializes all emulated node mappings to `NUMA_NO_NODE`, and parses the command:

- A string containing `U` requests uniform splitting within each physical node into a specified number of nodes.
- A string containing `M` or `G` requests fake nodes with a fixed size.
- A plain number requests that total available memory be split into that many interleaved fake nodes.

The splitting helpers walk physical blocks, account for absent pages through `mem_hole_size()`, preserve at least `FAKE_NODE_MIN_SIZE` non-reserved memory per node where possible, avoid leaving unusably small fragments below DMA32 boundaries, and call `emu_setup_memblk()` to append each emulated block. `emu_setup_memblk()` records the fake range, sets the fake-to-physical mapping on first use, advances the physical block start, removes exhausted physical blocks, and logs the fake node range.

After splitting, `numa_emulation()` sanitizes `ei` with `numa_cleanup_meminfo()`. If a physical distance table exists, it copies the current `node_distance()` matrix into memblock memory. It then computes the highest emulated node and default physical node, rebuilds `numa_nodes_parsed` from emulated blocks, calls `fix_pxm_node_maps()` to avoid ACPI PXM collisions, commits `ei` back to `*numa_meminfo`, and updates CPU-to-node data through `numa_emu_update_cpu_to_node()`.

Distance handling is rebuilt in two phases. First, `numa_reset_distance()` clears the old table. Then each emulated pair receives either explicit distances parsed after `:` from the command line, a local/remote default if the physical node is outside the copied table, or the physical distance between the backing nodes. A second pass fills entries involving non-emulated physical nodes using the copied physical table. Finally the copied table is freed.

CPU hotplug hooks map a CPU to every online emulated node backed by the CPU's physical node. Non-debug mode updates `node_to_cpumask_map` directly; debug mode uses `debug_cpumask_set_cpu()`.

## State And Persistence Behavior

All major transformations happen during boot with `__init` data. The persistent result is the rewritten `numa_meminfo`, updated global `numa_nodes_parsed`, rebuilt NUMA distance table, modified CPU-to-node mappings, and `emu_nid_to_phys[]`, which remains needed by CPU add/remove callbacks.

If emulation fails at any validation step, control goes to `no_emu`, restores the physical parsed-node mask, and fills `emu_nid_to_phys[i] = i` so later CPU hooks still have a defined identity mapping.

## Dependencies And Integration Points

The file depends on generic memblock, topology, `numa_memblks` helpers, x86/architecture NUMA hooks in `asm/numa.h`, and ACPI NUMA PXM maps. It calls `numa_cleanup_meminfo()`, `numa_reset_distance()`, `numa_set_distance()`, `fix_pxm_node_maps()`, `numa_emu_update_cpu_to_node()`, `numa_emu_dma_end()`, and node-distance APIs.

Its integration point with memory management is early topology mutation before page allocator node registration. Filesystems such as Ceph see the effects indirectly through allocation locality, reclaim, dirty limits, and CPU/node masks.

## Risks And Edge Cases

- Bad command-line sizes or excessive fake node counts can fail emulation or force size adjustments.
- Memory holes and DMA32 boundary preservation make the final fake-node layout non-obvious; tests should inspect boot logs.
- The code assumes fixed-size arrays bounded by `MAX_NUMNODES` and `NR_NODE_MEMBLKS`; overproduction of fake blocks fails emulation.
- Distance override parsing is stateful over `emu_cmdline` after `:`; malformed or incomplete overrides fall back to physical/default distances.
- `phys_dist` allocation failure disables emulation when a distance table must be preserved.
- CPU masks intentionally associate one physical CPU with all emulated nodes backed by the same physical node; scheduler and locality behavior is synthetic rather than hardware-real.

## Test Signals

- Boot with `numa=fake=N`, fixed-size `numa=fake=SIZE`, and uniform `U` forms; verify `Faking node` logs and `/sys/devices/system/node/`.
- Validate `numa_nodes_parsed`, CPU masks, and `node_distance()` matrices after emulation.
- Exercise memory pressure and writeback workloads on fake nodes to confirm per-node accounting behaves consistently.
- Test malformed command lines and too-small sizes to ensure graceful fallback to identity mapping.
