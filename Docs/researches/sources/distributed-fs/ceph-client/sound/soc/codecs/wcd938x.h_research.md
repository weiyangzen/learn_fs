<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.h

## Purpose

`wcd938x.h` is the shared register and SoundWire contract header for the WCD938x codec driver family. It defines the codec CSR address map, bit masks, SoundWire port/channel enumerations, the per-SoundWire-child state structure, and the exported SoundWire helper prototypes used by `wcd938x.c`.

The header is intentionally hardware-facing. Most definitions are one-to-one names for analog, MBHC, TX, RX, class-H, interrupt, digital, efuse, SoundWire, pad, GPIO, and debug registers in the WCD938x address range from `WCD938X_BASE_ADDRESS` through `WCD938X_MAX_REGISTER`.

## Important APIs, types, and constants

The register map starts at `WCD938X_BASE_ADDRESS` and declares analog registers such as `WCD938X_ANA_BIAS`, `WCD938X_ANA_RX_SUPPLIES`, `WCD938X_ANA_HPH`, `WCD938X_ANA_EAR`, ADC channel registers, MBHC mechanical/electrical/ZDET/result/button registers, micbias registers, class-H and flyback registers, headphone PA and RDAC registers, earpiece and AUX registers, sleep/watchdog registers, and digital CDC/SoundWire/interrupt/efuse/pad/debug registers. `WCD938X_MAX_REGISTER` is `WCD938X_DIGITAL_DEM_BYPASS_DATA3`, giving regmap users a bounded maximum.

Bit-mask definitions describe fields used throughout `wcd938x.c`: RX supply and regulator mode bits, headphone PA/reference enables, earpiece gain fields, TX HPF init bits, MBHC detection and result masks, micbias VOUT and enable modes, LDOH enable, clock enable masks, TX/RX digital clock bits, ADC mode fields, compander enables, digital gain enables, DMIC clock masks, PDM watchdog masks, interrupt status/mask/clear registers, efuse ID masks, and moisture detection controls.

The SoundWire TX port enum maps logical source paths to data port numbers: `WCD938X_ADC_1_2_PORT`, `WCD938X_ADC_3_4_PORT`, `WCD938X_DMIC_0_3_MBHC_PORT`, and `WCD938X_DMIC_4_7_PORT`, with `WCD938X_MAX_TX_SWR_PORTS` as the last port number. `enum wcd938x_tx_sdw_channels` names ADC1-4, DMIC0-7, and MBHC channel IDs. The RX port enum maps `WCD938X_HPH_PORT`, `WCD938X_CLSH_PORT`, `WCD938X_COMP_PORT`, `WCD938X_LO_PORT`, and `WCD938X_DSD_PORT`; `enum wcd938x_rx_sdw_channels` names HPH, CLSH, compander, LO, and DSD channels.

`struct wcd938x_sdw_priv` is the bridge object shared between the SoundWire child driver and the aggregate codec driver. It contains the SoundWire slave pointer, stream config, current stream runtime, per-port `sdw_port_config` array, logical channel info table, `port_enable` booleans indexed by channel/port IDs, active port count, TX/RX direction flag, parent `wcd938x_priv`, shared slave IRQ domain, and child regmap.

The exported functions are `wcd938x_sdw_free()`, `wcd938x_sdw_set_sdw_stream()`, and `wcd938x_sdw_hw_params()`. When `CONFIG_SND_SOC_WCD938X_SDW` is enabled they are implemented by the SoundWire support object; otherwise inline stubs return `-EOPNOTSUPP`, allowing the main codec code to compile while making DAI operations fail cleanly without SoundWire support.

## Control flow and integration

The header has no executable control flow beyond compile-time configuration, but it controls how the C files interact. `wcd938x.c` includes it to program named registers and fields, build DAPM event handlers, configure MBHC register descriptors, map regmap IRQs, and bridge ASoC DAI operations to SoundWire helper functions. The SoundWire child implementation includes it to allocate and populate `wcd938x_sdw_priv`, expose channel tables, and configure SoundWire ports using the same enum values.

The port and channel enums are part of an implicit ABI inside the driver. ALSA controls in `wcd938x.c` use enum constants as `private_value` register/channel identifiers; DAPM and SoundWire helpers then use those IDs to locate `wcd938x_sdw_priv->ch_info[]` entries and mutate `port_config[port_num - 1].ch_mask`.

## State and persistence behavior

The header defines state shape but does not allocate persistent state. State persistence is handled by users of `struct wcd938x_sdw_priv`: the SoundWire child persists stream runtime, port masks, direction, regmap cache and IRQ domain pointers for the lifetime of the device, while the main codec stores pointers to the RX and TX child objects in `wcd938x_priv`.

Register definitions are persistent only in the hardware/regmap sense. They are used as stable symbolic addresses for reads, writes, cache defaults, volatile-register policy, and DAPM/MBHC sequencing. The fallback inline stubs make absence of SoundWire support an explicit runtime error for DAI operations rather than silently pretending stream setup succeeded.

## Dependencies and integration points

The header depends on Linux SoundWire types from `<linux/soundwire/sdw.h>` and `<linux/soundwire/sdw_type.h>`, kernel bit helpers such as `BIT()` and `GENMASK()`, ALSA PCM and DAI types referenced in function prototypes, and `struct wcd_sdw_ch_info` from the common WCD codec support included by C users.

Its main integration points are `wcd938x.c`, the WCD938x SoundWire child implementation, regmap configuration code, MBHC field descriptors, and ASoC controls that use these enum values. Device-tree and ACPI do not include this header directly, but their SoundWire port mapping and codec compatible data must match the register and port layout represented here.

## Risks

Because the file is a dense hardware register map, incorrect address or mask edits can break unrelated codec paths. Many masks are reused by event handlers that assume one-bit fields can be written with logical `1` values through `snd_soc_component_write_field()`. Changing enum order is risky because channel IDs index channel-info arrays and are embedded in ALSA control private data.

`WCD938X_MAX_SWR_CH_IDS` bounds `port_enable`, but RX and TX channel enums plus port enums use different logical spaces. Code that indexes `port_enable` by port number in one path and by channel ID in another needs careful review to avoid off-by-one or cross-direction confusion. The `CONFIG_SND_SOC_WCD938X_SDW` stubs also mean builds without SoundWire support compile, but runtime stream operations will fail with `-EOPNOTSUPP`.

## Test signals

Compile coverage should include both `CONFIG_SND_SOC_WCD938X_SDW=y/m` and disabled configurations to verify prototypes and inline stubs stay compatible. Runtime signals include successful regmap access through all referenced register ranges, correct SoundWire port masks for ADC/DMIC/HPH/CLSH/COMP/LO/DSD controls, correct interrupt mask/status/clear register use, and no undefined register access beyond `WCD938X_MAX_REGISTER`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x.h -->
