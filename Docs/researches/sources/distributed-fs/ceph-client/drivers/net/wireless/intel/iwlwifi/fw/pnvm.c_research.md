<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.c

Purpose: selects, parses, loads, and activates PNVM and reduced-power regulatory data for firmware.

Important APIs/functions: exported `iwl_pnvm_load()` drives the flow. Helpers select PNVM source (`BIOS`, external `.pnvm`, embedded `.ucode`, or none), request firmware from filesystem, parse SKU and hardware-matching TLV sections, load PNVM/reduced-power chunks into transport, set active transport data, ring the PNVM doorbell, and wait for `PNVM_INIT_COMPLETE_NTFY`.

Control flow: source selection depends on Intel vs non-Intel SKU, device family, and RF type. Parsing scans `IWL_UCODE_TLV_PNVM_SKU`, matches three SKU words, then scans the section for PNVM version, HW type, runtime section chunks, UEFI mem descriptors, and section delimiters. Load failures set transport flags to avoid repeated parsing attempts.

State and persistence: mutates `trans->pnvm_loaded`, `trans->fail_to_parse_pnvm_image`, `trans->reduce_power_loaded`, `trans->failed_to_load_reduce_power_image`, and `trans->reduced_cap_sku`. Loaded data is held by transport; temporary images are freed unless embedded.

Dependencies/integration: uses firmware TLV definitions, UEFI helpers, filesystem firmware loader, transport load/set hooks, notification wait framework, regulatory/NVM command ids, and PNVM filename generation.

Risks/test signals: source fallback, SKU/HW matching, chunk limits, ownership of embedded vs allocated data, and notification timeout are high-risk. Test BIOS-only non-Intel SKU, AX210 GF external PNVM, embedded PNVM on newer devices, missing PNVM assert/log path, reduced-power UEFI parse, doorbell notification success/timeout, and empty SKU no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/pnvm.c -->
