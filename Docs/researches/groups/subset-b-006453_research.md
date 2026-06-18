# subset-b-006453 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125-sdw.c

## Purpose
This is the SoundWire slave-side driver for the Qualcomm PM4125 codec. It exposes RX and TX SoundWire endpoints to the common PM4125 platform codec driver, supplies the codec register map over the TX SoundWire device, and plugs the slave interrupt callback into the shared WCD interrupt path.

## Important APIs, types, and functions
The key exported API is `pm4125_sdw_hw_params()`, which turns the selected `struct pm4125_sdw_priv` port/channel state into `struct sdw_stream_config` plus `struct sdw_port_config` and calls `sdw_stream_add_slave()`. The file defines RX/TX `wcd_sdw_ch_info` maps, two `sdw_dpn_prop` entries, a large PM4125 regmap default table, readable/writeable/volatile register predicates, `pm4125_interrupt_callback()`, `pm4125_probe()`, runtime PM callbacks, and the `sdw_driver` named `pm4125-codec`.

## Control flow and integration
Probe decides whether this slave instance is TX or RX from `qcom,tx-port-mapping` versus `qcom,rx-port-mapping`, loads optional static channel maps, fills SoundWire properties, and registers itself as a component through `wcd_sdw_component_ops`. TX devices initialize `devm_regmap_init_sdw()` and start cache-only until enumeration/resume; RX devices only provide sink port data and channel mapping. Interrupt delivery enters from SoundWire OOB status, calls `wcd_interrupt_callback()`, and triggers the codec-level IRQ domain owned by `pm4125.c`.

## State and persistence
Persistent driver state is in `struct pm4125_sdw_priv`: stream runtime, port configs, channel map, port-enable flags, TX/RX role, back pointer to `pm4125_priv`, shared IRQ domain, and TX regmap. Runtime suspend marks the regmap cache-only and dirty; resume exits cache-only and syncs. Port and channel selections are in memory and are consumed during PCM hw_params.

## Dependencies
This file depends on Linux SoundWire core, regmap, runtime PM, component framework, `wcd-common.h` helpers through `pm4125.h`, and the PM4125 register definitions. Device-tree properties are central for SoundWire port and channel mapping.

## Risks and test signals
`pm4125_sdw_hw_params()` initializes `ch_count` to 1 before counting selected channels, so stream channel count behavior should be checked against hardware expectations. `for_each_set_bit(..., 4)` only counts four mask bits although constants allow more IDs. Probe logs but continues on missing mappings, so DT mistakes can become silent audio routing failures. Test signals include TX/RX SoundWire enumeration, regcache sync after runtime PM, PCM startup with selected switches/companders, and jack/MBHC interrupts reaching the PM4125 regmap IRQ chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125.c

## Purpose
This is the main ASoC component driver for the Qualcomm PM4125 audio codec. It binds the RX and TX SoundWire child devices into one codec component, manages power supplies and SPMI reset, exposes mixer controls and DAPM routes, initializes MBHC headset detection, and implements the DAI operations that delegate stream setup to the SoundWire layer.

## Important APIs, types, and functions
`struct pm4125_priv` is the central state object: RX/TX SoundWire devices, regmaps, phandles, IRQ chip/domain data, MBHC state, mic-bias reference counters, watchdog IRQs, compander flags, and global mbias atomic counter. Important functions include `pm4125_reset()`, `pm4125_io_init()`, `pm4125_global_mbias_enable/disable()`, DAPM callbacks for RX clocks, headphone DACs/PAs, lineout/ear paths, ADC/DMIC enable, mic-bias control, `pm4125_connect_port()`, compander and SWR switch get/put callbacks, `pm4125_mbhc_init()`, `pm4125_irq_init()`, `pm4125_soc_codec_probe()`, DAI callbacks, `pm4125_bind()`, and platform `pm4125_probe()`.

## Control flow and integration
Platform probe enables bulk regulators, obtains the parent SPMI regmap, resets the codec, parses WCD micbias/MBHC DT data, records RX/TX SoundWire phandles, and registers as a component master. `pm4125_bind()` waits briefly, binds the SoundWire slave components, resolves RX/TX devices, links PM runtime dependencies, takes the TX SoundWire regmap as the CSR interface, creates a small IRQ domain feeding `devm_regmap_add_irq_chip()`, shares the virtual IRQ domain with both SoundWire children, writes micbias data, and registers the ASoC component plus two DAIs. Component probe waits for TX SoundWire initialization, initializes the component regmap, performs hardware IO setup, configures edge-triggered interrupt levels, requests PDM watchdog threaded IRQs, disables them until DAPM enables output paths, and starts MBHC.

