<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mdp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mdp.c

Purpose: This driver registers MT8186 Multimedia Data Path gates.

Important APIs, types, and functions: `mdp0_cg_regs` and `mdp2_cg_regs` define two gate banks; `GATE_MDP0` and `GATE_MDP2` populate `mdp_clks`; `mdp_desc` is selected by `mediatek,mt8186-mdpsys`.

Control flow: Simple probe registers MDP gates and publishes a provider for display/media data-path consumers.

State and persistence behavior: Gate state is volatile register state. Provider metadata exists only while bound.

Dependencies and integration points: It depends on MT8186 clock IDs, common gate helpers, top-level MDP parents, MDP/display drivers, power domains, and memory/LARB clocks.

Risks and edge cases: MDP paths require coordinated display, MM, and memory clocks. Wrong gate bank selection causes pipeline stalls or DMA faults.

Test signals: MDP blit/resize/composition workloads, display pipeline use, runtime PM, clock summary transitions, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mdp.c -->
