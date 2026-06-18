# sources/distributed-fs/ceph-client/include/linux/tsm.h

## Purpose
Defines the core TSM report-generation and device-registration interface for confidential-computing attestation providers.

## Important APIs, Types, And Functions
Key types are `struct tsm_report_desc`, `struct tsm_report`, `enum tsm_attr_index`, `enum tsm_bin_attr_index`, `struct tsm_report_ops`, and `struct tsm_dev`. APIs include `tsm_report_register()`, `tsm_report_unregister()`, `tsm_register()`, `tsm_unregister()`, and `find_tsm_dev()`. `DEFINE_FREE(put_tsm_dev, ...)` provides cleanup-attribute support for device references.

## Control Flow
A provider registers `tsm_report_ops` with a name, privilege floor, visibility callbacks, and `report_new()` implementation. Consumers configure report descriptors with input blob, privilege level, and optional service-provider fields; `report_new()` fills output, auxiliary, and manifest blobs.

## State, Persistence, And Dependencies
TSM report state includes copied input descriptor and dynamically allocated output blobs up to `TSM_REPORT_OUTBLOB_MAX`. Device state embeds `struct device`, id, and optional PCI TSM ops. Dependencies include sizes, UUID/GUID, devices, and base types.

## Integration Points
Integrates configfs/sysfs TSM report instances, CC guest attestation drivers, PCI TSM providers, and service-provider-specific attestation metadata.

## Risks And Test Signals
Risks include oversized output blobs, privilege-level validation gaps, provider singleton conflicts, blob lifetime leaks, and visibility callbacks hiding required ABI files. Test signals include report generation with boundary input sizes, provider register/unregister, privilege floor enforcement, service GUID parsing, and cleanup of output/aux/manifest buffers.
