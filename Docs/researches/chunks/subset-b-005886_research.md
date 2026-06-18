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
