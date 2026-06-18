# sources/distributed-fs/ceph-client/arch/x86/kernel/amd_nb.c

## Purpose
`amd_nb.c` provides shared AMD/Hygon northbridge discovery and helper functions for older AMD64 northbridge and derivative devices. It caches per-node PCI function devices, exposes northbridge feature flags, supports L3 cache partitioning controls, provides MMCONFIG range discovery, and serializes/flushed GART TLB requests for the GART IOMMU/AGP stack.

## Important APIs, Types, and Functions
- Device tables: `amd_nb_misc_ids[]` and `amd_nb_bus_dev_ranges[]`.
- Cached global state: `amd_northbridges` and `flush_words`.
- Exported helpers: `amd_nb_num()`, `amd_nb_has_feature()`, `node_to_amd_nb()`, `amd_flush_garts()`.
- Discovery: `amd_cache_northbridges()`, `early_is_amd_nb()`, and `init_amd_nbs()`.
- MMCONFIG: `amd_get_mmconfig_range()`.
- L3 controls: `amd_get_subcaches()` and `amd_set_subcaches()`.
- GART flush setup: `amd_cache_gart()` and `amd_flush_garts()`.
- Erratum handling: `fix_erratum_688()` and `__fix_erratum_688()`.

## Control Flow
At `fs_initcall`, `init_amd_nbs()` checks for AMD/Hygon vendor, caches northbridge devices by calling `amd_num_nodes()` and `amd_node_get_func()` for functions 3 and 4, detects GART and L3 feature flags, caches GART flush register values, and applies erratum 688 if needed. Consumers then query the cached state through exported helpers.

GART flushing serializes on a static spinlock, writes each northbridge's cached flush word with bit 0 set, and polls until hardware clears the bit on every node. L3 partitioning reads/writes PCI config registers on the node's link/misc functions and preserves reset/BAN state across changes.

## State and Persistence Behavior
`amd_northbridges` owns a heap-allocated array of `struct amd_northbridge` entries and feature flags for the boot. `flush_words` stores per-node GART flush control values. `amd_set_subcaches()` uses static `reset` and `ban` variables to remember original L3 partitioning/BAN state.

## Dependencies and Integration Points
The file integrates AMD node PCI helpers from `amd_node.c`, CPUID feature/family data, PCI config access, GART IOMMU flushing in `amd_gart_64.c`, aperture detection in `aperture_64.c`, L3 cache partitioning users, and MMCONFIG setup logic.

## Risks
- Discovery assumes each node has a misc function; missing devices clear the cache and disable dependent features.
- `amd_flush_garts()` busy-waits on hardware clear bits and can hang if a northbridge stops responding.
- L3 partitioning writes low-level PCI config registers and can alter cache behavior system-wide.
- Early northbridge detection intentionally excludes Zen because newer systems use data-fabric paths.

## Test Signals
- Boot AMD/Hygon non-Zen systems and verify northbridge count/features.
- Exercise GART DMA mappings and confirm `amd_flush_garts()` completes under load.
- Test L3 subcache get/set on family 0x15 partitioning-capable machines.
- Validate MMCONFIG range discovery on Fam10h+ systems.
