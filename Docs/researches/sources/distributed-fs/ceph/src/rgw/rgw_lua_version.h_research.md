## sources/distributed-fs/ceph/src/rgw/rgw_lua_version.h

Purpose: centralizes the Lua major/minor version string used for Lua package paths.

Important API/type: `const std::string CEPH_LUA_VERSION(LUA_VERSION_MAJOR "." LUA_VERSION_MINOR);`.

Control flow: package installation and runtime path setup append this version to `share/lua/<version>` and `lib/lua/<version>` paths.

State and persistence: no runtime state beyond a constant string initialized from Lua headers.

Dependencies/integration: includes `lua.hpp` for `LUA_VERSION_MAJOR`/`LUA_VERSION_MINOR`. Used by `rgw_lua.cc` and `rgw_lua_utils.cc`.

Risks and test signals: compiled Lua version and installed LuaRocks version must match. Tests should verify package path construction when building against different Lua versions.
