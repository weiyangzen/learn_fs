# sources/distributed-fs/ceph-client/arch/x86/events/intel/uncore_discovery.h

## Purpose

`uncore_discovery.h` defines constants, packed discovery-table record layouts, generic PMON bit masks, access-type identifiers, discovered-unit/type records, and function prototypes for Intel uncore PerfMon discovery and generic uncore backends.

## Important APIs, Types, And Fields

Important constants identify discovery sources (`UNCORE_DISCOVERY_MSR`, `CBB_UNCORE_DISCOVERY_MSR`, `PACKAGE_UNCORE_DISCOVERY_MSR`), PCI discovery table devices, DVSEC offsets/IDs, global map size, and fields for PCI-domain/bus/devfn/box-control extraction. `uncore_discovery_invalid_unit()` centralizes validation of empty or all-ones discovery records.

`enum uncore_access_type` distinguishes MSR, MMIO, and PCI units. `struct uncore_global_discovery` describes table type, stride, unit count, access type, global control address, and status layout. `struct uncore_unit_discovery` describes unit counter count, control/counter offsets, bit width, access type, control address, box type, and box ID. `intel_uncore_discovery_unit` and `intel_uncore_discovery_type` are the in-memory normalized records used by `uncore_discovery.c`.

The prototypes expose discovery execution, cleanup, generic CPU/PCI/MMIO init, generic backend operations, discovered-unit lookup, and `uncore_get_uncores()` platform override merging.

## Control Flow

This header has no executable control flow except macros. It provides the contract used by `uncore.c` to request discovery and by `uncore_discovery.c` to populate generic PMU structures.

## State And Persistence Behavior

The structs describe transient discovery and runtime mapping state. Discovery records are read from hardware tables, normalized into RB-tree nodes, and freed on module exit. No durable state is managed here.

## Dependencies And Integration Points

It depends on `struct uncore_plat_init`, `struct intel_uncore_type`, `struct intel_uncore_box`, and perf event types declared through `uncore.h` and perf headers. Platform init tables in `uncore.c` use its constants to configure discovery domains.

## Risks And Edge Cases

Bitfield definitions must match hardware discovery-table encoding. PCI address extraction uses fixed bit positions and must stay aligned with discovered unit address formats. Generic raw event masks only cover common event/umask/edge/invert/thresh fields, so platform-specific units may still need overrides.

## Test Signals

Build coverage for discovery users, boot discovery on PCI and MSR table platforms, sysfs PMU naming for units without names, and perf reads through all three generic access types validate this contract.
