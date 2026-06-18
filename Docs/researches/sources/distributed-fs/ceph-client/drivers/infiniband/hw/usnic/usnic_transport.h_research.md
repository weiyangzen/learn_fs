# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.h

Purpose: public transport helper declarations for usNIC.

Important APIs: declares transport string formatting, socket string/address helpers, RoCE custom port reserve/unreserve, socket get/put, and module init/fini functions.

Control flow: QP group code calls reserve/get helpers during flow creation and unreserve/put helpers during flow release. Debugfs calls string formatting. Main module calls init/fini.

State and persistence: header declares no state; implementation maintains the RoCE bitmap and socket refs.

Dependencies and integration: includes the usNIC ABI transport enum and uses kernel `struct socket` from includers.

Risks: comments define ownership rules: callers must call `usnic_transport_put_socket()` after `get_socket()` and call socket address helpers only after obtaining a reference.

Test signals: compile linkage and QP create/destroy paths for both custom RoCE and UDP transports.
