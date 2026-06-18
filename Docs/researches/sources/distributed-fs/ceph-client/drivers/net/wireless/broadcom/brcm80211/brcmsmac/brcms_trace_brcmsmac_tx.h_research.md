# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/brcms_trace_brcmsmac_tx.h

Purpose: defines TX-focused tracepoints for D11 descriptors, TX status words, and A-MPDU session summaries.

Important APIs and tracepoints: `brcms_txdesc` captures device name and a dynamic byte array copy of the TX descriptor. `brcms_txstatus` records frame length, frame ID, status, last TX time, sequence, PHY error, and ACK PHY RX status. `brcms_ampdu_session` records aggregate limits and current aggregate length/frame/DMA counts.

Control flow: A-MPDU and TX status code call these trace helpers while processing descriptors and completions. Tracepoint definitions are generated only under `CONFIG_BRCM_TRACING`; otherwise inline stubs are used.

State and persistence: no owned state. Trace records copy descriptor/status data at event time.

Dependencies and integration: depends on Linux tracepoints and brcmsmac TX paths. The dynamic descriptor array avoids depending on a single printable descriptor format.

Risks and test signals: large descriptor capture can increase trace overhead. Consumers need matching kernel trace format. Test with tracing enabled during TX traffic and A-MPDU aggregation, and verify disabled tracing compiles to stubs.
