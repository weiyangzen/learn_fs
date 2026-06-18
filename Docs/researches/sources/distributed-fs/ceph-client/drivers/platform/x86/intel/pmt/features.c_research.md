# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/features.c

## Purpose

This file is the static PMT discovery metadata catalog. It maps `enum pmt_feature_id` values to sysfs-visible feature names, declares each feature's attribute layout, and defines capability-bit name tables used by `discovery.c` when rendering the `caps` sysfs file.

## Important APIs, Types, And Functions

The exported arrays are `pmt_feature_names[]`, `feature_layout[]`, and the feature-specific `struct pmt_cap` arrays such as `pmt_cap_common`, `pmt_cap_pcpt`, `pmt_cap_pcet`, `pmt_cap_crashlog`, `pmt_cap_tpmi`, `pmt_cap_tracing`, and `pmt_cap_rmid_energy`. Each exported `pmt_caps_*[]` pointer array combines common capability names with feature-specific capability names and terminates with `NULL`.

## Control Flow

There is no runtime control flow beyond static data access. Discovery sysfs code selects the appropriate `pmt_caps_*[]` array based on feature ID and walks nested capability arrays until a zero-name terminator, printing whether each mask bit is present in the hardware-reported capability word.

## State And Persistence

All state is static process memory and effectively immutable after module load. There is no hardware access and no persistence.

## Dependencies And Integration Points

The file depends on `linux/intel_pmt_features.h` for feature IDs, layout enums, and capability masks. `pmt_feature_names` is exported in `INTEL_PMT_DISCOVERY`; the capability arrays are included by PMT discovery code through the public feature header.

## Risks

The arrays rely on enum-index alignment. Adding a new `enum pmt_feature_id` without updating names, layouts, and capability tables will produce missing sysfs naming or incorrect attribute selection. Capability names are user-visible ABI-ish debug information, so spelling or mask mistakes mislead tools.

## Test Signals

Build coverage catches missing enum or mask definitions. Runtime signals include `caps` output containing common and feature-specific names, valid sysfs directory names for all discovered IDs, and no out-of-bounds access when discovery exposes every supported PMT feature.
