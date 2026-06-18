<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mcu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mcu.c

Purpose: This file registers MT8186 mcusys CPU/bus mux composites for little, big, and bus clock domains.

Important APIs, types, and functions: Parent arrays select among `clk26m`, ARM PLLs, `mainpll`, and `univpll` divided parents. `mcu_muxes` defines composite muxes, and `mcu_desc` exposes them through `mediatek,mt8186-mcusys`.

Control flow: Simple probe registers the MCU mux composites and publishes a clock provider. CPU frequency and bus-clock users can then switch parents through CCF.

State and persistence behavior: Mux state is volatile mcusys register state. Provider metadata is runtime-only.

Dependencies and integration points: It depends on MT8186 bindings, MediaTek composite helpers, apmixedsys PLL parents, topckgen divided parents, CPU/cluster clock consumers, and DVFS.

Risks and edge cases: CPU mux parent order and safe switching are critical. Bad mux fields can destabilize CPU clocks. This file does not register a custom notifier, so safe switching must be handled by common mux/composite behavior and consumers.

Test signals: CPU frequency scaling, bus-clock changes, clk summary parent changes, stress workloads during DVFS, suspend/resume, and provider removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8186-mcu.c -->
