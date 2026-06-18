<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/pdata.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/arizona/pdata.h

## Purpose
This header defines platform data for Wolfson/Cirrus Arizona audio codec devices. It covers reset and IRQ configuration, GPIO defaults, regulator child platform data, clocking hints, jack/headphone/mic-detection policy, digital microphone references, MICBIAS setup, input/output modes, speaker/haptic settings, and general-purpose switch control.

## Important APIs, Types, And Functions
- GPIO field masks define direction, pull-up/down, level, polarity, output config, debounce, and function fields for packed GPIO default values.
- Limits define array sizes: `ARIZONA_MAX_GPIO`, `ARIZONA_MAX_INPUT`, `ARIZONA_MAX_MICBIAS`, `ARIZONA_MAX_OUTPUT`, `ARIZONA_MAX_AIF`, and `ARIZONA_MAX_PDM_SPK`.
- `struct arizona_micbias` describes voltage, external capacitor, discharge, soft-start, and bypass behavior.
- `struct arizona_micd_config` and `struct arizona_micd_range` describe mic-detect polarity/source/bias and impedance-to-key mappings.
- `struct arizona_pdata` aggregates reset GPIO, MICVDD/LDO1 regulator data, 32 kHz clock source, IRQ flags/base GPIO, GPIO defaults, AIF clocking limits, jack detection policy, mic detection tuning, DMIC references, micbias settings, input/output modes and limits, speaker mute/format, haptic actuator type, optional legacy IRQ GPIO, and GPSW setting.

## Control Flow
Platform or device-tree parsing fills `struct arizona_pdata`, which is embedded in `struct arizona` during core probe. The core and codec drivers use it to configure reset, IRQ polarity, child regulators, GPIO register defaults, clock source selection, jack/mic detection algorithms, input/output analog modes, speaker outputs, and haptic behavior.

## State And Persistence
The structure is configuration state copied into the core device. Once applied, it influences hardware register state for GPIOs, MICBIAS, jack detection, DMIC references, input/output routing, output volume limits, PDM speaker behavior, haptics, and GPSW. Runtime detection state is owned by core/codec drivers rather than this header.

## Dependencies And Integration Points
The header includes device-tree bindings and regulator platform-data headers for Arizona LDO1 and microphone supply children. It integrates with the MFD core, ASoC codec drivers, extcon/input headset detection, regulator framework, GPIO descriptors, and optional legacy gpiolib paths.

## Risks And Edge Cases
- Array fields are fixed-size and variant-sensitive; board data must not configure non-existent inputs, outputs, GPIOs, micbiases, or AIFs.
- Mic-detect impedance ranges and polarity configs directly affect headset button reporting and can cause false events if misordered or mismatched.
- `gpio_defaults` are packed register values; callers must compose fields with the provided masks/shifts.
- Legacy `irq_gpio` exists only under `CONFIG_GPIOLIB_LEGACY`; portable users should prefer descriptors and `irq_flags`.
- Output volume limits and micbias voltage settings need validation to avoid unsafe board-level behavior.

## Test Signals
Test platform-data and device-tree parsing, reset GPIO sequencing, IRQ polarity, regulator child setup, GPIO default programming, 32 kHz source selection, jack insert/remove and mic/button detection across configured impedance ranges, DMIC reference and micbias settings, input/output mode programming, speaker/haptic settings, and bounds handling for variant-specific array entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/pdata.h -->
