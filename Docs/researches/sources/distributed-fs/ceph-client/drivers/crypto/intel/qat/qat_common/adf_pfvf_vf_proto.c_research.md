# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_proto.c

Purpose: implements VF-side low-level PF/VF transport, synchronous request/response handling, block-message reconstruction with CRC, PF message dispatch, and VF communication enablement.

Important APIs: `adf_send_vf2pf_msg`, `adf_send_vf2pf_req`, `adf_send_vf2pf_blkmsg_req`, `adf_recv_and_handle_pf2vf_msg`, and `adf_enable_vf2pf_comms`.

Control flow and state: synchronous requests reinitialize `vf.msg_received`, send a message, then wait with bounded retries for a PF response completed by interrupt handling. Block-message retrieval asks for version, length, payload bytes, and CRC byte-by-byte, truncating to local buffer length and verifying CRC. PF messages either trigger restart handling, complete responses, or log fatal/unknown messages. Enabling comms initializes CRC, enables PF2VF interrupts, then requests version, capabilities, and ring map.

Dependencies and integration: uses completions, PFVF ops, compatibility fields, VF response storage, and high-level VF query helpers.

Risks and test signals: response timeout returns `-EIO`; concurrent requests share `vf.response` and completion, so transport should be serialized by call paths. Test PF response loss/retry, CRC mismatch, truncated payloads, restart notifications, fatal messages, and enablement sequencing.
