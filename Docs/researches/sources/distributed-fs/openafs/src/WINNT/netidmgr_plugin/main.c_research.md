# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/main.c

## Purpose
Module-level entry point for the core AFS NetIDMgr plugin DLL.

## Important APIs, Types, And Functions
Defines KMM module/resource handles, configuration-space handles (`csp_plugins`, `csp_afscred`, `csp_params`), supported locales, placeholder `init_afs()`/`exit_afs()`, `init_module()`, `exit_module()`, and `DllMain()`.

## Control Flow
`init_module()` sets locale info, delays Heimdal loading, registers the `AfsCred` credential plugin with dependencies and icon/description, initializes delayed imports, opens the NetIDMgr plugin configuration root, loads `schema_afsconfig`, and opens `AfsCred/Parameters`. `exit_module()` calls delayed import cleanup, closes config spaces, unloads the schema, and clears globals. `DllMain()` records `hInstance` and calls the empty AFS attach/detach hooks.

## State And Persistence
Maintains open handles to plugin configuration spaces and loads a configuration schema. It does not directly write configuration values.

## Dependencies And Integration Points
Integrates KMM module lifecycle, `afs_plugin_cb()` from `afsplugin.c`, resource strings/icons from language DLLs, dynamic imports, Kerberos compatibility delay loading, and schema data from `afsconfig.c`.

## Risks
If initialization fails after `kmm_provide_plugin()`, partial registration may rely on KMM cleanup. Config handles must be opened before other plugin code reads `csp_params`. `DllMain()` intentionally does little, which is correct for loader-lock safety.

## Test Signals
Module load with missing resources, missing imports, schema load failure, normal unload, and successful availability of `csp_params` to new-credential/config paths.
