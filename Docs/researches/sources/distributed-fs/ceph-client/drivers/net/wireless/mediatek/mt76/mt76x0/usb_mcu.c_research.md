<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb_mcu.c

Purpose: MT76x0 USB MCU firmware loader. It validates firmware headers, loads ILM/DLM segments over the shared mt76x02 USB firmware-data path, sends the IVB block with a vendor request, and marks the MCU running.

Important APIs/types/functions: `mt76x0u_mcu_init()`, `mt76x0u_load_firmware()`, `mt76x0u_upload_firmware()`, and `mt76x0_get_firmware()`. It consumes `struct mt76x02_fw_header`, `MT_MCU_IVB_SIZE`, `MT_MCU_DLM_OFFSET`, and `mt76x02u_mcu_fw_send_data()`.

Control flow: initialization enables USB DMA, returns early if firmware is already running, requests `mt7610e.bin` with fallback to `mt7610u.bin`, validates header size/ILM/DLM lengths, resets firmware, programs FCE/PSE registers, toggles UDMA drop, uploads ILM then DLM chunks, sends IVB via `MT_VEND_DEV_MODE`, and polls `MT_MCU_COM_REG0` for start.

State and persistence: only hardware/firmware state changes persist until device reset: FCE DMA pointers, USB DMA config, firmware running bit, and `MT76_STATE_MCU_RUNNING`. Firmware is requested from the kernel firmware loader but not modified.

Dependencies/integration: depends on Linux firmware APIs, mt76 USB vendor requests/bulk firmware transfer, mt76x02 MCU header layout, and mt76x0 firmware-running detection.

Risks: exact firmware size validation is critical; ILM length must exceed IVB size; bulk-transfer chunk limits and sleeps affect reliability; COM register polling controls failure detection. Test signals include missing `mt7610e.bin` fallback, malformed firmware lengths, firmware already running, COM timeout, and bulk or vendor-request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb_mcu.c -->
