# sources/distributed-fs/ceph-client/drivers/nfc/st21nfca/se.c

## Purpose
`se.c` implements secure-element support for the HCI-based ST21NFCA driver. It discovers UICC/eSE presence, activates/deactivates secure elements via device-management events, handles APDU exchange through the APDU reader gate, and reports connectivity/transaction events.

## Important APIs, types, and functions
- `st21nfca_hci_discover_se()`, `st21nfca_hci_enable_se()`, `st21nfca_hci_disable_se()`, and `st21nfca_hci_se_io()` implement the HCI secure-element ops.
- `st21nfca_hci_control_se()` sends UICC/eSE activate/deactivate events, waits for hot-plug/pipe completion, and validates host-list state.
- `st21nfca_se_get_atr()` and `st21nfca_se_get_bwi()` derive APDU wait timeout from ATR.
- `st21nfca_connectivity_event_received()` reports connectivity and transaction events to NFC core.
- `st21nfca_apdu_reader_event_received()` completes APDU I/O and sends end-of-transfer.
- BWI timeout is split between timer callback and `timeout_work` to avoid doing reset work directly in timer context.

## Control flow
Discovery adds UICC/eSE entries unless factory mode is set. Enable sends the correct activation event, starts a hot-plug timer, waits for completion, validates the host list, and for eSE reads ATR then soft-resets the SE. APDU I/O stores callback context, arms BWI timer, and sends transmit-data on the APDU reader gate. Response events cancel timer/work, send end-of-transfer to device management, and call the user callback. WTX events extend the BWI timer. Timeout work alternates soft reset and hard reset, then calls the callback with `-ETIME`.

## State and persistence
`struct st21nfca_se_info` stores ATR, completion, BWI/activation timers, active flags, expected/count pipes, exchange-error toggle, callback/context, and timeout work. State is runtime-only; presence booleans come from platform properties.

## Dependencies and integration points
The file depends on NFC HCI APIs, NFC secure-element APIs, timers, workqueues, and event handlers called from `core.c`.

## Risks
Host-list scanning can read past the skb if the requested host id is absent. Error returns in transaction parsing may leave skb ownership ambiguous. APDU callbacks are stored globally per device, so concurrent APDU requests would race. Disable does not perform the eSE end-of-transfer best-effort path used by ST_NCI.

## Test signals
Test factory mode discovery suppression, UICC/eSE enable/disable success and absent-host failure, ATR/BWI parsing, APDU success and WTX extension, APDU timeout soft/hard reset alternation, end-of-transfer failure handling, and malformed transaction TLVs.
