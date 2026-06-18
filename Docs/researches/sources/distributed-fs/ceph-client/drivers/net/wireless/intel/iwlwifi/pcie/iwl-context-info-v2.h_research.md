# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info-v2.h

## Purpose
This header defines the second-generation iwlwifi PCIe context-info ABI used to boot newer devices through peripheral scratch/context structures. It describes CSR offsets, scratch control bits, message-ring metadata, DRAM firmware maps with FSEQ support, PNVM/reduce-power pointers, and function prototypes for allocation, kick, free, and PNVM/reduce-power loading.

## Important APIs, Types, and Functions
- CSR constants include `CSR_CTXT_INFO_BOOT_CTRL`, `CSR_CTXT_INFO_ADDR`, `CSR_IML_DATA_ADDR`, `CSR_IML_SIZE_ADDR`, and `CSR_IML_RESP_ADDR`.
- `enum iwl_prph_scratch_mtr_format`, `enum iwl_prph_scratch_flags`, and `enum iwl_prph_scratch_ext_flags` encode firmware-visible boot/debug/RB/MTR/reset settings.
- Packed structs such as `iwl_prph_scratch_version`, `iwl_prph_scratch_control`, `iwl_prph_scratch_pnvm_cfg`, `iwl_prph_scratch_hwm_cfg`, `iwl_prph_scratch_rbd_cfg`, `iwl_prph_scratch_uefi_cfg`, and `iwl_prph_scratch_ctrl_cfg` model the peripheral scratch control region.
- `struct iwl_context_info_dram_fseq` extends the v1 non-FSEQ DRAM map with `fseq_img` entries.
- `struct iwl_context_info_v2` defines IPC message/completion ring base addresses, index arrays, ring sizes, doorbell/MSI vectors, optional header/footer sizes, peripheral info, and scratch addresses.
- Exported declarations include `iwl_pcie_ctxt_info_v2_alloc()`, `iwl_pcie_ctxt_info_v2_kick()`, `iwl_pcie_ctxt_info_v2_free()`, PNVM loaders/setters, and reduce-power loaders/setters.

## Control Flow
This file has no executable control flow. Runtime code in the matching context-info implementation allocates coherent memory, fills these packed structs with little-endian physical addresses and sizes, writes context-info CSR pointers, and kicks device boot. Firmware then reads the context-info and scratch layouts as an ABI contract.

## State and Persistence Behavior
The structs represent DMA-backed boot state consumed by firmware. Fields persist only for the lifetime of the transport allocation, but the contents are hardware-visible and must remain stable until firmware has finished reading them. Flags in scratch control govern early debug, RBD size, MTR descriptor format, external FSEQ, URM mode, 32 KHz clock validity, SCU force-active, and top reset behavior.

## Dependencies and Integration Points
It includes `iwl-context-info.h` for shared DRAM map definitions and relies on Linux fixed-width little-endian types. It integrates with PCIe context-info v2 implementation files, PNVM handling, UEFI reduce-power handling, firmware capability parsing, and the iwlwifi transport boot sequence.

## Risks and Edge Cases
The packed layout is an ABI: changing field order, size, endianness, or reserved padding can break firmware boot. Address fields are 64-bit and must match DMA allocations. RB size flags have older-firmware compatibility notes; callers must set legacy and extended RB-size fields consistently. `UNFRAGMENTED_PNVM_PAYLOADS_NUMBER` and `IPC_DRAM_MAP_ENTRY_NUM_MAX` imply fixed firmware limits that loaders must respect.

## Test Signals
Signals include successful firmware boot on v2 devices, correct PNVM/reduce-power loading, early debug buffer operation, ring interrupt delivery, and failure diagnostics when scratch flags or address arrays are malformed. Build coverage should catch struct references, but runtime validation is primarily hardware/firmware driven.
