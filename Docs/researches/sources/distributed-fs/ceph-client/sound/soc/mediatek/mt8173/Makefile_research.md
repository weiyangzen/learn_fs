# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8173/Makefile

## Purpose

This Makefile builds the MT8173 AFE platform driver and several codec-specific machine drivers.

## Important APIs, Types, and Functions

`CONFIG_SND_SOC_MT8173` builds `mt8173-afe-pcm.o`. Machine entries build MAX98090, RT5650, RT5650+RT5514, and RT5650+RT5676 card drivers under their respective Kconfig symbols.

## Control Flow

Kbuild selects independent platform and machine objects. Machine drivers bind to the platform through DAI names and DT references at runtime.

## State and Persistence Behavior

No runtime state. It controls which object files are available.

## Dependencies and Integration Points

Depends on the MT8173 platform file and codec drivers. Machine drivers require matching DT compatible strings and routing.

## Risks and Edge Cases

Unlike newer platform composites, this platform has a single object; missing machine Kconfig symbols only removes board-card support, not the AFE itself. Machine/platform Kconfig mismatch can build a card that cannot bind.

## Test Signals

Kbuild all listed Kconfig combinations and boot DTs for each supported codec board.
