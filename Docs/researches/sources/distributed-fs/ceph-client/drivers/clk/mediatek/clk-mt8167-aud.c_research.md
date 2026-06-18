<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-aud.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-aud.c

Purpose: This small provider exposes MT8167 audsys clock gates for AFE, I2S, PCM, SPDIF, APB, and related audio blocks.

Important APIs, types, and functions: `aud_cg_regs` uses a shared set/clear/status offset pattern; `GATE_AUD` builds `struct mtk_gate` entries with MediaTek set/clear gate ops; `aud_desc` contains the gate table; the platform driver binds `mediatek,mt8167-audsys` and uses `mtk_clk_simple_probe/remove`.

Control flow: Probe is descriptor-driven: map the audsys register block, register each gate under its DT clock ID, and publish the OF provider. Audio consumers enable the relevant gates through the common clock framework.

State and persistence behavior: Gate state persists only in audsys MMIO bits while the SoC is powered. Kernel state is the registered onecell provider and gate handles. Remove unregisters them.

Dependencies and integration points: It depends on `clk-gate.h`, `clk-mtk.h`, MT8167 binding IDs, and parent clocks from topckgen such as audio bus and audio engine selectors. ALSA/SoC audio drivers are the primary consumers.

Risks and edge cases: Gate bit positions and parent names must match the audio hardware. Incorrectly gating APB or AFE can hang or mute audio paths. Runtime PM users depend on enable/disable balance.

Test signals: Audio playback/capture, I2S and SPDIF operation, clk summary gate toggling during stream start/stop, and module bind/unbind cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8167-aud.c -->
