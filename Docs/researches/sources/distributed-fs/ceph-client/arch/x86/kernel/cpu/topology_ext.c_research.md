# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_ext.c

## Purpose
Parses modern CPUID topology leaves and maps hardware level types into Linux x86 topology domains.

## Important APIs, Types, And Functions
`enum topo_types` mirrors CPUID topology type encodings. `topo_domain_map_0b_1f` maps Intel leaves `0xb`/`0x1f`; `topo_domain_map_80000026` maps AMD leaf `0x80000026`. `topo_subleaf()` decodes one subleaf and updates a `topo_scan`. `parse_topology_leaf()` walks subleafs. `cpu_parse_topology_ext()` chooses the best supported leaf.

## Control Flow
Intel tries leaf `0x1f`, AMD tries `0x80000026`, and both can fall back to `0x0b`. Each subleaf must have a processor count and nonzero type. Known types map to SMT/core/module/tile/die/die-group domains; unknown future types are placed after the previous domain with an error. The parser records x2APIC ID consistency and fixes broken SMT subleaf shift zero cases.

## State, Persistence, And Dependencies
It only mutates the caller-provided `topo_scan` and `cpuinfo_x86.topo.initial_apicid`, then sets `X86_FEATURE_XTOPOLOGY`. It depends on CPUID subleaf layout and common topology helpers.

## Integration Points
Called from Intel and AMD topology discovery in `topology_common.c`; its domain shifts are later copied into `x86_topo_system` or validated per CPU.

## Risks
Future or vendor-specific topology types may be guessed incorrectly. Broken firmware can advertise inconsistent APIC IDs or impossible SMT shifts. Domain map changes can affect scheduler grouping and package/core IDs.

## Test Signals
Boot on Intel leaf `0x1f`, Intel leaf `0x0b`, and AMD `0x80000026` systems should set `XTOPOLOGY` and produce stable topology domains without warnings except on known broken firmware.
