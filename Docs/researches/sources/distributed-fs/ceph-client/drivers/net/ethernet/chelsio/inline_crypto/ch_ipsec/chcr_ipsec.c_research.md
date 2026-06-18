# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.c

## Purpose
Implements Chelsio T6 inline IPsec ESP TX crypto offload as a cxgb4 upper-layer driver. It registers xfrmdev callbacks for SA lifecycle management and a ULD TX handler that converts outbound ESP skbs into Chelsio crypto work requests using AES-GCM key context and CPL security PDU descriptors.

## Important APIs, Types, And Functions
The module registers `ch_ipsec_uld_info` with `cxgb4_register_uld(CXGB4_ULD_IPSEC, ...)` and exposes xfrmdev operations through `ch_ipsec_xfrmdev_ops`. Device context is tracked in global `uld_ctx_list` under `dev_mutex`.

Key functions include `ch_ipsec_uld_add()`, `ch_ipsec_uld_state_change()`, `ch_ipsec_xfrm_add_state()`, `ch_ipsec_xfrm_del_state()`, `ch_ipsec_xfrm_free_state()`, `ch_ipsec_advance_esn_state()`, `ch_ipsec_setauthsize()`, `ch_ipsec_setkey()`, `calc_tx_sec_flits()`, `copy_esn_pktxt()`, `copy_cpltx_pktxt()`, `copy_key_cpltx_pktxt()`, `ch_ipsec_crypto_wreq()`, and `ch_ipsec_xmit()`.

## Control Flow
Module init registers the ULD. When cxgb4 attaches, `ch_ipsec_uld_add()` stores low-level adapter information, and state changes add/remove the context from the global list. On xfrm state add, `ch_ipsec_xfrm_add_state()` validates that the SA is ESP, IPv4/IPv6, transport/tunnel, AEAD AES-GCM with supported ICV/key lengths, no encapsulation/compression/TFC padding, `seqiv` geniv, and crypto offload type. It then pins the module, allocates `ipsec_sa_entry`, derives auth truncation mode, detects ESN, extracts key/salt, computes GHASH H by AES encrypting zero, builds the hardware key context header, and stores the SA pointer in `x->xso.offload_handle`.

Outbound data enters `ch_ipsec_xmit()` from the cxgb4 ULD TX hook. It validates the offload handle and single secpath, reclaims completed TX descriptors, calculates flits/descriptor credits, maps non-immediate skbs, builds a `FW_ULPTX_WR` with `CPL_TX_SEC_PDU`, copies key context, CPL TX packet context, optional ESN AAD/IV, then either inlines packet bytes or writes an SGL. It records retained skbs in TX software descriptors, advances queue producer state, and rings the cxgb4 TX doorbell.

Module exit removes live contexts from `uld_ctx_list`, resets adapter IPsec stats, frees ULD contexts, and unregisters the ULD.

## State And Persistence
Per-SA state lives in `struct ipsec_sa_entry` attached to `xfrm_state.xso.offload_handle`; it stores auth mode, ESN flag, encryption key length, key-context length, auth tag size, key-context header, salt, and key plus GHASH H material. Per-device state is the ULD context list and cxgb4 adapter stats (`ch_ipsec_stats.ipsec_cnt`). TX queue state is shared with cxgb4 SGE rings and software descriptors. State is in-memory only and is freed on xfrm state free or module exit.

## Dependencies And Integration Points
The file depends on Linux xfrm/ESP offload APIs, crypto AES/hash helpers, cxgb4 ULD registration, cxgb4 SGE helper exports (`cxgb4_reclaim_completed_tx()`, `cxgb4_map_skb()`, `cxgb4_write_sgl()`, `cxgb4_inline_tx_skb()`, `cxgb4_ring_tx_db()`), Chelsio CPL/ULPTX firmware structures, and crypto key-context macros from drivers/crypto/chelsio headers. cxgb4 main netdev xfrmdev ops delegate SA lifecycle calls to this ULD, and cxgb4 SGE dispatches IPsec TX skbs to `tx_handler`.

## Risks
SA validation is narrow: only AES-GCM key lengths 128/256 plus 32-bit salt and ICV 96/128 are accepted, while `ch_ipsec_setauthsize()` has an ICV_8 case that cannot be reached through current validation. `ch_ipsec_xfrm_add_state()` ignores the return from `ch_ipsec_setkey()`, which risks installing an SA with incomplete key context if key setup fails. ESN handling builds synthetic AAD/IV data and adjusts cipher offsets; offset mistakes can produce invalid packets. TX ring wrap and immediate/SGL paths are sensitive to descriptor math. `ch_ipsec_uld_state_change()` removes list entries without taking `dev_mutex` on down/detach paths, which is a concurrency point to review against cxgb4 ULD state-change serialization.

## Test Signals
Signals include module load/unload and ULD registration, xfrm state add rejection messages for unsupported algorithms/modes, successful AES-GCM ESP offload for IPv4/IPv6 transport and tunnel, ESN and non-ESN packet validation against a peer, TX ring pressure behavior, DMA API checks on mapped SGLs, `ip xfrm` offload lifecycle tests, adapter debugfs IPsec counter changes, and fallback behavior when offload handles are absent.
