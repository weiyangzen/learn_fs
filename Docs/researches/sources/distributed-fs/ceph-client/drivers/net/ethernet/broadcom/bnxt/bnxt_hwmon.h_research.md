# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwmon.h

## Purpose

`bnxt_hwmon.h` provides the conditional public interface for BNXT hwmon support. It declares real initialization, teardown, and notification functions when `CONFIG_BNXT_HWMON` is enabled, and no-op inline stubs otherwise so the rest of the driver can call hwmon hooks unconditionally.

## Important APIs

- `bnxt_hwmon_notify_event(struct bnxt *bp)` reports firmware thermal events to hwmon.
- `bnxt_hwmon_uninit(struct bnxt *bp)` unregisters any hwmon device.
- `bnxt_hwmon_init(struct bnxt *bp)` probes and registers hwmon temperature attributes.
- Disabled-config stubs are empty inline functions.

## Control flow role

BNXT core and async event code can call these hooks without local `#ifdef`s. The compile-time config selects either the implementation in `bnxt_hwmon.c` or no-op behavior.

## State and persistence behavior

The header stores no state. The real implementation mutates `bp->hwmon_dev` and temperature threshold caches; the stubs deliberately leave all state unchanged.

## Dependencies and integration points

- Depends on `struct bnxt` being visible to users.
- Integrates with driver probe/remove and firmware async event paths.
- Shields the rest of the driver from direct dependency on Linux hwmon APIs when the feature is disabled.

## Risks and edge cases

- Callers must not assume hwmon registration happened; with the config disabled every hook is a no-op.
- Any new hwmon hook should be added to both the enabled declarations and disabled stubs to keep call sites config-independent.

## Test signals

- Compile with `CONFIG_BNXT_HWMON=y` and `CONFIG_BNXT_HWMON=n`.
- Probe/remove and thermal async event paths should build and run with no conditional call-site changes.
