# sources/distributed-fs/ceph-client/include/soc/rockchip/pm_domains.h

Purpose: declares Rockchip PMU block/unblock helpers used by drivers that need to serialize sensitive PMU or DRAM-frequency interactions with power-domain changes.

Important APIs/types/functions: exports `rockchip_pmu_block()` and `rockchip_pmu_unblock()` when `CONFIG_ROCKCHIP_PM_DOMAINS` is enabled; otherwise provides success/no-op stubs.

Control flow: callers block PMU power-domain transitions, perform their protected operation, then unblock. Disabled builds allow callers to compile and proceed without PM-domain coordination.

State and persistence: implementation-owned block state likely gates PM-domain transitions. The header owns no state.

Dependencies and integration: consumed by Rockchip PM-domain and devfreq/DMC code such as `rk3399_dmc.c`.

Risks: missing unblock calls can freeze PM-domain changes, while missing block calls can race power changes. Test signals include Rockchip devfreq transitions, PM-domain on/off stress, suspend/resume, and disabled-config builds.
