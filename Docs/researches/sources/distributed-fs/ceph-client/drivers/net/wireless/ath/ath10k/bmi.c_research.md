# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/bmi.c

Purpose: Implementation of ath10k Bootloader Messaging Interface operations. BMI is the one-shot boot-time protocol for reading/writing target memory and registers, downloading firmware/patch data, executing target code, setting the app start address, and finally closing bootloader access with `BMI_DONE`.

Important APIs/types/functions: Public exported lifecycle and transfer APIs include `ath10k_bmi_start`, `ath10k_bmi_done`, `ath10k_bmi_get_target_info`, `ath10k_bmi_get_target_info_sdio`, `ath10k_bmi_read_memory`, `ath10k_bmi_write_memory`, `ath10k_bmi_read_soc_reg`, `ath10k_bmi_write_soc_reg`, `ath10k_bmi_execute`, `ath10k_bmi_lz_stream_start`, `ath10k_bmi_lz_data`, `ath10k_bmi_fast_download`, and `ath10k_bmi_set_start`. All real transport is delegated to `ath10k_hif_exchange_bmi_msg`.

Control flow: `ath10k_bmi_start` clears `ar->bmi.done_sent`. Each command rejects use after `BMI_DONE` with `-EBUSY`. Standard target-info sends `BMI_GET_TARGET_INFO` and validates response length; the SDIO variant handles a sentinel/version-length split response. Memory reads and writes chunk transfers at `BMI_MAX_DATA_SIZE`, with writes rounded to 4 bytes after copying. Large LZ data optionally uses a heap-allocated command buffer up to `BMI_MAX_LARGE_DATA_SIZE`. `ath10k_bmi_fast_download` starts an LZ stream, sends aligned bulk data, pads a trailing partial word, then starts a fake zero stream to flush target caches. `ath10k_bmi_done` sends `BMI_DONE` once and marks the window closed before exchange.

State/persistence: The only persistent driver state is `ar->bmi.done_sent`. Effects are target-side boot state: memory contents, SoC registers, patch data, execution results, app start address, and final exit from BMI mode. No host filesystem persistence.

Dependencies/integration: Used by ath10k core firmware boot paths across PCI/AHB/SDIO/USB/SNOC HIFs. Depends on `bmi.h` wire formats, HIF BMI exchange, host-interest address helpers for macros in the header, and debug/warn logging.

Risks: BMI is available only during early boot; accidental `BMI_DONE` ordering prevents further recovery commands. Chunking/rounding must avoid reading past caller buffers and keep target lengths aligned. SDIO target-info sequencing is special and easy to regress. Large download allocation failures and HIF timeouts directly fail firmware boot.

Test signals: Firmware boot success, target info version/type reads, board/OTP reads through BMI memory/register helpers, successful compressed firmware download, no commands after `BMI_DONE`, and debug logs under `ATH10K_DBG_BMI` validate behavior.
