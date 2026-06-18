# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4copy_to_user.S

Purpose: Niagara4 optimized copy-to-user wrapper over `NG4memcpy.S`.

Important APIs/functions: Defines guarded store macros, `FUNC_NAME NG4copy_to_user`, user stores through `%asi`, `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`, and `EX_RETVAL(0)`.

Control flow: Checks `%asi`, diverts non-user ASI cases to `raw_copy_in_user`, then uses NG4 copy paths with exception-table protected stores.

State and persistence: No persistent data; transiently uses `%asi`, VIS state, and fixup table entries.

Dependencies/integration: Depends on `NG4memcpy.S`, `Memcpy_utils.S`, SPARC ASIs, and `NG4patch.S`.

Risks/test signals: Store faults in large optimized paths must leave correct residuals and restored state. Test destination faults, short and long copies, and post-fault continued kernel execution.
