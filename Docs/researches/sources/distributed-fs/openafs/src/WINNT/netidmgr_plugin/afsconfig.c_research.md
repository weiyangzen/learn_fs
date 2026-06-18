# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsconfig.c

## Purpose

`afsconfig.c` is generated configuration schema data for the OpenAFS NetIDMgr credential provider. It declares the tree of plugin configuration spaces and default values consumed by the plugin at registration and runtime.

## Important APIs, types, and functions

The only exported object is `kconf_schema schema_afsconfig[]`. It defines the root `AfsCred` space, metadata keys `Module`, `Description`, `Dependencies`, `Type`, and `Flags`, plugin options such as `Cells` and `Disableafscreds`, the nested `Parameters` space with `AFSEnabled`, `LRUCells`, `LRURealms`, and `DefaultCells`, plus a `Cells` space for per-identity cell mappings and per-cell `_Schema` values `MethodName`, deprecated `Method`, and `Realm`.

## Control flow

There is no runtime code. NetIDMgr configuration registration walks the schema array until `KC_ENDSPACE` entries close nested spaces.

## State and persistence behavior

Defaults become persistent configuration values when NetIDMgr creates or opens plugin spaces. User changes are later written through `khc_write_*` calls in dialog and credential code. The schema stores multi-string-like options as `KC_STRING` values.

## Dependencies and integration points

The file includes `kconfig.h` and is declared in `afscred.h`. Plugin initialization registers it so `csp_afscred` and `csp_params` can be opened and read by `afsconfigdlg.c`, `afsfuncs.c`, and new-credential UI code.

## Risks and edge cases

The file is generated and warns not to edit directly. Duplicate space names (`Parameters` under `AfsCred`, and `Cells` used both as a string and a nested space name) require consumers to open the correct path. `Method` is marked deprecated but retained for compatibility; code must prefer `MethodName` where supported.

## Test signals

Configuration tests should verify schema registration, default `AFSEnabled=1`, default `Disableafscreds=0`, default empty LRU/default cell lists, and migration behavior for deprecated numeric method values.
