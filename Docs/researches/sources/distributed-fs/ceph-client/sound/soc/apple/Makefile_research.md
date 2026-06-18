# sources/distributed-fs/ceph-client/sound/soc/apple/Makefile

## Purpose
This Makefile maps `CONFIG_SND_SOC_APPLE_MCA` to the Apple MCA driver object.

## Important APIs, Types, And Functions
`snd-soc-apple-mca-y := mca.o` names the composite object, and `obj-$(CONFIG_SND_SOC_APPLE_MCA) += snd-soc-apple-mca.o` attaches it to the build.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
It depends on the Kconfig symbol in the same directory. Runtime behavior is entirely in `mca.c`.

## Risks And Test Signals
Test with `make sound/soc/apple/` or full kernel builds for built-in and module configurations. A mismatch between object name and module alias would prevent loading, but this file is straightforward.
