# sources/distributed-fs/ceph-client/drivers/reset/sti/reset-syscfg.c

Purpose: generic ST syscfg reset-controller implementation using regmap fields for reset and optional acknowledge bits.

Important APIs/types/functions: `syscfg_reset_channel` stores reset/ack fields; `syscfg_reset_controller` embeds rcdev plus flexible channel array. `syscfg_reset_program_hw()` writes reset polarity and optionally polls ack. `syscfg_reset_status()` reads ack or reset field. `syscfg_reset_controller_register()` allocates fields from syscon regmaps and registers the controller.

Control flow: SoC data probe passes a `syscfg_reset_controller_data` through match data. Registration resolves each channel’s syscon compatible, builds fields, then exposes reset ops.

State and persistence: software stores regmap-field handles; hardware syscfg bits hold reset state. Allocation is devm, but `reset_controller_register()` is not devm-wrapped in this file.

Dependencies and integration: regmap fields, syscon lookup by compatible, platform OF match data, reset framework.

Risks and test signals: no explicit unregister path because driver is arch-init/built-in style. Ack polling timeout is one second. Test bad compatible strings, active-low behavior, ack and no-ack controllers, invalid IDs, and timeout handling.
