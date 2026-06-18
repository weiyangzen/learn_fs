# sources/distributed-fs/ceph-client/drivers/misc/lkdtm/cfi.c

## Purpose
`lkdtm/cfi.c` provides LKDTM crash types for forward-edge and backward-edge control-flow integrity. It checks whether mismatched indirect-call prototypes are blocked and whether stack return-address tampering is stopped by PAC or shadow call stack.

## Important APIs, types, and functions
Forward-edge testing uses `lkdtm_increment_void`, `lkdtm_increment_int`, `lkdtm_indirect_call`, and `lkdtm_CFI_FORWARD_PROTO`. Backward-edge testing uses `set_return_addr_unchecked`, `set_return_addr`, architecture-specific `FRAME_RA_OFFSET`, `no_pac_addr`, and `lkdtm_CFI_BACKWARD`. The `crashtypes` array exports `CFI_FORWARD_PROTO` and `CFI_BACKWARD` through `cfi_crashtypes`.

## Control flow
`CFI_FORWARD_PROTO` first performs a valid indirect call, then casts an incompatible function pointer and calls it through the same indirect-call helper. With CFI enabled, the mismatched call should trap before the final failure message. `CFI_BACKWARD` first demonstrates that an unprotected helper can rewrite the return address, then tries the same through a normal helper and expects PAC or shadow call stack to preserve control flow.

## State and persistence
`called_count` records indirect-call side effects, and `force_check` prevents compiler simplification while making label addresses reachable. No state is persistent beyond module lifetime.

## Dependencies and integration points
The file depends on LKDTM core registration, compiler CFI instrumentation, arm64 pointer authentication/BTI/SCS attributes, RISC-V frame layout differences, `__builtin_frame_address`, labels-as-values, and page-offset masking for PAC-stripped comparisons.

## Risks
The return-address tests depend on compiler frame layout and architecture calling conventions. If the helper cannot find the return address, the test warns instead of proving mitigation behavior. Special attributes intentionally disable PAC/SCS for the unchecked helper, so build-flag drift can invalidate the test.

## Test signals
A protected kernel should trap or report expected mitigation behavior before `FAIL` messages. Useful configurations include `CONFIG_CFI`, `CONFIG_ARM64_PTR_AUTH_KERNEL`, `CONFIG_SHADOW_CALL_STACK`, and builds without those mitigations to verify warning/XFAIL behavior.
