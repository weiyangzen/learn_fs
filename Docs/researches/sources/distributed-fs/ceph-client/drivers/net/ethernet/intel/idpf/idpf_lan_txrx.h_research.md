# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_lan_txrx.h

## Purpose
`idpf_lan_txrx.h` defines the LAN transmit descriptor formats, descriptor bit fields, completion descriptor fields, context descriptor formats, and default RSS hash capability masks used by IDPF TX/RX datapath code. It is a hardware contract header rather than executable logic.

## Important APIs, types, and functions
- RSS definitions: `enum idpf_rss_hash`, `IDPF_DEFAULT_RSS_HASH`, and `IDPF_DEFAULT_RSS_HASH_EXPANDED`.
- Split queue TX completion fields: `IDPF_TXD_COMPLQ_*` masks and `struct idpf_splitq_4b_tx_compl_desc` / `struct idpf_splitq_tx_compl_desc`.
- Base TX descriptor fields: `struct idpf_base_tx_desc`, `struct idpf_base_tx_ctx_desc`, `enum idpf_tx_desc_dtype_value`, `enum idpf_tx_ctx_desc_cmd_bits`, `enum idpf_tx_desc_len_fields`, and `enum idpf_tx_base_desc_cmd_bits`.
- Tunnel/TSO/checksum fields: `IDPF_TXD_CTX_QW0_TUNN_*`, `IDPF_TXD_CTX_QW1_*`, `IDPF_TXD_QW1_*`.
- Flex descriptor support: `struct idpf_flex_tx_desc`, `struct idpf_flex_tx_sched_desc`, `struct idpf_flex_tx_tso_ctx_qw`, `union idpf_flex_tx_ctx_desc`, and flex command masks.

## Control flow
This header has no functions. TX datapath code builds descriptor quadwords by combining these masks with `FIELD_PREP()` and CPU-to-little-endian conversions, then hardware consumes descriptors from DMA rings. Completion code interprets completion descriptor fields and descriptor done values defined here.

## State and persistence behavior
The structures map DMA memory shared between CPU and NIC hardware. State is encoded in descriptor rings: buffer DMA addresses, command bits, header offsets, payload sizes, L2 tags, TSO length/MSS, tunnel metadata, completion type, queue ID, generation bit, and optional timestamp fields. The definitions themselves are stateless, but any layout change changes the DMA ABI.

## Dependencies and integration points
The header depends on `linux/bits.h` and standard endian types. It is consumed by single queue TX in `idpf_singleq_txrx.c`, split queue TX/RX files elsewhere in the IDPF driver, RSS configuration code, and feature validation in `idpf_lib.c`. It also complements virtchnl2 RX descriptor definitions included through other headers.

## Risks and edge cases
- Descriptor layout must exactly match hardware. Wrong bit positions for command, dtype, TSO, tunnel, or length fields can cause packet corruption, checksum failures, hangs, or dropped completions.
- Comments note reserved dtype and completion values; using reserved encodings may work on one device and fail on another.
- The `IDPF_TX_CTX_MSS_M` definition uses `GENMASK_ULL(50, 63)`, which is visually reversed from common high/low order and should be verified against macro behavior and usage.
- RSS hash masks must align with control-plane advertised capabilities or default RSS programming may request unsupported hashes.

## Test signals
Signals include successful TX with checksum offload, TSO, UDP tunnel, GRE tunnel, VLAN tag insertion, split queue completions, TX timestamps carried in flex flow descriptors, RSS default hash programming, descriptor ring dumps compared with expected bitfields, and hardware traffic tests with offloads enabled and disabled.
