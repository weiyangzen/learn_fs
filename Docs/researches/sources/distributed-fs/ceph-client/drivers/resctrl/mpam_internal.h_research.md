# sources/distributed-fs/ceph-client/drivers/resctrl/mpam_internal.h

## Purpose

This header defines the shared internal contract for the Arm MPAM driver and its resctrl bridge. It contains core topology types, feature and quirk enumerations, monitor/config state, exported globals and helper prototypes, MMIO register offsets, bit definitions, and small allocation helpers for monitor IDs.

## Important APIs, Types, And Functions

Core topology types are `struct mpam_msc`, `struct mpam_msc_ris`, `struct mpam_vmsc`, `struct mpam_component`, and `struct mpam_class`. `struct mpam_config` stores per-PARTID control values and feature-valid bits. `struct mon_cfg` and `struct msmon_mbwu_state` model monitoring filters and preserved MBWU counter state. `struct mpam_resctrl_dom`, `struct mpam_resctrl_res`, and `struct mpam_resctrl_mon` are the private bridge objects used by `mpam_resctrl.c`.

`enum mpam_device_features` enumerates cache portion/capacity/associativity, memory bandwidth, priority, monitor, and PARTID narrowing capabilities. `enum mpam_device_quirks` captures T241 and CMN workarounds. `mpam_has_feature()`, `mpam_set_feature()`, and `mpam_clear_feature()` manipulate packed-safe feature bitmaps. `mpam_is_enabled()` reads the `mpam_enabled` static key.

The header declares `mpam_srcu`, `mpam_classes`, `mpam_partid_max`, `mpam_pmg_max`, device-layer APIs, monitor APIs, resctrl APIs, and fallback no-op resctrl stubs when `CONFIG_RESCTRL_FS` is off.

## Control Flow

There is no standalone runtime flow, but the header defines the state transitions used by the implementation: MSC discovery builds the topology structs, feature probing fills `mpam_props`, enable allocates per-component config arrays and monitor state, resctrl maps classes and components into domains, and disable/free paths use `mpam_garbage` for SRCU-safe teardown.

## State And Persistence

Most persistent MPAM driver state is shaped here. `struct mpam_msc` stores hardware identity, interface type, accessibility mask, probe status, register mapping, interrupts, locks, RIS list, error flags, and quirk state. `struct mpam_component` stores per-PARTID config arrays read by CPU hotplug callbacks. `struct mpam_msc_ris` stores RIS ID, feature props, reset state, affinity, and MBWU state.

State protected by SRCU may not be freed immediately, so `struct mpam_garbage` allows deferred `kfree()` or `devm_kfree()` after `synchronize_srcu()`. Monitor selector locking is currently valid only for MMIO MSCs and intentionally returns false for firmware-backed interfaces.

## Dependencies And Integration Points

The header integrates Linux resctrl, Arm MPAM architecture helpers, SRCU, bitmap APIs, cpumasks, IO accessors, jump labels, and generated ACPI MPAM types. Register definitions follow the Arm MPAM System Component specification and are consumed directly by `mpam_devices.c`.

## Risks And Edge Cases

The source snapshot contains duplicate enum and macro definitions, including duplicate `COUNT_BOTH` and duplicate `MPAMF_CPOR_IDR_CPBM_WD`, which are compile-integrity risks. `mpam_mon_sel_lock()` currently warns and fails for non-MMIO interfaces, so PCC support declared in device state is not practically implemented. Several structs rely on lock comments for correctness rather than type-level enforcement. `PACKED_FOR_KUNIT` changes `struct mpam_props` layout under tests to catch sanitization gaps, so tests intentionally alter packing assumptions.

## Test Signals

Compile coverage is the first signal because this header defines many shared symbols and macros. Runtime signals come from MPAM device probing, resctrl bridge compilation, and KUnit tests that exercise packed `mpam_props`, feature bit operations, and register constants used by bitmap reset tests.
