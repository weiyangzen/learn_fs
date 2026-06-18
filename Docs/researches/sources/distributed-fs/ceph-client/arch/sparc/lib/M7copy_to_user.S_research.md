# sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_to_user.S

Purpose: M7 optimized copy-to-user wrapper using the shared `M7memcpy.S` copy engine with user-space stores.

Important APIs/functions: Defines integer/FP store exception wrappers, `FUNC_NAME M7copy_to_user`, `STORE(type,src,addr)` using `%asi`, `STORE_ASI ASI_BLK_INIT_QUAD_LDD_AIUS`, `EX_RETVAL(0)`, and a `%asi` preamble.

Control flow: Verifies user ASI before copying, then dispatches through M7 alignment and block-copy paths. Store faults are routed through exception-table entries to residual helpers.

State and persistence: No persistent storage. Temporarily manipulates `%asi` and VIS/FPU registers through included code.

Dependencies/integration: Depends on `M7memcpy.S`, `Memcpy_utils.S`, SPARC M7 block-init ASIs, `raw_copy_in_user`, and `m7_patch_copyops`.

Risks/test signals: Risks include incorrect store ASI selection, missed FP-state restoration after fault, and wrong residual counts. Test protected user destinations, unaligned sizes, large streaming copies, and post-fault FPU/VIS state.
