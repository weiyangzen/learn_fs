## sources/distributed-fs/ceph/src/rgw/rgw_lua_types.h

Purpose: defines the shared type used to carry either Lua source text or compiled Lua bytecode.

Important API/type: `using LuaCodeType = std::variant<std::string, std::vector<char>>;`.

Control flow: producers read scripts or bytecode from the Lua manager/background cache; consumers pass the variant to `lua_execute()`, which dispatches on the active alternative.

State and persistence: source strings and bytecode vectors are value types. Persistence is external to this header.

Dependencies/integration: included by Lua administration, request execution, data filters, and utility code.

Risks and test signals: callers must understand that `std::string` means executable source while `std::vector<char>` means Lua bytecode. Tests should cover both alternatives wherever scripts are executed.
