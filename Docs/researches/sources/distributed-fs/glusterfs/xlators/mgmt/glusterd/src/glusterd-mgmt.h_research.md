# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-mgmt.h

## Purpose

`glusterd-mgmt.h` exposes the management v3 transaction coordinator API implemented by `glusterd-mgmt.c`. It is the include boundary used by other GlusterD modules that need to initiate or participate in mgmt v3 operations without knowing the RPC callback internals.

## Important APIs and contracts

The header declares the operation-specific local phase dispatchers (`gd_mgmt_v3_pre_validate_fn()`, `gd_mgmt_v3_brick_op_fn()`, `gd_mgmt_v3_commit_fn()`, `gd_mgmt_v3_post_commit_fn()`, `gd_mgmt_v3_post_validate_fn()`) and the public transaction drivers (`glusterd_mgmt_v3_initiate_all_phases()`, `glusterd_mgmt_v3_initiate_all_phases_with_brickop_phase()`, `glusterd_mgmt_v3_initiate_snap_phases()`). It also exposes phase helpers for lock acquisition, payload construction, prevalidation, commit, peer-lock release, and barrier changes. Several declarations refer to operation-specific helpers implemented elsewhere, including snapshot response aggregation, reset-brick prevalidation/commit, and post-commit brick operation handling.

## Control flow represented by the header

The API shape documents the phase model: callers can either invoke a full orchestration entry point or call individual phases in sequence. The function signatures consistently pass `glusterd_op_t`, `dict_t` operation context, `char **op_errstr`, optional `uint32_t *op_errno`, and a `txn_generation` for peer-list stability. This makes the management transaction boundary explicit: the dictionary is the mutable payload, `op_errstr` is the user-visible diagnostic channel, and `txn_generation` constrains which peers participate.

## State and persistence behavior

The header itself stores no state, but its signatures reveal ownership-sensitive behavior. `glusterd_mgmt_v3_build_payload()` returns a newly referenced `dict_t **req`; error strings may be allocated into `*op_errstr`; lock functions report acquisition through `gf_boolean_t *is_acquired`; and commit/post-commit helpers can update persistent volume and snapshot state through the operation-specific implementation behind the phase dispatchers.

## Dependencies and integration points

This header depends on GlusterD core types (`glusterd_op_t`, `dict_t`, `rpcsvc_request_t`, `gf_boolean_t`, `uuid_t`, `struct syncargs`) supplied by surrounding includes before the header is consumed. It is included by `glusterd-mgmt.c` and by modules that need mgmt v3 orchestration for CLI or peer-originated operations.

## Risks and test signals

The header has no include guard dependencies beyond `_GLUSTERD_MGMT_H_`, but it relies on consumers including the right type definitions first. There is a formatting oddity: a standalone `int` line appears before `glusterd_mgmt_v3_initiate_lockdown()`, which still forms a valid declaration with the following function but is easy to break during edits. Build coverage should compile all consumers with warnings enabled, and API tests should verify callers free returned dictionaries/error strings according to implementation ownership rules.
