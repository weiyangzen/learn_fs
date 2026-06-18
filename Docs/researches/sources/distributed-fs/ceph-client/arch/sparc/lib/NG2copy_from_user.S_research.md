# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_from_user.S

Purpose: Niagara2 optimized copy-from-user wrapper over `NG2memcpy.S`.

Important APIs/functions: Defines guarded `EX_LD` and `EX_LD_FP`, `FUNC_NAME NG2copy_from_user`, `%asi` user loads, block loads via `ASI_BLK_AIUS_4V`, and `EX_RETVAL(0)`.

Control flow: The preamble checks `%asi` and diverts non-user ASI cases to `raw_copy_in_user`. The included NG2 engine then selects alignment, VIS/block, medium, and tail paths; user loads are exception-table protected.

State and persistence: Stateless beyond temporary registers, VIS state, `%asi`, and exception-table entries.

Dependencies/integration: Depends on `NG2memcpy.S`, Niagara2 ASI definitions, `raw_copy_in_user`, and `niagara2_patch_copyops`.

Risks/test signals: User fault fixups, 4V block ASI behavior, and VIS restore are sensitive. Test user source faults, all alignments, large block paths, and patched runtime selection on Niagara2.
