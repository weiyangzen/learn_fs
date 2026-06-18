# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-clk.c

## Purpose
This file implements MT8195 AFE clock acquisition, generic clock helpers, APLL tuner setup, register-access clock sequencing, main AFE clock sequencing, and top clock-gate control. It is the clock-control backend used by MT8195 PCM and DAI drivers.

## Important APIs, Types, and Functions
The public functions are `mt8195_afe_get_mclk_source_clk_id()`, `mt8195_afe_get_mclk_source_rate()`, `mt8195_afe_get_default_mclk_source_by_rate()`, `mt8195_afe_init_clock()`, `mt8195_afe_enable_clk()`, `mt8195_afe_disable_clk()`, `mt8195_afe_prepare_clk()`, `mt8195_afe_unprepare_clk()`, `mt8195_afe_enable_clk_atomic()`, `mt8195_afe_disable_clk_atomic()`, `mt8195_afe_set_clk_rate()`, `mt8195_afe_set_clk_parent()`, `mt8195_afe_enable_main_clock()`, `mt8195_afe_disable_main_clock()`, `mt8195_afe_enable_reg_rw_clk()`, and `mt8195_afe_disable_reg_rw_clk()`. Only `mt8195_afe_enable_clk()` and `mt8195_afe_disable_clk()` are explicitly exported with `EXPORT_SYMBOL_GPL`.

The main private data type is `struct mt8195_afe_tuner_cfg`, which stores tuner register addresses, shifts, masks, defaults, a spinlock, and a reference count for each audio PLL tuner. The `aud_clks[]` table maps `enum MT8195_CLK_*` IDs to DT/CCF clock names.

## Control Flow
`mt8195_afe_init_clock()` registers audsys clocks, allocates `afe_priv->clk`, resolves every clock name with `devm_clk_get()`, and initializes the five tuner configs. MCLK helpers map user-facing MCK selections to clock IDs and choose APLL1 for 8 kHz-family rates and APLL2 otherwise.

Generic clock wrappers guard NULL clock pointers, call CCF APIs, and return/log errors. Non-atomic helpers use `clk_prepare_enable()` or `clk_disable_unprepare()`, while atomic helpers use `clk_enable()` or `clk_disable()` for contexts where preparation is already handled.

APLL tuner enable first writes default divider/reference/upper-bound values, enables tuner-related clocks for PLL1 or PLL2, then increments the tuner refcount under `ctrl_lock` and sets the tuner enable bit only on the first user. Disable decrements under the same lock, clears the tuner enable bit at zero, clamps negative counts back to zero, and disables the tuner clocks.

`mt8195_afe_enable_reg_rw_clk()` enables the infra, bus, 26 MHz, AFE, and A1SYS clocks needed for register access. Its disable counterpart turns them off in reverse order. `mt8195_afe_enable_main_clock()` enables timing-system clocks, sets top CG bits, turns on `AFE_DAC_CON0` bit 0, and enables APLL1/APLL2 tuners. Disable runs the reverse sequence.

## State and Persistence
Mutable state lives in `mt8195_afe_private->clk` and in the static tuner config array. Tuner `ref_cnt` and `ctrl_lock` manage shared use across stream paths. Hardware state is persisted in clock framework enables and AFE registers such as APLL tuner config registers, `ASYS_TOP_CON`, and `AFE_DAC_CON0`. The file does not store state on disk.

## Dependencies and Integration Points
The file depends on Linux CCF (`clk_*`), regmap, `mt8195-afe-common.h`, `mt8195-afe-clk.h`, `mt8195-reg.h`, and `mt8195-audsys-clk.h`. It is called from the MT8195 PCM runtime PM paths, ADDA/ETDM/PCM DAI setup, and machine-driver MCLK configuration. Clock names in `aud_clks[]` must match the SoC clock providers and device tree.

## Risks
Several loops ignore return values from individual enable/disable calls, so partial clock failures can be hidden in aggregate sequencing. APLL tuner disable decrements before checking underflow and always disables tuner clocks even if the refcount was already zero, which can unbalance CCF enables if callers mismatch enable/disable. `get_top_cg_*()` returns zero for invalid types, leading to harmless-looking writes to register 0 with mask 0, but invalid callers would not receive an error. Missing DT clocks fail probe during init.

## Test Signals
Validation should include probe with every clock resolved, runtime resume/suspend cycling with no unbalanced clock warnings, stream start/stop across ADDA, ETDM, PCM, HDMI/DPTX, and memif paths, sample-rate changes that select APLL1 vs APLL2 correctly, debug register checks showing AFE on/timing CG/tuner bits set and cleared, and fault injection for missing clocks or failed `clk_set_parent()`/`clk_set_rate()` paths.
