<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/onie-tlv.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/onie-tlv.c

## Purpose
Parses ONIE Type-Length-Value EEPROM/NVMEM tables and adds NVMEM cells for recognized TLV fields, including indexed MAC address handling and CRC validation.

## Important APIs, Types, And Functions
`struct onie_tlv_hdr` and `struct onie_tlv` describe the table. `onie_tlv_cell_name()` maps TLV type codes to cell names. `onie_tlv_crc_is_valid()` validates the JAMCRC field. `onie_tlv_parse_table()` reads the header and full table from the backing NVMEM device. `onie_tlv_add_cells()` creates cells with offsets into the table and optional post-processing from `onie_tlv_read_cb()`. The layout driver registers as `onie-tlv-layout`.

## Control Flow
Probe sets `layout->add_cells` and calls `nvmem_layout_register()`. Parsing reads the header, validates magic `TlvInfo` and version 1, bounds total size to 2048 bytes, reads the table, validates the trailing CRC TLV, then iterates data TLVs. Recognized TLV types become cells, with DT child nodes looked up under the layout container. MAC address cells use a post-process callback that adds the requested index.

## State And Persistence
The layout stores no persistent driver state beyond generated core cell entries. The backing ONIE table persists in the provider. The parsed table allocation is devm-managed for the layout device lifetime.

## Dependencies And Integration Points
Depends on the NVMEM layout bus, NVMEM direct reads, OF layout container lookup, CRC32, and Ethernet address helpers. It exposes standardized ONIE fields to ordinary NVMEM consumers.

## Risks
The loop continues without advancing offset for unknown cell names, which can hang on unrecognized TLV types; this is a notable correctness risk in the current code. Bounds checking uses `offset + tlv.len >= data_len`, which may reject or mishandle edge TLVs depending on intended inclusive semantics. CRC validation assumes the final TLV is type 0xfe length 4.

## Test Signals
Parse valid ONIE tables, invalid magic/version, oversized length, bad CRC, missing CRC TLV, unknown TLV types, edge-length TLVs, MAC address indexed consumers, and DT child-node association. A regression test should specifically cover unknown TLVs to detect infinite-loop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/onie-tlv.c -->
