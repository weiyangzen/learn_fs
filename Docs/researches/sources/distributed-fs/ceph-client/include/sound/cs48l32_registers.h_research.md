# sources/distributed-fs/ceph-client/include/sound/cs48l32_registers.h

## Purpose
This is the CS48L32 register map and bit-field catalog. It gives the codec driver symbolic addresses and masks for device ID, clocks, FLL, GPIO, regulators/micbias, inputs, PDM, ASPs, mixers, ISRC/EQ/DRC/LHPF, tone/noise/ultrasonic blocks, DSP memory windows, and interrupt state.

## Important APIs, Types, and Constants
The header is macro-only. Address macros include `CS48L32_DEVID`, `CS48L32_SYSTEM_CLOCK1`, `CS48L32_FLL1_CONTROL*`, `CS48L32_INPUT*`, `CS48L32_ASP*`, mixer input bases, `CS48L32_DSP1_*` memory ranges, and `CS48L32_IRQ1_*`. Field macros pair masks/shifts for device revision, sysclk source/frequency/enables, FLL lock/reference/divider values, input modes/volumes, ASP formats/widths, mixer source/volume, ISRC enables/rates, EQ/DRC controls, ultrasonic detector settings, and IRQ bits such as boot done, DSP MPU error, watchdog expiry, DSP IRQ, and FLL lock status.

## Control Flow
The driver uses these definitions in regmap reads/writes and regmap field helpers. Initialization reads ID/revision, releases MCU/reset state, enables clocks and FLL, configures sample rates, powers input paths, configures ASP and mixer routing, loads or controls DSP memory regions, and unmasks/handles IRQ events.

## State and Persistence
All state is hardware register state, usually shadowed by regmap cache. DSP memories and firmware-visible scratch/control windows are volatile across reset and power loss. IRQ mask/status registers define transient event state. Regulator and clock configuration must be re-applied after suspend/resume or reset.

## Dependencies and Integration Points
The map is consumed by the CS48L32 codec/MFD-style implementation, ASoC widgets/routes/DAIs, regmap, firmware/DSP code, IRQ handlers, and clock/FLL setup helpers. No functions are declared here.

## Risks and Edge Cases
The file has a large address surface, including high DSP memory windows, so off-by-one range handling can corrupt firmware memory or expose invalid regmap ranges. Shared field macros such as `CS48L32_INx_*`, `CS48L32_ASP_*`, and `CS48L32_MIXER_*` intentionally apply to repeated register banks; callers must compute the correct bank address. IRQ status/mask naming spans multiple banks and can be easy to mis-pair.

## Test Signals
Regmap range/readability tests, boot done IRQ handling, FLL lock tests, stream playback/capture over both ASPs, mixer route validation, DSP firmware load/control tests, and suspend/resume register-cache sync are the best signals.
