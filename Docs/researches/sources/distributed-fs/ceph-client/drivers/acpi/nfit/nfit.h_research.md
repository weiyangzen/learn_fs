# sources/distributed-fs/ceph-client/drivers/acpi/nfit/nfit.h

`nfit.h` is the internal NFIT driver contract. It defines UUID strings, command masks, NFIT table wrapper structs, per-DIMM and per-bus state, ARS enums, block-window data, inline helpers, and cross-file declarations used by `core.c`, `intel.c`, and `mce.c`.

Important definitions include `enum nvdimm_family_cmds`, `enum nvdimm_bus_family_cmds`, `enum nfit_uuids`, `NVDIMM_STANDARD_CMDMASK`, Intel security and firmware command masks, `NVDIMM_INTEL_DENY_CMDMASK`, `struct nfit_spa`, `nfit_dcr`, `nfit_bdw`, `nfit_idt`, `nfit_flush`, `nfit_memdev`, `struct nfit_mem`, and `struct acpi_nfit_desc`. `__to_nfit_memdev()` selects the best MEMDEV association for a DIMM, and `to_acpi_desc()` recovers provider state from a bus descriptor.

There is no substantial control flow beyond inline selectors. The header defines durable runtime state layout: descriptor lists, ARS work and status, DSM masks, platform capabilities, scrub flags/counters, firmware activation caches, per-DIMM ACPI/libnvdimm pointers, flush resources, dirty shutdown fields, and label/DSM flags.

Dependencies include libnvdimm, ndctl, ACPI, workqueues, and ACPI UUID constants. Risks are cross-file state drift, bitmask shifts beyond supported command IDs, flexible-array allocation mismatches, and compile-option skew around MCE declarations. Test signals include build coverage with and without `CONFIG_X86_MCE`, provider-data conversion, command-mask attachment, ARS state transitions, and Intel ops integration.
