# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_msg.h

Purpose: defines the PF/VF register-message protocol ABI used by QAT SR-IOV PF and VF drivers. It documents Gen2 and Gen4 register layouts, common interrupt/origin bits, typed messages, compatibility versions, ring reset responses, block-message formats, and block payload structs.

Important types and macros: `struct pfvf_message` is the abstract message. Enums cover PF2VF and VF2PF message types, compatibility versions, compatibility results, ring-reset results, block response types/errors, block request categories, capabilities versions, and ring-to-service map versions. Payload structs include `capabilities_v1/v2/v3` and `ring_to_svc_map_v1`.

Control flow and state: no runtime behavior. The header defines bitfield masks and bounds used by PF/VF protocol implementations to encode/decode CSR messages and byte-wise block transfers.

Dependencies and integration: included by PF and VF message/protocol files, generation-specific PFVF ops, SR-IOV, and VF hardware initialization.

Risks and test signals: ABI changes affect PF/VF compatibility. Test old/new PF-VF pairings, block-message truncation, CRC validation, Gen2/Gen4 type width limits, and ring-reset field validation.