## State and persistence
Analog power sequencing is DAPM-driven. `gloal_mbias_cnt` reference-counts shared global mbias hardware, while `micb_ref[]` and `pullup_ref[]` track individual mic-bias enable and pull-up users. `status_mask` remembers temporary headset-mic BCS state. `comp1_enable` and `comp2_enable` persist control choices and alter SoundWire port connection state. SoundWire channel masks live in each child `pm4125_sdw_priv` and are reported through `get_channel_map()`.

## Dependencies
The driver integrates ASoC, DAPM, SoundWire, component framework, runtime PM, regmap IRQ, IRQ domains, regulators, WCD MBHC v2, and WCD common micbias helpers. DT must provide `qcom,rx-device`, `qcom,tx-device`, supplies, and optional MBHC/micbias tuning.

## Risks and test signals
The bind path has many ordered resources; missing cleanup of `virq` itself or mismatched `free_irq()` with `devm_request_threaded_irq()` should be reviewed. The field name `gloal_mbias_cnt` is misspelled but consistently used. `pm4125_connect_port()` indexes `port_config[port_idx - 1]`, so invalid channel info or DT port maps can corrupt state. Test signals include simple-card registration of both DAIs, playback/capture PCM open and close, DAPM power transitions with no pop/watchdog storms, MBHC jack insertion/button reports, runtime PM ordering between TX/RX, and regmap IRQ delivery through SoundWire OOB interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125.h

## Purpose
This header is the PM4125 hardware contract shared by the PM4125 platform codec and its SoundWire slave driver. It defines analog/digital register addresses, bit masks and values, SoundWire port/channel IDs, private SoundWire state, IRQ numbers, and conditional SoundWire helper prototypes.

## Important APIs, types, and functions
The most important type is `struct pm4125_sdw_priv`, which stores a SoundWire slave, stream configuration/runtime, per-port configs, WCD channel information, enable flags, master channel map, role flags, parent codec pointer, IRQ domain, and regmap. The header declares `pm4125_sdw_free()`, `pm4125_sdw_set_sdw_stream()`, and `pm4125_sdw_hw_params()` when `CONFIG_SND_SOC_PM4125_SDW` is enabled, with `-EOPNOTSUPP` stubs otherwise. Enumerations define TX ports, RX ports, IRQ indices, TX channels, and RX channels.

## Control flow and integration
The register constants are consumed by both `pm4125.c` DAPM/control code and `pm4125-sdw.c` regmap definitions. IRQ enum ordering matches the three SoundWire interrupt status/mask/clear registers used by `regmap_irq`. SoundWire port/channel enums align with `wcd_sdw_ch_info` arrays in the SoundWire driver and with mixer-control private values in the codec driver.

## State and persistence
The header does not persist state by itself but defines the in-memory shape used for SoundWire endpoint state across DAI calls. It also defines max register ranges and max micbias/channel counts that bound arrays in the implementation.

## Dependencies
It includes SoundWire headers and `wcd-common.h`, so users of this header depend on the WCD SoundWire channel description types and micbias constants. Bit operations such as `BIT()` and `GENMASK()` are used throughout.

## Risks and test signals
Header constants are single points of failure for bitfield writes in both drivers. Off-by-one errors are especially risky around `PM4125_SWRM_CH_MASK(ch_idx)` and port enum values beginning at 1 while arrays are zero-indexed. Build tests should cover both enabled and disabled `CONFIG_SND_SOC_PM4125_SDW` configurations. Runtime tests should exercise all IRQ enum mappings, micbias rails, compander channels, headphone channels, and ADC channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.c

## Purpose
This is the ASoC driver for the Rockchip RK3308 internal audio codec. It supports an eight-channel ADC capture path, stereo DAC playback to headphone/lineout pins, version-dependent register programming, DAPM power sequencing, and I2S/PCM DAI format and width configuration.

