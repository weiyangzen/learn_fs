# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_ope.h

## Purpose
Defines OPE RX/TX/global register offsets, enable/reset/direction fields, the parent `struct tegra210_ope`, and a shared extended bytes-control helper for AHUB RAM programming controls.

## Important APIs, Types, And Functions
`struct tegra210_ope` stores parent, PEQ, and MBDRC regmaps; PEQ RAM shadow arrays; and selected data direction. `struct tegra_soc_bytes` extends ASoC `soc_bytes` with a RAM offset `shift`. `TEGRA_SOC_BYTES_EXT()` builds mixer controls with custom get/put/info callbacks and is used by PEQ and MBDRC controls.

## Control Flow
The header has no executable flow. Its macro-generated controls pass a compound `tegra_soc_bytes` private value to handlers in PEQ/MBDRC implementations.

## State And Persistence
Defines the OPE aggregate state used by the parent runtime PM path. The PEQ shadow arrays are intended for RAM persistence, while `data_dir` is a software copy of user-selected flow direction.

## Dependencies And Integration Points
Includes regmap, ASoC, and `tegra210_peq.h` for PEQ RAM sizing. Included by OPE, PEQ, and MBDRC source files to share parent state and control macro definitions.

## Risks
The compound-literal `private_value` pattern relies on static storage duration rules for compound literals at file scope inside control arrays; misuse in block scope would be unsafe. `struct tegra210_ope` contains only one PEQ gain/shift buffer per payload type, not per-channel storage, which constrains exact restore semantics.

## Test Signals
Compile with PEQ/MBDRC controls enabled and inspect ALSA byte/integer controls for correct element counts and stable private values.
