# sources/distributed-fs/ceph-client/drivers/clk/ti/mux.c

Purpose: TI mux clock implementation for standalone mux clocks and composite mux components. It reads/writes mux selector fields, supports legacy index encodings, latches updates, and saves/restores selected parents.

Important APIs/types/functions: exported `ti_clk_mux_ops`, `of_mux_clk_setup()`, `ti_clk_build_component_mux()`, and `of_ti_composite_mux_clk_setup()`. Runtime ops are `ti_clk_mux_get_parent()`, `ti_clk_mux_set_parent()`, context save, and context restore.

Control flow: standalone setup requires at least two parents, fills parent names, parses register/shift and optional latch bit, handles one-based indices and set-rate-parent, computes a selector mask from parent count, registers the mux, and adds an OF provider. Runtime get reads and decodes the selector through an optional table, bit index, or one-based index. Set encodes the parent index, writes with optional hiword mask support, and pulses latch.

State and persistence: mux structures hold register location, mask, shift, latch, flags, optional table, and saved parent. Hardware selector fields persist; context callbacks restore them.

Dependencies/integration: uses `ti_clk_get_reg_addr()`, `ti_clk_latch()`, CCF mux rate determination, and composite registration through `ti_clk_add_component()`.

Risks: the code comments note ambiguity between bitwise and numeric selector encodings. `CLK_MUX_INDEX_BIT` encoding uses `ffs(index)`, which is sensitive to zero-based assumptions. Parent count determines mask width, so holes require tables.

Test signals: parent switching for zero-based, one-based, table, and bit encodings; latch behavior; save/restore selected parent; and composite mux registration.
