# sources/distributed-fs/ceph-client/include/xen/interface/io/xs_wire.h

## Purpose
`xs_wire.h` defines the Xenstore client/server wire protocol: request types, error-string mapping, socket message header layout, shared ring structure, payload/path limits, server feature bits, and reconnect/error status fields.

## Important APIs, Types, and Functions
Important definitions include `enum xsd_sockmsg_type`, `struct xsd_sockmsg`, `struct xsd_errors`, `enum xs_watch_type`, `struct xenstore_domain_interface`, `XENSTORE_RING_SIZE`, `MASK_XENSTORE_IDX`, `XENSTORE_PAYLOAD_MAX`, path length limits, server feature flags, and connection/error status constants.

## Control Flow
Clients send an `xsd_sockmsg` header plus string payload through a socket or shared ring. Xenstored replies with matching `req_id` and may emit asynchronous watch events. Transactions use `XS_TRANSACTION_START` and `XS_TRANSACTION_END`; watches use path/token pairs; reconnect-capable rings use the `connection` and `error` fields.

## State and Persistence Behavior
The ring stores request/response bytes and producer/consumer indices shared between guest and xenstored. Xenstore contents persist in the Xenstore daemon's runtime database, while the ring fields only describe live communication state.

## Dependencies and Integration Points
The header assumes errno names are visible where included and is consumed by Xenstore libraries and guest kernels. It integrates with Linux xenbus operations, Xenstore watches, backend/frontend device discovery, and suspend/resume reconnect handling.

## Risks and Test Signals
Risks include producer/consumer index corruption, payload/path length violations, error-string mismatches, watch-event ordering races, and reconnect support mismatches. Test signals include transaction retry tests, watch delivery/unwatch behavior, ring wraparound, max payload rejection, and feature-bit fallback tests.
