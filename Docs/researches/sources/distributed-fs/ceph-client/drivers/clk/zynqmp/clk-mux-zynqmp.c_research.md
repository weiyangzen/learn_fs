# sources/distributed-fs/ceph-client/drivers/clk/zynqmp/clk-mux-zynqmp.c

Purpose: implements firmware-controlled parent selection for ZynqMP mux clock nodes.

Important APIs/types/functions: `struct zynqmp_clk_mux` carries `clk_hw`, mapped mux flags, and firmware `clk_id`. `zynqmp_clk_register_mux()` registers either writable or read-only mux operations. `zynqmp_clk_mux_get_parent()` and `zynqmp_clk_mux_set_parent()` call PM firmware.

Control flow: CCF asks for the active parent or requests a parent switch; the driver forwards the request to `zynqmp_pm_clock_getparent()` or `zynqmp_pm_clock_setparent()`. Rate determination uses `__clk_mux_determine_rate_closest`.

State and persistence: parent selection persists in firmware-controlled clock state. The Linux object stores the firmware clock id and decoded flags.

Dependencies and integration points: used by `clkc.c` for `TYPE_MUX` topology nodes. Depends on CCF mux semantics and the ZynqMP PM clock parent APIs.

Risks: the read-only check tests `nodes->type_flag & CLK_MUX_READ_ONLY`, while type flags are decoded from ZynqMP-specific constants; this relies on bit compatibility with the generic flag. On get-parent failure, returning `num_parents` intentionally forces an invalid index. The mapped `mux->flags` are stored but not supplied to a generic mux helper.

Test signals: parent enumeration, `clk_set_parent()` success/failure, read-only mux behavior, and firmware-returned invalid parent indexes.
