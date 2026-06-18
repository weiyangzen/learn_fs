# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmx-unavail.c

Purpose: focused stress test that VMX unavailable during a transaction does not corrupt checkpointed VMX0 after abort.

Important APIs/types/functions: `worker()` executes inline VMX/TM sequence; `tm_vmx_unavail_test()` launches 4x online CPU worker threads; global `passed` records corruption.

Control flow: each worker initializes VMX0 from a stack value, busy-waits to encourage VMX being turned off by the kernel, begins a transaction, executes a VMX instruction to trigger unavailable, then on abort compares VMX0 to the saved value. Mismatch prints TEXASR details.

State and persistence behavior: global `passed` is shared by worker threads. No persistent external state.

Dependencies and integration points: requires pthreads, VMX, ppc64, HTM, and `htmintrin.h`.

Risks and test signals: race/stress based, so absence of failure is not exhaustive. `passed` is unsynchronized but only clears to 0.
