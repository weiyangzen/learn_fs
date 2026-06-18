# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_hwrm.h

## Purpose

`bnxt_hwrm.h` defines the public BNXT HWRM request-management API and the private context/token structures used by `bnxt_hwrm.c`. It centralizes request buffer layout constants, timeout constants, request flags, wait-token states, CHIMP/KONG channel routing helpers, and typed initialization/send/drop/dma-slice prototypes.

## Important APIs, types, and macros

- `enum bnxt_hwrm_ctx_flags` controls request ownership internals and caller-visible behavior: silent errors and full timeout.
- `struct bnxt_hwrm_ctx` records managed request/response DMA state, optional indirect DMA slice, request length, flags, timeout, allocation watermark, and GFP flags.
- `enum bnxt_hwrm_wait_state` and `struct bnxt_hwrm_wait_token` model pending/deferred/complete/cancelled mailbox completions.
- `enum bnxt_hwrm_chnl` distinguishes CHIMP and KONG mailbox channels.
- Layout constants define one DMA buffer containing request, context, and response regions: `BNXT_HWRM_DMA_SIZE`, `BNXT_HWRM_RESP_OFFSET`, `BNXT_HWRM_CTX_OFFSET`, alignment, reserved response size, and request size limits.
- Timeout constants define short initial sleeps, normal sleep ranges, maximum command timeouts, reset timeout, and valid-bit wait.
- `bnxt_cfa_hwrm_message()` and `bnxt_kong_hwrm_message()` route CFA and explicit KONG-targeted commands to the KONG mailbox when firmware supports it.
- Public API prototypes include request init, hold, drop, flags, timeout, send, silent send, replacement, allocation flags, DMA slices, and token updates.
- `bnxt_hwrm_func_cfg_short_req_init()` initializes a shortened HWRM_FUNC_CFG request for older devices with smaller max request lengths.

## Control flow role

Callers use the `hwrm_req_init(bp, req, TYPE)` macro to allocate a typed request based on `sizeof(*req)`. They fill fields, optionally call customization helpers, and call send/drop helpers. Header inline routing functions are evaluated by `__hwrm_send()` to select the firmware mailbox channel. The short FUNC_CFG helper lets callers avoid `-E2BIG` by intentionally truncating fields not needed by older firmware.

## State and persistence behavior

The header defines state structures but does not instantiate them. Instances are embedded in managed DMA buffers or allocated as wait tokens at runtime. No persistent storage is managed here, but HWRM commands declared through this API can produce persistent firmware/device side effects.

## Dependencies and integration points

- Includes `<linux/bnxt/hsi.h>` for HWRM request IDs, target IDs, and wire structures.
- Requires `struct bnxt`, DMA APIs, RCU list handling, and firmware capability bits defined in BNXT core headers.
- Used across the BNXT driver as the standard firmware command API.

## Risks and edge cases

- Any layout constant change must preserve the non-overlapping request/context/response memory map expected by `bnxt_hwrm.c`.
- Adding public flags requires updating `HWRM_API_FLAGS`; internal flags must not be settable by callers.
- KONG routing depends on a maintained list of CFA request types. New CFA commands can accidentally go to CHIMP unless added.
- `BNXT_HWRM_MAX_REQ_LEN` is macro-expanded from `bp`; it is only valid in scopes where `bp` exists.
- Short FUNC_CFG requests intentionally use `min(sizeof, bp->hwrm_max_ext_req_len)` and must only be used when omitted trailing fields are not needed.

## Test signals

- Compile all HWRM users after adding new request types or flags.
- Exercise KONG-routed CFA commands and CHIMP-routed ordinary commands.
- Verify old-firmware short FUNC_CFG paths avoid oversized request failures.
- Static analysis for misuse of request ownership flags and invalid macro contexts.
