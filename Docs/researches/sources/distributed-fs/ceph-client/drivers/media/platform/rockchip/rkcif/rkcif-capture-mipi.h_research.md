# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-capture-mipi.h

Purpose: public internal header for the CIF MIPI capture implementation.

Important APIs/types/functions: declares `rkcif_rk3568_vicap_mipi_match_data`, `rkcif_mipi_register()`, `rkcif_mipi_unregister()`, and `rkcif_mipi_isr()`. It imports `rkcif-common.h` for `struct rkcif_device` and match-data type definitions.

Control flow: consumed by `rkcif-dev.c` to attach RK3568 MIPI match data, register/unregister MIPI entities, and route the shared IRQ into the MIPI ISR.

State and persistence: no state; the header exposes module boundaries only.

Dependencies/integration: tightly coupled to `rkcif-capture-mipi.c` and platform match data.

Risks: any change to MIPI match-data shape or registration semantics requires this header and users to remain in sync.

Test signals: build/link coverage on RK3568 VICAP configs and probe/remove paths.
