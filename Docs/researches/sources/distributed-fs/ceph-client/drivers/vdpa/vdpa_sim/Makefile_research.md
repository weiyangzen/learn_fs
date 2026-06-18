<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/Makefile

Purpose: Builds the vDPA simulator core and optional net/block simulator frontends.

Important APIs/types/functions: `obj-$(CONFIG_VDPA_SIM) += vdpa_sim.o`, `obj-$(CONFIG_VDPA_SIM_NET) += vdpa_sim_net.o`, and `obj-$(CONFIG_VDPA_SIM_BLOCK) += vdpa_sim_blk.o`.

Control flow: The core simulator can be built independently, while net and block modules depend on it for `vdpasim_create()` and work scheduling.

State and persistence: Build-only; no runtime state.

Dependencies and integration points: Controlled by Kconfig symbols for simulator core, network, and block devices.

Risks: Net/block simulator objects require exported core symbols; building frontends without core support would fail through Kconfig dependency expectations.

Test signals: Build all three symbols as modules and verify `vdpa_sim_net` and `vdpa_sim_blk` load after or with `vdpa_sim`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/vdpa_sim/Makefile -->
