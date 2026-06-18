## sources/distributed-fs/ceph/src/rgw/rgw_lua_request.h

Purpose: declares the public request-context Lua execution API.

Important APIs: `create_top_metatable(lua_State*, req_state*, const char*)` exposes `Request` into an existing Lua state. Two `execute()` overloads run Lua source/bytecode with `RGWREST`, `OpsLogSink`, `req_state`, `RGWOp`, and optionally return an integer script return code by reference.

Control flow: users either create only the metatable for a larger Lua environment, as data filters do, or run a complete request-context script through `execute()`.

State and persistence: this header itself stores no state. The implementation can mutate request state and write ops logs through the provided pointers.

Dependencies/integration: uses forward declarations to avoid pulling in RGW operation internals. Consumed by request processing and data filters.

Risks and test signals: because pointer arguments are not owning, caller lifetime is critical. Tests should include null/empty optional objects and ensure both overloads return consistent errno-style results.
