# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_struct.h

## Purpose

`rvu_struct.h` defines hardware-visible RVU, NPA, NIX, and queue-context structures for the AF driver. It maps block addresses/types, interrupt vector numbers, admin queue operation encodings, NPA aura/pool contexts, NIX RQ/SQ/CQ/RSS/MCE/bandwidth-profile contexts, LSO and flow-key formats, VLAN tag controls, and per-LF statistic enums.

## Important APIs, Types, And Functions

- Block enums `rvu_block_addr_e` and `rvu_block_type_e` encode hardware block addresses and abstract block types used during discovery and resource assignment.
- Interrupt vector enums describe AF, PF, NPA, NIX, and CPT interrupt layout.
- `npa_aq_inst_s`, `npa_aq_res_s`, `nix_aq_inst_s`, and `nix_aq_res_s` define admin queue instruction/result words.
- `npa_aura_s` and `npa_pool_s` define buffer-pool state, flow control, thresholds, counters, and memory-stack metadata.
- `nix_cq_ctx_s`, `nix_rq_ctx_s`, `nix_sq_ctx_s`, `nix_cn10k_rq_ctx_s`, and `nix_cn10k_sq_ctx_s` are 128-byte queue contexts programmed by AQ.
- `nix_rsse_s`, `nix_rx_mce_s`, and `nix_bandprof_s` cover RSS entries, multicast/mirror entries, and ingress policer bandwidth profiles.
- `nix_lso_format` and `nix_rx_flowkey_alg` describe hardware LSO and RSS/parser extraction algorithms.
- VLAN enums and `VTAG_STRIP`/`VTAG_CAPTURE` define NIX VTAG behavior.
- `nix_stat_lf_tx` and `nix_stat_lf_rx` define per-LF stats indexes used by AF and NIC stats code.
- `static_assert(sizeof(...) == NIX_MAX_CTX_SIZE)` protects context sizes.

## Control Flow

The header has no executable control flow. Runtime code populates these packed bitfield structures in mailbox AQ requests and the AF writes them to hardware contexts. The same definitions are used to decode/read contexts in debug or stats paths. CN10K/CN20K-specific code chooses CN10K/CN20K request types but shares many field names, so the structure layout is part of the hardware ABI.

## State And Persistence

The structures represent persistent hardware context while an LF is configured: NPA aura/pool counters and flow-control state, NIX queue enable bits, buffer auras, scheduler mapping, stats counters, RSS entries, multicast chains, policer rates/actions, and VLAN/LSO/parser formats. In memory, they appear as transient mailbox request payloads or debug copies; in hardware, they remain until AQ write/disable/reset.

## Dependencies And Integration Points

Consumers include AF NPA/NIX resource handlers, NIC queue setup in `otx2_common.c`, CN10K/CN20K SQ/RQ/aura/pool setup, representor stat reads, RSS/LSO programming, TC/policer offload, and debugfs context dumping. The file depends on the compiler's kernel bitfield layout conventions for the target architecture and on exact alignment/size expectations from hardware.

## Risks

- Bitfield ordering and width errors directly corrupt queue or buffer-pool hardware context.
- CN10K and older NIX queue context differences are subtle; using the wrong request/context type can set unrelated bits.
- Several fields encode counter widths and split high/low ids; masks in callers must match these definitions.
- `static_assert` only validates total size, not bit position correctness.
- Hardware revisions with extended fields require coordinated changes across this header, mailbox structs, and setup code.

## Test Signals

Compile-time `static_assert` coverage, successful NPA/NIX LF allocation, RX/TX queue bring-up, RSS distribution, MCAM multicast/mirror operation, ingress policer behavior, VLAN tag insertion/strip, LSO offload, and debug context dumps matching expected hardware values are strong signals. Hardware smoke tests should include CN10K/CN20K and older OTX2 silicon.
