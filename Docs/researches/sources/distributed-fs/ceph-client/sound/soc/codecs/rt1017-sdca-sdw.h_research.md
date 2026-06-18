# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1017-sdca-sdw.h

## Purpose
`rt1017-sdca-sdw.h` defines the private SDCA entity/control identifiers, selected vendor register fields, supported SDCA rate codes, driver state, and default register table for the RT1017 SoundWire smart amplifier.

## Important APIs, Types, And Definitions
The header includes regmap, SoundWire, SDW type/register, and ASoC headers. It defines SDCA function number `FUNC_NUM_SMART_AMP`, entity IDs for power domains, converter, SAPU, extension unit, feature unit, and UDMPU, and control IDs for sample-rate index, requested power state, protection status, bypass, mute, volume, and cluster selection. It also defines `RT1017_CLASSD_INT_1`, `RT1017_PWM_TRIM_1`, and PWM frequency source masks.

The rate enum maps 44.1, 48, 96, and 192 kHz to SDCA FS index values. `struct rt1017_sdca_priv` carries component, regmap, SoundWire slave, bus params, and `hw_init`/`first_hw_init` flags. `rt1017_sdca_reg_defaults[]` seeds the regmap cache for vendor and SDCA controls, including default mute, bypass, FS index, and PDE power-state values.

## Control Flow
The header contains no functions. Its SDCA macros and defaults drive `rt1017-sdca-sdw.c` register access in hardware init, DAPM events, ALSA controls, PCM rate setup, PM cache sync, and readable/volatile register declarations.

## State And Persistence
`struct rt1017_sdca_priv` defines the state persisted across SoundWire status, PM, and ASoC callbacks. The default table establishes reset/cache state and is used by regmap for restore after suspend or reattach.

## Dependencies And Integration Points
This header is tightly coupled to the Linux SoundWire SDCA macro API, especially `SDW_SDCA_CTL()`. It is private to the RT1017 SDCA SoundWire driver but its constants encode the SDCA function topology used by ASoC controls and DAPM.

## Risks
The 32-bit SDCA address construction is easy to misuse; wrong function/entity/control IDs can target unrelated controls. The default table mixes vendor registers and SDCA controls, so additions must be checked against readable/volatile lists in the C file. `struct rt1017_sdca_priv` has a `params` field that is not actively used in the current C file, which can confuse future changes.

## Test Signals
Build coverage validates SDCA macro usage. Runtime tests should verify default mute/bypass/power states, FS index writes for each supported rate, PDE power-state DAPM transitions, cache restore after SoundWire resume, and readable/volatile coverage for all defaults.
