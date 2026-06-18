<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.h

## Purpose

`spectrum_acl_flex_actions.h` is the public Spectrum ACL flexible-action header. It exposes only the initialization and teardown entry points needed by the Spectrum driver.

## Important APIs, Types, And Functions

- `mlxsw_sp_afa_init(struct mlxsw_sp *mlxsw_sp)` creates `mlxsw_sp->afa` using chip-specific AFA ops.
- `mlxsw_sp_afa_fini(struct mlxsw_sp *mlxsw_sp)` destroys the AFA object.
- The header includes `spectrum.h` so callers have `struct mlxsw_sp`.

## Control Flow

The header has no runtime control flow. It participates in driver initialization ordering by making AFA setup available before ACL rules can create or commit action blocks.

## State And Persistence

The header stores no state. Its declared functions manage the runtime `mlxsw_sp->afa` pointer and action-related hardware resources through the implementation file.

## Dependencies And Integration Points

It is included by ACL setup code and by `spectrum_acl_flex_actions.c`. It ties the Spectrum driver to `core_acl_flex_actions` without exposing implementation details such as KVDL, SPAN, counters, policers, or sampling.

## Risks

- The narrow interface is simple, but incorrect init/fini ordering can leave ACL rule construction without an AFA handle or destroy AFA while rules still reference action blocks.
- Since the header does not expose feature flags, chip differences are hidden in `mlxsw_sp->afa_ops` and must be initialized correctly elsewhere.

## Test Signals

Build coverage, Spectrum probe/remove, ACL rule creation after AFA init, and cleanup with no outstanding action blocks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_actions.h -->
