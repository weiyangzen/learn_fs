<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_mcu.c

Purpose: shared mt76x02 USB MCU transport and firmware-upload helper. It implements in-band USB command messages, random register read/write batches, response polling, firmware reset, and chunked firmware transfer through FCE.

Important APIs/types/functions: `mt76x02u_init_mcu()`, `mt76x02u_mcu_fw_reset()`, `mt76x02u_mcu_fw_send_data()`, USB MCU send/read/write helpers, and `mt76x02u_mcu_wait_resp()`.

Control flow: normal MCU send allocates an skb, locks the MCU mutex, optionally assigns a sequence, prepends USB DMA info, bulk-sends to the in-band command endpoint, and waits on command-response endpoint for matching done event. Random writes recurse over max packet-sized chunks; random reads require one command and place returned values into caller pairs. Firmware upload writes FCE DMA address/length, bulk-sends a command header plus payload, bumps CPU descriptor index, and sleeps between chunks.

State and persistence: uses `usb->mcu.data`, `rp/rp_len/base`, `mcu.msg_seq`, and hardware FCE/descriptor registers. Firmware data changes MCU memory until reset.

Dependencies/integration: mt76 USB bulk/vendor helpers, shared MCU parse response, DMA/FCE bitfields, mt76x0/mt76x2 USB firmware loaders.

Risks: response sequence mismatch, read-pair length mismatch, recursive write depth, fixed response retries, firmware chunk alignment, and removed-device behavior. Test signals include random register read/write, command timeout, firmware chunk upload, unplug during MCU command, and multi-command sequence wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_mcu.c -->
