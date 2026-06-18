# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.c

Purpose: implements the common PMT class layer. It creates `/sys/class/intel_pmt` devices, maps PMT data buffers, exposes common attributes/bin files, and provides shared helper functions for telemetry, discovery, and crashlog drivers.

Important APIs/types/functions: `intel_pmt_is_early_client_hw()` checks VSEC early hardware quirks. `pmt_telem_read_mmio()` reads telemetry either through platform callbacks or direct MMIO, with special aligned 64-bit handling for SPR PUNIT GUID. `intel_pmt_read()` and `intel_pmt_mmap()` back binary sysfs access. `intel_pmt_populate_entry()` resolves PMT base addresses for `ACCESS_LOCAL` and `ACCESS_BARID`. `intel_pmt_dev_register()`, `intel_pmt_dev_create()`, and `intel_pmt_dev_destroy()` manage class devices, xarray IDs, sysfs groups, ioremap, bin attributes, and optional endpoint registration. `intel_pmt_class` is exported.

Control flow: feature drivers provide an `intel_pmt_namespace` with a header decoder and optional endpoint callback, then call `intel_pmt_dev_create()` for each VSEC resource. The class maps the discovery table, decodes the feature header, computes the data base address, creates the class device and sysfs files, maps the data resource if non-empty, and registers feature-specific endpoints. Destroy removes bin files/groups, unregisters the device, and erases the xarray entry.

State and persistence: xarray IDs are namespace-owned and allocated from 1 to INT_MAX. Each `intel_pmt_entry` stores mapped discovery/data addresses, kobject, header, device ID, GUID, feature flags, callback pointer, and optional telemetry endpoint. The class itself is registered at module init and unregistered at exit.

Dependencies and integration points: depends on Intel VSEC auxiliary devices, PCI BAR resources, sysfs, xarray, MMIO helpers, and `class.h`. Telemetry and crashlog drivers reuse this layer. `intel_pmt_attr_visible()` suppresses common attributes for discovery-capability devices.

Risks: address calculation differs for early client hardware, so wrong quirks can map the wrong BAR/offset. `mmap` forbids writable mappings and bounds by page-rounded physical size, but incorrect `entry->size` from header decoding can still expose wrong ranges. `pmt_memcpy64_fromio()` requires 8-byte alignment for SPR PUNIT reads. Error paths must remove partially created sysfs and xarray entries in the correct order.

Test signals: sysfs should show `guid`, `size`, `offset`, and a read-only bin attribute for non-discovery PMT entries. `mmap` with write flags should fail `-EROFS`; oversized mmap should fail `-EINVAL`. VSEC telemetry/crashlog probes exercise create/destroy unwinds.
