# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/norm_desc.c

Purpose: Implements normal descriptor operations for older non-enhanced GMAC descriptor formats.

Important APIs and flow: Exported `ndesc_ops` supplies descriptor status, initialization, release, TX preparation, ownership handoff, interrupt-on-completion, frame length, timestamp, display, address, and clear callbacks. TX status reports DMA ownership, non-last-segment status, and error summary counters. RX status reports ownership, last descriptor, error summary counters, dribbling, length, MII, CRC, overflow, and checksum errors.

Control flow and state: The code manipulates little-endian DMA descriptors shared with hardware. RX initialization sets OWN, buffer size, ring/chain markers, and optional interrupt disable. TX cleanup preserves ring end markers before clearing reusable fields. TX preparation updates first/last flags, checksum insertion, length fields using ring/chain helpers, and optionally sets OWN.

Dependencies and integration: Depends on `common.h` and `descs_com.h`. `hwif.c` selects this table for GMAC devices without enhanced descriptors; generic TX/RX paths invoke it through `hwif.h` wrappers.

Risks and test signals: Normal descriptors have less metadata, so common code must not assume enhanced-only callbacks. Test old MAC100/GMAC paths, ring and chain modes, checksum offload type-1 length adjustment, corrupted timestamp sentinel handling, VLAN status under `STMMAC_VLAN_TAG_USED`, and descriptor release marker preservation.
