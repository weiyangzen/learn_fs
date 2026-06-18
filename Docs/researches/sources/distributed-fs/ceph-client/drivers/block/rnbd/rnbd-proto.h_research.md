# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-proto.h

## Purpose
Defines the RNBD wire protocol shared by client and server: protocol version, message types and layouts, access modes, cache policy flags, and conversions between Linux request operations and RNBD I/O flags.

## Important APIs, types, and functions
- `RNBD_PROTO_VER_MAJOR`/`MINOR` are `2.2`; `RTRS_PORT` defaults to `1234`.
- Message structures include `rnbd_msg_hdr`, `rnbd_msg_sess_info`, `rnbd_msg_sess_info_rsp`, `rnbd_msg_open`, `rnbd_msg_open_rsp`, `rnbd_msg_io`, and `rnbd_msg_close`.
- `enum rnbd_access_mode` supports `ro`, `rw`, and `migration`; `rnbd_access_modes[]` provides strings.
- `enum rnbd_io_flags` encodes read, write, flush, discard, secure erase, write zeroes, sync, FUA, preflush, and nounmap.
- `rnbd_to_bio_flags()` converts protocol flags to server-side `blk_opf_t`; `rq_to_rnbd_flags()` converts client requests to protocol flags.

## Control flow
Client code fills protocol messages before calling RTRS; server code decodes the same layouts in `rnbd_srv_rdma_ev()`. Module init on both sides uses `BUILD_BUG_ON()` to assert fixed sizes for the wire ABI.

## State and persistence behavior
The header owns no runtime state. It defines little-endian wire fields and reserved padding, so layout and endian conversion are persistent ABI concerns between client and server versions.

## Dependencies and integration points
Depends on Linux block request types, limits, inet types, and RDMA headers. It is included by RNBD client, server, trace, and logging code.

## Risks and test signals
- Any structure layout change can break interoperability; keep size assertions and cross-version tests.
- `rq_to_rnbd_flags()` uses `op_is_flush()` to set `RNBD_F_FUA`, which deserves attention in flush/FUA semantic tests.
- Test all operation translations in both directions, including invalid op warnings and old-server behavior where server checks `usrlen` before reading `prio`.
