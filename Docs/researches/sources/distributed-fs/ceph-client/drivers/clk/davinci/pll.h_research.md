# sources/distributed-fs/ceph-client/drivers/clk/davinci/pll.h

Purpose: declares shared DaVinci PLL metadata structures, quirk flags, SYSCLK/OBSCLK descriptors, registration APIs, and DA850 platform callbacks.

Important APIs/types/functions: `davinci_pll_clk_info` captures PLL register masks, multiplier limits, output limits, CFGCHIP unlock information, and `PLL_*` flags. `davinci_pll_sysclk_info` describes SYSCLKn name, parent, ID, ratio width, and `SYSCLK_*` flags. `SYSCLK()` is the descriptor macro used by DA850. `davinci_pll_obsclk_info` describes OBSCLK mux parents and hardware selection table.

Control flow: no executable control flow. The header defines the contracts that platform data files pass into `pll.c` registration functions and OF initialization.

State and persistence: no runtime state. The structs are static descriptor data used to create persistent registered clocks at boot/probe time.

Dependencies and integration points: includes bitops, common clock provider interfaces, OF, regmap, and types. It links generic `pll.c` with DA850 descriptors and callbacks (`da850_pll1_init()`, `of_da850_pll0_init()`, `of_da850_pll1_init()`).

Risks: flag combinations encode hardware behavior; wrong flags can disable critical dividers, treat writable dividers as fixed, or compute PLL rates incorrectly. The `SYSCLK()` macro stringifies symbol names, so renaming descriptors changes clock names visible to consumers.

Test signals: compile-time coverage for descriptor users, boot-time verification that generated names match DT/clkdev consumers, and rate tests confirming flag combinations produce expected parent propagation and divider behavior.
