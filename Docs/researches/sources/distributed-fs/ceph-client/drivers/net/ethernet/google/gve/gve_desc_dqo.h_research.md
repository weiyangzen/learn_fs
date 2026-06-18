# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_desc_dqo.h

## Purpose

`gve_desc_dqo.h` defines the DQO descriptor ABI for TX packets/context descriptors, TX completions, RX buffer descriptors, and RX completion descriptors. DQO uses little-endian bitfields and generation bits rather than the legacy GQI RX sequence model.

## Important APIs, types, and constants

- `struct gve_tx_pkt_desc_dqo`: 16-byte DQO packet descriptor with buffer address, dtype, end-of-packet, checksum-offload, report-event, completion tag, and buffer size.
- `GVE_TX_MAX_HDR_SIZE_DQO`, `GVE_TX_MIN_TSO_MSS_DQO`, `GVE_TX_MAX_DATA_DESCS`, `GVE_TX_MIN_RE_INTERVAL`: constraints enforced by DQO TX code.
- `struct gve_tx_tso_context_desc_dqo` and `struct gve_tx_general_context_desc_dqo`: context descriptors for TSO and metadata.
- `struct gve_tx_metadata_dqo`: packed metadata version, path hash, and rehash flag inserted into context descriptor flex fields.
- `struct gve_tx_compl_desc`: 8-byte TX completion with queue id, completion type, generation bit, and either head pointer or packet completion tag.
- `GVE_COMPL_TYPE_DQO_*` and `GVE_ALT_MISS_COMPL_BIT`: completion-class constants used by DQO TX completion handling.
- `struct gve_rx_desc_dqo`: RX buffer-queue descriptor with `buf_id`, packet buffer DMA address, and optional header buffer DMA address.
- `struct gve_rx_compl_desc_dqo`: RX completion descriptor with packet type, checksum status, packet/header lengths, split-header/RSC flags, buffer id, hash, timestamp, and generation bit.
- `GVE_RX_BUF_THRESH_DQO`: posting threshold used to limit RX doorbell frequency.

## Control flow and state

The header itself is declarative. DQO RX posts `gve_rx_desc_dqo` entries through the buffer queue, then consumes `gve_rx_compl_desc_dqo` entries until the generation bit indicates no new work. DQO TX writes packet/context descriptors, tracks pending packets by completion tag, and consumes `gve_tx_compl_desc` records.

## Dependencies and integration points

The file deliberately errors out if `__LITTLE_ENDIAN_BITFIELD` is not set. `gve_dqo.h`, `gve_rx_dqo.c`, and DQO TX code use these definitions. `gve_rx_dqo.c` relies on packet type indexes into the ptype LUT obtained by adminq, checksum flags, RSC fields, and timestamp fields. `gve_buffer_mgmt_dqo.c` fills RX buffer descriptors.

## Risks and test signals

Risks include compiler bitfield layout assumptions, firmware ABI drift, generation-bit wrap bugs, missing DMA barriers before reading completions, and incomplete handling of error/status bits. Test signals include static descriptor size assertions, DQO RX/TX wraparound, checksum/RSS/RSC validation, header-split overflow, timestamp validity, and DQO completion-type handling.
