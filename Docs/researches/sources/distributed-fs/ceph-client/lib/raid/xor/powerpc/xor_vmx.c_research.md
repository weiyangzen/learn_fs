# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.c

Purpose: implements the raw PowerPC AltiVec XOR inner loop.

Important APIs and flow: uses `vector signed char` as the native vector type. `__xor_altivec_{2,3,4,5}` load four vector registers from each buffer, combine sources with `vec_xor()`, store the destination, and advance by four vectors. `__DO_XOR_BLOCKS()` emits `xor_gen_altivec_inner()`.

State and persistence: no persistence; destination memory changes in place. The caller must have enabled kernel AltiVec.

Dependencies and integration: includes `<altivec.h>` outside sparse checking and exports the inner function declared by `xor_vmx.h`; `xor_vmx_glue.c` wraps it.

Risks and test signals: risks include AltiVec ABI/compiler issues and vector-state use outside the critical section. Signals are PowerPC build/sparse coverage, KUnit XOR tests, and boot calibration output.
