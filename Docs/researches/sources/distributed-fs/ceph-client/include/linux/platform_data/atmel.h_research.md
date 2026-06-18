# sources/distributed-fs/ceph-client/include/linux/platform_data/atmel.h

Purpose: provides a temporary common declaration point for Atmel power-management slow-clock status.

Important APIs and types: when `CONFIG_ATMEL_PM` is enabled, declares `at91_suspend_entering_slow_clock()`. Otherwise, an inline stub returns 0.

Control flow: Atmel drivers can call this helper unconditionally to adjust behavior while the platform is entering slow-clock suspend; non-PM builds take the neutral false path.

State and persistence: no state is stored here. Enabled builds query platform PM state maintained by AT91 suspend code.

Dependencies and integration points: integrates Atmel platform drivers with optional AT91 power-management code while preserving compile coverage for configurations without `CONFIG_ATMEL_PM`.

Risks and test signals: risks include the stub hiding PM-only assumptions and drivers relying on slow-clock status without selecting the config. Test compile with and without `CONFIG_ATMEL_PM`, suspend entry/exit behavior, and driver behavior around slow-clock transitions.
