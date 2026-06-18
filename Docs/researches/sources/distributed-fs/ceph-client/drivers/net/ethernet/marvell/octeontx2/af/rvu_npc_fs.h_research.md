# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_npc_fs.h

Purpose: defines flow-steering helper constants and declares the cross-file functions used to populate MCAM entries from parsed flow fields. It is the narrow interface between the flow-steering implementation, core NPC setup, hash support, and CN20K-specific code.

Important APIs and constants: `IPV6_WORDS` defines the four 32-bit words used when converting IPv6 addresses. `NPC_BYTESM`, `NPC_HDR_OFFSET`, `NPC_KEY_OFFSET`, and `NPC_LDATA_EN` describe fields in legacy KEX LDATA configuration words, while `NPC_KEY_OFFSET` and related masks are consumed by scanner and hash code. `npc_update_entry()` inserts a value/mask for one `enum key_fields` item into an MCAM metadata container. `npc_update_flow()` translates a full `flow_msg` packet/mask pair into MCAM keywords and stored rule packet/mask copies. `npc_populate_mcam_mdata()` points a generic metadata wrapper at either a normal `struct mcam_entry` or a `struct cn20k_mcam_entry`.

Control flow role: callers allocate or receive the correct entry object, call `npc_populate_mcam_mdata()` to bind keyword/action pointers, then call `npc_update_flow()` and lower-level action helpers before writing the entry to hardware. `npc_update_entry()` is also used by exact-match drop-rule installation and DMAC update paths when only one field needs changing.

State and persistence: no state is declared here. The APIs mutate caller-owned MCAM entry buffers and, through those buffers, the eventual hardware MCAM state. They also copy packet/mask fields into `struct rvu_npc_mcam_rule` objects passed as output.

Dependencies and integration: depends on `struct rvu`, `enum key_fields`, `struct mcam_entry_mdata`, `struct flow_msg`, `struct rvu_npc_mcam_rule`, `struct cn20k_mcam_entry`, and `struct mcam_entry` from the surrounding RVU/NPC headers. It is included by `rvu_npc_fs.c`, `rvu_npc_hash.c`, and CN20K support where generic field insertion is needed.

Risks: the bit masks in this header encode the hardware register layout for non-CN20K extractor config; using them for CN20K without the CN20K-specific masks would produce wrong byte lengths. The function contracts assume `mcam->rx_key_fields`/`tx_key_fields` were already populated by `npc_flow_steering_init()`. Calling `npc_update_entry()` before profile scanning will result in no field writes.

Test signals: compile tests should catch signature drift across common and CN20K implementations. Runtime signals are successful flow installation for both normal and CN20K entry formats, correct IPv6 field conversion, and exact-match drop rules that match the intended channel/LXMB/exact-result bits.
