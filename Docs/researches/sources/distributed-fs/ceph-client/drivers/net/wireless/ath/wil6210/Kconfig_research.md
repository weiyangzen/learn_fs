# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/Kconfig

## Purpose
`Kconfig` declares build-time configuration for the Wilocity/Qualcomm Atheros `wil6210` 60 GHz IEEE 802.11ad wireless driver and its debug/tracing options.

## Important APIs, Types, and Functions
- `CONFIG_WIL6210` is a tristate driver option depending on `CFG80211` and `PCI`, selecting `WANT_DEV_COREDUMP` and `CRC32`.
- `CONFIG_WIL6210_ISR_COR` selects clear-on-read interrupt status handling, defaulting to enabled for production.
- `CONFIG_WIL6210_TRACING` enables kernel tracepoints when `EVENT_TRACING` is available.
- `CONFIG_WIL6210_DEBUGFS` enables debugfs support when `DEBUG_FS` is available.

## Control Flow
There is no runtime control flow. The selected options control which objects the Makefile builds and which conditional code paths are compiled.

## State and Persistence Behavior
Configuration persists in the kernel build configuration. Runtime impact includes whether interrupt registers use COR semantics and whether tracing/debugfs interfaces exist.

## Dependencies and Integration Points
The file integrates the driver into the kernel wireless Kconfig tree. It constrains the driver to PCI/cfg80211 systems and drives conditional objects in `Makefile`.

## Risks and Test Signals
Risks include selecting debug defaults that expose unsupported interfaces or disabling trace/debug objects required during field diagnosis. Test signals are build coverage for built-in/module/disabled states and all combinations of tracing/debugfs/ISR mode.
