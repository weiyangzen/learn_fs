
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/mac.h

Purpose: Declares RTL8192C MAC helper functions and RX descriptor/firmware-info structures used by CU TRX and hardware initialization code.

Important APIs/types: Defines LLT and beacon timing constants, prototypes for chip version, LLT, CAM keys, interrupts, QoS, EDCA/rate/retry/beacon/min-space helpers, `rtl92c_get_txdma_status()`, `rtl92c_map_hwqueue_to_fwqueue()`, and `rtl92c_translate_rx_signal_stuff()`. `struct rx_fwinfo_92c` captures PHY status bytes; `struct rx_desc_92c` documents RX descriptor bitfields.

Control flow: Header only. It creates the compile-time contract between `mac.c`, `hw.c`, `trx.c`, and the HAL ops in `sw.c`.

State and persistence: The declared functions read/write hardware MAC registers, CAM state, interrupt masks, and signal statistics. The RX structs describe DMA-delivered state.

Dependencies/integration: Included by CU MAC/TRX/HW/SW files. Uses mac80211 types, rtlwifi `rtl_stats`, descriptor queue enums, and hardware rate definitions inherited from surrounding includes.

Risks: Struct bitfields mirror hardware and should not be used as a portable serialization mechanism when le32 helpers are available. Prototype/order drift with `mac.c` or common users breaks the module. The `rtl92c_init_edca_param()` declaration parameter names differ in order from the implementation names, so callers must rely on position.

Test signals: Build coverage, RX descriptor parsing checks, and HAL op invocation tests for each declared initializer.
