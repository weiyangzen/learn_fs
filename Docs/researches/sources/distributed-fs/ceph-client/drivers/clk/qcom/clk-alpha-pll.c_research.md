# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-alpha-pll.c

## Purpose
Implements Qualcomm alpha PLL clock operations for the common clock framework. The file covers generic alpha PLLs and many hardware families, including Huayra, Fabia, Trion/Lucid, Zonda/Regera, Lucid 5LPE/Evo/OLE, Pongo ELU, Rivian, Stromer, and slew-capable PLLs. It translates CCF rate and enable requests into regmap writes against family-specific PLL layouts.

## Important APIs, Types, And Functions
Exports the global register offset table `clk_alpha_pll_regs`, configuration helpers such as `clk_alpha_pll_configure()`, `clk_fabia_pll_configure()`, `clk_trion_pll_configure()`, `clk_lucid_evo_pll_configure()`, `clk_pongo_elu_pll_configure()`, `qcom_clk_alpha_pll_configure()`, and many `struct clk_ops` tables. Core helpers include `wait_for_pll()`, `alpha_pll_round_rate()`, `alpha_pll_calc_rate()`, `alpha_pll_find_vco()`, `clk_alpha_pll_update_latch()`, `clk_alpha_pll_update_configs()`, and per-family enable, disable, recalc, determine, and set-rate callbacks.

## Control Flow
Configuration helpers write L, alpha, config, test, user, VCO, divider, and output bits using a `struct alpha_pll_config`. Generic enable clears bypass, waits, deasserts reset, waits for lock, then enables output; FSM paths vote through `clk_enable_regmap()` and poll active/offline bits. Rate changes calculate integer and fractional fields, validate VCO ranges, update registers, and, when the PLL is running and supports dynamic updates, latch the new values and wait for update acknowledgements. Family-specific paths adjust this sequence: Huayra allows live L-only changes, Fabia and Trion use OPMODE and calibration, Lucid variants use latch bits and calibration state, Zonda polls frequency-lock in CFA mode, Pongo calibrates against XO before selecting an internal clock, and Stromer can slew within a VCO range.

## State And Persistence
Persistent state lives in hardware registers selected by `offset` and `regs`; software carries only static descriptors, VCO tables, flags, and CCF `clk_hw` objects. Hardware state includes mode bits, lock/update/offline flags, OPMODE, L/alpha/fraction fields, post-dividers, output enables, calibration fields, and VCO selection. Dynamic update and slew paths preserve enabled state while altering rate; other paths may disable or park outputs temporarily.

## Dependencies And Integration Points
Depends on regmap, Linux CCF provider APIs, divider helpers, delays, and qcom common helpers such as `qcom_pll_set_fsm_mode()`. The header supplies descriptor types and exported ops used by SoC clock controller drivers, including the MSM8996 CPU and CBF drivers in this subset. `clk_regmap` vote helpers are used when PLLs run in hardware FSM mode.

## Risks And Edge Cases
Most failures are timeout or invalid-rate paths: lock, active, offline, latch, and update bits can fail to change. Incorrect `regs` tables or alpha widths corrupt unrelated PLL fields. Several configure functions intentionally skip bootloader-enabled PLLs to avoid hanging downstream RCGs. Rate rounding has family-specific limits; Fabia, Trion, Agera, and Zonda reject rounded rates outside a small margin. Slew-capable PLLs cannot dynamically switch VCO ranges and fall back to full set-rate. Some functions ignore regmap read failures in best-effort disable paths.

## Test Signals
High-value tests are boot-time configuration for every PLL type, enable/disable transitions in normal and FSM modes, dynamic set-rate while enabled and disabled, VCO range rejection, alpha rounding/recalc consistency, post-divider programming, timeout injection for lock/update bits, bootloader-left-enabled Trion/Lucid handling, and CPU/CBF rate changes that rely on alpha PLL dynamic updates.
