# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8192-aud.c

## Purpose
`clk-mt8192-aud.c` provides MT8192 audio subsystem clocks for AFE, I2S, memory interface, DAC/ADC, TDM, and related audio paths.

## Important APIs, Types, And Functions
The driver defines three audio gate banks, `aud_clks`, `aud_desc`, and custom `clk_mt8192_aud_probe()`/`remove()`. Probe wraps `mtk_clk_simple_probe()` and calls `mt8192_mmsys_clk_register()` for cross-subsystem audio/display clock integration; remove calls `mt8192_mmsys_clk_unregister()` before simple removal.

## Control Flow, State, And Persistence
Audio gate registration is handled by the simple helper. Additional MMSYS clock registration is layered after successful simple probe and explicitly unwound on failure or remove. State includes audio clock provider data and the auxiliary MMSYS registration.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `clk-mtk`, audio DT consumers, and the MT8192 MMSYS clock hook. Risks include asymmetry between audio and mmsys registration and audio paths failing only under display/audio shared-clock scenarios. Test signals include ALSA probe/playback/capture, I2S/TDM paths, MMSYS registration failure injection, and remove/reprobe cleanup.
