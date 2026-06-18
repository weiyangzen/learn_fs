<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/fw.h

## Purpose
This header defines the firmware-facing BPF ABI structures and constants used by the NFP BPF app. It covers BPF capability TLVs, stable firmware encodings for selected verifier register types, BPF map control-message payloads, firmware return codes, fixed ABI v2 map element slot sizes, and asynchronous BPF event messages.

## Important APIs, Types, And Functions
- Capability types: `enum bpf_cap_tlv_type` includes helper functions, adjust-head, maps, random, queue-select, adjust-tail, ABI version, and multi-entry control-message support.
- Capability payloads: `struct nfp_bpf_cap_tlv_func`, `struct nfp_bpf_cap_tlv_adjust_head`, and `struct nfp_bpf_cap_tlv_maps`.
- Register-type ABI constants: `NFP_BPF_SCALAR_VALUE`, `NFP_BPF_MAP_VALUE`, `NFP_BPF_STACK`, and `NFP_BPF_PACKET_DATA` decouple firmware ABI from kernel enum churn.
- Map control messages: `cmsg_req_map_alloc_tbl`, `cmsg_reply_map_alloc_tbl`, `cmsg_req_map_free_tbl`, `cmsg_req_map_op`, and `cmsg_reply_map_op`.
- Event message: `struct cmsg_bpf_event` carries CPU id, map id/pointer, data size, packet size, and payload bytes.

## Control Flow
The header is consumed by app startup to parse `_abi_bpf_capabilities`, by verifier checks to gate helpers/features, by control-message code to serialize map requests, and by event-output code to decode firmware-generated perf events. Firmware return codes in `enum nfp_bpf_cmsg_status` are translated to host errnos by `cmsg.c`.

## State And Persistence
The header defines ABI layout, not storage. Runtime parsed capability state is stored in `struct nfp_app_bpf`; firmware map state is addressed by table ids returned in map allocation replies. Endianness is explicit in control messages (`__be32`/`__be64`) and capability TLVs are read from little-endian firmware memory with MMIO accessors.

## Dependencies And Integration Points
It includes Linux bitops/types and `../ccm.h` for the common control-message header. It is shared by BPF `main.c`, `cmsg.c`, `offload.c`, `verifier.c`, and `jit.c`, and by firmware that must emit exactly matching TLVs and control-message replies.

## Risks And Edge Cases
- These structs are firmware ABI; field size, order, and endianness changes break compatibility.
- The comment notes kernel `enum bpf_reg_type` is not uABI, so `BUILD_BUG_ON()` checks in verifier code are needed to catch drift for event-output pointer types.
- ABI v2 fixed key/value longword sizes can waste MTU or truncate if map validation is wrong; ABI v3 relies on parsed max sizes.
- Event messages include separate packet and data payload lengths; callers must validate combined size to avoid overrun.

## Test Signals
Validate capability TLV parsing for every known type, ABI version fallback and rejection, map control-message serialization against firmware, firmware return-code coverage, event-output decoding with valid and malformed lengths, and compile-time checks that stable NFP pointer-type constants still match kernel verifier constants where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/fw.h -->
