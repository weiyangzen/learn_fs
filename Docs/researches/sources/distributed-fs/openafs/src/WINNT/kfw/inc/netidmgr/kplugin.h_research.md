# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kplugin.h

## Purpose

`kplugin.h` defines the required exported callbacks and symbol names for NetIDMgr plugin modules. It is the binary contract that lets KMM load a DLL, initialize it, discover provided plugins, route plugin messages, and optionally run module cleanup.

## Important APIs, Types, and Functions

- `init_module(kmm_module h_module)` is the required module initialization entry point.
- `init_module_t` is its function-pointer type.
- `EXP_INIT_MODULE` is the exported symbol name, undecorated on Win64 and `_init_module@4` on 32-bit stdcall.
- `_plugin_proc()` is the KMQ-compatible plugin message processor prototype; `_plugin_proc_t` aliases `kmq_callback_t`.
- `exit_module(kmm_module h_module)` is the optional cleanup entry point.
- `exit_module_t` is its function-pointer type.
- `EXP_EXIT_MODULE` mirrors architecture-specific export decoration.

## Control Flow

KMM loads a module DLL and resolves `EXP_INIT_MODULE`. `init_module()` runs on the plugin-manager thread in the current user context. It must not rely on `DllMain` for NetIDMgr API calls; instead it calls `kmm_set_locale_info()` for localization and `kmm_provide_plugin()` for every plugin implemented by the module. If it returns `KHM_ERROR_SUCCESS` and provides plugins, KMM initializes those plugins and routes KMQ messages to their message processors. On unload or failed init, KMM stops plugins, then calls optional `exit_module()` before unloading the module and any resource libraries.

## State and Persistence Behavior

The callback declarations themselves hold no state. Module/plugin runtime state is tracked by KMM handles and plugin message processors. Registration metadata and locale information are persisted or managed through `kmm.h`. A module that provides no plugins is immediately exited and unloaded even if `init_module()` succeeds.

## Dependencies and Integration Points

`kplugin.h` includes `kmm.h` and `kherror.h`. It is consumed by plugin DLLs and by KMM's dynamic loader. The callback contracts interact with KMQ (`_plugin_proc_t`), module locale/resource APIs, and plugin registration/lifecycle state in `kmm.h`.

## Risks and Edge Cases

- Export decoration differs by architecture; incorrect `.def` files or compiler calling conventions make modules unloadable.
- Calling NetIDMgr APIs from `DllMain` can deadlock or observe uninitialized subsystems; the header explicitly directs initialization into `init_module()`.
- `exit_module()` is optional and its return value is ignored, so critical cleanup should generally live in per-plugin shutdown paths as well.
- `init_module()` success without provided plugins still causes immediate unload.
- The documentation mentions `kmm_set_locale()` but the declared API in `kmm.h` is `kmm_set_locale_info()`, so plugin authors should follow the actual declaration.

## Test Signals

- Build sample plugins for x86 and x64 and verify exported names match `EXP_INIT_MODULE` and `EXP_EXIT_MODULE`.
- Load a module that provides one plugin, multiple plugins, no plugins, and an init failure.
- Confirm `kmm_provide_plugin()` is accepted only during `init_module()`.
- Verify KMQ messages reach `_plugin_proc` and shutdown calls `exit_module()` after plugin exit.
