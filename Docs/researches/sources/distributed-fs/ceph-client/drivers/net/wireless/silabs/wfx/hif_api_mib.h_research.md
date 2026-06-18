# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_mib.h

Purpose: Defines WF200 MIB IDs and packed MIB payloads used to configure global and per-interface firmware behavior.

Important APIs and types: MIB IDs cover global power/multi-message settings, data filtering, ARP/NS tables, RX/beacon filters, counters/statistics, MAC address, WEP default key, RTS/slot/TX power, protection, template frames, beacon wakeup, RCPI/RSSI thresholds, block-ack policy, association mode, U-APSD, TX retry policy, PMF, keep-alive, inactivity, and beacon stats. Structures include global operational power mode, multi-message setting, ARP IPv4 table, RX filter, beacon filter table/enable, legacy and extended counters, MAC address, template frame, beacon wake period, RSSI threshold, block-ack policy, association mode, U-APSD info, retry policy, PMF policy, and keep-alive period.

Control flow and integration: `hif_tx_mib.c` wraps these structures in read/write MIB commands for station/AP setup, power management, beacon filtering, debug counters, template upload, queue policy, ARP filtering, and operational power mode after probe.

State and persistence: MIB writes configure firmware state that persists until reset, interface removal, or explicit overwrite. Counter MIB reads expose firmware-maintained statistics.

Dependencies: Depends on `hif_api_general.h`, firmware MIB numbering, packed LE layout, and HIF command read/write MIB wrappers.

Risks and test signals: Risks include MIB ID mismatch, variable-length table sizing, older firmware counter-table compatibility, byte-order conversion for signed values, and invalid bounds for wake intervals/policy indexes. Tests should cover every MIB wrapper, legacy vs extended counters, beacon filter programming, template frame size limit, RSSI threshold conversion, U-APSD bits, block-ack policy in combo mode, and ARP filter updates.

Test signals: Source read size: 346 lines, 9573 bytes.
