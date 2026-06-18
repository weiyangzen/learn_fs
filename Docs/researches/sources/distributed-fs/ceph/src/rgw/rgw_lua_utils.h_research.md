## sources/distributed-fs/ceph/src/rgw/rgw_lua_utils.h

Purpose: declares and templates the Lua metatable framework used to expose C++ RGW state safely to Lua scripts.

Important APIs/types: `lua_state_guard` owns a limited VM. Constants define max value/key counts, upvalue indexes, and return-count helpers. `create_metatable()` builds Lua tables with `__index`, `__newindex`, `__pairs`, and `__len` closures bound to arbitrary C++ upvalues. `EmptyMetaTable` provides default read-only/non-iterable behavior. Generic helpers include `pushstring()`, `pushvalue()`, `pushtime()`, `StringMapWriteableNewIndex()`, iterator metadata helpers, `next()`, `Pairs()`, and `StringMapMetaTable`.

Control flow: RGW-specific metatable structs implement static closures and pass themselves to `create_metatable()`. For maps, `Pairs()` creates an iterator closure; `create_iterator_metadata()` stores/reuses iterator userdata and prevents overlapping iterations.

State and persistence: templates bind non-owning pointers into Lua closures as lightuserdata. Iterator state is held in Lua userdata/metatables. Map writes mutate the underlying C++ maps directly.

Dependencies/integration: used heavily by request, data, and background Lua code. Includes perf counters, Ceph time, Lua, and `LuaCodeType`.

Risks and test signals: non-owning lightuserdata requires the C++ object to outlive Lua execution. Iterator reuse and invalidation are subtle. Size checks use `strnlen()` with fixed limits. Tests should cover readonly errors, unknown field errors, map deletion during iteration, nested-iteration rejection, nil handling, and write limits.
