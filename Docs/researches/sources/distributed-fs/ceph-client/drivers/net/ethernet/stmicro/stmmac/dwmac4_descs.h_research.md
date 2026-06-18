<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.h

## Purpose
Defines DWMAC4 descriptor bit fields for transmit and receive read/write-back formats, context descriptors, VLAN, TSO, timestamps, ownership, and extended launch-time fields.

## Important APIs, Types, And Functions
Macros cover `TDES2/TDES3` buffer sizes, checksum insertion, TSO payload/header fields, context type, timestamp status, ownership, VLAN insertion, `TDES4/TDES5` launch time, and `RDES0..RDES3` RX status/filter/timestamp/error fields. It declares `dwmac4_ring_mode_ops` and `dwmac4_desc_ops`.

## Control Flow
The header has no executable flow. The descriptor ops use these masks to fill descriptors before DMA ownership and parse write-back descriptors after DMA completion.

## State And Persistence
No state is stored. It defines the memory ABI of descriptor rings shared between CPU and DMA, which persists until descriptors are recycled.

## Dependencies And Integration Points
Includes Linux bitops and is consumed by `dwmac4_descs.c` and STMMAC descriptor handling. It underpins checksum, VLAN, PTP, TSO, split-header, secondary buffer, and time-based scheduling features.

## Risks
Read and write-back formats reuse descriptor words with different meanings; using the wrong mask in the wrong phase corrupts behavior. Context descriptor bits overlap normal descriptor bits. Endianness conversion must be done by users.

## Test Signals
Descriptor ring unit/traffic tests for TSO, checksum offload, VLAN insertion/extraction, timestamping, RX filter stats, error stats, and TBS indirectly verify these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac4_descs.h -->
