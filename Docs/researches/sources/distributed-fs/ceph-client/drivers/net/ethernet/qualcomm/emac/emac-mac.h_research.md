# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.h

### Purpose
`emac-mac.h` defines Qualcomm EMAC MAC-layer descriptor formats, ring/queue data structures, descriptor bitfield helpers, DMA ordering enums, wrapper register offsets, and public MAC function prototypes.

### Important APIs, Types, And Functions
Key types are `emac_rrd`, `emac_tpd`, `emac_ring_header`, `emac_buffer`, `emac_rfd_ring`, `emac_rrd_ring`, `emac_rx_queue`, `emac_tpd_ring`, and `emac_tx_queue`. Macros such as `BITS_GET`, `BITS_SET`, `RRD_*`, and `TPD_*` encode/decode hardware descriptor fields. Prototypes expose MAC up/down/reset/stop, mode config, RX/TX process, transmit send, ring init/alloc/free, and multicast hash programming.

### Control Flow
The header has no executable control flow, but it defines the data model consumed by `emac-mac.c`: RFDs provide empty RX buffers, RRDs return completed RX packets, and TPDs describe TX buffers and offloads. Producer/consumer indices in queue structures map to hardware mailbox registers selected during ring initialization.

### State, Persistence, And Dependencies
Queue state persists in memory while the netdev is open and mirrors hardware descriptor state. DMA addresses are stored both in descriptors and software `emac_buffer` entries so completions can unmap and free SKBs. The header depends on Linux endian/bit macros through included kernel context and forward-declares `struct emac_adapter`.

### Integration Points
This header is shared by the EMAC core, MAC implementation, ethtool statistics/configuration, and other driver files through `emac.h`. It is the contract between software queues and the EMAC DMA engine.

### Risks
Bitfield macros must preserve little-endian descriptor layout. Descriptor sizes and index masks must match hardware register programming in `emac-mac.c`. Any change to ring structures affects allocation, NAPI processing, and TX completion assumptions.

### Test Signals
Compile with sparse/endian checks, validate descriptor encoding against hardware documentation or known packets, test wraparound of producer/consumer indices, and exercise RX/TX paths with checksum, TSO, VLAN, and DMA address high-bit cases.
