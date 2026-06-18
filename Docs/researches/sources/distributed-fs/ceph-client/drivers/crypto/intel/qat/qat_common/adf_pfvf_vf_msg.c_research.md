# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_pfvf_vf_msg.c

Purpose: implements VF-side high-level messages and queries to the PF: init/shutdown/restart-complete notifications, compatibility negotiation, extended capabilities retrieval, and ring-to-service mapping retrieval.

Important APIs: `adf_vf2pf_notify_init`, `adf_vf2pf_notify_shutdown`, `adf_vf2pf_notify_restart_complete`, `adf_vf2pf_request_version`, `adf_vf2pf_get_capabilities`, and `adf_vf2pf_get_ring_to_svc`.

Control flow and state: init sends `INIT` and sets `ADF_STATUS_PF_RUNNING`. Shutdown sends only if PF is marked running. Version request sends current compatibility and stores PF version after accepting compatible/unknown responses. Capabilities query uses block message v1-v3 parsing to update extended DC capabilities, capabilities mask, and clock frequency when provided. Ring map query updates `hw_device->ring_to_svc_map`.

Dependencies and integration: depends on VF protocol request helpers, bitfield masks, PF compatibility version, and hardware data fields consumed later by VF config and service mapping.

Risks and test signals: truncated block messages are partially accepted only where version length permits; missing capabilities leave defaults. Test old PF, newer PF, incompatible PF, truncated v1/v2/v3 payloads, and ring-to-service map fallback.
