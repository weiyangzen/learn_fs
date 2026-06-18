<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/core.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/arizona/core.h

## Purpose
This header defines the internal MFD core contract for Wolfson/Cirrus Arizona audio codec families such as WM5102, WM5110, WM8997, WM8280, WM8998, WM1814, WM1831, and CS47L24. It centralizes core supplies, clocks, IRQ IDs, device state, notifier support, IRQ helper APIs, 32 kHz clock reference APIs, and variant patch hooks.

## Important APIs, Types, And Functions
- Type and clock enums: `enum arizona_type`, `ARIZONA_MCLK1`, `ARIZONA_MCLK2`, and `ARIZONA_NUM_MCLK`.
- IRQ ABI: `ARIZONA_IRQ_*` logical interrupt IDs cover GPIOs, jack/mic/headphone detection, DSP RAM/IRQ signals, speaker faults, clock/FLL/ASRC/AIF errors, boot completion, DCS, short-circuit events, and `ARIZONA_NUM_IRQ`.
- `struct arizona` stores regmap, parent device, variant/revision, regulator supplies, DCVDD state, platform data, IRQ domains/chips, headphone-detect state, clock lock/refcount, MCLK handles, DAPM pointer, TDM settings, DAC compensation state, and notifier chain.
- Helper APIs include `arizona_call_notifiers()`, `arizona_clk32k_enable()`, `arizona_clk32k_disable()`, `arizona_request_irq()`, `arizona_free_irq()`, and `arizona_set_irq_wake()`.
- Patch hooks include `wm5102_patch()`, `wm5110_patch()`, `cs47l24_patch()`, `wm8997_patch()`, and `wm8998_patch()`.

## Control Flow
The core driver identifies the variant, powers supplies, initializes regmap IRQ chips and domains, applies variant patches, parses platform data, and registers audio/regulator/GPIO/IRQ children. Codec and accessory-detection drivers request logical IRQs through `arizona_request_irq()`, use `arizona_clk32k_enable()`/disable with reference counting, and publish cross-component events through the blocking notifier chain.

## State And Persistence
Software state in `struct arizona` tracks power-supply ownership, whether DCVDD is external, IRQ-domain handles, 32 kHz clock reference count, MCLK handles, DAPM context, TDM slots/widths, DAC compensation fields, and notifier subscribers. Hardware state includes codec registers, IRQ masks/status, clocks/FLLs, DSP state, jack detection, speaker protection, GPIOs, and audio route/power settings.

## Dependencies And Integration Points
The header depends on clk, interrupt, notifier, regmap, regulator, and Arizona platform-data APIs. It integrates with ASoC codec drivers, extcon/input jack detection, regulator child drivers, GPIO/pinctrl-style users, regmap IRQ, runtime PM, and variant-specific patch code.

## Risks And Edge Cases
- IRQ numeric IDs are an ABI between MFD core and child drivers; reordering breaks request mappings.
- `clk32k_ref` must be updated under `clk_lock` to avoid disabling a shared 32 kHz clock while a child still needs it.
- Variant patch stubs can compile to no-op depending on Kconfig, so users must not assume a patch ran for disabled variants.
- DAC compensation and DAPM pointers are shared with ASoC paths and require lifetime coordination.
- Power sequencing across `core_supplies`, `dcvdd`, reset GPIO, and register access is critical for reliable probe/resume.

## Test Signals
Validate probe for each supported variant, patch hook execution, regulator enable/disable and external DCVDD handling, logical IRQ request/free/wake behavior, 32 kHz clock reference counting under multiple users, notifier delivery, ASoC codec probe and DAPM integration, suspend/resume, and fault interrupt delivery for clock and speaker-protection events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/arizona/core.h -->
