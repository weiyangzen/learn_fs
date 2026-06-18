# Research: sources/distributed-fs/ceph-client/include/linux/mfd/wm8994/registers.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005885`: lines 1-4378, `Docs/researches/chunks/subset-b-005885_research.md`
- `subset-b-005886`: lines 4379-4817, `Docs/researches/chunks/subset-b-005886_research.md`

## Chunk Research

### subset-b-005885: lines 1-4378

# sources/distributed-fs/ceph-client/include/linux/mfd/wm8994/registers.h lines 1-4378

## Purpose

This chunk is the public register-definition header for the Wolfson/Cirrus WM8994 family codec MFD. It contains preprocessor constants only: register addresses, register-count/cache bounds, and bitfield mask/shift/width definitions used by the WM8994 core, ASoC codec, interrupt, GPIO, regulator, jack-detect, clocking, DSP, and firmware-control code to address the hardware register map without magic numbers.

The covered range begins with the include guard and register-address map and continues through field definitions up to the first `WM8994_SPKMODE_PU` macro in `R1825 (0x721) - Pull Control (2)`. The requested slice stops at line 4378, so later field definitions for the rest of pull control, interrupts, GPIOs, DSP, and write-sequencer fields are outside this chunk even though their register addresses may already be listed in the address table.

## Important APIs, Types, And Constants

There are no C functions, structs, enums, or runtime APIs in this slice. Its API surface is macro names consumed by driver code.

Key address constants:

- Core analogue/power path: `WM8994_SOFTWARE_RESET`, `WM8994_POWER_MANAGEMENT_1` through `_6`, input/output mixer, volume, Class-D, charge-pump, Class-W, DC-servo, headphone, MICBIAS, and LDO registers.
- Chip/control and sequencing: `WM8994_CHIP_REVISION`, `WM8994_CONTROL_INTERFACE`, `WM8994_WRITE_SEQUENCER_CTRL_1`, `WM8994_WRITE_SEQUENCER_CTRL_2`, plus `WM8994_WRITE_SEQUENCER_0` through `_511`.
- Clocking and FLL: AIF1/AIF2 clocking, sample-rate, rate-status, FLL1/FLL2 control, and WM8958 EFS registers.
- Digital audio interfaces: AIF1/AIF2 control, master/slave, BCLK, LRCLK, data inversion, and WM8958 AIF3 registers.
- Digital audio processing: AIF volume/filter, noise gate, DRC, EQ coefficient windows, DAC/ADC mixer routing, DAC soft-mute, oversampling, and sidetone.
- GPIO/IRQ and pins: GPIO 1-11, WM1811 jack-detect alias at `0x705`, pull controls, interrupt status/mask/control, and debounce addresses.
- WM8958 DSP/firmware parameter windows: DSP2 program/config/status/config registers and firmware, MBC, crossover/filter, RMS limit, and write-sequencer memory ranges.

Important global limits:

- `WM8994_REGISTER_COUNT` is `736`, used by driver tables sized to the sparse register cache.
- `WM8994_MAX_REGISTER` is `0x31FF`, matching the final write-sequencer slot.
- `WM8994_MAX_CACHED_REGISTER` is `0x749`, excluding high DSP/firmware/write-sequencer windows from the normal cached range.

Field-definition pattern:

- Single-bit fields usually expose the bit value, `_MASK`, `_SHIFT`, and `_WIDTH`, for example `WM8994_BIAS_ENA`, `WM8994_CP_ENA`, `WM8994_AIF1_MSTR`, and `WM8994_DAC_OSR128`.
- Multi-bit fields expose `_MASK`, `_SHIFT`, and `_WIDTH`, for example `WM8994_VMID_SEL_MASK`, `WM8994_FLL1_N_MASK`, `WM8994_AIF1_WL_MASK`, and `WM8994_AIF2DRC_KNEE_IP_MASK`.
- Stereo-linked volume update bits are intentionally reused across left/right registers, such as `WM8994_AIF1DAC1_VU`, `WM8994_AIF2DAC_VU`, `WM8994_DAC1_VU`, and `WM8994_DAC2_VU`.
- Variant-specific fields use prefixes such as `WM8958_` and `WM1811_`, but they live in the same header because the related devices share a large register map.

## Control Flow

This header has no executable control flow. Runtime behavior is created by consumers that combine these constants with register-map helpers such as `regmap_update_bits()`, `regmap_write()`, IRQ status reads, ASoC DAPM routing, mixer control callbacks, and clock/FLL configuration routines.

