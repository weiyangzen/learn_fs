# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.c

## Purpose
`iavf_fdir.c` implements Flow Director filter validation, virtchnl add-message construction, diagnostics, duplicate detection, and adapter list management. It is shared by ethtool ntuple rules and TC u32 raw FDIR offload paths.

## Important APIs, Types, And Functions
Public functions are `iavf_validate_fdir_fltr_masks`, `iavf_fill_fdir_add_msg`, `iavf_print_fdir_fltr`, `iavf_fdir_is_dup_fltr`, `iavf_find_fdir_fltr`, `iavf_fdir_add_fltr`, and `iavf_fdir_del_fltr`. They operate on `struct iavf_fdir_fltr` from `iavf_fdir.h`.

Message construction is decomposed by protocol: `iavf_fill_fdir_eth_hdr`, IPv4/IPv6 helpers, TCP/UDP/SCTP helpers, AH/ESP helpers, `iavf_fill_fdir_l4_hdr` for L2TPv3-over-IP session ID, and UDP payload helpers for GTP-U, NAT-T-ESP, and PFCP. Constants for well-known UDP ports and flex offsets encode the subset of payload fields supported by the PF parser, such as GTP-U TEID/QFI, PFCP S field, and NAT-T ESP SPI.

## Control Flow
Validation first enforces full-or-empty masks for Ethernet type, IPv4/IPv6 addresses, TOS/traffic class, protocol, ports, SPI, and first L4 bytes. `iavf_fill_fdir_add_msg` then always emits an Ethernet protocol header and switches by `flow_type` to append IP and L4 headers. Each helper sets `VIRTCHNL_SET_PROTO_HDR_TYPE`, fills protocol header buffers from filter data, and marks selected fields with `VIRTCHNL_ADD_PROTO_HDR_FIELD_BIT`.

For UDP flex payloads, the code computes the offset relative to the UDP payload by subtracting Ethernet + IP + UDP header length. It accepts only a small set of exact offsets, rejects flex offsets before the payload, and rejects unsupported payload formats. For GTP-U, QFI selection requires seeing a PSC extension header marker before QFI extraction. For NAT-T-ESP, SPI 0 is rejected because that represents the IKE header format rather than ESP.

List management uses `adapter->fdir_fltr_lock`. `iavf_fdir_add_fltr` checks `iavf_fdir_max_reached`, inserts ethtool filters sorted by `loc` while raw TC u32 filters are not location-sorted, increments active accounting, marks the filter `ADD_REQUEST` when link is up or `INACTIVE` when down, and schedules `IAVF_FLAG_AQ_ADD_FDIR_FILTER` for live links. `iavf_fdir_del_fltr` finds by rule location or TC u32 handle, marks active filters `DEL_REQUEST`, frees inactive filters immediately, and reports busy for filters already in a transient state.

## State And Persistence Behavior
Filter state is entirely in memory on `adapter->fdir_list_head`, with active counters maintained by `iavf_inc_fdir_active_fltr` and `iavf_dec_fdir_active_fltr`. Hardware persistence is mediated through PF virtchnl messages stored in each filter's `vc_add_msg`. Filters may remain in inactive or pending states across link down/up and reset; `iavf_main.c` clears, disables, restores, or deletes them based on driver lifecycle.

## Dependencies And Integration Points
The file depends on `iavf.h`, Linux network header structs, endian helpers, `linux/bitfield.h`, virtchnl protocol header macros, and adapter locks/list heads from the main driver. It is called from `iavf_ethtool.c` for ethtool ntuple and from `iavf_main.c` TC u32 paths. Actual PF messaging is performed later by `iavf_virtchnl.c` when AQ flags are processed.

## Risks
The strict mask policy means many ethtool masks are rejected; this is intentional but easy to regress. Protocol header count increments must stay within virtchnl array capacity. Flex parsing is offset-sensitive and combines network-order fields with host-order `flex_words`, so endianness and alignment are important. `iavf_fdir_is_dup_fltr` skips raw filters and compares only flow, Ethernet, IP, and ext data, so action/queue differences do not make an ethtool rule unique. Deletion can return `-EINVAL` only when active filters exist but the requested filter does not, which affects empty-list semantics.

## Test Signals
Exercise full and partial masks for every supported flow type, UDP payload flex cases for GTP-U/PFCP/NAT-T-ESP, duplicate ethtool filters with different queues, raw TC u32 add/delete by handle, add while link is down then open, delete while add/delete is pending, max-filter exhaustion, and PF completion paths that transition from request/pending to active or freed.
