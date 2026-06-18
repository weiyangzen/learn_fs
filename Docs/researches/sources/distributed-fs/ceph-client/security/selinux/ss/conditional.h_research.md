<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/conditional.h

## Purpose
Declares SELinux conditional policy structures and APIs. It models booleans, reverse-polish expressions, true/false rule lists, and conditional nodes embedded in a policy database.

## Important APIs, Types, and Functions
Types include `struct cond_expr_node`, `struct cond_expr`, `struct cond_av_list`, and `struct cond_node`. Expression operators are `COND_BOOL`, `COND_NOT`, `COND_OR`, `COND_AND`, `COND_XOR`, `COND_EQ`, and `COND_NEQ`; `COND_EXPR_MAXDEPTH` caps evaluation stack depth. APIs cover policydb init/destroy/duplication, boolean indexing and I/O, conditional list I/O, evaluation, and decision contribution.

## Control Flow
Policy load uses `cond_read_bool()` and `cond_read_list()` to populate structures. Boolean state changes call `evaluate_cond_nodes()` to update AV node enabled flags. Access decisions call `cond_compute_av()` and `cond_compute_xperms()` after base table lookups.

## State and Persistence
The header defines policy-owned state rather than global state. Conditional AV lists store pointers to nodes in `te_cond_avtab`, so persistence and duplication must rebuild pointer arrays along with the table.

## Dependencies and Integration Points
Depends on `avtab`, `symtab`, `policydb`, and the exported conditional uapi header. Used by policydb parsing/writing, service decision code, and selinuxfs boolean controls.

## Risks
The pointer relationship between `cond_av_list.nodes` and `te_cond_avtab` is invariant-critical. Operator values are serialized in binary policy, so changing them breaks compatibility. Stack depth is a load-time/runtime safety constraint.

## Test Signals
Compile all conditional users, load/write policies with every operator, toggle booleans, verify enabled state and decision changes, and test policy duplication/destruction with memory leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/conditional.h -->
