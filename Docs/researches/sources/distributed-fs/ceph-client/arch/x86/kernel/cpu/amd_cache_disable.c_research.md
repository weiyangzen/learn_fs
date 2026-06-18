# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/amd_cache_disable.c

## Purpose
This file exposes AMD L3 cache index disable and subcache partitioning controls through private cache sysfs attributes.

## Important APIs, Types, and Functions
`amd_init_l3_cache()` attaches an AMD northbridge object to L3 cacheinfo and computes L3 indices via `amd_calc_l3_indices()`. `cache_get_priv_group()` returns the private attribute group for eligible L3 caches. Attribute handlers include `cache_disable_0/1_show`, `cache_disable_0/1_store`, `subcaches_show()`, and `subcaches_store()`. Hardware programming is done through `amd_get_l3_disable_slot()`, `amd_set_l3_disable_slot()`, and `amd_l3_disable_index()`.

## Control Flow
For L3 cacheinfo entries, initialization finds the northbridge for the current AMD node and lazily calculates subcache geometry from PCI config. Sysfs visibility depends on `ci->priv` and AMD northbridge feature bits. Writes require `CAP_SYS_ADMIN`, parse an index or mask, select a CPU from the shared cache map, validate slot/index state, program PCI config registers, run `wbinvd_on_cpu()` on a CPU in the owning node, and activate the disable slot.

## State and Persistence
Persistent state lives mostly in hardware PCI config registers and the northbridge `l3_cache` descriptor. The attribute array is allocated once and stored in the static `cache_private_group`.

## Dependencies and Integration Points
The file depends on cacheinfo sysfs, AMD northbridge discovery/features, PCI config access, topology node mapping, shared CPU maps, capability checks, and cache flush helpers.

## Risks and Test Signals
Risks include disabling an invalid cache index, programming the wrong node, missing flush ordering, exposing controls on unsupported hardware, and concurrent sysfs writes racing through hardware slots. Test signals include presence/absence of sysfs attributes by feature bit, correct `FREE` or index reads, rejection of duplicate/out-of-range writes, visible subcache masks, and hardware-specific cache disable validation.
