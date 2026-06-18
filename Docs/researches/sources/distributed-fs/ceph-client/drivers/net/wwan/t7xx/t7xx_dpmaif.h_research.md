# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.h

Purpose: declares DPMAIF hardware-facing constants, queue counts, interrupt enums, queue property structures, initialization parameters, and exported register-layer APIs.

Important APIs/types: `DPMAIF_RXQ_NUM` is 2 and `DPMAIF_TXQ_NUM` is 5. `struct dpmaif_isr_en_mask` tracks enabled interrupt masks. `struct dpmaif_ul` and `struct dpmaif_dl` store hardware queue state and DMA base/counts. `struct dpmaif_hw_info` owns device pointer, PCIe register base, queue arrays, and masks. `struct dpmaif_hw_params` passes software-allocated DRB/BAT/frag/PIT DMA addresses into hardware init. `enum dpmaif_hw_intr_type` gives HIF code semantic interrupt types.

Control flow and state: this header forms the boundary between DPMAIF HIF code and low-level MMIO implementation. HIF allocates rings, fills `dpmaif_hw_params`, calls hardware init, and later uses exported functions to add/release descriptors and unmask interrupts.

Dependencies and integration points: depends on Linux bit/type macros and `t7xx_reg.h` constants indirectly through implementation. It is included by HIF DPMAIF TX/RX and orchestration code.

Risks and test signals: queue-count mismatches, interrupt type mismatches, and constants like PIT sequence value or DRB word size can break datapath operation. Build all DPMAIF users and test queue init, interrupt decoding, and descriptor-count updates on hardware.
