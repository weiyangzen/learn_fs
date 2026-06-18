# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-mem-types.h

## Purpose
This header declares memory accounting type IDs for the EC/disperse translator. The IDs let GlusterFS attribute allocations for EC private state, inode/fd contexts, self-heal structures, Galois-field/code-generation data, matrices, and stripe cache entries.

## Important APIs, Types, And Functions
The only exported symbol is enum `gf_ec_mem_types_`. Important members include `ec_mt_ec_t`, `ec_mt_xlator_t`, `ec_mt_ec_inode_t`, `ec_mt_ec_fd_t`, `ec_mt_subvol_healer_t`, `ec_mt_ec_gf_t`, `ec_mt_ec_code_t`, `ec_mt_ec_code_builder_t`, `ec_mt_ec_matrix_t`, and `ec_mt_ec_stripe_t`. `ec_mt_end` is passed to `xlator_mem_acct_init()` in `ec.c`.

## Control Flow
There is no runtime control flow. Allocation sites in EC source files pass these IDs to `GF_MALLOC`, `GF_CALLOC`, and related helpers; initialization in `mem_acct_init()` registers the enum range.

## State And Persistence Behavior
The header affects observability of heap state only. It does not persist data and does not hold mutable state.

## Dependencies And Integration Points
It includes `<glusterfs/mem-types.h>` and starts at `gf_common_mt_end + 1`, which is the standard GlusterFS convention for translator-local memory classes.

## Risks
Risks are mostly maintenance risks: adding a new allocation class out of order or before existing values could break accounting compatibility, while forgetting to add a type makes memory reports less useful. The enum must remain below `ec_mt_end` for `xlator_mem_acct_init()`.

## Test Signals
Build coverage and translator initialization are the primary checks. Memory-accounting/statedump tests can confirm EC allocations are tagged under expected names and do not fall into common unknown buckets.
