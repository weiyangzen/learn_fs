## sources/distributed-fs/ceph/src/rgw/rgw_lua_background.h

Purpose: declares the Lua background service and the Lua-visible `RGW` shared table metatable.

Important APIs/types: `BackgroundMapValue` is `std::variant<std::string, long long int, double, bool>`; `BackgroundMap` maps names to values. `RGWTable` implements `__index`, `__newindex`, `__len`, and `__pairs` for the `RGW` Lua table, including reserved `increment` and `decrement` function names. `Background` owns the runner thread, script manager, shared table, bytecode cache, and pauser hooks.

Control flow: writers call `put_table_value()` from C++ or assign `RGW[key]` from Lua. Lua writes validate supported value types, total key/value size, and max entry count; assigning `nil` erases keys and updates iterator metadata. Background lifecycle is start/shutdown/pause/resume, with script updates queued through `process_script_add()`.

State and persistence: table contents are process-local and disappear on restart. Cached bytecode is process-local. Script source persists through `LuaManager`.

Dependencies/integration: includes `rgw_realm_reloader.h`, `rgw_lua_utils.h`, Boost lockfree queue, shared mutexes, and Ceph logging. The class is held by `AppMain` and registered with the realm reloader pauser set.

Risks and test signals: table limits (`MAX_LUA_VALUE_SIZE`, `MAX_LUA_KEY_ENTRIES`) need boundary tests. Lua iterator invalidation logic is subtle, especially erasing during iteration. Background shutdown must join the thread before `LuaManager`/Ceph context teardown.
