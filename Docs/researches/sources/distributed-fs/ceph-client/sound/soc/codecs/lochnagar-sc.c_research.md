# sources/distributed-fs/ceph-client/sound/soc/codecs/lochnagar-sc.c

## Purpose
`lochnagar-sc.c` is a small ASoC component driver that models the Cirrus Logic Lochnagar board sound-card endpoints. It provides three DAIs: one line interface and two USB audio interfaces. The driver mainly supplies DAPM endpoints/routes, runtime hardware constraints, DAI format validation, and MCLK enable/disable for the line interface.

## Important APIs, Types, And Functions
`struct lochnagar_sc_priv` stores the required `mclk`. The component driver `lochnagar_sc_driver` exposes two line widgets (`Line Jack`, `USB Audio`) and routes between those widgets and the DAI streams. The DAI array `lochnagar_sc_dai[]` declares `lochnagar-line`, `lochnagar-usb1`, and `lochnagar-usb2`. `lochnagar_sc_probe()` allocates private state, obtains the `"mclk"` clock, stores drvdata, and registers the component and DAIs.

The DAI callbacks are `lochnagar_sc_startup()`, `lochnagar_sc_line_startup()`, `lochnagar_sc_line_shutdown()`, `lochnagar_sc_set_line_fmt()`, and `lochnagar_sc_set_usb_fmt()`. `lochnagar_sc_hw_rule_rate()` adds a dynamic upper bound tying sample rate to frame size so bit clock stays within `24576000 / frame_bits`.

## Control Flow
On probe, device-managed allocation and `devm_clk_get()` must succeed before registering the ASoC component. On stream startup, all DAIs get a fixed supported-rate list of 8 kHz through 192 kHz families plus a hardware rule that refines rate based on `SNDRV_PCM_HW_PARAM_FRAME_BITS`. The line DAI additionally enables `mclk` before constraints are installed and limits channels to 4 or 8. On line shutdown, `mclk` is disabled. DAI format calls require I2S with normal bit/frame polarity; the line DAI must be codec bit/frame consumer (`SND_SOC_DAIFMT_CBC_CFC`), and the USB DAIs must be provider (`SND_SOC_DAIFMT_CBP_CFP`).

## State And Persistence
Runtime state is limited to the prepared/enabled state of `mclk`; it is not reference-counted in the driver beyond ALSA startup/shutdown ordering. The component has no regmap, persistent controls, or suspend/resume hooks. ALSA's runtime constraints and DAPM graph are rebuilt from static data at registration.

## Dependencies And Integration Points
The driver depends on the platform bus, common clock framework, ASoC, and Lochnagar MFD device tree binding. It matches `cirrus,lochnagar2-soundcard` and exposes the platform alias `lochnagar-soundcard`. Machine drivers can connect the DAI names and rely on this component to enforce the Lochnagar board's channel/rate/format limitations.

## Risks And Notes
If `lochnagar_sc_line_startup()` enables `mclk` and then a later constraint call fails, it returns without disabling `mclk`, leaving a possible clock leak on rare error paths. The format validation masks out only clock-provider bits and requires exact format/polarity matches, so any machine-driver format flags outside the expected set will be rejected. The rate rule depends on `FRAME_BITS` max being meaningful when the rule runs.

## Test Signals
Build and DT binding tests should confirm the platform device probes with an `mclk`. ALSA PCM tests should verify line streams only accept 4 or 8 channels, USB streams accept 1-8 channels, unsupported rates are rejected, and high frame-bit configurations refine max rate correctly. DAI format tests should cover accepted I2S NB_NF provider/consumer combinations and rejected polarity/format variants. Clock tests should verify line startup/shutdown balances `mclk`.
