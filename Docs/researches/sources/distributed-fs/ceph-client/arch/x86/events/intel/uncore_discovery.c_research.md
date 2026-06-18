# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.c

## Purpose

`uncore_discovery.c` implements Intel uncore PerfMon discovery. It parses discovery tables exposed through PCI DVSEC BARs or MSRs, records discovered uncore unit types and boxes in red-black trees, and synthesizes generic `intel_uncore_type` arrays for MSR, PCI, and MMIO access backends.

## Important APIs, Types, And Functions

The main exported functions are `uncore_discovery()`, `intel_uncore_clear_discovery_tables()`, generic backend box/event operations (`intel_generic_uncore_*`), `intel_generic_uncore_assign_hw_event()`, `intel_uncore_generic_init_uncores()`, `intel_uncore_generic_uncore_cpu_init()`, `intel_uncore_generic_uncore_pci_init()`, `intel_uncore_generic_uncore_mmio_init()`, `intel_uncore_find_discovery_unit_id()`, `uncore_find_add_unit()`, and `uncore_get_uncores()`.

Internal state includes `discovery_tables`, keyed by box type, and `num_discovered_types[]` by access type. Each discovered type owns a unit tree keyed by PMU index and die. Parsing helpers include `__parse_discovery_table()`, `parse_discovery_table()`, `uncore_discovery_pci()`, `uncore_discovery_msr()`, `uncore_insert_box_info()`, and ignore-list filtering.

## Control Flow

`uncore_discovery()` iterates configured discovery domains from `struct uncore_plat_init`. MSR domains read one discovery-table base per logical die from online CPUs. PCI domains find Intel discovery-table devices, scan DVSEC capabilities for PMON discovery entries, derive the table BAR, compute die ID, and parse the mapped table.

Parsing first reads the global discovery record, validates it, maps the full table based on stride and max-unit count, optionally runs a platform global-init callback, then iterates unit records. Valid, non-ignored units become `intel_uncore_discovery_unit` nodes attached to a type record. Later, generic init converts discovered records into `intel_uncore_type` objects with common format groups, event masks, counter width/offsets, unit trees, and backend-specific ops.

## State And Persistence Behavior

Discovery data is held in kernel memory until module exit or init failure, when `intel_uncore_clear_discovery_tables()` frees all type and unit nodes. It does not persist across boots. Generic PMUs reference discovery unit trees through `intel_uncore_type.boxes`; live boxes use those records to compute control addresses and MMIO mappings.

## Dependencies And Integration Points

The file integrates with `uncore.c` platform init, PCI config/DVSEC access, MSR reads on specific CPUs, `ioremap()` discovery-table reads, red-black tree helpers, and generic uncore perf callbacks. It is used both as a fallback for unknown CPUs with discovery support and as a supplement for newer known platforms.

## Risks And Edge Cases

Invalid discovery records are common enough to be explicitly filtered: missing table/control fields, all-ones sentinel values, unsupported access types, ignored platform unit IDs, absent DVSEC entries, disabled/invalid BARs, and unavailable NUMA die info. Generic MMIO mapping uses a default map size unless platform code overrides a type through `uncore_get_uncores()`. Discovery state is global, so cleanup must release nested unit trees reliably.

## Test Signals

Useful checks include booting discovery-capable platforms with and without `uncore_no_discover`, verifying generic PMU names and aliases, validating discovered box counts and counter widths against hardware documentation, PCI DVSEC parsing tests, MSR-domain parsing on multi-die systems, and exercising generic MSR/PCI/MMIO event reads through perf.
