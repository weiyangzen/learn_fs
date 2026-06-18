# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htt.c

Purpose: implements HTT initialization, firmware-version negotiation, HTC service connection, firmware-specific T2H message mapping, and chip-specific RX descriptor ops. It bridges HTC transport with the fuller HTT TX/RX implementations in `htt_tx.c` and `htt_rx.c`.

Important APIs/types/functions: exported RX descriptor ops are `qca988x_rx_desc_ops`, `qca99x0_rx_desc_ops`, and `wcn3990_rx_desc_ops`. Exported functions are `ath10k_htt_connect`, `ath10k_htt_init`, and `ath10k_htt_setup`. Static T2H arrays translate MAIN, 10.x, TLV, and 10.4 firmware message IDs to common `enum htt_t2h_msg_type`.

Control flow: `ath10k_htt_init` selects T2H mapping from firmware metadata, sets prefetch length, and installs TX/RX ops. `ath10k_htt_connect` connects `ATH10K_HTC_SVC_ID_HTT_DATA_MSG` over HTC, records endpoint ID, enables HL bundling when needed, and handles HIF TX-completion behavior. `ath10k_htt_setup` sends a version request, waits for response, verifies major version 2 or 3, then configures fragment descriptor banks, RX rings, and aggregation limits.

State and persistence: runtime state is in `struct ath10k_htt`: endpoint, version completion/fields, message maps, ops, prefetch length, and setup configuration. Descriptor ops are const tables selected via hardware parameters. No persistence exists.

Dependencies/integration: depends on `htt.h`, `core.h`, `hif.h`, HTC service connection, `htt_tx.c` H2T config messages, `htt_rx.c` response handling, and `rx_desc.h` layouts.

Risks: wrong firmware op version breaks T2H decode; unset firmware metadata fails init; missing version response times out setup; unsupported major versions are rejected; wrong RX descriptor ops can corrupt RX parsing or destabilize firmware.

Test signals: boot every firmware op version, verify T2H dispatch, inject setup/version failures, test frag/RX-ring/aggr config errors, and validate v1/v2 descriptor offsets and QCA99x0/WCN3990 accessors.
