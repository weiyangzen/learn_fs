# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx_glue.c

Purpose: wraps PowerPC AltiVec XOR in safe kernel vector-state handling and publishes the `altivec` template.

Important APIs and flow: `xor_gen_altivec()` disables preemption, enables kernel AltiVec, calls `xor_gen_altivec_inner()`, disables AltiVec, then re-enables preemption. `xor_block_altivec` exposes the function to the XOR core.

State and persistence: no durable state; it temporarily changes CPU vector-state ownership.

Dependencies and integration: depends on `<asm/switch_to.h>` and the PowerPC registration header.

Risks and test signals: preemption and vector state bracketing are critical. Signals include KUnit under preemptible kernels, RAID workloads, and absence of vector-state corruption warnings.
