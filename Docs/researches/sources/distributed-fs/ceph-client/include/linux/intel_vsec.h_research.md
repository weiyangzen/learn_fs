<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_vsec.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_vsec.h

Purpose: Defines Intel VSEC/DVSEC discovery, auxiliary-device, PMT telemetry, and OOBMSM platform interfaces.

Important APIs/types/functions: Capability bits cover telemetry, watcher, crashlog, SDSI, TPMI, and discovery. DVSEC macros extract table BAR/offset. Enums identify discovery source and VSEC ids. `struct intel_vsec_header`, quirks, `pmt_callbacks`, feature dependencies, `intel_vsec_platform_info`, `intel_vsec_device`, `oobmsm_plat_info`, `telemetry_region`, and `pmt_feature_group` model discovery metadata, resources, aux devices, dependencies, callbacks, and grouped telemetry regions. APIs add aux devices, register VSEC platform info, set/get mappings, and acquire/release PMT feature groups with Kconfig stubs.

Control flow: Parent PCI/ACPI drivers discover VSEC headers, register platform info, create auxiliary devices, then PMT clients query telemetry regions by feature.

State/persistence: Aux devices, resources, ida ids, mappings, telemetry regions, and kref-counted feature groups persist while registered.

Dependencies/integration: Depends on auxiliary bus, PCI resources, PMT feature tables, krefs, debugfs, and Kconfig.

Risks: Discovery quirks and source-specific tables must be interpreted correctly; feature group references require balanced put.

Test signals: PCI and ACPI discovery, aux device creation/removal, quirk paths, mapping lookup, PMT telemetry get/put, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_vsec.h -->
