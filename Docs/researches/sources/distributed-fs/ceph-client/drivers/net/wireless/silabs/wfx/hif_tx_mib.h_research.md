# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.h

Purpose: Declares high-level MIB helper APIs used by station, scan, debug, data TX policy, and probe code.

Important APIs and types: Exports setters/getters for output power, beacon wake period, RSSI threshold, counters, MAC address, RX/beacon filters, operational power mode, template frame, PMF, block-ack policy, association mode, TX retry policy, keep-alive, ARP IPv4 filters, multi-TX confirmations, U-APSD, ERP protection, slot time, WEP default key, and RTS threshold.

Control flow and integration: These helpers abstract `wfx_hif_read_mib()`/`wfx_hif_write_mib()` so mac80211 callbacks can update firmware with typed arguments.

State and persistence: No state is declared; firmware MIB state is persistent after writes.

Dependencies: Depends on `hif_api_mib.h`, SKBs for template upload, and `struct wfx_vif`/`wfx_dev`.

Risks and test signals: Build tests should keep prototypes synchronized with implementation; runtime tests should validate the mac80211 callbacks call the correct helper for each changed flag.

Test signals: Source read size: 48 lines, 2300 bytes.
