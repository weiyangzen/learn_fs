## sources/distributed-fs/ceph/src/rgw/rgw_lua.h

Purpose: public interface for RGW Lua administration and script/package persistence.

Important APIs/types: `enum class context` lists execution contexts: `preRequest`, `postAuth`, `postRequest`, `background`, `getData`, `putData`, and `none`. Declarations expose `to_context()`, `verify()`, `write_script()`, `read_script()`, `read_script_or_bytecode()`, and `delete_script()`. When package support is compiled in, `packages_t` plus `add_package()`, `remove_package()`, `list_packages()`, `reload_packages()`, and `install_packages()` form the package management API.

Control flow: callers convert external context names to `context`, verify and persist scripts through `sal::LuaManager`, then later retrieve either source or cached bytecode for request/data/background execution.

State and persistence: this header defines no storage itself. The contract is that script data is keyed by tenant and context in the Lua manager, while package allowlists are globally managed through the default Lua manager.

Dependencies/integration: includes Lua version/type helpers, async yield support, SAL forward declarations, and `DoutPrefixProvider`. It is consumed by REST/admin Lua endpoints, request/data filters, and background script execution.

Risks and test signals: all APIs return negative errno-style codes, so callers must preserve those semantics. Tests should cover context-string compatibility because external admin APIs rely on these names.
