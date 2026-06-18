# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.c

## Purpose
This file implements the ICE PF-side virtchnl RSS handlers for SR-IOV VFs. It translates VF-provided `virtchnl_rss_cfg`, RSS key, LUT, hash-function, and hash-capability requests into ICE VSI and flow profile programming. It supports both classic key/LUT/hfunc operations and advanced RSS profile add/delete, including protocol-header parsing, raw packet pattern parsing, symmetric hashing, GTPU rule ordering, and per-VF context tracking.

## Important APIs, Types, And Functions
The exported handlers are `ice_vc_handle_rss_cfg()`, `ice_vc_config_rss_key()`, `ice_vc_config_rss_lut()`, `ice_vc_config_rss_hfunc()`, `ice_vc_get_rss_hashcfg()`, and `ice_vc_set_rss_hashcfg()`. Internal mapping tables `ice_vc_hdr_list` and `ice_vc_hash_field_list` convert `VIRTCHNL_PROTO_HDR_*` and field selectors to `ICE_FLOW_SEG_HDR_*` and `ICE_FLOW_FIELD_IDX_*` masks. `ice_vc_validate_pattern()` checks whether the PF package enables the derived packet type. `ice_vc_parse_rss_cfg()` builds `struct ice_rss_hash_cfg`. `ice_add_rss_cfg_wrap()` and `ice_rem_rss_cfg_wrap()` program or remove flow RSS profiles while keeping VF hash context state coherent.

## Control Flow
`ice_vc_handle_rss_cfg()` validates PF RSS support, advanced RSS capability negotiation, VF active state, algorithm range, and VSI existence. `VIRTCHNL_RSS_ALG_R_ASYMMETRIC` only updates the VSI hash mode to XOR or Toeplitz. Other algorithms update VSI hash mode to symmetric or standard Toeplitz and then choose either raw-pattern handling when `proto_hdrs.count == 0` and `tunnel_level == 0`, or protocol-header parsing for normal profiles. Raw profiles are parsed through the ICE parser, then installed with `ice_flow_set_parser_prof()` and tracked by packet-type group. Normal profiles are parsed, validated, added through `ice_add_rss_cfg_wrap()`, or removed through `ice_rem_rss_cfg_wrap()`.

## State And Persistence
The file updates persistent in-memory VF state in `vf->hash_ctx`, `vf->rss_prof_info`, and `vf->rss_hashcfg`. VSI RSS hash mode is persisted in `vsi->info.q_opt_rss` after `ice_update_vsi()` succeeds. GTPU contexts are cached separately for IPv4 and IPv6 to preserve TCAM ordering across later adds and deletes. Raw RSS profile state is cached per packet-type group. This state is runtime driver state, rebuilt through virtchnl requests after VF/PF reset rather than stored on disk.

## Dependencies And Integration Points
The code depends on virtchnl ABI definitions, ICE flow director/RSS profile helpers, parser profile helpers, VSI update admin queue calls, and VF state from `ice_vf_lib_private.h`. It is integrated by `virtchnl.c` through `ice_virtchnl_ops` entries for RSS opcodes. Error responses are converted to virtchnl status and returned with `ice_vc_send_msg_to_vf()`.

## Risks
The highest-risk behavior is rule ordering for overlapping GTPU extension-header, uplink, and downlink RSS profiles. Incorrect moveout, remove, or moveback logic can shadow more-specific profiles or leave stale hardware rules. Raw profile parsing depends on VF-provided packet bytes and masks, so length bounds and allocation failures matter. `ice_vc_parse_rss_cfg()` mutates protocol header field selectors for fragment cases, so callers must not expect the message buffer to remain logically unchanged.

## Test Signals
Useful tests include VF virtchnl add/delete RSS profiles for IPv4, IPv6, TCP, UDP, SCTP, ESP/NAT-T ESP, PFCP, L2TP, GRE, and GTPU EH/UP/DWN combinations; symmetric versus asymmetric algorithm changes; raw profile add/remove with valid and invalid packet lengths; RSS key length and LUT size validation; reset/replay behavior for `vf->hash_ctx`; and negative tests for inactive VFs, missing RSS PF flag, unsupported ptypes, invalid protocol counts, and package-disabled packet types.
