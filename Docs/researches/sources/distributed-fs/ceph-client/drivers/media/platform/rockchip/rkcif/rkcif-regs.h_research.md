# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-regs.h

Purpose: register bit definitions and register index enums for the CIF DVP and MIPI capture driver.

Important APIs/types/functions: defines `RKCIF_REGISTER_NOTSUPPORTED`, coordinate/fetch helpers, DVP control/interrupt/status/format/scaler bits, RK3568 GRF offsets and write-enable helper, DVP register indices (`enum rkcif_dvp_register_index`), MIPI block register indices (`enum rkcif_mipi_register_index`), and per-stream MIPI ID register indices (`enum rkcif_mipi_id_register_index`).

Control flow: match-data tables in DVP/MIPI modules map these enum indices to SoC-specific offsets. Register helper functions validate an enum index, look up the offset, and skip unsupported registers.

State and persistence: header constants only. Hardware state is controlled by writes from DVP/MIPI modules.

Dependencies/integration: consumed by `rkcif-common.h`, `rkcif-capture-dvp.c`, and `rkcif-capture-mipi.c`. Uses Linux `BIT()`/`GENMASK()` style macros via included kernel headers in users.

Risks: wrong bit definitions or enum ordering directly misprograms hardware. The sentinel value must not collide with real register offsets. Some duplicated macro names such as `RKCIF_INTSTAT_*` refer to different hardware contexts and require careful local interpretation.

Test signals: hardware stream tests across supported SoCs, register dumps while streaming, IRQ enable/status behavior, and compile warnings for missing enum initializers in match-data tables.