## Important APIs, types, and functions
`struct rk3308_codec_priv` stores device, MMIO regmap, GRF syscon regmap, reset control, clocks, component pointer, and codec hardware version. The main functions are `rk3308_codec_set_dai_fmt()`, `rk3308_codec_dac_dig_config()`, `rk3308_codec_adc_dig_config()`, `rk3308_codec_hw_params()`, `rk3308_codec_reset()`, `rk3308_codec_initialize()`, `rk3308_codec_set_bias_level()`, `rk3308_codec_get_version()`, `rk3308_codec_set_micbias_level()`, and platform probe. The file also defines extensive ALSA controls, TLV scales, DAPM widgets/routes, one `rk3308-hifi` DAI, and a simple 32-bit MMIO regmap.

## Control flow and integration
Platform probe resolves `rockchip,grf`, reset, and three clocks, enables clocks, identifies the codec version through GRF chip ID, maps codec registers, applies optional `rockchip,micbias-avdd-percent`, and registers the component. Component probe resets hardware and writes default-safe initialization values. DAI `set_fmt` programs all four ADC LR groups and the DAC for slave/master, I2S/LJ/RJ/DSP_A, and clock polarity. ADC master mode temporarily clears `RK3308_ADC_DIG_WORK` so all ADC digital format registers take effect together. `hw_params` selects valid sample width and enables active ADC groups according to capture channel count.

## State and persistence
Hardware state is almost entirely register state under DAPM control. `codec_ver` gates version-C-only digital gain defaults and different DAC master bits. Bias level transitions implement TRM power-up and power-down reference-current sequencing. No regcache is configured; registers are direct MMIO.

## Dependencies
The driver depends on Rockchip GRF syscon, reset framework, clocks `hclk`, `mclk_rx`, `mclk_tx`, ASoC controls/DAPM, and the register definitions in `rk3308_codec.h`.

## Risks and test signals
`rk3308_codec_clocks` is a static mutable `clk_bulk_data` array shared by probe instances, which is acceptable for a single SoC codec but fragile for hypothetical multiple instances. Version B is explicitly rejected. Clock enables are devm-acquired but not explicitly disabled on later probe errors after enabling clocks. Test signals include component registration on version A/C hardware, valid rejection of version B/unknown IDs, capture channel counts 1/2/4/6/8, all supported sample formats, master/slave clocking without abnormal ADC clocks, DAPM bias transitions, micbias percentage validation, and headphone pop-sound state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.h

## Purpose
This header defines the RK3308 internal codec register map and bitfields used by `rk3308_codec.c`. It covers global control, four ADC digital register groups, ALC registers, DAC digital registers, four ADC analog register groups, and DAC analog registers.

## Important APIs, types, and functions
There are no functions or exported types. Register macros such as `RK3308_ADC_DIG_CON01(ch)`, `RK3308_ADC_ANA_CON00(ch)`, and `RK3308_DAC_ANA_CON13` encode the grouped register layout. Bit macros define I2S modes, sample widths, master/slave bits, work bits, HPF settings, BIST paths, version-C digital gains, microphone enable/work/unmute bits, micbias level range, DAC headphone/lineout gains, HPMIX selects, and pop-sound values.

## Control flow and integration
The `.c` file composes these macros inside DAI format programming, hw_params, DAPM widgets/routes, reset, initialization, and bias-level power sequencing. Grouped ADC address macros are essential because capture channels are configured in left/right pairs across four groups.

## State and persistence
This file describes persistent hardware register state but does not maintain software state. Some definitions encode reset-value caveats: version-C ADC/DAC digital gain reset values are undocumented and corrected during initialization; HPMIX reset gain `0` is illegal and must be updated.

## Dependencies
The header relies on `BIT()` and other kernel bit macros being available via includes in users. It is tightly coupled to RK3308/RK3308BS TRM register semantics.

## Risks and test signals
Several comments distinguish version-specific behavior and unsupported hardware capabilities; incorrect macro reuse across chip versions could produce silent audio or bad clocks. The grouped macros mask channel index to two bits, so callers must validate group counts. Tests should verify every macro used in DAPM corresponds to the intended physical ADC/DAC channel, and that version-C gain defaults program the documented 0 dB values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3308_codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.c

## Purpose
This is the ASoC driver for the RK3328 internal codec. It primarily sequences DAC/headphone playback hardware, exposes one `rk3328-hifi` DAI, configures I2S/PCM format and word length, controls an optional external mute GPIO, and initializes the codec through MMIO regmap and GRF syscon.

