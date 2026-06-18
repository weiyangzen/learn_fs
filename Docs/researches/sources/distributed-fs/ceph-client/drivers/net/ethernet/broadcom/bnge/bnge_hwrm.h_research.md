# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.h

## Purpose
This header declares the HWRM request context model, wait-token state machine, mailbox channel constants, timeout constants, DMA layout, and public request APIs used by all firmware-command wrappers.

## Important APIs, Types, And Functions
Important types are `enum bnge_hwrm_ctx_flags`, `struct bnge_hwrm_ctx`, `enum bnge_hwrm_wait_state`, `enum bnge_hwrm_chnl`, and `struct bnge_hwrm_wait_token`. Important constants define the DMA pool layout: `BNGE_HWRM_DMA_SIZE`, `BNGE_HWRM_RESP_OFFSET`, `BNGE_HWRM_CTX_OFFSET`, `BNGE_HWRM_DMA_ALIGN`, and `BNGE_HWRM_SENTINEL`. `bnge_hwrm_timeout` converts polling loops into approximate elapsed microseconds for diagnostics.

## Control Flow
The header supports a create/populate/send/drop flow. `bnge_hwrm_req_init` wraps `bnge_hwrm_req_create` with the typed request size. Callers may use `bnge_hwrm_req_hold` to keep the response valid across send, `bnge_hwrm_req_dma_slice` to reserve command-adjacent DMA, and `bnge_hwrm_req_flags` or `bnge_hwrm_req_timeout` to alter send behavior.

## State And Persistence
The context state is per request and lives inside the DMA allocation. Flags distinguish internal ownership, dirty held responses, silent error logging, and full waits. Wait tokens live on the device pending list for CHIMP completions and carry sequence IDs and state transitions from pending to deferred, complete, or cancelled.

## Dependencies And Integration Points
The header depends on `<linux/bnge/hsi.h>` for common HWRM input/output layouts. It is included by command wrappers, resource setup, link management, and netdev initialization. It assumes `struct bnge_dev` has HWRM timeout, DMA pool, and pending-list members.

## Risks
The layout constants assume a two-page DMA object where request, context, and response do not overlap. Any request larger than `BNGE_HWRM_CTX_OFFSET` is invalid. The API is intentionally `void *` based, so type safety relies on caller discipline and runtime sentinel validation.

## Test Signals
Compilation with HSI structures is the first guard. Runtime coverage comes from commands that hold responses, commands that need custom timeouts, replacement of requests for larger messages, and commands requiring DMA slices such as tables or backing-store configuration.
