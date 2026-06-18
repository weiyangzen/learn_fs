# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_configfs.h

## Purpose
This header declares the configfs interface and provides no-op/default fallbacks when `CONFIG_CONFIGFS_FS` is disabled.

## Important APIs, Types, and Functions
It exposes subsystem lifecycle functions, device-check diagnostics, getters for survivability, GT type masks, engine masks, PSMI, context restore mid/post BB data, and SR-IOV PF options. Fallback inlines return conservative defaults such as both GTs allowed, all engines allowed, PSMI disabled, and module/default SR-IOV limits.

## Control Flow
There is no executable flow beyond inline fallback returns. Compile-time conditionals select the real configfs implementation or default behavior.

## State and Persistence Behavior
The header stores no state. With configfs enabled, state is held by `xe_configfs.c`; without it, all settings are effectively immutable defaults.

## Dependencies and Integration Points
It includes defaults, engine class types, and module parameter declarations. Callers can use the getters unconditionally without scattering configfs `#ifdef` logic through probe and engine code.

## Risks
Fallback defaults must match `xe_configfs.c` defaults or behavior diverges by kernel configuration. SR-IOV fallback is especially important because it mixes module parameters and default admin-only PF policy.

## Test Signals
Build both with and without configfs enabled. Probe tests should confirm that disabling configfs preserves normal GT/engine discovery, PSMI off, and module-parameter max_vfs behavior.