## Important APIs, types, and functions
`struct rk3328_codec_priv` stores regmap, mute GPIO, `mclk`, `pclk`, cached sample clock, and speaker depop delay. Important functions are `rk3328_codec_reset()`, `rk3328_set_dai_fmt()`, `rk3328_mute_stream()`, `rk3328_codec_power_on/off()`, `rk3328_codec_open_playback()`, `rk3328_codec_close_playback()`, `rk3328_hw_params()`, startup/shutdown callbacks, component probe/remove, regmap predicates, and platform probe. Power sequencing data lives in `playback_open_list` and `playback_close_list`.

## Control flow and integration
Platform probe enables GRF `i2s_acodec_en`, reads `spk-depop-time-ms` with default 200 ms, obtains optional `mute` GPIO, handles a Rock64 legacy implicit mute path, enables `mclk` and `pclk`, maps MMIO registers, creates a cached regmap, and registers the ASoC component and DAI. Component probe resets and precharges the codec. PCM startup opens playback by applying the ordered register list, waiting for depop, unmuting GPIO, and setting output gains. Shutdown mutes GPIO, clears gains, applies the close list, resets the codec to avoid a 48 kHz to 44.1 kHz silence issue, and restores precharge current.

## State and persistence
Register state is cached with `REGCACHE_FLAT`; only reset is volatile. The mute GPIO state persists across open/close. `spk_depop_time` comes from DT and directly affects user-visible stream startup latency. Clocks remain enabled for the device lifetime after probe.

## Dependencies
The driver depends on Rockchip GRF syscon, MMIO resource mapping, regmap, clocks `mclk` and `pclk`, optional GPIO descriptor, ASoC DAI/component registration, and `rk3328_codec.h` for register definitions.

## Risks and test signals
Probe lacks a remove callback to disable clocks on driver removal because registration is devm-only; this may be acceptable for built-in SoC audio but is a resource-lifetime concern. The DAI advertises capture despite the driver only meaningfully sequences playback. The close path resets hardware as a sample-rate workaround, so cache coherency and next-open state should be tested. Test signals include startup/shutdown pop behavior, mute GPIO polarity, legacy Rock64 behavior, all supported DAI formats and PCM widths, regcache defaults after reset, and sample-rate switching from 48 kHz to 44.1 kHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.h

## Purpose
This header defines the RK3328 codec register offsets, bit masks, symbolic values, DAI ID, and a small register/mask/value helper struct used by the RK3328 codec driver.

## Important APIs, types, and functions
The only type is `struct rk3328_reg_msk_val`, used for ordered playback open/close register update lists. Macros define `CODEC_RESET`, DAC init/precharge/power/clock/mixer/select/headphone/gain/pop registers, reset bits, pin direction, I2S master/slave mode, sample valid length, PCM/I2S/LJ/RJ modes, precharge/discharge current controls, headphone mute/init/work bits, DAC select bits, and gain masks.

## Control flow and integration
`rk3328_codec.c` uses these constants in DAI `set_fmt`, `hw_params`, mute control, reset, power on/off, playback open/close lists, and regmap readable/writeable filters. The address macros shift register indices by two, matching the 32-bit MMIO stride configured in regmap.

## State and persistence
The header describes hardware state but stores none. It establishes the bit values that drive persistent codec output state such as mute, DAC work, precharge current, HPMIX enable/init, and headphone pop mode.

## Dependencies
It includes `<linux/bitfield.h>` for `BIT()` and `GENMASK()`. The bit definitions are local to RK3328 and should not be reused for other Rockchip codecs.

## Risks and test signals
Because the driver uses ordered arrays of these constants for analog sequencing, a wrong mask/value pair can create pops, no output, or stuck mute. Tests should confirm register offsets match the hardware manual, sample-width macros produce correct LRCLK framing, and the open/close lists leave reset/default state compatible with `rk3328_codec_reg_defaults`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk3328_codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk817_codec.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rk817_codec.c

## Purpose
This is the ASoC codec driver for the RK817 PMIC-integrated audio codec. It registers one playback/capture DAI, initializes codec registers through the parent RK808 regmap, provides DAPM routes for mic capture, headphone playback, and class-D speaker playback, and supports a DT option for differential microphone input.

