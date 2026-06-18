# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c

Purpose: implements the SpacemiT DDN clock type, a rational M/N divider with a fixed pre-divider factor used for clocks such as slow UART and I2S sysclk generation.

Important APIs and control flow: `ccu_ddn_calc_rate()` computes `prate * den / pre_div / num`. `ccu_ddn_calc_best_rate()` uses `rational_best_approximation()` to choose numerator and denominator fields within the configured bit masks. `ccu_ddn_determine_rate()` reports the closest achievable rate using the current best parent rate. `ccu_ddn_recalc_rate()` reads numerator and denominator from `reg_ctrl`, and `ccu_ddn_set_rate()` writes selected numerator/denominator fields through `ccu_update()`. `spacemit_ccu_ddn_ops` exports recalc, determine, and set-rate operations.

State and persistence behavior: no independent state is allocated; the selected numerator/denominator persists in the hardware control register. Each `struct ccu_ddn` stores mask/shift metadata, pre-divider, and embedded `ccu_common`, with its regmap filled by common probe.

Dependencies and integration points: depends on Linux CCF, `linux/rational.h`, the common SpacemiT regmap helpers, and SoC macro declarations from `ccu_ddn.h`. Consumers see DDN clocks as ordinary CCF clocks capable of rate changes without parent changes.

Risks and test signals: risks include divide-by-zero if hardware or tables produce `num == 0`, unchecked regmap read errors, overflow/truncation from unsigned long arithmetic at high parent rates, rational approximation parameter order sensitivity, and no explicit hardware settle/poll after writes. Test signals include requested UART/I2S sample rates selecting expected fields, `clk_get_rate()` matching register values, rate changes preserving unrelated bits, and malformed zero fields not crashing downstream users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_ddn.c -->
