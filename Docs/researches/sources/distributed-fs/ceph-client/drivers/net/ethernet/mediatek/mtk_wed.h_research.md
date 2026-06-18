<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.h

## Purpose
`mtk_wed.h` is the private WED header for the MediaTek Ethernet driver. It defines per-SoC WED register metadata, private hardware state, AMSDU allocation records, WDMA forwarding information, MMIO/regmap accessors for WED/WDMA/WPDMA rings, version helpers, public internal WED entry points, and build-time stubs when WED support is disabled.

## Important APIs And Types
`struct mtk_wed_soc_data` stores variant-specific register offsets, reset masks, TX ring descriptor size, and WDMA descriptor size. `struct mtk_wed_amsdu` records a v3 AMSDU TXD buffer and DMA address. `struct mtk_wed_hw` is the private hardware instance: it points to SoC data, device tree node, Ethernet core, WED regmap, hifsys/mirror regmaps, WDMA MMIO/physical base, debugfs directory, attached `mtk_wed_device`, WOCPU object, AMSDU array, PCIe base, flow count, version, IRQ, and index. `struct mtk_wdma_info` is the compact path result used by PPE offload to program WDMA index, queue, WCID, BSS, and AMSDU flag.

Inline helpers include version predicates, `wed_w32/r32`, `wdma_w32/r32`, `wpdma_tx_*`, `wpdma_rx_*`, `wpdma_txfree_*`, and `mtk_wed_get_pcie_base`. Public internal functions include `mtk_wed_add_hw`, `mtk_wed_exit`, `mtk_wed_flow_add`, `mtk_wed_flow_remove`, `mtk_wed_fe_reset`, `mtk_wed_fe_reset_complete`, and `mtk_wed_hw_add_debugfs`.

## Control Flow
When `CONFIG_NET_MEDIATEK_SOC_WED` is enabled, callers can register WED hardware, attach WLAN devices through the public ops table, and access WED/WDMA/WPDMA registers through these helpers. WPDMA accessor helpers return zero or no-op if a ring has not been configured yet, which lets debugfs and setup paths safely query optional rings. When WED is disabled, inline stubs compile out WED registration and make flow add return `-EINVAL`.

## State And Persistence
The header defines state owned by `mtk_wed.c`; it does not allocate directly. `mtk_wed_hw` persists across WLAN attaches until `mtk_wed_exit`. The attached `mtk_wed_device` pointer is a handoff to the WLAN owner and is cleared on detach. `num_flows` persists as the per-hardware WED offload reference count.

## Dependencies And Integration Points
It depends on the public MediaTek WED SoC header, debugfs, regmap, netdevice, and `mtk_wed_regs.h`. Ethernet code uses it to register WED hardware and call reset hooks. PPE offload uses `struct mtk_wdma_info` and `mtk_wed_flow_add/remove`. Debugfs uses raw register access helpers. The public `mtk_soc_wed_ops` path in external WLAN drivers depends on the behavior implemented behind these declarations.

## Risks
Because accessors hide missing ring pointers by returning zero, diagnostics can look like real zeroed hardware if a ring was never configured. Version helpers are simple equality checks, so future SoC versions require auditing `mtk_wed_is_v3_or_greater` assumptions. Build stubs must preserve call-site semantics; returning `-EINVAL` for flow add is important for offload cleanup paths. `mtk_wed_hw` lifetime is protected externally by `hw_lock` and RCU publication, not by the header itself.

## Test Signals
Build with WED enabled and disabled. With WED disabled, Ethernet should probe and TC offload should gracefully reject WED paths. With WED enabled, debugfs register access should reflect configured rings, WDMA info should program WED flows, and attach/detach should leave `wed_dev` and flow counts consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed.h -->
