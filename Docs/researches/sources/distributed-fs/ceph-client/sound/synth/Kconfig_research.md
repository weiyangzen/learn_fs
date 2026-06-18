# sources/distributed-fs/ceph-client/sound/synth/Kconfig

## Purpose
This Kconfig file declares the internal ALSA EMUX wavetable synthesizer support symbol.

## Important APIs, types, and functions
`config SND_SYNTH_EMUX` is a tristate symbol with no prompt in this file. It is selected or depended on by concrete drivers that need the shared EMU wavetable synthesizer layer.

## Control flow
There is no runtime flow. At configuration time, other Kconfig entries control whether this hidden symbol is enabled.

## State and persistence behavior
The only state is the generated kernel configuration value, which controls whether `sound/synth/emux` is built.

## Dependencies and integration points
It integrates the shared EMUX layer into Kconfig without making it a direct user-facing option.

## Risks and edge cases
Because the symbol has no prompt, build failures can occur if dependent drivers expect EMUX objects but fail to select the symbol. Direct user configuration is intentionally limited.

## Test signals
Kconfig tests should verify that EMUX-dependent drivers select or enable this symbol and that disabling all consumers omits the module.
