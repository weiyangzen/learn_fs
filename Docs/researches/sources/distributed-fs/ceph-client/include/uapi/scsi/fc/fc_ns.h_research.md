# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_ns.h

## Purpose
`fc_ns.h` defines Fibre Channel directory/name service request codes and payload structures used inside FC-CT transactions. It supports querying and registering N_Port IDs, WWPN/WWNN values, symbolic names, FC-4 type bitmaps, port type, and FC-4 feature data.

## Important APIs, Types, and Constants
`FC_NS_SUBTYPE` selects the name server common-transport subtype. `enum fc_ns_req` defines name-service commands such as `FC_NS_GA_NXT`, `FC_NS_GPN_ID`, `FC_NS_GNN_ID`, `FC_NS_GID_PN`, `FC_NS_GID_FT`, `FC_NS_GPN_FT`, `FC_NS_RPN_ID`, `FC_NS_RNN_ID`, `FC_NS_RFT_ID`, `FC_NS_RSPN_ID`, `FC_NS_RFF_ID`, and `FC_NS_RSNN_NN`.

`enum fc_ns_pt` describes port types. Object structures include `struct fc_ns_pt_obj`, `struct fc_ns_fid`, `struct fc_ns_fts`, and `struct fc_ns_ff`. Request/response payloads include `struct fc_ns_gid_pt`, `struct fc_ns_gid_ft`, `struct fc_gpn_ft_resp`, `struct fc_ns_gid_pn`, `struct fc_gid_pn_resp`, `struct fc_gspn_resp`, `struct fc_ns_rft_id`, `struct fc_ns_rn_id`, `struct fc_ns_rsnn`, `struct fc_ns_rspn`, and `struct fc_ns_rff_id`.

## Control Flow and State
There is no executable flow in the header. Name-service flow is CT-based: a driver builds `fc_ct_hdr` with directory service type and `FC_NS_SUBTYPE`, places one of these request payloads after it, and parses a response containing IDs, names, bitmaps, or a generic CT accept/reject. Registration commands update the fabric name server; query commands discover remote ports and capabilities.

## State and Persistence Behavior
The header models fabric directory state: port IDs, WWPN/WWNN registration, symbolic names, FC-4 type support, and FC-4 feature bits. Persistence is external in the fabric name server and in driver discovery caches. Variable-length symbolic-name responses are serialized tails and must be length-bound by the CT payload.

## Dependencies and Integration Points
It includes `<linux/types.h>` and integrates with `fc_gs.h` common transport, `fc_fs.h` FC frame types, SCSI FC transport discovery, FCoE/libfc, and management tools that inspect or register fabric identity.

## Risks and Test Signals
Risks are bitmap size/bit-order mistakes (`FC_NS_TYPES`, `FC_NS_BPW`), 24-bit FC_ID byte ordering, missing packed layout on variable-name structures, and treating `FC_NS_FID_LAST` incorrectly when iterating multi-object responses. Tests should include name-service payload round trips, GID_FT/GPN_FT multi-entry parsing with final-entry flags, and registration payload size checks.
