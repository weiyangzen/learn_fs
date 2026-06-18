# sources/distributed-fs/ceph-client/drivers/clk/rockchip/softrst.c

Purpose: common Rockchip reset-controller implementation used by SoC-specific reset LUT files and simple contiguous reset banks.

Important APIs/types/functions: `struct rockchip_softrst`, `rockchip_softrst_assert()`, `rockchip_softrst_deassert()`, `rockchip_softrst_ops`, and exported `rockchip_register_softrst_lut()`. `rockchip_register_softrst()` is an inline wrapper in `clk.h`.

Control flow: registration allocates a reset-controller object, records optional LUT, base, register count, flags, and per-register bit count, then calls `reset_controller_register()`. Assert/deassert optionally remap `id = lut[id]`, compute `bank = id / num_per_reg` and `offset = id % num_per_reg`, then either write high-word mask values or perform locked read/modify/write.

State and persistence: one heap object per reset controller stores mapping and spinlock. Hardware CRU reset registers hold actual reset state. High-word mode treats each register as 16 reset bits; non-high-word mode treats each as 32 bits.

Dependencies and integration: Linux reset-controller framework, MMIO helpers, spinlocks, and Rockchip clock headers. SoC clock init calls this after mapping CRU registers.

Risks: LUT bounds are trusted by reset core via `nr_resets`; sparse C arrays with omitted IDs may contain zero entries. Non-high-word mode requires locking to avoid clobbering unrelated bits. High-word mode depends on Rockchip write-mask semantics and does not read back state.

Test signals: reset controller appears in DT provider lookup, assert/deassert writes expected values, concurrent reset users do not corrupt non-high-word registers, and invalid IDs are rejected by reset core based on `nr_resets`.
