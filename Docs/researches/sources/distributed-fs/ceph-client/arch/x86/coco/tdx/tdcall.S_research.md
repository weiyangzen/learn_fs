# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdcall.S

## Purpose
Assembly wrappers for TDX guest TDCALL and TDVMCALL operations. They provide C-callable noinstr entry points around the shared `TDX_MODULE_CALL` macro.

## Important APIs, Types, And Functions
Defines `__tdcall()`, `__tdcall_ret()`, and `__tdcall_saved_ret()`. The first issues a TDX module call without saving output registers, the second saves RCX/RDX/R8-R11 outputs to `struct tdx_module_args`, and the third saves all argument registers for TDVMCALL-style interactions. Inputs are passed as leaf ID in RDI and args pointer in RSI.

## Control Flow And State
Each wrapper moves the leaf into RAX via the macro implementation, exposes the configured register set, executes TDCALL, and returns the status in RAX or the TDVMCALL error path convention. The file lives in `.noinstr.text`, so it avoids instrumentation and must preserve ABI expectations exactly.

## Dependencies And Integration
Includes `../../virt/vmx/tdx/tdxcall.S` for the macro body and depends on offsets for `struct tdx_module_args`. `tdx.c` and `tdx-shared.c` rely on these wrappers for TD metadata reads/writes, #VE info retrieval, memory acceptance, attestation, and hypercalls.

## Risks And Test Signals
Risks are register ABI drift, CFI/unwind mismatch, noinstr violations, and incorrect saved-register masks exposing private state to the VMM. Signals are objtool validation, TDX guest boot, TDREPORT/RTMR calls, TDVMCALL failures, and low-level ABI tests around all output registers.
