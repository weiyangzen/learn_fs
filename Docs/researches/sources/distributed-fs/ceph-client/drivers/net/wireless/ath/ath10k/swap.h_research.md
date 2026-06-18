# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.h

Purpose: Defines firmware code-swap binary limits, packed TLV/tail/hardware-info structures, runtime segment state, and public code-swap lifecycle APIs.

Important APIs and types: Defines maximum swap binary length, magic size, maximum/supported segment counts, `ath10k_swap_code_seg_tlv`, `ath10k_swap_code_seg_tail`, `ath10k_swap_code_seg_item`, `ath10k_swap_code_seg_hw_info`, `ath10k_swap_code_seg_info`, and the init/configure/release prototypes.

Control flow, state, and persistence: No flow. The packed structures form the host/firmware ABI for code-swap metadata and DMA bus addresses.

Dependencies and integration points: References `struct ath10k_fw_file` and uses little-endian and DMA address types. Consumed by firmware loading, normal boot, and testmode UTF boot paths.

Risks: ABI packing and endianness must match firmware. `ATH10K_SWAP_CODE_SEG_NUM_SUPPORTED` is currently one despite room for 16 bus addresses, so adding multi-segment support requires implementation changes, not just constants.

Test signals: Compile firmware loader and testmode paths, validate structure sizes against firmware expectations, and boot firmware images with and without code-swap segments.
