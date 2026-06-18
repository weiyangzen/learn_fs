# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-debug.h

## Purpose
Defines the iwlwifi logging/debug macro surface and debug-level bit taxonomy.

## Important APIs, Types, and Functions
Important pieces are `iwl_have_debug_level()`, `enum iwl_err_mode`, low-level declarations, `CHECK_FOR_NEWLINE`, `IWL_ERR`, `IWL_WARN`, `IWL_INFO`, `IWL_CRIT`, `IWL_DEBUG*`, hex dump helpers, and debug masks from `IWL_DL_INFO` through `IWL_DL_TX_QUEUES`.

## Control Flow
Macros validate literal format strings end in newline, resolve a module/transport object to `dev`, and dispatch to low-level implementations. Debug macros compile to no-op device printing when debug support is disabled, while tracing can still keep `__iwl_dbg()` available.

## State and Persistence Behavior
Debug-level state is the module parameter `debug_level`. Logs and trace events are external outputs.

## Dependencies and Integration Points
Depends on `iwl-modparams.h`, device logging implementation in `iwl-debug.c`, and trace definitions. Used by almost every iwlwifi file.

## Risks
The macros assume the first argument has a `dev` member unless using `_DEV` variants. `CHECK_FOR_NEWLINE` requires compile-time string literals. Debug bit additions must avoid collisions.

## Test Signals
Builds with/without `CONFIG_IWLWIFI_DEBUG` and device tracing, call-site compile failures for missing newline, ratelimited debug macros, and sysfs/debugfs debug-level toggling are useful.
