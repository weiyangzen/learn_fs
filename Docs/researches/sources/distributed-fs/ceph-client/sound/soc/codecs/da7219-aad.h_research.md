# sources/distributed-fs/ceph-client/sound/soc/codecs/da7219-aad.h

## Purpose

`da7219-aad.h` is the local private contract for the DA7219 accessory auto-detect implementation. It defines ACCDET register addresses, bit masks, timing constants, private AAD state, and the internal functions used by `da7219.c` and `da7219-aad.c`.

## Important APIs, Types, and Constants

- Register definitions cover `DA7219_ACCDET_STATUS_A/B`, IRQ event/mask registers, and `DA7219_ACCDET_CONFIG_1` through `_8`.
- Bit fields define jack insertion, jack type, pin order, mic-bias-up status, button press/release events, IRQ masks, debounce/rate fields, button threshold registers, averaging/repeat controls, force bits, and headphone-test controls.
- `DA7219_AAD_MAX_BUTTONS` and `DA7219_AAD_REPORT_ALL_MASK` describe the supported ALSA jack reporting surface.
- Timing constants include mic-bias polling delay/retries and headphone-test ramp, period, and internal oscillator path delays.
- `enum da7219_aad_event_regs` indexes the two event bytes used in bulk regmap reads/writes.
- `struct da7219_aad_priv` is the complete private runtime state for the AAD subdriver.
- Exports include `da7219_aad_jack_det()`, optional PM helpers, `da7219_aad_init()`, `da7219_aad_exit()`, and `da7219_aad_probe()`.

## Control Flow

This header has no executable flow, but its declarations shape the AAD lifecycle. The main codec allocates AAD private data during I2C probe, initializes AAD from component probe, calls `da7219_aad_jack_det()` from `.set_jack`, delegates PM transitions to the AAD helpers, and calls `da7219_aad_exit()` during component remove. The event-register enum and report mask are used by the IRQ handler to read, clear, and report jack state atomically by event group.

## State and Persistence

`struct da7219_aad_priv` persists the component binding, IRQ, ground-switch delay, firmware-derived mic-bias/button configuration, three work items, single workqueue, current jack object, mic-bias resume intent, and physical jack-insertion flag. This state is not stored outside driver memory and is reconstructed on probe; hardware register state is synchronized by init, IRQ handling, and PM hooks.

## Dependencies and Integration Points

The header depends on Linux timer/mutex declarations, ASoC component and jack types, and public DA7219 AAD platform definitions from `<sound/da7219-aad.h>`. It is tightly coupled to `da7219.h` for parent codec register definitions and `struct da7219_priv` access in the implementation.

## Risks and Edge Cases

- Register and bit definitions must remain aligned with the DA7219 datasheet and with the regmap defaults in `da7219.c`.
- `DA7219_AAD_REPORT_ALL_MASK` determines what removal clears; missing a future button or jack bit would leave stale input state.
- The private structure contains both workqueue and IRQ-owned state, so implementation changes must preserve cancellation ordering around `jack_inserted`, `micbias_resume_enable`, and queued work.

## Test Signals

Header-level validation is mostly compile-time: all bit masks must match users in `da7219-aad.c`, PM stubs must compile with and without `CONFIG_PM`, and ALSA jack bits must match supported headset functionality. Runtime tests are the AAD insertion/button/PM scenarios described for the `.c` file.
