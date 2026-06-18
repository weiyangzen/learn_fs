# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c

Purpose: implements SpacemiT MIX clock operations, combining CCF gate, fixed factor, mux, divider, and mux/div/gate variants with optional hardware frequency-change handshakes.

Important APIs and control flow: gate callbacks `ccu_gate_enable()`, `ccu_gate_disable()`, and `ccu_gate_is_enabled()` update or test `gate.mask` with optional inverted semantics. Factor clocks return `parent_rate * mul / div` and accept set-rate as a no-op. Divider clocks read/write a raw divider field and use CCF `divider_recalc_rate()`. Mux clocks read/write parent index fields. `ccu_mix_calc_best_rate()` scans every available parent and divider value, choosing the closest rate; determine-rate returns the selected parent/rate, set-rate writes the divider field, and mux/div set-parent or set-rate calls `ccu_mix_trigger_fc()` when `reg_fc` is configured. FC polling sets `mask_fc` then waits for hardware to clear it with `regmap_read_poll_timeout_atomic()`.

State and persistence behavior: persistent state is the hardware register contents for gate, mux, divider, and FC bits. Static `struct ccu_mix` instances contain factor/gate/div/mux metadata and an embedded common object whose regmap is installed at probe. No cached rate or parent state is kept in software.

Dependencies and integration points: depends on CCF gate/mux/div semantics, `divider_recalc_rate()`, regmap polling, and definitions from `ccu_mix.h`. SoC files instantiate different exported `clk_ops` combinations: gate-only, factor, mux, div, factor-gate, mux-gate, div-gate, mux-div, and mux-div-gate.

Risks and test signals: risks include `abs()` on unsigned-long rate deltas, divider encoding assumptions where hardware field value `n` means divide by `n + 1`, missing support for non-linear div tables, FC timeout causing rate/parent changes to fail after registers were already written, parent scanning ignoring `req` constraints beyond current rates, and no explicit locking beyond regmap internals. Test signals include gate polarity correctness, `clk_round_rate()` selecting expected parent/divider, set-rate and set-parent clearing FC bits before timeout, unchanged behavior for factor no-op set-rate, and no spurious parent selection when parent lookups return NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.c -->
