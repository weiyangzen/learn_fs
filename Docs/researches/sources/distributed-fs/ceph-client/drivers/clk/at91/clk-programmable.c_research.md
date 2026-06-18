# sources/distributed-fs/ceph-client/drivers/clk/at91/clk-programmable.c

Purpose: provider for AT91 programmable clocks (`PCK0..PCK7`) using PCKR CSS and prescaler fields.

Important APIs and data: `at91_clk_register_programmable()` registers a programmable clock with layout-specific CSS/prescaler behavior. Layout constants cover RM9200, SAM9G45, and SAM9x5. `struct clk_programmable` stores id, regmap, layout, optional mux table, and PM state.

Control flow: recalc reads `PCKR(id)` and divides parent by either direct divisor (`pres + 1`) or power-of-two shift. determine-rate searches all parents and legal prescalers for the closest rate not above the request. set_parent maps parent index to hardware CSS including the special RM9200 `CSSMCK_MCK` path. set_rate validates direct or power-of-two divisors and writes prescaler bits.

State and persistence: parent/rate are stored on save and restored by calling set_parent then set_rate. Hardware holds the live PCKR values.

Dependencies and integration: SoC setup files instantiate two or three PCKs; DT compat creates child node providers. It depends on regmap and common-clock rate/parent gates.

Risks: parent selection logic is layout-sensitive; direct prescaler layouts can accept many divisors while legacy layouts require powers of two; no ready wait is done here, system clocks for PCK IDs perform readiness waits. Test signals include PCK parent/rate selection, PCK system gate readiness, and suspend/resume restoration of parent plus prescaler.
