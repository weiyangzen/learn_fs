# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.h

Purpose: declares VF-side low-level PF/VF protocol transport functions.

Important API: `adf_send_vf2pf_msg` sends an asynchronous VF message. `adf_send_vf2pf_req` sends a request and returns the PF response. `adf_send_vf2pf_blkmsg_req` reconstructs a block message into a caller buffer. `adf_enable_vf2pf_comms` initializes VF communication.

Control flow and state: no header state. Implementation uses `accel_dev->vf` lock/completion/response state and generation-specific PFVF ops.

Dependencies and integration: included by VF message code and VF setup paths. It is the lower layer beneath VF capabilities and ring-map queries.

Risks and test signals: signatures expose buffer length as in/out for block messages; callers must pass adequate space and inspect final length. Test request/response sequencing and error propagation into VF probe/config code.
