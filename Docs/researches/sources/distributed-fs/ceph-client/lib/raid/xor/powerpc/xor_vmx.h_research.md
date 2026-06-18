# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.h

Purpose: provides the small interface between PowerPC AltiVec implementation and glue files.

Important APIs and flow: declares `xor_gen_altivec_inner()` with the common XOR generator signature.

State and persistence: no state.

Dependencies and integration: included by `xor_vmx.c` and `xor_vmx_glue.c` to enforce separation between vector instruction implementation and vector-state enabling.

Risks and test signals: prototype mismatch is the main local risk; compile coverage catches it, while KUnit validates runtime behavior.
