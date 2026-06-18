# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_audio_graph_card.c

## Purpose
Tegra audio-graph-card machine driver for newer APE systems. It extends generic audio graph/simple-card handling with Tegra PLLA and PLLA_OUT0 clock programming.

## Important APIs/types/functions
Key types are `struct tegra_audio_priv` and `struct tegra_audio_cdata`. Main functions are `need_clk_update`, `tegra_audio_graph_update_pll`, `tegra_audio_graph_hw_params`, `tegra_audio_graph_card_probe`, and `tegra_audio_graph_probe`. SoC rate tables cover Tegra210, Tegra186, Tegra238, and Tegra264.

## Control flow
Probe allocates a simple-card wrapper, enables component chaining and forced DPCM, installs custom ops, and parses audio graph DT. Card probe gets `pll_a` and `plla_out0`. `hw_params` updates PLLs for CPU DAIs named I2S/DMIC/DSPK, chooses 44.1/48 kHz-family rates, halves PLLA_OUT0 if divider would exceed 128, then delegates to `simple_util_hw_params`.

## State, dependencies, integration, risks, tests
State is embedded simple-card data and two clock handles; rates are not cached. Dependencies are graph-card utilities, ASoC, clocks, and OF match data. Risks include fragile DAI-name matching, unsupported rates, and clock conflicts across links. Test audio graph parse, low-rate I2S, 44.1/48/176.4/192 kHz rates, DPCM links, and clock-tree state.
