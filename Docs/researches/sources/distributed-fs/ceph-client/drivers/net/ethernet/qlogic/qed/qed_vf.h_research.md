# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_vf.h

## Purpose
`qed_vf.h` defines the VF/PF mailbox ABI used by the QED VF driver and declares the VF helper API implemented in `qed_vf.c`. It contains the TLV wire structures for acquisition, queue/vport management, filters, RSS, tunnel updates, coalescing, bulletin MAC updates, PF responses, and the PF-to-VF bulletin board.

## Important APIs, Types, And Functions
Important wire types include `struct channel_tlv`, `struct vfpf_first_tlv`, `struct pfvf_tlv`, `struct vfpf_acquire_tlv`, `struct pfvf_acquire_resp_tlv`, queue TLVs such as `vfpf_start_rxq_tlv`, `vfpf_start_txq_tlv`, stop/update queue TLVs, vport update TLVs, `vfpf_ucast_filter_tlv`, `vfpf_update_tunn_param_tlv`, `pfvf_update_tunn_param_tlv`, coalescing TLVs, and `vfpf_bulletin_update_mac_tlv`. The unions `union vfpf_tlvs` and `union pfvf_tlvs` reserve the fixed 1024-byte mailbox size. `struct qed_bulletin_content` is the PF-published shared status structure, and `struct qed_vf_iov` is the per-hwfn VF runtime container.

## Control Flow
The header describes the control vocabulary consumed by `qed_vf.c`. Every request begins with `vfpf_first_tlv`, which carries a physical reply address, then optional typed TLVs, and ends with `CHANNEL_TLV_LIST_END`. PF responses embed `pfvf_tlv` headers with `PFVF_STATUS_*` status codes. Acquisition negotiates VF capabilities, requested resources, bulletin address/size, PF capabilities, device identity, queue/status-block IDs, stats locations, and fastpath HSI compatibility. Later TLVs use relative queue IDs and optionally `CHANNEL_TLV_QID` when the PF negotiated queue-QID support.

## State, Persistence, And Dependencies
`struct qed_vf_iov` stores mailbox pointers and DMA addresses, a mutex and TLV offset cursor, the coherent bulletin board and shadow, saved acquisition response, legacy-HSI compatibility state, registered status-block pointers, and doorbell-bar mode. `struct qed_bulletin_content` persists PF-provided link parameters, link state, link capabilities, forced/suggested MAC, forced VLAN/default untagged flags, tunnel UDP ports, and a CRC/version pair for race detection. The header depends on QED L2/MCP types, Ethernet constants, QED queue CIDs, link parameter structures, and SR-IOV build configuration.

## Integration Points
When `CONFIG_QED_SRIOV` is enabled this header exposes the VF operations used by the rest of QED and QEDE: hardware prepare/release/reset, queue and vport commands, filtering, interrupt cleanup, coalescing, link/resource getters, bulletin polling, tunnel update preparation, and MAC bulletin requests. When SR-IOV is disabled, inline stubs return `-EINVAL`, `false`, `0`, or no-op behavior so callers can compile without VF support.

## Risks
The TLV structures are a hardware/firmware ABI, so layout, sizes, alignment, and enum values must remain compatible with PF firmware and older drivers. `CHANNEL_TLV_VPORT_UPDATE_MAX` assumes vport update TLV enum values stay sequential. `TLV_BUFFER_SIZE` constrains future extension space. Several fields are documented as deprecated but still required for backward compatibility. The fallback stubs can hide accidental VF calls in non-SRIOV builds until runtime paths observe `-EINVAL`.

## Test Signals
Validation should include compile-time structure size/layout checks where available, acquisition with old and new PF capability combinations, mailbox TLV list parsing, vport update enum iteration, SR-IOV enabled and disabled builds, bulletin CRC/version parsing, and queue-QID negotiation coverage.
