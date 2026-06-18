# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/siw_cm.h

Purpose: Declares the SoftiWARP connection endpoint model, MPA negotiation state, CM work item types, socket helper shims, and public CM entry points used by `siw_cm.c`, `siw_main.c`, and QP close paths.

Important APIs/types/functions: `enum siw_cep_state` is the endpoint state machine. `struct siw_mpa_info` stores the received/sent MPA header, MPAv2 negotiation payload, private data pointer, and bytes received. `struct siw_cep` binds IWCM id, SIW device, socket, QP, listener links, work freelist, MPA timer, negotiated ORD/IRD, enhanced setup flag, saved socket callbacks, lock/kref/waitqueue, and in-use serialization. `enum siw_work_type` and `struct siw_cm_work` describe accept, MPA read, socket close, peer close, and timeout work. `getname_peer()`, `getname_local()`, and `ksock_recv()` are thin socket helpers.

Control flow: CM code allocates a CEP, associates it with a socket through `sk_user_data`, replaces socket callbacks, queues `siw_cm_work` items, and eventually moves the socket to QP callbacks. Listen CEPs hold child CEPs through `listen_cep`; passive connect requests pass child CEPs through IWCM provider data.

State and persistence behavior: No persistent storage. The header encodes in-memory synchronization expectations: CEP lock protects state/work freelist/timer, kref guards callback/work lifetimes, and `in_use` plus waitqueue serialize state-machine execution across callbacks and worker context.

Dependencies/integration: Includes `net/sock.h`, TCP, and `rdma/iw_cm.h`. It exposes `siw_connect`, `siw_accept`, `siw_reject`, listen create/destroy, CM init/exit, CEP refcount helpers, and `siw_cm_queue_work()` to the rest of the driver.

Risks: Because `sk_to_cep()` and `sk_to_qp()` trust `sk_user_data`, any callback after disassociation or wrong callback ordering can crash. Work freelist sizing must cover concurrent close/data/timeout events. Provider-data overloading for listener versus passive child IDs is subtle.

Test signals: Compile-time coverage of prototypes, active/passive IWCM calls, socket callback stress, listener teardown, private data propagation, timeout path, and sanitizers/lockdep around CEP lifetime.
