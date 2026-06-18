# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/Kconfig

## Purpose
`side-codecs/Kconfig` declares build configuration for HD-audio side-codec support. It covers shared Cirrus side-codec library/test options plus CS35L41, CS35L56, and TAS2781 amplifier support over I2C or SPI.

## APIs, Types, and Functions
This is Kconfig metadata, not C API. Symbols include `SND_HDA_CIRRUS_SCODEC`, `SND_HDA_CIRRUS_SCODEC_KUNIT_TEST`, `SND_HDA_SCODEC_CS35L41`, bus-specific `SND_HDA_SCODEC_CS35L41_I2C/SPI`, `SND_HDA_SCODEC_COMPONENT`, CS35L56 symbols and calibration debugfs option, and TAS2781 I2C/SPI symbols.

## Control Flow
User-visible bus options select hidden core objects and their dependencies. CS35L41 bus drivers depend on ACPI, EFI, SND_SOC, and I2C or SPI, then select the shared CS35L41 HDA core, SND_SOC CS35L41 library, and CS amp library. CS35L56 options select FW CS DSP, generic HDA, shared CS35L56 support, Cirrus side-codec library, and amp library. TAS2781 options select the matching comms/firmware libraries and CRC support.

## State and Persistence Behavior
Kconfig state is build-time configuration. Tristate selections determine which modules are built in, loadable, or absent. Comments warn that module autoloading may require enabling side-codec drivers when core HDA is built in.

## Dependencies and Integration Points
The file integrates the side-codec directory with kernel configuration, ALSA HDA generic support, ACPI, EFI, SND_SOC, I2C/SPI buses, firmware DSP support, debugfs, and vendor codec libraries.

## Risks
Incorrect dependencies can create link failures or runtime probe paths without required bus, ACPI, firmware, or calibration support. Hidden tristate cores selected by bus options must match Makefile object names.

## Test Signals
Build matrix coverage for built-in and module combinations, KUnit enabling for Cirrus side-codec tests, I2C/SPI variants, CS35L56 debugfs on/off, and no unmet-symbol warnings are the key signals.
