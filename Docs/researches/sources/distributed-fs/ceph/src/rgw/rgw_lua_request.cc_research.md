## sources/distributed-fs/ceph/src/rgw/rgw_lua_request.cc

Purpose: implements the Lua request context, exposing RGW request state to scripts through nested Lua metatables and allowing selected request mutation, tracing, and logging.

Important APIs/functions: `create_top_metatable()` creates global `Request`. `execute()` runs a script/bytecode with request globals and optional integer return-code capture. `RequestLog()` invokes normal `rgw_log_op()`. `SetAttribute()` and `AddEvent()` expose tracing. Metatables model response errors, quotas, placement, user, trace, owner, bucket tags, bucket, object, ACL grants, IAM policies/statements, HTTP request info, copy source, zonegroup, and the top-level request.

Control flow: `execute()` creates a limited Lua state, opens libraries, sets package path from `s->penv.lua.manager`, creates debug action, installs `Request`, adds `RGW_ABORT_REQUEST`, attaches `Request.Log`, exposes background `RGW` if present, then calls `lua_execute()`. After success it attempts to read an integer return from the stack for script-controlled request handling.

State and persistence: scripts can mutate `s->err` response fields, `s->trace_enabled`, request HTTP metadata map, storage class, and empty-bucket URL name. Many nested structures are read-only. `Request.Log()` persists through configured ops-log sinks. Tracing calls persist in the active span when recording.

Dependencies/integration: depends on RGW request/operation state, ACL/IAM policy structures, SAL bucket/object interfaces, ops logging, trace span API, background Lua service, and Lua utilities.

Risks and test signals: the top-level script return-code path is suspicious because `lua_execute()` uses `luaL_dostring()`/`lua_pcall()` with zero expected results for bytecode, so returned values may not be consistently left on the stack. `RequestLog()` logs through normal sinks and may duplicate logs if scripts call it unexpectedly. Tests should cover every exposed field, write permissions, unknown field errors, trace no-op when not recording, IAM/ACL iteration, package path setup, abort return code semantics, and null/empty bucket/object cases.
