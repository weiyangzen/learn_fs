# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-fh.h

Purpose: Defines iwlwifi Flow Handler, TFH/RFH, RX DMA, TX DMA, TFD, byte-count-table, and IMR DMA hardware ABI constants plus descriptor structures used by the PCIe transport.

Important APIs and types: `FH_MEM_CBBC_QUEUE()` selects generation-specific TFD circular-buffer base registers. `iwl_get_dma_hi_addr()` extracts 36-bit DMA address high bits. `struct iwl_rb_status`, `struct iwl_tfd_tb`, `struct iwl_tfh_tb`, `struct iwl_tfd`, `struct iwl_tfh_tfd`, and `struct iwl_bc_tbl_entry` describe host/firmware shared DMA memory. Macros cover keep-warm memory, RX status/write pointers, RFH multi-queue tables, TFH transfer mode, service DMA, queue sizes, and TX/RX idle bits.

Control flow: This header has no executable flow beyond inline address helpers. Runtime code uses its constants to allocate DMA rings, program RX status buffers, post RBD write indexes, configure RX buffer sizes, program TX TFD tables, start service DMA transfers, and poll idle/error status during stop/reset.

State and persistence: It owns no state, but defines persistent hardware-visible state: descriptor rings in host DRAM, RX status writeback layout, TFD table addresses, keep-warm buffer address, and byte-count tables. Alignment, wrap, and size comments are part of the hardware contract.

Dependencies and integration points: Depends on `iwl-trans.h`, Linux bit helpers, DMA address types, and cfg values such as `trans->mac_cfg->gen2`. It is consumed by PCIe RX/TX queue setup, FH dumps in `iwl-io.c`, transport memory programming, and scheduler code.

Risks: Register offsets and bit masks are silicon ABI. Wrong queue range selection, DMA high bits, descriptor packing, or RX write-index granularity can corrupt DMA. Pre-gen2 and gen2 register maps differ sharply. RX ring fullness leaves unusable entries, and TX descriptors have hardware limits that callers must respect.

Test signals: Compile all PCIe generation paths, bring up RX/TX traffic on legacy and gen2 devices, validate RX queue wrap and idle polling, verify TFD DMA addresses above 4GB, exercise service DMA/IMR copy paths, and inspect FH/RFH dumps during firmware error collection.
