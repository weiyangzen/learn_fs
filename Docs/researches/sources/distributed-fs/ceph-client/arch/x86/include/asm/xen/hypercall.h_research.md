<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypercall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypercall.h

Purpose: Implements the Linux x86 Xen hypercall calling convention. It wraps Xen hypercalls in inline assembly, hides 32-bit versus 64-bit register assignments, routes calls through a static call trampoline, and exposes typed helpers for common Xen operations.

Important APIs/types/functions: `xen_hypercall_func`, `DECLARE_STATIC_CALL(xen_hypercall, ...)`, `_hypercall0` through `_hypercall4`, `xen_single_call()`, `privcmd_call()`, `__xen_stac()`, `__xen_clac()`, `HYPERVISOR_*` wrappers for trap table, MMU update, GDT, callback, debug registers, descriptor updates, VA mappings, scheduler, timer, MCA, platform, memory, multicall, event channel, Xen version, console, physdev, grant table, vm assist, vCPU, suspend, HVM, PMU, and device-model ops; `MULTI_*` multicall builders.

Control flow: Callers enter a typed `HYPERVISOR_*` wrapper, which loads hypercall number in `a/eax` and arguments into the Xen ABI registers, emits a call to the static-call trampoline, and returns the result. Privcmd and dm_op paths wrap the hypercall in `STAC`/`CLAC` because the hypervisor accesses user buffers. PV-only sections expose trap/MMU multicall helpers.

State and persistence behavior: No private runtime state is stored here, but it relies on the global static-call target for the active hypercall page/trampoline. Multicall builders populate caller-owned `struct multicall_entry` objects and emit trace events.

Dependencies and integration points: Depends on x86 alternative/static-call infrastructure, SMAP, nospec branch support, page-table types, Xen public interfaces, and Xen tracepoints. Integrated with Xen PV MMU batching, grant tables, event channels, platform ops, suspend, device model, and privileged userspace `privcmd`.

Risks and test signals: Highest risks are register constraint mistakes, clobber omissions, SMAP window errors, and ABI mismatch between 32-bit and 64-bit. Test with Xen PV and HVM boots, MMU update stress, multicall batching traces, suspend/resume, grant-table mapping, privcmd ioctls, module builds, objtool validation, and compiler variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypercall.h -->
