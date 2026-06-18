# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_marshall.c

## Purpose

`uverbs_marshall.c` converts in-kernel RDMA address, QP, and path-record structures into the stable userspace ABI structures used by uverbs. It is a compatibility layer that hides kernel-internal representation changes and handles OPA-to-IB address conversion for older IB-shaped userspace fields.

## Important APIs, Types, and Functions

- `rdma_ah_conv_opa_to_ib()` maps OPA AH attributes to IB-compatible AH attributes, using the port subnet prefix and OPA LID-derived interface ID.
- `ib_copy_ah_attr_to_user()` fills `struct ib_uverbs_ah_attr` from `struct rdma_ah_attr`, including GRH fields when present.
- `ib_copy_qp_attr_to_user()` fills `struct ib_uverbs_qp_attr` from `struct ib_qp_attr`, including caps and primary/alternate AH attributes.
- `ib_copy_path_rec_to_user()` converts `struct sa_path_rec` to `struct ib_user_path_rec`, converting OPA path records first through `sa_convert_path_opa_to_ib()`.

## Control Flow

The copy helpers are straightforward field-by-field marshalling. AH conversion first zeroes the destination GRH, optionally converts OPA addressing when the DLID is not permissive, then copies DLID, SL, path bits, static rate, global route fields, port number, and reserved zeros. QP marshalling copies QP state/caps/path migration fields and delegates primary and alternate AH attributes to `ib_copy_ah_attr_to_user()`.

## State and Persistence Behavior

There is no stored state. The functions are pure marshalling operations except for `rdma_ah_conv_opa_to_ib()`, which queries port attributes to derive a subnet prefix and reports conversion failure by falling back to a default prefix and `-EINVAL`.

## Dependencies and Integration Points

The file depends on `rdma/ib_marshall.h`, SA path helpers, AH accessor helpers, and `ib_query_port()`. It is exported for other RDMA/uverbs code that needs userspace-compatible representations, especially query-style commands that return QP, AH, or path information.

## Risks and Edge Cases

The primary risk is ABI correctness: endian conversion, OPA LID truncation, reserved-field zeroing, and preserving userspace struct layout. Incorrect OPA conversion can mislead userspace route reconstruction. The active behavior of returning default subnet prefix on query failure is intentional but should be visible in tests.

## Test Signals

Useful tests include IB and OPA AH marshalling, GRH present/absent cases, permissive vs non-permissive DLIDs, query-port failure during OPA conversion, QP attr marshalling including alternate path fields, and SA path records with OPA and non-OPA `rec_type`.
