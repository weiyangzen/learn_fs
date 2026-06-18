# sources/distributed-fs/ceph-client/include/acpi/nfit.h

Purpose: Provides the small public NFIT helper API used outside the NVDIMM/ACPI NFIT driver.

Important APIs, types, and functions: Declares `nfit_get_smbios_id(u32 device_handle, u16 *flags)` when `CONFIG_ACPI_NFIT` is enabled; otherwise provides an inline `-EOPNOTSUPP` stub.

Control flow: Consumers pass an NFIT device handle and receive SMBIOS identity/flags from the ACPI NFIT implementation if available.

State and persistence: Persistent state is firmware NFIT/SMBIOS information; this header has no state.

Dependencies and integration points: Integrates with NVDIMM, persistent memory, and platform inventory/health reporting code.

Risks and test signals: Risks include callers ignoring `-EOPNOTSUPP`, stale handles after device removal, and mismatched NFIT handle decoding. Test enabled/disabled builds, known DIMM handles, absent SMBIOS mappings, and NVDIMM hotplug/removal.
