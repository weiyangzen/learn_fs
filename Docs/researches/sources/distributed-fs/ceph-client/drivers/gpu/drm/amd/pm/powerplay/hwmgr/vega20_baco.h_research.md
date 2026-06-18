# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_baco.h

`vega20_baco.h` declares the Vega20 BACO helper interface used by the power-management backend. It exposes support detection, state query, state transition, and VDCI workaround functions.

The declared functions are `vega20_get_bamaco_support()`, `vega20_baco_get_state()`, `vega20_baco_set_state()`, and `vega20_baco_apply_vdci_flush_workaround()`. The header imports `hwmgr.h` for `struct pp_hwmgr` and `common_baco.h` for `enum BACO_STATE` and common BACO definitions.

There is no runtime control flow or stored state in this header. It allows the hwmgr implementation to call BACO implementation code without embedding register programming details in broader power-management code. The declared operations manipulate SMU and hardware BACO state through `vega20_baco.c`.

Risks are declaration drift and incorrect inclusion of common BACO types. Test signals are compile coverage for all call sites and runtime verification that callback wiring can enter, exit, and query BACO state.
