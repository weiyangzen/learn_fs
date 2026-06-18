<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/seamcall.S -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/seamcall.S

## Purpose
`seamcall.S` provides host-side assembly wrappers for Intel SEAMCALL into P-SEAMLDR or the TDX module.

## Important APIs, types, and functions
Exports `__seamcall`, `__seamcall_ret`, and noinstr `__seamcall_saved_ret`, all implemented through `TDX_MODULE_CALL` from `tdxcall.S`.

## Control flow
Callers pass the leaf in RDI and a `struct tdx_module_args` pointer in RSI. The macro moves inputs into SEAMCALL registers, executes the module call, optionally saves outputs, and returns either `TDX_SEAMCALL_VMFAILINVALID` or the leaf completion status. The saved variant preserves/saves all argument registers for KVM TDH.VP.ENTER use.

## State and persistence behavior
No file-local data state exists; architectural state is the SEAMCALL register ABI and output fields written to the args structure.

## Dependencies and integration points
It depends on `tdxcall.S`, linkage/frame macros, TDX module ABI, and noinstr constraints for KVM entry paths.

## Risks and edge cases
Register clobber/save semantics are critical. Instrumentation is forbidden for the saved wrapper because KVM uses it in a non-instrumentable path.

## Test signals
Signals are TDX module initialization, KVM TDX entry/exit tests, objtool/noinstr validation, and SEAMCALL failure status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/seamcall.S -->
