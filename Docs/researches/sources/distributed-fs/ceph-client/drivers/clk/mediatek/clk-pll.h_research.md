# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-pll.h

Purpose: `clk-pll.h` defines the descriptor and runtime structures for MediaTek PLL clocks and declares the common PLL operations implemented in `clk-pll.c`.

Important APIs and types: `struct mtk_pll_div_table` describes frequency thresholds for post-divider selection. Flags include `HAVE_RST_BAR`, `PLL_AO`, `PLL_PARENT_EN`, and `POSTDIV_MASK`. `struct mtk_pll_data` contains all hardware description fields: IDs, names, register offsets, enable masks, fenc status offset/bit, post-divider and PCW metadata, tuner metadata, optional init ops, PLL flags, fmin/fmax, divider table, parent name, set/clear registers, PLL enable bit, and PCW change bit. `struct mtk_clk_pll` stores resolved MMIO addresses, device pointer, `clk_hw`, and descriptor pointer.

Control flow: this header does not execute code except for `to_mtk_clk_pll()`. Its field layout drives the implementation: registration resolves offsets to MMIO pointers, prepare/unprepare consult flags and enable bits, rate calculation consults PCW fields and divider tables, and set/clear variants consult enable set/clear addresses and fenc fields.

State and persistence: descriptor instances are static SoC data. Runtime state is the allocated `struct mtk_clk_pll`, common clock registration state, and hardware PLL registers. No persistent storage exists.

Dependencies and integration points: it includes Linux clock-provider and type headers. It is used by normal PLL registration and by PLL frequency-hopping support, where `struct mtk_fh` embeds `struct mtk_clk_pll`.

Risks: many fields have default-by-zero semantics, such as `pll_en_bit`, `pcw_chg_bit`, `pcw_chg_reg`, and parent name. This is compact but makes descriptor review important because omission can be intentional or a bug. Register offsets are SoC-specific and untyped, so invalid offsets compile cleanly. Consumers must ensure ID values fit the onecell data array allocated by the parent clock driver.

Test signals: compile tests should cover all SoC descriptor initializers. Runtime checks should validate PLL parent names, rate rounding, lock/fenc status bits, always-on critical flags for `PLL_AO`, parent-enable behavior for `PLL_PARENT_EN`, and unregister cleanup under driver removal or probe failure.
