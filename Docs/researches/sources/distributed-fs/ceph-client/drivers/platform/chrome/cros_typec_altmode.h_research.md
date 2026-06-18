<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.h

## Purpose

This header declares the Chrome EC Type-C altmode registration helpers and provides build-time fallbacks when DisplayPort or Thunderbolt altmode support is disabled.

## Important APIs, Types, And Functions

It forward-declares `struct cros_typec_port`, `struct typec_altmode`, `struct typec_altmode_desc`, and `struct typec_displayport_data`. With `CONFIG_TYPEC_DP_ALTMODE`, it declares `cros_typec_register_displayport()` and `cros_typec_displayport_status_update()`. Without that config, the registration helper falls back to `typec_port_register_altmode()` and status updates become no-ops. The Thunderbolt section similarly declares or stubs `cros_typec_register_thunderbolt()`.

## Control Flow

Including code calls these helpers without needing local `#ifdef` blocks. The compiled configuration either routes to Chrome EC-specific altmode operations or to plain Type-C altmode registration.

## State And Persistence

The header owns no state. It controls whether per-altmode private state from `cros_typec_altmode.c` exists in the build.

## Dependencies And Integration Points

It depends on `linux/kconfig.h` for `IS_ENABLED()` and `linux/usb/typec.h` for Type-C core declarations. It is consumed by Chrome EC Type-C code that wants optional DP/TBT support.

## Risks

The fallback functions register plain altmodes without Chrome EC VDM/enter/exit handling, so runtime behavior differs substantially in reduced configs. The inline fallback references `port->port`, requiring callers to include a complete `struct cros_typec_port` definition before use.

## Test Signals

Compile with DP/TBT enabled and disabled, ensure callers build in all combinations, and verify reduced configurations still register altmodes without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.h -->
