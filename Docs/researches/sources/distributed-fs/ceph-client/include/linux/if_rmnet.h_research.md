# `sources/distributed-fs/ceph-client/include/linux/if_rmnet.h`

Purpose: Qualcomm RMNET MAP header definitions for multiplexed mobile data packets and checksum offload metadata.

Important APIs/types/functions: packed/aligned `struct rmnet_map_header`, downlink checksum trailer, uplink checksum header, MAP v5 checksum header, flag masks for pad length, command, next header, checksum valid/requested, and `RMNET_MAP_HEADER_TYPE_CSUM_OFFLOAD`.

Control flow and state: no functions. The structures describe on-wire per-packet metadata interpreted by RMNET drivers.

Dependencies/integration: depends on kernel integer types, `GENMASK`, `BIT`, and checksum types. Used in RMNET data path encode/decode and checksum offload handling.

Risks: fields are intentionally byte-aligned and network-order; padding, mux ID, and packet length mistakes can corrupt frame parsing; checksum flags differ between uplink/downlink and v5; no helper functions enforce bounds.

Test signals: MAP packet encode/decode with padding, muxed channels, command packets, v5 next-header chains, checksum insertion/validation, and unaligned-access build coverage.
