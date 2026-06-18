# sources/distributed-fs/ceph-client/drivers/edac/skx_common.c

Purpose: `skx_common.c` is the shared Intel server EDAC support library for SKX-family drivers. It manages common topology lists, ADXL firmware decoding, DIMM/NVDIMM metadata, EDAC MC registration, MCE filtering/reporting, cleanup, and debugfs address injection.

Important APIs/types/functions: exported helpers include `skx_adxl_get/put()`, `skx_set_decode()`, `skx_set_mem_cfg()`, `skx_set_res_cfg()`, `skx_get_src_id()`, `skx_get_all_bus_mappings()`, `skx_get_hi_lo()`, `skx_get_dimm_info()`, `skx_get_nvdimm_info()`, `skx_register_mci()`, `skx_mce_check_error()`, and `skx_remove()`. `skx_adxl_decode()` translates firmware component names into `struct decoded_addr`; `skx_mce_output_error()` reports EDAC events.

Control flow: front-end drivers configure resource/decode callbacks, discover bus mappings, register MCs, and let `skx_mce_check_error()` handle runtime MCEs. The MCE path ignores non-memory/addressless/already-handled events, validates the address, tries driver decode, falls back to ADXL, selects the MC, logs context, emits EDAC, and marks the MCE handled.

State and persistence: global ADXL buffers/indexes, decode callbacks, TOLM/TOHM, `dev_edac_list`, memory mode, and resource config exist only for module lifetime. `skx_remove()` unregisters MCs, releases PCI/device references, unmaps MMIO, and frees devices.

Dependencies/integration: EDAC core, ACPI ADXL/NFIT, DMI, x86 MCE, PCI, topology/NUMA, UV detection, page validation, and EDAC debugfs.

Risks: strict ADXL component matching, shared globals across SKX-family users, firmware/driver decode disagreements, online-page filtering, and register-derived DIMM capacity assumptions.

Test signals: debugfs fake MCEs, ADXL success/failure paths, 1LM and 2LM near/far classification, hidden-controller mapping, NVDIMM size lookup, and cleanup after registration failures.
