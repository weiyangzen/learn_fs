# sources/distributed-fs/ceph-client/drivers/infiniband/core/sa_query.c

## Purpose
`sa_query.c` implements InfiniBand and OPA Subnet Administration query support. It packs SA records into MAD payloads, sends requests through the MAD layer or optional netlink local-service resolution, handles responses and timeouts, caches class-port information, maintains SM address handles per port, and registers as an IB client for capable devices.

## Important APIs, types, and functions
- Client API: `ib_sa_register_client()`, `ib_sa_unregister_client()`, and `ib_sa_cancel_query()`.
- Query APIs: `ib_sa_path_rec_get()`, `ib_sa_service_rec_get()`, `ib_sa_mcmember_rec_query()`, and `ib_sa_guid_info_rec_query()`.
- Address conversion/API helpers: `ib_init_ah_attr_from_path()`, `ib_sa_pack_path()`, `ib_sa_unpack_path()`, `ib_sa_pack_service()`, and `ib_sa_unpack_service()`.
- Lifecycle: `ib_sa_init()`, `ib_sa_cleanup()`, `ib_sa_add_one()`, and `ib_sa_remove_one()`.
- Local-service netlink handlers: `ib_nl_handle_resolve_resp()` and `ib_nl_handle_set_timeout()`.
- Core callbacks: `send_handler()`, `recv_handler()`, `update_sm_ah()`, `update_ib_cpi()`, and `ib_sa_event()`.

## Control flow and behavior
At initialization, the file seeds transaction IDs, registers the SA IB client, initializes multicast handling, creates a netlink timeout workqueue, and prepares delayed timeout work. Device add allocates per-port SA state, registers GSI MAD agents on SA-capable ports, initializes SM AH update work and class-port delayed work, installs an event handler, and builds initial SM address handles.

Each query allocates a query-specific wrapper, obtains the per-port SM AH, allocates a send MAD, initializes headers/TID, packs the requested record, stores callback/release functions, and calls `send_mad()`. `send_mad()` allocates a query ID in a global XArray, configures timeout/retry values, and either sends the request through the local-service netlink path for path records or posts a MAD. Send completion maps MAD WC status to callback status, erases the XArray entry, frees MAD/SM AH references, drops client references, and calls the query release function. Receive completion unpacks MAD or RMPP payloads and invokes the registered callback before freeing the receive MAD.

The local-service path constructs RDMA netlink resolve requests from path record component masks, queues them in `ib_nl_request_list`, and falls back to MAD if local resolution fails or times out. Good netlink responses are filtered by requested path use, unpacked or copied into MAD form, and completed through the normal send handler path.

## State, persistence, and dependencies
Global state includes `queries` XArray, transaction `tid`, netlink request list/lock/sequence, `ib_nl_wq`, `ib_nl_timed_work`, and configurable local-service timeout. Per-device state is `struct ib_sa_device`; per-port state includes MAD agent, cached SM AH, class-port info cache, update work, delayed CPI work, and locks. Query state persists until completion/cancel/send failure and holds client references, MAD buffers, SM AH refs, IDs, flags, netlink sequence, and callback metadata.

## Integration points
The file integrates with MAD core, RDMA netlink local service, OPA address handling, RDMA CM path resolution, GID cache, AH creation, multicast initialization, IB event handling, packing helpers in `packer.c`, and public SA APIs in `<rdma/ib_sa.h>`.

## Risks and test signals
Risks include query ID leaks, callback after cancel, netlink/MAD double completion, stale SM AH after port events, class-port cache retry races, RMPP service record sizing mistakes, OPA/IB path conversion errors, and local-service timeout list ordering bugs. Test signals include path/service/mcmember/guid queries with success, timeout, cancel and send error; netlink listener present/absent; malformed netlink replies; SM/LID/PKey/client-reregister events; OPA port path-record support; RMPP multi-record service replies; and cleanup with outstanding queries.
