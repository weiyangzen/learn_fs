## sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.h

Purpose: declares Lua-backed GET/PUT object data filters.

Important APIs/types: `RGWObjFilter` stores `req_state*` and `LuaCodeType` and exposes `execute(bufferlist&, off_t, const char*)`. `RGWGetObjFilter` derives from `RGWGetObj_Filter` and overrides `handle_data()`. `RGWPutObjFilter` derives from `rgw::putobj::Pipe` and overrides `process()`.

Control flow: callers insert these wrappers into existing RGW data pipelines when `getdata` or `putdata` Lua scripts are configured. Each wrapper invokes `RGWObjFilter` and then forwards to the next filter/processor.

State and persistence: the classes retain only request/script references. Object data persistence remains owned by the surrounding GET/PUT pipeline.

Dependencies/integration: includes `rgw_op.h` for request and data pipeline base classes. Integrates with request Lua metatables and background Lua through the implementation.

Risks and test signals: `LuaCodeType` is copied into the filter, which is safe for script lifetime but may be costly for large bytecode. Tests should confirm forwarding still happens after Lua errors and that construction handles both source and bytecode variants.
