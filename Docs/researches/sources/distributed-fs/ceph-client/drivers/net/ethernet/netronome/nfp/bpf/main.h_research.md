<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.h

## Purpose
This header defines the shared internal model for NFP eBPF offload. It contains app private state, map private state, neutral-map records, JIT instruction metadata, program compilation state, per-vNIC state, register/relocation conventions, opcode classification helpers, and prototypes linking the BPF app, verifier, JIT, control-message, and offload code.

## Important APIs, Types, And Functions
- `struct nfp_app_bpf` stores CCM transport, BPF offload device, cmsg sizing/cache count, map list/resource counters, neutral-map rhashtable, ABI version, parsed capabilities, helper addresses, and feature booleans.
- `struct nfp_bpf_map` attaches firmware table id, cache state, and per-4-byte use tracking to an offloaded map.
- `struct nfp_bpf_neutral_map` tracks maps that are legal to reference by id for event output without being NFP-offloaded maps.
- `struct nfp_insn_meta` wraps each BPF instruction with verifier pointer/range state, optimization flags, jump/call metadata, packet-cache/gather metadata, and generated-code offset.
- `struct nfp_prog` stores the full compilation unit: generated image, stack/subprogram info, relocation targets, map records, instruction list, and translation error state.
- Register/relocation definitions include `enum nfp_relo_type`, static register ids, packet-vector accessors, `STACK_FRAME_ALIGN`, and instruction flags such as `FLAG_INSN_DO_ZEXT`.
- Inline classifiers such as `is_mbpf_load()`, `is_mbpf_store()`, `is_mbpf_atomic()`, `is_mbpf_helper_call()`, and `is_mbpf_pseudo_call()` keep verifier and JIT opcode logic aligned.

## Control Flow
The header's structures carry a BPF program through offload lifecycle. `offload.c` allocates `struct nfp_prog` and populates `nfp_insn_meta`; `verifier.c` updates metadata during kernel verifier callbacks; `jit.c` uses that metadata to optimize, translate, and relocate machine code; `offload.c` then loads the image into firmware. Map device ops use `struct nfp_bpf_map` and control-message prototypes; event output uses neutral-map records.

## State And Persistence
All state is volatile kernel memory. `nfp_app_bpf` persists for the app lifetime, `nfp_bpf_vnic` for vNIC lifetime, `nfp_bpf_map` for map lifetime, and `nfp_prog`/`nfp_insn_meta` for program offload lifetime. Firmware-visible state is referenced by helper addresses, table ids, and loaded code offsets but is not stored in this header.

## Dependencies And Integration Points
The header includes Linux BPF verifier/offload, rhashtable, skb, waitqueue, bitfield, and NFP assembly/CCM/FW headers. It is the central contract among `main.c`, `cmsg.c`, `offload.c`, `verifier.c`, and `jit.c`, and it exposes `nfp_bpf_dev_ops`, `nfp_ndo_bpf()`, and `nfp_net_bpf_offload()` to app/netdev integration.

## Risks And Edge Cases
- Metadata unions reuse storage for pointer, jump, call, and ALU range information; users must only read fields relevant to the instruction class.
- `FLAG_INSN_SKIP_MASK` coordinates verifier and JIT optimizations; branch destinations into skipped instructions are invalid.
- Stack and subprogram accounting depend on verifier-populated call metadata and fixed NFP stack-frame alignment.
- Map use tracking is per 4-byte word, so unaligned or mixed-size accesses can mark multiple words and reject conflicting atomic/read use.
- Relocation marker bits temporarily occupy instruction bits and must be cleared before firmware load.

## Test Signals
Compile coverage across all BPF source files, verifier/JIT tests for every opcode helper classifier, map cache/use tracking, neutral-map event output, subprogram stack metadata, relocation target generation, zero-extension flags, and teardown warnings for non-empty map lists or resource counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.h -->
