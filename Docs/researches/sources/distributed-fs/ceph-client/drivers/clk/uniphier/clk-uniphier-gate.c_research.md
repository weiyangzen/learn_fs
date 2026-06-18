# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-gate.c

Purpose: UniPhier regmap-backed gate clock implementation.

Important APIs/types/functions: `uniphier_clk_register_gate()`, `uniphier_clk_gate_enable()`, `uniphier_clk_gate_disable()`, `uniphier_clk_gate_is_enabled()`, and `uniphier_clk_gate_ops`. State is `struct uniphier_clk_gate`.

Control flow: registration allocates state, sets parent and `CLK_SET_RATE_PARENT` when present, stores regmap/register/bit from data, and registers CCF hw. Enable/disable update one bit via `regmap_write_bits()`. `is_enabled()` reads the register and tests the bit.

State and persistence: hardware gate bits persist in syscon registers; driver state stores location metadata.

Dependencies/integration: used by UniPhier system, MIO, peripheral, and SoC-glue data. Depends on syscon regmap from the parent device.

Risks: disable and is_enabled cannot return regmap errors through void/u8 CCF interfaces, so they warn and continue. Parentless gates are allowed for root-controlled blocks.

Test signals: enable/disable every exposed gate index, check register bits, validate warning paths with regmap failure injection, and verify parent rate propagation when a parent exists.
