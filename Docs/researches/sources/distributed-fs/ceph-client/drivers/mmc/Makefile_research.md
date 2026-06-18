# sources/distributed-fs/ceph-client/drivers/mmc/Makefile

## Purpose
Routes top-level MMC Kbuild traversal into core and host subdirectories.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_MMC) += core/` builds the core.
- `obj-$(subst m,y,$(CONFIG_MMC)) += host/` descends into host drivers whenever MMC is enabled.

## Control Flow
Kbuild enters `core/` according to the MMC tristate and enters `host/` for both built-in and modular MMC so host drivers can decide their own object modes.

## State And Persistence
Build graph only; no runtime state.

## Dependencies And Integration Points
Integrates with Kbuild and child Makefiles under `drivers/mmc/core` and `drivers/mmc/host`.

## Risks And Edge Cases
Misrouting here can omit every MMC host or the core. The `subst m,y` pattern is intentional for modular builds.

## Test Signals
Inspect build logs for `CONFIG_MMC=y/m/n` and confirm expected descent into `core/` and `host/`.
