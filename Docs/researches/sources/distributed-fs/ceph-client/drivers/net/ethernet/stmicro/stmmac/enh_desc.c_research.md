# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/enh_desc.c

Purpose: Implements enhanced/alternate descriptor operations for older GMAC cores. These descriptors support richer TX/RX error reporting, checksum-offload status, PTP extended status, timestamp extraction, and ring/chain layout helpers.

Important APIs and flow: Exported `enh_desc_ops` provides status, init, release, prepare, ownership, IOC, frame length, extended RX status, timestamp, display, address, and clear callbacks. TX status decodes last-segment errors and may flush the TX FIFO. RX status validates ownership and last descriptor, updates detailed error counters, and maps checksum-offload status to stack-visible frame results.

Control flow and state: Descriptor fields are little-endian shared DMA state. Initialization marks RX descriptors owned and sets buffer sizes for chain or ring mode. Release preserves ring end markers. TX preparation writes length, first/last flags, checksum mode, and uses `dma_wmb()` before giving the first descriptor to hardware. Extended status updates PTP message, IP checksum, AV, VLAN priority, and L3/L4 match counters.

Dependencies and integration: Depends on `common.h` status enums and `descs_com.h` ring/chain bit helpers. `hwif.c` chooses it for GMAC devices using enhanced descriptors, with extended descriptors enabled only on sufficiently new Synopsys IDs.

Risks and test signals: Error accounting and descriptor marker preservation are easy to regress. Test enhanced ring and chain modes, checksum status variants, timestamp with and without extended descriptors, FIFO flush on underflow/frame-flush, VLAN status, and TX/RX descriptor reuse after cleanup.