## Important APIs, types, and functions
`struct rk817_codec_priv` stores the component, parent `struct rk808`, MCLK, cached sysclk, and `mic_in_differential`. Key functions are `rk817_init()`, `rk817_set_component_pll()`, volume controls, virtual playback mux, DAPM widget/route tables, `rk817_set_dai_sysclk()`, `rk817_set_dai_fmt()`, `rk817_hw_params()`, `rk817_digital_mute()`, component probe/remove, DT parsing, and platform probe/remove.

## Control flow and integration
Platform probe gets the parent RK808 data, parses the child `codec` node for `rockchip,mic-in-differential`, enables parent `mclk`, and registers the component. Component probe initializes the ASoC regmap from the parent PMIC regmap, stores the component, asserts a digital top reset value, writes vendor-kernel-derived defaults, conditionally enables differential mic mode, and programs fixed PLL values through `snd_soc_component_set_pll()`. DAI format currently only selects codec slave or master mode; hw_params writes 16-bit or 24-bit TX/RX word length registers.

## State and persistence
Most state lives in PMIC registers and is managed by DAPM supplies. `stereo_sysclk` records the requested sysclk but is not otherwise used. The fixed PLL configuration is persistent until changed. `mic_in_differential` is DT-derived and applied once during init.

## Dependencies
The driver depends on the RK808 MFD parent, RK817 codec register definitions from `<linux/mfd/rk808.h>`, parent regmap, MCLK, ASoC DAPM/control/DAI APIs, and simple-card compatible clock/PLL setup.

## Risks and test signals
Several PLL values and init registers are hard-coded from vendor code with comments noting poor documentation, so portability across boards is uncertain. `of_get_child_by_name()` failure leaves `node` NULL but still passes it to `of_property_read_bool()`, which is typically safe but worth checking. `RK817_FORMATS` advertises S20_3LE, yet `rk817_hw_params()` rejects S20_3LE. Test signals include module bind under the RK808 MFD, MCLK enable/disable on probe/remove, playback mux exclusivity between HP and SPK, mute control, 16/24/32-bit stream behavior, rejection or support alignment for S20_3LE, and differential mic DT behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rk817_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6231.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rl6231.c

## Purpose
This file provides shared Realtek RL6231-family clock helpers used by codec drivers. It converts register encodings to pre-divider values, calculates DMIC divider selections, calculates PLL M/N/K codes, and reports pre-divider indices for system-clock/sample-rate relationships.

## Important APIs, types, and functions
Exported APIs are `rl6231_get_pre_div()`, `rl6231_calc_dmic_clk()`, `rl6231_pll_calc()`, and `rl6231_get_clk_info()`. Internal `struct pll_calc_map` and `pll_preset_table` provide known-good PLL settings. `find_best_div()` scales input/output frequencies to avoid integer overflow during brute-force search.

## Control flow and integration
`rl6231_get_pre_div()` reads a regmap field and maps hardware codes 0..7 to dividers 1,2,3,4,6,8,12,16. `rl6231_calc_dmic_clk()` scans allowed dividers and chooses an index that keeps the DMIC frequency below or near the supported range while skipping divisors divisible by 3. `rl6231_pll_calc()` validates input frequency, checks presets, computes possible K range from target output, reduces frequencies by GCD/divider, then searches N/M/K for an exact or closest match. It returns bypass flags and codes in `struct rl6231_pll_code`. `rl6231_get_clk_info()` matches `sclk == rate * 256 * pre_div`.

## State and persistence
The file maintains no persistent state. It reads caller-owned regmaps and fills caller-owned PLL code structs. All lookup tables are static constants.

## Dependencies
It depends on regmap, `gcd()`, kernel error codes/logging, and the constants/type in `rl6231.h`. Downstream codec drivers are expected to write the returned codes into their own hardware registers.

## Risks and test signals
`regmap_read()` return value is ignored in `rl6231_get_pre_div()`, so bus failures can produce bogus divider results. PLL search uses integer arithmetic and `abs()` on unsigned-derived differences, so boundary tests around large frequencies matter. Test signals include known preset input/output pairs, invalid frequencies outside min/max, exact and approximate PLL matches, all pre-divider encodings, too-low/too-high DMIC base clocks, and `sclk/rate` combinations for each supported pre-divider.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6231.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6231.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rl6231.h

