# sources/distributed-fs/ceph-client/drivers/watchdog/watchdog_pretimeout.h

## Purpose
This header defines the watchdog pretimeout governor interface and provides either real declarations or stubbed inline fallbacks depending on `CONFIG_WATCHDOG_PRETIMEOUT_GOV`.

## Important APIs, types, and functions
It defines `WATCHDOG_GOV_NAME_MAXLEN`, forward-declares `struct watchdog_device`, and defines `struct watchdog_governor` with a fixed-length `name` and `pretimeout` callback. Enabled builds declare governor registration, watchdog pretimeout registration, available-governor listing, and per-device governor get/set functions. Disabled builds return success for registration/unregistration no-ops and `-EINVAL` for sysfs governor operations.

## Control flow
Consumers include this header unconditionally. Compile-time conditionals decide whether calls link to `watchdog_pretimeout.c` or fold into harmless stubs. The default governor macro is selected from `CONFIG_WATCHDOG_PRETIMEOUT_DEFAULT_GOV_NOOP` or `CONFIG_WATCHDOG_PRETIMEOUT_DEFAULT_GOV_PANIC`.

## State and persistence
The header has no state of its own. It controls whether runtime governor state exists in the pretimeout subsystem.

## Dependencies and integration points
It is included by watchdog core code and governor implementations. Its stub design lets `watchdog_dev.c` compile without pretimeout governor support while keeping call sites simple.

## Risks and test signals
Risks are mismatches between Kconfig defaults and the macro, fixed name truncation, and call sites assuming sysfs operations work when governors are disabled. Test signals include builds with governor support disabled, noop default, panic default, and pretimeout-capable devices under each configuration.
