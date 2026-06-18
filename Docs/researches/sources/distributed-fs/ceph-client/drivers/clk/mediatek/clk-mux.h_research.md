# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mux.h

Purpose: `clk-mux.h` declares the descriptor format and construction macros for MediaTek mux clocks backed by set/clear/update registers, gate bits, fenc status monitoring, optional indexed parent values, and hardware voter support.

Important APIs and types: `struct mtk_mux` stores IDs, names, parent arrays, optional hardware parent index table, offsets for mux/set/clear/update/HWV/fenc registers, bit shifts and widths, selected `clk_ops`, and parent count. The header declares the four mux `clk_ops`, `mtk_clk_register_muxes()`, `mtk_clk_unregister_muxes()`, `struct mtk_mux_nb`, `to_mtk_mux_nb()`, and `devm_mtk_clk_mux_notifier_register()`.

Control flow: macros encode which runtime operations the implementation will use. `MUX_CLR_SET_UPD` creates a parent-only mux. `MUX_GATE_CLR_SET_UPD*` adds gate control. `MUX_GATE_FENC_CLR_SET_UPD*` adds fenc status polling. `MUX_GATE_HWV_FENC_CLR_SET_UPD*` routes enable/disable through hardware voter registers and fenc status. Indexed variants decouple logical parent indexes from hardware selector values.

State and persistence: the header contributes static, compile-time mux descriptors. Runtime state, such as the selected parent, gate state, fenc status, and `reparent` tracking, is maintained by hardware registers and the `struct mtk_clk_mux` allocated by `clk-mux.c`.

Dependencies and integration points: it depends on Linux notifier, spinlock, and type declarations. It is included by MediaTek SoC clock table files and the implementation. `struct mtk_mux_nb` links common clock rate-change notifiers with mux ops so a SoC can switch away from a PLL while the PLL is being retuned.

Risks: the macros are dense and parameter order is register-sensitive, so a shift or offset typo silently targets the wrong bit. `GATE_CLR_SET_UPD_FLAGS_INDEXED()` uses `ARRAY_SIZE(_paridx)` as `num_parents`, which assumes the index table length matches the parent-name array. Hardware voter descriptors require valid HWV offsets and a `mediatek,hardware-voter` phandle at runtime.

Test signals: build coverage catches missing ops symbols; runtime tests should check all descriptor-created clocks appear in `clk_summary`, parent indexes match hardware selectors, gate bits and fenc bits reflect enable state, and notifier users restore the original parent after successful and aborted PLL rate changes.
