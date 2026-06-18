# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwxgmac2_descs.c

Purpose: Provides the XGMAC2 descriptor callback table used by the generic stmmac TX/RX paths. It understands XGMAC normal descriptors plus extended descriptor fields for TBS, VLAN insertion, RSS hash reporting, split-header metadata, timestamps, and context descriptors.

Important APIs and flow: Exported `dwxgmac210_desc_ops` implements descriptor initialization, ownership handoff, TX/RX status, TX/TSO preparation, interrupt-on-completion, MSS context descriptors, address programming, VLAN context descriptors, source-address insertion, RSS hash extraction, RX header length extraction, secondary buffer address programming, and TBS launch time fields.

Control flow and state: Descriptor state persists in little-endian DMA descriptors shared with hardware. TX preparation fills buffer lengths, first/last flags, checksum insertion, TSO fields, and sets OWN last after a `dma_wmb()` on first descriptors to avoid hardware seeing a partial frame. RX status checks OWN, context descriptors, last descriptor, and error summary. RX timestamps are valid only when a context descriptor follows and timestamp bits are sane.

Dependencies and integration: Depends on XGMAC descriptor masks from `dwxgmac2.h`, generic status enums from `common.h`, and is selected for XGMAC/XLGMAC by `hwif.c`. Callers reach it through `stmmac_desc_ops` wrappers in `hwif.h`.

Risks and test signals: Ownership ordering, endian conversion, and context descriptor reuse are critical. Test TX cleanup and DMA ownership races, multi-fragment and TSO packets, VLAN outer/inner insertion, RSS hash type reporting for TCP/UDP IPv4/IPv6, RX timestamp context descriptor validation, TBS descriptors, and error/discard behavior.
