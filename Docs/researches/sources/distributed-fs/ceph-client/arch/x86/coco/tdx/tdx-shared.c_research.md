# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx-shared.c

## Purpose
Shared TDX helpers for accepting private memory and issuing TDVMCALL hypercalls. This code is small enough to be shared with early contexts.

## Important APIs, Types, And Functions
`tdx_accept_memory()` accepts a physical range using `TDG_MEM_PAGE_ACCEPT`, trying 1G, then 2M, then 4K chunks through `try_accept_one()`. `__tdx_hypercall()` wraps `__tdcall_saved_ret(TDG_VP_VMCALL)` and returns the TDVMCALL leaf status from R10.

## Control Flow And State
Memory acceptance advances `start` only when a module call succeeds for an aligned chunk. If no page size succeeds, it returns false and leaves the remaining range unaccepted. Hypercall setup overwrites `args->rcx` with the shared-register exposure mask, treats failure of the TDCALL mechanism itself as fatal via `__tdx_hypercall_failed()`, and otherwise returns the VMM-provided leaf result.

## Dependencies And Integration
Depends on `__tdcall()` and `__tdcall_saved_ret()` from `tdcall.S`, TDX leaf IDs, page-level sizing, and `cc_mkdec()/cc_mkenc()` users in `tdx.c`. `tdx_enc_status_changed()` calls `tdx_accept_memory()` for shared-to-private conversion; most TDX emulation paths call `__tdx_hypercall()`.

## Risks And Test Signals
Risks include alignment mistakes, accepting only part of a range, interpreting module failure as VMM leaf failure, and wrong RCX exposure mask. Signals include memory hotplug/acceptance tests, shared-private conversion tests, TDX boot on systems supporting large SEPT pages, and TDVMCALL error injection.
