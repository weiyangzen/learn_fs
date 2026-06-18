<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_debugfs.c

## Purpose
`mtk_wed_debugfs.c` creates debugfs diagnostics for WED hardware instances. It provides formatted register dumps for TX, RX, AMSDU, route queue manager, and RRO/indirect-command paths, plus a raw `regidx`/`regval` pair for direct WED register reads and writes. The file is primarily an observability and bring-up aid for complex WED/WDMA/WPDMA interactions.

## Important APIs And Functions
`struct reg_dump` describes one dump item: name, offset, register source type, base/ring index, and mask. Macros such as `DUMP_WED`, `DUMP_WDMA`, `DUMP_WPDMA_TX_RING`, `DUMP_WPDMA_RX_RING`, `DUMP_WED_RING`, and `DUMP_WED_MASK` build static register lists. `dump_wed_regs` selects the right accessor based on type and prints values with `print_reg_val`. Show functions are `wed_txinfo_show`, `wed_rxinfo_show`, `wed_amsdu_show`, `wed_rtqm_show`, and `wed_rro_show`. `mtk_wed_reg_get/set` implement raw register access. `mtk_wed_hw_add_debugfs` creates the per-instance directory and files.

## Control Flow
At hardware registration, `mtk_wed_hw_add_debugfs` creates `wed%d`, `regidx`, `regval`, and `txinfo`. For non-v1 hardware it adds `rxinfo`; for v3 or newer it also adds `amsdu`, `rtqm`, and `rro`. Each read obtains `hw` from `s->private`, checks `hw->wed_dev`, and dumps static register arrays. `wed_rxinfo_show` combines common RX registers with v2 or v3 route/RRO-specific arrays. Raw register access writes or reads `hw->debugfs_reg` through the WED regmap.

## State And Persistence
Debugfs state is the directory pointer in `hw->debugfs_dir` and the mutable `hw->debugfs_reg` selected by users. The dump files read live WED, WDMA, and WLAN WPDMA ring registers; they do not cache values. `regval` can mutate hardware state, so it is diagnostic control state rather than pure observation.

## Dependencies And Integration Points
The file depends on seq_file/debugfs, public WED structs, private WED helpers, and WED register macros. It uses `wed_r32`, `wdma_r32`, `wpdma_tx_r32`, `wpdma_rx_r32`, and `wpdma_txfree_r32`, so it reflects the same configured ring pointers created by `mtk_wed.c`. `mtk_wed_exit` removes the directory.

## Risks
`debugfs_create_file_unsafe` and raw `regval` writes are powerful and can destabilize hardware if used incorrectly. Dumps are unsynchronized with attach/detach and live reset beyond checking `wed_dev`, so values may be transient. Several dump labels or repeated counters appear copy-pasted, which can mislead manual diagnosis. Reading unconfigured WPDMA rings returns zero through helper stubs, which may be confused with valid zero register values.

## Test Signals
With debugfs enabled, verify `wed0/txinfo` appears for all WED versions, `rxinfo` for v2/v3, and `amsdu`, `rtqm`, `rro` for v3. During traffic, TX/RX ring indexes and MIB counters should move. During reset, dump files should not crash. Raw `regidx/regval` should read a known harmless register before any write testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_debugfs.c -->
