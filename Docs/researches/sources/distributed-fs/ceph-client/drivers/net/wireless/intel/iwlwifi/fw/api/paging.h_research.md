<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/paging.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/paging.h

`paging.h` defines the firmware paging layout command. It is intentionally small: `NUM_OF_FW_PAGING_BLOCKS` is 33, representing 32 data blocks plus one CSS block, and `struct iwl_fw_paging_cmd` carries flags, block size, block count, and an array of firmware/device-side physical addresses.

This ABI is used when the driver loads firmware that supports pageable code/data. The host allocates or maps paging blocks, fills `device_phy_addr[]` with the addresses the device should use, sets `block_size` as a power-of-two encoding, sets `block_num`, and sends the packed command to firmware. The header has no executable code and no notification path.

State and persistence live outside this file: DMA mappings, firmware image sections, and paging block lifetime are managed by firmware-loading code. The command itself is a one-time or reload-time transfer of a memory layout. Dependencies are minimal but consumers must use little-endian fields and must keep the address array aligned with firmware expectations.

Risks are DMA address truncation if a platform address does not fit the 32-bit ABI field, off-by-one errors around the CSS block, declaring more blocks than populated, mismatched block-size encoding, and lifetime bugs if paging memory is freed while firmware still references it. Test signals include firmware load on devices requiring paging, boundary checks for `NUM_OF_FW_PAGING_BLOCKS`, DMA mapping failure paths, suspend/resume or restart reload paths, and firmware error logs indicating invalid paging addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/paging.h -->
