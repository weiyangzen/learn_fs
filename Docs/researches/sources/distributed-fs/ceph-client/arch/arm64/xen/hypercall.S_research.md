# sources/distributed-fs/ceph-client/arch/arm64/xen/hypercall.S

## Purpose

implements arm64 Xen hypercall stubs used by the Xen guest front-end and privcmd paths

## Important APIs, Types, and Functions

Source read size: 130 lines, 4332 bytes. Includes: `linux/linkage.h`, `asm/assembler.h`, `asm/asm-
uaccess.h`, `xen/interface/xen.h`. Assembly/global entries: `HYPERVISOR_##hypercall`,
`HYPERVISOR_dm_op`, `privcmd_call`. Key macros/defines: `XEN_IMM`, `HYPERCALL_SIMPLE(hypercall)`,
`HYPERCALL0`, `HYPERCALL1`, `HYPERCALL2`, `HYPERCALL3`, `HYPERCALL4`, `HYPERCALL5`.

## Control Flow and Behavior

HYPERCALL_SIMPLE emits wrappers that load a Xen immediate and trap via hvc; HYPERVISOR_dm_op and
privcmd_call provide argument reshuffling and return handling for special hypercall forms

## State and Persistence

no kernel state is persisted by the assembly itself; state changes occur in the hypervisor as a
result of the trap

## Dependencies and Integration Points

depends on Xen public hypercall numbering, arm64 calling convention, and linkage macros used by
arch/arm64 Xen support

## Risks and Test Signals

register ordering and hvc immediate values are ABI-critical; Xen guest boot, grant/device
operations, and privcmd tests exercise this code
