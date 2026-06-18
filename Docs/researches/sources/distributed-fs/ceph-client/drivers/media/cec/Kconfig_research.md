# sources/distributed-fs/ceph-client/drivers/media/cec/Kconfig

Purpose: This file defines the CEC core feature symbols and the user-visible HDMI CEC driver menu. It separates internal core objects (`CEC_CORE`, `CEC_NOTIFIER`, `CEC_PIN`) from optional RC integration, pin error injection, and the driver families sourced beneath I2C/platform/USB.

Important APIs, types, and functions: Symbols include tristate `CEC_CORE`, bool `CEC_NOTIFIER`, bool `CEC_PIN`, `MEDIA_CEC_RC`, `CEC_PIN_ERROR_INJ`, and menuconfig `MEDIA_CEC_SUPPORT`. `MEDIA_CEC_RC` depends on `CEC_CORE` and `RC_CORE` with module/builtin compatibility; `CEC_PIN_ERROR_INJ` depends on `CEC_PIN` and `DEBUG_FS`.

Control flow and state: When `MEDIA_CEC_SUPPORT` is enabled, this file sources the CEC I2C, platform, and USB driver menus. Drivers select `CEC_CORE` and any helper features they require. Pin error injection is only available for pin-backed adapters and debugfs-enabled kernels.

State and persistence behavior: Only `.config` state is affected. Runtime behavior is delegated to the core and drivers selected here.

Dependencies and integration points: Integrates with RC core for CEC remote-control passthrough, debugfs for pin error injection, and subordinate CEC driver trees. The core symbol is tristate so CEC can be a module while helper flags are boolean feature inclusions.

Risks and edge cases: Incorrect `depends on CEC_CORE=m || RC_CORE=y`-style module compatibility can produce invalid link combinations. Because `CEC_NOTIFIER` and `CEC_PIN` are bool helpers selected by drivers, new drivers must select them explicitly when they call notifier or pin APIs.

Test signals: Kconfig tests should cover CEC core as built-in/module, RC integration with RC built-in vs module, debugfs on/off, and driver menus hidden when `MEDIA_CEC_SUPPORT=n`.
