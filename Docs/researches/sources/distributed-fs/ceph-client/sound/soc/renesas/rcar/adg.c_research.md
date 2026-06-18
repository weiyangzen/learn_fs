# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/adg.c

## Purpose

`adg.c` implements helper routines for the R-Car Audio Clock Generator. It discovers ADG input clocks, computes BRGA/BRGB divider settings for 44.1 kHz and 48 kHz clock families, registers optional ADG clock outputs, and programs clock selectors used by SSI, SRC, and CMD modules. The rest of the driver treats it as the clock authority behind `rsnd_adg_clk_query()`, `rsnd_adg_ssi_clk_try_start()`, and the Gen2 timing selector helpers.

## Important APIs, types, and functions

`struct rsnd_adg` stores the ADG clock, input clocks, clock-output provider state, cached input rates, BRG register values, and the embedded `rsnd_mod`. `rsnd_adg_probe()` allocates this state, initializes the pseudo module, gets clock inputs and outputs, enables clocks, and logs debug information. `rsnd_adg_remove()` unregisters clkouts, deletes the OF clock provider, disables clocks, and unregisters the null clock. `rsnd_adg_clk_control()` enables/disables the ADG and input clocks while caching rates to avoid `clk_get_rate()` in atomic paths. `rsnd_adg_clk_query()` maps a requested master rate to CLKA/B/C/I or BRGA/BRGB selector codes. `rsnd_adg_ssi_clk_try_start()` and `rsnd_adg_ssi_clk_stop()` program `AUDIO_CLK_SEL*` for SSI clock output. `rsnd_adg_set_src_timesel_gen2()` and `rsnd_adg_set_cmd_timsel_gen2()` program SRC/CMD timing selectors for rate conversion paths.

## Control Flow

Probe builds an ADG module with no real module clock, fetches `adg` and generation-specific `clkin` clocks, falls back to a registered fixed-rate null clock when optional clocks are missing, parses `clock-frequency`, computes BRRA/BRRB candidates, registers clkout providers when requested, and enables the ADG. Runtime clock selection flows from SSI/SRC/CMD callbacks into ADG: SSI asks for an exact main clock; SRC/CMD ask for timesel values based on runtime input/output rates. For conversion paths, `rsnd_adg_get_timesel_ratio()` defaults to SSI word-select timing and only searches clock/divider ratios when runtime rate differs from SRC input or output.

## State and Persistence Behavior

ADG persists cached register images (`ckr`, `brga`, `brgb`) and BRG rates so suspend/resume and runtime re-enable can restore hardware state. `clkin_rate[]` is valid only while clocks are enabled and is deliberately cleared on disable. Clock outputs are registered with the common clock framework and must be unregistered during remove or failed probe cleanup. The null clock is lazily created and explicitly cleaned after ADG clocks are disabled.

## Dependencies and Integration Points

The file depends on common clock framework APIs, OF clock-provider registration, pseudo-register access from `gen.c`, and `rsnd_priv`/`rsnd_mod` helpers from `rsnd.h`. SSI uses ADG for master-clock output, SRC and CMD use ADG for Gen2 timesel routing, and debugfs uses `rsnd_adg_clk_dbg_info()`.

## Risks and Test Signals

Key risks are clock-frequency DT mistakes, approximate CLKI-derived rates, BRG divider edge cases, SSI8/SSI9 special timing, and leaked OF clock providers on probe errors. Tests should exercise DTs with and without ADG clocks, 44.1 kHz and 48 kHz families, suspend/resume, clock-master startup for normal/TDM streams, SRC conversion rates, and debugfs clock output consistency.
