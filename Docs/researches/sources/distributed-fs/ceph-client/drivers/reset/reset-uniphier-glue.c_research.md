# sources/distributed-fs/ceph-client/drivers/reset/reset-uniphier-glue.c

Purpose: UniPhier glue-layer reset controller for USB3/AHCI blocks that need associated clocks enabled and upstream resets deasserted before exposing simple active-low reset bits.

Important APIs/types/functions: `uniphier_glue_reset_soc_data` lists required clock/reset names. `uniphier_glue_reset_probe()` maps registers, bulk-gets/enables clocks, registers a cleanup action, bulk-gets shared deasserted resets, initializes `reset_simple_data`, and registers `reset_simple_ops`.

Control flow: OF match data chooses one- or two-name resource sets. Probe prepares dependencies first, then exposes all bits in the mapped resource as active-low reset controls.

State and persistence: clock enable state and shared reset deassertions are runtime-managed by devm actions. Hardware reset bits hold state.

Dependencies and integration: clock framework, reset controls, platform MMIO, `reset_simple_ops`, and UniPhier glue compatible strings.

Risks and test signals: `nr_resets` is based on full resource size, not a binding-specific count. MAX limits are guarded by WARN. Test clock/reset dependency failures, devm clock disable on error, active-low bit behavior, and all compatible resource-name sets.
