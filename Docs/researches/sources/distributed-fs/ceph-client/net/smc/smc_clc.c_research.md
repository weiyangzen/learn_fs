# sources/distributed-fs/ceph-client/net/smc/smc_clc.c

## Purpose
`smc_clc.c` implements CLC, the TCP in-band handshake protocol used before SMC-R/SMC-D data transfer. It manages user and system EID negotiation, netlink EID/SEID operations, CLC message validation, IP prefix construction and matching, CLC receive framing, DECLINE/PROPOSAL/ACCEPT/CONFIRM construction, v2 feature negotiation, hostname initialization, and cleanup of the EID table.

## Important APIs, Types, And Functions
Public functions include `smc_clc_ueid_count()`, `smc_nl_add_ueid()`, `smc_nl_remove_ueid()`, `smc_nl_flush_ueid()`, `smc_nl_dump_ueid()`, `smc_nl_dump_seid()`, `smc_nl_enable_seid()`, `smc_nl_disable_seid()`, `smc_clc_match_eid()`, `smc_clc_prfx_match()`, `smc_clc_wait_msg()`, `smc_clc_send_decline()`, `smc_clc_send_proposal()`, `smc_clc_send_confirm()`, `smc_clc_send_accept()`, `smc_clc_srv_v2x_features_validate()`, `smc_clc_clnt_v2x_features_validate()`, `smc_clc_v2x_features_confirm_check()`, `smc_clc_get_hostname()`, `smc_clc_init()`, and `smc_clc_exit()`. Internal helpers validate UEIDs, validate message headers/lengths/trailers, build first-contact extensions, and fill SMC-R/SMC-D accept-confirm payloads.

## Control Flow
EID control flows through a global locked table. Netlink add validates a 32-byte UEID, rejects duplicates and over-capacity, and appends it. Remove and flush delete entries; on s390, removing the last UEID re-enables system EID use. During handshake, `smc_clc_send_proposal()` builds an iovec containing the base proposal, optional SMC-D v1 data, optional IP prefix data, optional v2 extension with UEIDs and SMC-R RoCE GID, optional SMC-D v2 extension with system EID and GID/CHID pairs, and trailer, then sends it over the CLC socket.

`smc_clc_wait_msg()` peeks the CLC header from the TCP stream to determine exact message length, receives that many bytes without consuming following data, validates eyecatcher/type/length/trailer, drains any extra proposal bytes beyond the caller buffer, and returns either success, peer-decline reason, or socket/protocol error. Accept and confirm share `smc_clc_send_confirm_accept()`, which selects SMC-D or SMC-R formatting, inserts first-contact extension data when required, and sends the assembled iovec. Feature validation compares release, max connections, max links, and feature masks across proposal, accept, and confirm.

## State And Persistence
Persistent module state is `smc_hostname` and the global `smc_clc_eid_table` containing a rwlock, UEID list, UEID count, and SEID-enabled flag. Handshake-specific data persists only through CLC wire messages and the caller's `struct smc_init_info`: selected versions, negotiated EID, release number, feature mask, max connections/links, GID/CHID candidates, and routing data.

## Dependencies And Integration Points
The file integrates with generic netlink attributes, UTS hostname, TCP socket send/recv, IPv4/IPv6 address and prefix inspection, network device/dst lookup under RCU, SMC core initialization data, RDMA GID/MAC values, ISM system EID/GID/CHID helpers, SMC netlink family definitions, and version/feature constants from `smc.h` and `smc_clc.h`.

## Risks And Edge Cases
CLC parsing is security-sensitive because it handles peer-controlled lengths and offsets. Validation must reject malformed offsets, excessive IPv6 prefix counts, excessive UEIDs/GID entries, wrong accept lengths, and missing trailers. The proposal validator references SMC-D v2 extension sizing only when v2 data is present; offset helpers must prevent out-of-bounds access. `smc_clc_wait_msg()` temporarily overwrites CLC socket receive timeout and must restore it on every exit. SEID behavior differs on s390 versus other platforms.

## Test Signals
Useful tests include netlink add/remove/flush/dump UEID and SEID behavior, invalid UEID character and count rejection, proposal/accept/confirm/decline encode/decode length checks for v1/v2 SMC-R/SMC-D, malformed CLC fuzzing, TCP stream coalescing where extra bytes follow a CLC message, timeout and signal interruption in `smc_clc_wait_msg()`, IPv4/v4-mapped/IPv6 prefix match tests, feature negotiation for release/max-links/max-conns, and endian/layout tests for packed CLC structures.
