<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/file.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/file.h

Purpose: firmware file/TLV ABI definition for iwlwifi microcode, capabilities, debug TLVs, command-version tables, calibration, PNVM, and FSEQ data.

Important APIs/types: includes old `iwl_ucode_header`, TLV header `iwl_ucode_tlv`, TLV type enum, API and capability bit enums, calibration and PHY config types, debug destination/config/trigger structs, command-version and BIOS command revision records, dump exclusion records, FSEQ file layout, and helpers `iwl_tlv_array_len()`/`iwl_tlv_array_len_with_size()`.

Control flow: parser code outside this file consumes the TLV enum and packed structs; debug collection later uses parsed `iwl_fw_dbg_*` pointers. The array-length helper validates that variable-length TLV payloads are multiples of the element size before iteration.

State and persistence: all structures represent persistent firmware file content or parsed runtime capabilities. The many enums are effectively ABI values shared with firmware, BIOS/UEFI tables, and userspace dump/debug tooling.

Dependencies/integration: included by `img.h`, `dbg.h`, and firmware loaders. It touches cfg80211 interface type constants, netdevice Ethernet address sizing, and firmware debug APIs.

Risks/test signals: TLV numeric values and packed layouts are high risk. Test firmware parsing across old and TLV formats, sparse bitwise API/capability handling, debug trigger/config parsing, variable-length TLV validation, command-version defaults, PNVM embedded TLVs, and FSEQ file validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/file.h -->
