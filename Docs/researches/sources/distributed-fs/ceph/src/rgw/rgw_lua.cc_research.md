## sources/distributed-fs/ceph/src/rgw/rgw_lua.cc

Purpose: implements RGW Lua script context naming, script CRUD through the SAL Lua manager, script syntax verification, and optional LuaRocks package allowlist/install support.

Important APIs/functions: `to_context()` maps case-insensitive strings such as `prerequest`, `postauth`, `background`, `getdata`, and `putdata` to `rgw::lua::context`; `to_string()` reverses it. `verify()` loads a script into a Lua state without executing it. `script_oid()` creates persistent object ids as `script.<context>.<tenant>`. `read_script()`, `read_script_or_bytecode()`, `write_script()`, and `delete_script()` call `sal::LuaManager`. Package functions behind `WITH_RADOSGW_LUA_PACKAGES` manage allowlisted LuaRocks packages.

Control flow: script CRUD is a thin null-checked manager dispatch returning `-ENOENT` if no manager exists. `add_package()` shells out to `luarocks search --porcelain`, optionally restricts to binary rocks, removes previous versions by base package name, then records the allowlist entry. `install_packages()` reads the allowlist, creates a parent and temporary tree, sets `HOME`, optionally logs `luarocks config`, and installs each package into the tree while collecting failures.

State and persistence: scripts and package allowlists persist in the SAL Lua manager, not local memory. `install_packages()` creates transient install directories and returns the chosen directory to callers for `package.path`/`cpath` setup.

Dependencies/integration: depends on Lua C API, `lua_state_guard`, SAL driver/LuaManager, Boost.Process, filesystem, and `CEPH_LUA_VERSION`.

Risks and test signals: shell command construction with package names is sensitive to quoting and input validation. `mkdtemp()` mutates the template string and installation directories must be cleaned by the owner. Tests should cover context parsing, invalid script syntax, missing manager handling, LuaRocks-not-found behavior, allowlist replacement, and failed package collection.
