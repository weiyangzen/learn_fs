# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-audsys-clk.c

## Purpose

`mt8186-audsys-clk.c` registers the MT8186 audsys clock gates that live inside the AFE register space. These gates become CCF/clkdev clocks consumed by DAPM clock supplies and by `mt8186-afe-clk.c`.

## Important APIs, Types, and Functions

`struct afe_gate` describes a gate clock ID, name, parent, register offset, bit, flags, clock ops, and gate polarity. The `GATE_AUD0/1/2` macros build entries for `AUDIO_TOP_CON0`, `AUDIO_TOP_CON1`, and `AUDIO_TOP_CON2`. `aud_clks[CLK_AUD_NR_CLK]` defines AFE, APLL 22/24 MHz, tuner, TDM, ADC/DAC, DAC pre-distortion, TML, NLE, I2S BCLK, ASRC, hi-res, ADDA6, third DAC, and ETDM gate clocks.

`mt8186_audsys_clk_register()` allocates `afe_priv->lookup`, loops over the gate table, registers each gate with `clk_register_gate()` using `afe->base_addr + gate->reg`, creates a `clk_lookup` with `con_id = gate->name` and `dev_id = dev_name(afe->dev)`, stores it for cleanup, and registers `mt8186_audsys_clk_unregister()` as a devm action. The unregister action drops clkdev lookups and unregisters gates.

## Control Flow and State

The file is called from `mt8186_init_clock()` before consumer `devm_clk_get()` calls. Registered gates persist for the device lifetime and are torn down by the devm action. `afe_priv->lookup` is the cleanup ledger.

## Dependencies and Integration Points

It depends on Linux CCF, clkdev, AFE base MMIO, register offsets, and clock IDs from `mt8186-audsys-clkid.h`. The gate names must match the consumer strings in `mt8186-afe-clk.c` and DAPM `SND_SOC_DAPM_CLOCK_SUPPLY()` names.

## Risks

Registration failures are logged and skipped, but the function continues; later consumers may receive missing clocks. If `kzalloc_obj(*cl)` fails after some gates are registered, cleanup relies on the devm action only if it is reached, so this path deserves scrutiny. Gate bit polarity uses `CLK_GATE_SET_TO_DISABLE`; a wrong flag would invert clock enable behavior. Direct gate registration against AFE MMIO assumes the base address is valid and clock-register layout matches the table.

## Test Signals

Test with `CONFIG_COMMON_CLK` and MT8186 AFE probe. Check that every `aud_*` clock can be acquired by `devm_clk_get()`, DAPM clock supplies enable routes, and clock summary/debugfs shows expected prepare counts during playback/capture. Missing gate names show as `devm_clk_get ... fail` later in clock init.
