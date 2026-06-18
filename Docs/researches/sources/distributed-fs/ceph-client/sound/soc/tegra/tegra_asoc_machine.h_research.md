# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.h

## Purpose
Defines the shared private contracts between Tegra codec-specific machine wrappers and the common Tegra machine implementation.

## Important APIs/types/functions
`struct tegra_asoc_data` carries immutable board/codec policy: MCLK callback, codec platform-device name, HP jack name, card pointer, MCLK ID, jack/control/widget flags, AC97 mode, and legacy HP polarity. `struct tegra_machine` stores runtime clocks, cached rates, GPIOs, selected policy, and jack pointers. It declares the common probe/init helpers.

## Control flow
No executable code. Codec wrappers instantiate `tegra_asoc_data`; the common probe/init consumes it to configure card registration, clocks, phandles, jacks, widgets, and controls.

## State, dependencies, integration, risks, tests
`tegra_machine` is per-card drvdata; `tegra_asoc_data` is matched from OF compatibles. Dependencies are forward-declared Linux clock/GPIO/ASoC/platform types. Risks are ABI drift and new flags not handled by probe/init. Compile all Tegra machine wrappers and probe each compatible.