The implied operational flows are hardware sequencing flows:

- Power-up and bias flows set `BIAS_ENA`, `VMID_SEL`, MICBIAS, input/output enable, charge-pump, anti-pop, and DC-servo fields in a defined order to avoid pops and unsafe analogue states.
- Audio routing flows enable mixer path bits such as `INx_TO_MIXINx`, `DACx_TO_MIXOUTx`, `MIXOUTx_TO_LINEOUTx`, `DACx_TO_SPKMIXx`, and AIF-to-DAC or ADC-to-AIF routing bits.
- Clock setup flows select AIF clock sources, BCLK/LRCLK dividers, FLL fractional/integer parameters, and sample-rate fields before enabling digital paths.
- DSP/EQ/DRC flows write coefficient and control registers using the address constants and set enable bits after coefficients are in place.
- Pin and accessory flows configure pull-up/pull-down bits, MICBIAS thresholds, WM8958 mic-detect status fields, and WM1811 jack-detect fields.

## State And Persistence Behavior

The state represented here lives in hardware registers and, for cached registers, in the Linux regmap/cache layer. The header itself stores no state.

The distinction between `WM8994_MAX_REGISTER` and `WM8994_MAX_CACHED_REGISTER` is important. The hardware address space extends to `0x31FF`, but the normal cached register range ends at `0x749`; high firmware/DSP and write-sequencer windows are likely volatile, sparse, or special-purpose and should not be blindly cached by generic register-cache code.

Many fields persist only while the codec is powered and may reset on software reset or hardware power loss. Fields like soft-mute, mixer routing, volume, FLL configuration, MICBIAS, pull-control, and DRC/EQ settings need reprogramming during probe, resume, or bias-level transitions according to the owning driver logic. Write-sequencer memory and DSP/firmware windows are especially sensitive because they can encode hardware-side state machines or firmware parameters.

## Dependencies And Integration Points

Primary integration points are Linux kernel driver layers, not this repository's distributed filesystem logic:

- MFD core code includes this header to identify and cache registers, expose child devices, and service IRQs.
- ASoC codec code uses the address and bitfield macros in DAPM widgets, DAI operations, kcontrols, clock/FLL code, EQ/DRC controls, and bias/power sequencing.
- Regulator code can use LDO and MICBIAS definitions for enable, discharge, and voltage-selection behavior.
- GPIO/irq/jack-detect code consumes GPIO, pull-control, interrupt, MICBIAS, mic-detect, and WM1811 jack-detect definitions.
- Firmware/DSP loaders consume WM8958 DSP2, firmware ID/version, MBC, filter, RMS, and write-sequencer address constants.

The header depends only on the C preprocessor and include guards. It intentionally avoids pulling other headers, so it is safe to include from multiple kernel subsystems.

## Risks And Edge Cases

- Macro values are hardware ABI. Any incorrect address, mask, shift, or width can silently program the wrong register bit and cause audio failure, unsafe analogue output, broken clocking, failed jack detection, or firmware/DSP corruption.
- Some macro names are duplicated intentionally for shared update bits or repeated field semantics across paired registers. Consumers must rely on register address plus field macro context, not just macro name uniqueness.
- Device-family prefixes matter. `WM8958_` and `WM1811_` definitions may not apply to base WM8994 silicon even when the address is shared or adjacent.
- Register aliases exist, notably `WM1811_JACKDET_CTRL` sharing address `0x705` with `WM8994_GPIO_6`. Variant-aware code must avoid treating that address as both a normal GPIO and a jack-detect control register at the same time.
- The sparse register map has large gaps and high windows. Iterating from zero to `WM8994_MAX_REGISTER` without valid-register checks can touch reserved or volatile areas.
- The chunk boundary is mid-register-definition at `R1825 (0x721) - Pull Control (2)`. A final merged report must combine the continuation before describing pull control, interrupt, GPIO, or later field definitions as complete.
- Generated-style macro headers are easy to regress through formatting or regeneration churn. Manual edits should be checked against the datasheet and existing driver tables.

## Test Signals

Useful validation signals for changes involving this header:

