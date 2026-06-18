# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/pcie/iwl-context-info.h

## Purpose
This header defines the original iwlwifi PCIe boot-loader context-info ABI. It describes firmware DRAM image maps, RX buffer descriptor configuration, command queue location, debug/PNVM pointers, and the top-level packed `iwl_context_info` consumed by firmware during INIT boot.

## Important APIs, Types, and Functions
- `IWL_MAX_DRAM_ENTRY` and `CSR_CTXT_INFO_BA` define the firmware DRAM map limit and context-info base CSR.
- `enum iwl_context_info_flags` encodes auto-init, early debug, core dump, RB cyclic-buffer exponent, long TFD format, and RX buffer size values.
- `struct iwl_context_info_dram_nonfseq` maps UMAC, LMAC, and virtual/paged firmware chunks.
- `struct iwl_context_info_rbd_cfg`, `iwl_context_info_hcmd_cfg`, `iwl_context_info_dump_cfg`, `iwl_context_info_pnvm_cfg`, and `iwl_context_info_early_dbg_cfg` hold DMA addresses and sizes for runtime rings, command queue, core dump, PNVM, and early debug.
- Function declarations include context init/free, paging free, firmware-section DMA initialization, coherent allocation, and generic DMA copy allocation.

## Control Flow
There is no direct logic. Callers allocate DMA memory, convert host values to little-endian fields, populate the top-level context-info structure, and program the device so firmware can discover boot images and queues.

## State and Persistence Behavior
All state is ABI data in DMA-coherent memory or CSR pointers. It persists across the firmware boot handoff and is freed by the PCIe context-info cleanup path. The DRAM arrays can reference up to 64 chunks per image category; stale addresses or premature free would leave firmware reading invalid memory.

## Dependencies and Integration Points
The header depends on Linux endian types and iwlwifi transport/firmware structs declared elsewhere. It integrates with older context-info implementation, firmware image section loading, RX queue setup, host command queue setup, early debug/core dump paths, PNVM loading, and paging cleanup.

## Risks and Edge Cases
The main risk is ABI drift: these packed structs must match firmware expectations exactly. Callers must provide DMA addresses that remain valid, set RB sizes supported by firmware, and avoid exceeding `IWL_MAX_DRAM_ENTRY`. Size units differ by field: some are bytes, some DWs, and `cmd_queue_size` is an entry count.

## Test Signals
Successful INIT firmware boot and working RX/host-command queues are the primary test signal. Early debug dumps, PNVM application, and core dump capture provide secondary evidence. Compile-time users also validate declarations against implementation.
