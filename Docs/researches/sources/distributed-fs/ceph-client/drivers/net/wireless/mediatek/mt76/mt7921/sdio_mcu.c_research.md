# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mcu.c

Purpose: SDIO-specific MCU transport and power ownership support for MT7921. It adapts common connac2 MCU messages to SDIO packet framing and implements driver-own/firmware-own transitions.

Important APIs/types/functions: `mt7921s_mcu_init()` installs `mt76_mcu_ops`, powers the chip to driver-own, runs firmware, and marks `MT76_STATE_MCU_RUNNING`. `mt7921s_mcu_send_message()` fills connac2 MCU TXD, chooses command versus firmware-download SDIO packet type, appends USB/SDIO header and padding, queues to `MT_MCUQ_WM`, and kicks the queue. `mt7921s_mcu_drv_pmctrl()` and `mt7921s_mcu_fw_pmctrl()` manipulate WHLPCR/mailbox ownership.

Control flow: command send refuses work during firmware assertion, fills the message, sets a three-second timeout, tags firmware scatter downloads as `MT7921_SDIO_FWDL`, aligns to four bytes, submits the raw MCU queue, and kicks. PM wake clears firmware-own request and polls PCR/mailbox until driver-own; PM sleep clears driver-own mailbox ack, requests firmware-own, and polls until ownership drops.

State/persistence: updates `mdev->mcu.timeout`, `dev->mt76.mcu_ops`, `MT76_STATE_MCU_RUNNING`, `MT76_STATE_PM`, and PM awake/doze accounting in `pm->stats`. Hardware-visible state is SDIO WHLPCR/PCR and D2HRM3R mailbox state.

Dependencies/integration: uses `mt76_connac2_mcu_fill_message()`, `mt7921_mcu_parse_response`, mt76 SDIO queue operations, SDIO register helpers, and MT7921 firmware loader. The PM functions are consumed by SDIO reset and runtime PM paths.

Risks: ownership polling timeouts return `-EIO` and can block reset/recovery. `dev->fw_assert` deliberately returns `-EBUSY` to avoid common workqueue blockage, so callers must tolerate transient MCU send failures. Queue submission errors leave ownership and timeout state unchanged.

Test signals: verify firmware download over SDIO, normal MCU command/response sequences, ownership transitions around runtime PM, firmware assert behavior, and reset paths that call driver-own before touching registers.
