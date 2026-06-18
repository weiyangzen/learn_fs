# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/topology.h

## Purpose

This header defines the internal x86 topology scan state and helper functions used by generic and vendor-specific topology parsers.

## Important APIs, Types, And Functions

`struct topo_scan` holds the current `cpuinfo_x86`, per-domain shifts and CPU counts, legacy CPUID[1] logical-processor shift, and AMD node metadata. Prototypes cover topology initialization/parsing, domain updates, extended topology parsing, AMD parsing, and AMD fixups. Inline helpers are `topo_shift_apicid()`, `topo_relative_domain_id()`, `topo_domain_mask()`, and `topology_update_dom()`. `topology_unit_count()` is declared when local APIC support is enabled and stubbed otherwise.

## Control Flow

The inline helpers shift or mask APIC IDs according to `x86_topo_system.dom_shifts` and `dom_size`. `topology_update_dom()` updates one scan domain without propagating changes to higher domains, which is useful for vendor fixups.

## State, Dependencies, And Integration

The header does not own global state but depends on `x86_topo_system` and topology domain enums from broader x86 CPU headers. It integrates `topology.c`, AMD topology parsing, and generic extended topology parsing.

## Risks And Test Signals

Domain shifts and masks must remain consistent with parser-populated topology. Incorrect relative IDs affect package/core/thread IDs and downstream sched/perf users. Test by comparing parsed topology on Intel, AMD, Hygon, no-APIC, and sparse-domain systems.
