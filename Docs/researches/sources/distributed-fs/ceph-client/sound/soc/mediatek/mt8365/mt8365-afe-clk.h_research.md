# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.h

## Purpose
Private MT8365 AFE clock-control interface shared by the platform PCM driver and backend DAI implementations.

## APIs, Types, and Functions
The header forward-declares `struct mtk_base_afe` and `struct clk`, then declares all clock helper entry points implemented by `mt8365-afe-clk.c`: clock initialization, generic disable, rate/parent changes, top clock-gate enable/disable, main AFE clock enable/disable, EMI clock hooks, AFE-on reference control, and APLL tuner/associated configuration enable/disable.

## Control Flow, State, and Persistence
The header carries no state itself. It defines the call boundary through which stream startup, stream shutdown, platform probe, and DAI-specific APLL code manipulate persistent counters and clock pointers stored in `struct mt8365_afe_private`.

## Dependencies and Integration
Included by `mt8365-afe-pcm.c`, `mt8365-dai-adda.c`, `mt8365-dai-dmic.c`, and other MT8365 DAI files. It avoids requiring every includer to pull in full clock headers by using forward declarations, while concrete implementations still depend on Linux `clk` and the common MTK AFE structures.

## Risks and Test Signals
Risks are interface drift between declarations and implementation, lack of kernel-doc describing required pairing rules, and no explicit return contract documenting helpers that currently return success even when internal clock enables fail. Build coverage across all MT8365 objects is the primary static signal; runtime signals are balanced main-clock, top-CG, AFE-on, and APLL enable/disable behavior across every DAI startup/shutdown path.
