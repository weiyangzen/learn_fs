## sources/distributed-fs/ceph-client/include/linux/mfd/cs42l43-regs.h

Purpose: This dense header is the CS42L43/CS42L43B register and bitfield map. It is consumed by the CS42L43 MFD core and audio, soundwire, GPIO, SPI bridge, accessory-detect, amplifier, PLL, firmware/MCU, and codec subdrivers.

Important APIs, types, and constants: Register definitions span general interrupt status/masks, device/revision IDs, reset, drive strength, GPIO, clocking and sample-rate selection, PLL, PDM/ADC/decimator controls, digital volume/ramping, ASP/I2S configuration, routing/mixer inputs, ASRC/ISRC enables, headset/tip/ring/mic detect, block enables, SPI master and software-to-SPI bridge, headphone path, EQ coefficient/control, many interrupt and shadow status blocks, MCU boot/config/firmware status, and CS42L43B-specific register relocations/extensions. Bitfield masks and shifts are provided for every major register group. Magic values include `CS42L43_DEVID_VAL`, `CS42L43B_DEVID_VAL`, soft reset value, and firmware mission-control disable value.

Control flow: No functions are implemented. Driver control flow uses these constants to reset the device, validate variant IDs, configure clock/PLL/sample-rate domains, route audio mixers, enable functional blocks, program headset/accessory detection, operate the embedded SPI bridge, service interrupts, and coordinate MCU firmware configuration.

State and persistence: Hardware register state includes audio routing, gain/mute/ramp settings, PLL and sample rates, GPIO levels, headset detection state, SPI bridge transaction status, MCU boot/config flags, and interrupt shadows. Firmware state may persist while MCU memory remains powered.

Dependencies and integration points: This header is paired with `cs42l43.h` and regmap configuration. It integrates with ALSA SoC, SoundWire, GPIO, regulator/reset handling, interrupt controller, SPI controller, and firmware/configuration paths.

Risks: The file contains duplicate definitions for several CS42L43B firmware mission-control addresses; duplicate identical macros are harmless for C preprocessing but increase maintenance risk. Variant-specific addresses must be selected by device ID. Many masks are 32-bit; regmap val width must match. Incorrect mixer source or block-enable programming can create silent audio rather than obvious errors.

Test signals: Regmap readable/volatile/default tests, ID-based variant selection, soft reset, PLL lock/lost-lock IRQs, ASP/PDM/ASRC routing audio tests, headset/tip/ring detection interrupts, SPI bridge transfer tests, MCU firmware config handshake, and CS42L43B-specific decimator/register address coverage.
