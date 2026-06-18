# sources/distributed-fs/ceph-client/arch/sh/kernel/return_address.c

Purpose: implements `return_address()` for SH when the DWARF unwinder is available.

Important APIs and control flow: `return_address(depth)` repeatedly calls `dwarf_unwind_stack()` up to the requested depth, frees the previous frame each iteration, stops when no frame or return address exists, frees the final frame, and returns the resolved return address as a pointer. The symbol is exported GPL.

State, dependencies, and risks: state is transient DWARF frame allocations. Dependencies include DWARF unwinder readiness and frame reliability; without `CONFIG_DWARF_UNWINDER` the implementation is absent. Risks include returning NULL for assembly/unwinder gaps and relying on interrupt/ftrace graph handling in `dwarf.c`. Test signals are callers such as tracing/debug helpers requesting shallow/deep return addresses and behavior with/without DWARF unwinder.
