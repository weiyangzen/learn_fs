## sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.cc

Purpose: implements shared Lua runtime utilities: debug logging, library restriction, package path setup, memory/runtime guarded Lua state creation, and script/bytecode execution.

Important APIs/functions: `create_debug_action()` installs global `RGWDebugLog`; `stack_dump()` prints Lua stack diagnostics; `set_package_path()` sets Lua `package.path` and `package.cpath`; `open_standard_libs()` opens libraries and removes dangerous loaders/debug/`os.exit`; `allocator()` enforces memory limits; `lua_state_guard` owns a Lua state and perf counter accounting; `lua_execute()` runs a `LuaCodeType`.

Control flow: `lua_state_guard` creates a Lua state with a custom allocator, sets panic conversion to C++ exceptions, and optionally installs a runtime hook. The hook checks elapsed wall time on line/count events and raises Lua errors past the limit. Destructor disables limits for cleanup, closes Lua, logs possible leaks, and decrements VM counters.

State and persistence: state is per Lua VM. Memory usage is tracked in `lua_state_guard::mem_in_use`; runtime configuration is stored in the Lua registry as lightuserdata to guard-owned fields.

Dependencies/integration: depends on Lua C API, Ceph context/logging, perf counters, `CEPH_LUA_VERSION`, and `LuaCodeType`.

Risks and test signals: `pushtime()` in the header uses `std::localtime`, which is not thread-safe. The destructor computes a percentage with `max_memory`; logging when max is zero could be fragile if memory remains. `lua_execute()` for source uses `luaL_dostring()`, which discards detailed result handling expectations. Tests should cover memory-limit allocation failure, runtime limit, restricted globals, package path values, bytecode load errors, and perf counter increments/decrements.