- Kernel build coverage for all WM8994-family drivers that include this header, with warnings treated seriously because macro renames or duplicate definitions can break consumers at compile time.
- Static checks that register defaults/cache tables reference addresses within `WM8994_MAX_CACHED_REGISTER` unless deliberately accessing volatile/high windows.
- Driver probe on WM8994, WM8958, and WM1811 hardware or emulation sufficient to verify regmap initialization, readable/writable/volatile callbacks, and child-device registration.
- ASoC runtime tests for playback/capture on AIF1 and AIF2, FLL lock and sample-rate changes, mixer routing, volume update bits, soft mute, EQ/DRC enable paths, and suspend/resume restore.
- Accessory tests for MICBIAS/mic-detect thresholds and WM1811 jack-detect behavior, especially at the shared `0x705` address.
- Regmap trace or debugfs inspection showing writes use the intended register addresses and masks when enabling power rails, clocks, audio paths, and pull controls.

### subset-b-005886: lines 4379-4817

# sources/distributed-fs/ceph-client/include/linux/mfd/wm8994/registers.h lines 4379-4817

## Purpose

This chunk is the tail of the WM8994-family register definition header. It completes the `R1825 (0x721) - Pull Control (2)` speaker-mode pull-up bit started in the previous chunk, then defines bitfields for the WM8994 interrupt controller and the WM8958 DSP2 control/version registers.

The section is purely declarative: it exposes preprocessor constants for register bits, masks, shifts, and widths. These macros form the hardware ABI used by the MFD interrupt controller, regmap policy, ASoC jack-detection code, and WM8958 DSP2 firmware/runtime control. The file closes the include guard at line 4817.

## Important APIs, Types, And Constants

There are no functions, structs, or runtime types in this range. The public API is a set of macro names consumed by other driver code.

Key interrupt register field groups:

- `WM8994_GP1_EINT` through `WM8994_GP11_EINT` define GPIO interrupt status bits in `R1840 (0x730) - Interrupt Status 1`. Each has matching `_MASK`, `_SHIFT`, and `_WIDTH` constants. Bits are packed from GPIO1 at bit 0 through GPIO11 at bit 10.
- `WM8994_TEMP_SHUT_EINT`, `WM8994_MIC1_DET_EINT`, `WM8994_MIC1_SHRT_EINT`, `WM8994_MIC2_DET_EINT`, `WM8994_MIC2_SHRT_EINT`, `WM8994_FLL1_LOCK_EINT`, `WM8994_FLL2_LOCK_EINT`, `WM8994_SRC1_LOCK_EINT`, `WM8994_SRC2_LOCK_EINT`, `WM8994_AIF1DRC1_SIG_DET_EINT`, `WM8994_AIF1DRC2_SIG_DET_EINT`, `WM8994_AIF2DRC_SIG_DET_EINT`, `WM8994_FIFOS_ERR_EINT`, `WM8994_WSEQ_DONE_EINT`, `WM8994_DCS_DONE_EINT`, and `WM8994_TEMP_WARN_EINT` define `R1841 (0x731) - Interrupt Status 2`.
- `*_STS` equivalents in `R1842 (0x732) - Interrupt Raw Status 2` expose raw state for the same non-GPIO interrupt sources. These are used when software needs current hardware level/status rather than the latched interrupt status.
- `WM8994_IM_GP1_EINT` through `WM8994_IM_GP11_EINT` define mask bits in `R1848 (0x738) - Interrupt Status 1 Mask`.
- `WM8994_IM_TEMP_SHUT_EINT` through `WM8994_IM_TEMP_WARN_EINT` define mask bits in `R1849 (0x739) - Interrupt Status 2 Mask`.
- `WM8994_IM_IRQ` is the top-level interrupt mask/control bit in `R1856 (0x740) - Interrupt Control`.
- `WM8994_TEMP_SHUT_DB`, `WM8994_MIC1_DET_DB`, `WM8994_MIC1_SHRT_DB`, `WM8994_MIC2_DET_DB`, `WM8994_MIC2_SHRT_DB`, and `WM8994_TEMP_WARN_DB` define debounce enable bits in `R1864 (0x748) - IRQ Debounce`.

Key WM8958 DSP2 field groups:

