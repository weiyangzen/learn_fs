# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmm.h

## Purpose

`kmm.h` declares the NetIDMgr Module Manager API. It controls module and plugin registration, loading/unloading, dependency handling, runtime handles, plugin/module information queries, enable/disable state, configuration namespaces, and localization resource libraries.

## Important APIs, Types, and Functions

- Opaque handles `kmm_module` and `kmm_plugin` are `khm_handle`.
- Limits define maximum name, description, vendor, support URI, dependency count, dependant count, and dependency multistring sizes.
- `kmm_plugin_reg` describes a plugin: name, owning module, type, flags, KMQ message processor, dependency multistring, description, and optional icon.
- `kmm_plugin_info` extends registration with runtime state, failure count/time/reason, handle, and disabled flag.
- Plugin types are credential, identity, configuration, and miscellaneous.
- Plugin states cover failure reasons, placeholder, registered, preinit, hold, init, running, and exited.
- `kmm_module_reg` describes a module path, descriptive metadata, and provided plugin registrations.
- `kmm_module_info` adds language, state, versions, failure data, and handle.
- Module states cover failure reasons and lifecycle from none through preinit/init/init plugins/running/exit plugins/exit/exited.
- Runtime APIs initialize/exit KMM, identify current plugin/module, load/unload/default-load modules, query pending loads and state, get Win32 module handle, hold/release module/plugin handles, provide plugins during `init_module()`, and query plugin state.
- Registration/config APIs open module/plugin config spaces, get info by name or handle, enumerate plugins, enable plugins, register/unregister plugins and modules.
- Localization APIs define `kmm_module_locale`, `LOCALE_DEF`, default-locale flag, `kmm_set_locale_info()`, `kmm_get_resource_hmodule()`, and convenience resource-loading macros.

## Control Flow

The core calls `kmm_init()`, loads default modules from configuration, and eventually calls `kmm_exit()`. Loading can be async or sync. A module is loaded from its registered path, its `init_module()` entry point runs, and the module calls `kmm_provide_plugin()` for each plugin. KMM initializes plugin message processors after module init, respecting dependencies; unresolved dependencies put plugins on hold. Unload reverses the lifecycle: plugins exit, then module exit runs, then resource libraries are released. Registration APIs can be used by installers or tools to persist module/plugin metadata before runtime.

## State and Persistence Behavior

KMM maintains runtime module/plugin handles with reference counts and state machines. It also persists registration, enable/disable state, failure counts, failure timestamps, module paths, plugin dependencies, and metadata in configuration spaces opened via `kconfig.h`. Locale selection loads a resource module for the current user locale and stores the selected language on module info.

## Dependencies and Integration Points

`kmm.h` depends on `khdefs.h`, `kmq.h`, Windows `HMODULE`/`HICON`/resource APIs, `kconfig.h` for configuration spaces, and `kplugin.h` for required module exports. Plugin message processors are KMQ callbacks and consume message types from `khmsgtypes.h`. OpenAFS NetIDMgr plugin modules use this interface to provide AFS credential and configuration plugins.

## Risks and Edge Cases

- `KMM_MAXCB_DESC` is defined using `KMM_MAXCCH_NAME` rather than `KMM_MAXCCH_DESC`, likely undercounting description bytes.
- `kmm_provide_plugin()` is only valid during `init_module()`; late calls must fail.
- Async `kmm_load_module()` success only means queued, not loaded; callers must query state or wait.
- Automatic registration uses user configuration, which can diverge from machine registration expectations.
- Dependencies are stored as multistrings with fixed maximum count/length; malformed or unterminated multistrings can block plugin startup.
- Direct use of `kmm_get_hmodule()` can desynchronize state if callers perform arbitrary Win32 module operations.

## Test Signals

- Register modules/plugins with maximum-length metadata, dependencies, duplicate names, and disabled flags.
- Load modules sync and async, checking every state transition and failure reason.
- Verify dependency ordering, hold state, failure propagation, and plugin enable/disable persistence.
- Query info by name and handle, then release internal-buffer info correctly.
- Exercise locale matching, default fallback, and convenience resource macros.
