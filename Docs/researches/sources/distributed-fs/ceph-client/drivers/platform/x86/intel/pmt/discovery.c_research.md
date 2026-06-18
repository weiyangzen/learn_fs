# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery.c

## Purpose

This file implements the Intel Platform Monitoring Technology feature-discovery auxiliary driver. It consumes `intel_vsec.discovery` resources, decodes PMT feature discovery tables, creates one sysfs kobject per supported feature under the PMT class device, and exports discovered feature metadata so PMT telemetry entries can be tagged with feature flags.

## Important APIs, Types, And Functions

Core internal types are `struct feature_discovery_table`, `struct feature_header`, `struct feature_table`, `struct feature`, and `struct pmt_features_priv`. `pmt_feature_get_disc_table()` maps each discovery resource, rejects duplicate IDs, skips reserved/zero-size/too-new/invalid features, and records the ID in `priv->mask`. `pmt_feature_get_feature_table()` maps the actual feature table for `ACCESS_LOCAL`, validates table size against the resource, copies attributes and GUIDs, and fills `feature->table`. `pmt_features_discovery()` chooses the sysfs attribute layout from `feature_layout[]`, initializes the feature kobject, emits the add uevent, and links it into the global list. `intel_pmt_get_features()` is the exported PMT namespace function used by telemetry entries to match entry GUIDs against discovered feature GUID lists.

## Control Flow

The auxiliary driver binds to `intel_vsec.discovery`. Probe creates a PMT class child named `features-<parent>`, iterates all VSEC resources, decodes each discovery table, skips benign unsupported entries, initializes kobjects for valid entries, and increments `priv->count` only after full setup. Sysfs reads dispatch through layout-specific kobject types: RMID features expose caps, `num_rmids`, watcher period, command sizes, and GUIDs; watcher and command layouts expose only applicable command/watcher fields; caps-only layouts expose caps and GUIDs. Removal walks fully initialized entries, removes list membership and sysfs groups, drops kobject refs, and unregisters the child device.

## State And Persistence

Runtime state is the `pmt_features_priv` allocation, per-feature kobjects, devm-allocated GUID arrays, and global `pmt_feature_list` protected by `feature_list_lock`. The driver stores no persistent on-disk state. Hardware table contents are read-only MMIO snapshots; discovered feature associations last only until the auxiliary device is removed.

## Dependencies And Integration Points

The file depends on the auxiliary bus, Intel VSEC resource enumeration, PMT class support from `class.h`, PMT feature definitions from `linux/intel_pmt_features.h`, sysfs/kobject APIs, and exported PMT namespace consumers. It imports `INTEL_PMT` and exports `intel_pmt_get_features()` in that namespace.

## Risks

The table decoder currently supports only `ACCESS_LOCAL`; future BAR-based feature tables would fail probe. `pmt_feature_get_disc_table()` indexes `pmt_feature_names[disc_tbl->id]` for duplicate reporting before validating the ID, so malformed duplicate IDs outside the enum would be sensitive to discovery table integrity. The empty kobject release is acceptable because feature memory is devm-owned, but lifetime expectations must remain aligned with device removal. Feature GUID matching is parent-device scoped, so incorrect parent pointers would under- or over-tag telemetry entries.

## Test Signals

Good signals are successful probe on `intel_vsec.discovery`, sysfs feature directories named from `pmt_feature_names[]`, correct per-layout attributes, duplicate-feature rejection, reserved/zero-size skip behavior, `intel_pmt_get_features()` adding flags and RMID counts to PMT telemetry entries, and clean kobject/sysfs teardown on module unload or device unbind.
