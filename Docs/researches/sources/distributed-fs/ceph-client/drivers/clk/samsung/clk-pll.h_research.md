# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-pll.h

Purpose: shared Samsung PLL type and rate-table contract used by SoC descriptors and the common PLL implementation.

Important APIs/types/functions: `enum samsung_pll_type`; `struct samsung_pll_rate_table`; rate construction/validation macros `PLL_RATE`, `PLL_VALID_RATE`, `PLL_FRACO_RATE`, `PLL_FRACO_VALID_RATE`, `PLL_35XX_RATE`, `PLL_36XX_RATE`, `PLL_4508_RATE`, `PLL_4600_RATE`, `PLL_4650_RATE`, and `PLL_A9FRACO_RATE`.

Control flow: no runtime flow. The header creates compile-time descriptor data consumed by `clk-pll.c` through `struct samsung_pll_clock`.

State and persistence behavior: no runtime storage; constant tables persist in kernel image or init sections. Registration code expects tables to be descending and zero-terminated.

Dependencies/integration points: included by Samsung common `clk.h` and PLL/SoC files; relies on kernel bit/compile-time assertion helpers.

Risks: wrong reference frequency or fractional shift creates wrong output rates or compile-time failures. The descending-order requirement is semantic, not enforced except by runtime behavior in `samsung_pll_determine_rate()`.

Test signals: compile SoC tables using validation macros, review table ordering/sentinels, and compare exposed CCF rates against hardware manuals.
