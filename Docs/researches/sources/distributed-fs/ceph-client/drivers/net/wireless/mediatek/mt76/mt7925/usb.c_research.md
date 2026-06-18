# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/usb.c

## Purpose
This file implements the MT7925U USB bus driver. It matches USB IDs, sends MCU messages over USB endpoints, powers on and initializes USB DMA, registers the shared MT7925 device, and handles USB reset/suspend/resume/disconnect through MT792x USB helpers.

## Important APIs, Types, And Functions
The module entry is `module_usb_driver(mt7925u_driver)`. Key functions are `mt7925u_probe()`, `mt7925u_mcu_send_message()`, `mt7925u_mcu_init()`, `mt7925u_mac_reset()`, and PM callbacks `mt7925u_suspend()`/`mt7925u_resume()`. Driver ops select `mt7925_usb_sdio_tx_prepare_skb()`, `mt7925_usb_sdio_tx_complete_skb()`, `mt7925_usb_sdio_tx_status_data()`, MT7925 RX and station callbacks, and shared survey updates.

## Control Flow
Probe clones mac80211 ops and replaces stop with USB stop, allocates `mt792x_dev`, resets the USB device, initializes mt76 USB state and bus ops, reads revision, resets WFSYS if firmware is already ready, powers on the MCU, allocates MCU/data queues, initializes USB DMA, sets max TX fragments based on scatter-gather support, then registers the MT7925 device. MCU send fills the MT7925 message header, chooses in-band command or AC_BE/FWDL endpoint, prepends USB/SDIO header, pads to a four-byte boundary plus tail, sends a bulk message, and frees the SKB. Reset stops RX/TX, resets WFSYS, resumes RX, powers on MCU, initializes DMA, reloads firmware/eeprom/MAC, and restarts the PHY. Suspend requests HIF suspend and waits for idle before stopping USB RX/TX. Resume polls firmware suspend flags, optionally reinitializes DMA, resumes RX, clears HIF suspend, and resets on failure.

## State And Persistence
State includes USB interface data, device reference, bus ops, MCU ops, FWDL mode bit in `MT_UDMA_TX_QSEL`, `MT76_STATE_MCU_RUNNING`, PM suspended/HIF flags, queue allocations, scatter-gather TX fragment capability, and firmware suspend event bits.

## Dependencies And Integration Points
It integrates Linux USB core, mt76 USB queue/control helpers, shared MT792x USB register access and WFSYS reset, MT7925 firmware/MAC/EEPROM code, and connac HIF suspend commands.

## Risks
USB control and bulk endpoint selection must match firmware boot state. Padding/header length errors break MCU commands. Resume reinitialization depends on firmware SER suspend bits and DMA reinit detection. Error paths must release USB references, interface data, queues, and mt76 device memory correctly.

## Test Signals
USB probe for MediaTek and Netgear IDs, firmware load, traffic with and without SG, suspend/resume/reset_resume, unplug/disconnect, forced MAC reset, MCU command responses, and queue teardown under errors validate this driver.