- `WM8958_DSP2_ENA` controls `R2304 (0x900) - DSP2_Program`, indicating or enabling DSP2 program execution.
- `WM8958_MBC_SEL_MASK`/`SHIFT`/`WIDTH` and `WM8958_MBC_ENA` control `R2305 (0x901) - DSP2_Config`, selecting the DSP path and enabling the multiband compressor/DSP data-path insertion.
- `WM8958_DSP2_MAGIC_NUM_MASK`, `WM8958_DSP2_RELEASE_YEAR_MASK`, `WM8958_DSP2_RELEASE_MONTH_MASK`, `WM8958_DSP2_RELEASE_DAY_MASK`, `WM8958_DSP2_RELEASE_HOURS_MASK`, `WM8958_DSP2_RELEASE_MINS_MASK`, `WM8958_DSP2_MAJOR_VER_MASK`, `WM8958_DSP2_MINOR_VER_MASK`, and `WM8958_DSP2_BUILD_VER_MASK` expose DSP firmware identity and build metadata registers from `0xA00` through `0xA05`.
- `WM8958_DSP2_RUN`, `WM8958_DSP2_RUNR`, `WM8958_DSP2_STOP`, `WM8958_DSP2_STOPI`, `WM8958_DSP2_STOPS`, and `WM8958_DSP2_STOPC` define command/status-style bits in `R2573 (0xA0D) - DSP2_ExecControl`.

## Control Flow

This header has no executable control flow. The control flow is in consumers that combine these constants with regmap and ASoC component helpers.

Interrupt flow:

- `drivers/mfd/wm8994-irq.c` builds a `struct regmap_irq` table using the `*_EINT` bits from this chunk. GPIO interrupts use register offset 0 from `WM8994_INTERRUPT_STATUS_1`; non-GPIO interrupts use register offset 1 from `WM8994_INTERRUPT_STATUS_2`.
- The same IRQ driver registers a `regmap_irq_chip` with `status_base = WM8994_INTERRUPT_STATUS_1`, `mask_base = WM8994_INTERRUPT_STATUS_1_MASK`, and `ack_base = WM8994_INTERRUPT_STATUS_1`, so these bit masks drive status decoding, mask writes, and interrupt acknowledgement.
- During IRQ initialization, `wm8994_irq_init()` writes `0` to `WM8994_INTERRUPT_CONTROL` to enable the top-level interrupt if `WM8994_IM_IRQ` had masked it.
- For microphone handling, `sound/soc/codecs/wm8994.c` enables debounce bits in `WM8994_IRQ_DEBOUNCE`, reads `WM8994_INTERRUPT_RAW_STATUS_2`, and tests `WM8994_MIC1_DET_STS` and `WM8994_MIC1_SHRT_STS` to report headset/headphone/button state.

DSP2 flow:

- `sound/soc/codecs/wm8958-dsp2.c` checks `WM8958_DSP2_PROGRAM & WM8958_DSP2_ENA` to avoid restarting an already running DSP.
- Start paths load firmware/configuration, set `WM8958_DSP2_ENA`, write `WM8958_DSP2_RUNR` to `WM8958_DSP2_EXECCONTROL`, then update `WM8958_DSP2_CONFIG` with `path << WM8958_MBC_SEL_SHIFT` plus `WM8958_MBC_ENA`.
- Stop paths clear `WM8958_MBC_ENA`, write `WM8958_DSP2_STOP` to `WM8958_DSP2_EXECCONTROL`, clear `WM8958_DSP2_ENA`, and disable the DSP2 clock in a separate clocking register defined earlier in the header.

## State And Persistence Behavior

The state represented here is hardware register state, with some visibility through regmap caching and volatility rules. The header itself persists no state.

Interrupt status bits are event or status state owned by the codec hardware. `WM8994_INTERRUPT_STATUS_1` and `_2` are marked volatile in `drivers/mfd/wm8994-regmap.c`, so regmap should not treat cached values as authoritative. `WM8994_INTERRUPT_RAW_STATUS_2` is readable/writable per the regmap access policy but is not listed as volatile in the excerpted callbacks, so consumers that require live raw microphone state explicitly read it when needed.

Interrupt mask and debounce registers are configuration state. Their values affect future interrupt delivery and signal conditioning and must be set during probe, jack-detection setup, resume, or runtime reconfiguration as appropriate. The top-level `WM8994_IM_IRQ` bit gates the entire interrupt output.

DSP2 program/config/exec registers model firmware and algorithm runtime state for WM8958-family devices. The regmap layer marks several DSP2 identity and execution/configuration registers readable and some volatile, including `WM8958_DSP2_EXECCONTROL` and version/config memory registers. DSP enable and MBC path selection interact with firmware downloads, codec clocks, AIF power state, and `wm8994->dsp_active`; after reset or power loss the DSP must be re-enabled and firmware/configuration may need to be restored by the codec driver.

