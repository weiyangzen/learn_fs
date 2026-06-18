# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_pf_msg.c

Purpose: implements PF-originated notifications to VFs and PF-side block-message providers for VF queries.

Important APIs: `adf_pf2vf_notify_restarting`, `adf_pf2vf_wait_for_restarting_complete`, `adf_pf2vf_notify_restarted`, `adf_pf2vf_notify_fatal_error`, `adf_pf_capabilities_msg_provider`, and `adf_pf_ring_to_svc_msg_provider`.

Control flow and state: restarting notification marks initialized, compatible VFs as `restarting` and sends a message. The wait loop polls up to 100 times with 100 ms sleeps for VFs to send restart-complete. Restarted and fatal-error notifications are sent to initialized compatible VFs. Providers serialize PF hardware extended DC capabilities, capabilities mask, and ring-to-service map into block-message buffers with versioned headers.

Dependencies and integration: uses PCI VF count, PFVF send helper, VF info state, and hardware data. Called by SR-IOV disable/restart/error paths and PF block-message request handling.

Risks and test signals: wait loop can delay shutdown up to about 10 seconds; provider version content must match VF parser expectations. Test VF restart handshake, timeout warning, fatal-error broadcast, and VF retrieval of capabilities/ring map.
