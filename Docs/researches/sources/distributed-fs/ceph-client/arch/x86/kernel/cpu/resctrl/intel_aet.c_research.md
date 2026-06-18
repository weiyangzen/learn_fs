# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/intel_aet.c

## Purpose

This file adds Intel Application Energy Telemetry support as a package-scoped resctrl monitoring resource. It discovers PMT telemetry aggregators, validates their GUIDs and MMIO layouts, exposes selected per-RMID energy/activity/performance events through resctrl, and reads package-domain counters from MMIO.

## Important APIs, Types, And Functions

Key structures are `struct pmt_event` and `struct event_group`. Static event groups describe known XML GUIDs for energy and performance telemetry, including event IDs, counter indices, fixed-point fractional bits, expected RMID counts, and MMIO size. Public hooks are `intel_handle_aet_option()`, `intel_aet_get_events()`, `intel_aet_exit()`, `intel_aet_read_event()`, and `intel_aet_mon_domain_setup()`.

## Control Flow

Boot option parsing can force event groups on or off by PMT feature name and optional GUID. `intel_aet_get_events()` asks the Intel PMT driver for feature regions, validates package IDs and MMIO sizes, rejects groups with insufficient RMIDs unless forced on, enables resctrl monitor events, and adjusts the resource RMID count to the minimum supported. `intel_aet_read_event()` derives the containing event group from `arch_priv`, computes the per-RMID MMIO slot, sums valid data across matching package aggregators, and returns `-EINVAL` when no valid data exists.

## State, Dependencies, And Integration

Each enabled `event_group` retains a `pmt_feature_group` reference until `intel_aet_exit()`. Resctrl package monitor domains are allocated in `intel_aet_mon_domain_setup()`. Dependencies include the Intel PMT telemetry driver, topology package count, MMIO `readq()`, and generic resctrl monitor event registration.

## Risks And Test Signals

Risks include stale XML-derived sizes, bad package IDs from firmware, mismatched RMID counts, invalid MMIO index arithmetic, and duplicate event IDs already enabled by another source. Test on AET-capable Intel hardware by using `rdt=energy`, `rdt=!energy`, and GUID-qualified options, mounting resctrl, checking package monitor domains/events, reading counters for several RMIDs, and unloading/exiting to verify PMT references are released.
