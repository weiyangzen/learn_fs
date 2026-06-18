# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.h

Purpose: declares PF-side low-level PF/VF protocol entry points.

Important API: `adf_send_pf2vf_msg(struct adf_accel_dev *, u8 vf_nr, struct pfvf_message)` sends a PF message to a specific VF. `adf_enable_pf2vf_comms(struct adf_accel_dev *)` initializes PF-side protocol support.

Control flow and state: header only. Runtime state lives in PF/VF ops and `accel_dev->pf` fields initialized by the implementation.

Dependencies and integration: includes Linux types and `adf_accel_devices.h`. Used by PF notification code, SR-IOV, and generation-specific operations.

Risks and test signals: build catches type drift. Runtime tests should verify PF comms init initializes CRC and interrupt lock before SR-IOV enables VF interrupts.
