<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/main.c

Purpose: Provides shared ath module metadata and common utility functions for RX buffer allocation, beacon ownership checks, logging, and bus type names.

Important APIs/types/functions: Exports `ath_rxbuf_alloc()`, `ath_is_mybeacon()`, `ath_printk()`, and `ath_bus_type_strings`.

Control flow: RX buffer allocation reserves cacheline alignment slack and adjusts skb data alignment. Beacon matching checks frame type, nonzero current BSSID, and address equality. `ath_printk()` formats logs either with wiphy name and tracepoint emission or as generic ath logs when no wiphy is available.

State and persistence: Stateless except for allocated skbs returned to callers and exported static bus string table.

Dependencies and integration points: Depends on mac80211 skb/header helpers, `ath_common`, and `trace_ath_log()` from `trace.h`.

Risks and test signals: Risks include oversized allocations on systems that round skb allocation size up and missing wiphy context in logs. Test signals are RX path buffer alignment, beacon filtering in station power-save paths, and trace/log output coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/main.c -->
