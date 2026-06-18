# sources/distributed-fs/ceph-client/include/uapi/scsi/fc/fc_els.h

## Purpose
`fc_els.h` defines Fibre Channel Extended Link Services payload formats and command identifiers for login, logout, discovery, state-change, diagnostic, and fabric-performance notification exchanges. It is a userspace-visible protocol layout header shared by libfc, FC transport drivers, diagnostic tooling, and BSG users that need to build or decode ELS frame payloads. It complements `fc_fs.h` frame header/type definitions and uses big-endian network-order scalar fields for wire compatibility.

## Important APIs, Types, and Constants
The central command namespace is `enum fc_els_cmd`, with `FC_ELS_CMDS_INIT` for decoder name tables. It covers core link service commands such as `ELS_LS_RJT`, `ELS_LS_ACC`, `ELS_PLOGI`, `ELS_FLOGI`, `ELS_LOGO`, `ELS_PRLI`, `ELS_PRLO`, `ELS_SCR`, `ELS_RSCN`, `ELS_RNID`, and newer diagnostic commands including `ELS_FPIN`, `ELS_EDC`, and `ELS_RDF`.

Reject handling is represented by `struct fc_els_ls_rjt`, `enum fc_els_rjt_reason`, and `enum fc_els_rjt_explan`. The accept case uses `struct fc_els_ls_acc`. Login negotiation uses `struct fc_els_csp`, `struct fc_els_cssp`, and `struct fc_els_flogi`, with feature bits such as `FC_SP_FT_NPIV`, `FC_SP_FT_FPORT`, `FC_SP_FT_EDTR`, and payload-size bounds inherited from `FC_MIN_MAX_PAYLOAD`/`FC_MAX_PAYLOAD`.

Process login and recovery payloads are represented by `struct fc_els_spp`, `struct fc_els_prli`, `struct fc_els_prlo`, `struct fc_els_rrq`, `struct fc_els_rec`, and `struct fc_els_rec_acc`. Discovery and topology/status payloads include `struct fc_els_adisc`, `struct fc_els_scr`, `struct fc_els_rscn`, `struct fc_els_rscn_page`, `struct fc_els_rnid*`, `struct fc_els_rpl*`, `struct fc_els_rps*`, `struct fc_els_lesb`, `struct fc_els_rls*`, `struct fc_els_rlir`, `struct fc_els_clir`, and `struct fc_els_clid`.

Diagnostic and FPIN support is built around `struct fc_tlv_desc`, tag enum `fc_ls_tlv_dtag`, `fc_tlv_next_desc()`, descriptor size helpers, `struct fc_els_fpin`, `struct fc_fn_li_desc`, `struct fc_fn_deli_desc`, `struct fc_fn_peer_congn_desc`, `struct fc_fn_congn_desc`, `struct fc_df_desc_fpin_reg`, `struct fc_els_rdf`, `struct fc_els_rdf_resp`, `struct fc_diag_lnkflt_desc`, `struct fc_diag_cg_sig_desc`, `struct fc_els_edc`, and `struct fc_els_edc_resp`. Flexible arrays and `_Static_assert()` checks preserve ABI offsets for variable descriptor lists.

## Control Flow and State
This header has no executable kernel flow except the inline `fc_tlv_next_desc()` helper, which advances through a received TLV list by converting the descriptor length from big endian and adding the TLV header size. The operational flow is protocol-driven: userspace or a driver selects an ELS command byte, fills the command-specific request structure, transmits the payload inside an FC frame, and then interprets the response as either `LS_ACC`, `LS_RJT`, or a command-specific accept payload.

Login flows use FLOGI/PLOGI payloads to exchange common and class-specific service parameters, then may use PRLI/PRLO to activate or tear down FC-4 process images. Change notification flow uses SCR registration followed by RSCN payloads containing one or more affected-port pages. Diagnostic flow uses EDC/RDF exchanges to advertise supported descriptor tags and FPIN events to report link integrity, delivery, peer congestion, or congestion conditions.

## State and Persistence Behavior
The header does not persist data itself. It encodes state exchanged across the fabric: login negotiated parameters, timeout values, registered state-change interests, link-error counters, diagnostic-capability registration, FPIN event metadata, and topology identity information. Consumers must treat variable-length arrays (`desc[]`, `pname_list[]`, `rpl_pnb[1]`) as serialized message tails whose lifetime and bounds are owned by the containing receive buffer.

## Dependencies and Integration Points
It includes `<linux/types.h>`, `<asm/byteorder.h>`, and `stddef`/`linux/stddef.h` for `offsetof`. It depends on Fibre Channel scalar types and payload bounds defined in `fc_fs.h`. Integration points are FC transport drivers, libfc, fcoe tooling, BSG ELS passthrough (`scsi_bsg_fc.h`), and diagnostic tools that parse FPIN/RDF/EDC TLV lists.

## Risks and Test Signals
Primary risks are ABI layout drift, endian mistakes, and unbounded TLV walking. Variable payloads must be length-checked before accessing flexible arrays or using `fc_tlv_next_desc()`. Packed login/discovery structs should be guarded by compile-time size/offset checks where code depends on exact wire positions. Test signals include building exported UAPI headers for userspace, sparse/endian checking for `__be*` conversions, unit tests for TLV descriptor traversal with malformed lengths, and BSG or fabric-loop tests that verify LS_ACC/LS_RJT and FPIN/RDF/EDC decoding against known payload captures.
