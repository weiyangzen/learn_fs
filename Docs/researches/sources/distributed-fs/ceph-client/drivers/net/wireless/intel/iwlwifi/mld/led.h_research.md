# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.h

Purpose: Provides the LED subsystem interface for MLD and compiles it out cleanly when LED support is disabled.

Important APIs/types/functions: `iwl_mld_leds_init()`, `iwl_mld_leds_exit()`, and `iwl_mld_led_config_fw()`, with static inline no-op versions when `CONFIG_IWLWIFI_LEDS` is not set.

Control flow: Callers can unconditionally invoke LED init, exit, and firmware replay hooks. The header maps those calls either to real implementations in `led.c` or no-op/stub behavior.

State/persistence: With LED support disabled, no LED state is allocated or mutated. With support enabled, state resides in `mld->led` and is managed by `led.c`.

Dependencies/integration: Includes `mld.h` and is consumed by firmware startup and op-mode lifecycle code.

Risks: The no-op `iwl_mld_leds_init()` always returns success, so tests must consider both build-time variants. Any future LED caller should remain valid when support is compiled out.

Test signals: Compile both `CONFIG_IWLWIFI_LEDS=y` and disabled configurations. In disabled builds, op-mode start/stop should not require LED class symbols.
