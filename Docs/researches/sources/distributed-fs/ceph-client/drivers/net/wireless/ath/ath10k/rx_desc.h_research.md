# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/rx_desc.h

Purpose: Defines the packed RX descriptor ABI used by ath10k HTT receive paths to interpret hardware/firmware metadata for MPDU/MSDU boundaries, decapsulation, checksum status, PHY/PPDU status, locationing, spectral/radar-related PHY errors, and high-latency firmware RX descriptors.

Important APIs, types, and definitions: The file exports descriptor structures such as `rx_attention`, `rx_frag_info`, `rx_mpdu_start`, `rx_mpdu_end`, `rx_msdu_start`, `rx_msdu_end`, `rx_ppdu_start`, `rx_ppdu_end`, `rx_pkt_end`, `rx_location_info`, `rx_phy_ppdu_end`, `fw_rx_desc_base`, and `fw_rx_desc_hl`. Bit definitions cover attention flags, MPDU peer/sequence/encryption fields, MSDU lengths, protocol/checksum offsets, decap formats, PPDU preambles, PHY error bits, RTT/locationing fields, and firmware forward/discard/inspect flags.

Control flow, state, and persistence: This header has no executable flow and owns no mutable state. Its packed layouts are consumed by RX parsing code and therefore act as persistent hardware/firmware contracts. Versioned variants distinguish WCN3990/current layouts from v1/QCA988x/QCA6174/QCA99x0/QCA9984 layouts.

Dependencies and integration points: Depends on Linux bit macros and little-endian integer types. It integrates with HTT RX handlers, monitor/status reporting, checksum offload interpretation, PN/security handling, spectral/PHY error processing, and tracing of HTT RX descriptors.

Risks: Any field offset, packing, endian conversion, or mask/LSB error can corrupt frame delivery, checksum status, decryption error reporting, peer accounting, radiotap metadata, or crash/debug analysis. The unions require callers to select the layout that matches `ar->hw_rev`. Some comments encode hardware semantics, so maintenance mistakes can silently break firmware compatibility.

Test signals: Build all supported ath10k hardware variants, receive encrypted and plaintext frames, A-MPDU/A-MSDU boundary cases, checksum pass/fail, FCS/MIC/decrypt errors, monitor-mode metadata, spectral/PHY error reports, WCN3990 receive paths, and trace dumps of HTT RX descriptors.
