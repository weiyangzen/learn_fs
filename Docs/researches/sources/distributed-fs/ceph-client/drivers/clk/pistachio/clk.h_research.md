# sources/distributed-fs/ceph-client/drivers/clk/pistachio/clk.h

Purpose: Defines Pistachio clock descriptor structures, construction macros, provider state, and shared registration function declarations.

Important APIs, types, and functions: Structures include `pistachio_gate`, `pistachio_mux`, `pistachio_div`, `pistachio_fixed_factor`, `pistachio_pll_rate_table`, `pistachio_pll`, and `pistachio_clk_provider`. Macros `GATE`, `MUX`, `DIV`, `DIV_F`, `FIXED_FACTOR`, `PLL`, and `PLL_FIXED` build descriptor arrays. Function declarations expose provider allocation, registration, PLL registration, and critical force-enable helpers.

Control flow: Descriptor macros are used by `clk-pistachio.c` to build static topology tables. Helper declarations are implemented in `clk.c` and `clk-pll.c`.

State and persistence: The header owns no runtime state but defines `pistachio_clk_provider`, whose instances hold the mapped base and one-cell data.

Dependencies and integration points: Depends on Linux CCF types and binding IDs supplied by includers. It is private to the Pistachio clock directory.

Risks: Macros hide field ordering and default flags; mistakes in macro arguments can create wrong clock IDs or parents with little compile-time protection. `MUX` calculates parent count from the array, so arrays must remain in scope as `__initconst` until registration.

Test signals: Build tests should catch structure signature drift. Runtime provider inspection should verify descriptor IDs map to expected binding IDs and parent names.
