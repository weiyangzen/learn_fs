# sources/distributed-fs/ceph-client/drivers/acpi/nfit/mce.c

`mce.c` connects x86 machine-check decoding to NFIT persistent-memory poison handling. It registers a high-priority MCE notifier, detects uncorrectable memory errors inside NFIT pmem SPAs, records bad ranges in libnvdimm, notifies the affected region, and optionally schedules an ARS rescan.

The main function is `nfit_handle_mce()`, registered by `nfit_mce_register()` and removed by `nfit_mce_unregister()`. It filters out non-memory, correctable, and unusable-address MCEs, locks `acpi_desc_lock`, scans active `acpi_descs`, takes `init_mutex`, and searches `NFIT_SPA_PM` ranges covering `mce->addr`. On a hit it aligns the address using `MCI_MISC_ADDR_LSB`, calls `nvdimm_bus_add_badrange()`, notifies `NVDIMM_REVALIDATE_POISON`, may call `acpi_nfit_ars_rescan()`, and marks `MCE_HANDLED_NFIT`.

This file owns no durable state; it reads `acpi_descs` and writes badrange state into libnvdimm plus a flag into the MCE record. It depends on x86 MCE helpers, global NFIT descriptor locking, `nfit_spa_type()`, and libnvdimm poison notification.

Risks are teardown races, address-alignment mistakes, assuming no SPA aliasing, and limited recovery when ARS scheduling fails. Test signals include injected correctable/uncorrectable MCEs, addresses in and out of pmem SPAs, scrub-mode behavior, multiple descriptors, and notifier register/unregister ordering.
