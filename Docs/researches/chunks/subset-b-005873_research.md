# sources/distributed-fs/ceph-client/include/linux/mfd/arizona/registers.h lines 1-4705

## Scope

This chunk covers the start of the Wolfson/Cirrus Logic Arizona MFD register-definition header through line 4705. It includes the header guard, the complete top-level register-address map from `ARIZONA_SOFTWARE_RESET` through DSP control/scratch registers, and the first large portion of generated-style field definitions through the first half of `ARIZONA_SLIMBUS_TX_CHANNEL_ENABLE`.

The file is not executable code. Its API surface is the preprocessor contract used by Arizona-family Linux drivers to address hardware registers and to pack/unpack bitfields with `*_MASK`, `*_SHIFT`, and `*_WIDTH` constants. The requested range ends mid-field group at `ARIZONA_SLIMTX4_ENA_MASK`; later fields for the same SLIMbus TX enable register are outside this chunk.

## Purpose

`registers.h` centralizes the hardware register ABI for Arizona audio codecs and companion functions. The address block names device-wide registers for reset, revision, control interfaces, write sequencer, tone/PWM/haptics, clocks, FLLs, regulators, microphone bias/detect, input and output paths, AIF ports, SLIMbus, DSP blocks, GPIO/pads, IRQ status/masks, audio effects, sample-rate conversion, and DSP memory/DMA control.

The field-definition block gives drivers a stable way to write individual bits without embedding magic constants. Common patterns are:

- A raw bit value such as `ARIZONA_FLL1_ENA` or `ARIZONA_OUT1L_MUTE`.
- A matching `*_MASK` for `regmap_update_bits()`.
- A `*_SHIFT` for positioning enumerated values.
- A `*_WIDTH` documenting field size.

This header is the shared register vocabulary for the MFD core, regmap cache tables, regmap-irq chips, regulator drivers, GPIO, haptics, jack/accessory detection, and ASoC codec drivers.

## Important APIs, Types, and Data

There are no C types or functions in this range; all data is exported as macros.

Register-address macros in lines 1-1190 define the coarse hardware map. Major address families include:

- Core/control interface: reset/revision, SPI and I2C auto-increment/busy state, write-sequencer control/PROM, wake/sequence trigger selection, and spare triggers.
- Utility generators: tone generator, PWM drive, comfort-noise generator, and haptics phase/intensity/duration/status registers.
- Clocking: 32 kHz clock, system/async clocks, sample-rate registers and status mirrors, output clocks, rate estimator, dynamic frequency scaling, and two FLL instances with synchronizer, spread-spectrum, and GPIO clock registers.
- Power and accessory: microphone charge pump, LDO1/LDO2, MICBIAS1-3, headphone short/status control, accessory detect mode, headphone detect, MICD clamp/detect/level/status, isolation, and analogue jack detect.
- Audio input/output: input enables/rate/ramp/HPF, IN1-IN4 analog/DMIC/digital-volume controls, output enables/status/rate/ramp, OUT1-OUT6 path config, DAC volume/limits, noise-gate source selection, DRE/EDRE, AEC loopback, PDM speaker, headphone short-circuit, and DAC/AEC compensation.
- Digital interfaces: AIF1/AIF2/AIF3 BCLK, pin control, rate, format, BCLK-per-frame, frame-slot, TX/RX enables, and force-write registers; SPDIF TX; SLIMbus rates and RX/TX channel enables.
- Routing and processing address map: mixer input source/volume registers for PWM, mic, noise, outputs, AIF TX, SLIM TX, SPDIF TX, EQ, DRC, HPLP, DSP, ASRC, and ISRC paths; effect/EQ/DRC/HPLP/ASRC/ISRC control; ANC/FCL/FCR coefficient ranges; DSP1-DSP4 control/clock/status/DMA/scratch registers.

Field macros from line 1195 onward define bit layouts for many of those registers. Notable groups in this chunk include:

