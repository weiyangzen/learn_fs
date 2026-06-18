# sources/distributed-fs/ceph-client/drivers/media/i2c/aptina-pll.h

Purpose: Public helper header for Aptina sensor PLL calculation used by media I2C sensor drivers.

Important APIs/types/functions: `struct aptina_pll` contains input fields `ext_clock` and `pix_clock` plus calculated output fields `n`, `m`, and `p1`. `struct aptina_pll_limits` describes allowed external, internal, output, and pixel clocks plus min/max ranges for `N`, `M`, and `P1`. `aptina_pll_calculate()` is declared as the only exported API.

Control flow: No executable control flow. The header defines the caller contract: populate clocks and limits, call the calculator, and consume the written divider/multiplier fields on success.

State/persistence: No state of its own. The state boundary is the caller-owned `struct aptina_pll`, which acts as both input and output.

Dependencies/integration: Forward declares `struct device` for logging and avoids pulling in full device headers. Used with the GPL-exported implementation in `aptina-pll.c`.

Risks: Field units are implicit Hertz-style integer frequencies; callers must use consistent units. There is no type-level separation between input and output fields, so callers can accidentally reuse a partially mutated `struct aptina_pll` after an error.

Test signals: Compile users against this header and verify ABI expectations by checking that successful calls update all three output fields and failures do not get programmed into hardware by the caller.
