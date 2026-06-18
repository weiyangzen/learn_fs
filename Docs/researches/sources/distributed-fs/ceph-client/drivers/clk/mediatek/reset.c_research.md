# sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.c

Purpose: `reset.c` registers reset-controller support for MediaTek clock-controller blocks. It supports two hardware styles: simple read/modify/write reset bits and set/clear register pairs.

Important APIs and functions: the exported entry point is `mtk_register_reset_controller_with_dev()`. Internal operations include `mtk_reset_assert()`, `mtk_reset_deassert()`, `mtk_reset()`, set/clear variants, and `reset_xlate()` for optional DT reset-index remapping.

Control flow: registration validates the descriptor, selects `reset_control_ops` based on `desc->version`, resolves the clock-controller regmap from the device node, allocates `struct mtk_clk_rst_data` with devm, fills `reset_controller_dev`, and registers it with `devm_reset_controller_register()`. Runtime assert/deassert calculates the bank offset from `id / RST_NR_PER_BANK` and bit from `id % RST_NR_PER_BANK`. Simple mode uses `regmap_update_bits()` with either all ones for assert or zero for deassert. Set/clear mode writes the bit to the bank offset, adding `0x4` for deassert.

State and persistence: reset state is entirely in hardware registers. The in-memory controller data and registration are devm-scoped to the device. No persistent data is stored.

Dependencies and integration points: the code depends on Linux reset-controller APIs, regmap syscon lookup, platform device infrastructure, and `reset.h`. `clk-mtk.c` invokes it when a clock descriptor includes `rst_desc`, allowing one clock-controller node to provide both clocks and resets.

Risks: the simple mode uses `regmap_update_bits()` with `val = ~0` for assert, relying on the mask to constrain the write. Descriptor bank offsets and optional `rst_idx_map` must be correct or reset consumers will manipulate the wrong lines. `reset_xlate()` validates against both `nr_resets` and `rst_idx_map_nr`, but only when a map is present; direct mode exposes `rst_bank_nr * 32` linear resets.

Test signals: DT reset consumers should acquire, assert, deassert, and pulse expected reset lines. Probe logs should show no unknown reset version or regmap lookup failures. Hardware validation can read reset registers before and after reset operations and verify mapped reset indexes match binding definitions.
