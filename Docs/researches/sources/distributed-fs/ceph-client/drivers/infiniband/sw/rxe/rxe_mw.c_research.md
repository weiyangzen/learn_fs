# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_mw.c

## Purpose
`rxe_mw.c` implements RXE memory windows, including type 1 and type 2B allocation, bind, invalidate, lookup, and cleanup.

## Important APIs, types, and functions
External functions are `rxe_alloc_mw()`, `rxe_dealloc_mw()`, `rxe_bind_mw()`, `rxe_invalidate_mw()`, `rxe_lookup_mw()`, and `rxe_mw_cleanup()`. Internal helpers `rxe_check_bind_mw()`, `rxe_do_bind_mw()`, `rxe_check_invalidate_mw()`, and `rxe_do_invalidate_mw()` enforce IB access and state rules. State lives in `struct rxe_mw`, including rkey, state, access, bound MR, bound QP for type 2, address, length, and lock.

## Control flow
Allocation takes a PD reference, adds the MW to the pool, assigns an rkey using the pool index plus random key byte, initializes state to VALID for type 1 or FREE for type 2, and finalizes the object. Binding looks up the MW by rkey index, checks full rkey, optionally looks up the target MR by lkey, validates supported access flags, takes `mw->lock`, enforces type-specific state/PD/null-MR rules and MR access/range requirements, updates the low rkey byte, attaches MR/QP references, increments `mr->num_mw`, and marks the MW valid. Invalidation rejects type 1 and invalid MWs, then drops QP/MR refs and returns type 2 MWs to FREE. Cleanup drops PD/MR/QP references and marks the MW invalid.

## State and persistence
MW state is in-memory object-pool state. Bound type 2 MWs hold references to both QP and MR; bound MRs track `num_mw`, which blocks MR invalidation. Rkeys change on bind via the low key byte.

## Dependencies and integration points
MWs are used by requester bind/invalidate WQEs and responder remote access checks. The file depends on MR pools, PD/QP identity, RXE access masks, key generation from `rxe_mr.c`, and RXE object refcounting.

## Risks
Bind and invalidate correctness depends on state transitions under `mw->lock`. `rxe_do_invalidate_mw()` assumes valid type 2 MWs always have QP and MR pointers. Range checks must account for zero-based vs virtual-address MWs. Key mismatch handling must drop looked-up references on every error path.

## Test signals
Test type 1 and type 2 allocation, bind success/failure by state, PD mismatch, unsupported access, MR lacking bind/local-write access, zero-length/null MR behavior, zero-based range checks, remote lookup by rkey/access/QP, invalidate type 2, reject type 1 invalidate, cleanup while bound, and MR invalidation blocked by `num_mw`.
