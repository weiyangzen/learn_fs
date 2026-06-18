## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.h

Purpose: SDIO register map, constants, state structures, and public probe/remove declarations for the rtw88 SDIO HCI.

Important APIs/types: defines SDIO bus-domain offsets, host interrupt mask/status registers, indirect register access registers, command address encodings, block size, RX FIFO address macro, and 8-byte data pointer alignment. `struct rtw_sdio` holds the SDIO function, IRQ mask, RX address, SDIO3 mode, IRQ-thread marker, TX workqueue, work item, and TX skb queues. `struct rtw_sdio_tx_data` stores TX report sequence number in skb driver data.

Control flow and state: no complex runtime flow except `rtw_sdio_is_sdio30_supported()`, which reads `sdio3_bus_mode` from private HCI state. The register constants direct all read/write and FIFO operations in `sdio.c`.

Dependencies and integration: includes forward declarations for `sdio_func` and `sdio_device_id`, exports `rtw_sdio_pm_ops`, and declares SDIO lifecycle functions used by chip glue modules such as `rtw8822cs.c`.

Risks and test signals: register offset and bit-mask correctness are critical. State layout must fit the `ieee80211_alloc_hw(sizeof(rtw_dev)+sizeof(rtw_sdio))` allocation model. Test through compilation, SDIO IRQ/RX/TX operation, and descriptor alignment checks on strict hosts.
