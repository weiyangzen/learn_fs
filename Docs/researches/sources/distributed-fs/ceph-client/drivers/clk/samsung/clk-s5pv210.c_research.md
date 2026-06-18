# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-s5pv210.c

Purpose: main CMU clock tree for Samsung S5PV210 and S5P6442.

Important APIs/types/functions: `__s5pv210_clk_init()`; DT entry points `s5pv210_clk_dt_init()` and `s5p6442_clk_dt_init()`; register-offset definitions; saved-register list; parent arrays; common and SoC-specific mux/divider/gate/fixed-rate/fixed-factor tables; PLL descriptors; legacy aliases.

Control flow: DT init maps the CMU base and calls the shared initializer with a SoC selector. The initializer registers early `fin_pll`, chooses S5PV210 or S5P6442 tables, registers common clocks, aliases, sleep-save state, publishes the provider, and logs major rates.

State and persistence behavior: static `reg_base`; register state for PLL/source/mask/divider/gate/output registers; suspend persistence through `s5pv210_clk_regs` and Samsung common sleep code.

Dependencies/integration points: `dt-bindings/clock/s5pv210.h`, Samsung common clock helpers, OF mapping, and consumers such as audio/display/MMC/USB blocks.

Risks: large literal tables can break DT IDs or parent names; S5P6442 has different fixed rates and available parents; the local source includes a duplicated `MOUT_D1SYNC` mux entry.

Test signals: boot both compatible strings, inspect provider slots and `clk_summary`, verify APLL/MPLL/EPLL/VPLL rates, confirm peripheral consumers resolve clocks, and run suspend/resume.
