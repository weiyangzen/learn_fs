<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec.c

Purpose: Intel PCIe Vendor Specific Extended Capability driver. It discovers Intel VSEC/DVSEC discovery tables on selected PCI devices, turns them into auxiliary devices for PMT telemetry/watcher/crashlog, SDSI, TPMI, and discovery features, and exports helper APIs for other code to register VSEC-backed auxiliary devices.

Important APIs/types/functions: `struct vsec_priv` tracks platform info, supplier devices, OOBMSM mapping, feature states, and found capability bitmap. `intel_vsec_add_aux()` creates an `intel_vsec_device` on the auxiliary bus. `intel_vsec_register()` registers static headers supplied by another device. `intel_vsec_register_device()`, `intel_vsec_walk_dvsec()`, and `intel_vsec_walk_vsec()` implement discovery. `intel_vsec_set_mapping()` and `intel_vsec_get_mapping()` store CPU-package-to-PCI mapping used by TPMI consumers. PCI error handlers tear down and rediscover auxiliary devices after reset.

Control flow: PCI probe enables the device, installs `vsec_priv`, then repeatedly scans DVSEC/VSEC/static headers until all expected capabilities are found or dependency skips are resolved. Each supported header is converted to resource ranges based on BAR base, table offset, entry count, and entry size, with memory-region availability checked before creating the auxiliary device. Dependency metadata delays consumers until supplier capabilities have been registered and device links can be created.

State/persistence: IDA allocators provide auxiliary IDs, `auxdev_array` tracks live devices for release and PCI error recovery, and `vsec_priv->state` records not found, registered, or skipped per feature. No persistent user state exists; hardware capability discovery is repeated on probe/reset.

Dependencies/integration: integrates PCI extended config access, auxiliary bus, xarray/IDA, device links, Intel VSEC public headers, and Kconfig presence checks for downstream feature drivers. Feature names such as `telemetry`, `sdsi`, `tpmi`, and `discovery` are consumed by auxiliary drivers.

Risks: feature dependency ordering is subtle; skipped suppliers can intentionally unblock consumers but missing configured drivers suppress auxiliary creation. Resource calculation depends on table offset quirks, entry size, and BAR selection. PCI error recovery removes all aux devices for the parent and reprobes, so consumers must tolerate teardown/recreation.

Test signals: supported PCI IDs should produce expected auxiliary devices only when corresponding downstream configs are enabled; dependency cases such as OOBMSM should create supplier links before telemetry consumers; invalid headers with zero entries/sizes or unsupported revisions should be skipped; AER slot reset should remove and recreate matching aux devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/vsec.c -->
