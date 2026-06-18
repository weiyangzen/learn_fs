# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.c

## Purpose
This file implements the generic Host Wire Resource Manager request engine. It allocates DMA-backed request/response buffers, validates request ownership with a sentinel, sends commands through the CHIMP mailbox registers, waits for completion or polled response validity, maps firmware errors to Linux errno values, and cleans up HWRM resources.

## Important APIs, Types, And Functions
Public APIs include `bnge_init_hwrm_resources`, `bnge_cleanup_hwrm_resources`, `bnge_hwrm_req_create`, `bnge_hwrm_req_init`, `bnge_hwrm_req_hold`, `bnge_hwrm_req_drop`, `bnge_hwrm_req_flags`, `bnge_hwrm_req_timeout`, `bnge_hwrm_req_alloc_flags`, `bnge_hwrm_req_replace`, `bnge_hwrm_req_send`, `bnge_hwrm_req_send_silent`, and `bnge_hwrm_req_dma_slice`. Internal helpers include `bnge_cal_sentinel`, `__hwrm_ctx_get`, `bnge_hwrm_create_token`, `bnge_hwrm_destroy_token`, `bnge_map_hwrm_error`, and `__hwrm_send_ctx`.

## Control Flow
Callers allocate a typed HWRM request with `bnge_hwrm_req_init`, optionally hold the response buffer, populate command-specific fields, then call `bnge_hwrm_req_send`. `__hwrm_send_ctx` creates a wait token under `bd->hwrm_cmd_lock`, assigns a sequence ID, writes the request window to BAR0, rings the CHIMP doorbell, and either waits for completion-ring processing or polls `resp_len` and the response valid byte. On exit it destroys the token and either invalidates the context or leaves it owned for callers that held the response.

## State And Persistence
The persistent driver state is `bd->hwrm_dma_pool`, `bd->hwrm_pending_list`, `bd->hwrm_cmd_seq`, `bd->hwrm_cmd_kong_seq`, and command timeout/capability fields populated elsewhere. Per-command state is held in `struct bnge_hwrm_ctx`, including DMA address, request length, response dirty flag, timeout, optional coherent DMA slice, and ownership flags.

## Dependencies And Integration Points
It integrates with every HWRM command wrapper in `bnge_hwrm_lib.c`, link management, ring allocation, and resource setup. It uses Linux DMA pools, coherent DMA, RCU hlist deletion for pending CHIMP tokens, PCI BAR I/O, memory barriers, and HSI `struct input`/`struct output`.

## Risks
Risks concentrate around lifetime and concurrency: invalid requests are caught only by the sentinel, held responses must be dropped, command buffers can be reused with `bnge_hwrm_req_replace`, and cleanup marks pending tokens cancelled after destroying the DMA pool. Timeout math and response valid-byte handling are hardware-sensitive. DMA slices allow only one external allocation per context, so callers must size requests correctly.

## Test Signals
Probe-time HWRM version, function capability, resource, link, ring, VNIC, and stats commands provide coverage. Fault signals include timeout logs, out-of-sequence response warnings, busy firmware warnings, sentinel mismatch dumps, and leaked or double-dropped request contexts under error injection.
