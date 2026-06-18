<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.h

Purpose: central in-memory firmware image model for iwlwifi.

Important APIs/types: defines firmware image types (`REGULAR`, `INIT`, `WOWLAN`, `REGULAR_USNIFFER`), section descriptors, `struct iwl_ucode_capabilities`, `fw_has_api()`, `fw_has_capa()`, `struct fw_img`, paging constants, `struct iwl_fw_paging`, firmware type, debug metadata `struct iwl_fw_dbg`, and the top-level `struct iwl_fw`.

Control flow: mostly declarative. Inline helpers convert parsed state into decisions: debug monitor mode string, whether a config uses usniffer, and safe image lookup. Paging constants are consumed by `paging.c` and dump code.

State and persistence: `struct iwl_fw` stores parsed firmware version strings, image sections, capabilities, event/error log pointers, calibration defaults, antenna masks, debug TLVs, PHY integration version, dump exclusion ranges, and embedded PNVM data. It is shared read-only-ish runtime state after firmware load.

Dependencies/integration: includes firmware debug TLV, NVM/regulatory, file, and error-dump contracts. Almost every firmware runtime component receives a `const struct iwl_fw *`.

Risks/test signals: capability bitmaps and image section offsets gate command formats and memory loading. Test all image types, paging/no-paging images, embedded PNVM, debug TLV presence, `IWL_UCODE_TYPE_MAX` bounds, and feature checks via `fw_has_api()`/`fw_has_capa()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/img.h -->
