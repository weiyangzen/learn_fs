# Research: sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h -->
## sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h

**Purpose:** Provides the generated register address and bitfield namespace for Madera codecs. It is the canonical compile-time map used by MFD, ASoC, regulator, GPIO, interrupt, clock/FLL, DSP, accessory-detect, and audio-route code.

**Important APIs and types:** The file is macro-only. Address macros cover reset/revision, clocks, FLLs, charge pumps, LDOs, MICBIAS, headphone/mic/accessory detection, inputs/outputs, AIF/SLIMbus/SPDIF, mixers, EQ/DRC/ASRC/ISRC/DFC, DSP IRQ/config/scratch regions, GPIOs, IRQ status/masks/raw status/debounce/control, write sequencer, OTP HPDET calibration, and 32-bit DSP windows. Bitfield macros provide value, mask, and shift triples for many registers.

**Control flow:** There is no executable control flow; users combine address macros with regmap reads/writes and bitfield masks. Control sequences are implemented in consumers such as codec, IRQ, clock, and regulator drivers.

**State and persistence:** The macros name hardware state. Persistence is entirely in codec registers and OTP/calibration fields. The same header supports volatile runtime registers and one-time calibration data.

**Dependencies and integration:** Standalone include guard with no includes. It integrates by being included into Madera core and child drivers that use regmap.

**Risks:** The map contains overlapping/common and chip-specific aliases, for example CS47L92 FLL and AIF/DSP regions that share addresses with generic names. Address ranges span normal 16-bit control registers, 32-bit OTP/calibration, and large DSP windows, so consumers must use the correct regmap width. Generated macro volume makes typo detection dependent on compile coverage.

**Test signals:** Compile all Madera consumers, regmap access tests for representative 16-bit and 32-bit registers, field-mask tests for clock/FLL/input/output/IRQ macros, chip-variant tests for CS47L35/CS47L85/CS47L92 aliases, and audio route tests exercising mixer address patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/madera/registers.h -->
