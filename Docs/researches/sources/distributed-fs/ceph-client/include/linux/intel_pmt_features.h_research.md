<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_pmt_features.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_pmt_features.h

Purpose: Defines Intel Platform Monitoring Technology feature ids, capability bits, layouts, and exported capability tables.

Important APIs/types/functions: `PMT_CAP_*` bits describe telemetry, watcher, crashlog, streaming, threshold, security, TPMI, trace, energy, and feature-specific capabilities. `enum pmt_feature_id` and `enum feature_layout` identify feature groups and data layouts. `struct pmt_cap` maps capability bit to name. Extern arrays provide names and capability sets for common, PCPT, PCET, RMID, accel, uncore, crashlog, PETE, TPMI, S3M, tracing, and energy. `pmt_feature_id_is_valid()` bounds-checks ids.

Control flow: PMT discovery and sysfs/debug code select feature layout/capability tables by id.

State/persistence: Tables are const exported data; device-specific capabilities live elsewhere.

Dependencies/integration: Depends on bit helpers and Intel VSEC/PMT telemetry drivers.

Risks: Capability bit reuse is feature-specific; interpreting a bit with the wrong table mislabels hardware.

Test signals: Feature id validation, sysfs capability names, discovery of each feature class, and table bounds tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_pmt_features.h -->
