# sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_from_user.S

Purpose: First-generation Niagara copy-from-user wrapper over `NGmemcpy.S`.

Important APIs/functions: Defines guarded loads, `FUNC_NAME NGcopy_from_user`, `LOAD`, `LOAD_TWIN`, `EX_RETVAL(%g0)`, and ASI-checking preamble.

Control flow: Checks `%asi`, falls back to `raw_copy_in_user`, then runs the windowed `NGmemcpy.S` implementation. User loads and twin loads are exception protected.

State and persistence: Stateless; uses register-window state from the included implementation plus `%asi` and exception tables.

Dependencies/integration: Depends on `NGmemcpy.S`, `raw_copy_in_user`, and `niagara_patch_copyops`.

Risks/test signals: `NGmemcpy.S` uses input registers and save/restore style, so fault paths must match register conventions. Test user-source faults, all length buckets, and patched copy-from-user calls.
