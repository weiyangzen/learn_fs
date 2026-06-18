# sources/distributed-fs/ceph-client/sound/soc/img/pistachio-internal-dac.c

Purpose: ASoC codec driver for the Pistachio SoC internal DAC, controlling power/reset through a syscon regmap and a `VDD` regulator.

Important APIs/types/functions: `struct pistachio_internal_dac` stores regmap, regulator, and mute flag. DAPM exposes a DAC and AOUTL/AOUTR outputs; control `Playback Switch` maps to the power-down bit. `pistachio_internal_dac_reg_writel()` writes indirect GTI registers. Runtime PM callbacks power the DAC and regulator on/off. Probe configures supply voltage selection, powers the DAC, enables runtime PM, and registers one playback DAI.

Control flow: probe allocates state, gets `img,cr-top` syscon and `VDD` regulator, enables regulator, validates voltage as 1.8 V or 3.3 V, writes power select, cycles DAC power, enables runtime PM, then registers the codec component/DAI. Runtime resume enables regulator and powers the DAC; runtime suspend powers off then disables regulator. Remove disables PM, powers off, and disables regulator.

State and persistence: driver state is regulator/regmap handles and unused `mute`. Hardware state persists in top-level DAC control, reset, GTI indirect write, and power registers. Runtime PM owns current power state after probe.

Dependencies/integration: depends on syscon/regmap phandle `img,cr-top`, regulator named `VDD`, ASoC codec registration, and compatible `img,pistachio-internal-dac`.

Risks: regulator is enabled in probe before runtime PM and may be disabled twice only through carefully paired error/remove paths. Only two exact voltages are accepted. `mute` field is unused. The indirect register write sequence has no readback or completion polling.

Test signals: probe with 1.8 V and 3.3 V supplies, invalid-voltage rejection, runtime suspend/resume power sequencing, DAPM route visibility, playback DAI constraints, and regulator/syscon failure injection.
