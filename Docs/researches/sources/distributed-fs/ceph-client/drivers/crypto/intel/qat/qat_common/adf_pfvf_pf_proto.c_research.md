# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_proto.c

Purpose: implements PF-side receive, dispatch, response, compatibility negotiation, block-message serving, and ring-pair reset handling for VF-to-PF messages.

Important APIs: `adf_send_pf2vf_msg`, `adf_recv_and_handle_vf2pf_msg`, and `adf_enable_pf2vf_comms`. Key helpers include `handle_blkmsg_req`, `handle_rp_reset_req`, and `adf_handle_vf2pf_msg`.

Control flow and state: received messages are decoded through generation-specific PFVF ops. Version requests store `vf_info->vf_compat_ver` and return compatibility. Init/shutdown/restart-complete toggle `vf_info->init/restarting`. Block requests map small/medium/large request encoding to registered providers and can return data bytes or CRC. Ring reset validates reserved bits and VF-local bank index, converts it to PF bank number, and calls `ring_pair_reset`.

Dependencies and integration: uses `accel_dev->pf.vf_info`, PF/VF locks, CRC utilities, capability/ring-map providers, hardware reset callback, and SR-IOV workqueue scheduling.

Risks and test signals: malformed block offsets or provider sizes return protocol error data; unknown message returns false so interrupt may remain disabled. Test compatibility matrix, block CRC/truncation paths, ring reset success/invalid/timeout, and interrupt re-enable after handler.
