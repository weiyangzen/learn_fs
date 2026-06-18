# sources/distributed-fs/ceph-client/include/linux/soc/qcom/pdr.h

Purpose: This header defines Qualcomm Protection Domain Restart service lookup and restart helpers.

Important APIs/types/functions: It defines service name/PFR lengths, opaque `struct pdr_service` and `struct pdr_handle`, `enum servreg_service_state`, and APIs `pdr_handle_alloc`, `pdr_add_lookup`, `pdr_restart_pd`, and `pdr_handle_release`.

Control flow: A client allocates a PDR handle with a status callback, adds service lookups by name/path, receives service up/down/early-down/uninit state changes, can request PD restart, and releases the handle.

State and persistence: The PDR subsystem owns lookup registrations, service objects, callback private data, and remote service state. Remote protection domains persist independently across restarts.

Dependencies and integration: Includes Qualcomm QMI support and integrates with service registry, remoteproc/subsystem restart, audio/modem/WLAN clients, and GLINK/QMI transports.

Risks and test signals: Service path/name mismatch prevents notifications; restart calls can disrupt shared domains. Test service up/down callbacks, SSR events, lookup cleanup, restart failure, and long service names.