## Purpose
This header exposes RL6231-family PLL and clock helper limits, the PLL-code result structure, and the helper prototypes implemented in `rl6231.c`.

## Important APIs, types, and functions
`struct rl6231_pll_code` contains `m_bp`, `k_bp`, `m_code`, `n_code`, and `k_code` for callers to program codec PLL registers. Constants bound accepted PLL input and search ranges: input 256 kHz to 50 MHz, N max `0x1ff`, K max `0x1f`, and M max `0xf`. Prototypes expose DMIC clock calculation, PLL calculation, sysclk/rate divider lookup, and register pre-divider decode.

## Control flow and integration
Codec drivers include this header when they need Realtek shared clock math. The header itself does not define register addresses; callers supply target registers and shifts to `rl6231_get_pre_div()` and interpret returned codes according to their codec.

## State and persistence
No state is stored. The PLL-code struct is a transient output container whose fields become persistent only when a caller writes them into hardware.

## Dependencies
The prototypes mention `struct regmap`, so includers need a visible declaration or include path that provides regmap. The `.c` implementation includes regmap directly.

## Risks and test signals
The header does not include `<linux/regmap.h>` itself, so include-order assumptions should be build-tested. Callers must honor the min/max constants before programming hardware. Tests should compile representative Realtek codec drivers and verify returned `rl6231_pll_code` fields are mapped to the correct hardware bitfields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6231.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6347a.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rl6347a.c

## Purpose
This file provides shared low-level I2C read/write helpers for Realtek RL6347A-class devices that expose HDA verb-style register access. It is intended for use as regmap bus callbacks or codec helper operations.

## Important APIs, types, and functions
The exported APIs are `rl6347a_hw_write()` and `rl6347a_hw_read()`. Both take an opaque I2C client context. `rl6347a_hw_write()` handles indexed coefficient registers, updates the caller's `index_cache` when possible, packs a 32-bit HDA verb/value frame, and sends it with `i2c_master_send()`. `rl6347a_hw_read()` handles indexed coefficient reads, converts the command to a read verb, applies a special `AC_VERB_GET_AMP_GAIN_MUTE` index transformation, and performs a two-message I2C transfer.

## Control flow and integration
For register numbers `<= 0xff`, write and read first write `RL6347A_COEF_INDEX` and then access `RL6347A_PROC_COEF`. For normal writes, bytes 0..1 carry high register bits while byte 2 ORs register VID bits with high value bits, matching a 4-bit/12-bit VID encoding comment. Reads set bit `0x80000`, send the big-endian register command, and read back a big-endian 32-bit value.

## State and persistence
Persistent software state is limited to the optional `index_cache` in `struct rl6347a_priv`, updated on indexed writes. Hardware register state lives on the device.

## Dependencies
The file depends on I2C core, regmap types for `struct reg_default`, HDA verb definitions through `rl6347a.h`, and caller-provided `i2c_set_clientdata()` state.

## Risks and test signals
`rl6347a_hw_write()` recursively calls itself for coefficient index writes; this is bounded because `RL6347A_COEF_INDEX` is a full verb value above `0xff`, but it should be kept that way. Return handling treats short I2C sends/transfers as `-EIO`. Tests should cover indexed write cache update, indexed read path, amp gain/mute read transformation, endian correctness, short transfer errors, and ordinary vendor-register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6347a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6347a.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rl6347a.h

## Purpose
This header defines the HDA verb encoding helpers and private cache structure used by RL6347A-class Realtek codec I2C access helpers.

## Important APIs, types, and functions
`VERB_CMD(V, N, D)` packs an HDA verb, node ID, and data field. `RL6347A_VENDOR_REGISTERS`, `RL6347A_COEF_INDEX`, and `RL6347A_PROC_COEF` define the vendor coefficient access verbs. `struct rl6347a_priv` stores an index register cache pointer and size. Prototypes expose `rl6347a_hw_write()` and `rl6347a_hw_read()`.

## Control flow and integration
The `.c` helper uses these constants to detect small indexed registers and translate them to HDA coefficient-index/proc-coefficient operations over I2C. Codec drivers should set `struct rl6347a_priv` as I2C client data before using the helpers.

## State and persistence
The header defines the cache state shape but does not allocate it. The cache mirrors indexed coefficient default values for regmap users.

