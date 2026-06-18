# sources/distributed-fs/ceph-client/sound/soc/intel/boards/Kconfig

## Purpose
This Kconfig file defines the configuration surface for Intel ASoC machine drivers under `sound/soc/intel/boards`. It gates legacy SST/Catpt, Baytrail/Cherrytrail/Braswell, Broadwell, SOF HDA/I2S, and SoundWire board drivers behind `SND_SOC_INTEL_MACH`, then selects codec, ACPI, GPIO, SoundWire, and helper dependencies needed by each board module.

## Important APIs, Types, and Symbols
The primary exported symbols are tristate machine options such as `SND_SOC_INTEL_BDW_RT5650_MACH`, `SND_SOC_INTEL_BDW_RT5677_MACH`, `SND_SOC_INTEL_BROADWELL_MACH`, `SND_SOC_INTEL_BYTCR_RT5640_MACH`, `SND_SOC_INTEL_BYTCR_RT5651_MACH`, `SND_SOC_INTEL_BYTCR_WM5102_MACH`, `SND_SOC_INTEL_CHT_BSW_RT5645_MACH`, `SND_SOC_INTEL_CHT_BSW_MAX98090_TI_MACH`, `SND_SOC_INTEL_CHT_BSW_NAU8824_MACH`, `SND_SOC_INTEL_BYT_CHT_CX2072X_MACH`, `SND_SOC_INTEL_BYT_CHT_DA7213_MACH`, `SND_SOC_INTEL_BYT_CHT_ES8316_MACH`, and `SND_SOC_INTEL_BYT_CHT_NOCODEC_MACH`. It also defines common helper symbols including `SND_SOC_INTEL_USER_FRIENDLY_LONG_NAMES`, `SND_SOC_INTEL_HDA_DSP_COMMON`, `SND_SOC_INTEL_SOF_*_COMMON`, and `SND_SOC_INTEL_SOF_BOARD_HELPERS`.

## Control Flow and Integration
Menu visibility starts at `menuconfig SND_SOC_INTEL_MACH`, which depends on either the SST or SOF Intel top-level families. Nested `if` blocks partition options by runtime family: Catpt/Haswell, Catpt or SOF Broadwell, Atom/SOF Baytrail, SOF Apollo Lake/Gemini Lake/HDA, and SoundWire. Each board symbol constrains hardware prerequisites with `depends on` and pulls codec drivers with `select`. The Makefile consumes these symbols to build matching machine modules.

## State, Persistence, and Dependencies
There is no runtime state. The persistent effect is kernel configuration state, which controls object inclusion, module availability, and transitive codec/helper selection. Dependencies are mostly compile/link dependencies (`I2C`, `ACPI`, `SPI_MASTER`, `GPIOLIB`, `MFD_*`, `SOUNDWIRE`, `SND_HDA_CODEC_HDMI`) plus codec selections such as `SND_SOC_RT5640`, `SND_SOC_RT5645`, `SND_SOC_RT5677`, `SND_SOC_ES8316`, `SND_SOC_NAU8824`, `SND_SOC_MAX98090`, and `SND_SOC_WM5102`.

## Risks and Test Signals
The main risk is dependency drift: missing `select` or `depends on` clauses can produce link failures, missing probe-time helpers, or unbuildable `COMPILE_TEST` configurations. Another risk is overly broad `select` usage increasing kernel footprint for distro configs. Test signals include `olddefconfig` visibility, `allyesconfig` and `allmodconfig` build coverage, `COMPILE_TEST` builds without target hardware, and verifying that every Kconfig symbol used in the Makefile has a matching config block.