- Reset/revision and bus status fields: `ARIZONA_SW_RST_DEV_ID1_MASK`, `ARIZONA_DEVICE_REVISION_MASK`, `ARIZONA_SPI_*`, `ARIZONA_I2C1_BUSY`, and `ARIZONA_SPI_BUSY`.
- Write sequencer state and triggers: `ARIZONA_WSEQ_ABORT`, `ARIZONA_WSEQ_START`, `ARIZONA_WSEQ_ENA`, `ARIZONA_WSEQ_CURRENT_INDEX_MASK`, `ARIZONA_LOAD_DEFAULTS`, sequence address fields for sample-rate detection and always-on triggers, and wake/event enable bits.
- Clock/FLL control: `ARIZONA_SYSCLK_*`, `ARIZONA_ASYNC_CLK_*`, `ARIZONA_OPCLK*`, rate-estimator fields, `ARIZONA_FLL1_*`, `ARIZONA_FLL2_*`, synchronizer N/theta/lambda/fratio/source/gain fields, and spread-spectrum/GPIO divider fields.
- Regulator/mic/accessory fields: charge-pump enable/bypass/discharge, LDO voltage select/bypass/high-power bits, MICBIAS level/fast/rate/discharge/bypass/enable bits, headphone impedance/poll/done/level fields, MICD debounce/bias/source/rate/ADC/status fields, and jack detect enables.
- Input/output fields: per-channel enable/status bits, analog PGA volume, HPF/mode/OSR/DMIC support, digital volume/mute/update bits, output path low-power/OSR/mono/ANC/PGA fields, DAC volume limits, noise-gate source/global control, DRE/EDRE enable/control, AEC loopback, speaker mute/format, short-circuit enable, and compensation coefficient selectors.
- Digital interface fields: AIF BCLK inversion/force/master/frequency, TX/RX LRCLK source/inversion/force/master, data tri-state, AIF rate/tri-state/format, BCLK-per-frame, slot length/word length, slot indexes, TX/RX channel enables, SPDIF channel-status fields, SLIMbus framer gear/rates, and RX/TX channel enable bits.

The chunk includes chip-specific deviations, notably `WM8998_*` variants for headphone detect rate and DRE enable bit assignments. Those aliases let shared code or chip-specific drivers choose the correct bit layout while using the same physical register address.

## Control Flow

The header itself has no runtime control flow, but it encodes the register flow used by callers:

1. The MFD core powers the device, reads `ARIZONA_SOFTWARE_RESET` as an ID register, optionally writes it to reset, waits for boot, reads `ARIZONA_DEVICE_REVISION`, and selects chip-specific regmap tables and child devices.
2. Regmap tables in `drivers/mfd/*-tables.c` use these addresses to classify readable/volatile/precious/default registers and to configure `regmap_irq_chip` status, mask, and ack bases.
3. Child drivers use the field macros with regmap helpers. For example, regulator code maps LDO voltage selection through `ARIZONA_LDO1_CONTROL_1` and `ARIZONA_LDO1_VSEL_MASK`; haptics writes `ARIZONA_HAPTICS_PHASE_2_INTENSITY` and `ARIZONA_HAP_CTRL_MASK`; GPIO reads and updates `ARIZONA_GPIO1_CTRL + offset`; codec DAPM widgets toggle bits in `ARIZONA_OUTPUT_ENABLES_1`.
4. ASoC codec setup uses AIF base addresses, FLL control bases, input/output control offsets, mixer source/volume addresses, and sample-rate/routing fields to expose ALSA controls and to build audio paths.
5. IRQ handling uses `ARIZONA_INTERRUPT_STATUS_*`, `*_MASK`, raw status, pin status, AOD IRQ, and wake/trigger bits to map nested regmap IRQs to Linux IRQs and wake events.

