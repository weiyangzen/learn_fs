## sources/distributed-fs/ceph/src/rgw/rgw_lua_background.cc

Purpose: implements the RGW Lua background execution thread, a shared Lua-visible `RGW` table, and script-to-bytecode caching for faster request/data-context execution.

Important APIs/functions: `RGWTable::increment_by()` backs `RGW.increment()`/`RGW.decrement()`. `Background::start()`, `shutdown()`, `pause()`, and `resume()` control the runner thread. `initialize_lguard_state()` creates a limited Lua VM with libraries, package path, debug action, and the `RGW` table. `process_script_add()`, `process_scripts()`, and `get_script_bytecode()` manage bytecode cache updates.

Control flow: `run()` loops until stopped. If paused, it waits. Otherwise it initializes a fresh Lua state, reads the tenantless background script, executes it when present, updates success/failure counters, processes queued script compile work, and sleeps for `execute_interval` or until stop. `process_scripts()` drains a lockfree queue, reads updated scripts from `LuaManager`, compiles them with `luaL_loadstring()`, dumps bytecode using `lua_dump()`, and stores it in a shared cache.

State and persistence: persistent scripts live in `LuaManager`; runtime state is `rgw_map`, a mutex-protected in-memory map of string/integer/double/bool values visible to Lua as `RGW`. Bytecode cache is in-memory and protected by `std::shared_mutex`.

Dependencies/integration: used by `RGWRealmReloader::Pauser`, request/data Lua contexts, SAL Lua manager, perf counters, and Ceph thread naming/logging.

Risks and test signals: `RGWTable::increment_by()` manually calls `mtx.unlock()` while using `unique_lock`, which is a correctness hazard if reached. Queue capacity is fixed at 16 and dropped pushes are silently retained only by unreleased ownership behavior. Tests should cover pause/resume, absent script, runtime/memory limit failures, map mutation/iteration, bytecode cache refresh/removal, and background table visibility from request/data scripts.
