# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_mstate_mgr.h

Purpose: defines migration-state section identifiers, manager/preamble structures, callback types, and the public state-buffer manager API.

Important types and API: constants such as `ADF_MSTATE_ETRB_IDS`, `ADF_MSTATE_CONFIG_IDS`, `ADF_MSTATE_SLA_IDS`, `ADF_MSTATE_VM2PF_IDS`, and `ADF_MSTATE_PF2VM_IDS` form the state schema. `struct adf_mstate_mgr`, `struct adf_mstate_preh`, and `struct adf_mstate_vreginfo` define the generic buffer cursor, preamble, and virtual-register copy source. Callback typedefs support custom preamble validation, population, and restore actions.

Control flow and state: header only. State is caller-owned buffer memory plus the manager cursor.

Dependencies and integration: consumed by `adf_mstate_mgr.c` and migration/device-specific code that serializes QAT VF state.

Risks and test signals: section IDs are fixed-width eight-byte fields, so naming collisions/truncation would break lookup. Test all producer/consumer section IDs, buffer size accounting, and compatibility with older remote preamble versions.
