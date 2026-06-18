# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7724.c

Purpose: registers the SH7724 PFC register window for the SuperH PFC driver.

Important APIs, types, and functions: `plat_pinmux_setup()` calls `sh_pfc_register("pfc-sh7724", ...)`; the sole resource maps `0xa4050100-0xa405016f`.

Control flow: the arch initcall provides PFC resources before board-level pin requests and before device drivers configure their pins.

State and persistence: no local runtime state; pinmux state is externalized to the PFC hardware and driver.

Dependencies and integration points: the registration names the SoC-specific PFC driver used by SH7724 setup paths for SCIF, DMA-capable peripherals, multimedia blocks, and sleep-state restoration.

Risks: resource range must match the PFC driver register model. Any mismatch can make pins unavailable or corrupt unrelated registers.

Test signals: PFC probe should succeed; SH7724 board devices should be able to request GPIO/function pins; suspend/resume should keep restored pins usable.
