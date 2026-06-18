# sources/distributed-fs/ceph-client/arch/sparc/lib/NG2copy_to_user.S

Purpose: Niagara2 optimized copy-to-user wrapper over `NG2memcpy.S`.

Important APIs/functions: Defines `EX_ST`, `EX_ST_FP`, `FUNC_NAME NG2copy_to_user`, user stores through `ASI_AIUS`, block stores through `ASI_BLK_AIUS_4V`, and `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`.

Control flow: Checks `%asi`, falls back to `raw_copy_in_user` when needed, then runs NG2 copy paths with store exception fixups for faults.

State and persistence: No persistent data. Uses `%asi`, VIS/FPU registers, and exception-table records.

Dependencies/integration: Depends on `NG2memcpy.S`, SPARC 4V user block ASIs, `Memcpy_utils`/local residual helpers, and Niagara2 patching.

Risks/test signals: Store faults at block boundaries and tail copies must return accurate residuals. Test protected user destinations, partial copies, ASI fallback, and large copy throughput.
