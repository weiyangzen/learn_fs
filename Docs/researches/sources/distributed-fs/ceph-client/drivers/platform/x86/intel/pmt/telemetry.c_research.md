# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/telemetry.c

## Purpose

This file implements the Intel PMT telemetry auxiliary driver. It creates PMT telemetry endpoints from Intel VSEC telemetry resources, exposes endpoint handles through an xarray, provides exported endpoint registration/read APIs for in-kernel clients, and provides a feature-query API returning telemetry regions grouped by PMT feature ID.

## Important APIs, Types, And Functions

Important types include `struct pmt_telem_priv`, `struct telem_endpoint`, `struct intel_pmt_entry`, and `struct pmt_feature_group`. The PMT namespace callbacks are `pmt_telem_header_decode()` and `pmt_telem_add_endpoint()`. Public APIs are `pmt_telem_get_next_endpoint()`, `pmt_telem_register_endpoint()`, `pmt_telem_unregister_endpoint()`, `pmt_telem_get_endpoint_info()`, `pmt_telem_find_and_register_endpoint()`, `pmt_telem_read()`, `pmt_telem_read32()`, `intel_pmt_get_regions_by_feature()`, and `intel_pmt_put_feature_group()`.

## Control Flow

Probe binds to `intel_vsec.telemetry`, allocates storage for all possible resources, and calls `intel_pmt_dev_create()` under `ep_lock` for each resource. The PMT class helper decodes discovery headers, maps telemetry MMIO, and stores entries in `telem_array`. After a successful entry is created, `intel_pmt_get_features()` annotates it using the discovery driver's feature list. Clients enumerate endpoint IDs with `pmt_telem_get_next_endpoint()`, get a kref with `pmt_telem_register_endpoint()`, read qwords or dwords by sample ID, and release with `pmt_telem_unregister_endpoint()`. Removal marks endpoints absent through `intel_pmt_dev_destroy()` and drops endpoint krefs.

## State And Persistence

`telem_array` is the global endpoint index protected by `ep_lock`. Each endpoint has a kref, `present` flag, MMIO base, header, device pointer, and optional VSEC read callback. Feature-region queries allocate a kref-counted `pmt_feature_group` snapshot. State is volatile and tied to auxiliary device lifetime; no persistent state is stored.

## Dependencies And Integration Points

The file integrates with Intel VSEC, PMT class helper code, PMT discovery, xarray, kref, auxiliary bus, and the `INTEL_PMT_TELEMETRY` exported namespace. `pmt_copy_region()` uses `intel_vsec_get_mapping()` and PCI parent platform data to build OOB telemetry region descriptors.

## Risks

Endpoint reads rely on callers honoring alignment and count semantics. `pmt_telem_read()` checks `present` before and after MMIO access, returning `-EPIPE` if removal raced with the read, but copied data must then be considered invalid. The xarray stores `intel_pmt_entry` pointers while endpoint krefs manage only `entry->ep`, so class helper teardown must remove xarray entries before freeing entry storage. Early-client overlap detection skips fixed telemetry blocks for some hardware, so device-specific GUID/type handling is sensitive.

## Test Signals

Useful tests include endpoint enumeration, endpoint info retrieval, qword and dword bounds checks, removal races returning `-ENODEV` or `-EPIPE`, feature-group queries for valid and invalid IDs, successful import/export namespace linkage, and telemetry reads through both direct MMIO and any VSEC callback path.
