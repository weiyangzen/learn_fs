# sources/distributed-fs/ceph-client/sound/soc/intel/keembay/Makefile

## Purpose
Builds the Intel Keem Bay ASoC platform driver object when `CONFIG_SND_SOC_INTEL_KEEMBAY` is enabled.

## Important APIs, Types, And Functions
Defines `snd-soc-kmb_platform-y := kmb_platform.o` and adds `snd-soc-kmb_platform.o` to `obj-$(CONFIG_SND_SOC_INTEL_KEEMBAY)`.

## Control Flow, State, And Persistence
There is no runtime state. The file controls kernel build composition for the Keem Bay audio platform module.

## Dependencies And Integration Points
Integrates with the sound/soc/intel Kbuild hierarchy and the Kconfig symbol that selects Keem Bay support.

## Risks And Test Signals
Risks are stale object names or mismatched Kconfig symbols. Test signals are `make M=sound/soc/intel/keembay` and full kernel builds with the config enabled as built-in and module.
