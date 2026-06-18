<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb.h

Purpose: public prototypes for the mt76x02 USB support layer. It exposes USB MAC start, MCU init/firmware reset/data upload, TX DMA-info preparation/completion, and USB beacon timer setup/teardown.

Important APIs/types/functions: `mt76x02u_mac_start()`, `mt76x02u_init_mcu()`, `mt76x02u_mcu_fw_reset()`, `mt76x02u_mcu_fw_send_data()`, `mt76x02u_skb_dma_info()`, `mt76x02u_tx_prepare_skb()`, `mt76x02u_tx_complete_skb()`, `mt76x02u_init_beacon_config()`, and `mt76x02u_exit_beacon_config()`.

Control flow: declarative header linking mt76x0/mt76x2 USB bus drivers to shared USB core/MCU helpers.

State and persistence: no local state; callers affect USB DMA headers, firmware upload state, and beacon timers.

Dependencies/integration: includes `mt76x02.h`; consumed by mt76x0 USB, mt76x2 USB, and mt76x02 USB implementation files.

Risks: prototypes must stay aligned with shared USB implementations and driver ops. Test signals include build coverage for `CONFIG_MT76x02_USB`, USB firmware loading, TX completion, and AP beacons on USB devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb.h -->
