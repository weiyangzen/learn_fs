# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/infracfg.h

Purpose: This MediaTek header is a shared register map for infrastructure bus protection, SMI clamp, GALS, and reset control bits across many MediaTek SoCs.

Important APIs/types/functions: It defines hundreds of register offsets and bit masks for MT8365, MT8195, MT8192, MT8188, MT8186, MT8183, MT8173, MT8167, MT2701, MT7622, MT6735, and common infrastructure registers. It declares `mtk_infracfg_set_bus_protection` and `mtk_infracfg_clear_bus_protection`, both operating on a `struct regmap`, mask, and `reg_update` flag.

Control flow: Power-domain, clock, and multimedia drivers use the masks to set isolation/protection before powering down a domain and clear them after powering up. Some sequences require ordered multi-step masks and status polling.

State and persistence: Hardware registers hold bus-protection, clamp, reset, and control state. The state persists until explicitly changed or reset and directly affects interconnect reachability.

Dependencies and integration: Uses `BIT`, `GENMASK`, `regmap`, and MediaTek SoC PM domains. It integrates with genpd, display/video/camera/audio/GPU power sequencing, SMI, and infracfg syscon nodes.

Risks and test signals: Incorrect masks or ordering can deadlock AXI/GALS paths, isolate active masters, or hang power transitions. Test every domain transition, timeout paths, concurrent runtime PM, and register readback on each SoC variant.
