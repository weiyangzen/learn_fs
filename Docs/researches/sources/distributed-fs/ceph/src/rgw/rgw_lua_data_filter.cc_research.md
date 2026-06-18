## sources/distributed-fs/ceph/src/rgw/rgw_lua_data_filter.cc

Purpose: runs Lua scripts in object data paths for GET and PUT, exposing the current data chunk as a Lua `Data` table.

Important APIs/functions: `BufferlistMetaTable` gives Lua 1-based byte indexing, `pairs()` iteration, and length for `bufferlist`. `RGWObjFilter::execute()` creates the Lua VM and global tables. `RGWGetObjFilter::handle_data()` and `RGWPutObjFilter::process()` wrap RGW data pipelines.

Control flow: each data chunk creates a memory/runtime-limited state, opens restricted standard libraries, installs `RGWDebugLog`, creates `Data`, `Request`, and `Offset` globals, optionally exposes background `RGW`, then calls `lua_execute()` with script or bytecode. GET and PUT wrappers ignore filter execution errors and continue the underlying data pipeline.

State and persistence: no persistent data is written. Lua sees the chunk `bufferlist` by pointer for the duration of execution. `Offset` identifies the logical offset. Background `RGW` accesses shared in-memory state if available.

Dependencies/integration: depends on `RGWGetObj_Filter`, `rgw::putobj::Pipe`, request Lua metatables, process environment Lua background pointer, and `lua_state_guard`.

Risks and test signals: per-chunk VM creation can be expensive. The script cannot mutate `Data` through this metatable, so behavior is observational unless scripts modify request/background state. Because errors are ignored by design, tests should assert request success despite Lua failure and should validate byte iteration boundaries, offsets, and package path/debug availability.