## Dependencies And Integration Points

This chunk depends only on the C preprocessor and the include guard opened earlier in the file. Its consumers provide the real subsystem integration:

- Linux MFD/regmap IRQ support consumes `*_EINT` and `IM_*` masks through `struct regmap_irq` and `struct regmap_irq_chip`.
- `drivers/mfd/wm8994-regmap.c` uses the register-address constants defined earlier, plus these field definitions indirectly, to declare interrupt and DSP2 registers readable, writable, or volatile.
- ASoC codec jack-detection logic uses debounce and raw-status bits to translate hardware microphone detect/short events into ALSA jack reports.
- ASoC WM8958 DSP code uses the DSP2 enable, run/stop, MBC select, and MBC enable bits to load firmware, start one of several DSP algorithms, insert it into the selected audio path, and shut it down.
- Variant prefixes matter: `WM8958_*` DSP2 fields are not generic WM8994 controls, while `WM8994_*` interrupt fields apply to the shared interrupt block used by the family.

## Risks And Edge Cases

- These macros are hardware ABI. A wrong bit value, mask, or shift can silently acknowledge the wrong interrupt, leave an interrupt masked, report the wrong jack state, or command the DSP incorrectly.
- Interrupt Status 1 GPIO bits are densely packed and easy to transpose. The local IRQ table should map `WM8994_IRQ_GPIO(n)` to the matching `WM8994_GPn_EINT`; the nearby consumer currently maps GPIO9 to `WM8994_GP8_EINT`, which is a risk signal for this area even though it is outside this header chunk.
- The status, raw-status, and mask registers intentionally reuse the same bit layout with different prefixes. Using an `IM_*` mask where a status bit is expected, or a raw `*_STS` bit where a latched `*_EINT` bit is expected, can make code compile while changing runtime semantics.
- Debounce bits only exist for temperature and microphone-related signals, not for every interrupt source. Generic debounce logic must not assume every interrupt bit has a matching `_DB` field.
- `WM8994_IM_IRQ` is a single top-level gate. Accidentally setting it while configuring per-source masks can suppress all interrupt delivery and make child IRQ users appear broken.
- DSP2 command bits in `WM8958_DSP2_EXECCONTROL` look like independent bit flags, but consumers treat writes such as `WM8958_DSP2_RUNR` and `WM8958_DSP2_STOP` as commands/status interactions. Read-modify-write may be unsafe if the hardware expects command writes.
- DSP2 fields are WM8958-specific in a shared family header. Unconditional use on base WM8994 or other variants could access unsupported addresses or no-op hardware.
- The chunk is the end of the header. Any generated update must preserve the final `#endif`; losing it would break every includer.

## Test Signals

Useful validation signals for changes touching this chunk:

- Kernel build coverage for `drivers/mfd/wm8994-irq.c`, `drivers/mfd/wm8994-regmap.c`, `sound/soc/codecs/wm8994.c`, and `sound/soc/codecs/wm8958-dsp2.c`; macro renames or removed definitions should fail at compile time.
- IRQ functional testing on WM8994-family hardware: GPIO1-11 interrupt delivery, FLL/SRC lock interrupts, DCS/write-sequencer completion, FIFO error, DRC signal detect, and temperature warning/shutdown events.
- Regmap IRQ trace/debugfs inspection showing `WM8994_INTERRUPT_STATUS_1/2`, mask registers, and acknowledge writes use the intended bit positions.
- Jack-detection tests that toggle microphone detect and short conditions and verify debounce programming in `WM8994_IRQ_DEBOUNCE`, raw status reads from `WM8994_INTERRUPT_RAW_STATUS_2`, and ALSA jack reports.
- Suspend/resume or runtime-PM tests confirming interrupt masks/debounce settings and top-level interrupt enable survive or are restored after power transitions.
- WM8958 DSP2 playback-path tests for MBC, VSS/HPF, and enhanced EQ modes: firmware load, `DSP2_ENA` set/clear, `DSP2_RUNR` start, `DSP2_STOP` stop, MBC path selection, and clean DSP clock disable.
- Variant testing that exercises WM8994, WM1811, and WM8958 paths separately, ensuring WM8958 DSP2 definitions are only used where the silicon supports them.
