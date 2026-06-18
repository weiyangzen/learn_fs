# sources/distributed-fs/ceph-client/sound/soc/apple/Kconfig

## Purpose
This Kconfig fragment exposes the Apple Silicon MCA ASoC platform driver under the `Apple` menu.

## Important APIs, Types, And Functions
The key symbol is `SND_SOC_APPLE_MCA`, a tristate option labeled "Apple Silicon MCA driver". It depends on `ARCH_APPLE || COMPILE_TEST` and selects `SND_DMAENGINE_PCM`.

## Control Flow
Build-time only. Selecting the symbol permits the `apple/mca.c` driver to be built as built-in or module.

## State And Persistence
No runtime state. It influences kernel configuration and build artifacts.

## Dependencies And Integration Points
It integrates with ASoC Kconfig and the generic DMAengine PCM layer. Device matching at runtime is handled by the OF match table in `mca.c`.

## Risks And Test Signals
The risk is dependency under-selection if MCA requires additional Apple platform services not expressed here. Test signals include successful compile under `ARCH_APPLE` and `COMPILE_TEST`, and module availability when devicetree advertises `apple,mca`.
