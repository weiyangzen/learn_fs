# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-cpugear.c

Purpose: UniPhier CPU gear clock implementation. It is a mux-like clock that changes CPU gear selection through a set register and update handshake.

Important APIs/types/functions: `uniphier_clk_register_cpugear()`, `uniphier_clk_cpugear_set_parent()`, `uniphier_clk_cpugear_get_parent()`, and `uniphier_clk_cpugear_ops`. Runtime state is in `struct uniphier_clk_cpugear`.

Control flow: registration allocates device-managed state, fills CCF init data with parent names and `CLK_SET_RATE_PARENT`, stores regmap/regbase/mask, and registers the hw. Set-parent writes the requested index to `SET`, asserts the `UPD` bit, then polls until hardware clears it. Get-parent reads `STAT`, masks the selector, and validates it against parent count.

State and persistence: regmap-backed hardware registers hold selected gear. Driver state stores regbase and selector mask only.

Dependencies/integration: used by system clock data for LD11/LD20/PXS3/NX1 CPU clocks; depends on regmap polling and parent factor clocks.

Risks: poll timeout is one microsecond total as written, so slow hardware update could fail. The selector value is assumed to be directly represented by `mask` without shifting.

Test signals: switch CPU gear parents, confirm `UPD` clears, validate reported parent against `STAT`, and test parent-rate propagation.
