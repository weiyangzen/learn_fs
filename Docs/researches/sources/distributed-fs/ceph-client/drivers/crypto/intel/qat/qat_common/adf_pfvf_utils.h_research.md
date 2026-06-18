# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_utils.h

Purpose: declares PF/VF utility helpers, CSR field-format descriptors, timing constants for acknowledgement waits, and compatibility checking logic.

Important types and API: `struct pfvf_field_format` and `struct pfvf_csr_format` describe type/data bit positions and masks. Declares CRC and CSR conversion helpers. `adf_vf_compat_checker` returns incompatible for zero, compatible for versions up to current, and unknown for newer VFs.

Control flow and state: inline compatibility policy is the only behavior. There is no persistent state in the header.

Dependencies and integration: includes `adf_pfvf_msg.h` for protocol versions/results. Shared by PF and VF protocol implementations and generation-specific CSR ops.

Risks and test signals: compatibility policy permits newer VFs as "unknown" rather than hard fail at PF side, while VF-side handling decides final acceptance. Test mixed-version PF/VF behavior and ack timing under slow or contended register access.
