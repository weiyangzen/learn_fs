# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mcu.c

Purpose: MT76x2U USB firmware loader and MCU radio initialization. It loads optional ROM patch, downloads ILM/DLM firmware over USB/FCE, starts the MCU, and enables radio functions.

Important APIs: `mt76x2u_mcu_fw_init` and `mt76x2u_mcu_init`. Internal helpers send vendor/class commands for IVB loading, patch enable, WMT reset, ROM patch loading, and firmware loading.

Control flow: ROM patch loading optionally acquires a hardware semaphore, checks whether the patch is already active, requests firmware, validates header, configures USB DMA and FCE, resets MCU, sends patch chunks to `MT76U_MCU_ROM_PATCH_OFFSET`, enables patch, resets WMT, polls patch status, releases semaphore, and releases firmware. Main firmware loading validates ILM/DLM lengths, logs version/build, resets MCU, configures DMA/FCE, sends ILM and DLM chunks, loads IVB, polls firmware start bit, sets running bit, and records ethtool firmware version. MCU init selects queue function and turns radio on.

State and persistence: firmware files are module firmware dependencies; runtime state includes MCU registers, hardware semaphore, firmware version, USB transfer buffers, and radio state.

Dependencies and integration: depends on Linux firmware loader, mt76 USB vendor requests, mt76x02 firmware header structures, FCE register programming, and common MCU function/radio commands.

Risks: malformed firmware lengths or failed chunk transfers must not leave semaphores held. Revision-specific patch bits and DLM offsets are fragile. The shared `usb->data` buffer is used for control payloads and assumes serialized MCU setup.

Test signals: missing/invalid firmware files, ROM patch already-applied path, semaphore timeout, E3 versus older revision offsets, successful ethtool firmware version, and recovery after firmware start timeout.
