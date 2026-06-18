# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk.h

Purpose: central Samsung clock-driver descriptor and provider interface.

Important APIs/types/functions: `struct samsung_clk_provider`, alias/fixed/factor/mux/div/gate/PLL/CPU descriptors, register dump/cache structures, `struct samsung_cmu_info`, construction macros `ALIAS`, `FRATE`, `FFACTOR`, `MUX`, `DIV`, `GATE`, `PLL`, `CPU_CLK`, and prototypes for common registration/sleep/auto-gate helpers.

Control flow: no implementation, but SoC table files use these types/macros to feed `clk.c`, `clk-pll.c`, and CPU clock registration.

State and persistence behavior: describes provider state, onecell storage, register caches, and CMU save/suspend lists. Actual persistence is implemented by common code.

Dependencies/integration points: CCF, mod device table, regmap, `clk-pll.h`, and `clk-cpu.h`; this is the contract between Samsung SoC files and common helpers.

Risks: macro defaults such as `CLK_SET_RATE_NO_REPARENT` affect many clocks; `clk_data` must remain last for flexible allocation; the local `__GATE` macro contains a duplicated `.parent_name` initializer.

Test signals: compile all Samsung users with warnings, boot representative CMUs, verify DT binding IDs align with onecell indices, and inspect generated clock topology.
