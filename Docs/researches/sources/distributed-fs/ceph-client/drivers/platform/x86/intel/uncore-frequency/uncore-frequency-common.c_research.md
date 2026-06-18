# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.c

## Purpose

This file implements the shared sysfs layer for Intel uncore frequency control. Hardware-specific backends provide read/write callbacks and per-instance `struct uncore_data`; the common layer creates and removes sysfs groups under the CPU subsystem.

## Important APIs, Types, And Functions

Exports are `uncore_freq_common_init()`, `uncore_freq_common_exit()`, `uncore_freq_add_entry()`, and `uncore_freq_remove_die_entry()`. Internal helpers generate show/store callbacks for min/max/current frequency, initial values, ELC thresholds, domain/cluster/package IDs, agent types, and die ID. `create_attr_group()` dynamically includes optional attributes only when backend reads succeed or metadata is meaningful.

## Control Flow

A backend calls `uncore_freq_common_init()` with hardware read/write callbacks; the common layer creates `/sys/devices/system/cpu/intel_uncore_frequency` once and increments an instance count. For each die/domain, the backend calls `uncore_freq_add_entry()`, which names the instance, samples initial min/max frequencies, creates attributes, and marks the entry valid. Writes parse integers or booleans, serialize under `uncore_lock`, and call the backend write callback. Removal deletes the group, clears validity, and frees any allocated IDA instance. Exit drops the root kobject when the last backend exits.

## State And Persistence

Global state includes `uncore_lock`, root kobject, instance count, IDA allocator, and callback pointers. Per-instance state lives in backend-owned `struct uncore_data`, including cached initial frequency values and validity/control CPU. User writes modify hardware state; common code stores no resume policy beyond the `stored_uncore_data` field available to backends.

## Dependencies And Integration Points

The file integrates with the CPU subsystem root device, sysfs/kobject APIs, IDA, topology helpers, and hardware-specific uncore backends. It exports namespace `INTEL_UNCORE_FREQUENCY`.

## Risks

Only one global read/write callback pair exists, so simultaneous different backend types would conflict. `uncore_freq_remove_die_entry()` assumes the entry is valid and group exists. `kstrtobool(buf, (bool *)&input)` writes through a bool pointer into an unsigned int object, which is unusual and depends on layout. Attribute array capacity must stay in sync with optional attributes.

## Test Signals

Signals include root kobject creation/removal, sysfs group creation for package/die and domain modes, optional current/ELC attributes appearing only when reads succeed, min/max writes reaching backend callbacks, boolean ELC parsing, IDA naming, and concurrent access serialization.
