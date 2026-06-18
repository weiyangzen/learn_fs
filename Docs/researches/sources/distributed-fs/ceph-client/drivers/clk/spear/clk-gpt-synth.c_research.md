# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c

Purpose: implements SPEAr general-purpose timer synthesizer clocks, where output rate is `Fin / ((2 ^ (N + 1)) * (M + 1))`.

Important APIs and control flow: `gpt_calc_rate()` computes the table rate for `mscale` and `nscale`. `clk_gpt_determine_rate()` uses `clk_round_rate_index()` to choose a table entry. `clk_gpt_recalc_rate()` reads M and N scale fields from MMIO and divides the parent rate. `clk_gpt_set_rate()` writes the selected M/N scale fields under the optional lock. `clk_register_gpt()` validates arguments, allocates `struct clk_gpt`, initializes CCF metadata, and registers the clock.

State and persistence behavior: hardware state persists in M/N scale fields. Software state is heap-allocated and consists of the register pointer, rate table, count, lock, and embedded `clk_hw`. No automatic lifetime management or unregister helper is present.

Dependencies and integration points: depends on CCF, raw MMIO, shared SPEAr rounding helper, and `struct gpt_rate_tbl`. It is available to SPEAr platform clock files that need programmable GPT sources, though the selected SPEAr1310/1340 files mainly use generic mux/gate GPT clocks rather than this helper directly.

Risks and test signals: risks include table ordering assumptions, potential overflow in `1 << (nscale + 1)` if table values exceed the documented field width, NULL returns on registration failure, and no devm cleanup. Test signals include rate calculations for boundary M/N values, register writes preserving unrelated bits, timer tick accuracy, and compile/link coverage for platforms that instantiate GPT synthesizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spear/clk-gpt-synth.c -->
