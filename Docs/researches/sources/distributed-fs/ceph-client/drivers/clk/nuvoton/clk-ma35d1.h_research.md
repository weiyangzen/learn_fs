# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1.h

Purpose: Declares the MA35D1 private helper interface shared between the main clock driver, PLL helper, and ADC divider helper.

Important APIs, types, and functions: Declares `ma35d1_reg_clk_pll()` for registering PLL clocks and `ma35d1_reg_adc_clkdiv()` for registering the special ADC divider. Both return `struct clk_hw *` for insertion into the main one-cell provider array.

Control flow: `clk-ma35d1.c` includes this header and calls the helpers while populating `hws[]`. The helper implementation files export the symbols GPL-only.

State and persistence: No state is owned by the header. It defines function signatures that pass device lifetime, parent clock hardware, MMIO base/register, locking, and encoding metadata into helper objects.

Dependencies and integration points: Depends on forward declarations from Linux CCF and device headers included by consumers. It is private to the Nuvoton clock directory.

Risks: The `ma35d1_reg_adc_clkdiv()` parameter name `mask_bit` implies a bit index, while call sites may pass masks; the header does not clarify semantics. Signature drift would break all MA35D1 object integration.

Test signals: Build tests should catch helper signature mismatches. Code review should verify every helper caller passes register and mask/bit parameters with the expected semantics.
