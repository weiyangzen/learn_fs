# sources/distributed-fs/ceph-client/drivers/nfc/nfcmrvl/fw_dnld.c

Purpose: Implements the Marvell NCI firmware downloader, including bootrom reset handling, logical connection setup, helper upload, firmware upload, and final boot command sequencing.

Important APIs and functions: Public entry points are `nfcmrvl_fw_dnld_init()`, `nfcmrvl_fw_dnld_deinit()`, `nfcmrvl_fw_dnld_start()`, `nfcmrvl_fw_dnld_abort()`, and `nfcmrvl_fw_dnld_recv_frame()`. Internal state handlers include `process_state_reset()`, `process_state_init()`, `process_state_set_ref_clock()`, `process_state_set_hi_config()`, `process_state_open_lc()`, `process_state_fw_dnld()`, `process_state_close_lc()`, and `process_state_boot()`.

Control flow: `nfcmrvl_fw_dnld_start()` requests the firmware image, validates the Marvell magic and PHY id, chooses helper or firmware config, programs bootrom transport settings, arms a timeout, resets the chip, and waits for CORE_RESET notification. Receive frames are queued to a single-thread workqueue. The worker matches exact NCI response patterns, configures reference clock and host-interface parameters, opens the proprietary firmware-download logical connection, exchanges helper commands, ACK/NACKs, data chunks, and credits, closes the logical connection, and sends the proprietary boot command. If a helper was loaded, the state machine returns to reset for the real firmware image.

State and persistence: State lives in `priv->fw_dnld`: firmware pointer, parsed header/config, state/substate, current file offset, chunk length, RX queue/workqueue, and timeout timer. It also manipulates `ndev->cmd_cnt` and `ndev->cmd_timer` to coexist with NCI command serialization. There is no durable persistence; the firmware file is released at completion or failure.

Dependencies and integration points: Depends on Linux firmware loading, NCI command/frame helpers, `nfcmrvl_private`, bus `nci_update_config()` callbacks, reset/halt helpers, raw NFC socket tracing, and `nfc_fw_download_done()`.

Risks: Response matching is byte-exact and brittle to bootrom revisions. Chunk length/complement validation protects protocol integrity, but firmware offsets are trusted after header validation. Timer/workqueue cleanup must race safely with unregister. Failure halts the chip, which affects later recovery. Test signals include valid helper+firmware paths, firmware-without-helper, bad magic/PHY, malformed NCI responses, bad length complement NACK, credit sequencing, timeout, abort during unregister, and per-PHY config updates.
