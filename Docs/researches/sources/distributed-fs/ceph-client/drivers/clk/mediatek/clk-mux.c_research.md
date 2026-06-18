# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.c

Purpose: `clk-mux.c` implements MediaTek mux clocks that use set/clear/update registers, optional gate bits, optional fenc status polling, and optional hardware voter registers. It also provides a devm clock notifier that temporarily switches a mux to a bypass parent around PLL parent-rate changes.

Important APIs and functions: `struct mtk_clk_mux` wraps `clk_hw`, register maps, source descriptor, optional lock, and a `reparent` flag. Exported `clk_ops` are `mtk_mux_clr_set_upd_ops`, `mtk_mux_gate_clr_set_upd_ops`, `mtk_mux_gate_fenc_clr_set_upd_ops`, and `mtk_mux_gate_hwv_fenc_clr_set_upd_ops`. Exported registration functions are `mtk_clk_register_muxes()` and `mtk_clk_unregister_muxes()`. `devm_mtk_clk_mux_notifier_register()` installs the bypass notifier.

Control flow: enable paths clear the gate bit through `clr_ofs`; fenc enable additionally polls `fenc_sta_mon_ofs`; hardware-voter enable writes the HWV set register, waits for HWV status, then waits for fenc status. Disable paths either write normal set registers or hardware-voter clear registers. Parent reads mask and shift `mux_ofs`, translating through `parent_index` if present. Parent changes read/modify the mux value, write clear and set masks, and trigger `upd_ofs` when `upd_shift >= 0`; if the clock is gated, `reparent` causes the update bit to be rewritten when the gate is later enabled.

State and persistence: runtime state is only the hardware register values and the in-memory `reparent` boolean. Clock registration state is stored in the onecell `hws[]` table and released by `mtk_clk_unregister_muxes()`. No persistent storage is used.

Dependencies and integration points: the driver depends on Linux regmap, common clock framework mux helpers, spinlocks, syscon lookup from device tree, and `mtk_clk_get_hwv_regmap()`. It plugs into the common MediaTek descriptor path in `clk-mtk.c`; SoC tables from `clk-mux.h` select the appropriate ops.

Risks: `mtk_clk_register_mux()` returns early if HWV is required but no HWV regmap exists without freeing the just-allocated `clk_mux`, which appears to leak memory on that error path. Parent index tables must map every hardware value correctly; otherwise `get_parent()` can return an impossible index. Poll timeouts are short and atomic, so wrong fenc/HWV offsets can fail probe or enable under interrupt-disabled contexts. Lockless operation uses sparse annotations, so shared register users must provide a real spinlock when needed.

Test signals: validate parent selection through `clk_set_parent()` and `clk_get_parent()`, enable/disable state through fenc and non-fenc muxes, deferred probe/error behavior when hardware-voter phandles are missing, and PLL rate-change notifier behavior by observing temporary bypass selection during `PRE_RATE_CHANGE` and restoration on `POST_RATE_CHANGE` or `ABORT_RATE_CHANGE`.
