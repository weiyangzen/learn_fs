# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.c

Purpose: Registers MT8188 audio subsystem gate clocks that are backed by AFE audio top registers rather than separate clock-controller nodes. These gates are made available through `clkdev` so the AFE driver and DAPM `SND_SOC_DAPM_CLOCK_SUPPLY` widgets can obtain them by connection ID.

Important APIs and functions: `struct afe_gate` describes each gate ID, name, parent name, register offset, bit, flags, and gate polarity. Macros `GATE_AUD0`, `GATE_AUD1`, `GATE_AUD3`, `GATE_AUD4`, `GATE_AUD5`, and `GATE_AUD6` instantiate gates for `AUDIO_TOP_CON*` registers with `CLK_SET_RATE_PARENT` and `CLK_GATE_SET_TO_DISABLE`. `mt8188_audsys_clk_register()` allocates `afe_priv->lookup`, calls `clk_register_gate()` for every `aud_clks[]` entry, creates `clk_lookup` records, and installs a devm cleanup action. `mt8188_audsys_clk_unregister()` unregisters gates and drops lookups.

Control flow: `mt8188_afe_init_clock()` calls this before `devm_clk_get()` on the same names. Each successful gate registration creates a lookup with `dev_id = dev_name(afe->dev)`, allowing later device-scoped clock gets. On device teardown or devm reset, cleanup iterates lookups, unregisters gate clocks, and drops clkdev entries.

State and persistence: Gate lookup pointers are stored in `mt8188_afe_private->lookup`. Hardware gate state persists in `AUDIO_TOP_CON0/1/3/4/5/6` registers. Clock framework state persists until devm cleanup.

Dependencies and integration: Depends on Linux clock provider and clkdev APIs, AFE MMIO base address, `mt8188-audsys-clkid.h` ID count, and register offsets from `mt8188-reg.h`. Clock names match `mt8188-afe-clk.c`'s `aud_clks[]` and DAPM clock supply names such as `aud_dac`, `aud_pcmif`, and `aud_hdmi_out`.

Risks: `clk_register_gate()` failures are logged but do not abort registration, so missing clocks may surface later in `devm_clk_get()` rather than at the original failure. If `kzalloc_obj(*cl)` fails after some gates are registered, cleanup coverage depends on devm action registration not yet installed; this can leak earlier gates. Register offsets assume `afe->base_addr + reg` is valid for all audio top gate registers. ID order must match `CLK_AUD_NR_CLK`.

Test signals: Probe should create all expected clock lookups and later `devm_clk_get()` in `mt8188_afe_init_clock()` should succeed. DAPM path tests for ADDA, DMIC, eTDM, PCMIF, and memifs should show gate enable/disable transitions. Module unload or device removal should not leave stale clkdev lookups.
