# Research: sources/distributed-fs/ceph-client/drivers/net/wwan/t7xx/t7xx_dpmaif.c

Purpose: implements the DPMAIF hardware register layer for t7xx data path queues, covering initialization, interrupt decoding, DL BAT/PIT/fragment setup, UL DRB setup, queue enable/disable, and hardware index updates.

Important APIs/functions: `t7xx_dpmaif_hw_init()` resets/configures DPMAIF, initializes interrupts, stores queue properties, configures DL and UL queues, and marks UL/DL init done. `t7xx_dpmaif_hw_get_intr_cnt()` reads UL/DL interrupt status, masks queue-done interrupts before bottom halves, clears status, and fills `dpmaif_hw_intr_st_para`. `t7xx_dpmaif_ul_update_hw_drb_cnt()` notifies hardware of new TX descriptors. `t7xx_dpmaif_dl_snd_hw_bat_cnt()`, `_frg_cnt()`, and `t7xx_dpmaif_dlq_add_pit_remain_cnt()` return released DL buffers/PIT entries to hardware. Stop functions disable UL/DL queues and poll idle/sync.

Control flow and state: `struct dpmaif_hw_info` holds MMIO base, per-queue base addresses/counts, and interrupt enable masks. Initialization programs shared BAT/frag BAT and per-DLQ PIT tables, then UL DRB queues. Interrupt handling classifies status into semantic events consumed by `t7xx_hif_dpmaif.c`.

Dependencies and integration points: depends on `t7xx_reg.h`, `t7xx_dpmaif.h`, bitfield helpers, IO polling, and the HIF DPMAIF layer.

Risks and test signals: readiness polling timeouts, interrupt mask polarity, shared BAT assumptions, hardware/software index mismatch, and queue stop loops are key risks. Test modem boot data-path init, RX/TX interrupt delivery, PIT/BAT refill, suspend/resume, and error interrupts.
