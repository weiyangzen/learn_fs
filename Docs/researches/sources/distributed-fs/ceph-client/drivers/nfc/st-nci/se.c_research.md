# sources/distributed-fs/ceph-client/drivers/nfc/st-nci/se.c

## Purpose
`se.c` implements ST_NCI secure-element and HCI-session support. It loads dynamic HCI pipe state, manages UICC/eSE discovery and activation, handles APDU reader and connectivity events, and enforces APDU timeout recovery.

## Important APIs, types, and functions
- `st_nci_hci_load_session()` connects the device-management gate, queries existing pipe lists/info, maps open pipes into the NCI HCI gate tables, and connects link management.
- `st_nci_discover_se()`, `st_nci_enable_se()`, `st_nci_disable_se()`, and `st_nci_se_io()` implement secure-element NCI ops.
- `st_nci_hci_event_received()` dispatches HCI events by gate to admin, APDU reader, and connectivity handlers.
- `st_nci_hci_cmd_received()` counts opened pipes during activation.
- `st_nci_hci_network_init()` creates an HCI access connection, sets gate init data/session id, initializes HCI session, and enables/disables NFCEE based on factory mode.
- Timers `bwi_timer` and `se_active_timer` handle APDU wait extension and hot-plug/pipe activation waits.

## Control flow
During secure-element discovery, HCI network initialization creates an NFCEE HCI connection and session. Unless factory mode is set, a whitelist is programmed from device properties and UICC/eSE entries are added to NFC core. Enabling an SE calls `nci_nfcee_mode_set()`, waits for hot-plug/open-pipe completion, rechecks host list, and for eSE reads ATR plus sends a soft reset. APDU I/O stores the caller callback/context, starts BWI timeout, and sends APDU data on the APDU reader gate. APDU reader transmit responses stop the timer and call the callback; WTX events extend the timer. Connectivity transaction events parse AID/parameters TLVs and report through `nfc_se_transaction()`.

## State and persistence
`struct st_nci_se_info` stores secure-element presence pointer, ATR, request completion, BWI timeout, activation timeout, active flags, exchange-error toggle, APDU callback, and callback context. HCI session id is generated from `"ST21BH"` plus a bitmap-selected device number, but the bitmap is not cleared in visible remove code. No file persistence is used.

## Dependencies and integration points
The file depends on NCI HCI APIs, NCI core connection APIs, NFC secure-element APIs, timer/completion APIs, and ST_NCI device-management gates. It consumes `ese-present` and `uicc-present` status supplied by physical layers.

## Risks
Host-list scanning reads `sk_host_list->data[i]` after a loop that can end at `i == len`, risking out-of-bounds if the host is absent. Several event parse error paths return without freeing skb, depending on caller handling. `st_nci_se_deinit()` exists but `st_nci_remove()` does not call it directly. BWI timeout calls the APDU callback from timer context after sending reset events, so callback assumptions matter.

## Test signals
Test pipe-list discovery with existing dynamic pipes, factory mode skipping SE activation, host list absent/present cases, UICC/eSE enable/disable, ATR-derived BWI timeout, WTX extension, APDU response callback, APDU timeout soft/hard reset alternation, and malformed connectivity transaction TLVs.