## Dependencies
It includes `<sound/hda_verbs.h>` for HDA verb constants and relies on `struct reg_default` from regmap headers being visible to includers that instantiate `rl6347a_priv`.

## Risks and test signals
The `VERB_CMD` macro lacks parentheses around individual arguments, so callers should pass simple values. Include-order for `struct reg_default` should be build-tested. Runtime tests should ensure coefficient-index constants remain above `0xff`; otherwise the recursive write guard in the implementation would become unsafe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rl6347a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt-sdw-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt-sdw-common.c

## Purpose
This file provides common helper functions for Realtek SoundWire SDCA codecs. It wraps Realtek indexed SDCA register access and decodes jack/headset/button events from SDCA controls and HID UMP buffers.

## Important APIs, types, and functions
Exported APIs are `rt_sdca_index_write()`, `rt_sdca_index_read()`, `rt_sdca_index_update_bits()`, `rt_sdca_btn_type()`, `rt_sdca_headset_detect()`, and `rt_sdca_button_detect()`. The index helpers build an address as `(nid << 20) | reg`. Button helpers map UMP nibble bits to ALSA jack button flags. Headset detection maps detected modes `0x03` and `0x05` to `SND_JACK_HEADPHONE` and `SND_JACK_HEADSET`.

## Control flow and integration
Codec drivers call index helpers to access Realtek-defined node/register space through regmap. Jack detection reads `RT_SDCA_CTL_DETECTED_MODE` from the jack codec entity and writes the same value to `RT_SDCA_CTL_SELECTED_MODE` when nonzero. Button detection checks HID current owner, skips if the device owns the buffer, reads message offset, reads three bytes from the HID buffer, checks the report ID, decodes two payload bytes, and returns ownership to the device.

## State and persistence
No persistent software state is kept. Hardware state changes include indexed register writes, selected headset mode writes, and HID owner restoration.

## Dependencies
The file depends on regmap, bit operations, SoundWire SDCA control macros, ALSA jack constants, and definitions from `rt-sdw-common.h`.

## Risks and test signals
`rt_sdca_index_update_bits()` performs a read-modify-write outside regmap's native update lock, so concurrent callers could lose updates if they target the same register. `rt_sdca_button_detect()` suppresses I/O errors by returning zero for some paths, which can hide button events during bus failures. Tests should cover SDCA headset modes, unknown mode returning no jack, HID owner transitions, report ID mismatch, each button bit mapping, regmap I/O error logs, and concurrent update behavior in codec users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt-sdw-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt-sdw-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/rt-sdw-common.h

## Purpose
This header exposes constants, control-private-data helpers, ALSA control initializer macros, and function prototypes shared by Realtek SoundWire SDCA codec drivers.

## Important APIs, types, and functions
Constants define SDCA entity numbers for jack codec, mic array, HID, and amplifier plus Realtek control IDs for selected mode, detected mode, HID current owner, and HID message offset. `struct rt_sdca_dmic_kctrl_priv` stores a register base, channel/control count, maximum value, and invert flag. `RT_SDCA_PR_VALUE()`, `RT_SDCA_FU_CTRL()`, and `RT_SDCA_EXT_TLV()` construct ALSA mixer controls with private SDCA data. Function prototypes expose index read/write/update, button type decode, headset detect, and button detect helpers.

## Control flow and integration
Codec drivers include this header to create consistent kcontrols and use the shared `.c` detection helpers. The macros package a compound-literal private data pointer into `private_value`, so the resulting controls expect static-duration use from file-scope control arrays.

## State and persistence
The header does not allocate persistent state beyond macro-created compound literals embedded in control definitions. Those values guide get/put callbacks in codec drivers.

## Dependencies
The macros use ALSA control constants such as `SNDRV_CTL_ELEM_IFACE_MIXER` and access flags, so including files must already include suitable ALSA headers. Function prototypes mention `struct regmap`.

## Risks and test signals
Compound-literal private values must remain valid; file-scope macro use is safe, but block-scope use would be dangerous. Missing direct includes for ALSA/regmap types place include-order requirements on users. Test signals include building all Realtek SoundWire codec users, verifying generated controls have correct access flags and TLV pointers, and validating callback private data interpretation for count/max/invert fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/rt-sdw-common.h -->
