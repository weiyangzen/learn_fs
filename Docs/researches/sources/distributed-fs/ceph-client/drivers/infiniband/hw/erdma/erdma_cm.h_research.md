# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cm.h

Defines ERDMA iWARP CM protocol constants, MPA headers, endpoint states, socket callback storage, CM work types, CEP state, and IWCM prototypes.

Important definitions include MPA revision 129, max private data, request/reply keys, MPA flags, `struct mpa_rr`, `struct erdma_mpa_ext`, `struct erdma_mpa_info`, `struct erdma_sk_upcalls`, `enum erdma_cep_state`, `struct erdma_cep`, `enum erdma_work_type`, and `struct erdma_cm_work`.

The header describes the CM state machine: idle, listening, connecting, awaiting MPA request/reply, received request, RDMA mode, and closed. CEP state persists across a connection or listener and tracks socket, QP, IWCM ID, MPA partial receive buffers, timers, private data, and saved callbacks.

Dependencies are TCP/socket and IWCM headers plus ERDMA users in CM, QP, and main protocol ops. Risks include the assumption that `sk_user_data` is owned by ERDMA while callbacks are installed, IPv4-only implementation support, and strict MPA revision expectations. Test signals include state-machine coverage, callback association/disassociation, MPA private-data limits, and connection churn refcount tests.
