# sources/distributed-fs/ceph-client/include/rdma/iw_cm.h

Purpose: Kernel iWARP Connection Manager API for RDMA over TCP/iWARP connection setup, teardown, events, and provider/client callbacks.

Important APIs/types/functions: `enum iw_cm_event_type`, `struct iw_cm_event`, `iw_cm_handler`, `iw_event_handler`, `struct iw_cm_id`, `struct iw_cm_conn_param`, `enum iw_flags`, and APIs `iw_create_cm_id`, `iw_destroy_cm_id`, `iw_cm_listen`, `iw_cm_accept`, `iw_cm_reject`, `iw_cm_connect`, `iw_cm_disconnect`, `iw_cm_init_qp_attr`, and `iwcm_reject_msg`.

Control flow: Clients create IDs with callbacks, then listen/accept/reject or actively connect. Providers deliver lower-level events to IW CM, which calls the client handler. Events can be delivered before connect/accept returns, and destroy/failure paths document when no more events will arrive.

State and persistence behavior: `iw_cm_id` stores runtime connection state: device, context, local/remote socket addresses, mapped addresses, provider data, provider ref hooks, TOS, mapping state, and AF restriction.

Dependencies and integration points: Depends on Linux socket addresses and RDMA CM/verbs types. Integrates with `ib_device_ops` iWARP callbacks, RDMA CM adaptation, and iWARP port mapping.

Risks: Event ordering and ID destruction are race-prone. Provider reference hooks must be balanced. Address mapping state must remain coherent with port mapper state. Private-data lengths are constrained.

Test signals: Active/passive setup, reject private data, graceful/abrupt disconnect, close event delivery, QP attr initialization, provider ref balancing, TOS/AF-only settings, and immediate-event races.