Repeated address spacing is part of the implicit flow. Many consumers compute register addresses by adding channel offsets, such as `ARIZONA_IN1L_CONTROL + channel * 8`, `ARIZONA_OUTPUT_PATH_CONFIG_1L + channel * 4`, or `ARIZONA_AIF1_BCLK_CTRL` as the base of an AIF register block. The constants therefore define both named registers and layout arithmetic.

## State and Persistence Behavior

These macros describe hardware state, not kernel-owned persistence. Values written through them live in device registers and are mediated by regmap caching, runtime PM, reset, and power sequencing.

Volatile/status state includes busy bits, boot/write-sequencer indexes, sample-rate status, FLL clock status via raw interrupt registers outside some immediate field groups, headphone/MICD detection status, input/output enable status, haptics one-shot status, SLIMbus port status, and IRQ status/raw status registers. Reads of these fields must respect volatile regmap classification in the chip table files rather than relying on cached values.

Mutable configuration state includes clocks, FLL parameters, write-sequencer triggers, regulator and MICBIAS setup, jack/MICD thresholds, input/output path controls, digital volumes, routing selectors, AIF format/slot settings, PDM/SPDIF/SLIMbus settings, DSP DMA controls, and effect coefficients. Most of this state is lost on hardware reset or power removal and is restored by the driver through regmap cache sync, probe-time defaults, or ALSA/DAPM state reconstruction.

Some registers interact with more persistent hardware behavior. `ARIZONA_WSEQ_OTP_WRITE` and write-sequencer PROM/default-load controls imply nonvolatile or boot-sequence programming paths. Wake, AOD, jack-detect, and interrupt-mask registers affect suspend/resume behavior. Regulator and clock fields control whether later register accesses are valid, so incorrect state can make following regmap operations fail or read stale cached data.

## Dependencies and Integration Points

The header depends only on the C preprocessor and the Linux include path; it does not include other headers. Its constants are consumed by:

- `drivers/mfd/arizona-core.c` for reset, device ID/revision, FLL/sysclk freerun support, boot sequencing, and cache/power transitions.
- `drivers/mfd/arizona-irq.c` and chip table files for regmap IRQ status/mask/ack bases and interrupt wake behavior.
- `drivers/mfd/wm5102-tables.c`, `wm5110-tables.c`, `wm8997-tables.c`, `wm8998-tables.c`, and `cs47l24-tables.c` for register defaults, readability, volatility, and precious register policy.
- `sound/soc/codecs/arizona.c` plus chip-specific codec drivers for ALSA controls, DAPM widgets, FLL setup, AIF setup, input/output volumes, routes, jack detection, and DSP/audio processing integration.
- `drivers/regulator/arizona-ldo1.c` and `arizona-micsupp.c` for regulator descriptors backed by register fields.
- `drivers/gpio/gpio-arizona.c` for GPIO direction/level/control registers.
- `drivers/input/misc/arizona-haptics.c` for force-feedback playback through haptics registers.
- Platform quirks such as x86 Android tablet setup code that may preconfigure Arizona registers.

The principal external API is Linux `regmap`: callers pass these addresses and masks to `regmap_read()`, `regmap_write()`, `regmap_update_bits()`, `regmap_update_bits_async()`, regcache helpers, and regmap-irq setup. The ASoC layer also embeds constants in `SOC_SINGLE`, `SOC_ENUM`, `SND_SOC_DAPM_PGA_E`, and related control/widget macros.

## Risks

Register ABI drift is the main risk. A wrong address, mask, shift, or chip-specific alias can silently write the wrong hardware field. This is especially risky where drivers compute offsets from base macros rather than naming every register directly.

Bitfield duplication can hide semantic differences. Generic names such as `ARIZONA_IN_VU`, `ARIZONA_OUT_VU`, and repeated AIF/LRCLK fields appear under many registers. They are only safe because the hardware reuses the same bit position; changing one apparent duplicate without auditing every user could break unrelated paths.

