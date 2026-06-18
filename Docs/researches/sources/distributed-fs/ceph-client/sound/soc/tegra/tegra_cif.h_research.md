# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_cif.h

## Purpose
Inline helpers for programming Tegra Audio CIF control registers, including the altered Tegra264 bit layout.

## Important APIs/types/functions
`struct tegra_cif_conf` carries FIFO threshold, audio/client channels, audio/client bits, expansion, stereo conversion, replication, truncation, and mono conversion. `tegra_set_cif` and `tegra264_set_cif` pack fields and call `regmap_update_bits` with `TEGRA_ACIF_UPDATE_MASK`.

## Control flow
The helpers encode channel counts as `count - 1`, shift each field into a single value, and update the target register. Tegra264 uses different shifts for audio bits and channel fields.

## State, dependencies, integration, risks, tests
No local state; persistent effect is hardware CIF register state. It depends only on regmap and is used by Tegra audio fabric clients. Risks are zero-channel underflow, wrong Tegra264 shifts, and stale bits outside the mask. Validate via register dumps and mono/stereo/multichannel playback/capture on multiple Tegra generations.
