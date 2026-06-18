# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/bmi.c

Purpose: Implements the ath6kl Bootloader Messaging Interface used before firmware start to query target info, read/write target memory and registers, execute target code, set application start, and download compressed firmware data.

Important APIs and functions: `ath6kl_bmi_init()` allocates the command buffer based on HIF-provided `max_data_size`; `ath6kl_bmi_cleanup()` frees it; `ath6kl_bmi_reset()` clears the done flag. Command APIs include `ath6kl_bmi_done()`, `ath6kl_bmi_get_target_info()`, `ath6kl_bmi_read()`, `ath6kl_bmi_write()`, `ath6kl_bmi_execute()`, `ath6kl_bmi_set_app_start()`, `ath6kl_bmi_reg_read()`, `ath6kl_bmi_reg_write()`, `ath6kl_bmi_lz_stream_start()`, `ath6kl_bmi_lz_data()`, and `ath6kl_bmi_fast_download()`.

Control flow: Every command checks `ar->bmi.done_sent` and refuses access after `BMI_DONE`. Requests are serialized into `ar->bmi.cmd_buf` with command ID, address/length/parameters, then sent through `ath6kl_hif_bmi_write()`; commands with responses read through `ath6kl_hif_bmi_read()`. Memory reads/writes split transfers by `max_data_size`. Writes pad short unaligned final chunks to 4 bytes. Fast download starts an LZ stream, sends aligned compressed data, sends a padded final word if needed, then starts a zero-address stream to flush target caches.

State and persistence: Mutates `ar->bmi.done_sent`, `cmd_buf`, `max_cmd_size`, and target memory/register/application-start state through BMI commands. Host buffer state is runtime-only; target-side changes persist until target reset or firmware takeover.

Dependencies and integration points: Depends on `core.h`, `hif-ops.h`, `target.h`, debug helpers, HIF transport BMI read/write operations, and target boot ROM protocol definitions from `bmi.h`. Called during `ath6kl_core_init()` and firmware loading before WMI/HTC operation.

Risks: The code uses host-endian command fields as expected by the target/HIF path; mismatch would break boot. Incorrect `max_data_size` can overflow the fixed local `aligned_buf` or violate command-size checks. After `BMI_DONE`, commands correctly return `-EACCES`; callers must order firmware setup before done. There is a subtle write-loop behavior where padding increases `len_remain`, so accounting depends on padded target write semantics.

Test signals: Boot AR6003/AR6004 over SDIO and USB, target-info old/new sentinel formats, memory read/write chunk boundaries, unaligned write and fast-download tails, register read/write, execute return parameter, command rejection after BMI done, allocation failure, and HIF error propagation.
