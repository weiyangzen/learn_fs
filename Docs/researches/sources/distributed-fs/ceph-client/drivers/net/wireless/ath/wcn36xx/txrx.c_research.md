# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/txrx.c

## Purpose
`txrx.c` translates between WCN36xx firmware/DXE frame descriptors and mac80211 skbs. On RX it validates firmware buffer descriptors, reconstructs frame data, fills `ieee80211_rx_status`, updates survey data, handles chained A-MSDU fragments, and submits frames to mac80211. On TX it builds firmware TX descriptors, selects station/VIF indices, requests optional TX status, and hands frames to DXE.

## Important APIs, Types, and Functions
- `wcn36xx_rx_skb()` is the RX entry point. It endian-converts `struct wcn36xx_rx_bd`, checks descriptor offsets and lengths, extracts frame metadata, fills rate/signal/band/frequency fields, reassembles chained A-MSDUs, and calls `ieee80211_rx_irqsafe()`.
- `wcn36xx_start_tx()` is the TX entry point. It determines data vs management/control, broadcast vs unicast, ACK-status needs, fills `struct wcn36xx_tx_bd`, endian-converts it, and calls `wcn36xx_dxe_tx_frame()`.
- `wcn36xx_set_tx_data()` and `wcn36xx_set_tx_mgmt()` populate descriptor fields for data and management/control frames.
- `wcn36xx_tx_start_ampdu()` starts BA sessions after enough non-aggregated QoS frames.
- `wcn36xx_process_tx_rate()` converts firmware stats rate flags into mac80211 `rate_info`.
- `wcn36xx_rate_table` maps firmware RX rate IDs to mac80211 bitrate/MCS/encoding/bandwidth fields.

## Control Flow
RX starts with descriptor sanity checks before mutating skb length and data pointers. Scan-learn frames derive channel information from the descriptor; normal frames use current hardware channel state. Rate IDs are table-mapped when valid and defaulted otherwise. Chained A-MSDU fragments are queued in `wcn->amsdu` until the last segment, then copied into the first skb. Any malformed descriptor drops the skb and purges the chain.

TX starts by logging and initializing a zeroed descriptor. If mac80211 requested TX status, the driver stops queues because firmware supports one outstanding ACK indication, then sets `tx_comp`. Data frames get STA/DPU indices from `sta_priv` when available or from the owning VIF for non-unicast frames; management frames use self station indices. The descriptor is byte-swapped with `buff_to_be()`, stamped, and sent to DXE.

## State and Persistence Behavior
The file updates per-channel survey RSSI/SNR under `survey_lock`, adds SNR samples to kernel randomness, maintains the temporary A-MSDU skb queue, mutates per-STA AMPDU state under `ampdu_lock`, and temporarily stops/wakes mac80211 queues around firmware TX ACK indications.

## Dependencies and Integration Points
It depends on `txrx.h` descriptor definitions, `wcn36xx.h` private state, DXE transmit entry points, mac80211 RX/TX status APIs, Linux skb helpers, and channel/rate definitions. It cooperates with `smd.c` for BA session negotiation and statistics conversion.

## Risks and Test Signals
Risks include descriptor offset trust, endian conversion mistakes, A-MSDU chain leaks, NULL VIF lookup for management/non-unicast paths, queue stalls when TX ACK indication is lost, and inaccurate rate mappings for newer firmware. Test signals include RX malformed-descriptor drops without crashes, beacon/probe timestamps, scan result channels, sustained encrypted/unencrypted TX, AMPDU startup, TX-status queue recovery, and no skb leaks under chained A-MSDU traffic.