Chip variants do not always share bit assignments. The `WM8998_*` DRE and headphone-detect fields show that not every Arizona-family device is layout-compatible. Shared code must select the correct macro set for the detected device type.

Status and write-one/ack registers need correct regmap volatility and precious classification. IRQ status, raw status, detect status, sequencer state, and control-interface busy bits should not be treated like ordinary cached configuration. Incorrect classification can lose interrupts, return stale status, or acknowledge hardware unexpectedly.

Power and clock dependencies are tight. Many fields are meaningful only when supplies, SYSCLK, FLLs, or DAPM paths are active. Updating audio path, haptics, GPIO input, MICD, or jack-detect registers while runtime suspended may require cache-only writes or an explicit resume.

Generated-style names can encode mistakes that compile cleanly. Examples in the covered range include odd comments and edge cases such as `ARIZONA_SPD1_CLKACU_WIDTH` being `0` despite a mask, and the chunk ending in the middle of the SLIMbus TX enable fields. Tests should validate against real hardware documentation rather than assuming macro regularity.

Write sequencer and OTP/default controls have high blast radius. Misusing `ARIZONA_WSEQ_OTP_WRITE`, `ARIZONA_LOAD_DEFAULTS`, or trigger sequence address fields could alter boot-time sequencing or cause unexpected register programming.

Audio-user-visible failures may be subtle. Incorrect masks for volume, mute, ramp, AIF slot, sample-rate, FLL, or routing fields can compile and probe successfully but manifest as silence, swapped channels, distorted sample rates, broken jack detection, missed wake events, or intermittent suspend/resume failures.

## Test and Validation Signals

Build validation should compile all Arizona MFD, regulator, GPIO, input, and ASoC codec users. Undefined macro, duplicate-definition, and control/widget construction failures catch many header regressions immediately.

Regmap-table validation should compare every address in this chunk against each chip's readable/volatile/default tables. Reset, revision, IRQ status/mask/ack, FLL, input/output, AIF, and SLIMbus ranges are especially important because they are used across multiple drivers.

Hardware probe tests should verify ID read from `ARIZONA_SOFTWARE_RESET`, revision masking with `ARIZONA_DEVICE_REVISION_MASK`, software reset behavior, boot completion, runtime PM resume/suspend, and regcache sync after reset.

Clock tests should exercise SYSCLK, async clock, output clocks, FLL1/FLL2 enable/freerun/synchronizer settings, and rate estimator status. Good signals include successful FLL lock/clock-ok handling, correct sample-rate status fields, and stable AIF audio at expected rates.

Audio-path tests should toggle input enables, HPF, PGA/digital volumes, mutes, output enables, DAC limits, AIF formats/slots, PDM/SPDIF/SLIMbus paths, and mixer routing. ALSA mixer changes should produce matching regmap writes and audible or loopback-verifiable behavior.

Accessory and wake tests should cover jack detect, MICD clamp/detect/level/status, headphone impedance detect, wake triggers, AOD interrupts, IRQ masks, and suspend wake. Expected signals are correct nested IRQ delivery, no stale status reads, and correct wake source reporting.

Peripheral tests should cover LDO voltage/bypass/high-power behavior, MICBIAS enable/level/rate/discharge, GPIO input/output/cache handling, and haptics force-feedback intensity/control sequences.

Static validation should check field macros against vendor register documentation or generated source input, including mask/shift/width consistency and variant-specific fields such as `WM8998_HP_RATE_*` and `WM8998_DRE*`.

## Cross-Chunk Notes

This is the first chunk for `sources/distributed-fs/ceph-client/include/linux/mfd/arizona/registers.h`. Later chunks continue the SLIMbus TX enable field group and then cover GPIO field definitions, IRQ bit definitions, DSP/effects fields, mixer fields, and any terminal header content. The merge lane should preserve that this chunk establishes the shared address map and the early-to-mid field definitions used by most Arizona child drivers.
