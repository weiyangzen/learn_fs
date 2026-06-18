# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/dep.c

## Purpose
`dep.c` implements NFC-DEP/NFCIP-1 handling for ST21NFCA in both target mode and initiator mode. It builds/parses ATR, PSL, and DEP request/response PDUs and bridges them to the NFC core's DEP activation/data callbacks.

## Important APIs, types, and functions
- PDU structs model ATR_REQ/RES, PSL_REQ/RES, and DEP_REQ/RES.
- Target-mode handlers receive ATR_REQ/PSL_REQ/DEP_REQ on card-F events and send ATR_RES/PSL_RES/DEP_RES.
- Initiator-mode functions `st21nfca_im_send_atr_req()` and `st21nfca_im_send_dep_req()` send reader-F exchange commands and process async responses.
- `st21nfca_dep_event_received()` dispatches card-F HCI events.
- `st21nfca_dep_init()` initializes delayed TX work and default DEP state; `st21nfca_dep_deinit()` cancels it.

## Control flow
Target mode receives card-F send-data events, distinguishes NFCIP request commands, replies to ATR_REQ using peer NFCID3/general bytes, reports activation with `nfc_tm_activated()`, handles PSL speed changes, and passes DEP payloads to `nfc_tm_data_received()`. Initiator mode sends ATR_REQ with local general bytes and target NFCID3/random fallback, waits for ATR_RES, stores remote general bytes, reports link-up, and optionally sends PSL if the remote LRI differs. DEP_REQ/RES handling maintains the current packet number information (PNI) and handles supervisor PDUs by rewrapping and resending.

## State and persistence
`struct st21nfca_dep_info` stores pending TX skb, work item, current PNI, target index, timeout, DID, bitrate, and length-reduction information. State is runtime-only and reset during init/link activation.

## Dependencies and integration points
The file depends on HCI async command/event APIs, NFC DEP target-mode and initiator callbacks, random bytes for NFCID3 fallback, and the async callback fields in `struct st21nfca_hci_info`.

## Risks
Several callbacks return early on parse errors without freeing received skbs, relying on HCI callback ownership conventions that should be verified. `st21nfca_im_recv_dep_res_cb()` uses `ST21NFCA_NFC_DEP_PFB_PNI(dep_res->pfb + 1)`, which appears suspicious because it increments the PFB before masking. Async callback fields are global to the device and can be overwritten by overlapping operations. `st21nfca_tx_work()` uses `tx_pending` without NULL checks.

## Test signals
Test ATR_REQ/RES with and without general bytes, ATR length bounds, PSL bitrate changes, DEP I-PDU/ACK/NACK/supervisor handling, PNI progression, target-mode activation, initiator link-up callback, async callback overwrite prevention, and work cancellation on remove.
