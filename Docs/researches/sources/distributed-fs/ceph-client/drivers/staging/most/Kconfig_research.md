# sources/distributed-fs/ceph-client/drivers/staging/most/Kconfig

## Purpose
Defines the staging MOST components menu and includes component-specific Kconfig files.

## Important APIs, Types, And Functions
`MOST_COMPONENTS` is a tristate requiring `HAS_DMA`, `CONFIGFS_FS`, and `MOST`. It describes the core module name `most_core` and sources `net`, `video`, and `dim2` Kconfig files when enabled.

## Control Flow
Controls whether MOST component drivers are visible/selectable in kernel configuration.

## State And Persistence
No runtime state; persists as kernel config.

## Dependencies And Integration Points
Integrates with the MOST core framework, configfs, DMA support, and child component Kconfigs.

## Risks And Test Signals
Dependency mismatches can expose modules without required core support. Test signals are menuconfig visibility and builds with individual child components enabled/disabled.
