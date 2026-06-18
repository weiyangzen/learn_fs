# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-dvp.h

Purpose: public internal header for the CIF DVP implementation. It exposes DVP match data and lifecycle/IRQ entry points to the platform driver.

Important APIs/types/functions: declares `rkcif_px30_vip_dvp_match_data`, `rkcif_rk3568_vicap_dvp_match_data`, `rkcif_dvp_register()`, `rkcif_dvp_unregister()`, and `rkcif_dvp_isr()`. It includes `rkcif-common.h`, so callers share the `struct rkcif_device` and `struct rkcif_dvp_match_data` definitions.

Control flow: `rkcif-dev.c` uses the match-data externs in SoC descriptors, calls `rkcif_dvp_register()` during probe/media entity setup, calls `rkcif_dvp_unregister()` during remove/error unwind, and dispatches the shared platform IRQ to `rkcif_dvp_isr()`.

State and persistence: this header has no state; it formalizes ownership boundaries between the platform glue and DVP module.

Dependencies/integration: local driver-only interface tied to `rkcif-capture-dvp.c` and `rkcif-dev.c`.

Risks: declarations must stay synchronized with the implementation and match data. Because match data is exported as objects rather than factory functions, any struct layout change in `rkcif-common.h` directly affects this interface.

Test signals: compile coverage for all supported compatibles and module builds; probe/unwind paths verify all declarations are linked.
