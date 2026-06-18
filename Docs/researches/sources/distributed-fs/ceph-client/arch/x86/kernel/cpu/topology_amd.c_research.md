# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology_amd.c

## Purpose

This file implements AMD and Hygon-specific topology parsing and fixups. It extracts SMT/core/package/node information from extended CPUID leaves and legacy MSRs, works around disabled topology extensions, sets LLC IDs, and adjusts core IDs on multi-node legacy systems.

## Important APIs, Types, And Functions

Primary public functions are `cpu_parse_topology_amd()` and `cpu_topology_fixup_amd()`. Helpers include `parse_8000_0008()`, `store_node()`, `parse_8000_001e()`, `parse_fam10h_node_id()`, `legacy_set_llc()`, `topoext_fixup()`, and `parse_topology_amd()`.

## Control Flow

Parsing first initializes AMD nodes-per-package to one, attempts to re-enable disabled Topology Extensions for affected Family 15h systems, then prefers modern extended topology leaves through `cpu_parse_topology_ext()`. If unavailable, it parses CPUID `0x80000008` for core-domain width and `0x8000001e` for extended APIC ID, SMT thread count, node ID, and nodes per socket. Legacy systems fall back to `MSR_FAM10H_NODE_ID`. Hygon receives a package-shift workaround for certain non-hypervisor models. Final fixup sets AMD DCM capability for multi-node packages and adjusts legacy core IDs relative to node.

## State, Dependencies, And Integration

State is written into `topo_scan`, `cpuinfo_x86::topo`, and CPU capability bits. Dependencies include CPUID/MSR helpers, cacheinfo AMD/Hygon LLC ID setup, x86 vendor/family/model data, and generic topology parser helpers. It integrates with CPU initialization and later topology registration.

## Risks And Test Signals

AMD topology leaves vary by family, and BIOS-disabled Topology Extensions or Hygon quirks can produce wrong package/core IDs if mishandled. Node ID is not always representable in APIC bits. Test on Family 10h/15h/17h+ AMD systems, Hygon systems, hypervisor guests, systems with multiple nodes per package, and CPUs with leaf `0x80000026`.
