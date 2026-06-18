<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/Makefile

## Purpose
`virt/vmx/tdx/Makefile` builds the Intel TDX host support objects in the TDX subdirectory.

## Important APIs, types, and functions
It adds `seamcall.o` and `tdx.o` to `obj-y`.

## Control flow
Kbuild links the SEAMCALL assembly wrappers with the higher-level TDX host implementation.

## State and persistence behavior
No runtime state is held in the Makefile.

## Dependencies and integration points
It depends on parent `CONFIG_INTEL_TDX_HOST` selection and the sibling `tdx.o` source.

## Risks and edge cases
Object omission would leave TDX module call sites unresolved.

## Test signals
Signals are TDX host build/link success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/Makefile -->
