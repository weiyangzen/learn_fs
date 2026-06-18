# sources/distributed-fs/ceph-client/drivers/reset/reset-sunplus.c

Purpose: Sunplus SP7021 reset controller using HIWORD mask registers and providing a restart sys-off handler.

Important APIs/types/functions: `sp_resets[]` maps logical IDs to packed register/bit positions. `sp_reset_update()` writes high-word mask plus asserted value; `sp_reset_status()` reads current bit. `sp_restart()` pulses reset ID 0. `sp_reset_probe()` maps MMIO, derives reset count from resource size, registers reset ops, then registers restart priority 192.

Control flow: reset consumers assert/deassert via high-word-mask writes. Restart callback asserts and deasserts reset 0 during system restart.

State and persistence: hardware reset registers hold state; no runtime mutable software state beyond MMIO base and rcdev.

Dependencies and integration: platform MMIO, reset-controller framework, sys-off restart handling, Sunplus compatible `sunplus,sp7021-reset`.

Risks and test signals: `nr_resets` is resource-derived rather than `ARRAY_SIZE(sp_resets)`, so mismatched resource size could expose IDs beyond `sp_resets`. Test DT resource sizing, reset ID coverage, restart behavior, and status polarity.
