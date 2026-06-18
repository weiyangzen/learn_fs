# sources/distributed-fs/ceph-client/drivers/clk/uniphier/clk-uniphier-peri.c

Purpose: UniPhier peripheral clock data for UART, I2C/FI2C, SCSSI, and MCSSI gates.

Important APIs/types/functions: exports `uniphier_ld4_peri_clk_data[]` and `uniphier_pro4_peri_clk_data[]`. Macros define gate entries for UART channels, common/individual I2C, fast I2C, SCSSI, and MCSSI.

Control flow: core selects the array by peripheral compatible. LD4-style data gates UART0-3, an internal `i2c-common` gate, I2C0-4 derived from it, and SCSSI0. Pro4-style data gates UART0-3, FI2C0-6, SCSSI0-3, and MCSSI.

State and persistence: static table only. Runtime state is generated gate clocks and syscon register bits at `0x20`/`0x24`.

Dependencies/integration: parent clocks are expected from system clock data (`uart`, `i2c`, `spi`). Gate helper writes the described syscon bits.

Risks: index assignments are ABI-visible to DT consumers. Shared parent/common gates mean disabling a common parent can affect multiple children if consumer usage is wrong.

Test signals: peripheral driver clock gets by index/name, gate bit toggles for UART/I2C/SPI channels, and correct parent rate inheritance.
