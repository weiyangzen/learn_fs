# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-utils.c

Purpose: Implements miscellaneous iwlwifi helpers for TSO segmentation into A-MSDU-oriented MPDUs and averaging negative dBm measurements in linear space.

Important APIs and functions: `iwl_tx_tso_segment()` is built under `CONFIG_INET` and exports segmented SKBs into a caller-provided queue. `iwl_average_neg_dbm()` exports signal/noise averaging for unsigned negative dBm inputs. Static `iwl_div_by_db()` scales fixed-point factors by decibel deltas.

Control flow: TSO segmentation temporarily changes `gso_size` to aggregate multiple subframes, calls `skb_gso_segment()`, restores GSO metadata, consumes the original skb when segmentation returns a list, copies skb control blocks into each segment, adjusts IPv4 IDs, clears A-MSDU-present QoS bit for non-GSO tail segments, and appends MPDUs. dBm averaging skips invalid `0xff` entries, maintains a common dBm magnitude and 16.16 factor sum, divides by count, then normalizes back to a signed dBm value.

State and persistence: Mutates SKB metadata, QoS control bits, IPv4 header checksums, and the output skb queue. The averaging helper is stateless.

Dependencies and integration points: Uses Linux GSO/IP/TCP/skbuff APIs, ieee80211 header helpers, and exported iwlwifi symbol macros. Called by TX paths that build A-MSDU/TSO frames and by telemetry/noise code.

Risks: Incorrect restoration of GSO fields or skb control block copying can break later TX processing. IPv4 ID sequencing depends on `num_subframes`. QoS A-MSDU bit handling assumes an IEEE80211 data QoS header. Fixed-point dBm math trades precision for bounded integer operations.

Test signals: IPv4/IPv6 TSO segmentation, memory failure from `skb_gso_segment()`, single-tail non-GSO segment QoS bit clearing, checksum after IPv4 ID change, skb queue ownership, all-invalid dBm input, and mixed dBm averages against floating-point references.
