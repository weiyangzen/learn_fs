# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.c

## Purpose

`bnxt_hwrm.c` is the BNXT Host Wire Resource Manager request framework. It allocates DMA-backed request/response contexts, validates request ownership with sentinels, supports indirect DMA slices, sends requests through CHIMP or KONG firmware mailboxes, waits for completion by polling or completion-ring token updates, maps firmware error codes to Linux errno values, and releases all resources consistently.

## Important APIs and functions

- Request lifecycle:
  - `__hwrm_req_init()` allocates a DMA-pool buffer, lays out request, response, and context regions, initializes common request fields, and returns a typed request pointer.
  - `hwrm_req_hold()` marks the context caller-owned and returns the response pointer so callers can inspect response data or reuse a request.
  - `hwrm_req_drop()` releases owned or unsent requests and any associated slice.
  - `__hwrm_ctx_drop()` frees external slices, invalidates the context, and returns the backing buffer to the DMA pool.
- Request customization:
  - `hwrm_req_timeout()` sets per-request timeout.
  - `hwrm_req_alloc_flags()` changes GFP flags for future DMA slice allocation.
  - `hwrm_req_flags()` applies public behavior flags such as silent logging or full wait.
  - `hwrm_req_replace()` copies or references prebuilt request data while preserving managed response DMA resources.
  - `hwrm_req_dma_slice()` suballocates indirect DMA memory from unused request-buffer space or allocates one external coherent slice.
- Send/completion:
  - `hwrm_req_send()` validates the context and calls `__hwrm_send()`.
  - `hwrm_req_send_silent()` sets silent logging then sends.
  - `__hwrm_send()` chooses CHIMP/KONG channel, assigns a sequence token, optionally wraps large/short-command requests in `hwrm_short_input`, writes the mailbox, rings the doorbell, waits for response, validates response sequence and valid bit, maps firmware error codes, and consumes or preserves the context based on ownership.
  - `hwrm_update_token()` is called from completion handling to mark a pending CHIMP token as deferred/complete/cancelled.
- Support helpers:
  - `hwrm_calc_sentinel()` and `__hwrm_ctx()` detect invalid request pointers or use-after-free.
  - `__hwrm_to_stderr()` maps HWRM error codes to Linux errno.
  - `bnxt_kong_hwrm_message()` is declared inline in the header and used to route CFA/KONG-targeted messages.

## Control flow

Callers allocate a request with `hwrm_req_init()` or `__hwrm_req_init()`, fill request-specific fields, optionally allocate DMA slices or hold the request, and call `hwrm_req_send()` or `hwrm_req_send_silent()`. Unheld requests are consumed automatically on send completion or error. Held requests remain valid after send and must be dropped by the caller.

`__hwrm_send()` first clears a previously dirty response for held/reused requests, validates firmware access, rejects oversized requests, and routes KONG mailbox traffic when needed. It acquires a wait token under `bp->hwrm_cmd_lock`; CHIMP tokens are inserted into an RCU pending list so completion interrupts can update them, while KONG tokens are local because KONG ring completions are not supported.

For short command mode or messages larger than the maximum inline mailbox request length, the function builds a `struct hwrm_short_input` pointing at the full DMA request buffer. It writes the request words into BAR0 mailbox space, zeroes remaining mailbox words, rings the firmware doorbell, and then waits.

If the request uses a completion ring, it waits for `hwrm_update_token()` to mark the token complete. Otherwise, it polls `ctx->resp->resp_len`, checks the response sequence id, tolerates and logs out-of-sequence responses, then waits for the final response valid byte. In both paths it aborts on fatal firmware state or unhealthy firmware status when health registers are reliable.

After a valid response, it clears the valid byte for forward compatibility, reads `error_code`, logs non-success errors unless silent, maps the error, releases the token, and either marks a held response dirty for future reuse or drops the context.

## State and persistence behavior

- Per-request state lives in `struct bnxt_hwrm_ctx`: DMA handle, request/response pointers, optional external slice, request length, flags, timeout, allocation watermark, GFP flags, and sentinel.
- Global sequencing state lives in `bp->hwrm_cmd_seq`, `bp->hwrm_cmd_kong_seq`, `bp->hwrm_cmd_lock`, and `bp->hwrm_pending_list`.
- Firmware health state is observed through `bp->fw_health`, `BNXT_STATE_FW_FATAL_COND`, and health register reads.
- No durable persistence exists. The framework sends commands that may cause persistent side effects in caller-specific HWRM operations, such as NVM writes.

## Dependencies and integration points

- DMA pool allocation (`bp->hwrm_dma_pool`) and coherent DMA for indirect slices.
- PCI BAR0 mailbox/register access with `__iowrite32_copy()`, `writel()`, and firmware-specific CHIMP/KONG offsets.
- RCU pending-list integration with completion handlers in the RX/TX/completion path.
- Firmware health monitoring helpers and BNXT state bits.
- HWRM request/response wire structures from `<linux/bnxt/hsi.h>`.
- Callers across nearly every BNXT module, including ethtool, PTP, hwmon, link, VNIC, filters, rings, and NVM.

## Risks and edge cases

- The request pointer is a managed pointer into a larger DMA buffer; passing copied, stale, or external pointers trips sentinel checks and indicates driver bugs.
- Held requests require strict `hwrm_req_drop()` discipline. Missing drops leak DMA pool buffers or external coherent slices.
- Only one external DMA slice is supported per request; repeated large slice requests log stack traces and fail.
- The suballocation math in `hwrm_req_dma_slice()` must avoid overlap with request payload and prior allocations.
- Short-command mode and request replacement must preserve `resp_addr` and sentinel correctness even when the request body is externally supplied.
- Sequence handling is critical. Out-of-sequence responses are logged and ignored; persistent sequence confusion leads to timeouts.
- Completion-ring waits require `hwrm_update_token()` from interrupt context. Missed completions or wrong sequence id cause timeouts.
- The valid-byte clearing assumes response length is valid and nonzero; malformed firmware responses can still lead to timeout/error paths.
- KONG commands reject completion-ring usage; callers must use polling semantics.

## Test signals

- Request lifecycle tests for unheld send, held send/drop, reuse after dirty response, aborted unsent drop, replacement request, and slice allocation/free.
- Fault injection for DMA pool allocation failure, coherent slice allocation failure, oversized request, invalid request pointer, duplicate hold, duplicate drop, and repeated external slice allocation.
- Firmware simulation for success, busy, invalid params, access denied, no buffer, unsupported command, PF unavailable, out-of-sequence responses, missing valid bit, timeout, deferred token, and fatal firmware health.
- Runtime tracing should confirm all HWRM callers drop held requests and that `bp->hwrm_pending_list` is empty after command completion.
