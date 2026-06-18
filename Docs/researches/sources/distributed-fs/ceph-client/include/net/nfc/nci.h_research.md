# sources/distributed-fs/ceph-client/include/net/nfc/nci.h

Purpose: defines NCI wire constants, header manipulation macros, opcodes, command/response/notification layouts, and RF/NFCEE protocol structures for NFC Controller Interface packets.

Important APIs and types: constants cover statuses, RF tech/modes, bit rates, protocols, interfaces, config tags, reset/deactivate types, GIDs, SPI headroom, and packet sizes. Header structs `nci_ctrl_hdr` and `nci_data_hdr` plus macros `nci_mt()`, `nci_pbf()`, `nci_opcode_*()`, and `nci_conn_id()` parse/construct packet headers. Packed structs describe core reset/init/config/connection commands, RF discovery/map/select/deactivate commands, NFCEE management, reset/init/config responses, credit/error notifications, RF discovery/activation/deactivation notifications, and NFCEE discovery TLVs.

Control flow: NCI core builds command payloads with these layouts, parses controller responses/notifications by opcode, and translates RF discovery/activation data into generic NFC targets and connection state.

State and persistence: this header stores no state; it specifies transient on-wire packet formats.

Dependencies and integration points: depends on NFC core size constants and is consumed by `nci_core.h` and transport drivers.

Risks and test signals: risks are packed-layout drift, variable-length array bounds, NCI 1.x/2.x parsing differences, endian mistakes, and duplicate opcode definitions. Test controller init/reset, RF discovery for A/B/F/V, activation params, NFCEE discovery, credits, malformed lengths, and NCI v2 init responses.
