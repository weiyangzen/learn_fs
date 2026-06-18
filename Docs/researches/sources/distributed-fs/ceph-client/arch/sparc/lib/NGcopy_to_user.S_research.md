# sources/distributed-fs/ceph-client/arch/sparc/lib/NGcopy_to_user.S

Purpose: First-generation Niagara copy-to-user wrapper over `NGmemcpy.S`.

Important APIs/functions: Defines guarded stores, `FUNC_NAME NGcopy_to_user`, user stores through `ASI_AIUS`, `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`, `EX_RETVAL(%g0)`, and ASI preamble.

Control flow: Verifies active ASI, branches to `raw_copy_in_user` if not user ASI, then executes NG copy paths with exception-protected stores.

State and persistence: No persistent state; relies on `%asi`, register-window locals, and exception-table fixups.

Dependencies/integration: Depends on `NGmemcpy.S` and Niagara copyops patching.

Risks/test signals: Store fixups must map from NG register-window residual helpers back to raw-copy semantics. Test protected destinations, short and long copies, and after-patch behavior.
