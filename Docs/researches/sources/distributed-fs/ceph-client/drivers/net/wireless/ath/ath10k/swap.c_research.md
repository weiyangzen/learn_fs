# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/swap.c

Purpose: Implements ath10k firmware code swap support, allowing firmware code segments to reside in host DMA-coherent memory and communicating segment metadata to the target through BMI.

Important APIs and functions: Public functions are `ath10k_swap_code_seg_init()`, `ath10k_swap_code_seg_configure()`, and `ath10k_swap_code_seg_release()`. Internal helpers allocate coherent memory, parse the code-swap TLV/tail format, fill `ath10k_swap_code_seg_info`, and free the segment.

Control flow: Init checks firmware-provided code-swap data, allocates a bounded coherent buffer, parses one or more TLV payloads until a zero-length tail with a zeroed magic signature supplies the BMI write address, copies payload data into host memory, and stores the segment info on the firmware file. Configure writes the hardware info structure to the target address via BMI. Release frees coherent memory and clears code-swap fields from the firmware file.

State and persistence: State is attached to `fw_file->firmware_swap_code_seg_info`, with coherent virtual address, DMA address, target BMI write address, and hardware info fields. No durable persistence exists, but the target consumes the DMA bus address after BMI configuration.

Dependencies and integration points: Depends on ath10k core device DMA APIs, BMI memory write, firmware file parsing, and the code-swap structures declared in `swap.h`. Testmode UTF startup can also initialize/release code-swap firmware.

Risks: TLV length validation protects against malformed firmware blobs; a bad `size_log2` or DMA address truncation would break target fetches. Only one segment is supported. Release comments note that clearing `codeswap_data`/`codeswap_len` may be misplaced, which is a lifecycle risk if firmware ownership assumptions change.

Test signals: Firmware without code-swap data, valid code-swap TLV/tail parse, oversized image rejection, invalid TLV length, missing tail, BMI write failure, release after init failure, normal firmware startup, and UTF testmode startup with code-swap data.
