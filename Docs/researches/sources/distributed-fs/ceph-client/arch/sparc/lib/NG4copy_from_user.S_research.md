# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_from_user.S

Purpose: Niagara4 optimized copy-from-user wrapper using `NG4memcpy.S`.

Important APIs/functions: Defines guarded load macros, `FUNC_NAME NG4copy_from_user`, `%asi` user loads, `EX_RETVAL(0)`, and `%asi` preamble.

Control flow: Validates the active ASI, falls back to `raw_copy_in_user` if needed, then executes NG4 alignment, prefetch, VIS/block, and tail paths with exception-protected loads.

State and persistence: Stateless except for temporary `%asi`, VIS, and exception-table fixup metadata.

Dependencies/integration: Depends on `NG4memcpy.S`, `Memcpy_utils.S`, `raw_copy_in_user`, and `niagara4_patch_copyops`.

Risks/test signals: Fault recovery through VIS paths and prefetch/copy interactions require testing. Exercise unmapped user sources, boundary lengths, and patched copy-from-user calls.
