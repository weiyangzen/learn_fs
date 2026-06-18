# sources/distributed-fs/ceph-client/net/smc/smc_clc.h

## Purpose
`smc_clc.h` defines the CLC wire protocol used for SMC negotiation over the internal TCP socket. It provides message type constants, SMC type encodings, wait timeouts, decline reason codes, packed v1/v2 proposal/accept/confirm/decline layouts, extension layouts for SMC-Dv2 and first contact, bounded proposal-area storage, offset helpers, type helpers, and CLC function prototypes.

## Important APIs, Types, And Functions
Important definitions include `SMC_CLC_PROPOSAL`, `SMC_CLC_ACCEPT`, `SMC_CLC_CONFIRM`, `SMC_CLC_DECLINE`, `SMC_TYPE_R`, `SMC_TYPE_D`, `SMC_TYPE_N`, `SMC_TYPE_B`, `CLC_WAIT_TIME`, and the `SMC_CLC_DECL_*` diagnosis codes. Core wire structs include `smc_clc_msg_hdr`, `smc_clc_msg_trail`, `smc_clc_msg_local`, `smc_clc_ipv6_prefix`, `smc_clc_v2_extension`, `smc_clc_msg_proposal`, `smc_clc_msg_proposal_area`, `smcr_clc_msg_accept_confirm`, `smcd_clc_msg_accept_confirm_common`, `smc_clc_first_contact_ext`, `smc_clc_first_contact_ext_v2x`, `smc_clc_fce_gid_ext`, `smc_clc_msg_accept_confirm`, `smc_clc_msg_decline`, and `smc_clc_msg_decline_v2`. Inline helpers locate variable proposal extensions and test indicated SMC types.

## Control Flow
`af_smc.c` and `smc_clc.c` use these layouts to build and parse the CLC state machine: client sends proposal, server sends accept, client sends confirm, or either side sends decline. Offset helpers such as `smc_clc_proposal_get_prefix()`, `smc_get_clc_msg_smcd()`, `smc_get_clc_v2_ext()`, `smc_get_clc_smcd_v2_ext()`, and `smc_get_clc_first_contact_ext()` let parsers navigate variable-length proposal and accept-confirm data while bounding offsets against `smc_clc_msg_proposal_area`.

## State And Persistence
The header owns no runtime storage, but its structs are serialized directly on the TCP CLC connection and copied into initialization/link-group state. The decline reason constants persist in fallback statistics and peer diagnosis fields. Negotiated EIDs, GIDs, CHIDs, release, max connections, max links, feature masks, first-contact hostnames, and SMC-D tokens originate from these wire structs.

## Dependencies And Integration Points
`smc_clc.h` includes RDMA verbs, public Linux SMC UAPI constants, `smc.h`, and SMC netlink definitions. It is consumed by socket handshake code, CLC encoding/decoding, SMC-R link setup, SMC-D device selection, netlink EID management, and feature negotiation.

## Risks And Edge Cases
Most structs are packed or aligned for external protocol compatibility. Bitfields depend on endian configuration, and variable-length extension offsets must remain consistent with `static_assert()` guarded fixed portions. Adding fields outside the tagged fixed groups would break offset calculations. The unioned accept/confirm layout reuses overlapping SMC-R and SMC-D data; callers must use `hdr.typev1` and `is_smcd` consistently.

## Test Signals
Signals include compile-time layout/static-assert coverage, protocol capture comparison for v1/v2 CLC messages, fuzz tests for extension offsets and counts, decline-code mapping tests, first-contact extension parsing, SMC type helper tests, and cross-endian build coverage for header bitfields.
