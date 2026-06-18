# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk_wed.h

Purpose: This header defines the MediaTek Wireless Ethernet Dispatch interface shared between WLAN drivers and the MediaTek Ethernet/WED offload provider.

Important APIs/types/functions: It defines TX/RX queue counts, WED WO command IDs, packed buffer descriptors, bus type enum, `struct mtk_wed_ring`, `struct mtk_wed_wo_rx_stats`, `struct mtk_wed_buf`, `struct mtk_wed_device`, and `struct mtk_wed_ops`. Inline helpers attach a device through the RCU-protected global `mtk_soc_wed_ops`, query RX/AMSDU capabilities, and macro-dispatch ring setup, IRQ, register, PPE, TC, reset, RRO, and stop/start operations. Disabled builds provide no-op or error-returning stubs.

Control flow: WLAN drivers fill `mtk_wed_device.wlan`, call attach, configure rings and buffers, start WED with IRQ masks, send firmware/WO messages, update RX stats, and detach/stop/reset when the WLAN device stops.

State and persistence: `mtk_wed_device` holds runtime ring descriptors, DMA addresses, buffer pools, WDMA/WPDMA register offsets, offload capabilities, token ranges, and callbacks. Hardware rings and firmware state persist while WED is running.

Dependencies and integration: Uses RCU, regmap, PCI, SKBs, netdevice, TC setup types, DMA, and `CONFIG_NET_MEDIATEK_SOC_WED`. Integrates WLAN drivers with MediaTek Ethernet, PPE, WDMA, and firmware offload.

Risks and test signals: Operation pointer lifetime, RCU attach semantics, ring DMA setup, token ranges, and version-gated RX/RRO support are critical. Test disabled configs, attach failure cleanup, traffic offload, IRQ masks, reset recovery, RRO/AMSDU paths, TC offload, and module unload.
