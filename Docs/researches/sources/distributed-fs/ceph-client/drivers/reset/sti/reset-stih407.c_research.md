# sources/distributed-fs/ceph-client/drivers/reset/sti/reset-stih407.c

Purpose: STiH407 reset data provider, defining powerdown, softreset, and picophy reset channels and registering them through the generic syscfg reset code.

Important APIs/types/functions: macros such as `STIH407_PDN_*` and `STIH407_SRST_*` build `syscfg_reset_channel_data` entries. Three `syscfg_reset_controller_data` instances describe acked powerdowns, active-low softresets, and picophy resets. Platform driver probe is `syscfg_reset_probe()`.

Control flow: arch init registers the platform driver early. OF match data selects a controller data block, and `reset-syscfg.c` performs actual regmap field registration and operations.

State and persistence: this file has only static channel tables; hardware syscfg registers hold reset/powerdown state.

Dependencies and integration: STiH407 reset dt-bindings, syscon compatible strings for core/SBC/LPM registers, generic syscfg reset implementation.

Risks and test signals: channel indices must match binding IDs. Powerdown entries wait for ack while softreset entries do not. Test all compatibles, ack timeout paths, active-low softreset polarity, and syscon compatible lookup.
