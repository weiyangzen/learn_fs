# sources/distributed-fs/ceph-client/drivers/clk/nuvoton/clk-ma35d1-pll.c

Purpose: Implements MA35D1 PLL clock hardware, including the special CAPLL SMIC format and generic integer, fractional, and spread-spectrum PLL formats for DDRPLL, APLL, EPLL, and VPLL.

Important APIs, types, and functions: `struct ma35d1_clk_pll` stores CCF hardware, clock id, mode, and CTL0/1/2 bases. `ma35d1_reg_clk_pll()` registers a PLL. `ma35d1_calc_smic_pll_freq()` and `ma35d1_calc_pll_freq()` recalculate rates from registers. `ma35d1_pll_find_closest()` searches valid input divider, feedback divider, and output divider combinations. `ma35d1_clk_pll_set_rate()`, `_recalc_rate()`, `_determine_rate()`, `_prepare()`, and `_unprepare()` implement CCF ops.

Control flow: The main driver registers CAPLL, DDRPLL, APLL, EPLL, and VPLL with modes parsed from DT. CAPLL and DDRPLL get fixed ops without set-rate; other PLLs can search, program CTL registers, and power up/down. Recalc dispatches by id and bypass bits return the parent rate.

State and persistence: PLL configuration persists in CTL registers. The in-memory object stores mode and register bases. Power-down state is tracked in CTL1 `PD` for generic PLLs; CAPLL has a different CTL0 layout for recalc.

Dependencies and integration points: Depends on dt-binding clock IDs, `<linux/bitfield.h>`, CCF, and MA35D1 register layout. The main driver supplies the parent `hxt` clock and base offsets.

Risks: `ma35d1_clk_pll_determine_rate()` calls the search but then overwrites `req->rate` with the current hardware rate instead of the found closest rate, which may make rate negotiation misleading. The set-rate path writes `PLL_CTL1_PD`, leaving the PLL powered down until prepare. CAPLL uses a different PD/BP layout but `ma35d1_clk_pll_is_prepared()` always reads CTL1, which is not valid for CAPLL; CAPLL avoids prepare ops via fixed ops. Search loops are large for fractional mode and can be expensive.

Test signals: Validate recalc against known register encodings for all PLL IDs and modes. For adjustable PLLs, test determine/set/prepare sequences and confirm requested rates converge. Confirm CAPLL/DDRPLL expose no set-rate ops. DT tests should cover valid `nuvoton,pll-mode` strings for all five PLLs.
