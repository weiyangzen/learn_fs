# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.h

## Purpose
`fbnic_rpc.h` defines the shadow TCAM model and public RPC/RSS/filtering interfaces used by FBNIC netdev, firmware recovery, and receive classification code.

## Important APIs, Types, And Functions
Key types are `struct fbnic_mac_addr`, `struct fbnic_ip_addr`, and `struct fbnic_act_tcam`, each carrying value/mask data, state, and action ownership or destination data. The header defines TCAM states (`DISABLED`, `VALID`, `ADD/UPDATE`, `DELETE`), table dimensions, MACDA index layout, action table offsets reserved for BMC/NFC/RSS, RSS enable indexes, hash option indexes, action TCAM field masks, and prototypes for all RSS, BMC, MAC, IP, and rule writer helpers.

## Control Flow
The header documents the intended state progression: disabled to add to valid, valid to update/add back to valid, and valid to delete to disabled. Inline wrappers `__fbnic_uc_unsync()` and `__fbnic_mc_unsync()` call the generic MAC owner-bit removal helper with host owner indexes.

## State And Persistence
Shadow state represented by these structs lives inside `struct fbnic_dev` and mirrors hardware TCAM entries. Bitmaps in MAC/IP entries link address entries to action TCAM owners. `rss_en_mask` and `dest` in action entries become hardware action-table words.

## Dependencies And Integration Points
It includes IPv6 UAPI and bitfield helpers, forward declares `fbnic_dev`/`fbnic_net`, and is included by netdev and RPC implementation. Netdev RX mode code depends on the MACDA index constants; RSS and timestamp code depends on hash option and action table constants.

## Risks
The numeric layout is part of the hardware/software contract. Changing offsets or reserved entries can break BMC traffic isolation, RSS rule allocation, and promisc/allmulti behavior. The state values intentionally use bit-compatible update/delete checks; arbitrary enum changes would break writer tests like `state & FBNIC_TCAM_S_UPDATE`.

## Test Signals
Build and sparse coverage should catch struct/prototype drift. Runtime signals include expected TCAM state transitions, correct reservation of BMC/broadcast/promisc entries, RSS action count matching table reservations, and no overflow of MACDA/action/IP TCAM dimensions.
