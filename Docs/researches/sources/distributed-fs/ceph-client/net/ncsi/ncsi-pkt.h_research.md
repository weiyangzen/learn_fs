# sources/distributed-fs/ceph-client/net/ncsi/ncsi-pkt.h

## Purpose
This header defines the wire-format packet structures and constants for NCSI commands, responses, OEM payloads, statistics, MAC address retrieval, and asynchronous event notifications.

## APIs, Types, and Functions
Common packet headers are `ncsi_pkt_hdr`, `ncsi_cmd_pkt_hdr`, `ncsi_rsp_pkt_hdr`, and `ncsi_aen_pkt_hdr`. Command structs cover default commands plus SP, DC, RC, AE, SL, SVF, EV, SMA, EBF, EGMF, SNFC, and OEM. Response structs cover OEM vendor layouts, GLS, GVI, GC, GP, GCPS, GNS, GNPTS, GPS, GPUUID, GMCMA, and AEN packet forms for LSC, CR, and HNCDSC. Constants define packet revision, command opcodes, response opcodes, response code/reason values, and AEN types.

## Control Flow
There is no executable control flow. `ncsi-cmd.c` writes these layouts into skbs, `ncsi-rsp.c` casts received skbs to these layouts and extracts fields, and `ncsi-aen.c` validates and consumes AEN layouts.

## State and Persistence
The structures describe transient on-wire data. Values decoded from them persist in `ncsi_channel` capabilities, modes, filters, statistics, package UUIDs, pending MAC address, and management state.

## Dependencies and Integration
The header depends on kernel fixed-width endian types and Ethernet address length. It must match DMTF NCSI packet layout, including padding, checksum positions, payload lengths, and packed/aligned statistics fields.

## Risks
Incorrect structure layout, missing packing where required, or wrong payload length constants can corrupt command generation or response parsing. Flexible array OEM and GMCMA payloads require callers to validate lengths before accessing variable data. Endianness conversions are handled by consumers, so fields must be declared with the correct endian type.

## Test Signals
Packet encode/decode tests should verify sizeof/offset expectations, command/response opcode correspondence, checksum placement, statistics layout, OEM response offsets, and AEN payload sizes.
