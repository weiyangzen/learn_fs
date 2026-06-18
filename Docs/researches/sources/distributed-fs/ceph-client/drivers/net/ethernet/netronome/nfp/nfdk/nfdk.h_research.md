# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfdk/nfdk.h

## Purpose
Defines the NFDK TX descriptor format, NFDK ring sizing constants, software TX buffer representation, and public NFDK datapath entry points used by common NFP netdev code.

## Important APIs, Types, and Functions
- Descriptor constants define TX descriptor block size, stop thresholds, maximum data per head/descriptor/block, gather limit, descriptor type values, EOP bit, checksum/encap flags, and metadata layout fields.
- `struct nfp_nfdk_tx_desc` overlays DMA, TSO, metadata, raw, and word-level descriptor interpretations.
- `struct nfp_nfdk_tx_buf` stores software state associated with TX descriptors: SKB, fragment pointer, DMA address, XDP pointer tags, and TSO packet/real-length accounting.
- `nfp_nfdk_headlen_to_segs()` converts a linear head length into required NFDK descriptors, accounting for the smaller first-descriptor head data field.
- Declares `nfp_nfdk_poll()`, `nfp_nfdk_tx()`, `nfp_nfdk_ctrl_tx_one()`, `nfp_nfdk_ctrl_poll()`, and `nfp_nfdk_rx_ring_fill_freelist()`.

## Control Flow
This header has no runtime flow, but its constants encode the constraints enforced by `dp.c` and `rings.c`: TX rings use twice the nominal packet descriptor count, each simple packet reserves data plus metadata descriptors, and packets may need padding to the next descriptor block.

## State and Persistence Behavior
The header defines in-memory structures shared between driver and firmware DMA rings. The lower bits of `nfp_nfdk_tx_buf.val` are used as driver-only tags for XDP buffer provenance and must be stripped before hardware sees DMA addresses.

## Dependencies and Integration Points
Included by NFDK datapath and ring setup files. It depends on Linux bitops/types and forward declarations from `nfp_net.h`. Its IPsec declaration is conditional on `CONFIG_NFP_NET_IPSEC`.

## Risks
Any mismatch with firmware descriptor ABI breaks TX/RX. The bitfield constants are tightly coupled with `FIELD_PREP()` use in `dp.c`. Pointer tagging assumes alignment leaves low bits free; changes to allocation alignment or architecture assumptions could invalidate XDP recycling.

## Test Signals
Compile-time coverage should catch struct references, but ABI correctness needs runtime TX descriptor inspection, firmware compatibility testing across NFDK ABI versions, TSO/gather boundary tests, and XDP_TX recycling tests.
