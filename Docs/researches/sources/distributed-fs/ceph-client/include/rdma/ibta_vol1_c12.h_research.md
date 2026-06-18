# sources/distributed-fs/ceph-client/include/rdma/ibta_vol1_c12.h

Purpose: Declares IBTA Volume 1 Chapter 12 Communication Management message layouts as `IBA_*` field descriptors.

Important APIs/types/functions: `CM_FIELD_BLOC`, `CM_FIELD8_LOC`, `CM_FIELD16_LOC`, `CM_FIELD32_LOC`, `CM_FIELD64_LOC`, `CM_FIELD_MLOC`, and `CM_STRUCT`. It defines field macros and structs for REQ, MRA, REJ, REP, RTU, DREQ, DREP, LAP, APR, SIDR_REQ, and SIDR_REP messages.

Control flow: No runtime logic beyond macro expansion. CM code uses these field descriptors with `IBA_GET`/`IBA_SET` to read and write payload fields after the MAD header.

State and persistence behavior: Defines transient wire message buffers. Actual CM state lives in the CM implementation and remote protocol exchange.

Dependencies and integration points: Depends on `rdma/iba.h`, `struct ib_mad_hdr`, and GID types. Integrates with InfiniBand CM and MAD transport code that encodes connection setup/teardown and SIDR messages.

Risks: Offset, width, and total-length errors break interoperability. Large private-data regions need caller length validation. Split vendor-ID fields in REP are easy to mishandle.

Test signals: Byte-for-byte encode/decode tests for all message types, bit-packed timeout/retry/service fields, GID memory fields, and private-data boundary lengths.
