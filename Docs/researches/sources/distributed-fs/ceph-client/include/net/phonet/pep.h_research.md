# sources/distributed-fs/ceph-client/include/net/phonet/pep.h

Purpose: defines Phonet Pipe End Point socket state, pipe protocol headers, message IDs, error codes, states, subblocks, and flow-control modes.

Important APIs and types: `struct pep_sock` embeds `pn_sock` and stores listener/connected socket state, control request queue, TX/RX credits, interface index, peer type, pipe handle, flow-control selections, auto-enable, and alignment flag. `struct pnpipehdr` models pipe message headers. Constants enumerate pipe create/remove/data, PEP connect/disconnect/reset/enable/control/disable, status indications, invalid handle, common type, flow-control models, and status/error states. `pep_sk()` and `pnp_hdr()` cast from sockets/skbs.

Control flow: Phonet stream operations exchange pipe protocol messages, negotiate flow control, queue control requests, consume/grant credits, and deliver aligned or normal data frames.

State and persistence: per-socket pipe state is runtime only: queues, credits, pipe handle, peer type, listener link, and selected flow-control mode.

Dependencies and integration points: depends on Phonet core socket types and skbuffs; integrates with `phonet_stream_ops`, GPRS helper hooks, and Phonet packet headers.

Risks and test signals: risks include credit underflow/overrun, control queue overflow, invalid pipe handle handling, listener/child lifetime, and aligned data parsing. Test pipe create/connect/enable/data/disable/remove, all flow-control modes, ctrlreq queue limit, peer errors, and socket close while connected.
