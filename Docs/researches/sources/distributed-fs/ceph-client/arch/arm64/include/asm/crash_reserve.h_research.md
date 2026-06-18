## sources/distributed-fs/ceph-client/arch/arm64/include/asm/crash_reserve.h

Purpose: declares architecture crash-kernel reservation initialization.

Important APIs/types/functions: exposes `crash_reserve_memblock(void)` when crash dump support is configured, otherwise an empty inline stub.

Control flow: early boot calls reserve memory for crash kernels when enabled.

State and persistence: reservation state lives in memblock and later kexec crash structures; this header only declares the hook.

Dependencies and integration: integrates arm64 early memory setup with kdump/kexec.

Risks: incorrect reservation can overlap normal memory or fail to preserve crash kernel memory. Test signals are `crashkernel=` boot tests, kdump capture, memblock debug output, and kexec-tools validation.
