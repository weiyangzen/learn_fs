<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_regs.h

## Purpose
`pdma0_core_ctx_regs.h` defines the PDMA0 core context programming registers. These registers describe one programmed DMA context, including rate/power settings, transfer dimensions, source/destination offsets and bases, and commit.

## Important APIs, types, and functions
The file exports `mmPDMA0_CORE_CTX_*` macros. Important registers include rate-limit token, power low-power control, transfer engine row count, context index/index increment, context control, source transfer sizes, source and destination offset low/high pairs, source and destination base low/high pairs, destination transfer size, and `COMMIT`.

## Control flow
There is no code here. DMA setup writes context index/control, transfer sizes, base addresses, and offsets, then writes `COMMIT` to make the context visible to hardware. Status and core registers in `pdma0_core_regs.h` expose active context state during execution.

## State and persistence
The hardware context registers persist the current programmed DMA descriptor/context until overwritten, committed, or reset. Base/offset/size values are critical transfer state and must match MMU/security policy.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this file works with `pdma0_core_regs.h` for global PDMA enable/status and `pdma0_core_ctx_axuser_regs.h` for transaction attributes. Queue-manager code may launch PDMA work that consumes these context definitions.

## Risks and test signals
Incorrect size or base registers can cause memory corruption. Context index/increment mistakes can overwrite the wrong context. Test signals include PDMA memcpy/fill tests over small and large transfers, boundary/offset tests, context commit visibility, status matching the active context, and protection faults for intentionally invalid addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_ctx_regs.h -->
